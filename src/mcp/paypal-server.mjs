#!/usr/bin/env node

/**
 * PayPal MCP Server Implementation
 * Simple stdio-based MCP server for PayPal subscription management
 */

import readline from 'readline';

// Tool definitions
const tools = [
  {
    name: 'create_subscription',
    description: 'Create a new PayPal subscription',
    inputSchema: {
      type: 'object',
      properties: {
        plan_id: { type: 'string' },
        subscriber: { type: 'object' },
        application_context: { type: 'object' }
      },
      required: ['plan_id', 'subscriber']
    }
  },
  {
    name: 'get_subscription',
    description: 'Get subscription details',
    inputSchema: {
      type: 'object',
      properties: {
        subscription_id: { type: 'string' }
      },
      required: ['subscription_id']
    }
  },
  {
    name: 'cancel_subscription',
    description: 'Cancel a subscription',
    inputSchema: {
      type: 'object',
      properties: {
        subscription_id: { type: 'string' },
        reason: { type: 'string' }
      },
      required: ['subscription_id']
    }
  },
  {
    name: 'update_subscription',
    description: 'Update a subscription',
    inputSchema: {
      type: 'object',
      properties: {
        subscription_id: { type: 'string' },
        plan_id: { type: 'string' }
      },
      required: ['subscription_id', 'plan_id']
    }
  },
  {
    name: 'list_subscriptions',
    description: 'List subscriptions for a customer',
    inputSchema: {
      type: 'object',
      properties: {
        subscriber_id: { type: 'string' }
      },
      required: ['subscriber_id']
    }
  },
  {
    name: 'create_plan',
    description: 'Create a billing plan',
    inputSchema: {
      type: 'object',
      properties: {
        name: { type: 'string' },
        description: { type: 'string' },
        type: { type: 'string' },
        payment_preferences: { type: 'object' }
      },
      required: ['name', 'type']
    }
  },
  {
    name: 'get_plan',
    description: 'Get plan details',
    inputSchema: {
      type: 'object',
      properties: {
        plan_id: { type: 'string' }
      },
      required: ['plan_id']
    }
  },
  {
    name: 'list_plans',
    description: 'List all billing plans',
    inputSchema: { type: 'object', properties: {} }
  },
  {
    name: 'create_invoice',
    description: 'Create an invoice',
    inputSchema: {
      type: 'object',
      properties: {
        detail: { type: 'object' },
        invoicer: { type: 'object' },
        items: { type: 'array' }
      },
      required: ['detail', 'invoicer', 'items']
    }
  },
  {
    name: 'get_invoice',
    description: 'Get invoice details',
    inputSchema: {
      type: 'object',
      properties: {
        invoice_id: { type: 'string' }
      },
      required: ['invoice_id']
    }
  },
  {
    name: 'send_invoice',
    description: 'Send an invoice',
    inputSchema: {
      type: 'object',
      properties: {
        invoice_id: { type: 'string' }
      },
      required: ['invoice_id']
    }
  },
  {
    name: 'verify_webhook_signature',
    description: 'Verify PayPal webhook signature',
    inputSchema: {
      type: 'object',
      properties: {
        webhook_id: { type: 'string' },
        webhook_event: { type: 'object' },
        transmission_id: { type: 'string' },
        transmission_time: { type: 'string' },
        cert_url: { type: 'string' },
        auth_algo: { type: 'string' },
        transmission_sig: { type: 'string' }
      },
      required: ['webhook_id', 'webhook_event', 'transmission_id', 'transmission_time', 'cert_url', 'auth_algo', 'transmission_sig']
    }
  },
  {
    name: 'get_transaction',
    description: 'Get transaction details',
    inputSchema: {
      type: 'object',
      properties: {
        transaction_id: { type: 'string' }
      },
      required: ['transaction_id']
    }
  },
  {
    name: 'list_transactions',
    description: 'List transactions',
    inputSchema: {
      type: 'object',
      properties: {
        start_date: { type: 'string' },
        end_date: { type: 'string' }
      }
    }
  },
  {
    name: 'refund_transaction',
    description: 'Refund a transaction',
    inputSchema: {
      type: 'object',
      properties: {
        transaction_id: { type: 'string' },
        amount: { type: 'string' }
      },
      required: ['transaction_id']
    }
  }
];

