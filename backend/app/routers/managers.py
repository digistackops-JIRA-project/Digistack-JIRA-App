from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.database import get_db
from app.models import Manager, Team
from app.schemas import ManagerCreate, ManagerResponse
from app.security import get_current_admin, hash_password

router = APIRouter()


def _build_response(mgr: Manager) -> ManagerResponse:
    return ManagerResponse(
        id=mgr.id,
        name=mgr.name,
        email=mgr.email,
        phone=mgr.phone,
        team_id=mgr.team_id,
        team_name=mgr.team.team_name if mgr.team else None,
        is_active=mgr.is_active,
        created_at=mgr.created_at,
    )


@router.get("/", response_model=List[ManagerResponse])
def list_managers(
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin),
):
    managers = (
        db.query(Manager)
        .options(joinedload(Manager.team))
        .order_by(Manager.name)
        .all()
    )
    return [_build_response(m) for m in managers]


@router.post("/", response_model=ManagerResponse, status_code=status.HTTP_201_CREATED)
def create_manager(
    payload: ManagerCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin),
):
    if not db.query(Team).filter(Team.id == payload.team_id).first():
        raise HTTPException(status_code=404, detail="Team not found")
    if db.query(Manager).filter(Manager.email == payload.email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    mgr = Manager(
        name=payload.name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        phone=payload.phone,
        team_id=payload.team_id,
    )
    db.add(mgr)
    db.commit()
    db.refresh(mgr)
    # reload with team relation
    mgr = db.query(Manager).options(joinedload(Manager.team)).filter(Manager.id == mgr.id).first()
    return _build_response(mgr)


@router.put("/{manager_id}", response_model=ManagerResponse)
def update_manager(
    manager_id: int,
    payload: ManagerCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin),
):
    mgr = db.query(Manager).filter(Manager.id == manager_id).first()
    if not mgr:
        raise HTTPException(status_code=404, detail="Manager not found")
    if not db.query(Team).filter(Team.id == payload.team_id).first():
        raise HTTPException(status_code=404, detail="Team not found")
    duplicate = (
        db.query(Manager)
        .filter(Manager.email == payload.email, Manager.id != manager_id)
        .first()
    )
    if duplicate:
        raise HTTPException(status_code=409, detail="Email already registered")

    mgr.name = payload.name
    mgr.email = payload.email
    mgr.hashed_password = hash_password(payload.password)
    mgr.phone = payload.phone
    mgr.team_id = payload.team_id
    db.commit()
    db.refresh(mgr)
    mgr = db.query(Manager).options(joinedload(Manager.team)).filter(Manager.id == mgr.id).first()
    return _build_response(mgr)


@router.delete("/{manager_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_manager(
    manager_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin),
):
    mgr = db.query(Manager).filter(Manager.id == manager_id).first()
    if not mgr:
        raise HTTPException(status_code=404, detail="Manager not found")
    if mgr.employees:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete manager with assigned employees",
        )
    db.delete(mgr)
    db.commit()
