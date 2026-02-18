-- Database migration to add onboarding-related tables
-- Run this SQL script to add the new tables for the PayPal purchase & onboarding system

-- OnboardingState table
CREATE TABLE IF NOT EXISTS onboarding_states (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) UNIQUE,
    current_step INTEGER DEFAULT 1,
    progress INTEGER DEFAULT 0,
    completed_steps JSON DEFAULT '[]',

    -- Business Information (Step 1)
    business_name VARCHAR,
    industry VARCHAR,
    business_phone VARCHAR,
    service_description TEXT,
    business_documents JSON DEFAULT '[]',

    -- Phone Configuration (Step 2)
    forwarding_number VARCHAR,
    sms_enabled BOOLEAN DEFAULT FALSE,
    sms_phone_number VARCHAR,

    -- Caller Responses (Step 3)
    caller_responses JSONB DEFAULT '{}',

    -- Calendar Integration (Step 4)
    calendar_provider VARCHAR,
    calendar_connected BOOLEAN DEFAULT FALSE,
    calendar_access_token VARCHAR,
    calendar_refresh_token VARCHAR,

    -- Demo Status (Step 5)
    demo_completed BOOLEAN DEFAULT FALSE,
    demo_transcripts JSON DEFAULT '[]',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ConversationLog table
CREATE TABLE IF NOT EXISTS conversation_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    call_id UUID NOT NULL REFERENCES calls(id),
    user_id UUID NOT NULL REFERENCES users(id),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Conversation data
    user_utterance TEXT,
    user_audio_url VARCHAR,
    ai_response TEXT,
    ai_audio_url VARCHAR,

    -- Technical metadata
    stt_provider VARCHAR,
    tts_provider VARCHAR,
    confidence FLOAT,
    sentiment VARCHAR,
    intent VARCHAR,

    -- Business metadata
    industry VARCHAR,
    profession VARCHAR,
    call_type VARCHAR,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AnalyticsEvent table
CREATE TABLE IF NOT EXISTS analytics_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    event_type VARCHAR NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Event data
    event_data JSONB DEFAULT '{}',
    session_id VARCHAR,
    metadata JSONB DEFAULT '{}',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- PayPalOrder table
CREATE TABLE IF NOT EXISTS paypal_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paypal_order_id VARCHAR UNIQUE NOT NULL,
    user_id UUID REFERENCES users(id),

    -- Order details
    plan_id VARCHAR NOT NULL,
    amount FLOAT NOT NULL,
    currency VARCHAR DEFAULT 'USD',
    status VARCHAR DEFAULT 'created',

    -- PayPal data
    paypal_payer_id VARCHAR,
    paypal_capture_id VARCHAR,
    paypal_data JSONB DEFAULT '{}',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_onboarding_states_user_id ON onboarding_states(user_id);
CREATE INDEX IF NOT EXISTS idx_conversation_logs_call_id ON conversation_logs(call_id);
CREATE INDEX IF NOT EXISTS idx_conversation_logs_user_id ON conversation_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_analytics_events_user_id ON analytics_events(user_id);
CREATE INDEX IF NOT EXISTS idx_analytics_events_event_type ON analytics_events(event_type);
CREATE INDEX IF NOT EXISTS idx_analytics_events_timestamp ON analytics_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_paypal_orders_paypal_order_id ON paypal_orders(paypal_order_id);
CREATE INDEX IF NOT EXISTS idx_paypal_orders_user_id ON paypal_orders(user_id);

-- Update triggers for updated_at columns
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_onboarding_states_updated_at
    BEFORE UPDATE ON onboarding_states
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_paypal_orders_updated_at
    BEFORE UPDATE ON paypal_orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();