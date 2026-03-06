# Quality Assurance & Security Steering

**Purpose:** Ensure code quality, security, and reliability through automated checks, linting, and security scanning.

**Scope:** All code generated in Phase 2+ (Frontend, Integration, Deployment)

---

## 🎯 Quality Gates

### Before Code Generation
- [ ] Review requirements for security implications
- [ ] Identify potential vulnerabilities
- [ ] Plan for error handling
- [ ] Consider edge cases

### During Code Generation
- [ ] Follow linting standards
- [ ] Include error handling
- [ ] Add input validation
- [ ] Include security checks

### After Code Generation
- [ ] Run linters (ESLint, Pylint)
- [ ] Run security scanners (Bandit, npm audit)
- [ ] Check for common vulnerabilities
- [ ] Verify test coverage

---

## 🔒 Security Scanning Checklist

### Frontend (React/JavaScript)
- [ ] **npm audit** - Check for vulnerable dependencies
- [ ] **ESLint security plugin** - Detect security issues
- [ ] **OWASP Top 10** - Check for common vulnerabilities
  - [ ] XSS prevention (sanitize user input)
  - [ ] CSRF protection (token validation)
  - [ ] SQL injection prevention (parameterized queries)
  - [ ] Authentication bypass prevention
  - [ ] Sensitive data exposure prevention
- [ ] **Dependency scanning** - Check for outdated packages
- [ ] **Code review** - Manual security review

### Backend (Python/Flask)
- [ ] **Bandit** - Python security linter
- [ ] **Safety** - Check for known vulnerabilities
- [ ] **pip audit** - Check for vulnerable dependencies
- [ ] **OWASP Top 10** - Check for common vulnerabilities
  - [ ] SQL injection prevention (SQLAlchemy ORM)
  - [ ] Authentication/authorization checks
  - [ ] Sensitive data handling
  - [ ] Error handling (no info leakage)
  - [ ] CORS configuration
- [ ] **Code review** - Manual security review

---

## 🐛 Bug Detection Strategy

### Static Analysis
- [ ] **ESLint** (JavaScript) - Code quality and bugs
- [ ] **Pylint** (Python) - Code quality and bugs
- [ ] **Type checking** (TypeScript) - Type safety
- [ ] **Dead code detection** - Unused code

### Runtime Analysis
- [ ] **Unit tests** - Test individual functions
- [ ] **Integration tests** - Test component interactions
- [ ] **End-to-end tests** - Test full workflows
- [ ] **Error boundary tests** - Test error handling

### Code Review
- [ ] **Manual review** - Peer review
- [ ] **Architecture review** - Design patterns
- [ ] **Performance review** - Optimization opportunities
- [ ] **Security review** - Vulnerability assessment

---

## 📋 Linting Standards

### JavaScript/React (ESLint)
```javascript
// .eslintrc.json
{
  "extends": ["eslint:recommended", "plugin:react/recommended"],
  "rules": {
    "no-console": "warn",
    "no-unused-vars": "error",
    "no-undef": "error",
    "eqeqeq": "error",
    "no-eval": "error",
    "no-implied-eval": "error",
    "no-new-func": "error"
  }
}
```

### Python (Pylint)
```ini
# .pylintrc
[MASTER]
disable=
    missing-docstring,
    too-few-public-methods

[DESIGN]
max-attributes=7
max-arguments=5
```

---

## 🔍 Security Scanning Tools

### Frontend
```bash
# Check dependencies
npm audit

# Run ESLint with security plugin
npm install --save-dev eslint-plugin-security
npx eslint --ext .js,.jsx src/

# Check for OWASP vulnerabilities
npm install --save-dev snyk
npx snyk test
```

### Backend
```bash
# Check Python security
pip install bandit safety
bandit -r backend-setup/
safety check

# Check dependencies
pip audit
```

---

## ✅ Code Quality Checklist

### Every Function/Component
- [ ] Has clear purpose and documentation
- [ ] Handles errors gracefully
- [ ] Validates input
- [ ] Returns expected type
- [ ] Has unit tests
- [ ] Follows naming conventions
- [ ] No console.log/print statements (except logging)
- [ ] No hardcoded secrets

### Every API Endpoint
- [ ] Validates request data
- [ ] Checks authentication
- [ ] Checks authorization
- [ ] Returns appropriate status codes
- [ ] Handles errors gracefully
- [ ] Logs important events
- [ ] Has rate limiting (if needed)
- [ ] Has CORS configuration

