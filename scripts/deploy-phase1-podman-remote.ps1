# Phase 1 Deployment Script for Podman (Remote Build)
# Transfers Dockerfile and code, builds on server
# Usage: .\scripts\deploy-phase1-podman-remote.ps1 -ServerHost "74.208.227.161" -ServerUser "cira"

param(
    [string]$ServerHost = "74.208.227.161",
    [string]$ServerUser = "cira",
    [string]$SSHKey = ".kiro/private-keys/id_kiro",
    [string]$ImageName = "billing-service",
    [string]$ImageTag = "phase1"
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
Write-Status "Phase 1: Billing Service - Remote Podman Build"
Write-Status "========================================"

# Step 1: Verify files exist
Write-Status "`nStep 1: Verifying files..."
$filesToCheck = @(
    "Dockerfile.billing-phase1",
    "backend-setup/services/billing_service.py",
    "backend-setup/services/usage_service.py",
    "backend-setup/db/models.py",
    "backend-setup/tests/test_billing_service_properties.py",
    "backend-setup/requirements.txt"
)

foreach ($file in $filesToCheck) {
    if (-not (Test-Path $file)) {
        Write-Error-Custom "File not found: $file"
        exit 1
    }
}
Write-Success "All files verified"

# Step 1.5: Verify requirements.txt has compatible versions
Write-Status "`nStep 1.5: Verifying requirements.txt has compatible versions..."
$reqContent = Get-Content backend-setup/requirements.txt -Raw
if ($reqContent -match "livekit-agents==0\.9\.0|livekit-plugins-deepgram==0\.9\.0") {
    Write-Error-Custom "requirements.txt has outdated versions!"
    Write-Error-Custom "  Found: livekit-agents==0.9.0 or livekit-plugins-deepgram==0.9.0"
    Write-Error-Custom "  These versions don't exist on PyPI"
    Write-Error-Custom "  Please update requirements.txt with compatible versions (>=0.15.0, >=1.4.0)"
    exit 1
}
Write-Success "requirements.txt has compatible versions"

# Step 2: Create project directory on server
Write-Status "`nStep 2: Creating project directory on server..."
ssh -o ConnectTimeout=5 -i $SSHKey "$ServerUser@$ServerHost" "mkdir -p /home/$ServerUser/ai-phone-sas/backend-setup/{services,db,tests} /home/$ServerUser/ai-phone-sas/data /home/$ServerUser/ai-phone-sas/logs"
if ($LASTEXITCODE -eq 0) {
    Write-Success "Project directory created"
} else {
    Write-Error-Custom "Failed to create project directory"
    exit 1
}

# Step 3: Transfer Dockerfile
Write-Status "`nStep 3: Transferring Dockerfile..."
$remoteTarget = "$ServerUser@$ServerHost`:/home/$ServerUser/ai-phone-sas/"
scp -i $SSHKey Dockerfile.billing-phase1 "$remoteTarget"
if ($LASTEXITCODE -eq 0) {
    Write-Success "Dockerfile transferred"
} else {
    Write-Error-Custom "Failed to transfer Dockerfile"
    exit 1
}

# Rename Dockerfile on server
ssh -o ConnectTimeout=5 -i $SSHKey "$ServerUser@$ServerHost" "cd /home/$ServerUser/ai-phone-sas && mv Dockerfile.billing-phase1 Dockerfile"
if ($LASTEXITCODE -eq 0) {
    Write-Success "Dockerfile renamed"
} else {
    Write-Error-Custom "Failed to rename Dockerfile"
    exit 1
}

# Step 4: Transfer backend code
Write-Status "`nStep 4: Transferring backend code..."
$filesToTransfer = @(
    "backend-setup/services/billing_service.py",
    "backend-setup/services/usage_service.py",
    "backend-setup/services/__init__.py",
    "backend-setup/db/models.py",
    "backend-setup/tests/test_billing_service_properties.py",
    "backend-setup/tests/__init__.py",
    "backend-setup/requirements.txt"
)

foreach ($file in $filesToTransfer) {
    $remoteDir = Split-Path -Path $file
    $remoteDir = $remoteDir -replace "\\", "/"
    scp -i $SSHKey $file "$ServerUser@$ServerHost`:/home/$ServerUser/ai-phone-sas/$file" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Error-Custom "Failed to transfer $file"
        exit 1
    }
}
Write-Success "All code transferred"

