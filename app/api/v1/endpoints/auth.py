
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from app.db.session import get_db
from app.models.all_models import User
from app.schemas import schemas
import uuid

router = APIRouter()

@router.post("/login", response_model=schemas.LoginResponse)
async def login(login_data: schemas.LoginRequest, db: Session = Depends(get_db)):
    # 1. Check user exists
    result = await db.execute(select(User).where(User.email == login_data.email))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # 2. Validate password (plain text check as per current setup)
    if user.hashed_password != login_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    # 3. Validation for active status
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    # 4. Generate token
    access_token = str(uuid.uuid4())
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.full_name or user.email, 
        "role": user.role, 
        "is_superadmin": user.is_superadmin,
        "is_admin": user.is_admin,
        "tenant_id": user.tenant_id
    }
