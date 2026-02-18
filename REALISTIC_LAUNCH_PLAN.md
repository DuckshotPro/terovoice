# Tero Voice - Realistic Launch Plan

**Status:** MVP Complete, Ready for Market
**Pricing Model:** Direct-to-SMB at $40-99/month
**Timeline:** 90 days to $3-5k MRR (realistic)
**Date:** January 4, 2026

---

## What's Already Done (Don't Redo)

✅ **Backend API** - Flask + PostgreSQL + LiveKit integration
✅ **AI Agent Logic** - Ollama + Deepgram + Cartesia (or local TTS)
✅ **9 Profession Prompts** - Dentist, plumber, mechanic, locksmith, etc.
✅ **Analytics Dashboard** - Real-time call tracking + revenue display
✅ **Docker Deployment** - Containerized, ready for VPS
✅ **SIP Integration** - LiveKit SIP trunking configured
✅ **Voice Cloning** - ElevenLabs/Cartesia integration ready
✅ **Database Schema** - Multi-tenant ready
✅ **Branding** - Tero Voice brand established

**Don't waste time rebuilding these.**

---

## What Actually Needs to Happen (90 Days)

### Week 1-2: Launch MVP to Market

**Goal:** Get first 5 paying customers

**Tasks:**
- [ ] Set up Stripe billing ($40/month starter tier)
- [ ] Create simple landing page (1 page, not 9)
- [ ] Write 3-5 case studies/testimonials (even if hypothetical)
- [ ] Create 30-second demo video
- [ ] Set up email capture form
- [ ] Deploy to production VPS
- [ ] Create basic onboarding flow
- [ ] Write quick start guide

**Why this works:**
- Stripe is easier than PayPal for recurring billing
- One landing page converts better than 9 (less decision paralysis)
- Demo video is your best sales tool
- Email list is your moat

**Realistic outcome:** 2-5 signups

---

### Week 3-4: Get First Customers Live

**Goal:** First customers making calls, seeing ROI

**Tasks:**
- [ ] Manual onboarding (you do it personally)
- [ ] Set up their phone number routing
- [ ] Clone their voice
- [ ] Configure their profession prompt
- [ ] Get them their first 10 calls
- [ ] Collect feedback
- [ ] Fix bugs they find
- [ ] Document what breaks

**Why this works:**
- Personal touch = higher success rate
- You learn what's broken before scaling
- Customers become advocates
- Feedback is gold

**Realistic outcome:** 3-8 customers, $120-320/month revenue

---

### Week 5-6: Automate Onboarding

**Goal:** Self-serve signup without manual work

**Tasks:**
- [ ] Create signup form (email, profession, phone number)
- [ ] Auto-generate dashboard URL
- [ ] Auto-route phone number to SIP
- [ ] Auto-clone voice (if they upload sample)
- [ ] Send welcome email with setup guide
- [ ] Create help docs for common issues
- [ ] Set up support email

**Why this works:**
- You can't manually onboard 100 customers
- Self-serve reduces your workload
- Customers like autonomy

**Realistic outcome:** 10-20 customers, $400-800/month revenue

---

### Week 7-8: Start Paid Ads

**Goal:** Consistent customer acquisition

**Tasks:**
- [ ] Create 3 Facebook ad creatives (dentist, plumber, mechanic)
- [ ] Set up conversion tracking
- [ ] Run $10/day test campaigns
- [ ] Track CAC (customer acquisition cost)
- [ ] Optimize best-performing ad
- [ ] Scale winning ad to $50/day
- [ ] Create landing page for each ad
- [ ] Set up retargeting

**Why this works:**
- Organic growth is slow
- Paid ads give you control
- $10/day = $300/month spend = manageable
- You'll know CAC within 2 weeks

**Realistic outcome:** 20-40 customers, $800-1,600/month revenue

---

### Week 9-12: Optimize & Scale

**Goal:** Hit $3-5k MRR

**Tasks:**
- [ ] Analyze which professions convert best
- [ ] Double down on winning professions
- [ ] Increase ad spend to $100-200/day
- [ ] Improve onboarding (reduce friction)
- [ ] Add customer success emails
- [ ] Create referral program ($50 per referral)
- [ ] Collect testimonials from happy customers
- [ ] Improve landing page conversion

**Why this works:**
- You now have data on what works
- Referrals are free customers
- Testimonials are your best marketing
- Scaling is just doing more of what works

**Realistic outcome:** 75-125 customers, $3,000-5,000/month revenue

---

## Realistic Pricing Model

### Tier 1: Starter - $40/month
- 500 minutes/month
- 1 phone number
- Basic analytics
- Email support

### Tier 2: Professional - $99/month
- 2,000 minutes/month
- 3 phone numbers
- Advanced analytics
- Priority support
- Custom prompts

### Tier 3: Enterprise - Custom
- Unlimited minutes
- Unlimited numbers
- White-label option
- Dedicated support
- Custom integrations

**Why this pricing:**
- Matches market ($40-99 is standard)
- Tier 1 is impulse-buy price
- Tier 2 is where most customers go
- Enterprise is where real money is

