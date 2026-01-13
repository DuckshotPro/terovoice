---
name: "ssh-remote-execution"
displayName: "SSH Remote Execution"
description: "Execute commands and manage files on remote servers via SSH. Connect to your VPS, run deployments, manage databases, and transfer files securely."
keywords: ["ssh", "remote", "vps", "deployment", "server", "command-execution"]
author: "Your Team"
---

# SSH Remote Execution

## Overview

This power enables secure remote command execution and file management on your VPS and other remote servers. Execute shell commands, manage files, and automate deployment tasks directly from Kiro without leaving your development environment.

**Key capabilities:**
- Execute commands on remote servers
- Read and write files remotely
- List and navigate remote directories
- Manage deployments and server operations
- Automate multi-step server tasks

## Onboarding

### Prerequisites

Before using this power, ensure you have:
- SSH access to your remote server (VPS, cloud instance, etc.)
- SSH key pair (private key on your local machine)
- Server hostname or IP address
- SSH username for the server
- Network connectivity to the server

### Configuration

This power connects to your remote server using SSH key authentication. You'll need to configure:

1. **SSH_HOST** - Your server's hostname or IP address
   - Example: `74.208.227.161` 

2. **SSH_USER** - The username to connect with
   -  `root`

3. **SSH_KEY_PATH** - Path to your SSH private key
   - Example: `./id_kiro` or `/home/user/.ssh/id_rsa`
   - **Important:** Keep this key secure and never commit to version control

### MCP Config Placeholders

**IMPORTANT:** Before using this power, replace the following placeholders in `mcp.json` with your actual values:

- **`74.208.227.161`**: Your remote server's IP address or hostname.
  - **How to get it:** Check your VPS provider's dashboard or use `ping your-server.com` to find the IP

- **`cira`**: The SSH username for your server.
  - **How to get it:** Check your VPS provider's documentation or SSH config file

- **`./id_kiro`**: Path to your SSH private key file.
  - **How to set it:** 
    1. Ensure your SSH key is in your project or home directory
    2. Use the relative path from your workspace (e.g., `./id_kiro`)
    3. Or use absolute path (e.g., `/Users/yourname/.ssh/id_rsa`)
    4. **Security:** Never commit private keys to version control

### Verify Connection

To verify your SSH connection is working:

```bash
# Test SSH connection (this will be done automatically when power loads)
ssh -i ./id_kiro cira@74.208.227.161 "echo 'SSH connection successful'"
```

If successful, you'll see: `SSH connection successful`

## Common Workflows

### Workflow 1: Execute Remote Commands

**Goal:** Run commands on your remote server

**Steps:**
1. Use the `execute_command` tool with your command
2. Specify the command to run on the remote server
3. View the output and any errors

**Example:**
```bash
# Check server uptime
execute_command: uptime

# Check disk usage
execute_command: df -h

# View running processes
execute_command: ps aux | grep node

# Restart a service
execute_command: sudo systemctl restart nginx
```

**Common commands:**
- `uptime` - Server uptime and load average
- `df -h` - Disk space usage
- `free -h` - Memory usage
- `ps aux` - Running processes
- `systemctl status {service}` - Service status
- `tail -f /var/log/syslog` - View system logs

### Workflow 2: Read Remote Files

**Goal:** View contents of files on your remote server

**Steps:**
1. Use the `read_file` tool
2. Provide the full path to the file
3. View the file contents

**Example:**
```bash
# Read application configuration
read_file: /app/config/settings.json

# Check environment variables
read_file: /app/.env

# View application logs
read_file: /var/log/app.log

# Check nginx configuration
read_file: /etc/nginx/nginx.conf
```

**Common files to read:**
- Application config files
- Log files for debugging
- Environment configuration
- System configuration files

### Workflow 3: Write Remote Files

**Goal:** Create or update files on your remote server

**Steps:**
1. Use the `write_file` tool
2. Provide the file path and content
3. File is created or updated on the remote server

**Example:**
```bash
# Create a deployment script
write_file: /app/deploy.sh
#!/bin/bash
cd /app
git pull origin main
npm install
npm run build
systemctl restart app

# Update environment configuration
write_file: /app/.env
DATABASE_URL=postgresql://user:pass@localhost/db
API_KEY=your-api-key
NODE_ENV=production
```

### Workflow 4: List Remote Directories

**Goal:** Navigate and explore remote file system

**Steps:**
1. Use the `list_directory` tool
2. Provide the directory path
3. View files and subdirectories

**Example:**
```bash
# List home directory
list_directory: /home/cira

# List application directory
list_directory: /app

# List logs directory
list_directory: /var/log

# List with details
list_directory: /app -la
```

### Workflow 5: Deploy Application

**Goal:** Deploy your application to the remote server

