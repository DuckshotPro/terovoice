# Tero Voice - Local Agency Model

**Business Model:** Premium hands-on service for local businesses ($500-2k/month)
**Sales Strategy:** Direct outreach + small targeted Facebook ads
**Automation:** Browser automation for lead generation & outreach
**Timeline:** 2 weeks to first client, 90 days to $10k MRR
**Date:** January 4, 2026

---

## Business Model

### Pricing (Premium, Hands-On)
- **Starter:** $500/month (setup + 3 months support)
- **Professional:** $1,000/month (setup + 6 months support + optimization)
- **Premium:** $2,000/month (setup + 12 months support + dedicated account manager)

### What You Provide
- Personal onboarding call
- Voice cloning (you guide them)
- Custom prompt optimization
- Weekly check-ins first month
- Monthly performance reviews
- Direct phone/email support
- Optimization recommendations

### Why This Works
- Local businesses prefer personal relationships
- They'll pay 10x more for hands-on support
- Lower customer count = easier to manage
- Higher margins = sustainable business
- Referrals are easier (they know you)

---

## What YOU Code (2 Days)

### Day 1: Billing + Onboarding
- [ ] Stripe integration ($500-2k/month tiers)
- [ ] Simple signup form (name, business, phone, email)
- [ ] Auto-generate client dashboard URL
- [ ] Send welcome email with setup guide
- [ ] Create client database (store phone, business type, etc.)

### Day 2: Client Management
- [ ] Create admin dashboard (list all clients)
- [ ] Client status tracker (setup → live → optimizing)
- [ ] Call analytics display (calls/day, success rate, revenue impact)
- [ ] Notes system (track client interactions)
- [ ] Invoice/payment history

**Total code time: 2 days with AI**

---

## What Comet Browser LLM Automates (Lead Generation)

### Task 1: Find Local Businesses (Daily)
**Goal:** Find 50 dentists/plumbers/contractors in your area

**Comet automation:**
```
1. Go to Google Maps
2. Search "dentists near [your city]"
3. Extract: name, phone, address, website, hours
4. Save to spreadsheet
5. Repeat for: plumbers, contractors, electricians, locksmiths
6. Filter out chains (focus on solo/small practices)
7. Save to CSV
```

**Output:** 200+ local business leads per week

**Why this works:**
- Google Maps has all the data you need
- Browser automation can extract it in minutes
- You get fresh leads daily
- No API needed

---

### Task 2: Personalized Outreach (Daily)
**Goal:** Send personalized emails to leads

**Comet automation:**
```
1. Read lead list (name, business, phone)
2. For each lead:
   a. Generate personalized email:
      "Hi [Name], I noticed [Business Name] is a [profession].
       Most [profession]s lose $5k-30k/month to missed calls.
       I built an AI receptionist that answers calls 24/7.
       Free 15-min demo? [Link]"
   b. Send via Gmail/SendGrid
   c. Log sent date
3. Track opens/clicks
4. Auto-follow-up after 3 days if no response
```

**Output:** 50-100 personalized emails per day

**Why this works:**
- Personalization = 5x higher response rate
- Automation = no manual work
- Follow-ups = 30% of responses come from follow-up
- You focus on calls, not emails

---

### Task 3: Facebook Ad Campaign Setup (Weekly)
**Goal:** Create and launch targeted Facebook ads

**Comet automation:**
```
1. Create 3 ad variations:
   - "Stop losing $10k/month to missed calls"
   - "Your competitors have AI receptionists. Do you?"
   - "24/7 AI receptionist for [profession]"
2. For each profession (dentist, plumber, contractor):
   a. Create audience (age 35-65, business owners, [city])
   b. Create landing page (Comet fills in profession-specific copy)
   c. Set budget ($5-10/day per profession)
   d. Launch campaign
   e. Track conversions
3. Daily: Check performance, pause underperformers
4. Weekly: Scale winners, test new variations
```

**Output:** 3-5 campaigns running, $15-30/day spend

**Why this works:**
- Targeted ads = lower CAC
- Automation = set and forget
- You only manage winners
- Small budget = low risk

---

### Task 4: Lead Qualification (Daily)
**Goal:** Automatically qualify leads before you call

