import asyncio
import sys
import os
from sqlalchemy import text

# Add project root to path
sys.path.append(os.getcwd())

from app.db.session import engine

async def fix():
    async with engine.begin() as conn:
        print("🔍 Checking and fixing smtp_configurations table...")
        
        # Add 'name' column if it doesn't exist
        await conn.execute(text('ALTER TABLE smtp_configurations ADD COLUMN IF NOT EXISTS name VARCHAR;'))
        
        # Let's also check for other potential missing columns from recent updates
        # Check current columns
        res = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'smtp_configurations';"))
        columns = [r[0] for r in res]
        print(f"Current columns: {columns}")
        
        # Based on model, let's ensure these exist too (just in case)
        # provider, host, port, username, password_encrypted, use_tls
        required_cols = {
            'provider': 'VARCHAR DEFAULT \'custom\'',
            'host': 'VARCHAR',
            'port': 'INTEGER',
            'username': 'VARCHAR',
            'password_encrypted': 'VARCHAR',
            'use_tls': 'BOOLEAN DEFAULT TRUE'
        }
        
        for col, col_type in required_cols.items():
            if col not in columns:
                print(f"Adding missing column: {col}")
                await conn.execute(text(f'ALTER TABLE smtp_configurations ADD COLUMN {col} {col_type};'))
        
        print("✅ Schema check complete.")

if __name__ == "__main__":
    asyncio.run(fix())
