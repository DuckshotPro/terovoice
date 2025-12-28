# Kiro Agent Hooks Configuration

Agent hooks automate tasks and provide context reminders during development.

## Hook 1: On New Session - Load Project Context

**Trigger:** When a new session is created (on first message send)

**Action:** Send message to agent

**Message:**
```
You are working on the AI Receptionist SaaS project. Here's the current status:

✅ PHASE 1 COMPLETE:
- Backend API with 16 endpoints (auth, clients, calls, analytics)
- PostgreSQL database on IONOS (74.208.227.161:5432)
- JWT authentication and user isolation
- Podman containerization
- Complete documentation

🔄 PHASE 2 IN PROGRESS:
- React frontend with Vite + TypeScript
- Tailwind CSS styling
- API client with Axios (src/services/api.js)
- Environment configuration (.env.local)

📋 NEXT TASKS:
1. Task 3: Set up Context API for state management
2. Task 4: Create routing structure with protected routes
3. Task 5: Configure Tailwind CSS styling
4. Task 6: Create authentication pages

🎯 KEY REMINDERS:
- All prompts are pre-approved - proceed with implementation
- Use Haiku 4.5 by default, escalate to Sonnet 3.5 for complex tasks
- Follow quality assurance guidelines (linting, security, testing)
- Reference spec documents: .kiro/specs/frontend-integration/
- Database: PostgreSQL on IONOS (user: user, password: cira)
- API Base URL: http://localhost:8000

📁 KEY FILES:
- .kiro/specs/frontend-integration/requirements.md - 12 requirements
- .kiro/specs/frontend-integration/design.md - Architecture & design
- .kiro/specs/frontend-integration/tasks.md - 67 implementation tasks
- src/services/api.js - Complete API client with all endpoints
- .env.local - Environment configuration

🚀 READY TO CONTINUE WITH PHASE 2 FRONTEND IMPLEMENTATION
```

---

## Hook 2: On File Save (src/**/*.jsx) - Run Linting & Type Check

**Trigger:** When a React component file is saved

**Action:** Ask agent

**Prompt:**
```
A React component was just saved. Please run: npm run lint -- --fix and report any linting or type errors found. Fix critical issues automatically.
```

**Purpose:** Auto-fix linting issues and catch type errors immediately

---

## Hook 3: On File Save (src/**/*.js) - Check for API Usage

**Trigger:** When a JavaScript service file is saved

**Action:** Send message to agent

**Message:**
```
A service file was just saved. Please verify:
1. All API calls use the centralized api.js client
2. Error handling is implemented
3. Loading states are managed
4. No hardcoded URLs or credentials
```

**Purpose:** Ensure consistent API usage patterns

---

## Hook 4: On Task Completion - Update Task Status

**Trigger:** When a task is marked complete in tasks.md

**Action:** Send message to agent

**Message:**
```
A task was just completed. Please:
1. Verify all sub-tasks are also complete
2. Run tests if applicable
3. Check for any console errors
4. Update git with a commit message
```

**Purpose:** Ensure quality before moving to next task

---

## Hook 5: Before Deployment - Security & Performance Check

**Trigger:** Manual hook - click "Run Security Check"

**Action:** Execute shell command

**Command:**
```bash
echo "🔒 Security Check:" && npm audit --audit-level=moderate && echo "✅ Security OK" || echo "⚠️ Security issues found"
```

**Purpose:** Catch security vulnerabilities before deployment

---

## Hook 6: On Git Commit - Validate Commit Message

**Trigger:** When git commit is made

**Action:** Execute shell command

**Command:**
```bash
git log -1 --pretty=%B | grep -E "^(feat|fix|docs|style|refactor|test|chore):" || echo "⚠️ Use conventional commits: feat:, fix:, docs:, etc."
```

**Purpose:** Enforce conventional commit messages

---

## How to Set Up Hooks

1. Open Kiro command palette: `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Search for: "Open Kiro Hook UI"
3. Click "Create New Hook"
4. Configure each hook above

**Or manually edit:** `.kiro/hooks.json` (if it exists)

---

## Hook Execution Order

1. **On Session Start** → Load context
2. **On File Save** → Lint & type check
3. **On Task Complete** → Verify quality
4. **On Git Commit** → Validate message
5. **Manual Trigger** → Security check

---

## Benefits

✅ **Automation** - Repetitive tasks run automatically  
✅ **Consistency** - Same checks every time  
✅ **Quality** - Catch issues early  
✅ **Context** - Always know project status  
✅ **Efficiency** - Less manual work  

---

## Notes

- Hooks run in the background without blocking your work
- You can disable any hook if it becomes annoying
- Hooks respect your current task context
- All hooks are optional - use what helps you most

---

**Status:** Ready to configure  
**Recommended:** Set up Hook 1 (context) and Hook 2 (linting) first

