# Robutler Python SDK

[![PyPI version](https://badge.fury.io/py/robutler.svg)](https://badge.fury.io/py/robutler)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

The official Python client for the Robutler Platform provides comprehensive access to all backend services using a modern object-oriented design with hierarchical resources and typed model objects.

## Installation

```bash
pip install robutler
```

## Quick Start

```python
from robutler.api.client import RobutlerClient, RobutlerAPIError

# Modern object-oriented usage
async with RobutlerClient() as client:
    try:
        # Get user information - returns UserProfile object
        user = await client.user.get()
        print(f"Welcome {user.name} ({user.email})!")
        print(f"Plan: {user.plan_name}")
        print(f"Available credits: {user.available_credits}")
        
        # List agents - returns List[Agent]
        agents = await client.agents.list()
        for agent in agents:
            print(f"Agent: {agent.name} (Model: {agent.model})")
        
        # Get content files - returns List[ContentFile]
        content_files = await client.content.list()
        for file in content_files:
            print(f"File: {file.name} ({file.size_formatted})")
        
    except RobutlerAPIError as e:
        print(f"API Error: {e} (Status: {e.status_code})")
```

## Environment Configuration

Set your API key:

```bash
# Required: Your Robutler API key
export WEBAGENTS_API_KEY="your-api-key"
```

Get your `WEBAGENTS_API_KEY` at https://robutler.ai/developer

## API Reference

The client provides hierarchical access to all Robutler Platform services through intuitive resource objects. All methods return typed model objects for clean, IDE-friendly development.

### Main Client

::: robutler.api.client.RobutlerClient
    options:
      members:
        - __init__
        - agents
        - content
        - user
        - api_keys
        - tokens
        - intents
        - close
      show_root_heading: true
      show_source: false

### Resources

#### Agent Management

::: robutler.api.client.AgentsResource
    options:
      show_root_heading: true
      show_source: false

#### Content Management  

::: robutler.api.client.ContentResource
    options:
      show_root_heading: true
      show_source: false

#### User Management

::: robutler.api.client.UserResource
    options:
      show_root_heading: true
      show_source: false

### Model Objects

#### Agent

::: robutler.api.client.Agent
    options:
      show_root_heading: true
      show_source: false

#### Content File

::: robutler.api.client.ContentFile
    options:
      show_root_heading: true
      show_source: false

#### User Profile

::: robutler.api.client.UserProfile
    options:
      show_root_heading: true
      show_source: false

### Exceptions

::: robutler.api.client.RobutlerAPIError
    options:
      show_root_heading: true
      show_source: false

## Practical Examples

### User Account Management

```python
async def get_account_summary():
    """Get a complete account summary with user info, credits, and recent activity."""
    async with RobutlerClient() as client:
        # Get user profile (single call, typed object)
        user = await client.user.get()
        
        # Get current credit balance
        credits = await client.user.credits()
        
        # Get recent transaction history
        transactions = await client.user.transactions(limit=10)
        
        # Get API keys
        api_keys = await client.api_keys.list()
        
        return {
            "user": {
                "name": user.name,
                "email": user.email,
                "plan": user.plan_name,
                "credits": str(credits)
            },
            "recent_transactions": len(transactions),
            "api_keys": len(api_keys)
        }
```

### Agent Operations

```python
async def create_and_configure_agent():
    """Create a new agent and configure its settings."""
    async with RobutlerClient() as client:
        # Create new agent
        agent = await client.agents.create({
            "name": "data-analyst",
            "instructions": "You are a data analysis expert. Help users understand their data through clear visualizations and insights.",
            "model": "gpt-4o",
            "description": "Specialized in data analysis and visualization",
            "isPublic": True,
            "canTalkToOtherAgents": True
        })
        
        print(f"Created agent: {agent.name} (ID: {agent.id})")
        
        # Get the agent's API key for external integrations
        agent_resource = await client.agents.get(agent.id)
        api_key = await agent_resource.api_key()
        
        print(f"Agent API key: {api_key}")
        
        return agent
```

### Content and File Management

```python
async def manage_content_files():
    """Upload files and manage agent access to content."""
    async with RobutlerClient() as client:
        # Upload a public file that agents can access
        with open("dataset.csv", "rb") as f:
            public_file = await client.content.upload(
                file_data=f.read(),
                filename="dataset.csv",
                visibility="public"  # Agents can access this
            )
        
        # Upload a private file for user-only access
        with open("private_notes.txt", "rb") as f:
            private_file = await client.content.upload(
                file_data=f.read(),
                filename="private_notes.txt",
                visibility="private"  # User-only access
            )
        
        print(f"Public file: {public_file.name} ({public_file.size_formatted})")
        print(f"Private file: {private_file.name} ({private_file.size_formatted})")
        
        # Get all files accessible to agents
        agent_files = await client.content.agent_access()
        print(f"Agents can access {len(agent_files)} files:")
        for file in agent_files:
            print(f"  📄 {file.name} - {file.url}")
```

### Error Handling Best Practices

```python
async def robust_api_usage():
    """Demonstrate proper error handling with the Robutler client."""
    try:
        async with RobutlerClient() as client:
            # Attempt to get user information
            user = await client.user.get()
            print(f"Successfully authenticated as: {user.name}")
            
            # Attempt to list agents
            agents = await client.agents.list()
            print(f"Found {len(agents)} agents")
            
    except RobutlerAPIError as e:
        # Handle specific API errors
        if e.status_code == 401:
            print("Authentication failed - check your API key")
        elif e.status_code == 403:
            print("Access denied - insufficient permissions")
        elif e.status_code == 404:
            print("Resource not found")
        elif e.status_code >= 500:
            print("Server error - please try again later")
        else:
            print(f"API Error: {e} (Status: {e.status_code})")
            
        # Log detailed error information for debugging
        print(f"Error details: {e.response_data}")
        
    except Exception as e:
        # Handle unexpected errors
        print(f"Unexpected error: {e}")
```