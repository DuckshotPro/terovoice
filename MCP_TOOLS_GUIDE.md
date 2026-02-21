# MCP Tools & Powers Guide for Frontend Integration

**Updated:** December 26, 2025
**Purpose:** Guide for using MCPs and tools during frontend-to-database integration

---

## 🎯 Overview

For the frontend integration phase, you have access to 9 MCP servers with auto-approved tools. These will help you:
- Query and manage the database
- Execute commands on the server
- Manage dependencies
- Handle version control
- Monitor containers
- Manage documentation

---

## 📋 Available MCP Servers

### 1. **PostgreSQL MCP** ✅ (Database Queries)
**Status:** Enabled with auto-approval
**Auto-Approved Tools:**
- `query_database` - Execute SQL queries
- `execute_query` - Run custom queries
- `get_schema` - Get database schema

**Use Cases:**
- Query user data
- Check call logs
- Verify data integrity
- Test API responses

**Example:**
```sql
-- Get all clients
SELECT * FROM clients LIMIT 10;

-- Get call statistics
SELECT client_id, COUNT(*) as call_count FROM calls GROUP BY client_id;

-- Check user subscriptions
SELECT * FROM subscriptions WHERE user_id = 'user_id';
```

---

### 2. **pgvector MCP** ✅ (Vector Embeddings)
**Status:** Enabled with auto-approval
**Auto-Approved Tools:**
- `query_database` - Query vectors
- `search_vectors` - Semantic search
- `insert_vectors` - Add embeddings
- `update_vectors` - Update embeddings

**Use Cases:**
- Store call transcripts as vectors
- Search similar calls
- Semantic analysis
- Recommendation engine

**Example:**
```sql
-- Search similar calls
SELECT * FROM call_embeddings
ORDER BY embedding <-> '[0.1, 0.2, 0.3]' LIMIT 5;

-- Store new embedding
INSERT INTO call_embeddings (call_id, embedding)
VALUES ('call_123', '[0.1, 0.2, 0.3]');
```

---

### 3. **SSH MCP** ✅ (Server Commands)
**Status:** Enabled with auto-approval
**Auto-Approved Tools:**
- `execute_command` - Run shell commands
- `read_file` - Read files from server
- `write_file` - Write files to server
- `list_directory` - List server directories

**Use Cases:**
- Deploy backend API
- Check service status
- View logs
- Manage files

**Example:**
```bash
# Check Ollama status
ps aux | grep ollama

# View API logs
tail -f /var/log/api.log

# Deploy backend
docker-compose up -d

# Check database
psql -h 74.208.227.161 -U user -d ai_receptionist -c "SELECT COUNT(*) FROM users;"
```

---

### 4. **GitHub MCP** ✅ (Version Control)
**Status:** Enabled with auto-approval
**Auto-Approved Tools:**
- `create_issue` - Create GitHub issues
- `create_pull_request` - Create PRs
- `read_repository` - Read repo info
- `list_issues` - List issues

**Use Cases:**
- Track integration tasks
- Create PRs for code review
- Document issues
- Manage project

**Example:**
```
# Create issue for backend API
Title: "Implement authentication API endpoints"
Description: "Create POST /api/auth/login, /api/auth/register, etc."

# Create PR for frontend integration
Title: "Add database connection to frontend"
Description: "Connects React frontend to PostgreSQL backend"
```

---

### 5. **Notion MCP** ✅ (Documentation)
**Status:** Enabled with auto-approval
**Auto-Approved Tools:**
- `create_page` - Create Notion pages
- `update_page` - Update pages
- `query_database` - Query Notion databases

**Use Cases:**
- Document API endpoints
- Track progress
- Store design decisions
- Manage requirements

---

### 6. **NPM MCP** ✅ (Dependency Management)
**Status:** Enabled with auto-approval
**Auto-Approved Tools:**
- `search_packages` - Search npm packages
- `get_package_info` - Get package details
- `get_package_versions` - Get version info

**Use Cases:**
- Find packages for authentication
- Check package versions
- Verify compatibility
- Research alternatives

**Example:**
```
# Search for JWT packages
npm search jwt

# Get package info
npm info jsonwebtoken

# Check versions
npm view axios versions
```

---

### 7. **Docker MCP** ✅ (Container Management)
**Status:** Enabled with auto-approval
**Auto-Approved Tools:**
- `list_containers` - List running containers
- `list_images` - List Docker images
- `get_container_logs` - View container logs

**Use Cases:**
- Monitor backend container
- Check deployment status
- View error logs
- Manage containers

