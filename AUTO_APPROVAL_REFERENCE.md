# Auto-Approval Reference Guide

**Updated:** December 26, 2025  
**Purpose:** Quick reference for auto-approved MCP tools

---

## ✅ Auto-Approved Tools (No Confirmation Needed)

### PostgreSQL MCP
```
✅ query_database      - Execute SQL SELECT queries
✅ execute_query       - Run custom SQL queries
✅ get_schema          - Get database schema information
```

### pgvector MCP
```
✅ query_database      - Query vector embeddings
✅ search_vectors      - Semantic search on vectors
✅ insert_vectors      - Add new vector embeddings
✅ update_vectors      - Update existing vectors
```

### SSH MCP
```
✅ execute_command     - Run shell commands on server
✅ read_file           - Read files from server
✅ write_file          - Write files to server
✅ list_directory      - List server directories
```

### GitHub MCP
```
✅ create_issue        - Create GitHub issues
✅ create_pull_request - Create pull requests
✅ read_repository     - Read repository information
✅ list_issues         - List GitHub issues
```

### Notion MCP
```
✅ create_page         - Create Notion pages
✅ update_page         - Update Notion pages
✅ query_database      - Query Notion databases
```

### NPM MCP
```
✅ search_packages     - Search npm packages
✅ get_package_info    - Get package information
✅ get_package_versions - Get package versions
```

### Docker MCP
```
✅ list_containers     - List Docker containers
✅ list_images         - List Docker images
✅ get_container_logs  - View container logs
```

### Git MCP
```
✅ get_repository_status - Get git status
✅ list_commits        - View commit history
✅ get_diff            - View file changes
```

### Fetch MCP
```
✅ fetch_url           - Fetch URLs
✅ get_content         - Get page content
```

---

## 🎯 Use Cases by Phase

### Phase 1: Backend API Setup
**Use These Tools:**
- PostgreSQL MCP: `query_database` - Check schema
- SSH MCP: `execute_command` - Deploy backend
- Docker MCP: `list_containers` - Verify running
- Git MCP: `get_repository_status` - Track changes

### Phase 2: Frontend Setup
**Use These Tools:**
- NPM MCP: `search_packages` - Find dependencies
- Fetch MCP: `fetch_url` - Test endpoints
- GitHub MCP: `create_pull_request` - Create PR
- Git MCP: `list_commits` - Track changes

### Phase 3: Frontend Pages & Components
**Use These Tools:**
- PostgreSQL MCP: `query_database` - Get test data
- Fetch MCP: `fetch_url` - Test API responses
- GitHub MCP: `create_issue` - Report bugs
- Git MCP: `get_diff` - Review changes

### Phase 4: Integration & Testing
**Use These Tools:**
- PostgreSQL MCP: `query_database` - Verify data
- Fetch MCP: `fetch_url` - Test all endpoints
- Docker MCP: `get_container_logs` - Check logs
- SSH MCP: `execute_command` - Run tests

### Phase 5: Deployment
**Use These Tools:**
- SSH MCP: `execute_command` - Deploy to production
- Docker MCP: `list_containers` - Verify containers
- Fetch MCP: `fetch_url` - Test production
- GitHub MCP: `create_issue` - Document release

---

## 💡 Quick Examples

### Query Database
```
"Query the users table to see all registered users"
→ Uses: PostgreSQL MCP: query_database
→ Auto-approved: ✅ Yes
```

### Deploy Backend
```
"Deploy the backend API to the server"
→ Uses: SSH MCP: execute_command
→ Auto-approved: ✅ Yes
```

### Test API Endpoint
```
"Test the /api/auth/login endpoint"
→ Uses: Fetch MCP: fetch_url
→ Auto-approved: ✅ Yes
```

### Search for Package
```
"Find JWT authentication packages on npm"
→ Uses: NPM MCP: search_packages
→ Auto-approved: ✅ Yes
```

### Create GitHub Issue
```
"Create a GitHub issue for the authentication bug"
→ Uses: GitHub MCP: create_issue
→ Auto-approved: ✅ Yes
```

