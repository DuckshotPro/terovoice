---
name: "twilio-telephony"
displayName: "Twilio Telephony Integration"
description: "Complete Twilio integration for AI voice agents with phone number management, SIP trunk configuration, call routing, and telephony analytics."
keywords: ["twilio", "telephony", "sip", "phone-numbers", "voice-calls", "sms", "ai-receptionist"]
author: "AI Voice Agent SaaS"
---

# Twilio Telephony Integration

## Overview

This power provides comprehensive Twilio integration for AI voice agent systems. It handles phone number provisioning, SIP trunk configuration, call routing, SMS capabilities, and telephony analytics for your AI receptionist SaaS.

The power integrates with Twilio's Voice API, Programmable Messaging, Phone Numbers API, and SIP Trunking to provide a complete telephony solution. It supports automated phone number purchasing, webhook configuration, call quality monitoring, and multi-tenant phone number management.

Key capabilities include phone number lifecycle management, SIP trunk automation, call routing configuration, SMS notifications, webhook processing, and comprehensive telephony analytics for your AI voice agent business.

## Onboarding

### Prerequisites

- Twilio Account with Voice and Messaging enabled
- Twilio Account SID and Auth Token
- Verified phone number for testing
- Webhook endpoint URL for call/SMS handling
- SSL certificate for webhook endpoints (required by Twilio)

### Twilio Account Setup

1. **Create Twilio Account:**
   - Sign up at https://www.twilio.com/
   - Complete phone number verification
   - Add billing information for production use

2. **Get API Credentials:**
   - Go to Twilio Console Dashboard
   - Copy Account SID and Auth Token
   - Note your Twilio phone number (if you have one)

3. **Configure Webhooks:**
   - Set up webhook URLs for:
     - Voice calls: `https://yourdomain.com/webhooks/twilio/voice`
     - SMS messages: `https://yourdomain.com/webhooks/twilio/sms`
     - Status callbacks: `https://yourdomain.com/webhooks/twilio/status`

### Installation

The Twilio MCP server provides tools for phone number management, call handling, and SMS capabilities.

### Configuration

Set these environment variables in your MCP configuration:

- `TWILIO_ACCOUNT_SID`: Your Twilio Account SID
- `TWILIO_AUTH_TOKEN`: Your Twilio Auth Token
- `TWILIO_PHONE_NUMBER`: Your primary Twilio phone number (optional)
- `TWILIO_WEBHOOK_URL`: Base URL for your webhook endpoints

## Common Workflows

### Workflow 1: Purchase and Configure Phone Numbers

**Goal:** Automatically purchase phone numbers for new AI receptionist clients

**Steps:**
1. Search available phone numbers by area code
2. Purchase phone number for client
3. Configure webhooks for voice and SMS
4. Set up SIP trunk routing
5. Test phone number functionality

**Example:**
```javascript
// Search for available phone numbers
const availableNumbers = await twilio.searchPhoneNumbers({
  areaCode: "555",
  type: "local",
  voiceEnabled: true,
  smsEnabled: true,
  limit: 10
});

// Purchase phone number for client
const phoneNumber = await twilio.purchasePhoneNumber({
  phoneNumber: availableNumbers[0].phoneNumber,
  friendlyName: "Dr. Mike Dentistry - AI Receptionist",
  voiceUrl: "https://yourdomain.com/webhooks/twilio/voice/dr-mike",
  smsUrl: "https://yourdomain.com/webhooks/twilio/sms/dr-mike",
  statusCallback: "https://yourdomain.com/webhooks/twilio/status/dr-mike"
});

console.log(`Phone number purchased: ${phoneNumber.phoneNumber}`);
```

### Workflow 2: SIP Trunk Configuration

**Goal:** Configure SIP trunks to route calls to AI voice agents

**Steps:**
1. Create SIP trunk for client
2. Configure authentication credentials
3. Set up call routing rules
4. Configure failover options
5. Test SIP connectivity