# Step 5: Build image on server
Write-Status "`nStep 5: Building image on server..."
Write-Status "This may take 2-3 minutes..."
ssh -i $SSHKey "$ServerUser@$ServerHost" @"
cd /home/$ServerUser/ai-phone-sas
podman build -f Dockerfile.billing-phase1 -t ${ImageName}:${ImageTag} .
"@
if ($LASTEXITCODE -eq 0) {
    Write-Success "Image built successfully"
} else {
    Write-Error-Custom "Failed to build image"
    exit 1
}

# Step 6: Run tests in container
Write-Status "`nStep 6: Running tests in container..."
ssh -i $SSHKey "$ServerUser@$ServerHost" @"
podman run --rm \
  -v /home/$ServerUser/ai-phone-sas/data:/app/data \
  -v /home/$ServerUser/ai-phone-sas/logs:/app/logs \
  -e PYTHONUNBUFFERED=1 \
  ${ImageName}:${ImageTag}
"@
if ($LASTEXITCODE -eq 0) {
    Write-Success "Tests completed successfully"
} else {
    Write-Error-Custom "Tests failed"
    exit 1
}

# Step 7: Verify deployment
Write-Status "`nStep 7: Verifying deployment..."
ssh -i $SSHKey "$ServerUser@$ServerHost" @"
podman run --rm \
  -v /home/$ServerUser/ai-phone-sas/data:/app/data \
  ${ImageName}:${ImageTag} \
  python3 -c "
import sys
sys.path.insert(0, '.')
from backend_setup.services import BillingService, UsageService
from backend_setup.db.models import Subscription, Usage, Invoice
print('✅ Services imported successfully')
print('✅ Models imported successfully')
print('✅ Deployment verified!')
"
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
Write-Success "Phase 1 Podman Deployment Complete!"
Write-Status "========================================"
Write-Host ""
Write-Host "Deployed Components:"
Write-Host "  ✅ BillingService"
Write-Host "  ✅ UsageService"
Write-Host "  ✅ Usage Database Model"
Write-Host "  ✅ Property-Based Tests (20+ tests)"
Write-Host ""
Write-Host "Container Details:"
Write-Host "  Image: ${ImageName}:${ImageTag}"
Write-Host "  Server: $ServerUser@$ServerHost"
Write-Host "  Project Dir: /home/$ServerUser/ai-phone-sas"
Write-Host "  Data Volume: /home/$ServerUser/ai-phone-sas/data"
Write-Host "  Logs Volume: /home/$ServerUser/ai-phone-sas/logs"
Write-Host ""
Write-Host "Next Steps:"
Write-Host "  1. Verify tests passed above"
Write-Host "  2. Begin Phase 2: Subscription Management"
Write-Host "  3. Implement subscription status retrieval"
Write-Host ""
Write-Host "Useful Commands:"
Write-Host "  # View images on server"
Write-Host "  ssh -i $SSHKey $ServerUser@$ServerHost 'podman images'"
Write-Host ""
Write-Host "  # Run container interactively"
Write-Host "  ssh -i $SSHKey $ServerUser@$ServerHost 'podman run -it --rm -v /home/$ServerUser/ai-phone-sas/data:/app/data ${ImageName}:${ImageTag} bash'"
Write-Host ""
Write-Host "  # View container logs"
Write-Host "  ssh -i $SSHKey $ServerUser@$ServerHost 'podman logs billing-service'"
Write-Host ""
Write-Host "Documentation:"
Write-Host "  - .kiro/PODMAN_DEPLOYMENT_STRATEGY.md"
Write-Host "  - .kiro/BILLING_IMPLEMENTATION_ROADMAP.md"
Write-Host ""
