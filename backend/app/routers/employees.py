from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.database import get_db
from app.models import Employee, Team, Manager
from app.schemas import EmployeeCreate, EmployeeResponse, EmployeesByManager
from app.security import get_current_admin, hash_password

router = APIRouter()


def _build_response(emp: Employee) -> EmployeeResponse:
    return EmployeeResponse(
        id=emp.id,
        name=emp.name,
        email=emp.email,
        phone=emp.phone,
        team_id=emp.team_id,
        team_name=emp.team.team_name if emp.team else None,
        manager_id=emp.manager_id,
        manager_name=emp.manager.name if emp.manager else None,
        is_active=emp.is_active,
        created_at=emp.created_at,
    )


def _load(emp_id: int, db: Session) -> Employee:
    return (
        db.query(Employee)
        .options(joinedload(Employee.team), joinedload(Employee.manager))
        .filter(Employee.id == emp_id)
        .first()
    )


@router.get("/", response_model=List[EmployeeResponse])
def list_employees(
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin),
):
    emps = (
        db.query(Employee)
        .options(joinedload(Employee.team), joinedload(Employee.manager))
        .order_by(Employee.name)
        .all()
    )
    return [_build_response(e) for e in emps]


@router.get("/by-manager", response_model=List[EmployeesByManager])
def employees_by_manager(
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin),
):
    """Return employees segregated by manager — used in the admin list view."""
    managers = (
        db.query(Manager)
        .options(
            joinedload(Manager.employees).joinedload(Employee.team),
            joinedload(Manager.employees).joinedload(Employee.manager),
        )
        .order_by(Manager.name)
        .all()
    )
    result = []
    for mgr in managers:
        result.append(
            EmployeesByManager(
                manager_id=mgr.id,
                manager_name=mgr.name,
                employees=[_build_response(e) for e in mgr.employees],
            )
        )
    return result


@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(
    payload: EmployeeCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin),
):
    if not db.query(Team).filter(Team.id == payload.team_id).first():
        raise HTTPException(status_code=404, detail="Team not found")
    if not db.query(Manager).filter(Manager.id == payload.manager_id).first():
        raise HTTPException(status_code=404, detail="Manager not found")
    if db.query(Employee).filter(Employee.email == payload.email).first():
        raise HTTPException(status_code=409, detail="Email already registered")

    emp = Employee(
        name=payload.name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        phone=payload.phone,
        team_id=payload.team_id,
        manager_id=payload.manager_id,
    )
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return _build_response(_load(emp.id, db))


@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: int,
    payload: EmployeeCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin),
):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    if not db.query(Team).filter(Team.id == payload.team_id).first():
        raise HTTPException(status_code=404, detail="Team not found")
    if not db.query(Manager).filter(Manager.id == payload.manager_id).first():
        raise HTTPException(status_code=404, detail="Manager not found")
    dup = (
        db.query(Employee)
        .filter(Employee.email == payload.email, Employee.id != employee_id)
        .first()
    )
    if dup:
        raise HTTPException(status_code=409, detail="Email already registered")

    emp.name = payload.name
    emp.email = payload.email
    emp.hashed_password = hash_password(payload.password)
    emp.phone = payload.phone
    emp.team_id = payload.team_id
    emp.manager_id = payload.manager_id
    db.commit()
    return _build_response(_load(employee_id, db))


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin),
):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(emp)
    db.commit()