**Comet automation:**
```
1. For each lead that clicked ad or opened email:
   a. Visit their website
   b. Extract: business type, size, phone volume (estimate)
   c. Check if they have existing phone system
   d. Score lead (1-10 based on fit)
2. Create "hot leads" list (score 8-10)
3. Send you daily summary:
   - 5 hot leads to call today
   - 10 warm leads for follow-up
   - 20 cold leads for nurture
```

**Output:** Pre-qualified leads ready to call

**Why this works:**
- You only call hot leads
- Higher conversion rate
- Less time wasted on bad fits
- Automation does the research

---

### Task 5: Follow-Up Automation (Daily)
**Goal:** Auto-follow-up with leads who didn't respond

**Comet automation:**
```
1. Track all outreach (emails, ads, calls)
2. For each lead:
   a. If no response after 3 days → send follow-up email
   b. If no response after 7 days → send SMS (if phone available)
   c. If no response after 14 days → move to "nurture" list
3. Nurture list gets weekly tips:
   - "5 ways to reduce missed calls"
   - "How AI receptionists save $30k/year"
   - "Case study: [similar business] saved $50k"
4. Track which nurture emails get opens
5. Re-engage high-engagement leads
```

**Output:** Consistent follow-up without manual work

**Why this works:**
- 80% of sales come from follow-up
- Automation = consistent follow-up
- Nurture = builds trust over time
- You focus on hot leads

---

## Your Weekly Schedule

### Monday (2 hours)
- Review weekend leads
- Call 5 hot leads
- Send personalized follow-ups
- Update client status

### Tuesday-Thursday (1 hour each)
- Call 5 hot leads per day
- Demo calls with interested leads
- Onboarding calls with new clients
- Check ad performance

### Friday (2 hours)
- Review week's results
- Optimize ads (pause underperformers, scale winners)
- Plan next week's outreach
- Client check-ins

### Ongoing (Automated)
- Comet finds leads daily
- Comet sends emails daily
- Comet qualifies leads daily
- Comet follows up daily
- You just call hot leads

**Total time: ~10 hours/week**

---

## Revenue Model

### Month 1
- Clients: 2-3
- Revenue: $1,000-2,000
- Time: 20 hours (setup + calls)

### Month 2
- Clients: 5-8
- Revenue: $3,000-6,000
- Time: 30 hours (onboarding + support)

### Month 3
- Clients: 10-15
- Revenue: $7,000-15,000
- Time: 40 hours (onboarding + support + optimization)

### Month 6
- Clients: 20-30
- Revenue: $15,000-30,000
- Time: 60 hours (you might hire support person)

---

## Cost Structure

### Infrastructure
- VPS: $50/month
- Database: $20/month
- Monitoring: $10/month
- **Subtotal: $80/month**

### Services
- Stripe fees: 2.9% + $0.30 per transaction (~$50 at $5k MRR)
- Email service: $20/month
- Voice cloning API: ~$100/month (varies)
- SMS service: $20/month (for follow-ups)
- **Subtotal: $190/month**

### Marketing
- Facebook ads: $100-300/month (you control)
- Landing page hosting: $10/month
- **Subtotal: $110-310/month**

### Total Monthly Cost: ~$380-580

**At $10k MRR:**
- Revenue: $10,000
- Costs: $500
- Gross profit: $9,500
- Gross margin: 95%

---

## Comet Browser Automation Setup

### What Comet Does
1. **Lead generation** - Find businesses on Google Maps
2. **Email outreach** - Send personalized emails
3. **Ad management** - Create and manage Facebook ads
4. **Lead qualification** - Score leads automatically
5. **Follow-up** - Auto-follow-up sequences

### How to Set It Up
1. Create Comet account
2. Give it access to:
   - Gmail (for sending emails)
   - Facebook Ads (for creating campaigns)
   - Google Maps (for finding leads)
   - Spreadsheet (for storing leads)
3. Create automation rules:
   - "Find 50 dentists daily"
   - "Send personalized email to each"
   - "Follow up after 3 days"
   - "Create Facebook ad for each profession"
4. Monitor daily (5 minutes)

### Cost
- Comet Browser: $50-100/month
- Total automation cost: ~$50-100/month

---

## Your First 2 Weeks

