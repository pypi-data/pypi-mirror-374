# UIO API

A Python library for interacting with UIO APIs, featuring built‑in authentication, robust retries, secure token storage, and pagination utilities.

## Documentation Map

- User Guide (usage, configuration, examples): `uio_api/README.md`
- Developer Guide (architecture, internals, patterns): `uio_api/INTERNAL.md`

## Features

- **🔐 Authentication**: Interactive login, static tokens, or system accounts
- **⚡ Retries**: Configurable retry strategy with exponential backoff
- **🛡️ Secure Storage**: Keyring or TOML‑based token storage
- **📄 Pagination**: DRF‑style pagination helpers and safeguards

## Installation

```bash
pip install uio-api
```

## Quick Start

```python
from uio_api import mreg_client
from uio_api.modules.mreg.endpoints import Endpoint

with mreg_client() as m:
    hosts = m.get_all(Endpoint.Hosts)
    print(f"Found {len(hosts)} hosts")
```

For full usage, configuration, and advanced examples, see `uio_api/README.md`.

## Token helpers

You can store credentials/tokens via the client instances (URLs resolved automatically):

```python
from uio_api import mreg_client, nivlheim_client

# MREG: add system user (uses MREG_URL from config)
with mreg_client() as client:
    client.add_system_user(username="svc", password="secret")

# MREG: add token with knobs (uses MREG_URL from config)
with mreg_client() as client:
    client.add_token(
        username="bob",
        token="abc123",
        scheme="Token",
        timeout=60.0,
        retry_attempts=5,
        page_size=1000,
    )

# Nivlheim: add API key (uses https://nivlheim.uio.no default)
with nivlheim_client() as client:
    client.add_token(
        username="svc",
        token="apikey123",
        scheme="APIKEY",
    )

# Or use explicit URLs
with mreg_client() as client:
    client.add_token(
        username="bob",
        token="abc123",
        url="https://custom.mreg.uio.no"
    )
```