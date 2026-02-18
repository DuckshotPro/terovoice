-- Query pgvector database for server and website setup information
-- List all tables
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
