from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.db.session import get_db
from app.models.all_models import Tenant
from app.schemas.schemas import TenantCreate, TenantResponse

router = APIRouter()

@router.post("/", response_model=TenantResponse)
async def create_tenant(tenant: TenantCreate, db: AsyncSession = Depends(get_db)):
    # Check if tenant with same name exists
    existing = await db.execute(select(Tenant).where(Tenant.name == tenant.name))
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="Tenant with this name already exists")
    
    new_tenant = Tenant(name=tenant.name)
    db.add(new_tenant)
    await db.commit()
    await db.refresh(new_tenant)
    return new_tenant

@router.get("/", response_model=List[TenantResponse])
async def read_tenants(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tenant).offset(skip).limit(limit))
    tenants = result.scalars().all()
    return tenants

@router.get("/{tenant_id}", response_model=TenantResponse)
async def read_tenant(tenant_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalars().first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant

@router.delete("/{tenant_id}", status_code=204)
async def delete_tenant(tenant_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalars().first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    await db.delete(tenant)
    await db.commit()
    return None

@router.patch("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(tenant_id: str, tenant_update: TenantCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    db_tenant = result.scalars().first()
    if not db_tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    db_tenant.name = tenant_update.name
    
    await db.commit()
    await db.refresh(db_tenant)
    return db_tenant
