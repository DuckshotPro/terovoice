#!/bin/bash

# Phase 1 Deployment Script for AI Phone SaaS (Bash)
# Deploys billing service infrastructure to the server
# Usage: ./scripts/deploy-phase1-to-server.sh [host] [user] [project_dir] [ssh_key]
# Example: ./scripts/deploy-phase1-to-server.sh 74.208.227.161 password /home/password/ai-phone-sas .kiro/private-keys/id_kiro

set -e

# Configuration (with defaults)
SERVER_HOST="${1:-74.208.227.161}"
SERVER_USER="${2:-password}"
PROJECT_DIR="${3:-/home/password/ai-phone-sas}"
SSH_KEY="${4:-.kiro/private-keys/id_kiro}"
SKIP_GIT_PUSH="${5:-false}"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

function write_status() {
    echo -e "${BLUE}$1${NC}"
}

function write_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

function write_error() {
    echo -e "${RED}❌ $1${NC}"
}

echo ""
write_status "========================================"
write_status "Phase 1: Billing Service Deployment"
write_status "========================================"

# Step 1: Verify SSH key exists
write_status "\nStep 1: Verifying SSH key..."
if [ ! -f "$SSH_KEY" ]; then
    write_error "SSH key not found at $SSH_KEY"
    exit 1
fi
write_success "SSH key found"

# Step 2: Test SSH connection
write_status "\nStep 2: Testing SSH connection..."
if ssh -i "$SSH_KEY" -o ConnectTimeout=5 "$SERVER_USER@$SERVER_HOST" "echo 'SSH connection successful'" > /dev/null 2>&1; then
    write_success "SSH connection successful"
else
    write_error "SSH connection failed"
    echo "Make sure:"
    echo "  1. Server is running"
    echo "  2. SSH key is correct"
    echo "  3. Server hostname/IP is correct: $SERVER_HOST"
    exit 1
fi

# Step 3: Push code to server or use SCP transfer
write_status "\nStep 3: Transferring code to server..."
if [ "$SKIP_GIT_PUSH" = "false" ]; then
    write_status "Attempting git push to repository..."
    if git push origin main > /dev/null 2>&1; then
        write_success "Code pushed to repository"

        # Step 3b: Pull latest code on server
        write_status "\nStep 3b: Pulling latest code on server..."
        ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_HOST" "cd $PROJECT_DIR && git pull origin main" > /dev/null 2>&1
        write_success "Code pulled on server"
    else
        write_status "Git push failed - using direct SCP transfer instead"
        SKIP_GIT_PUSH="true"
    fi
fi

# If git push failed, use SCP to transfer files directly
if [ "$SKIP_GIT_PUSH" = "true" ]; then
    write_status "\nStep 3b: Transferring files via SCP..."

    FILES_TO_TRANSFER=(
        "backend-setup/services/billing_service.py"
        "backend-setup/services/usage_service.py"
        "backend-setup/services/__init__.py"
        "backend-setup/db/models.py"
        "backend-setup/tests/test_billing_service_properties.py"
        "backend-setup/tests/__init__.py"
        "backend-setup/requirements.txt"
    )

    for file in "${FILES_TO_TRANSFER[@]}"; do
        remote_dir=$(dirname "$file")

        # Create remote directory
        ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_HOST" "mkdir -p $PROJECT_DIR/$remote_dir" > /dev/null 2>&1

        # Transfer file
        if scp -i "$SSH_KEY" "$file" "$SERVER_USER@$SERVER_HOST:$PROJECT_DIR/$file" > /dev/null 2>&1; then
            echo "  ✓ $file"
        else
            write_error "Failed to transfer $file"
            exit 1
        fi
    done

    write_success "Files transferred via SCP"
fi

# Step 4: Create virtual environment and install dependencies
write_status "\nStep 4: Setting up Python virtual environment..."
ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_HOST" "cd $PROJECT_DIR && python3 -m venv venv && source venv/bin/activate && pip install --upgrade pip setuptools wheel" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    write_success "Virtual environment created"
else
    write_error "Failed to create virtual environment"
    exit 1
fi

write_status "\nStep 4b: Installing Python dependencies..."
ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_HOST" "cd $PROJECT_DIR && source venv/bin/activate && pip install -r backend-setup/requirements.txt" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    write_success "Dependencies installed"
else
    write_error "Failed to install dependencies"
    exit 1
fi

# Step 5: Create database tables
write_status "\nStep 5: Creating database tables..."
ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_HOST" "cd $PROJECT_DIR && source venv/bin/activate && python3 << 'EOF'
import sys
sys.path.insert(0, '.')
try:
    from backend_setup.db.models import Base
    from backend_setup.db.connection import engine
    Base.metadata.create_all(engine)
    print('✅ Database tables created successfully')
except Exception as e:
    print(f'❌ Error creating tables: {e}')
    sys.exit(1)
EOF" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    write_success "Database tables created"
else
    write_error "Failed to create database tables"
    exit 1
fi

# Step 6: Run tests
write_status "\nStep 6: Running property-based tests..."
ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_HOST" "cd $PROJECT_DIR && source venv/bin/activate && python3 -m pytest backend-setup/tests/test_billing_service_properties.py -v --tb=short"
if [ $? -eq 0 ]; then
    write_success "Tests completed successfully"
else
    write_error "Tests failed - check output above"
    exit 1
fi

# Step 7: Verify deployment
write_status "\nStep 7: Verifying deployment..."
ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_HOST" "cd $PROJECT_DIR && source venv/bin/activate && python3 << 'EOF'
import sys
sys.path.insert(0, '.')
try:
    from backend_setup.services import BillingService, UsageService
    from backend_setup.db.models import Subscription, Usage, Invoice
    print('✅ Services imported successfully')
    print('✅ Models imported successfully')
    print('✅ Deployment verified!')
except Exception as e:
    print(f'❌ Error verifying deployment: {e}')
    sys.exit(1)
EOF" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    write_success "Deployment verified"
else
    write_error "Deployment verification failed"
    exit 1
fi

# Summary
echo ""
write_status "========================================"
write_success "Phase 1 Deployment Complete!"
write_status "========================================"
echo ""
echo "Deployed Components:"
echo "  ✅ BillingService"
echo "  ✅ UsageService"
echo "  ✅ Usage Database Model"
echo "  ✅ Property-Based Tests (20+ tests)"
echo ""
echo "Next Steps:"
echo "  1. Verify tests passed on server"
echo "  2. Begin Phase 2: Subscription Management"
echo "  3. Implement subscription status retrieval"
echo ""
echo "Documentation:"
echo "  - .kiro/BILLING_IMPLEMENTATION_ROADMAP.md"
echo "  - .kiro/DEPLOYMENT_CHECKLIST_BILLING.md"
echo "  - .kiro/QUICK_REFERENCE_BILLING.md"
echo ""
