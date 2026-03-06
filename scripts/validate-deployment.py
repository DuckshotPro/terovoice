#!/usr/bin/env python3
"""
AI Voice Agent Deployment Validation Script

This script validates that all components of the AI Voice Agent Powers ecosystem
are properly configured and ready for deployment.
"""

import os
import json
import sys
from pathlib import Path
import subprocess
import requests
from typing import Dict, List, Tuple

class DeploymentValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.success_count = 0
        self.total_checks = 0

    def log_success(self, message: str):
        print(f"✅ {message}")
        self.success_count += 1

    def log_warning(self, message: str):
        print(f"⚠️  {message}")
        self.warnings.append(message)

    def log_error(self, message: str):
        print(f"❌ {message}")
        self.errors.append(message)

    def check_environment_variables(self) -> bool:
        """Check that all required environment variables are set"""
        print("\n🔍 Checking Environment Variables...")
        self.total_checks += 1

        required_vars = [
            # PayPal Configuration
            'PAYPAL_CLIENT_ID',
            'PAYPAL_CLIENT_SECRET',
            'PAYPAL_ENVIRONMENT',

            # Twilio Configuration
            'TWILIO_ACCOUNT_SID',
            'TWILIO_AUTH_TOKEN',

            # Voice Processing
            'DEEPGRAM_API_KEY',
            'CARTESIA_API_KEY',
            'ELEVENLABS_API_KEY',

            # LiveKit
            'LIVEKIT_API_KEY',
            'LIVEKIT_API_SECRET',
            'LIVEKIT_URL',

            # Infrastructure
            'DATABASE_URL',
            'DOMAIN_BASE',
            'EMAIL_SMTP_HOST',
            'EMAIL_SMTP_USER',
            'EMAIL_SMTP_PASS'
        ]

        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            self.log_error(f"Missing environment variables: {', '.join(missing_vars)}")
            return False
        else:
            self.log_success("All required environment variables are set")
            return True

    def check_mcp_configuration(self) -> bool:
        """Validate MCP server configuration"""
        print("\n🔍 Checking MCP Configuration...")
        self.total_checks += 1

        mcp_config_path = Path('.kiro/settings/mcp.json')
        if not mcp_config_path.exists():
            self.log_error("MCP configuration file not found at .kiro/settings/mcp.json")
            return False

        try:
            with open(mcp_config_path) as f:
                config = json.load(f)

            required_servers = [
                'paypal',
                'twilio',
                'livekit',
                'ollama',
                'voice-processing',
                'client-onboarding',
                'analytics'
            ]

            missing_servers = []
            for server in required_servers:
                if server not in config.get('mcpServers', {}):
                    missing_servers.append(server)

            if missing_servers:
                self.log_error(f"Missing MCP servers: {', '.join(missing_servers)}")
                return False
            else:
                self.log_success("All required MCP servers are configured")
                return True

        except json.JSONDecodeError as e:
            self.log_error(f"Invalid JSON in MCP configuration: {e}")
            return False

    def check_power_files(self) -> bool:
        """Check that all power files are present and valid"""
        print("\n🔍 Checking Power Files...")
        self.total_checks += 1

        required_powers = [
            'paypal-ai-receptionist',
            'ai-voice-agent-manager',
            'twilio-telephony',
            'client-onboarding-automation',
            'analytics-monitoring'
        ]

        missing_powers = []
        for power in required_powers:
            power_dir = Path(f'powers/{power}')
            power_md = power_dir / 'POWER.md'
            mcp_json = power_dir / 'mcp.json'

            if not power_dir.exists():
                missing_powers.append(f"{power} (directory)")
            elif not power_md.exists():
                missing_powers.append(f"{power} (POWER.md)")
            elif not mcp_json.exists():
                missing_powers.append(f"{power} (mcp.json)")

        if missing_powers:
            self.log_error(f"Missing power files: {', '.join(missing_powers)}")
            return False
        else:
            self.log_success("All power files are present")
            return True

    def test_api_connections(self) -> bool:
        """Test connections to external APIs"""
        print("\n🔍 Testing API Connections...")
        self.total_checks += 1

        connection_tests = []

        # Test PayPal API
        paypal_client_id = os.getenv('PAYPAL_CLIENT_ID')
        paypal_env = os.getenv('PAYPAL_ENVIRONMENT', 'sandbox')
        if paypal_client_id:
            paypal_url = 'https://api.sandbox.paypal.com' if paypal_env == 'sandbox' else 'https://api.paypal.com'
            try:
                response = requests.get(f"{paypal_url}/v1/oauth2/token", timeout=10)
                if response.status_code in [200, 401]:  # 401 is expected without auth
                    connection_tests.append(("PayPal API", True))
                else:
                    connection_tests.append(("PayPal API", False))
            except Exception:
                connection_tests.append(("PayPal API", False))

        # Test Deepgram API
        deepgram_key = os.getenv('DEEPGRAM_API_KEY')
        if deepgram_key:
            try:
                headers = {'Authorization': f'Token {deepgram_key}'}
                response = requests.get('https://api.deepgram.com/v1/projects', headers=headers, timeout=10)
                connection_tests.append(("Deepgram API", response.status_code == 200))
            except Exception:
                connection_tests.append(("Deepgram API", False))

        # Test Ollama (if local)
        ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        try:
            response = requests.get(f"{ollama_url}/api/tags", timeout=5)
            connection_tests.append(("Ollama", response.status_code == 200))
        except Exception:
            connection_tests.append(("Ollama", False))

        # Report results
        failed_connections = [name for name, success in connection_tests if not success]
        if failed_connections:
            self.log_warning(f"Failed API connections: {', '.join(failed_connections)}")
            self.log_warning("Some services may not be available or configured yet")

        successful_connections = [name for name, success in connection_tests if success]
        if successful_connections:
            self.log_success(f"Successful API connections: {', '.join(successful_connections)}")

        return len(failed_connections) == 0

    def check_database_connection(self) -> bool:
        """Test database connectivity"""
        print("\n🔍 Checking Database Connection...")
        self.total_checks += 1

        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            self.log_warning("DATABASE_URL not set - database features will be unavailable")
            return False

        try:
            # Try to import psycopg2 and test connection
            import psycopg2
            conn = psycopg2.connect(database_url)
            conn.close()
            self.log_success("Database connection successful")
            return True
        except ImportError:
            self.log_warning("psycopg2 not installed - install with: pip install psycopg2-binary")
            return False
        except Exception as e:
            self.log_error(f"Database connection failed: {e}")
            return False

    def validate_deployment_readiness(self) -> bool:
        """Run comprehensive deployment validation"""
        print("🚀 AI Voice Agent Deployment Validation")
        print("=" * 50)

        # Run all validation checks
        checks = [
            self.check_environment_variables(),
            self.check_mcp_configuration(),
            self.check_power_files(),
            self.test_api_connections(),
            self.check_database_connection()
        ]

        # Print summary
        print("\n" + "=" * 50)
        print("📊 VALIDATION SUMMARY")
        print("=" * 50)

        print(f"✅ Successful checks: {self.success_count}/{self.total_checks}")

        if self.warnings:
            print(f"⚠️  Warnings: {len(self.warnings)}")
            for warning in self.warnings:
                print(f"   • {warning}")

        if self.errors:
            print(f"❌ Errors: {len(self.errors)}")
            for error in self.errors:
                print(f"   • {error}")

        # Determine overall status
        if self.errors:
            print("\n🔴 DEPLOYMENT NOT READY")
            print("Please fix the errors above before deploying.")
            return False
        elif self.warnings:
            print("\n🟡 DEPLOYMENT READY WITH WARNINGS")
            print("Deployment can proceed, but some features may be limited.")
            return True
        else:
            print("\n🟢 DEPLOYMENT READY")
            print("All systems validated and ready for production deployment!")
            return True

def main():
    """Main validation entry point"""
    validator = DeploymentValidator()

    # Load environment variables from .env file if it exists
    env_file = Path('.env')
    if env_file.exists():
        print("📁 Loading environment variables from .env file...")
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
    else:
        print("⚠️  No .env file found - using system environment variables only")

    # Run validation
    success = validator.validate_deployment_readiness()

    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()