### Check Container Status
```
"Check if the backend container is running"
→ Uses: Docker MCP: list_containers
→ Auto-approved: ✅ Yes
```

### View Server Logs
```
"Show me the backend API logs"
→ Uses: SSH MCP: execute_command
→ Auto-approved: ✅ Yes
```

### Search Vectors
```
"Find similar calls using vector search"
→ Uses: pgvector MCP: search_vectors
→ Auto-approved: ✅ Yes
```

---

## 🔐 Safety Notes

### Safe Operations (Auto-Approved)
- ✅ SELECT queries
- ✅ Read operations
- ✅ View operations
- ✅ Search operations
- ✅ List operations

### Caution Operations (Still Auto-Approved)
- ⚠️ INSERT queries
- ⚠️ UPDATE queries
- ⚠️ DELETE queries
- ⚠️ Shell commands
- ⚠️ File writes

### Best Practices
1. **Review before executing** - Even with auto-approval
2. **Test in staging** - Don't deploy directly to production
3. **Backup first** - Always backup before changes
4. **Log operations** - Keep audit trail
5. **Use transactions** - Wrap database changes

---

## 🚀 How to Use

### Step 1: Ask for What You Need
```
"Query the database to get all clients"
```

### Step 2: Tool Executes Automatically
```
✅ PostgreSQL MCP: query_database
✅ Auto-approved - no confirmation needed
```

### Step 3: Get Results Instantly
```
Results returned immediately
No waiting for approval
```

---

## 📊 Auto-Approval Status

| MCP | Tools | Count | Status |
|-----|-------|-------|--------|
| PostgreSQL | query_database, execute_query, get_schema | 3 | ✅ Auto |
| pgvector | query_database, search_vectors, insert_vectors, update_vectors | 4 | ✅ Auto |
| SSH | execute_command, read_file, write_file, list_directory | 4 | ✅ Auto |
| GitHub | create_issue, create_pull_request, read_repository, list_issues | 4 | ✅ Auto |
| Notion | create_page, update_page, query_database | 3 | ✅ Auto |
| NPM | search_packages, get_package_info, get_package_versions | 3 | ✅ Auto |
| Docker | list_containers, list_images, get_container_logs | 3 | ✅ Auto |
| Git | get_repository_status, list_commits, get_diff | 3 | ✅ Auto |
| Fetch | fetch_url, get_content | 2 | ✅ Auto |
| **TOTAL** | | **29** | **✅ Auto** |

---

## ⚡ Speed Benefits

### Without Auto-Approval
1. Ask for operation
2. Wait for confirmation
3. Approve operation
4. Get results
**Time: 30-60 seconds**

### With Auto-Approval
1. Ask for operation
2. Get results immediately
**Time: 5-10 seconds**

**Speed Improvement: 5-10x faster! 🚀**

---

## 🎯 Recommended Usage

### During Development
- Use auto-approved tools frequently
- Query database for testing
- Deploy and test continuously
- Track changes with Git

### During Testing
- Use Fetch MCP to test endpoints
- Use PostgreSQL MCP to verify data
- Use Docker MCP to check services
- Use SSH MCP to view logs

### During Deployment
- Use SSH MCP to deploy
- Use Docker MCP to verify
- Use Fetch MCP to test
- Use GitHub MCP to document

---

## 📝 Configuration

### Current Configuration
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

### To Modify Auto-Approvals
Edit `.kiro/settings/mcp.json` and update the `autoApprove` arrays

---

## ✅ Summary

### What's Auto-Approved
- ✅ 29 tools across 9 MCP servers
- ✅ All safe read operations
- ✅ All query operations
- ✅ All deployment operations
- ✅ All testing operations

### What You Can Do
- ✅ Query database instantly
- ✅ Deploy backend instantly
- ✅ Test endpoints instantly
- ✅ Manage dependencies instantly
- ✅ Track changes instantly

### Speed Improvement
- ✅ 5-10x faster than manual approval
- ✅ No waiting for confirmation
- ✅ Instant results
- ✅ Faster development cycle

---

**You're all set! Use these auto-approved tools to accelerate your development! 🚀**
