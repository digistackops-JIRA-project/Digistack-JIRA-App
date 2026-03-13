from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime
import re


# ── Auth ──────────────────────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


# ── Team ──────────────────────────────────────────────────────────────────────
class TeamCreate(BaseModel):
    team_name: str

    @field_validator("team_name")
    @classmethod
    def team_name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("team_name cannot be empty")
        if len(v) > 150:
            raise ValueError("team_name must be ≤ 150 characters")
        return v


class TeamResponse(BaseModel):
    id: int
    team_name: str
    created_at: datetime

    class Config:
        from_attributes = True


# ── Manager ───────────────────────────────────────────────────────────────────
class ManagerCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    team_id: int

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain an uppercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain a digit")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v and not re.match(r"^\+?[\d\s\-]{7,20}$", v):
            raise ValueError("Invalid phone number")
        return v


class ManagerResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str]
    team_id: int
    team_name: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ── Employee ──────────────────────────────────────────────────────────────────
class EmployeeCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    team_id: int
    manager_id: int

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain an uppercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain a digit")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v and not re.match(r"^\+?[\d\s\-]{7,20}$", v):
            raise ValueError("Invalid phone number")
        return v


class EmployeeResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str]
    team_id: int
    team_name: Optional[str] = None
    manager_id: int
    manager_name: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class EmployeesByManager(BaseModel):
    manager_id: int
    manager_name: str
    employees: List[EmployeeResponse]


# ── Health ────────────────────────────────────────────────────────────────────
class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str


class LivenessResponse(BaseModel):
    status: str


class ReadinessResponse(BaseModel):
    status: str
    database: str