**Revenue math:**
- 100 customers at $40 = $4,000/month
- 50 customers at $99 = $4,950/month
- 5 enterprise customers at $500 = $2,500/month
- **Total: $11,450/month** (realistic 6-month target)

---

## What NOT to Do (Waste of Time)

❌ **Don't build 9 landing pages** - One converts better
❌ **Don't hire a sales team yet** - Ads work better at this stage
❌ **Don't build white-label** - Focus on direct customers first
❌ **Don't add advanced features** - MVP features are enough
❌ **Don't optimize for scale** - Optimize for conversion first
❌ **Don't build integrations** - Customers don't need them yet
❌ **Don't create support chatbot** - Email support is fine
❌ **Don't build mobile app** - Web dashboard is enough

---

## Actual Blockers (Real Work)

### 1. Billing Integration (3 days)
- Set up Stripe account
- Create subscription logic
- Handle failed payments
- Create billing dashboard
- Test payment flow

### 2. Onboarding Automation (5 days)
- Create signup form
- Auto-generate dashboard URL
- Auto-route phone number
- Send welcome email
- Create help docs

### 3. Landing Page (2 days)
- Write copy
- Add demo video
- Create email capture
- Set up analytics
- Deploy

### 4. Customer Support (1 day)
- Set up support email
- Create FAQ
- Create troubleshooting guide
- Set up email templates

### 5. Paid Ads (3 days)
- Create ad creatives
- Set up Facebook Ads account
- Create landing pages
- Set up conversion tracking
- Launch test campaigns

**Total: ~2 weeks of focused work**

---

## Success Metrics (Realistic)

### Month 1
- Customers: 5-10
- MRR: $200-400
- Churn: 0% (too early)
- CAC: $50-100

### Month 2
- Customers: 20-40
- MRR: $800-1,600
- Churn: 5-10%
- CAC: $30-50

### Month 3
- Customers: 75-125
- MRR: $3,000-5,000
- Churn: 5-10%
- CAC: $20-30

### Month 6
- Customers: 200-300
- MRR: $8,000-12,000
- Churn: 5-10%
- CAC: $15-25

---

## Cost Structure (Monthly)

### Infrastructure
- VPS (Hetzner): $50
- Database: $20
- Monitoring: $10
- **Subtotal: $80**

### Services
- Stripe fees: 2.9% + $0.30 per transaction (~$50 at $3k MRR)
- Email service: $20
- Voice cloning API: ~$100 (varies by usage)
- **Subtotal: $170**

### Total Monthly Cost: ~$250

**At $3k MRR:**
- Revenue: $3,000
- Costs: $250
- Gross profit: $2,750
- Gross margin: 92%

---

## Go-to-Market Strategy

### Phase 1: Direct Outreach (Week 1-4)
- Find 50 dentists/plumbers on Google Maps
- Call them directly
- Offer free trial
- Get testimonials
- Build case studies

### Phase 2: Paid Ads (Week 5-8)
- Run Facebook ads to target professions
- Test 3 different professions
- Scale winning profession
- Optimize landing page

### Phase 3: Organic Growth (Week 9-12)
- Referral program ($50 per referral)
- Customer testimonials
- Case studies
- SEO (long-term)
- Content marketing (blog)

### Phase 4: Partnerships (Month 4+)
- Partner with agencies
- Partner with consultants
- White-label for resellers
- Integration partnerships

---

## Immediate Action Items (This Week)

1. **Set up Stripe** - 1 hour
2. **Create landing page** - 4 hours
3. **Record demo video** - 2 hours
4. **Write case studies** - 3 hours
5. **Deploy to production** - 2 hours
6. **Set up email capture** - 1 hour
7. **Create onboarding flow** - 4 hours
8. **Write help docs** - 3 hours

**Total: ~20 hours of work**

---

## Questions to Answer Before Launch

- [ ] What's your target customer? (Dentist? Plumber? All?)
- [ ] What's your unique angle? (Cheaper? Better? Easier?)
- [ ] Who are your 3 biggest competitors?
- [ ] What do customers hate about competitors?
- [ ] How will you get first 10 customers?
- [ ] What's your customer support plan?
- [ ] How will you handle refunds/cancellations?
- [ ] What's your churn prediction?

---

## Reality Check

**You don't need:**
- Fancy UI (functional is fine)
- Multiple landing pages (one works)
- Sales team (ads work better)
- Advanced features (MVP is enough)
- Perfect infrastructure (good enough is fine)

**You do need:**
- Working product (you have it)
- Clear value prop (save $5k-30k/month in missed calls)
- Easy signup (Stripe + form)
- Customer support (email is fine)
- Paid ads (to get customers)

**Timeline:**
- Week 1-2: Launch
- Week 3-4: First customers
- Week 5-8: Automate + scale
- Week 9-12: Hit $3-5k MRR

**Confidence:** High (proven model, clear path, MVP ready)

---

## Next Step

Pick ONE thing to do today:
1. Set up Stripe account
2. Write landing page copy
3. Record demo video
4. Call 5 local dentists

Don't do all 4. Pick one and finish it.

**What's your first move?**
