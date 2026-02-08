
import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from app.db.session import engine
from app.models.all_models import Base

async def recreate_tables():
    async with engine.begin() as conn:
        print("🗑️ Dropping all tables...")
        await conn.run_sync(Base.metadata.drop_all)
        print("✨ Creating all tables...")
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Tables recreated successfully.")

if __name__ == "__main__":
    asyncio.run(recreate_tables())
