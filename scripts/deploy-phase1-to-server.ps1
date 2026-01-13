# Phase 1 Deployment Script for AI Phone SaaS (PowerShell)
# Deploys billing service infrastructure to the server
# Usage: .\scripts\deploy-phase1-to-server.ps1 -ServerHost "74.208.227.161" -ServerUser "cira" -ProjectDir "/home/cira/ai-phone-sas"

param(
    [string]$ServerHost = "74.208.227.161",
    [string]$ServerUser = "cira",
    [string]$ProjectDir = "/home/cira/ai-phone-sas",
    [string]$SSHKey = ".kiro/private-keys/id_kiro",
    [switch]$SkipGitPush = $false
)

# Colors
$Green = "Green"
$Blue = "Cyan"
$Red = "Red"

function Write-Status {
    param([string]$Message, [string]$Color = $Blue)
    Write-Host $Message -ForegroundColor $Color
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor $Green
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor $Red
}

# Header
Write-Host ""
Write-Status "========================================"
Write-Status "Phase 1: Billing Service Deployment"
Write-Status "========================================"

# Step 1: Verify SSH key exists
Write-Status "`nStep 1: Verifying SSH key..."
if (-not (Test-Path $SSHKey)) {
    Write-Error-Custom "SSH key not found at $SSHKey"
    exit 1
}
Write-Success "SSH key found"

# Step 2: Test SSH connection
Write-Status "`nStep 2: Testing SSH connection..."
try {
    $testConnection = ssh -i $SSHKey -o ConnectTimeout=5 "$ServerUser@$ServerHost" "echo 'SSH connection successful'" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Success "SSH connection successful"
    } else {
        throw "SSH connection failed"
    }
} catch {
    Write-Error-Custom "SSH connection failed"
    Write-Host "Make sure:"
    Write-Host "  1. Server is running"
    Write-Host "  2. SSH key is correct"
    Write-Host "  3. Server hostname/IP is correct: $ServerHost"
    exit 1
}

# Step 3: Push code to server
Write-Status "`nStep 3: Pushing code to server..."
if ($SkipGitPush) {
    Write-Status "Skipping git push (using direct SCP transfer instead)"
} else {
    Write-Status "Attempting git push to repository..."
    git push origin main 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Status "Git push failed - will use direct SCP transfer instead"
        $SkipGitPush = $true
    } else {
        Write-Success "Code pushed to repository"
    }
}

# Step 3b: If git push failed, use SCP to transfer files directly
if ($SkipGitPush) {
    Write-Status "`nStep 3b: Transferring files via SCP..."
    
    # Create list of files to transfer
    $filesToTransfer = @(
        "backend-setup/services/billing_service.py",
        "backend-setup/services/usage_service.py",
        "backend-setup/services/__init__.py",
        "backend-setup/db/models.py",
        "backend-setup/tests/test_billing_service_properties.py",
        "backend-setup/tests/__init__.py",
        "backend-setup/requirements.txt"
    )
    
    # Transfer each file
    foreach ($file in $filesToTransfer) {
        $remoteDir = Split-Path -Path $file
        $remoteDir = $remoteDir -replace "\\", "/"
        
        # Create remote directory
        ssh -i $SSHKey "$ServerUser@$ServerHost" "mkdir -p $ProjectDir/$remoteDir" 2>&1 | Out-Null
        
        # Transfer file
        scp -i $SSHKey $file "$ServerUser@$ServerHost`:$ProjectDir/$file" 2>&1 | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ $file" -ForegroundColor Green
        } else {
            Write-Error-Custom "Failed to transfer $file"
            exit 1
        }
    }
    
    Write-Success "Files transferred via SCP"
}

# Step 4: Install dependencies
Write-Status "`nStep 4: Setting up Python virtual environment..."
ssh -i $SSHKey "$ServerUser@$ServerHost" "cd $ProjectDir && python3 -m venv venv && source venv/bin/activate && pip install --upgrade pip setuptools wheel"
if ($LASTEXITCODE -eq 0) {
    Write-Success "Virtual environment created"
} else {
    Write-Error-Custom "Failed to create virtual environment"
    exit 1
}

Write-Status "`nStep 4b: Installing Python dependencies..."
ssh -i $SSHKey "$ServerUser@$ServerHost" "cd $ProjectDir && source venv/bin/activate && pip install -r backend-setup/requirements.txt"
if ($LASTEXITCODE -eq 0) {
    Write-Success "Dependencies installed"
} else {
    Write-Error-Custom "Failed to install dependencies"
    exit 1
}

# Step 6: Create database tables
Write-Status "`nStep 6: Creating database tables..."
ssh -i $SSHKey "$ServerUser@$ServerHost" @"
cd $ProjectDir && source venv/bin/activate && python3 << 'EOF'
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
EOF
"@
if ($LASTEXITCODE -eq 0) {
    Write-Success "Database tables created"
} else {
    Write-Error-Custom "Failed to create database tables"
    exit 1
}

# Step 7: Run tests
Write-Status "`nStep 7: Running property-based tests..."
ssh -i $SSHKey "$ServerUser@$ServerHost" "cd $ProjectDir && source venv/bin/activate && python3 -m pytest backend-setup/tests/test_billing_service_properties.py -v --tb=short"
if ($LASTEXITCODE -eq 0) {
    Write-Success "Tests completed successfully"
} else {
    Write-Error-Custom "Tests failed - check output above"
    exit 1
}

# Step 8: Verify deployment
Write-Status "`nStep 8: Verifying deployment..."
ssh -i $SSHKey "$ServerUser@$ServerHost" @"
cd $ProjectDir && source venv/bin/activate && python3 << 'EOF'
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
EOF
"@
if ($LASTEXITCODE -eq 0) {
    Write-Success "Deployment verified"
} else {
    Write-Error-Custom "Deployment verification failed"
    exit 1
}

# Summary
Write-Host ""
Write-Status "========================================"
Write-Success "Phase 1 Deployment Complete!"
Write-Status "========================================"
Write-Host ""
Write-Host "Deployed Components:"
Write-Host "  ✅ BillingService"
Write-Host "  ✅ UsageService"
Write-Host "  ✅ Usage Database Model"
Write-Host "  ✅ Property-Based Tests (20+ tests)"
Write-Host ""
Write-Host "Next Steps:"
Write-Host "  1. Verify tests passed on server"
Write-Host "  2. Begin Phase 2: Subscription Management"
Write-Host "  3. Implement subscription status retrieval"
Write-Host ""
Write-Host "Documentation:"
Write-Host "  - .kiro/BILLING_IMPLEMENTATION_ROADMAP.md"
Write-Host "  - .kiro/DEPLOYMENT_CHECKLIST_BILLING.md"
Write-Host "  - .kiro/QUICK_REFERENCE_BILLING.md"
Write-Host ""
