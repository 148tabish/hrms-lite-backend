"""
Router for Attendance API endpoints.
"""

from typing import Optional
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends
from databases import Database

from app.core.database import db_connector
from app.schemas import SuccessResponse, ListResponse
from app.modules.attendance.schemas import (
    AttendanceCreate,
    AttendanceUpdate,
    AttendanceResponse,
)
from app.modules.attendance.service import AttendanceService
from app.modules.attendance.controller import AttendanceController


router = APIRouter(prefix="/api/attendance", tags=["Attendance"])


async def get_attendance_controller() -> AttendanceController:
    """Dependency injection for AttendanceController."""
    service = AttendanceService(db_connector.database)
    return AttendanceController(service)


@router.get(
    "",
    response_model=ListResponse[AttendanceResponse],
    summary="List attendance records"
)
async def list_attendance(
    employee_id: Optional[UUID] = None,
    date: Optional[date] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    status: Optional[str] = None,
    controller: AttendanceController = Depends(get_attendance_controller),
) -> ListResponse[AttendanceResponse]:
    """
    Retrieve attendance records with optional filters.

    Query Parameters:
    - employee_id: Filter by employee UUID
    - date: Filter by specific date
    - start_date: Filter by date range start
    - end_date: Filter by date range end
    - status: Filter by status ('Present' or 'Absent')
    """
    records = await controller.list_attendance(
        employee_id=employee_id,
        date_filter=date,
        start_date=start_date,
        end_date=end_date,
        status=status,
    )
    return ListResponse(count=len(records), data=records)


@router.post(
    "",
    response_model=SuccessResponse[AttendanceResponse],
    status_code=201,
    summary="Create attendance record"
)
async def create_attendance(
    data: AttendanceCreate,
    controller: AttendanceController = Depends(get_attendance_controller),
) -> SuccessResponse[AttendanceResponse]:
    """Create a new attendance record."""
    record = await controller.create_attendance(data)
    return SuccessResponse(data=record)


@router.get(
    "/{attendance_id}",
    response_model=SuccessResponse[AttendanceResponse],
    summary="Get attendance by ID"
)
async def get_attendance(
    attendance_id: UUID,
    controller: AttendanceController = Depends(get_attendance_controller),
) -> SuccessResponse[AttendanceResponse]:
    """Retrieve a single attendance record by UUID."""
    record = await controller.get_attendance(attendance_id)
    return SuccessResponse(data=record)


@router.put(
    "/{attendance_id}",
    response_model=SuccessResponse[AttendanceResponse],
    summary="Update attendance record"
)
async def update_attendance(
    attendance_id: UUID,
    data: AttendanceUpdate,
    controller: AttendanceController = Depends(get_attendance_controller),
) -> SuccessResponse[AttendanceResponse]:
    """Update an attendance record (status only)."""
    record = await controller.update_attendance(attendance_id, data)
    return SuccessResponse(data=record)


@router.delete("/{attendance_id}", status_code=204, summary="Delete attendance record")
async def delete_attendance(
    attendance_id: UUID,
    controller: AttendanceController = Depends(get_attendance_controller),
) -> None:
    """Delete an attendance record."""
    await controller.delete_attendance(attendance_id)
