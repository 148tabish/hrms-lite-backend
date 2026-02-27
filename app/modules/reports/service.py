"""
Service layer for Reporting operations.
All database queries are performed here using the databases library.
"""

from typing import Optional, List
from datetime import date
from databases import Database

from app.modules.reports.schemas import (
    AttendanceSummaryItem,
    AttendanceByRangeItem,
)


class ReportService:
    """Service for report-related database operations."""

    def __init__(self, database: Database):
        """
        Initialize with database connection.

        Args:
            database: Connected databases.Database instance
        """
        self.db = database

    async def attendance_summary(
        self, department: Optional[str] = None
    ) -> List[dict]:
        """
        Get attendance summary (present/absent counts) per employee.

        Args:
            department: Optional department filter

        Returns:
            List of summary dictionaries
        """
        if department:
            query = """
                SELECT e.id AS employee_id, e.full_name,
                       COUNT(*) FILTER (WHERE a.status = 'Present') AS total_present,
                       COUNT(*) FILTER (WHERE a.status = 'Absent')  AS total_absent
                FROM employees e
                LEFT JOIN attendance a ON a.employee_id = e.id
                WHERE e.department = :department
                GROUP BY e.id, e.full_name
                ORDER BY e.full_name
            """
            return await self.db.fetch_all(query, {"department": department})
        else:
            query = """
                SELECT e.id AS employee_id, e.full_name,
                       COUNT(*) FILTER (WHERE a.status = 'Present') AS total_present,
                       COUNT(*) FILTER (WHERE a.status = 'Absent')  AS total_absent
                FROM employees e
                LEFT JOIN attendance a ON a.employee_id = e.id
                GROUP BY e.id, e.full_name
                ORDER BY e.full_name
            """
            return await self.db.fetch_all(query)

    async def attendance_by_range(
        self,
        start_date: date,
        end_date: date,
        employee_id: Optional[str] = None,
        department: Optional[str] = None,
    ) -> List[dict]:
        """
        Get attendance records for a date range.

        Args:
            start_date: Range start date
            end_date: Range end date
            employee_id: Optional employee UUID filter
            department: Optional department filter

        Returns:
            List of attendance records with employee names
        """
        conditions = [
            "a.date BETWEEN :start_date AND :end_date"
        ]
        params = {
            "start_date": start_date,
            "end_date": end_date,
        }

        if employee_id:
            conditions.append("a.employee_id = :employee_id")
            params["employee_id"] = employee_id

        if department:
            conditions.append("e.department = :department")
            params["department"] = department

        where_clause = " AND ".join(conditions)

        query = f"""
            SELECT e.full_name, a.date, a.status
            FROM attendance a
            JOIN employees e ON e.id = a.employee_id
            WHERE {where_clause}
            ORDER BY a.date, e.full_name
        """

        return await self.db.fetch_all(query, params)
