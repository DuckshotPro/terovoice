"""
Database migration to add onboarding-related tables.
Run this script to add the new tables for the PayPal purchase & onboarding system.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from sqlalchemy import create_engine, text
from backend_setup.db.models import Base

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/tero_voice')

def run_migration():
    """Run the migration to add onboarding tables."""
    try:
        engine = create_engine(DATABASE_URL)
        
        print("Creating onboarding-related tables...")
        
        # Create all tables defined in models.py
        # This will only create tables that don't exist yet
        Base.metadata.create_all(bind=engine)
        
        print("✅ Migration completed successfully!")
        print("New tables added:")
        print("  - onboarding_states")
        print("  - conversation_logs") 
        print("  - analytics_events")
        print("  - paypal_orders")
        
        # Verify tables were created
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('onboarding_states', 'conversation_logs', 'analytics_events', 'paypal_orders')
                ORDER BY table_name;
            """))
            
            tables = [row[0] for row in result]
            print(f"\nVerified tables exist: {tables}")
            
            if len(tables) == 4:
                print("✅ All tables created successfully!")
            else:
                print(f"⚠️  Only {len(tables)}/4 tables found. Check for errors.")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        raise

if __name__ == "__main__":
    run_migration()