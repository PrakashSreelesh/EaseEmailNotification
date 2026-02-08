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

from app.core.config import settings
import aiosmtplib
from email.message import EmailMessage

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

    # Send Invitation Email for Tenant Admins
    try:
        if user.role == 'admin' and user.tenant_id:
            # Fetch tenant name
            tenant_res = await db.execute(select(Tenant).where(Tenant.id == user.tenant_id))
            tenant_obj = tenant_res.scalars().first()
            tenant_name = tenant_obj.name if tenant_obj else "EaseEmail"

            message = EmailMessage()
            message["From"] = settings.DEFAULT_FROM_EMAIL
            message["To"] = user.email
            message["Subject"] = f"{user.full_name or 'User'} - Verify Your Email"

            body = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <meta charset="UTF-8">
            <title>EaseEmail Account Details</title>
            </head>
            <body style="margin:0; padding:0; background-color:#f4f6f8; font-family:Arial, sans-serif;">
            
            <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f6f8; padding:20px 0;">
                <tr>
                <td align="center">
                    
                    <!-- Main container -->
                    <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff; border-radius:8px; overflow:hidden; box-shadow:0 2px 6px rgba(0,0,0,0.08);">
                    
                    <!-- Header -->
                    <tr>
                        <td style="background:#1f2937; color:#ffffff; padding:20px; text-align:center; font-size:22px; font-weight:bold;">
                        EaseEmail
                        </td>
                    </tr>

                    <!-- Body -->
                    <tr>
                        <td style="padding:30px; color:#333333; font-size:15px; line-height:1.6;">
                        
                        <p>
                            Your company <strong>"{tenant_name}"</strong> has been successfully registered in <strong>EaseEmail</strong>.
                        </p>

                        <p>Please use the credentials below to log in to your account:</p>

                        <!-- Credentials box -->
                        <table width="100%" cellpadding="10" cellspacing="0" style="background:#f9fafb; border:1px solid #e5e7eb; border-radius:6px; margin:15px 0;">
                            <tr>
                            <td style="font-size:14px;">
                                <strong>Username:</strong> {user.email}
                            </td>
                            </tr>
                            <tr>
                            <td style="font-size:14px;">
                                <strong>Password:</strong> {user.password}
                            </td>
                            </tr>
                        </table>

                        <!-- Button -->
                        <p style="text-align:center; margin:25px 0;">
                            <a href="http://0.0.0.0:8000/" 
                            style="background:#2563eb; color:#ffffff; padding:12px 24px; text-decoration:none; border-radius:5px; font-weight:bold; display:inline-block;">
                            Login to EaseEmail
                            </a>
                        </p>

                        <p style="font-size:13px; color:#666666;">
                            If you did not request this account, please ignore this email.
                        </p>

                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="background:#f3f4f6; padding:15px; text-align:center; font-size:12px; color:#888888;">
                        © 2026 EaseEmail. All rights reserved.
                        </td>
                    </tr>

                    </table>
                    <!-- End container -->

                </td>
                </tr>
            </table>

            </body>
            </html>
            """
            message.set_content(body, subtype='html')

            if settings.EMAIL_HOST and settings.EMAIL_PORT:
                await aiosmtplib.send(
                    message,
                    hostname=settings.EMAIL_HOST,
                    port=settings.EMAIL_PORT,
                    username=settings.EMAIL_HOST_USER,
                    password=settings.EMAIL_HOST_PASSWORD,
                    start_tls=settings.EMAIL_USE_TLS, # aiosmtplib uses start_tls for TLS
                )
    except Exception as e:
        print(f"Failed to send invitation email: {e}")

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
        query = select(func.count(User.id)).where(User.is_superadmin == False)

        # For dashboard counts, be more permissive
        # Only filter by tenant if explicitly provided
        if tenant_id:
            query = query.where(User.tenant_id == tenant_id)
        # If no tenant_id provided, return total count (for dashboard overview)

        result = await db.execute(query)
        count = result.scalar()
        return {"count": count}

    # Base query joined with Tenant - be permissive like count query
    query = select(User).options(joinedload(User.tenant)).where(User.is_superadmin == False).offset(skip).limit(limit)

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
