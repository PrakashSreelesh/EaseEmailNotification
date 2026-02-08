from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from typing import List, Optional, Union
from app.db.session import get_db
from app.models.all_models import User, Tenant
from app.schemas.schemas import UserCreate, UserResponse, UserBase
from sqlalchemy.orm import joinedload
from pydantic import BaseModel

class CountResponse(BaseModel):
    count: int

router = APIRouter()

@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # Check if email exists
    existing = await db.execute(select(User).where(User.email == user.email))
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=user.password, # In real app, hash this!
        role=user.role,
        is_superadmin=user.is_superadmin,
        is_admin=user.is_admin,
        tenant_id=user.tenant_id,
        is_active=user.is_active
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.get("/")
async def read_users(
    skip: int = 0,
    limit: int = 100,
    tenant_id: Optional[str] = Query(None),
    is_superadmin: bool = Query(False),
    count_only: bool = Query(False),
    db: AsyncSession = Depends(get_db)
):
    # If count_only is requested, return count
    if count_only:
        # Base count query
        query = select(func.count(User.id))

        # For dashboard counts, be more permissive
        # Only filter by tenant if explicitly provided
        if tenant_id:
            query = query.where(User.tenant_id == tenant_id)
        # If no tenant_id provided, return total count (for dashboard overview)

        result = await db.execute(query)
        count = result.scalar()
        return {"count": count}

    # Base query joined with Tenant - be permissive like count query
    query = select(User).options(joinedload(User.tenant)).offset(skip).limit(limit)

    # For list queries, be more permissive
    # Only filter by tenant if explicitly provided
    if tenant_id:
        query = query.where(User.tenant_id == tenant_id)
    # If no tenant_id provided, return all (for admin overview)

    result = await db.execute(query)
    users = result.scalars().all()

    # Populate tenant_name for response
    for u in users:
        u.tenant_name = u.tenant.name if u.tenant else "Unknown"

    return users

@router.get("/me", response_model=UserResponse)
async def read_user_me(email: str = Query(...), db: AsyncSession = Depends(get_db)):
    # Mock endpoint for demo - find user by email
    result = await db.execute(select(User).options(joinedload(User.tenant)).where(User.email == email))
    user = result.scalars().first()
    if user:
        user.tenant_name = user.tenant.name if user.tenant else "Unknown"
    return user

@router.get("/{user_id}", response_model=UserResponse)
async def read_user(user_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await db.delete(user)
    await db.commit()
    return None

@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user_update: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    db_user = result.scalars().first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_user.full_name = user_update.full_name
    db_user.email = user_update.email
    if user_update.password: # Only update if password provided
        db_user.hashed_password = user_update.password 
    db_user.role = user_update.role
    db_user.is_superadmin = user_update.is_superadmin
    db_user.is_admin = user_update.is_admin
    db_user.is_active = user_update.is_active
    db_user.tenant_id = user_update.tenant_id
    
    await db.commit()
    await db.refresh(db_user)
    return db_user
