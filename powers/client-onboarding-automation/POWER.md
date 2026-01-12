---
name: "client-onboarding-automation"
displayName: "Client Onboarding Automation"
description: "Automated client onboarding system for AI receptionist SaaS with voice cloning, infrastructure provisioning, and 60-second activation workflows."
keywords: ["onboarding", "automation", "voice-cloning", "provisioning", "ai-receptionist", "saas", "client-activation"]
author: "AI Voice Agent SaaS"
---

# Client Onboarding Automation

## Overview

This power provides complete automation for onboarding new AI receptionist clients. It handles the entire process from payment confirmation to service activation, including voice cloning, infrastructure provisioning, dashboard creation, and client notification - all within 60 seconds of payment.

The power integrates with PayPal webhooks, voice cloning services, container orchestration, and email systems to provide a seamless onboarding experience. It supports multi-tier pricing plans, profession-specific customization, and automated quality assurance testing.

Key capabilities include automated voice cloning from 30-second samples, infrastructure provisioning, profession-specific prompt deployment, dashboard generation, welcome email automation, and comprehensive onboarding analytics.

## Onboarding

### Prerequisites

- PayPal webhook integration (for payment notifications)
- Voice cloning service (ElevenLabs, Cartesia, or local)
- Container orchestration (Docker/Podman)
- Email service (SMTP or SendGrid)
- Domain management for client subdomains
- SSL certificate automation (Let's Encrypt)

### Service Dependencies

1. **Payment Processing:**
   - PayPal webhook endpoint configured
   - Subscription plan IDs mapped to service tiers

2. **Voice Processing:**
   - Voice cloning API credentials
   - Audio processing pipeline
   - Quality validation system

3. **Infrastructure:**
   - Container registry access
   - Load balancer configuration
   - Database provisioning

### Installation

The Client Onboarding MCP server provides tools for automated client activation and service provisioning.

### Configuration

Set these environment variables in your MCP configuration:

- `VOICE_CLONING_API_KEY`: API key for voice cloning service
- `CONTAINER_REGISTRY_URL`: Docker registry for agent images
- `EMAIL_SMTP_HOST`: SMTP server for welcome emails
- `EMAIL_SMTP_USER`: SMTP username
- `EMAIL_SMTP_PASS`: SMTP password
- `DOMAIN_BASE`: Base domain for client subdomains
- `SSL_CERT_EMAIL`: Email for Let's Encrypt certificates

## Common Workflows

### Workflow 1: Automated Client Activation

**Goal:** Automatically activate new clients within 60 seconds of payment

**Steps:**
1. Receive PayPal webhook notification
2. Extract client information and plan details
3. Trigger parallel onboarding processes
4. Validate all services are running
5. Send welcome email with credentials

**Example:**
```javascript
// Handle PayPal subscription activation webhook
async function handleSubscriptionActivation(webhookData) {
  const subscription = webhookData.resource;
  const clientEmail = subscription.subscriber.email_address;
  const planId = subscription.plan_id;
  
  // Extract client information
  const clientInfo = {
    email: clientEmail,
    name: subscription.subscriber.name.given_name + ' ' + subscription.subscriber.name.surname,
    planId: planId,
    subscriptionId: subscription.id,
    clientId: generateClientId(clientEmail)
  };
  
  // Start parallel onboarding processes
  const onboardingTasks = await Promise.allSettled([
    cloneVoiceFromSample(clientInfo),
    provisionInfrastructure(clientInfo),
    createClientDashboard(clientInfo),
    setupProfessionPrompts(clientInfo),
    configurePhoneNumber(clientInfo)
  ]);
  
  // Validate all tasks completed successfully
  const failedTasks = onboardingTasks.filter(task => task.status === 'rejected');
  if (failedTasks.length > 0) {
    await handleOnboardingFailure(clientInfo, failedTasks);
    return;
  }
  
  // Send welcome email
  await sendWelcomeEmail(clientInfo);
  
  // Log successful onboarding
  await logOnboardingSuccess(clientInfo);
}
```

### Workflow 2: Voice Cloning Automation

**Goal:** Automatically clone client voice from uploaded sample

**Steps:**
1. Receive voice sample upload
2. Validate audio quality and duration
3. Process voice cloning
4. Test voice quality
5. Deploy voice model to production

**Example:**
```javascript
// Automated voice cloning workflow
async function cloneVoiceFromSample(clientInfo) {
  // Get voice sample from client upload
  const voiceSample = await getClientVoiceSample(clientInfo.clientId);
  
  if (!voiceSample) {
    throw new Error('No voice sample found for client');
  }
  
  // Validate audio quality
  const audioValidation = await validateAudioSample(voiceSample);
  if (!audioValidation.isValid) {
    throw new Error(`Invalid audio sample: ${audioValidation.errors.join(', ')}`);
  }
  
  // Clone voice using preferred service
  const voiceClone = await cloneVoice({
    audioFile: voiceSample.filePath,
    voiceName: `${clientInfo.name} Professional`,
    description: `AI receptionist voice for ${clientInfo.name}`,
    language: 'en-US'
  });
  
  // Test voice quality with sample text
  const testAudio = await synthesizeTestPhrase({
    voiceId: voiceClone.voiceId,
    text: "Thank you for calling. How may I help you today?"
  });
  
  // Validate voice quality
  const qualityScore = await assessVoiceQuality(testAudio);
  if (qualityScore < 0.8) {
    throw new Error(`Voice quality too low: ${qualityScore}`);
  }
  
  // Store voice configuration
  await storeVoiceConfig(clientInfo.clientId, {
    voiceId: voiceClone.voiceId,
    voiceName: voiceClone.voiceName,
    qualityScore: qualityScore,
    createdAt: new Date()
  });
  
  return voiceClone;
}
```

### Workflow 3: Infrastructure Provisioning

**Goal:** Automatically provision client infrastructure and services

**Steps:**
1. Create client namespace/containers
2. Deploy AI voice agent
3. Configure load balancing
4. Set up monitoring
5. Validate service health

**Example:**
```javascript
// Infrastructure provisioning workflow
async function provisionInfrastructure(clientInfo) {
  const clientId = clientInfo.clientId;
  
  // Create client-specific configuration
  const agentConfig = {
    clientId: clientId,
    image: 'ai-voice-agent:latest',
    environment: {
      CLIENT_ID: clientId,
      PROFESSION: await getProfessionFromPlan(clientInfo.planId),
      VOICE_ID: await getVoiceId(clientId),
      LIVEKIT_ROOM_PREFIX: `${clientId}-`,
      DATABASE_URL: await createClientDatabase(clientId)
    },
    resources: await getResourcesForPlan(clientInfo.planId)
  };
  
  // Deploy agent container
  const deployment = await deployAgentContainer(agentConfig);
  
  // Configure load balancer
  await configureLoadBalancer({
    clientId: clientId,
    targetPort: deployment.port,
    healthCheckPath: '/health'
  });
  
  // Set up monitoring
  await setupClientMonitoring({
    clientId: clientId,
    endpoints: [deployment.healthEndpoint],
    alertEmail: clientInfo.email
  });
  
  // Wait for service to be healthy
  await waitForServiceHealth(deployment.healthEndpoint, 30000);
  
  return deployment;
}
```

### Workflow 4: Dashboard and Subdomain Creation

**Goal:** Create client dashboard with unique subdomain

**Steps:**
1. Generate unique subdomain
2. Create SSL certificate
3. Deploy dashboard application
4. Configure DNS routing
5. Test dashboard accessibility

**Example:**
```javascript
// Dashboard creation workflow
async function createClientDashboard(clientInfo) {
  const subdomain = generateSubdomain(clientInfo.clientId);
  const fullDomain = `${subdomain}.${process.env.DOMAIN_BASE}`;
  
  // Create SSL certificate
  const sslCert = await createSSLCertificate({
    domain: fullDomain,
    email: process.env.SSL_CERT_EMAIL
  });
  
  // Deploy dashboard application
  const dashboardConfig = {
    clientId: clientInfo.clientId,
    domain: fullDomain,
    sslCert: sslCert,
    environment: {
      CLIENT_ID: clientInfo.clientId,
      CLIENT_NAME: clientInfo.name,
      CLIENT_EMAIL: clientInfo.email,
      PLAN_ID: clientInfo.planId,
      API_BASE_URL: `https://api.${process.env.DOMAIN_BASE}`
    }
  };
  
  const dashboard = await deployDashboard(dashboardConfig);
  
  // Configure DNS
  await configureDNS({
    subdomain: subdomain,
    target: dashboard.loadBalancerIP,
    type: 'A'
  });
  
  // Wait for DNS propagation and test
  await waitForDNSPropagation(fullDomain);
  await testDashboardAccess(fullDomain);
  
  // Store dashboard configuration
  await storeDashboardConfig(clientInfo.clientId, {
    url: `https://${fullDomain}`,
    deploymentId: dashboard.id,
    sslCertId: sslCert.id
  });
  
  return {
    url: `https://${fullDomain}`,
    credentials: dashboard.credentials
  };
}
```

### Workflow 5: Welcome Email and Documentation

**Goal:** Send comprehensive welcome email with setup instructions

**Steps:**
1. Generate client-specific documentation
2. Create login credentials
3. Prepare welcome email content
4. Send email with attachments
5. Track email delivery

**Example:**
```javascript
// Welcome email workflow
async function sendWelcomeEmail(clientInfo) {
  // Get client configuration
  const clientConfig = await getClientConfiguration(clientInfo.clientId);
  
  // Generate welcome email content
  const emailContent = await generateWelcomeEmail({
    clientName: clientInfo.name,
    dashboardUrl: clientConfig.dashboard.url,
    phoneNumber: clientConfig.phoneNumber,
    voicePreview: clientConfig.voice.previewUrl,
    planFeatures: await getPlanFeatures(clientInfo.planId),
    setupInstructions: await generateSetupInstructions(clientInfo)
  });
  
  // Create PDF documentation
  const setupGuide = await generateSetupGuidePDF(clientInfo);
  
  // Send welcome email
  const emailResult = await sendEmail({
    to: clientInfo.email,
    subject: `Welcome to AI Voice Receptionist - Your Service is Live!`,
    html: emailContent.html,
    text: emailContent.text,
    attachments: [
      {
        filename: 'setup-guide.pdf',
        content: setupGuide,
        contentType: 'application/pdf'
      }
    ]
  });
  
  // Schedule follow-up emails
  await scheduleFollowUpEmails(clientInfo, [
    { delay: '1 day', template: 'day1-checkin' },
    { delay: '1 week', template: 'week1-optimization' },
    { delay: '1 month', template: 'month1-review' }
  ]);
  
  return emailResult;
}
```

## Troubleshooting

### Voice Cloning Failures

**Problem:** Voice cloning fails or produces poor quality
**Symptoms:**
- Voice cloning API errors
- Low quality scores
- Robotic or distorted voice

**Solutions:**
1. Validate audio sample quality (clear, 30+ seconds)
2. Check voice cloning service status and limits
3. Retry with different cloning parameters
4. Fallback to default professional voice
5. Manual review and re-cloning if needed

### Infrastructure Provisioning Issues

**Problem:** Container deployment or service startup failures
**Symptoms:**
- Container fails to start
- Health checks failing
- Service not accessible

**Solutions:**
1. Check container registry access and image availability
2. Verify resource limits and quotas
3. Review container logs for startup errors
4. Validate environment variables and configuration
5. Rollback to known good configuration

### DNS and SSL Certificate Problems

**Problem:** Subdomain not accessible or SSL errors
**Symptoms:**
- DNS resolution failures
- SSL certificate errors
- Dashboard not loading

**Solutions:**
1. Check DNS propagation status
2. Verify SSL certificate generation and installation
3. Test with different DNS servers
4. Validate load balancer configuration
5. Check firewall and security group rules

### Email Delivery Issues

**Problem:** Welcome emails not delivered
**Symptoms:**
- Emails bouncing or going to spam
- SMTP authentication failures
- Email content rendering issues

**Solutions:**
1. Verify SMTP credentials and server settings
2. Check email content for spam triggers
3. Validate recipient email addresses
4. Test with different email providers
5. Monitor email delivery logs and bounce rates

### Onboarding Timeout Issues

**Problem:** Onboarding process takes longer than 60 seconds
**Symptoms:**
- Client activation timeouts
- Partial service deployment
- Inconsistent service state

**Solutions:**
1. Optimize parallel processing and reduce dependencies
2. Implement proper error handling and rollback
3. Pre-provision common resources
4. Use async processing for non-critical tasks
5. Monitor and optimize bottleneck operations

## Best Practices

- **Validate all inputs** before starting onboarding process
- **Use parallel processing** for independent onboarding tasks
- **Implement comprehensive error handling** with rollback capabilities
- **Monitor onboarding metrics** and optimize bottlenecks
- **Test onboarding process** regularly with automated tests
- **Provide clear status updates** to clients during onboarding
- **Store detailed logs** for debugging and analytics
- **Implement graceful degradation** for non-critical failures
- **Regular backup** of client configurations and data
- **Security best practices** for credential generation and storage

## Configuration

### Environment Variables

- `VOICE_CLONING_API_KEY`: API key for voice cloning service (required)
- `CONTAINER_REGISTRY_URL`: Docker registry URL (required)
- `EMAIL_SMTP_HOST`: SMTP server hostname (required)
- `EMAIL_SMTP_USER`: SMTP username (required)
- `EMAIL_SMTP_PASS`: SMTP password (required)
- `DOMAIN_BASE`: Base domain for client subdomains (required)
- `SSL_CERT_EMAIL`: Email for SSL certificate generation (required)

### Plan Configuration

Configure features and resources for different pricing tiers:

```javascript
const PLAN_CONFIGURATIONS = {
  "solo-pro": {
    name: "Solo Pro Plan",
    price: 299,
    features: ["Unlimited minutes", "Voice cloning", "Basic analytics"],
    resources: {
      cpu: "1 core",
      memory: "2GB",
      storage: "10GB"
    }
  },
  "pro": {
    name: "Pro Plan",
    price: 499,
    features: ["Everything in Solo", "Advanced analytics", "Priority support"],
    resources: {
      cpu: "2 cores", 
      memory: "4GB",
      storage: "25GB"
    }
  },
  "enterprise": {
    name: "Enterprise Plan",
    price: 799,
    features: ["Everything in Pro", "Multi-location", "Custom integrations"],
    resources: {
      cpu: "4 cores",
      memory: "8GB", 
      storage: "50GB"
    }
  }
};
```

### Profession Templates

Available profession-specific configurations:

```javascript
const PROFESSION_TEMPLATES = {
  dentist: {
    greeting: "Thank you for calling {business_name}. How may I help you today?",
    services: ["cleaning", "filling", "crown", "emergency"],
    prompts: "dentist-receptionist-prompts.json"
  },
  plumber: {
    greeting: "This is {business_name}, what plumbing issue can I help you with?",
    services: ["leak repair", "drain cleaning", "installation", "emergency"],
    prompts: "plumber-receptionist-prompts.json"
  }
  // ... additional professions
};
```

---

**Package:** `mcp-server-client-onboarding`
**MCP Server:** client-onboarding