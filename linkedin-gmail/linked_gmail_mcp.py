import asyncio
import json
import os
import base64
from typing import Any, Sequence
from datetime import datetime

from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from mcp.server.stdio import stdio_server

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# LinkedIn email addresses to filter
LINKEDIN_SENDERS = [
    'messages-noreply@linkedin.com',
    'invitations@linkedin.com',
    'notifications@linkedin.com',
    'jobs-noreply@linkedin.com',
    'recruiting@linkedin.com',
    'linkedin@linkedin.com'
]

class LinkedInGmailServer:
    def __init__(self):
        self.server = Server("linkedin-gmail-server")
        self.gmail_service = None
        self.setup_handlers()
        
    def get_gmail_service(self):
        """Authenticate and return Gmail API service."""
        if self.gmail_service:
            return self.gmail_service
            
        creds = None
        token_path = 'token.json'
        credentials_path = 'credentials.json'
        
        # Load existing credentials
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(credentials_path):
                    raise FileNotFoundError(
                        f"credentials.json not found. Please download it from Google Cloud Console."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        self.gmail_service = build('gmail', 'v1', credentials=creds)
        return self.gmail_service
    
    def setup_handlers(self):
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            return [
                Tool(
                    name="list_linkedin_emails",
                    description="List LinkedIn emails from Gmail. Returns subject, sender, date, and snippet for each email.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "max_results": {
                                "type": "number",
                                "description": "Maximum number of emails to return (default: 10, max: 100)",
                                "default": 10
                            },
                            "query": {
                                "type": "string",
                                "description": "Additional Gmail search query to filter results (e.g., 'is:unread', 'after:2024/01/01')",
                                "default": ""
                            }
                        }
                    }
                ),
                Tool(
                    name="get_linkedin_email",
                    description="Get full content of a specific LinkedIn email by message ID.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message_id": {
                                "type": "string",
                                "description": "The Gmail message ID of the email to retrieve"
                            }
                        },
                        "required": ["message_id"]
                    }
                ),
                Tool(
                    name="search_linkedin_emails",
                    description="Search LinkedIn emails with specific criteria (e.g., job alerts, messages, invitations).",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "email_type": {
                                "type": "string",
                                "enum": ["messages", "invitations", "jobs", "notifications", "all"],
                                "description": "Type of LinkedIn email to search for",
                                "default": "all"
                            },
                            "max_results": {
                                "type": "number",
                                "description": "Maximum number of emails to return (default: 10)",
                                "default": 10
                            },
                            "include_read": {
                                "type": "boolean",
                                "description": "Include read emails (default: true)",
                                "default": True
                            }
                        }
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
            try:
                service = self.get_gmail_service()
                
                if name == "list_linkedin_emails":
                    max_results = min(int(arguments.get("max_results", 10)), 100)
                    additional_query = arguments.get("query", "")
                    
                    # Build query to find LinkedIn emails
                    sender_query = " OR ".join([f"from:{sender}" for sender in LINKEDIN_SENDERS])
                    query = f"({sender_query})"
                    if additional_query:
                        query += f" {additional_query}"
                    
                    results = service.users().messages().list(
                        userId='me',
                        q=query,
                        maxResults=max_results
                    ).execute()
                    
                    messages = results.get('messages', [])
                    
                    if not messages:
                        return [TextContent(type="text", text="No LinkedIn emails found.")]
                    
                    email_list = []
                    for msg in messages:
                        msg_data = service.users().messages().get(
                            userId='me',
                            id=msg['id'],
                            format='metadata',
                            metadataHeaders=['From', 'Subject', 'Date']
                        ).execute()
                        
                        headers = {h['name']: h['value'] for h in msg_data['payload']['headers']}
                        
                        email_list.append({
                            'id': msg['id'],
                            'subject': headers.get('Subject', 'No Subject'),
                            'from': headers.get('From', 'Unknown'),
                            'date': headers.get('Date', 'Unknown'),
                            'snippet': msg_data.get('snippet', '')
                        })
                    
                    return [TextContent(
                        type="text",
                        text=json.dumps(email_list, indent=2)
                    )]
                
                elif name == "get_linkedin_email":
                    message_id = arguments.get("message_id")
                    
                    msg = service.users().messages().get(
                        userId='me',
                        id=message_id,
                        format='full'
                    ).execute()
                    
                    headers = {h['name']: h['value'] for h in msg['payload']['headers']}
                    
                    # Extract email body
                    body = self.get_email_body(msg['payload'])
                    
                    email_data = {
                        'id': msg['id'],
                        'subject': headers.get('Subject', 'No Subject'),
                        'from': headers.get('From', 'Unknown'),
                        'to': headers.get('To', 'Unknown'),
                        'date': headers.get('Date', 'Unknown'),
                        'body': body
                    }
                    
                    return [TextContent(
                        type="text",
                        text=json.dumps(email_data, indent=2)
                    )]
                
                elif name == "search_linkedin_emails":
                    email_type = arguments.get("email_type", "all")
                    max_results = min(int(arguments.get("max_results", 10)), 100)
                    include_read = arguments.get("include_read", True)
                    
                    # Map email types to specific senders
                    type_mapping = {
                        "messages": ["messages-noreply@linkedin.com"],
                        "invitations": ["invitations@linkedin.com"],
                        "jobs": ["jobs-noreply@linkedin.com"],
                        "notifications": ["notifications@linkedin.com"],
                        "all": LINKEDIN_SENDERS
                    }
                    
                    senders = type_mapping.get(email_type, LINKEDIN_SENDERS)
                    sender_query = " OR ".join([f"from:{sender}" for sender in senders])
                    query = f"({sender_query})"
                    
                    if not include_read:
                        query += " is:unread"
                    
                    results = service.users().messages().list(
                        userId='me',
                        q=query,
                        maxResults=max_results
                    ).execute()
                    
                    messages = results.get('messages', [])
                    
                    if not messages:
                        return [TextContent(
                            type="text",
                            text=f"No {email_type} LinkedIn emails found."
                        )]
                    
                    email_list = []
                    for msg in messages:
                        msg_data = service.users().messages().get(
                            userId='me',
                            id=msg['id'],
                            format='metadata',
                            metadataHeaders=['From', 'Subject', 'Date']
                        ).execute()
                        
                        headers = {h['name']: h['value'] for h in msg_data['payload']['headers']}
                        
                        email_list.append({
                            'id': msg['id'],
                            'subject': headers.get('Subject', 'No Subject'),
                            'from': headers.get('From', 'Unknown'),
                            'date': headers.get('Date', 'Unknown'),
                            'snippet': msg_data.get('snippet', '')
                        })
                    
                    return [TextContent(
                        type="text",
                        text=json.dumps(email_list, indent=2)
                    )]
                
                else:
                    return [TextContent(
                        type="text",
                        text=f"Unknown tool: {name}"
                    )]
                    
            except HttpError as error:
                return [TextContent(
                    type="text",
                    text=f"Gmail API error: {str(error)}"
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]
    
    def get_email_body(self, payload):
        """Extract email body from payload."""
        if 'body' in payload and 'data' in payload['body']:
            return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                elif part['mimeType'] == 'text/html':
                    if 'data' in part['body']:
                        return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                elif 'parts' in part:
                    # Recursive call for nested parts
                    body = self.get_email_body(part)
                    if body:
                        return body
        
        return "No body content found"
    
    async def run(self):
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )

async def main():
    server = LinkedInGmailServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())