**Steps:**
1. Connect to the server
2. Navigate to application directory
3. Pull latest code
4. Install dependencies
5. Build application
6. Restart service

**Example deployment sequence:**
```bash
# 1. Navigate to app directory
execute_command: cd /app

# 2. Pull latest code from git
execute_command: git pull origin main

# 3. Install dependencies
execute_command: npm install

# 4. Build application
execute_command: npm run build

# 5. Restart the application service
execute_command: sudo systemctl restart app

# 6. Verify deployment
execute_command: systemctl status app
```

## Troubleshooting

### Connection Issues

**Problem:** "Permission denied (publickey)"
**Cause:** SSH key authentication failed
**Solution:**
1. Verify SSH key path is correct in mcp.json
2. Check key permissions: `ls -la ~/.ssh/id_rsa` (should be 600)
3. Verify key is added to server's authorized_keys
4. Test connection manually: `ssh -i ./id_kiro cira@74.208.227.161`

**Problem:** "Connection refused"
**Cause:** Server not reachable or SSH service not running
**Solution:**
1. Verify server IP/hostname is correct
2. Check network connectivity: `ping 74.208.227.161`
3. Verify SSH port is open (default 22)
4. Check server is running and SSH service is active

**Problem:** "Host key verification failed"
**Cause:** Server's host key not in known_hosts
**Solution:**
1. Accept the host key on first connection
2. Or manually add: `ssh-keyscan -H 74.208.227.161 >> ~/.ssh/known_hosts`

### Command Execution Issues

**Problem:** "Command not found"
**Cause:** Command doesn't exist on remote server
**Solution:**
1. Verify command is installed on server
2. Use full path to command if needed
3. Check PATH environment variable on server

**Problem:** "Permission denied"
**Cause:** User doesn't have permission to execute command
**Solution:**
1. Use `sudo` if command requires elevated privileges
2. Verify user is in correct group (e.g., docker group)
3. Check file/directory permissions

**Problem:** "Timeout"
**Cause:** Command taking too long or server unresponsive
**Solution:**
1. Check server load: `execute_command: uptime`
2. Check network connectivity
3. Try simpler command first to verify connection
4. Increase timeout if needed

### File Operations Issues

**Problem:** "File not found"
**Cause:** File path is incorrect or file doesn't exist
**Solution:**
1. Verify file path: `list_directory: /path/to/directory`
2. Check file exists: `execute_command: ls -la /path/to/file`
3. Use absolute paths instead of relative paths

**Problem:** "Permission denied" when reading/writing files
**Cause:** User doesn't have read/write permissions
**Solution:**
1. Check file permissions: `execute_command: ls -la /path/to/file`
2. Change permissions if needed: `execute_command: chmod 644 /path/to/file`
3. Use sudo if necessary: `execute_command: sudo cat /path/to/file`

## Best Practices

- **Use SSH keys, not passwords** - More secure and enables automation
- **Keep private keys secure** - Never commit to version control, use .gitignore
- **Use specific commands** - Avoid wildcards in automated scripts
- **Check before destructive operations** - Always verify before deleting or overwriting
- **Log important operations** - Keep audit trail of deployments and changes
- **Use sudo carefully** - Only when necessary, consider sudoers configuration
- **Monitor server health** - Regularly check uptime, disk space, and resource usage
- **Backup before major changes** - Always have a rollback plan
- **Use version control** - Keep deployment scripts in git for tracking changes
- **Test in staging first** - Deploy to staging environment before production

## Security Considerations

### SSH Key Management
- Store private keys outside version control
- Use strong passphrases for keys
- Rotate keys periodically
- Restrict key file permissions (600)
- Use different keys for different servers

### Access Control
- Use specific SSH users with minimal privileges
- Implement sudo rules for necessary commands
- Disable root login via SSH
- Use SSH config for host-specific settings
- Monitor SSH access logs

### Network Security
- Use VPN or bastion host for sensitive servers
- Restrict SSH access by IP address
- Use non-standard SSH ports if possible
- Enable SSH key-only authentication
- Disable password authentication

## Configuration

**Environment Variables in mcp.json:**

```json
{
  "mcpServers": {
    "ssh": {
      "command": "uvx",
      "args": ["mcp-server-ssh@latest"],
      "env": {
        "SSH_HOST": "74.208.227.161",
        "SSH_USER": "cira",
        "SSH_KEY_PATH": "./id_kiro"
      }
    }
  }
}
```

**Variable Descriptions:**
- `SSH_HOST` - Remote server hostname or IP address
- `SSH_USER` - Username for SSH authentication
- `SSH_KEY_PATH` - Path to SSH private key file

---

**MCP Server:** SSH Remote Execution
**Tools:** execute_command, read_file, write_file, list_directory