### Every Database Query
- [ ] Uses parameterized queries (SQLAlchemy ORM)
- [ ] Validates input
- [ ] Handles connection errors
- [ ] Logs slow queries
- [ ] Has appropriate indexes
- [ ] Handles NULL values
- [ ] Validates returned data

### Every Component/Page
- [ ] Has error boundary
- [ ] Handles loading state
- [ ] Handles error state
- [ ] Validates props
- [ ] Has accessibility attributes
- [ ] Is responsive
- [ ] Has unit tests
- [ ] Has integration tests

---

## 🧪 Testing Requirements

### Unit Tests
- [ ] Test happy path
- [ ] Test error cases
- [ ] Test edge cases
- [ ] Test boundary conditions
- [ ] Aim for 80%+ coverage

### Integration Tests
- [ ] Test component interactions
- [ ] Test API integration
- [ ] Test database integration
- [ ] Test error handling

### End-to-End Tests
- [ ] Test complete workflows
- [ ] Test user journeys
- [ ] Test error scenarios
- [ ] Test performance

---

## 🚨 Red Flags (Escalate to Sonnet 3.5)

🚩 **Security Issues:**
- [ ] Hardcoded secrets or credentials
- [ ] SQL injection vulnerability
- [ ] XSS vulnerability
- [ ] CSRF vulnerability
- [ ] Authentication bypass
- [ ] Authorization bypass
- [ ] Sensitive data exposure

🚩 **Code Quality Issues:**
- [ ] No error handling
- [ ] No input validation
- [ ] No tests
- [ ] Dead code
- [ ] Circular dependencies
- [ ] Memory leaks
- [ ] Performance issues

🚩 **Architecture Issues:**
- [ ] Tight coupling
- [ ] Violation of SOLID principles
- [ ] Poor separation of concerns
- [ ] Scalability issues
- [ ] Maintainability issues

---

## 📊 Quality Metrics

### Code Coverage
- **Target:** 80%+ for critical paths
- **Minimum:** 60% overall
- **Tools:** Jest (JavaScript), pytest-cov (Python)

### Linting Score
- **Target:** 0 errors, 0 warnings
- **Acceptable:** 0 errors, <5 warnings
- **Tools:** ESLint, Pylint

### Security Score
- **Target:** 0 vulnerabilities
- **Acceptable:** 0 critical, <3 high
- **Tools:** npm audit, Bandit, Safety

### Performance
- **API Response Time:** <100ms (p95)
- **Page Load Time:** <3s (p95)
- **Bundle Size:** <500KB (gzipped)

---

## 🔄 CI/CD Pipeline

### Pre-Commit Hooks
```bash
# Run linters
npm run lint
python -m pylint backend-setup/

# Run security checks
npm audit
bandit -r backend-setup/

# Run tests
npm test
pytest backend-setup/
```

### Pre-Push Checks
- [ ] All tests passing
- [ ] No linting errors
- [ ] No security vulnerabilities
- [ ] Code coverage >80%
- [ ] Documentation updated

### Pre-Deployment Checks
- [ ] All tests passing
- [ ] Security scan passed
- [ ] Performance benchmarks met
- [ ] Database migrations tested
- [ ] Rollback plan documented

---

## 📝 Security Best Practices

### Authentication
- [ ] Use JWT with secure expiration
- [ ] Hash passwords with bcrypt
- [ ] Validate tokens on every request
- [ ] Implement token refresh
- [ ] Log authentication events

### Authorization
- [ ] Check user permissions
- [ ] Validate resource ownership
- [ ] Implement role-based access
- [ ] Log authorization events
- [ ] Deny by default

### Data Protection
- [ ] Encrypt sensitive data
- [ ] Use HTTPS only
- [ ] Validate all input
- [ ] Sanitize output
- [ ] Implement rate limiting

### Error Handling
- [ ] Don't expose stack traces
- [ ] Log errors securely
- [ ] Return generic error messages
- [ ] Handle edge cases
- [ ] Implement graceful degradation

---

## 🎯 Phase 2 Specific Checks

### Frontend (React)
- [ ] **XSS Prevention**
  - [ ] Sanitize user input
  - [ ] Use dangerouslySetInnerHTML carefully
  - [ ] Validate API responses

- [ ] **CSRF Prevention**
  - [ ] Include CSRF tokens
  - [ ] Validate origin headers
  - [ ] Use SameSite cookies

- [ ] **Authentication**
  - [ ] Secure token storage
  - [ ] Validate JWT tokens
  - [ ] Implement logout
  - [ ] Handle token expiration