**Example:**
```javascript
// Create SIP trunk for AI voice agent
const sipTrunk = await twilio.createSipTrunk({
  friendlyName: "Dr. Mike AI Receptionist Trunk",
  domainName: "dr-mike.yourdomain.com",
  auth: {
    username: "dr_mike_ai",
    password: "secure_random_password"
  },
  termination: {
    sipUri: "sip:livekit.yourdomain.com:5060",
    username: "livekit_user",
    password: "livekit_password"
  }
});

// Configure phone number to use SIP trunk
await twilio.configurePhoneNumber({
  phoneNumber: "+15551234567",
  sipTrunkSid: sipTrunk.sid,
  voiceReceiveMode: "voice"
});
```

### Workflow 3: Call Routing and Handling

**Goal:** Route incoming calls to appropriate AI voice agents

**Steps:**
1. Receive incoming call webhook
2. Identify client based on called number
3. Route to appropriate AI agent
4. Handle call events and status updates
5. Log call analytics

**Example:**
```javascript
// Handle incoming call webhook
app.post('/webhooks/twilio/voice/:clientId', async (req, res) => {
  const clientId = req.params.clientId;
  const callSid = req.body.CallSid;
  const from = req.body.From;
  const to = req.body.To;

  // Get client configuration
  const clientConfig = await getClientConfig(clientId);
  
  // Generate TwiML to connect to LiveKit
  const twiml = new VoiceResponse();
  
  twiml.connect().stream({
    url: `wss://livekit.yourdomain.com/ws?client=${clientId}&call=${callSid}`,
    track: 'both_tracks'
  });

  // Log call start
  await logCallEvent({
    clientId,
    callSid,
    from,
    to,
    event: 'call_started',
    timestamp: new Date()
  });

  res.type('text/xml');
  res.send(twiml.toString());
});
```

### Workflow 4: SMS Integration

**Goal:** Send SMS notifications and handle incoming messages

**Steps:**
1. Send appointment confirmations via SMS
2. Handle incoming SMS queries
3. Route SMS to appropriate handlers
4. Track SMS delivery status
5. Manage opt-outs and compliance

**Example:**
```javascript
// Send appointment confirmation SMS
const confirmationSms = await twilio.sendSms({
  to: "+15551234567",
  from: "+15559876543",
  body: "Hi John! Your dental appointment with Dr. Mike is confirmed for tomorrow at 2:00 PM. Reply STOP to opt out.",
  statusCallback: "https://yourdomain.com/webhooks/twilio/sms-status"
});

// Handle incoming SMS
app.post('/webhooks/twilio/sms/:clientId', async (req, res) => {
  const clientId = req.params.clientId;
  const from = req.body.From;
  const body = req.body.Body;
  
  // Check for opt-out keywords
  if (body.toLowerCase().includes('stop')) {
    await handleOptOut(from, clientId);
    return res.status(200).send();
  }
  
  // Process SMS with AI
  const response = await processIncomingSms(clientId, from, body);
  
  // Send AI response
  if (response) {
    await twilio.sendSms({
      to: from,
      from: req.body.To,
      body: response
    });
  }
  
  res.status(200).send();
});
```

### Workflow 5: Telephony Analytics

**Goal:** Track call quality, usage, and performance metrics

**Steps:**
1. Collect call detail records (CDRs)
2. Analyze call quality metrics
3. Track usage by client
4. Generate billing reports
5. Monitor system performance

**Example:**
```javascript
// Get call analytics for client
const analytics = await twilio.getCallAnalytics({
  clientId: "dr-mike-dentistry",
  startDate: "2025-01-01",
  endDate: "2025-01-31"
});

// Calculate metrics
const metrics = {
  totalCalls: analytics.calls.length,
  totalMinutes: analytics.calls.reduce((sum, call) => sum + call.duration, 0) / 60,
  averageCallDuration: analytics.calls.reduce((sum, call) => sum + call.duration, 0) / analytics.calls.length,
  callQualityScore: analytics.calls.reduce((sum, call) => sum + (call.quality || 0), 0) / analytics.calls.length,
  costPerMinute: 0.0085, // Twilio voice pricing
  totalCost: (analytics.calls.reduce((sum, call) => sum + call.duration, 0) / 60) * 0.0085
};

