# Gymix Python SDK Documentation

![PyPI](https://img.shields.io/pypi/v/gymix)
![Python](https://img.shields.io/pypi/pyversions/gymix)
![License](https://img.shields.io/pypi/l/gymix)

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Authentication](#authentication)
5. [Client Configuration](#client-configuration)
6. [API Reference](#api-reference)
   - [Users Endpoint](#users-endpoint)
   - [Gym Endpoint](#gym-endpoint)
   - [Backup Endpoint](#backup-endpoint)
   - [Health Endpoint](#health-endpoint)
7. [Error Handling](#error-handling)
8. [Examples](#examples)
9. [Best Practices](#best-practices)
10. [Contributing](#contributing)

## Overview

The Gymix Python SDK is the official client library for interacting with the Gymix API. It provides a simple and intuitive interface for managing gym data, user accounts, backup services, and monitoring API health.

### Key Features

- **User Management**: Access user profiles and associated gym information
- **Gym Management**: Retrieve detailed gym information, subscriptions, and plans
- **Backup Services**: Complete backup lifecycle management (create, list, download, delete)
- **Health Monitoring**: Check API service status and system health
- **Type Safety**: Full type hints support for better development experience
- **Error Handling**: Comprehensive exception handling for all API errors
- **Context Manager**: Built-in support for resource cleanup

## Installation

### Requirements

- Python 3.7+
- requests library

### Install from PyPI

```bash
pip install gymix
```

### Install from Source

```bash
git clone https://github.com/mrssd/gymix-Python-SDK.git
cd gymix-Python-SDK
pip install -e .
```

## Quick Start

Here's a simple example to get you started:

```python
from gymix import GymixClient
from gymix.exceptions import GymixAPIError

# Initialize the client
client = GymixClient(api_token="your_api_token_here")

try:
    # Get user information
    user_info = client.users.get_info()
    print(f"Welcome, {user_info['name']} {user_info['lastname']}")

    # Get first gym
    if user_info['gyms']:
        gym_key = user_info['gyms'][0]['id']
        gym_info = client.gym.get_info(gym_key)
        print(f"Gym: {gym_info['gym_info']['name']}")

except GymixAPIError as e:
    print(f"API Error: {e}")
finally:
    client.close()
```

## Authentication

The Gymix SDK uses Bearer token authentication. You need to obtain an API token from your Gymix dashboard.

### Setting Up Authentication

```python
from gymix import GymixClient

# Method 1: Direct token
client = GymixClient(api_token="your_api_token_here")

# Method 2: Environment variable
import os
api_token = os.getenv("GYMIX_API_TOKEN")
client = GymixClient(api_token=api_token)
```

### Environment Variables

For security, it's recommended to store your API token in an environment variable:

```bash
export GYMIX_API_TOKEN="your_api_token_here"
```

## Client Configuration

### Basic Configuration

```python
from gymix import GymixClient

client = GymixClient(
    api_token="your_token",
    base_url="https://api.gymix.ir",  # Optional, default value
    timeout=30  # Optional, request timeout in seconds
)
```

### Using Context Manager (Recommended)

```python
from gymix import GymixClient

with GymixClient(api_token="your_token") as client:
    user_info = client.users.get_info()
    # Client automatically closes when exiting the context
```

## API Reference

### Users Endpoint

The Users endpoint provides access to user account information and associated gyms.

#### `client.users.get_info()`

Get current user's profile and gym information.

**Returns:**

```python
{
    "status": "active",           # User account status
    "name": "John",              # User's first name
    "lastname": "Doe",           # User's last name
    "phone": "+1234567890",      # User's phone number
    "address": "123 Main St",    # User's address
    "gyms": [                    # List of user's gyms
        {
            "id": "gym_key_123",
            "name": "Fitness Center",
            "location": "Downtown"
        }
    ],
    "balance": 50000             # User's account balance in Toman
}
```

**Raises:**

- `GymixAuthenticationError`: Invalid or missing auth token
- `GymixForbiddenError`: Account deactivated or restricted
- `GymixAPIError`: Other API errors

**Example:**

```python
user_info = client.users.get_info()
print(f"User: {user_info['name']} {user_info['lastname']}")
print(f"Balance: {user_info['balance']:,} تومان")
for gym in user_info['gyms']:
    print(f"Gym: {gym['name']} - {gym['location']}")
```

### Gym Endpoint

The Gym endpoint provides detailed information about gyms, subscriptions, and plans.

#### `client.gym.get_info(gym_public_key)`

Get comprehensive gym details including subscription and plan information.

**Parameters:**

- `gym_public_key` (str): Public key of the gym

**Returns:**

```python
{
    "gym_info": {
        "name": "Fitness Center",
        "location": "Downtown",
        "status": "active",
        "created_at": "2023-01-01",
        # ... other gym details
    },
    "subscription_info": {
        "name": "Premium Plan",
        "price": 100000,
        "remaining_days": 25,
        "usage_percentage": 75.5,
        "expires_at": "2024-01-01"
    },
    "plan_info": {
        "name": "Premium",
        "features": {
            "includes_backup": true,
            "includes_support": true,
            "max_members": 1000
        }
    },
    "subscription_summary": {
        "is_active": true,
        "is_expired": false
    }
}
```

**Raises:**

- `GymixAuthenticationError`: Invalid API token
- `GymixNotFoundError`: Gym not found or not owned by user
- `GymixAPIError`: Other API errors

**Example:**

```python
gym_info = client.gym.get_info("gym_key_123")
gym_data = gym_info['gym_info']
subscription = gym_info['subscription_info']

print(f"Gym: {gym_data['name']} ({gym_data['location']})")
print(f"Subscription: {subscription['name']}")
print(f"Days remaining: {subscription['remaining_days']}")
```

### Backup Endpoint

The Backup endpoint handles all backup-related operations including creation, listing, downloading, and deletion.

#### `client.backup.create(gym_public_key, file)`

Upload a backup ZIP file for a gym.

**Parameters:**

- `gym_public_key` (str): Public key of the gym
- `file` (BinaryIO): Binary file object containing the ZIP backup

**Returns:**

```python
{
    "id": "backup_123",
    "file_name": "backup_2024_01_01.zip",
    "created_at": "2024-01-01T10:00:00Z",
    "size": 1048576,  # File size in bytes
    "plan_info": {
        "max_backups": 10,
        "daily_limit": 3
    }
}
```

**Raises:**

- `GymixAuthenticationError`: Invalid API token
- `GymixNotFoundError`: Gym not found or not owned by user
- `GymixForbiddenError`: Subscription expired or backup not included in plan
- `GymixRateLimitError`: Daily backup limit reached
- `GymixBadRequestError`: Invalid file type (must be ZIP)
- `GymixServerError`: S3 upload failed

**Example:**

```python
with open("backup.zip", "rb") as backup_file:
    backup = client.backup.create("gym_key_123", backup_file)
    print(f"Backup created: {backup['id']}")
    print(f"File size: {backup['size']} bytes")
```

#### `client.backup.get_plan(gym_public_key)`

Get backup plan information and current usage statistics.

**Parameters:**

- `gym_public_key` (str): Public key of the gym

**Returns:**

```python
{
    "plan_info": {
        "max_backups": 10,
        "daily_limit": 3,
        "includes_backup": true
    },
    "current_usage": {
        "backup_count": 5,
        "today_backup_count": 1,
        "can_create_more_today": true
    },
    "subscription_info": {
        "expires_at": "2024-12-31",
        "is_expired": false
    }
}
```

**Example:**

```python
plan = client.backup.get_plan("gym_key_123")
usage = plan['current_usage']
print(f"Backups: {usage['backup_count']}/{plan['plan_info']['max_backups']}")
print(f"Today: {usage['today_backup_count']}/{plan['plan_info']['daily_limit']}")
```

#### `client.backup.list(gym_public_key, verified=None)`

List all backups for a gym with optional filtering.

**Parameters:**

- `gym_public_key` (str): Public key of the gym
- `verified` (bool, optional): Filter for verified backups

**Returns:**

```python
{
    "backups": [
        {
            "id": "backup_123",
            "file_name": "backup_2024_01_01.zip",
            "created_at": "2024-01-01T10:00:00Z",
            "size": 1048576,
            "verified": true
        }
    ],
    "total_count": 1,
    "verified": true
}
```

**Example:**

```python
# List all backups
all_backups = client.backup.list("gym_key_123")

# List only verified backups
verified_backups = client.backup.list("gym_key_123", verified=True)

for backup in all_backups['backups']:
    print(f"- {backup['file_name']} (ID: {backup['id']})")
```

#### `client.backup.download(backup_id, gym_public_key)`

Get a signed download URL for a backup file.

**Parameters:**

- `backup_id` (str): ID of the backup to download
- `gym_public_key` (str): Public key of the gym

**Returns:**

```python
{
    "backup_id": "backup_123",
    "file_name": "backup_2024_01_01.zip",
    "download_url": "https://s3.amazonaws.com/signed-url...",
    "expires_in": "24 hours",
    "created_at": "2024-01-01T10:00:00Z",
    "cached": false
}
```

**Raises:**

- `GymixBadRequestError`: Backup missing bucket info
- `GymixServerError`: S3 error or download URL generation failed

**Example:**

```python
download_info = client.backup.download("backup_123", "gym_key_123")
print(f"Download URL: {download_info['download_url']}")
print(f"Expires in: {download_info['expires_in']}")

# Use the URL to download the file
import requests
response = requests.get(download_info['download_url'])
with open(download_info['file_name'], 'wb') as f:
    f.write(response.content)
```

#### `client.backup.delete(backup_id, gym_public_key)`

Delete a backup file from storage and database.

**Parameters:**

- `backup_id` (str): ID of the backup to delete
- `gym_public_key` (str): Public key of the gym

**Returns:**

```python
{
    "backup_id": "backup_123",
    "message": "Backup deleted successfully"
}
```

**Example:**

```python
result = client.backup.delete("backup_123", "gym_key_123")
print(result['message'])
```

### Health Endpoint

The Health endpoint provides API status and system health information.

#### `client.health.check()`

Check API health status and system information. This endpoint does not require authentication.

**Returns:**

```python
{
    "status": "healthy",           # "healthy" or "unhealthy"
    "timestamp": "2024-01-01T10:00:00Z",
    "version": "1.0.0",
    "uptime": "72h 15m 30s",
    "database": "connected",
    "storage": "available"
}
```

**Raises:**

- `GymixServiceUnavailableError`: API temporarily unavailable
- `GymixAPIError`: Other API errors

**Example:**

```python
health = client.health.check()
print(f"API Status: {health['status']}")
print(f"Version: {health['version']}")
print(f"Database: {health['database']}")
print(f"Storage: {health['storage']}")
```

## Error Handling

The SDK provides comprehensive error handling with specific exception types for different scenarios.

### Exception Hierarchy

```python
GymixAPIError  # Base exception
├── GymixAuthenticationError     # 401 Unauthorized
├── GymixForbiddenError         # 403 Forbidden
├── GymixNotFoundError          # 404 Not Found
├── GymixBadRequestError        # 400 Bad Request
├── GymixRateLimitError         # 429 Too Many Requests
├── GymixServerError            # 5xx Server Errors
└── GymixServiceUnavailableError # 503 Service Unavailable
```

### Exception Properties

All exceptions include:

- `message`: Error description
- `status_code`: HTTP status code (if applicable)
- `response_data`: Full API response data

### Error Handling Examples

```python
from gymix import GymixClient
from gymix.exceptions import (
    GymixAuthenticationError,
    GymixNotFoundError,
    GymixRateLimitError,
    GymixAPIError
)

client = GymixClient(api_token="your_token")

try:
    user_info = client.users.get_info()

except GymixAuthenticationError:
    print("Invalid API token. Please check your credentials.")

except GymixNotFoundError as e:
    print(f"Resource not found: {e.message}")

except GymixRateLimitError as e:
    print(f"Rate limit exceeded: {e.message}")
    print(f"Status code: {e.status_code}")

except GymixAPIError as e:
    print(f"API Error: {e.message}")
    if e.status_code:
        print(f"Status Code: {e.status_code}")
    if e.response_data:
        print(f"Response: {e.response_data}")
```

## Examples

### Complete Backup Management Example

```python
import os
from gymix import GymixClient
from gymix.exceptions import GymixAPIError, GymixRateLimitError

def backup_management_example():
    """Complete example of backup management operations."""

    # Initialize client
    api_token = os.getenv("GYMIX_API_TOKEN")
    if not api_token:
        print("Please set GYMIX_API_TOKEN environment variable")
        return

    with GymixClient(api_token=api_token) as client:
        try:
            # Get user info and first gym
            user_info = client.users.get_info()
            if not user_info['gyms']:
                print("No gyms found")
                return

            gym_key = user_info['gyms'][0]['id']
            print(f"Working with gym: {user_info['gyms'][0]['name']}")

            # Check backup plan
            plan = client.backup.get_plan(gym_key)
            usage = plan['current_usage']
            print(f"Backup usage: {usage['backup_count']}/{plan['plan_info']['max_backups']}")

            # List existing backups
            backups = client.backup.list(gym_key)
            print(f"Existing backups: {len(backups['backups'])}")

            for backup in backups['backups']:
                print(f"  - {backup['file_name']} ({backup['id']})")

            # Create new backup (if file exists)
            backup_file = "example_backup.zip"
            if os.path.exists(backup_file):
                try:
                    with open(backup_file, "rb") as f:
                        new_backup = client.backup.create(gym_key, f)
                    print(f"Created backup: {new_backup['id']}")

                    # Get download URL
                    download_info = client.backup.download(new_backup['id'], gym_key)
                    print(f"Download URL: {download_info['download_url']}")

                except GymixRateLimitError:
                    print("Daily backup limit reached")

        except GymixAPIError as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    backup_management_example()
```

### Monitoring and Health Check Example

```python
import time
from gymix import GymixClient
from gymix.exceptions import GymixServiceUnavailableError

def monitor_api_health():
    """Monitor API health status."""

    client = GymixClient(api_token="your_token")

    while True:
        try:
            health = client.health.check()

            if health['status'] == 'healthy':
                print(f"✅ API is healthy - Version: {health['version']}")
            else:
                print(f"❌ API is unhealthy - Status: {health['status']}")

            # Check individual components
            print(f"Database: {health['database']}")
            print(f"Storage: {health['storage']}")

        except GymixServiceUnavailableError:
            print("⚠️ API is temporarily unavailable")

        except Exception as e:
            print(f"❌ Health check failed: {e}")

        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    monitor_api_health()
```

### Gym Information Dashboard Example

```python
from gymix import GymixClient
from gymix.exceptions import GymixAPIError

def gym_dashboard():
    """Display comprehensive gym information dashboard."""

    client = GymixClient(api_token=os.getenv("GYMIX_API_TOKEN"))

    try:
        # Get user and gym information
        user_info = client.users.get_info()

        print("=" * 50)
        print(f"GYMIX DASHBOARD")
        print("=" * 50)
        print(f"User: {user_info['name']} {user_info['lastname']}")
        print(f"Phone: {user_info['phone']}")
        print(f"Balance: {user_info['balance']:,} تومان")
        print(f"Account Status: {user_info['status']}")

        for gym in user_info['gyms']:
            gym_key = gym['id']

            print(f"\n{'=' * 30}")
            print(f"GYM: {gym['name']}")
            print(f"{'=' * 30}")

            # Get detailed gym info
            gym_info = client.gym.get_info(gym_key)
            gym_data = gym_info['gym_info']
            subscription = gym_info['subscription_info']
            plan = gym_info['plan_info']

            print(f"Location: {gym_data['location']}")
            print(f"Status: {gym_data['status']}")

            print(f"\nSubscription:")
            print(f"  Plan: {subscription['name']}")
            print(f"  Price: {subscription['price']:,} تومان")
            print(f"  Remaining Days: {subscription['remaining_days']}")
            print(f"  Usage: {subscription['usage_percentage']:.1f}%")

            print(f"\nFeatures:")
            features = plan['features']
            print(f"  Backup: {'✅' if features['includes_backup'] else '❌'}")
            print(f"  Support: {'✅' if features['includes_support'] else '❌'}")

            # Backup information
            if features['includes_backup']:
                backup_plan = client.backup.get_plan(gym_key)
                usage = backup_plan['current_usage']
                plan_info = backup_plan['plan_info']

                print(f"\nBackup Status:")
                print(f"  Total Backups: {usage['backup_count']}/{plan_info['max_backups']}")
                print(f"  Today's Backups: {usage['today_backup_count']}/{plan_info['daily_limit']}")
                print(f"  Can Create More: {'✅' if usage['can_create_more_today'] else '❌'}")

                # List recent backups
                backups = client.backup.list(gym_key)
                if backups['backups']:
                    print(f"\nRecent Backups:")
                    for backup in backups['backups'][-3:]:  # Last 3 backups
                        print(f"    - {backup['file_name']} ({backup['created_at']})")

    except GymixAPIError as e:
        print(f"Dashboard Error: {e}")

    finally:
        client.close()

if __name__ == "__main__":
    gym_dashboard()
```

## Best Practices

### 1. Use Context Managers

Always use context managers to ensure proper resource cleanup:

```python
# ✅ Good
with GymixClient(api_token="token") as client:
    user_info = client.users.get_info()

# ❌ Not recommended
client = GymixClient(api_token="token")
user_info = client.users.get_info()
client.close()  # Easy to forget
```

### 2. Handle Specific Exceptions

Catch specific exceptions rather than generic ones:

```python
# ✅ Good
try:
    backup = client.backup.create(gym_key, file)
except GymixRateLimitError:
    print("Rate limit exceeded, try again later")
except GymixAuthenticationError:
    print("Authentication failed")
except GymixAPIError as e:
    print(f"Unexpected error: {e}")

# ❌ Not recommended
try:
    backup = client.backup.create(gym_key, file)
except Exception as e:
    print(f"Something went wrong: {e}")
```

### 3. Use Environment Variables for Secrets

Never hardcode API tokens in your source code:

```python
# ✅ Good
import os
api_token = os.getenv("GYMIX_API_TOKEN")
if not api_token:
    raise ValueError("GYMIX_API_TOKEN environment variable is required")

# ❌ Never do this
api_token = "your_actual_token_here"  # Security risk!
```

### 4. Implement Retry Logic for Rate Limits

```python
import time
from gymix.exceptions import GymixRateLimitError

def create_backup_with_retry(client, gym_key, file, max_retries=3):
    """Create backup with retry logic for rate limits."""

    for attempt in range(max_retries):
        try:
            return client.backup.create(gym_key, file)
        except GymixRateLimitError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Rate limited. Waiting {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise e
```

### 5. Validate Inputs

Always validate inputs before making API calls:

```python
def safe_backup_create(client, gym_key, file_path):
    """Safely create a backup with input validation."""

    if not gym_key or not isinstance(gym_key, str):
        raise ValueError("gym_key must be a non-empty string")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Backup file not found: {file_path}")

    if not file_path.endswith('.zip'):
        raise ValueError("Backup file must be a ZIP file")

    file_size = os.path.getsize(file_path)
    if file_size > 100 * 1024 * 1024:  # 100MB limit
        raise ValueError("Backup file too large (max 100MB)")

    with open(file_path, 'rb') as f:
        return client.backup.create(gym_key, f)
```

### 6. Log Operations

Implement proper logging for debugging and monitoring:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def logged_backup_operation(client, gym_key):
    """Backup operation with comprehensive logging."""

    logger.info(f"Starting backup operation for gym: {gym_key}")

    try:
        # Check plan first
        plan = client.backup.get_plan(gym_key)
        logger.info(f"Backup plan: {plan['plan_info']['max_backups']} max backups")

        # List existing backups
        backups = client.backup.list(gym_key)
        logger.info(f"Found {len(backups['backups'])} existing backups")

        return backups

    except GymixAPIError as e:
        logger.error(f"Backup operation failed: {e}")
        raise
```

## Contributing

We welcome contributions to the Gymix Python SDK! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details on how to submit issues, feature requests, and pull requests.

### Development Setup

1. Clone the repository:

```bash
git clone https://github.com/mrssd/gymix-Python-SDK.git
cd gymix-Python-SDK
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:

```bash
pip install -e ".[dev]"
```

4. Run tests:

```bash
python -m pytest tests/
```

### Testing

The SDK includes comprehensive tests. To run the test suite:

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=gymix

# Run specific test file
python -m pytest tests/test_client.py
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: This document and inline code documentation
- **Issues**: [GitHub Issues](https://github.com/mrssd/gymix-Python-SDK/issues)
- **Email**: support@gymix.ir
- **Website**: [https://gymix.ir](https://gymix.ir)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes and releases.

---

_This documentation is for Gymix Python SDK version 1.0.0. For the latest updates, please check our GitHub repository._
