# Tool Optimization & Pre-Execution Strategy

**Purpose:** Minimize token usage and execution time by identifying and using only necessary tools before task execution.

**Status:** Recommended best practice for all Kiro executions.

---

## Overview

Before executing any task, Kiro should perform a **tool analysis phase** to:
- Identify which MCP servers and tools are actually needed
- Avoid loading unnecessary tools
- Reduce context bloat and token consumption
- Improve execution speed and cost efficiency

This is especially critical for:
- Complex multi-step tasks
- Spec-driven development workflows
- Large codebases with many file operations
- Tasks involving multiple external systems (DB, SSH, GitHub, etc.)

---

## Pre-Execution Tool Analysis Checklist

### Step 1: Analyze the Request
Before making any tool calls, ask:
- What is the core objective?
- What data sources are needed?
- What external systems must be accessed?
- What operations will be performed?

### Step 2: Map Required Tools
For each objective, identify:
- **File operations** → `readFile`, `readMultipleFiles`, `fileSearch`, `grepSearch`, `fsWrite`, `strReplace`
- **Directory operations** → `listDirectory`
- **Database queries** → `postgres` MCP server
- **SSH/Remote execution** → `ssh` MCP server
- **GitHub operations** → `github` MCP server
- **Web content** → `webFetch`, `remote_web_search`
- **Code diagnostics** → `getDiagnostics`
- **Task management** → `taskStatus`, `updatePBTStatus`
- **Spec operations** → `userInput`, `prework`

### Step 3: Disable Unused MCP Servers
If a task doesn't need certain MCP servers, they should remain disabled:
- Don't enable `postgres` if only reading files
- Don't enable `ssh` if working locally
- Don't enable `github` if not interacting with repositories
- Don't enable `docker` if not managing containers

### Step 4: Load Only Necessary Tools
Call only the tools identified in Step 2. Avoid:
- Exploratory tool calls
- "Just in case" tool invocations
- Redundant tool calls that could be combined

### Step 5: Execute with Minimal Context
- Use specific file paths instead of broad directory scans
- Use targeted searches instead of full-file reads
- Combine multiple file reads into single `readMultipleFiles` calls
- Use `fileSearch` for fuzzy matching before `readFile`

---

## Tool Usage Patterns

### Pattern 1: File Reading (Minimal)
**Bad:** Read entire directory, then search through files
```
listDirectory → readFile (multiple times) → grepSearch
```

**Good:** Use targeted search first
```
fileSearch (fuzzy match) → readFile (specific files only)
```

### Pattern 2: Code Analysis (Minimal)
**Bad:** Read all files, then run diagnostics on everything
```
readFile (all files) → getDiagnostics (all files)
```

**Good:** Identify problem files first, then diagnose
```
grepSearch (find errors) → getDiagnostics (only problem files)
```

### Pattern 3: Database Operations (Minimal)
**Bad:** Query entire database, then filter in code
```
postgres: SELECT * FROM table → filter results
```

**Good:** Filter at database level
```
postgres: SELECT * FROM table WHERE condition
```

### Pattern 4: Multi-File Operations (Minimal)
**Bad:** Read files one at a time
```
readFile (file1) → readFile (file2) → readFile (file3)
```

**Good:** Read all at once
```
readMultipleFiles ([file1, file2, file3])
```

---

## MCP Server Auto-Approval Configuration

Current `autoApprove` lists in `.kiro/settings/mcp.json` are optimized for:
- **fetch**: `fetch_url`, `get_content` (web operations)
- **postgres**: `query_database`, `execute_query`, `get_schema` (DB queries)
- **ssh**: `execute_command`, `read_file`, `write_file`, `list_directory` (remote ops)
- **github**: `create_issue`, `create_pull_request`, `read_repository`, `list_issues` (repo ops)
- **notion**: `create_page`, `update_page`, `query_database` (note-taking)
- **pgvector**: `query_database`, `search_vectors`, `insert_vectors`, `update_vectors` (vector DB)
- **npm**: `search_packages`, `get_package_info`, `get_package_versions` (package info)
- **docker**: `list_containers`, `list_images`, `get_container_logs` (container ops)
- **git**: `get_repository_status`, `list_commits`, `get_diff` (git ops)

**These are pre-approved and safe to use without additional confirmation.**

---

## Token Optimization Rules

### Rule 1: Combine Operations
- Use `readMultipleFiles` instead of multiple `readFile` calls
- Use `grepSearch` with specific patterns instead of reading entire files
- Use `fileSearch` to narrow scope before reading

### Rule 2: Avoid Redundant Calls
- Don't call `listDirectory` if you already know the file path
- Don't call `fileSearch` if you already know the exact file location
- Don't call `getDiagnostics` on files without errors

### Rule 3: Use Specific Queries
- Use `grepSearch` with exact patterns, not broad searches
- Use `fileSearch` with specific keywords, not generic terms
- Use database WHERE clauses instead of fetching all data

### Rule 4: Batch Operations
- Group related file operations together
- Combine multiple small tasks into single execution
- Use parallel tool calls when independent

### Rule 5: Cache Results
- Store file contents in context for reuse
- Reference previous search results instead of re-searching
- Build up understanding incrementally

