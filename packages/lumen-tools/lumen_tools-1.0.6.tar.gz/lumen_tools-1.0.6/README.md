# Lumen Core Python Client

A Python client library for Google services (Gmail, Calendar, Drive, Docs, more coming soon) with AI assistants through the Lumen platform. Build intelligent workflows with OAuth provider management, real-time webhooks, and OpenAI-compatible tool schemas.

## Installation

```bash
pip install lumen-tooling
```

## Quick Start

```python
import asyncio
from lumen_tools import LumenClient, ProviderCredentials

async def main():
    # Initialize the client
    client = LumenClient(api_key="your-api-key")

    # Create provider credentials
    google_credentials = ProviderCredentials(
        client_id="your-google-client-id",
        client_secret="your-google-client-secret",
        callback_url="http://localhost:8000/api/oauth/callback"
    )

    # Connect a provider with specific scopes
    connection = await client.connect_provider(
        user_id="user123",
        provider_name="google",
        credentials=google_credentials,
        scopes=["gmail", "calendar"]
    )

    print(f"Connection ID: {connection.connection_id}")
    print(f"OAuth URL: {connection.redirect_url}")

# Run the example
asyncio.run(main())
```

## Core Features

### 1. Provider Connections

Connect users to various OAuth providers like Google, Microsoft, etc.

```python
from lumen_tools import LumenClient, ProviderCredentials

client = LumenClient(api_key="your-api-key")

# Create credentials for Google
google_credentials = ProviderCredentials(
    client_id="google-client-id",
    client_secret="google-client-secret",
    callback_url="https://your-app.com/callback"
)

# Connect provider with specific services
connection = await client.connect_provider(
    user_id="user123",
    provider_name="google",
    credentials=google_credentials,
    scopes=["gmail", "calendar", "drive"]
)

# Access the OAuth authorization URL
print(f"Redirect user to: {connection.redirect_url}")
```

### 2. OAuth Callback Handling

Handle OAuth callbacks after user authorization:

```python
# Handle the OAuth callback
callback_result = await client.handle_oauth_callback(
    code="authorization_code_from_callback",
    state="state_from_callback"
)

print(f"Authentication status: {callback_result['status']}")
print(f"Provider: {callback_result['provider']}")
print(f"Service: {callback_result['service']}")
```

### 3. Tools Integration

Get available tools for AI integration and execute tool calls:

```python
from lumen_tools import App, Action
from openai import OpenAI

# Get available tools for OpenAI
tools = await client.tools.get(tools=[App.GMAIL, Action.CALENDAR_CREATE_EVENT])

# Use with OpenAI
openai_client = OpenAI(api_key="your-openai-key")
response = openai_client.chat.completions.create(
    model="gpt-4o-mini",
    tools=tools,
    messages=[
        {"role": "user", "content": "Create a calendar event for tomorrow"}
    ]
)

# Execute the tool calls
result = await client.provider.handle_tool_calls(
    user_id="user123",
    response=response
)
```

### 4. Webhook Triggers

Set up webhooks to receive real-time notifications:

```python
from lumen_tools import ServiceType, EventType

# Setup webhook for Gmail notifications
webhook = await client.triggers.setup(
    user_id="user123",
    base_url="https://your-app.com/api/webhooks/notification",
    service=ServiceType.GMAIL,
    calendar_id="primary",
    event_types=[EventType.GMAIL_NEW_MESSAGE],
    google_project_id="your-project-id",
    topic_name="gmail-webhooks"
)

print(f"Webhook configured: {webhook}")
```

## Complete Example

```python
import asyncio
from openai import OpenAI
from lumen_tools import LumenClient, ProviderCredentials, Action, App, ServiceType, EventType

async def main():
    # Initialize clients
    client = LumenClient(api_key="your-lumen-api-key")
    openai_client = OpenAI(api_key="your-openai-api-key")

    user_id = "unique-user-id"

    # Setup Google credentials
    google_credentials = ProviderCredentials(
        client_id="your-google-client-id",
        client_secret="your-google-client-secret",
        callback_url="http://localhost:8000/api/oauth/callback"
    )

    # Connect Google provider with calendar access
    connection_request = await client.connect_provider(
        user_id=user_id,
        provider_name="google",
        credentials=google_credentials,
        scopes=["calendar"]
    )

    print(f"Connection Link: {connection_request.redirect_url}")
    print(f"Configured services: {connection_request.providers_services_configured}")

    # Get tools for AI integration
    tools = await client.tools.get(tools=[App.GMAIL, Action.CALENDAR_CREATE_EVENT])

    # Setup webhook for Gmail notifications
    webhook = await client.triggers.setup(
        user_id=user_id,
        base_url="https://your-app.com/api/webhooks/notification",
        service=ServiceType.GMAIL,
        calendar_id="primary",
        event_types=[EventType.GMAIL_NEW_MESSAGE],
        google_project_id="your-google-project-id",
        topic_name="gmail-webhooks"
    )

    # Use OpenAI with Lumen tools
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        tools=tools,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": (
                    "Create an event for tomorrow about wedding planning, then send an email to "
                    "example@gmail.com with subject 'Wedding planning' and event details"
                ),
            },
        ],
    )

    # Execute the AI's tool calls
    result = await client.provider.handle_tool_calls(user_id=user_id, response=response)

    print("Tool execution result:", result)
    print("Webhook configured:", webhook)

if __name__ == "__main__":
    asyncio.run(main())
```