**Example:**
```bash
# List running containers
docker ps

# View backend logs
docker logs backend-api

# Check image status
docker images
```

---

### 8. **Git MCP** ✅ (Repository Management)
**Status:** Enabled with auto-approval
**Auto-Approved Tools:**
- `get_repository_status` - Get repo status
- `list_commits` - View commit history
- `get_diff` - View changes

**Use Cases:**
- Track code changes
- Review commits
- Manage branches
- Document changes

---

### 9. **Fetch MCP** ✅ (HTTP Requests)
**Status:** Enabled with auto-approval
**Auto-Approved Tools:**
- `fetch_url` - Fetch URLs
- `get_content` - Get page content

**Use Cases:**
- Test API endpoints
- Fetch documentation
- Verify deployments
- Check external services

---

## 🔐 Auto-Approval Settings

### Current Auto-Approvals

| MCP | Tools | Status |
|-----|-------|--------|
| PostgreSQL | query_database, execute_query, get_schema | ✅ Auto |
| pgvector | query_database, search_vectors, insert_vectors, update_vectors | ✅ Auto |
| SSH | execute_command, read_file, write_file, list_directory | ✅ Auto |
| GitHub | create_issue, create_pull_request, read_repository, list_issues | ✅ Auto |
| Notion | create_page, update_page, query_database | ✅ Auto |
| NPM | search_packages, get_package_info, get_package_versions | ✅ Auto |
| Docker | list_containers, list_images, get_container_logs | ✅ Auto |
| Git | get_repository_status, list_commits, get_diff | ✅ Auto |
| Fetch | fetch_url, get_content | ✅ Auto |

### What This Means
- ✅ These tools will execute without asking for approval
- ✅ Faster workflow during development
- ✅ Automatic database queries
- ✅ Automatic server commands
- ⚠️ Be careful with destructive operations

---

## 🛠️ Tools for Each Phase

### Phase 1: Backend API Setup
**Primary Tools:**
- PostgreSQL MCP - Query database schema
- SSH MCP - Deploy backend
- Docker MCP - Monitor containers
- Git MCP - Track changes

**Example Workflow:**
```
1. Use PostgreSQL MCP to check database schema
2. Use SSH MCP to deploy backend API
3. Use Docker MCP to verify container is running
4. Use Git MCP to commit changes
```

### Phase 2: Frontend Setup
**Primary Tools:**
- NPM MCP - Manage dependencies
- GitHub MCP - Create PRs
- Git MCP - Track changes
- Fetch MCP - Test API endpoints

**Example Workflow:**
```
1. Use NPM MCP to find authentication packages
2. Use Fetch MCP to test API endpoints
3. Use GitHub MCP to create PR
4. Use Git MCP to track changes
```

### Phase 3: Frontend Pages & Components
**Primary Tools:**
- PostgreSQL MCP - Query test data
- Fetch MCP - Test API responses
- GitHub MCP - Create issues for bugs
- Git MCP - Track component changes

**Example Workflow:**
```
1. Use PostgreSQL MCP to get test data
2. Use Fetch MCP to test API responses
3. Use GitHub MCP to create issues
4. Use Git MCP to commit components
```

### Phase 4: Integration & Testing
**Primary Tools:**
- PostgreSQL MCP - Verify data
- Fetch MCP - Test endpoints
- Docker MCP - Monitor services
- SSH MCP - Check logs

**Example Workflow:**
```
1. Use Fetch MCP to test all endpoints
2. Use PostgreSQL MCP to verify data
3. Use Docker MCP to check services
4. Use SSH MCP to view logs
```

### Phase 5: Deployment
**Primary Tools:**
- SSH MCP - Deploy to production
- Docker MCP - Manage containers
- Fetch MCP - Test production endpoints
- GitHub MCP - Create release notes

**Example Workflow:**
```
1. Use SSH MCP to deploy backend
2. Use Docker MCP to verify containers
3. Use Fetch MCP to test endpoints
4. Use GitHub MCP to create release
```

---

## 💡 Usage Examples

### Example 1: Query Database for Testing
```
Use PostgreSQL MCP:
SELECT * FROM users LIMIT 5;
SELECT * FROM clients WHERE user_id = 'test_user';
SELECT COUNT(*) FROM calls;
```

### Example 2: Deploy Backend
```
Use SSH MCP:
ssh password@74.208.227.161 "docker-compose up -d"
ssh password@74.208.227.161 "docker ps"
ssh password@74.208.227.161 "docker logs backend-api"
```

