"""
Router for Reporting API endpoints.
"""

from typing import Optional
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, Query

from app.core.database import db_connector
from app.schemas import ListResponse
from app.modules.reports.schemas import AttendanceSummaryItem, AttendanceByRangeItem
from app.modules.reports.service import ReportService


router = APIRouter(prefix="/api/reports", tags=["Reports"])


async def get_report_service() -> ReportService:
    """Dependency injection for ReportService."""
    return ReportService(db_connector.database)


@router.get(
    "/attendance-summary",
    response_model=ListResponse[AttendanceSummaryItem],
    summary="Attendance summary by employee"
)
async def attendance_summary(
    department: Optional[str] = None,
    service: ReportService = Depends(get_report_service),
) -> ListResponse[AttendanceSummaryItem]:
    """
    Get total present and absent days per employee.

    Query Parameters:
    - department: Optional department filter
    """
    records = await service.attendance_summary(department=department)
    items = [AttendanceSummaryItem(**record) for record in records]
    return ListResponse(count=len(items), data=items)


@router.get(
    "/attendance-by-range",
    response_model=ListResponse[AttendanceByRangeItem],
    summary="Attendance records by date range"
)
async def attendance_by_range(
    start_date: date = Query(..., description="Range start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Range end date (YYYY-MM-DD)"),
    employee_id: Optional[UUID] = None,
    department: Optional[str] = None,
    service: ReportService = Depends(get_report_service),
) -> ListResponse[AttendanceByRangeItem]:
    """
    Get attendance records for a date range with employee names.

    Query Parameters:
    - start_date: Range start date (required, format: YYYY-MM-DD)
    - end_date: Range end date (required, format: YYYY-MM-DD)
    - employee_id: Optional employee UUID filter
    - department: Optional department filter
    """
    records = await service.attendance_by_range(
        start_date=start_date,
        end_date=end_date,
        employee_id=str(employee_id) if employee_id else None,
        department=department,
    )
    items = [AttendanceByRangeItem(**record) for record in records]
    return ListResponse(count=len(items), data=items)
