"""
Router for Employee API endpoints.
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends
from databases import Database

from app.core.database import db_connector
from app.schemas import SuccessResponse, ListResponse
from app.modules.employees.schemas import EmployeeCreate, EmployeeUpdate, EmployeeResponse
from app.modules.employees.service import EmployeeService
from app.modules.employees.controller import EmployeeController


router = APIRouter(prefix="/api/employees", tags=["Employee"])


async def get_employee_controller() -> EmployeeController:
    """Dependency injection for EmployeeController."""
    service = EmployeeService(db_connector.database)
    return EmployeeController(service)


@router.get(
    "",
    response_model=ListResponse[EmployeeResponse],
    summary="List all employees"
)
async def list_employees(
    department: Optional[str] = None,
    controller: EmployeeController = Depends(get_employee_controller),
) -> ListResponse[EmployeeResponse]:
    """
    Retrieve all employees.

    Query Parameters:
    - department: Optional department filter
    """
    employees = await controller.list_employees(department=department)
    return ListResponse(count=len(employees), data=employees)


@router.post(
    "",
    response_model=SuccessResponse[EmployeeResponse],
    status_code=201,
    summary="Create a new employee"
)
async def create_employee(
    data: EmployeeCreate,
    controller: EmployeeController = Depends(get_employee_controller),
) -> SuccessResponse[EmployeeResponse]:
    """Create a new employee."""
    employee = await controller.create_employee(data)
    return SuccessResponse(data=employee)


@router.get(
    "/{employee_id}",
    response_model=SuccessResponse[EmployeeResponse],
    summary="Get employee by ID"
)
async def get_employee(
    employee_id: UUID,
    controller: EmployeeController = Depends(get_employee_controller),
) -> SuccessResponse[EmployeeResponse]:
    """Retrieve a single employee by UUID."""
    employee = await controller.get_employee(employee_id)
    return SuccessResponse(data=employee)


@router.put(
    "/{employee_id}",
    response_model=SuccessResponse[EmployeeResponse],
    summary="Update employee"
)
async def update_employee(
    employee_id: UUID,
    data: EmployeeUpdate,
    controller: EmployeeController = Depends(get_employee_controller),
) -> SuccessResponse[EmployeeResponse]:
    """Update an employee with partial data."""
    employee = await controller.update_employee(employee_id, data)
    return SuccessResponse(data=employee)


@router.delete("/{employee_id}", status_code=204, summary="Delete employee")
async def delete_employee(
    employee_id: UUID,
    controller: EmployeeController = Depends(get_employee_controller),
) -> None:
    """Delete an employee (cascades to attendance records)."""
    await controller.delete_employee(employee_id)