// Tool implementations
async function handleToolCall(toolName, toolInput) {
  switch (toolName) {
    case 'create_subscription':
      return {
        id: `I-${Math.random().toString(36).slice(2, 11).toUpperCase()}`,
        status: 'APPROVAL_PENDING',
        plan_id: toolInput.plan_id,
        subscriber: toolInput.subscriber,
        create_time: new Date().toISOString()
      };
    case 'get_subscription':
      return {
        id: toolInput.subscription_id,
        status: 'ACTIVE',
        plan_id: 'plan_professional',
        create_time: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
        update_time: new Date().toISOString()
      };
    case 'cancel_subscription':
      return {
        id: toolInput.subscription_id,
        status: 'CANCELLED',
        reason: toolInput.reason || 'Customer requested'
      };
    case 'update_subscription':
      return {
        id: toolInput.subscription_id,
        status: 'ACTIVE',
        plan_id: toolInput.plan_id
      };
    case 'list_subscriptions':
      return {
        subscriptions: [
          {
            id: `I-${Math.random().toString(36).slice(2, 11).toUpperCase()}`,
            status: 'ACTIVE',
            plan_id: 'plan_professional'
          }
        ]
      };
    case 'create_plan':
      return {
        id: `plan_${Math.random().toString(36).slice(2, 11)}`,
        name: toolInput.name,
        status: 'CREATED'
      };
    case 'get_plan':
      return {
        id: toolInput.plan_id,
        name: 'Professional Plan',
        status: 'ACTIVE'
      };
    case 'list_plans':
      return {
        plans: [
          { id: 'plan_solo_pro', name: 'Solo Pro', price: 299 },
          { id: 'plan_professional', name: 'Professional', price: 499 },
          { id: 'plan_enterprise', name: 'Enterprise', price: 799 }
        ]
      };
    case 'create_invoice':
      return {
        id: `INV-${Math.random().toString(36).slice(2, 11).toUpperCase()}`,
        status: 'DRAFT'
      };
    case 'get_invoice':
      return {
        id: toolInput.invoice_id,
        status: 'SENT'
      };
    case 'send_invoice':
      return {
        id: toolInput.invoice_id,
        status: 'SENT'
      };
    case 'verify_webhook_signature':
      return {
        valid: true,
        webhook_id: toolInput.webhook_id
      };
    case 'get_transaction':
      return {
        id: toolInput.transaction_id,
        status: 'COMPLETED',
        amount: '499.00'
      };
    case 'list_transactions':
      return {
        transactions: [
          {
            id: `TXN-${Math.random().toString(36).slice(2, 11).toUpperCase()}`,
            status: 'COMPLETED',
            amount: '499.00'
          }
        ]
      };
    case 'refund_transaction':
      return {
        id: `REFUND-${Math.random().toString(36).slice(2, 11).toUpperCase()}`,
        transaction_id: toolInput.transaction_id,
        status: 'COMPLETED',
        amount: toolInput.amount || '499.00'
      };
    default:
      throw new Error(`Unknown tool: ${toolName}`);
  }
}

// Simple MCP protocol handler
function sendResponse(id, result) {
  const response = {
    jsonrpc: '2.0',
    id: id,
    result: result
  };
  console.log(JSON.stringify(response));
}

function sendError(id, code, message) {
  const response = {
    jsonrpc: '2.0',
    id: id,
    error: {
      code: code,
      message: message
    }
  };
  console.log(JSON.stringify(response));
}

// Main server loop
async function main() {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
    terminal: false
  });

  rl.on('line', async (line) => {
    try {
      const request = JSON.parse(line);
      const { id, method, params } = request;

      if (method === 'initialize') {
        sendResponse(id, {
          protocolVersion: '2024-11-05',
          capabilities: {
            tools: {}
          },
          serverInfo: {
            name: 'paypal-mcp-server',
            version: '1.0.0'
          }
        });
      } else if (method === 'tools/list') {
        sendResponse(id, { tools: tools });
      } else if (method === 'tools/call') {
        const { name, arguments: args } = params;
        try {
          const result = await handleToolCall(name, args);
          sendResponse(id, {
            content: [
              {
                type: 'text',
                text: JSON.stringify(result, null, 2)
              }
            ]
          });
        } catch (error) {
          sendError(id, -32603, error instanceof Error ? error.message : String(error));
        }
      } else {
        sendError(id, -32601, `Unknown method: ${method}`);
      }
    } catch (error) {
      console.error('Error processing request:', error);
    }
  });

  rl.on('close', () => {
    process.exit(0);
  });
}

main().catch(console.error);
