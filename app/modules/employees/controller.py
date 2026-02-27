"""
Controller layer for Employee API.
Handles request/response orchestration.
"""

from typing import Optional
from uuid import UUID
from fastapi import HTTPException

from app.modules.employees.schemas import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
)
from app.modules.employees.service import EmployeeService


class EmployeeController:
    """Controller for employee-related operations."""

    def __init__(self, service: EmployeeService):
        """
        Initialize with employee service.

        Args:
            service: EmployeeService instance
        """
        self.service = service

    async def list_employees(
        self, department: Optional[str] = None
    ) -> list[EmployeeResponse]:
        """
        List all employees, optionally filtered by department.

        Args:
            department: Optional department filter

        Returns:
            List of EmployeeResponse models
        """
        employees = await self.service.list_employees(department=department)
        return [EmployeeResponse(**emp) for emp in employees]

    async def get_employee(self, employee_id: UUID) -> EmployeeResponse:
        """
        Get a single employee by UUID.

        Args:
            employee_id: UUID of the employee

        Raises:
            HTTPException: 404 if not found

        Returns:
            EmployeeResponse model
        """
        employee = await self.service.get_employee_by_id(employee_id)
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        return EmployeeResponse(**employee)

    async def create_employee(self, data: EmployeeCreate) -> EmployeeResponse:
        """
        Create a new employee.

        Args:
            data: EmployeeCreate request model

        Raises:
            HTTPException: 409 on duplicate employee_id or email

        Returns:
            EmployeeResponse model
        """
        try:
            employee = await self.service.create_employee(data)
            return EmployeeResponse(**employee)
        except ValueError as e:
            if "Duplicate" in str(e):
                raise HTTPException(
                    status_code=409,
                    detail="Employee ID or email already exists"
                )
            raise HTTPException(status_code=400, detail=str(e))

    async def update_employee(
        self, employee_id: UUID, data: EmployeeUpdate
    ) -> EmployeeResponse:
        """
        Update an employee with partial data.

        Args:
            employee_id: UUID of the employee to update
            data: EmployeeUpdate request model

        Raises:
            HTTPException: 404 if not found, 409 on duplicate

        Returns:
            EmployeeResponse model
        """
        try:
            employee = await self.service.update_employee(employee_id, data)
            return EmployeeResponse(**employee)
        except ValueError as e:
            error_msg = str(e)
            if "not found" in error_msg.lower():
                raise HTTPException(status_code=404, detail=error_msg)
            elif "Duplicate" in error_msg:
                raise HTTPException(status_code=409, detail="Employee ID or email already exists")
            raise HTTPException(status_code=400, detail=error_msg)

    async def delete_employee(self, employee_id: UUID) -> bool:
        """
        Delete an employee.

        Args:
            employee_id: UUID of the employee to delete

        Raises:
            HTTPException: 404 if not found

        Returns:
            True if deleted
        """
        deleted = await self.service.delete_employee(employee_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Employee not found")
        return True
