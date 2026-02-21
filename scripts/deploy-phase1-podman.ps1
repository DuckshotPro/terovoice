# Phase 1 Deployment Script for Podman (PowerShell)
# Builds container image and deploys to Podman server
# Usage: .\scripts\deploy-phase1-podman.ps1 -ServerHost "74.208.227.161" -ServerUser "password"

param(
    [string]$ServerHost = "74.208.227.161",
    [string]$ServerUser = "password",
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
Write-Status "Phase 1: Billing Service - Podman Deployment"
Write-Status "========================================"

# Step 1: Verify Dockerfile exists
Write-Status "`nStep 1: Verifying Dockerfile..."
if (-not (Test-Path "Dockerfile.billing-phase1")) {
    Write-Error-Custom "Dockerfile.billing-phase1 not found"
    exit 1
}
Write-Success "Dockerfile found"

# Step 2: Build image locally
Write-Status "`nStep 2: Building Podman image locally..."
Write-Status "This may take 2-3 minutes..."
podman build -f Dockerfile.billing-phase1 -t "${ImageName}:${ImageTag}" .
if ($LASTEXITCODE -eq 0) {
    Write-Success "Image built successfully"
} else {
    Write-Error-Custom "Failed to build image"
    exit 1
}

# Step 3: Verify image
Write-Status "`nStep 3: Verifying image..."
$imageExists = podman images | Select-String "${ImageName}.*${ImageTag}"
if ($imageExists) {
    Write-Success "Image verified"
} else {
    Write-Error-Custom "Image verification failed"
    exit 1
}

# Step 4: Save image as tar
Write-Status "`nStep 4: Saving image as tar file..."
$tarFile = "billing-service-phase1.tar"
podman save "${ImageName}:${ImageTag}" -o $tarFile
if ($LASTEXITCODE -eq 0) {
    Write-Success "Image saved to $tarFile"
} else {
    Write-Error-Custom "Failed to save image"
    exit 1
}

# Step 5: Verify SSH connection
Write-Status "`nStep 5: Testing SSH connection..."
if (-not (Test-Path $SSHKey)) {
    Write-Error-Custom "SSH key not found at $SSHKey"
    exit 1
}

ssh -o ConnectTimeout=5 -i $SSHKey "$ServerUser@$ServerHost" "podman --version" | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Success "SSH connection successful and Podman available"
} else {
    Write-Error-Custom "SSH connection failed or Podman not available"
    exit 1
}

# Step 6: Transfer image to server
Write-Status "`nStep 6: Transferring image to server..."
Write-Status "This may take 1-2 minutes depending on image size..."
$remoteTarget = "$ServerUser@$ServerHost`:/home/$ServerUser/"
scp -i $SSHKey $tarFile $remoteTarget
if ($LASTEXITCODE -eq 0) {
    Write-Success "Image transferred to server"
} else {
    Write-Error-Custom "Failed to transfer image"
    exit 1
}

# Step 7: Load image on server
Write-Status "`nStep 7: Loading image on server..."
ssh -i $SSHKey "$ServerUser@$ServerHost" @"
cd /home/$ServerUser
podman load -i $tarFile
if [ `$? -eq 0 ]; then
    echo "✅ Image loaded successfully"
else
    echo "❌ Failed to load image"
    exit 1
fi
"@
if ($LASTEXITCODE -eq 0) {
    Write-Success "Image loaded on server"
} else {
    Write-Error-Custom "Failed to load image on server"
    exit 1
}

# Step 8: Create project directory
Write-Status "`nStep 8: Creating project directory on server..."
ssh -i $SSHKey "$ServerUser@$ServerHost" "mkdir -p /home/$ServerUser/ai-phone-sas/data /home/$ServerUser/ai-phone-sas/logs"
if ($LASTEXITCODE -eq 0) {
    Write-Success "Project directory created"
} else {
    Write-Error-Custom "Failed to create project directory"
    exit 1
}

# Step 9: Run tests in container
Write-Status "`nStep 9: Running tests in container..."
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

# Step 10: Verify deployment
Write-Status "`nStep 10: Verifying deployment..."
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

# Step 11: Cleanup local tar file
Write-Status "`nStep 11: Cleaning up local files..."
Remove-Item $tarFile -Force
Write-Success "Local tar file removed"

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
Write-Host "  Data Volume: /home/$ServerUser/ai-phone-sas/data"
Write-Host "  Logs Volume: /home/$ServerUser/ai-phone-sas/logs"
Write-Host ""
Write-Host "Next Steps:"
Write-Host "  1. Verify tests passed above"
Write-Host "  2. Set up systemd service for persistence (optional)"
Write-Host "  3. Begin Phase 2: Subscription Management"
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