// Generate monthly report
const report = await generateTelephonyReport(metrics);
```

## Troubleshooting

### Phone Number Purchase Failures

**Problem:** Unable to purchase phone numbers
**Symptoms:**
- Error: "No phone numbers available"
- Purchase requests fail

**Solutions:**
1. Check Twilio account balance and billing status
2. Verify area code availability in your region
3. Try different area codes or number types
4. Check Twilio account limits and upgrade if needed
5. Ensure proper API credentials and permissions

### SIP Trunk Connection Issues

**Problem:** SIP trunk fails to connect or route calls
**Symptoms:**
- Calls don't reach AI agent
- SIP authentication failures
- Call quality issues

**Solutions:**
1. Verify SIP credentials and configuration
2. Check firewall rules for SIP ports (5060, 5061)
3. Test SIP connectivity with SIP testing tools
4. Verify LiveKit server SIP configuration
5. Check network latency and quality

### Webhook Delivery Failures

**Problem:** Twilio webhooks not reaching your server
**Symptoms:**
- Missing call events
- SMS not processed
- Status updates not received

**Solutions:**
1. Verify webhook URLs are accessible from internet
2. Check SSL certificate validity
3. Ensure webhook endpoints return 200 status
4. Test webhook URLs with curl or Postman
5. Check Twilio webhook logs in console

### Call Quality Issues

**Problem:** Poor audio quality or dropped calls
**Symptoms:**
- Choppy or distorted audio
- Calls dropping unexpectedly
- High latency

**Solutions:**
1. Check network bandwidth and stability
2. Optimize codec selection (prefer G.711)
3. Monitor jitter and packet loss
4. Use Twilio Insights for call quality analysis
5. Consider geographic routing optimization

### SMS Delivery Problems

**Problem:** SMS messages not delivered or delayed
**Symptoms:**
- Messages stuck in queue
- Delivery failures
- Compliance violations

**Solutions:**
1. Verify phone numbers are properly formatted
2. Check carrier filtering and spam detection
3. Ensure compliance with SMS regulations
4. Monitor delivery receipts and error codes
5. Implement proper opt-out handling

## Best Practices

- **Always validate phone numbers** before purchasing or messaging
- **Implement proper webhook security** with request validation
- **Monitor call quality metrics** continuously
- **Handle opt-outs and compliance** properly for SMS
- **Use status callbacks** to track call and message status
- **Implement retry logic** for failed API calls
- **Store webhook events** for debugging and analytics
- **Regular monitoring** of Twilio account usage and limits
- **Proper error handling** for all Twilio API operations
- **Security best practices** for SIP credentials and webhooks

## Configuration

### Environment Variables

- `TWILIO_ACCOUNT_SID`: Your Twilio Account SID (required)
- `TWILIO_AUTH_TOKEN`: Your Twilio Auth Token (required)
- `TWILIO_PHONE_NUMBER`: Your primary Twilio phone number (optional)
- `TWILIO_WEBHOOK_URL`: Base URL for webhook endpoints (required)
- `TWILIO_WEBHOOK_SECRET`: Secret for webhook validation (optional)

### Phone Number Configuration

Configure phone numbers for different clients:

```javascript
const CLIENT_PHONE_CONFIG = {
  "dr-mike-dentistry": {
    phoneNumber: "+15551234567",
    friendlyName: "Dr. Mike Dentistry AI Receptionist",
    voiceUrl: "https://yourdomain.com/webhooks/twilio/voice/dr-mike",
    smsUrl: "https://yourdomain.com/webhooks/twilio/sms/dr-mike"
  },
  "joes-plumbing": {
    phoneNumber: "+15559876543", 
    friendlyName: "Joe's Plumbing AI Receptionist",
    voiceUrl: "https://yourdomain.com/webhooks/twilio/voice/joes-plumbing",
    smsUrl: "https://yourdomain.com/webhooks/twilio/sms/joes-plumbing"
  }
};
```

### SIP Trunk Templates

Standard SIP trunk configurations:

```javascript
const SIP_TRUNK_TEMPLATES = {
  livekit: {
    domainName: "livekit.yourdomain.com",
    termination: {
      sipUri: "sip:livekit.yourdomain.com:5060",
      codecs: ["PCMU", "PCMA"],
      dtmf: "rfc2833"
    },
    origination: {
      sipUri: "sip:twilio.yourdomain.com:5060"
    }
  }
};
```

---

**Package:** `mcp-server-twilio`
**MCP Server:** twilio