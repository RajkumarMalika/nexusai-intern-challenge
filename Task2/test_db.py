import asyncio
import asyncpg
import os
from dotenv import load_dotenv
from repository import CallRecordRepository

# Load environment variables (Make sure you add DATABASE_URL to your .env)
load_dotenv()

async def run_db_tests():
    # 1. Get the database connection string from the environment
    # Example format: postgresql://username:password@localhost:5432/your_db_name
    db_url = os.getenv("DATABASE_URL")
    
    if not db_url:
        print("❌ Error: DATABASE_URL is missing from your .env file.")
        return

    print("🔌 Connecting to PostgreSQL...")
    
    try:
        # 2. Create the connection pool
        pool = await asyncpg.create_pool(dsn=db_url)
        repo = CallRecordRepository(pool)
        
        # 3. Test saving a record
        print("\n📝 Test 1: Saving a new call record...")
        dummy_data = {
            "customer_phone": "+1234567890",
            "channel": "voice",
            "intent_type": "billing_dispute",
            "transcript": "Customer: I was overcharged. AI: Let me look into that.",
            "ai_response": "Let me look into that.",
            "outcome": "resolved",
            "confidence_score": 0.95,
            "csat_score": 5, # 1-5 allowed
            "duration_seconds": 120
        }
        
        record_id = await repo.save(dummy_data)
        print(f"✅ PASS: Record saved successfully with ID: {record_id}")
        
        # 4. Test retrieving recent records
        print("\n🔍 Test 2: Fetching recent records for +1234567890...")
        recent_calls = await repo.get_recent("+1234567890", limit=3)
        print(f"✅ PASS: Found {len(recent_calls)} records.")
        for call in recent_calls:
            print(f"   -> Intent: {call['intent_type']} | Outcome: {call['outcome']} | CSAT: {call['csat_score']}")
            
        # 5. Test the complex analytics query
        print("\n📊 Test 3: Fetching lowest resolution intents...")
        analytics = await repo.get_lowest_resolution_intents()
        print(f"✅ PASS: Query executed successfully.")
        for stat in analytics:
             print(f"   -> Intent: {stat['intent_type']} | Resolution Rate: {stat['resolution_rate_percentage']}% | Avg CSAT: {stat['average_csat']}")

    except Exception as e:
        print(f"\n❌ Test Failed: {str(e)}")
        
    finally:
        # Always close the pool to prevent memory leaks
        if 'pool' in locals():
            await pool.close()
            print("\n🔒 Connection pool closed.")

if __name__ == "__main__":
    asyncio.run(run_db_tests())