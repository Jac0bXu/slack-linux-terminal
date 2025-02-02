# Slack Linux Terminal

A remote terminal access solution that allows you to control a Linux machine through Slack messages. This tool is particularly useful for:
- Remote server management when SSH access is blocked or unavailable
- Quick system checks without needing to log in via SSH
- Team collaboration on system administration tasks
- Emergency access when traditional remote access methods fail

Features
- Execute any Linux terminal command through Slack messages
- Real terminal-like experience with username@hostname:path$ formatting
- Directory navigation support (cd command maintains state)
- Command output formatted in code blocks for readability
- Built-in 15-second timeout protection against hanging commands
- Logs all commands and their outputs for accountability

Prerequisites
- Python 3.6+
- Slack workspace with admin privileges
- Slack Bot Token with appropriate permissions
- A dedicated private Slack channel for security

Installation
1. Clone the repository
2. Install dependencies: pip install -r requirements.txt
3. Create a .env file with:
   SLACK_BOT_TOKEN=xoxb-your-token
   SLACK_APP_TOKEN=xapp-your-token
   TARGET_CHANNEL_ID=your-channel-id

Slack Setup
1. Create a Slack App at api.slack.com/apps
2. Enable Socket Mode
3. Add Bot Token Scopes:
   - chat:write
   - channels:history
   - users:read
4. Install app to workspace
5. Add bot to your target channel

Usage
Run manually:
python3 slackLinuxTerminal.py

Auto-start after reboot (using crontab):
@reboot sleep 60 && /usr/bin/python3 /path/to/slackLinuxTerminal.py >> /path/to/slackLinuxTerminal.log 2>&1

Security Considerations
- Only use in private, trusted channels
- Run as regular user, not root
- Commands execute with script user's permissions
- All commands are logged for security auditing
- 15-second timeout prevents resource-intensive operations
- Channel restriction prevents unauthorized access

License
MIT License