- [ ] **Performance**
  - [ ] Code splitting
  - [ ] Lazy loading
  - [ ] Memoization
  - [ ] Bundle optimization

### Backend (Flask)
- [ ] **SQL Injection Prevention**
  - [ ] Use SQLAlchemy ORM
  - [ ] Parameterized queries
  - [ ] Input validation

- [ ] **Authentication**
  - [ ] JWT validation
  - [ ] Secure token storage
  - [ ] Password hashing

- [ ] **Authorization**
  - [ ] User isolation
  - [ ] Resource ownership checks
  - [ ] Role-based access

- [ ] **API Security**
  - [ ] CORS configuration
  - [ ] Rate limiting
  - [ ] Input validation
  - [ ] Error handling

---

## 🛠️ Tools Setup

### Frontend
```bash
# Install linting tools
npm install --save-dev eslint eslint-plugin-react eslint-plugin-security

# Install security tools
npm install --save-dev snyk npm-audit-html

# Install testing tools
npm install --save-dev jest @testing-library/react

# Install code coverage
npm install --save-dev jest-coverage
```

### Backend
```bash
# Install linting tools
pip install pylint flake8

# Install security tools
pip install bandit safety

# Install testing tools
pip install pytest pytest-cov

# Install code analysis
pip install radon
```

---

## 📋 Pre-Implementation Checklist

Before starting Phase 2, ensure:

- [ ] Linting tools installed
- [ ] Security scanning tools installed
- [ ] Testing framework configured
- [ ] CI/CD pipeline ready
- [ ] Code review process defined
- [ ] Security guidelines documented
- [ ] Performance benchmarks set
- [ ] Monitoring configured

---

## 🚀 Implementation by Phase

### Phase 2: Frontend Setup
- [ ] Set up ESLint and Prettier
- [ ] Configure Jest for testing
- [ ] Set up security scanning
- [ ] Implement error boundaries
- [ ] Add input validation
- [ ] Add authentication checks

### Phase 3: Frontend Pages
- [ ] Write unit tests for components
- [ ] Write integration tests
- [ ] Run security scans
- [ ] Check code coverage
- [ ] Optimize performance
- [ ] Document components

### Phase 4: Integration & Testing
- [ ] Write end-to-end tests
- [ ] Run full security audit
- [ ] Performance testing
- [ ] Load testing
- [ ] Stress testing
- [ ] Security penetration testing

### Phase 5: Deployment
- [ ] Final security scan
- [ ] Performance verification
- [ ] Backup verification
- [ ] Rollback plan tested
- [ ] Monitoring configured
- [ ] Alerts configured

---

## 📊 Quality Dashboard

Track these metrics:

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Code Coverage | 80%+ | - | 🔄 |
| Linting Errors | 0 | - | 🔄 |
| Security Issues | 0 | - | 🔄 |
| Test Pass Rate | 100% | - | 🔄 |
| Performance (p95) | <100ms | - | 🔄 |
| Bundle Size | <500KB | - | 🔄 |

---

## 🔔 When to Escalate to Sonnet 3.5

🚩 **Escalate immediately if:**
- Security vulnerability found
- Code coverage drops below 60%
- Performance regression detected
- Critical bug found
- Architecture issue identified
- Compliance issue found

---

## 📞 Quick Reference

### Run All Checks
```bash
# Frontend
npm run lint && npm test && npm audit

# Backend
pylint backend-setup/ && pytest backend-setup/ && bandit -r backend-setup/
```

### Security Scan
```bash
# Frontend
npm audit && npx snyk test

# Backend
bandit -r backend-setup/ && safety check
```

### Test Coverage
```bash
# Frontend
npm test -- --coverage

# Backend
pytest --cov=backend-setup/ backend-setup/
```

---

## ✅ Summary

**Quality Assurance Strategy:**
- ✅ Automated linting (ESLint, Pylint)
- ✅ Security scanning (npm audit, Bandit)
- ✅ Comprehensive testing (Unit, Integration, E2E)
- ✅ Code coverage tracking (80%+ target)
- ✅ Performance monitoring
- ✅ Manual code review

**Security Focus:**
- ✅ OWASP Top 10 prevention
- ✅ Input validation
- ✅ Authentication/Authorization
- ✅ Error handling
- ✅ Data protection

**Implementation:**
- ✅ Tools configured
- ✅ Checks automated
- ✅ Metrics tracked
- ✅ Escalation rules defined

---

**Ready for Phase 2 with quality assurance! 🚀**