---

## Spec-Driven Development Optimization

When working with specs (requirements.md, design.md, tasks.md):

### Before Reading Spec Files
1. Identify which spec files are needed (requirements? design? tasks?)
2. Identify which sections are relevant (only read what's needed)
3. Use `readFile` with line ranges if possible

### During Spec Execution
1. Load requirements.md first (understand what to build)
2. Load design.md only if needed (understand how to build)
3. Load tasks.md only when executing (understand what to do)
4. Don't load all three unless all three are needed

### Example: Executing a Single Task
```
✅ DO:
- Read tasks.md (find the specific task)
- Read requirements.md (understand context)
- Read design.md (only if task references it)
- Execute the task

❌ DON'T:
- Read all three files upfront
- Load entire spec directory
- Read files you won't use
```

---

## Pre-Execution Checklist Template

Before starting any task, use this checklist:

```
Task: [Description]

Required Tools:
- [ ] File operations (readFile, fsWrite, etc.)
- [ ] Directory operations (listDirectory)
- [ ] Database operations (postgres)
- [ ] SSH operations (ssh)
- [ ] GitHub operations (github)
- [ ] Web operations (webFetch, remote_web_search)
- [ ] Code diagnostics (getDiagnostics)
- [ ] Task management (taskStatus)
- [ ] Spec operations (userInput, prework)

MCP Servers to Enable:
- [ ] fetch (if web operations needed)
- [ ] postgres (if database queries needed)
- [ ] ssh (if remote execution needed)
- [ ] github (if repo operations needed)
- [ ] notion (if note-taking needed)
- [ ] pgvector (if vector search needed)
- [ ] npm (if package info needed)
- [ ] docker (if container ops needed)
- [ ] git (if git operations needed)

Specific Files/Paths Needed:
- [ ] [List specific files to read]
- [ ] [List specific directories to access]
- [ ] [List specific database tables]

Execution Plan:
1. [First tool call]
2. [Second tool call]
3. [Execute task]
```

---

## Examples

### Example 1: Reading a Spec File
**Task:** Review requirements for a feature

**Analysis:**
- Need: requirements.md file
- Don't need: design.md, tasks.md (not yet)
- Don't need: database, SSH, GitHub

**Execution:**
```
readFile("path/to/requirements.md")
```

### Example 2: Executing a Task
**Task:** Implement a feature from tasks.md

**Analysis:**
- Need: tasks.md (find the task)
- Need: requirements.md (understand requirements)
- Need: design.md (understand design)
- Need: relevant source files (implement)
- Don't need: database, SSH, GitHub (unless task requires)

**Execution:**
```
readFile("tasks.md")
readFile("requirements.md")
readFile("design.md")
readMultipleFiles([source files needed])
getDiagnostics([files to check])
fsWrite/strReplace (implement)
```

### Example 3: Debugging a Production Issue
**Task:** Fix a bug in production

**Analysis:**
- Need: SSH (access production server)
- Need: git (check recent changes)
- Need: postgres (query database for error logs)
- Don't need: GitHub (unless checking PR)
- Don't need: Notion (unless documenting)

**Execution:**
```
ssh: execute_command (check logs)
postgres: query_database (find error patterns)
git: get_diff (see recent changes)
ssh: read_file (examine code)
```

---

## Best Practices

### ✅ DO
- Analyze task requirements before making tool calls
- Identify specific files/paths needed upfront
- Use targeted searches instead of broad scans
- Combine related operations into single calls
- Disable unused MCP servers
- Reference previous results instead of re-querying
- Use line ranges when reading large files
- Batch independent operations together

### ❌ DON'T
- Load all tools "just in case"
- Read entire directories when you need one file
- Make exploratory tool calls
- Call the same tool multiple times for related data
- Enable MCP servers you won't use
- Read files without knowing what you're looking for
- Make redundant queries
- Ignore the autoApprove list

---

## Token Savings Estimate

By following this strategy:
- **File operations:** 30-50% reduction (targeted reads vs. full scans)
- **Database queries:** 40-60% reduction (WHERE clauses vs. fetch-all)
- **Search operations:** 20-40% reduction (specific patterns vs. broad searches)
- **Overall context:** 25-40% reduction (fewer unnecessary tool calls)

**Example:** A task that would normally use 50k tokens can be optimized to 30-35k tokens by:
1. Using `fileSearch` before `readFile`
2. Using `readMultipleFiles` instead of multiple `readFile` calls
3. Using `grepSearch` with specific patterns
4. Disabling unused MCP servers

---

## Implementation

This strategy is **already partially implemented** in Kiro through:
- `autoApprove` lists in MCP configuration
- Tool-specific parameters (line ranges, patterns, etc.)
- Parallel tool call support

**To fully implement:**
1. Always perform pre-execution analysis
2. Use the checklist template before starting tasks
3. Follow the tool usage patterns
4. Reference this guide when optimizing token usage

---

## References

- MCP Configuration: `.kiro/settings/mcp.json`
- Tool Documentation: See individual tool descriptions in Kiro
- Spec Workflow: `.kiro/steering/` (other steering files)

---

**Last Updated:** December 26, 2025
**Status:** Active Best Practice
