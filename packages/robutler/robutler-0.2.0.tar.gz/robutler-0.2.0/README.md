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
# Required: Your Robutler Webagents API key
export WEBAGENTS_API_KEY="your-api-key"
```

Get your `WEBAGENTS_API_KEY` at https://robutler.ai/developer