### Example 3: Test API Endpoint
```
Use Fetch MCP:
GET http://localhost:8000/api/auth/login
POST http://localhost:8000/api/clients
GET http://localhost:8000/api/analytics/dashboard
```

### Example 4: Search for Package
```
Use NPM MCP:
Search: "jwt authentication"
Get info: "jsonwebtoken"
Get versions: "axios"
```

### Example 5: Create GitHub Issue
```
Use GitHub MCP:
Title: "Fix authentication bug"
Description: "JWT token not refreshing properly"
Labels: "bug", "authentication"
```

---

## ⚙️ Configuration Details

### MCP Configuration File
**Location:** `.kiro/settings/mcp.json`

**Current Configuration:**
```json
{
  "mcpServers": {
    "postgres": {
      "autoApprove": ["query_database", "execute_query", "get_schema"]
    },
    "pgvector": {
      "autoApprove": ["query_database", "search_vectors", "insert_vectors", "update_vectors"]
    },
    "ssh": {
      "autoApprove": ["execute_command", "read_file", "write_file", "list_directory"]
    },
    "github": {
      "autoApprove": ["create_issue", "create_pull_request", "read_repository", "list_issues"]
    },
    "notion": {
      "autoApprove": ["create_page", "update_page", "query_database"]
    },
    "npm": {
      "autoApprove": ["search_packages", "get_package_info", "get_package_versions"]
    },
    "docker": {
      "autoApprove": ["list_containers", "list_images", "get_container_logs"]
    },
    "git": {
      "autoApprove": ["get_repository_status", "list_commits", "get_diff"]
    },
    "fetch": {
      "autoApprove": ["fetch_url", "get_content"]
    }
  }
}
```

---

## 🔒 Security Considerations

### Auto-Approved Operations
- ✅ Safe: Query operations (SELECT)
- ✅ Safe: Read operations (GET, list)
- ✅ Safe: View operations (logs, status)
- ⚠️ Caution: Write operations (INSERT, UPDATE)
- ⚠️ Caution: Delete operations (DELETE, DROP)
- ⚠️ Caution: Execute operations (shell commands)

### Best Practices
1. **Review before executing** - Even with auto-approval, review commands
2. **Test in staging first** - Don't deploy directly to production
3. **Use transactions** - Wrap database changes in transactions
4. **Backup before changes** - Always backup before major changes
5. **Log all operations** - Keep audit trail of changes

---

## 🚀 Quick Start

### To Use PostgreSQL MCP
```
1. Ask: "Query the users table"
2. Tool automatically executes
3. Results returned instantly
```

### To Use SSH MCP
```
1. Ask: "Check if Ollama is running"
2. Tool automatically executes
3. Results returned instantly
```

### To Use NPM MCP
```
1. Ask: "Find JWT authentication packages"
2. Tool automatically searches
3. Results returned instantly
```

---

## 📞 Troubleshooting

### If Tool Doesn't Execute
1. Check if MCP server is enabled
2. Check if tool is in autoApprove list
3. Check if credentials are correct
4. Try manually approving the operation

### If Tool Fails
1. Check error message
2. Verify parameters are correct
3. Check if service is running
4. Review logs for details

### If You Need to Disable Auto-Approval
Edit `.kiro/settings/mcp.json` and remove tool from `autoApprove` array

---

## 📚 Additional Resources

### MCP Documentation
- PostgreSQL MCP: Query databases
- pgvector MCP: Vector embeddings
- SSH MCP: Remote commands
- GitHub MCP: Repository management
- Docker MCP: Container management

### Tools for Frontend Integration
- **Database:** PostgreSQL MCP
- **Vectors:** pgvector MCP
- **Deployment:** SSH MCP + Docker MCP
- **Version Control:** Git MCP + GitHub MCP
- **Dependencies:** NPM MCP
- **Testing:** Fetch MCP

---

## ✅ Summary

### What You Have
- ✅ 9 MCP servers configured
- ✅ Auto-approval enabled for safe operations
- ✅ Database access configured
- ✅ Server access configured
- ✅ GitHub integration configured

### What You Can Do
- ✅ Query database automatically
- ✅ Execute server commands automatically
- ✅ Manage dependencies automatically
- ✅ Track changes automatically
- ✅ Monitor containers automatically

### What's Next
1. Use these tools during frontend integration
2. Query database for testing
3. Deploy backend API
4. Test API endpoints
5. Track changes with Git/GitHub

---

**You're all set! Use these tools to accelerate your frontend integration! 🚀**
