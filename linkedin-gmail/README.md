# LinkedIn Gmail MCP Server

Read and manage LinkedIn emails from Gmail through the Model Context Protocol. Filter messages, job alerts, invitations, and notifications with AI assistance.

## 📋 Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Gmail API Setup](#gmail-api-setup)
- [Configuration](#configuration)
- [Usage](#usage)
- [Available Tools](#available-tools)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## ✨ Features

- Automatic LinkedIn email filtering
- Categorize by type (messages, jobs, invitations, notifications)
- Read full email content
- Search by date, status, and keywords
- OAuth2 secure authentication
- Read-only Gmail access
- Local credential storage

## 🚀 Installation

### Prerequisites

- Python 3.8+
- Gmail account
- Google Cloud Project (free tier)

### Quick Setup

```bash
# Navigate to linkedin-gmail directory
cd linkedin-gmail

# Create virtual environment
python -m venv mcp-gmail-env

# Activate virtual environment
# macOS/Linux:
source mcp-gmail-env/bin/activate
# Windows:
mcp-gmail-env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Dependencies (requirements.txt)

```txt
mcp>=0.1.0
google-auth-oauthlib>=1.0.0
google-auth-httplib2>=0.1.0
google-api-python-client>=2.0.0
```

## 🔐 Gmail API Setup

### Step 1: Create Google Cloud Project

1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Click **New Project**
3. Name: "LinkedIn Email Reader"
4. Click **Create**

### Step 2: Enable Gmail API

1. Go to **APIs & Services** → **Library**
2. Search "Gmail API"
3. Click **Enable**

### Step 3: Create OAuth Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. Configure consent screen:
   - User Type: **External**
   - App name: "LinkedIn Email Reader"
   - Add your email as test user
4. Create OAuth client:
   - Application type: **Desktop app**
   - Name: "LinkedIn Gmail MCP"
5. **Download JSON** file
6. Rename to `credentials.json`
7. Move to `linkedin-gmail/` directory

### Step 4: First Authentication

```bash
# Activate environment
source mcp-gmail-env/bin/activate

# Run server (browser will open)
python linked_gmail_mcp.py

# Log in and grant permissions
# Creates token.json for future use
```

## ⚙️ Configuration

### MCP Client Setup

Add to Claude Desktop config:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "linkedin-gmail": {
      "command": "/absolute/path/to/linkedin-gmail/mcp-gmail-env/bin/python",
      "args": ["/absolute/path/to/linkedin-gmail/linked_gmail_mcp.py"]
    }
  }
}
```

**Example (macOS):**
```json
{
  "mcpServers": {
    "linkedin-gmail": {
      "command": "/Users/john/mcp-server/linkedin-gmail/mcp-gmail-env/bin/python",
      "args": ["/Users/john/mcp-server/linkedin-gmail/linked_gmail_mcp.py"]
    }
  }
}
```

**Example (Windows):**
```json
{
  "mcpServers": {
    "linkedin-gmail": {
      "command": "C:\\Users\\john\\mcp-server\\linkedin-gmail\\mcp-gmail-env\\Scripts\\python.exe",
      "args": ["C:\\Users\\john\\mcp-server\\linkedin-gmail\\linked_gmail_mcp.py"]
    }
  }
}
```

⚠️ **Use absolute paths only!**

## 📖 Usage

### Natural Language Queries

Once configured, ask Claude about your LinkedIn emails:

```
"Show my recent LinkedIn messages"
"Do I have unread job alerts?"
"Read that invitation from Sarah"
"What LinkedIn emails arrived this week?"
"Find messages about software engineer positions"
```

### Supported LinkedIn Email Types

| Type | Sender | Description |
|------|--------|-------------|
| Messages | `messages-noreply@linkedin.com` | Direct messages |
| Invitations | `invitations@linkedin.com` | Connection requests |
| Jobs | `jobs-noreply@linkedin.com` | Job alerts |
| Notifications | `notifications@linkedin.com` | Activity updates |

## 🛠️ Available Tools

### 1. **list_linkedin_emails**
List LinkedIn emails with previews.

**Parameters:**
- `max_results` (number): Max emails to return (default: 10, max: 100)
- `query` (string): Gmail search query (optional)

**Example:**
```json
{
  "max_results": 20,
  "query": "is:unread after:2024/09/01"
}
```

**Returns:**
```json
[
  {
    "id": "18f2c3b4d5e6a7b8",
    "subject": "New message from John Smith",
    "from": "messages-noreply@linkedin.com",
    "date": "Mon, 30 Sep 2024 10:15:30 -0700",
    "snippet": "John: Hi, I saw your profile..."
  }
]
```

### 2. **get_linkedin_email**
Get full email content by ID.

**Parameters:**
- `message_id` (string): Gmail message ID

**Example:**
```json
{
  "message_id": "18f2c3b4d5e6a7b8"
}
```

**Returns:**
```json
{
  "id": "18f2c3b4d5e6a7b8",
  "subject": "New message from John Smith",
  "from": "messages-noreply@linkedin.com",
  "to": "you@gmail.com",
  "date": "Mon, 30 Sep 2024 10:15:30 -0700",
  "body": "Full email content..."
}
```

### 3. **search_linkedin_emails**
Search by email type and status.

**Parameters:**
- `email_type` (string): `messages`, `invitations`, `jobs`, `notifications`, or `all` (default: `all`)
- `max_results` (number): Max emails (default: 10)
- `include_read` (boolean): Include read emails (default: true)

**Example:**
```json
{
  "email_type": "jobs",
  "max_results": 15,
  "include_read": false
}
```

## 💡 Examples

### Check Unread Messages

```python
search_linkedin_emails(
    email_type="messages",
    include_read=False,
    max_results=10
)
```

### Find Recent Job Alerts

```python
list_linkedin_emails(
    max_results=20,
    query="from:jobs-noreply@linkedin.com after:2024/09/23"
)
```

### Read Invitation Details

```python
# Get invitations
invitations = search_linkedin_emails(
    email_type="invitations",
    max_results=5
)

# Read full content
email = get_linkedin_email(message_id=invitations[0]['id'])
```

### Advanced Gmail Queries

```python
# Unread from last 7 days
list_linkedin_emails(query="is:unread newer_than:7d")

# Starred emails
list_linkedin_emails(query="is:starred")

# Specific subject
list_linkedin_emails(query="subject:'software engineer'")

# Date range
list_linkedin_emails(query="after:2024/09/01 before:2024/09/30")

# Combined filters
list_linkedin_emails(query="is:unread after:2024/09/01 subject:invitation")
```

## 🔒 Security

### Authentication

- **OAuth 2.0** industry-standard authentication
- **Read-only access** to Gmail
- **Local storage** of credentials
- **No third-party data sharing**

### Credential Files

| File | Purpose | Security |
|------|---------|----------|
| `credentials.json` | OAuth client ID/secret | ⚠️ Never commit to git |
| `token.json` | Your access token | ⚠️ Never commit to git |

### Best Practices

```bash
# Verify .gitignore includes
credentials.json
token.json

# Set file permissions
chmod 600 credentials.json token.json

# Rotate tokens periodically
rm token.json  # Re-authenticate on next run

# Revoke access
# Visit: https://myaccount.google.com/permissions
```

## 🐛 Troubleshooting

### credentials.json not found

```bash
# Download from Google Cloud Console
# Move to linkedin-gmail directory
mv ~/Downloads/client_secret_*.json credentials.json
```

### Authentication Failed

```bash
# Delete token and re-authenticate
rm token.json
python linked_gmail_mcp.py
```

### Gmail API Not Enabled

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Gmail API in your project
3. Wait a few minutes for propagation

### Access Blocked Error

1. Add your email as test user in OAuth consent screen
2. Stay in "Testing" mode for personal use
3. Submit for verification if sharing publicly

### No LinkedIn Emails Found

Check that emails are from these senders:
- `messages-noreply@linkedin.com`
- `invitations@linkedin.com`
- `jobs-noreply@linkedin.com`
- `notifications@linkedin.com`

### Module Not Found

```bash
# Activate virtual environment
source mcp-gmail-env/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

## 📁 Project Structure

```
linkedin-gmail/
├── README.md                # This file
├── linked_gmail_mcp.py      # MCP server
├── requirements.txt         # Dependencies
├── credentials.json         # OAuth credentials (not in git)
├── token.json              # Access token (not in git)
└── mcp-gmail-env/          # Virtual environment (not in git)
```

## ❓ FAQ

**Q: Is this safe?**  
A: Yes. Uses official Gmail API with OAuth2. Read-only access. Credentials stay local.

**Q: Works with Google Workspace?**  
A: Yes. Select "Internal" user type in OAuth consent screen (requires admin).

**Q: Multiple Gmail accounts?**  
A: One account at a time. Delete `token.json` to switch accounts.

**Q: Does it download all emails?**  
A: No. Only fetches on request with specified limits.

**Q: Stop access?**  
A: Delete credential files and revoke at [Google Account Permissions](https://myaccount.google.com/permissions).

## 🎯 Advanced Tips

### Custom Sender Filters

Edit `LINKEDIN_SENDERS` in `linked_gmail_mcp.py`:

```python
LINKEDIN_SENDERS = [
    'messages-noreply@linkedin.com',
    'custom@linkedin.com',  # Add custom senders
]
```

### Batch Processing

```python
# Get all unread messages
messages = search_linkedin_emails(
    email_type="messages",
    include_read=False,
    max_results=100
)

# Process each
for msg in messages:
    email = get_linkedin_email(message_id=msg['id'])
    # Your processing logic
```

## 📚 Resources

- [MCP Documentation](https://modelcontextprotocol.io/docs)
- [Gmail API Guide](https://developers.google.com/gmail/api)
- [OAuth 2.0 Overview](https://developers.google.com/identity/protocols/oauth2)

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome!

1. Fork repository
2. Create feature branch
3. Submit pull request

## 🗺️ Roadmap

- [ ] Mark emails as read
- [ ] Archive functionality
- [ ] Content parsing (extract job details)
- [ ] Multi-account support
- [ ] Email analytics
- [ ] Custom notifications

---

**Made with ❤️ for better email management**

Need help? [Open an issue](https://github.com/YOUR_USERNAME/mcp-server/issues)