### Week 1: Setup
- [ ] Day 1-2: Code Stripe + onboarding (2 days)
- [ ] Day 3: Set up Comet Browser automation
- [ ] Day 4: Create landing page (Comet can help)
- [ ] Day 5: Deploy to production

### Week 2: Launch
- [ ] Day 1: Start Comet lead generation
- [ ] Day 2-5: Call hot leads (5 calls/day)
- [ ] Goal: Get 2-3 first clients

---

## What You Actually Do (Hands-On)

### Sales Calls (30 min each)
- Listen to their pain (missed calls, lost revenue)
- Show demo of AI answering their phone
- Explain how it works
- Quote price ($500-2k/month)
- Close deal

### Onboarding (1-2 hours per client)
- Record their voice sample
- Clone voice
- Customize prompt for their profession
- Set up phone routing
- Do first test call together
- Send them live

### Monthly Check-Ins (30 min per client)
- Review call metrics
- Show revenue impact
- Optimize prompt if needed
- Answer questions
- Upsell if appropriate

### Support (As needed)
- Email support for issues
- Phone support for urgent issues
- Optimization recommendations

---

## Success Metrics

### Sales Metrics
- Leads generated: 200+/week (Comet)
- Response rate: 5-10% (50-100 responses/week)
- Demo rate: 20-30% of responses (10-30 demos/week)
- Close rate: 30-50% of demos (3-15 closes/week)
- CAC: $50-100 (cost per customer)

### Revenue Metrics
- Month 1: $1-2k
- Month 2: $3-6k
- Month 3: $7-15k
- Month 6: $15-30k

### Operational Metrics
- Time per client: 5 hours (setup + first month)
- Time per month: 40 hours (onboarding + support)
- Profit per client: $5k-20k (lifetime)

---

## Immediate Action Items (This Week)

1. **Code Stripe integration** (4 hours with AI)
2. **Code client dashboard** (4 hours with AI)
3. **Set up Comet Browser** (2 hours)
4. **Create landing page** (2 hours)
5. **Deploy to production** (1 hour)
6. **Start lead generation** (Comet runs automatically)

**Total: ~13 hours of work**

---

## Why This Model Works

✅ **High margins** - 95% gross margin
✅ **Low customer count** - 20-30 clients = $15-30k/month
✅ **Hands-on support** - Customers love you, refer you
✅ **Automation** - Comet does lead gen, you do sales
✅ **Local focus** - You know your market
✅ **Scalable** - Hire support person at $10k/month
✅ **Sustainable** - Not dependent on ads or virality

---

## Risks & Mitigation

### Risk: Customers churn after setup
**Mitigation:** Monthly check-ins + optimization = they see ROI

### Risk: You get overwhelmed with support
**Mitigation:** Hire support person at $10k/month revenue

### Risk: Ads don't work
**Mitigation:** Direct outreach works better anyway (Comet does it)

### Risk: Competitors undercut you
**Mitigation:** Your hands-on support is your moat

---

## Next Step

**Pick ONE to start today:**
1. Code Stripe integration
2. Set up Comet Browser
3. Create landing page

**What's your first move?**

---

## Appendix: Comet Browser Automation Examples

### Example 1: Find Dentists
```
1. Go to Google Maps
2. Search "dentists near [city]"
3. Extract: name, phone, address, website
4. Filter: solo practices only (not chains)
5. Save to spreadsheet
6. Repeat for 5 nearby cities
```

### Example 2: Send Personalized Email
```
For each dentist:
1. Get their name and business name
2. Generate email:
   "Hi [Name],
    I noticed [Business] is a dental practice.
    Most dentists lose $10k-30k/month to missed calls.
    I built an AI receptionist that answers calls 24/7.
    Would you like a free 15-min demo?
    [Link to demo]"
3. Send via Gmail
4. Log sent date
```

### Example 3: Create Facebook Ad
```
1. Create audience: age 35-65, business owners, [city], dentists
2. Create ad copy:
   "Stop losing $10k/month to missed calls.
    AI receptionist answers 24/7.
    Free demo: [link]"
3. Set budget: $5/day
4. Launch campaign
5. Track conversions
```

---

**Status:** Ready to execute
**Confidence:** Very high (proven model, clear path, automation handles lead gen)
**Timeline:** 2 weeks to first client, 90 days to $10k MRR
**Next Review:** Weekly progress check-ins
