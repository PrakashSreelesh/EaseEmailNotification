
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from app.db.session import get_db
from app.models.all_models import User
from app.schemas import schemas
import uuid

router = APIRouter()

@router.post("/login", response_model=schemas.LoginResponse)
async def login(login_data: schemas.LoginRequest, response: Response, db: Session = Depends(get_db)):
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
    
    # 5. Set access_token as httponly cookie for frontend
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,  # Prevents JavaScript access (XSS protection)
        secure=False,   # Set to True in production with HTTPS
        samesite="lax", # CSRF protection
        max_age=7 * 24 * 60 * 60,  # 7 days in seconds
        path="/"  # Available across entire site
    )
    
    # 6. Also set user email in cookie for frontend display
    response.set_cookie(
        key="user_email",
        value=user.email,
        httponly=False,  # Accessible by JavaScript for display
        secure=False,
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
        path="/"
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.full_name or user.email, 
        "role": user.role, 
        "is_superadmin": user.is_superadmin,
        "is_admin": user.is_admin,
        "tenant_id": user.tenant_id
    }


@router.post("/logout")
async def logout(response: Response):
    """
    Logout endpoint - clears authentication cookies
    """
    # Clear access_token cookie
    response.delete_cookie(key="access_token", path="/")
    # Clear user_email cookie
    response.delete_cookie(key="user_email", path="/")
    
    return {"message": "Logged out successfully"}
