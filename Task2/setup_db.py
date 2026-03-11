import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv(override=True)

# The entire schema directly in Python! No external files needed.
SCHEMA_SQL = """
-- 1. CLEAN SLATE
DROP TABLE IF EXISTS call_records CASCADE;
DROP TYPE IF EXISTS interaction_channel CASCADE;
DROP TYPE IF EXISTS interaction_outcome CASCADE;

-- 2. CREATE ENUMS
CREATE TYPE interaction_channel AS ENUM ('voice', 'whatsapp', 'chat');
CREATE TYPE interaction_outcome AS ENUM ('resolved', 'escalated', 'failed');

-- 3. CREATE MAIN TABLE
CREATE TABLE call_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_phone VARCHAR(20) NOT NULL,
    channel interaction_channel NOT NULL,
    intent_type VARCHAR(100) NOT NULL, 
    transcript TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    outcome interaction_outcome NOT NULL,
    confidence_score NUMERIC(3, 2) NOT NULL CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    csat_score INTEGER NULL CHECK (csat_score >= 1 AND csat_score <= 5),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    duration_seconds INTEGER NOT NULL
);

-- 4. CREATE INDEXES
CREATE INDEX idx_call_records_phone ON call_records(customer_phone);
CREATE INDEX idx_call_records_created_at ON call_records(created_at);
CREATE INDEX idx_call_records_intent_outcome ON call_records(intent_type, outcome);
"""

async def setup_database():
    db_url = os.getenv("DATABASE_URL")
    print("🔌 Connecting to the database...")
    
    try:
        conn = await asyncpg.connect(db_url)
        print("✅ Connected!")
        
        print("🏗️ Building tables and custom types...")
        await conn.execute(SCHEMA_SQL)
        print("🎉 Success! The call_records table is ready.")
        
    except Exception as e:
        print(f"❌ Error setting up database: {str(e)}")
        
    finally:
        if 'conn' in locals():
            await conn.close()

if __name__ == "__main__":
    asyncio.run(setup_database())