from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Team
from app.schemas import TeamCreate, TeamResponse
from app.security import get_current_admin

router = APIRouter()


@router.get("/", response_model=List[TeamResponse])
def list_teams(
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin),
):
    """Return all teams (used to populate dropdowns)."""
    return db.query(Team).order_by(Team.team_name).all()


@router.post("/", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
def create_team(
    payload: TeamCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin),
):
    """Create a new team."""
    existing = db.query(Team).filter(Team.team_name == payload.team_name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Team '{payload.team_name}' already exists",
        )
    team = Team(team_name=payload.team_name)
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(
    team_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin),
):
    """Delete a team (only if no managers/employees assigned)."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    if team.managers or team.employees:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete team with active managers or employees",
        )
    db.delete(team)
    db.commit()
