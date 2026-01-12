# Billing Integration - Quick Reference Guide

**Quick Links for Common Tasks**

---

## 🎯 I Want To...

### View Overall Progress
→ Open [BILLING_IMPLEMENTATION_ROADMAP.md](.kiro/BILLING_IMPLEMENTATION_ROADMAP.md)

### See All Active Specs
→ Open [SPEC_TRACKING_INDEX.md](.kiro/SPEC_TRACKING_INDEX.md)

### Deploy to Server
→ Follow [DEPLOYMENT_CHECKLIST_BILLING.md](.kiro/DEPLOYMENT_CHECKLIST_BILLING.md)

### Work on Next Task
→ Open [tasks.md](.kiro/specs/member-portal-billing/tasks.md) and click "Task 2"

### Understand Requirements
→ Read [requirements.md](.kiro/specs/member-portal-billing/requirements.md)

### Review Architecture
→ Read [design.md](.kiro/specs/member-portal-billing/design.md)

### Run Tests Locally
```bash
python -m pytest backend-setup/tests/test_billing_service_properties.py -v
```

### Check Service Code
- BillingService: `backend-setup/services/billing_service.py`
- UsageService: `backend-setup/services/usage_service.py`

### View Database Models
→ `backend-setup/db/models.py` (search for "Usage" model)

---

## 📊 Current Status

**Phase:** 1 of 9 ✅ COMPLETE  
**Tasks:** 1 of 25 ✅ COMPLETE  
**Progress:** 4%

**Next Phase:** Subscription Management (Task 2)

---

## 🚀 Deployment Command

```bash
# Stage files
git add backend-setup/services/ backend-setup/tests/ backend-setup/db/models.py backend-setup/requirements.txt

# Commit
git commit -m "Phase 1: Billing service infrastructure"

# Push
git push origin main

# On server
pip install -r backend-setup/requirements.txt
python -m pytest backend-setup/tests/test_billing_service_properties.py -v
```

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `backend-setup/services/billing_service.py` | Main billing service |
| `backend-setup/services/usage_service.py` | Usage tracking service |
| `backend-setup/tests/test_billing_service_properties.py` | Property-based tests |
| `backend-setup/db/models.py` | Database models (Usage added) |
| `.kiro/specs/member-portal-billing/tasks.md` | Task list |
| `.kiro/BILLING_IMPLEMENTATION_ROADMAP.md` | Phase tracking |

---

## 🔗 Navigation

```
.kiro/
├── QUICK_REFERENCE_BILLING.md (you are here)
├── SPEC_TRACKING_INDEX.md (all specs)
├── BILLING_IMPLEMENTATION_ROADMAP.md (billing phases)
├── DEPLOYMENT_CHECKLIST_BILLING.md (deployment steps)
└── specs/member-portal-billing/
    ├── requirements.md (what to build)
    ├── design.md (how to build it)
    └── tasks.md (step-by-step tasks)
```

---

## ✅ Phase 1 Deliverables

- ✅ BillingService class
- ✅ UsageService class
- ✅ Usage database model
- ✅ Property-based tests
- ✅ Documentation

---

## 📋 Phase 2 Preview

**Task 2:** Implement subscription status retrieval
- Get subscription status from PayPal
- Implement caching
- Add error handling
- Write property tests

**Estimated Time:** 2-3 hours

---

## 🆘 Need Help?

1. **Deployment Issues?** → See [DEPLOYMENT_CHECKLIST_BILLING.md](.kiro/DEPLOYMENT_CHECKLIST_BILLING.md)
2. **Understanding Requirements?** → See [requirements.md](.kiro/specs/member-portal-billing/requirements.md)
3. **Architecture Questions?** → See [design.md](.kiro/specs/member-portal-billing/design.md)
4. **Task Details?** → See [tasks.md](.kiro/specs/member-portal-billing/tasks.md)
5. **All Specs?** → See [SPEC_TRACKING_INDEX.md](.kiro/SPEC_TRACKING_INDEX.md)

---

**Last Updated:** January 12, 2025