## API Reference

### LumenClient

Main client class for interacting with the Lumen Core API.

#### Constructor

```python
LumenClient(api_key: str)
```

#### Core Methods

##### `connect_provider(user_id, provider_name, credentials, scopes=None)`

Connect a single provider for a user with specified scopes.

**Parameters:**

- `user_id` (str): Unique identifier for the user
- `provider_name` (str): Name of the provider (e.g., 'google', 'microsoft')
- `credentials` (ProviderCredentials): Provider credentials object
- `scopes` (Optional[List[str]]): List of service scopes

**Returns:** `ConnectionResponse` with connection details and OAuth URL

##### `handle_oauth_callback(code, state)`

Handle OAuth callback with authorization code and state.

**Parameters:**

- `code` (str): Authorization code from OAuth provider
- `state` (str): State parameter to verify the request

**Returns:** Dictionary containing callback result with provider, service, status, and tokens

### Manager Classes

#### `ToolsManager` (accessible via `client.tools`)

Manages tool-related operations.

- `get(tools: List[Union[App, Action]]) -> List[Dict]`: Get available tools for AI integration

#### `ProviderManager` (accessible via `client.provider`)

Manages provider-related operations.

- `handle_tool_calls(user_id: str, response: OpenAI.ChatCompletion) -> Dict`: Execute tool calls from AI responses

#### `TriggersManager` (accessible via `client.triggers`)

Manages webhook triggers.

- `setup(user_id, base_url, service, calendar_id, event_types, google_project_id, topic_name) -> Dict`: Setup webhook triggers

### Models

#### `ProviderCredentials`

```python
ProviderCredentials(
    client_id: str,
    client_secret: str,
    callback_url: str,
    services: Optional[List[str]] = None
)
```

#### `ConnectionResponse`

Response object containing:

- `connection_id`: Unique connection identifier
- `redirect_url`: OAuth authorization URL
- `state`: OAuth state parameter
- `providers_services_configured`: List of configured services

### Enums

#### `App`

- `GMAIL`
- `CALENDAR`
- `DRIVE`
- `DOCS`
- And more coming soon...

#### `ServiceType`

- `GMAIL`
- `CALENDAR`
- `DRIVE`
- `DOCS`
- And more coming soon...

## Context Manager Usage

The client supports async context manager for automatic resource cleanup:

```python
async with LumenClient(api_key="your-api-key") as client:
    connection = await client.connect_provider(
        user_id="user123",
        provider_name="google",
        credentials=google_credentials,
        scopes=["gmail"]
    )
    print(f"Connection created: {connection.connection_id}")
# Client automatically closed
```

## Error Handling

The client provides specific exception types for different error scenarios:

```python
from lumen_tools.exceptions import (
    LumenError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    ConnectionError
)

try:
    connection = await client.connect_provider(
        user_id="user123",
        provider_name="google",
        credentials=credentials,
        scopes=["gmail"]
    )
except AuthenticationError:
    print("Invalid API key")
except ValidationError as e:
    print(f"Validation error: {e}")
except LumenError as e:
    print(f"General API error: {e}")
```

## Supported Providers

- **Google**: Gmail, Calendar, Drive, Docs
- **And more coming soon...**

## Best Practices

1. **Always use context managers** for automatic resource cleanup
2. **Handle OAuth flows properly** by redirecting users to the provided OAuth URL
3. **Validate parameters** before making API calls
4. **Use appropriate error handling** for different error scenarios
5. **Store credentials securely** and never commit them to version control

## Development

### Setup

```bash
pip install lumen-tooling
```

## License

MIT License

## Author

Harsh Kumar [fyo9329@gmail.com](mailto:fyo9329@gmail.com)
