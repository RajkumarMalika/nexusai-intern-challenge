-- ==========================================
-- 1. CLEAN SLATE (Safe to run multiple times)
-- ==========================================
DROP TABLE IF EXISTS call_records CASCADE;
DROP TYPE IF EXISTS interaction_channel CASCADE;
DROP TYPE IF EXISTS interaction_outcome CASCADE;

-- ==========================================
-- 2. CREATE ENUMS
-- ==========================================
CREATE TYPE interaction_channel AS ENUM ('voice', 'whatsapp', 'chat');
CREATE TYPE interaction_outcome AS ENUM ('resolved', 'escalated', 'failed');

-- ==========================================
-- 3. CREATE MAIN TABLE
-- ==========================================
CREATE TABLE call_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_phone VARCHAR(20) NOT NULL,
    channel interaction_channel NOT NULL,
    intent_type VARCHAR(100) NOT NULL, 
    transcript TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    outcome interaction_outcome NOT NULL,
    
    -- Constraint 1: Confidence stays between 0 and 1
    confidence_score NUMERIC(3, 2) NOT NULL 
        CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
        
    -- Constraint 2: CSAT only accepts values 1-5
    csat_score INTEGER NULL 
        CHECK (csat_score >= 1 AND csat_score <= 5),
        
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    duration_seconds INTEGER NOT NULL
);

-- ==========================================
-- ==========================================
-- 4. CREATE INDEXES
-- ==========================================

-- WHY: We frequently query recent interactions by customer phone number (e.g., loading history). 
-- This index prevents full table scans and makes these lookups instantaneous.
CREATE INDEX idx_call_records_phone ON call_records(customer_phone);

-- WHY: Time-based queries (like "in the last 7 days") are extremely common for reporting. 
-- This index speeds up filtering by date ranges.
CREATE INDEX idx_call_records_created_at ON call_records(created_at);

-- WHY: A composite index specifically to optimize our analytics query. 
-- Since we GROUP BY intent_type and FILTER BY outcome, indexing them together drastically speeds up the aggregation.
CREATE INDEX idx_call_records_intent_outcome ON call_records(intent_type, outcome);