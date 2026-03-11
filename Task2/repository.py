import asyncpg
from typing import List, Dict, Any

class CallRecordRepository:
    def __init__(self, pool: asyncpg.Pool):
        """
        Initializes the repository with an active asyncpg connection pool.
        Connection pools are standard for production apps to handle multiple requests.
        """
        self.pool = pool

    async def save(self, call_data: dict) -> str:
        """Saves a new interaction record to the database."""
        query = """
            INSERT INTO call_records (
                customer_phone, channel, intent_type, transcript, 
                ai_response, outcome, confidence_score, csat_score, duration_seconds
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9
            ) RETURNING id;
        """
        
        # Using acquire() gets a connection from the pool
        async with self.pool.acquire() as conn:
            # $1 through $9 map exactly to the arguments passed here
            record_id = await conn.fetchval(
                query,
                call_data['customer_phone'],
                call_data['channel'],
                call_data['intent_type'],
                call_data['transcript'],
                call_data['ai_response'],
                call_data['outcome'],
                call_data['confidence_score'],
                call_data.get('csat_score'), # Handles None perfectly for nullable columns
                call_data['duration_seconds']
            )
            return str(record_id)

    async def get_recent(self, phone: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Fetches the most recent interactions for a specific phone number."""
        query = """
            SELECT id, customer_phone, channel, intent_type, transcript, 
                   ai_response, outcome, confidence_score, csat_score, 
                   created_at, duration_seconds
            FROM call_records
            WHERE customer_phone = $1
            ORDER BY created_at DESC
            LIMIT $2;
        """
        async with self.pool.acquire() as conn:
            records = await conn.fetch(query, phone, limit)
            # asyncpg returns Record objects, we convert them to standard Python dictionaries
            return [dict(record) for record in records]

    async def get_lowest_resolution_intents(self) -> List[Dict[str, Any]]:
        """
        Returns the top 5 intent types with the lowest resolution rate 
        in the last 7 days, along with their average CSAT.
        """
        query = """
            SELECT 
                intent_type,
                -- Calculate resolution rate: (resolved count / total count) * 100
                -- We use Postgres' native FILTER clause which is faster than a CASE statement
                ROUND(
                    (COUNT(*) FILTER (WHERE outcome = 'resolved')::numeric / COUNT(*)) * 100, 
                2) AS resolution_rate_percentage,
                
                -- Calculate average CSAT (Nulls are automatically ignored by AVG)
                ROUND(AVG(csat_score), 2) AS average_csat
            FROM call_records
            WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
            GROUP BY intent_type
            ORDER BY resolution_rate_percentage ASC
            LIMIT 5;
        """
        async with self.pool.acquire() as conn:
            records = await conn.fetch(query)
            return [dict(record) for record in records]