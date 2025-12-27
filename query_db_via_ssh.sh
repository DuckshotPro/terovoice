#!/bin/bash

# Query pgvector database for server/website setup
# This script runs on the remote server via SSH

echo "=== Querying pgvector Database ==="
echo ""

# Try using psql if available, otherwise use Python
if command -v psql &> /dev/null; then
    echo "Using psql to query database..."
    PGPASSWORD=cira psql -h localhost -U user -d ai_receptionist << 'EOFPSQL'
-- List all tables
\dt

-- Show table structures
\d

-- Look for setup/config data
SELECT * FROM information_schema.tables WHERE table_schema = 'public';
EOFPSQL
else
    echo "psql not found, using Python..."
    python3 << 'EOFPYTHON'
import sys
import os

# Try to connect using available Python libraries
try:
    # First try psycopg2
    try:
        import psycopg2
        print("Using psycopg2...")
        conn = psycopg2.connect(
            host='localhost',
            database='ai_receptionist',
            user='user',
            password='cira',
            port=5432
        )
    except ImportError:
        # Try psycopg3
        import psycopg
        print("Using psycopg3...")
        conn = psycopg.connect(
            host='localhost',
            database='ai_receptionist',
            user='user',
            password='cira',
            port=5432
        )
    
    cur = conn.cursor()
    
    # Get all tables
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    
    tables = cur.fetchall()
    print("\n=== Tables in ai_receptionist database ===")
    for table in tables:
        print(f"  - {table[0]}")
    
    # Get detailed info for each table
    print("\n=== Table Details ===")
    for table in tables:
        table_name = table[0]
        cur.execute(f"""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = %s
            ORDER BY ordinal_position;
        """, (table_name,))
        
        columns = cur.fetchall()
        print(f"\n{table_name}:")
        for col in columns:
            nullable = "NULL" if col[2] == 'YES' else "NOT NULL"
            print(f"  - {col[0]}: {col[1]} ({nullable})")
    
    # Try to find setup/config related data
    print("\n=== Searching for Setup/Config Data ===")
    
    # Check for common setup table names
    setup_keywords = ['server', 'website', 'config', 'setup', 'deploy', 'settings', 'client']
    
    for table in tables:
        table_name = table[0]
        # Check if table name contains setup keywords
        if any(keyword in table_name.lower() for keyword in setup_keywords):
            try:
                cur.execute(f"SELECT * FROM {table_name} LIMIT 3;")
                rows = cur.fetchall()
                if rows:
                    print(f"\n{table_name} (first 3 rows):")
                    print(rows)
            except Exception as e:
                print(f"  Error querying {table_name}: {e}")
    
    cur.close()
    conn.close()
    print("\n✓ Query completed successfully")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
EOFPYTHON
fi
