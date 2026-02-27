"""
Controller layer for Attendance API.
Handles request/response orchestration.
"""

from typing import Optional
from uuid import UUID
from datetime import date
from fastapi import HTTPException

from app.modules.attendance.schemas import (
    AttendanceCreate,
    AttendanceUpdate,
    AttendanceResponse,
    AttendanceStatus,
)
from app.modules.attendance.service import AttendanceService


class AttendanceController:
    """Controller for attendance-related operations."""

    def __init__(self, service: AttendanceService):
        """
        Initialize with attendance service.

        Args:
            service: AttendanceService instance
        """
        self.service = service

    async def list_attendance(
        self,
        employee_id: Optional[UUID] = None,
        date_filter: Optional[date] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[str] = None,
    ) -> list[AttendanceResponse]:
        """
        List attendance records with optional filters.

        Args:
            employee_id: Filter by employee UUID
            date_filter: Filter by specific date
            start_date: Filter by date range start
            end_date: Filter by date range end
            status: Filter by status string ("Present" or "Absent")

        Returns:
            List of AttendanceResponse models
        """
        status_enum = None
        if status:
            try:
                status_enum = AttendanceStatus(status)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid status. Must be 'Present' or 'Absent'"
                )

        records = await self.service.list_attendance(
            employee_id=employee_id,
            date_filter=date_filter,
            start_date=start_date,
            end_date=end_date,
            status=status_enum,
        )
        return [AttendanceResponse(**record) for record in records]

    async def get_attendance(self, attendance_id: UUID) -> AttendanceResponse:
        """
        Get a single attendance record by UUID.

        Args:
            attendance_id: UUID of the record

        Raises:
            HTTPException: 404 if not found

        Returns:
            AttendanceResponse model
        """
        record = await self.service.get_attendance_by_id(attendance_id)
        if not record:
            raise HTTPException(status_code=404, detail="Attendance record not found")
        return AttendanceResponse(**record)

    async def create_attendance(self, data: AttendanceCreate) -> AttendanceResponse:
        """
        Create a new attendance record.

        Args:
            data: AttendanceCreate request model

        Raises:
            HTTPException: 409 on duplicate, 400 on invalid employee

        Returns:
            AttendanceResponse model
        """
        try:
            record = await self.service.create_attendance(data)
            return AttendanceResponse(**record)
        except ValueError as e:
            error_msg = str(e)
            if "Duplicate" in error_msg:
                raise HTTPException(
                    status_code=409,
                    detail="Attendance already exists for this employee on this date"
                )
            elif "Foreign key" in error_msg:
                raise HTTPException(status_code=400, detail=error_msg)
            raise HTTPException(status_code=400, detail=error_msg)

    async def update_attendance(
        self, attendance_id: UUID, data: AttendanceUpdate
    ) -> AttendanceResponse:
        """
        Update an attendance record (status only).

        Args:
            attendance_id: UUID of the record to update
            data: AttendanceUpdate request model

        Raises:
            HTTPException: 404 if not found

        Returns:
            AttendanceResponse model
        """
        try:
            record = await self.service.update_attendance(attendance_id, data)
            return AttendanceResponse(**record)
        except ValueError as e:
            error_msg = str(e)
            if "not found" in error_msg.lower():
                raise HTTPException(status_code=404, detail=error_msg)
            raise HTTPException(status_code=400, detail=error_msg)

    async def delete_attendance(self, attendance_id: UUID) -> bool:
        """
        Delete an attendance record.

        Args:
            attendance_id: UUID of the record to delete

        Raises:
            HTTPException: 404 if not found

        Returns:
            True if deleted
        """
        deleted = await self.service.delete_attendance(attendance_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Attendance record not found")
        return True
