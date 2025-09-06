# UIO API LDAP Module

This module provides comprehensive LDAP client functionality for querying University of Oslo directory services.

## Features

- **Anonymous Binding**: Support for anonymous LDAP queries (default: enabled)
- **Authenticated Access**: Username/password authentication for restricted operations
- **Comprehensive Search**: Query users, people, hosts, organizations, netgroups, filegroups, and automount entries
- **Flexible Filtering**: Build complex LDAP filters with ease
- **Error Handling**: Detailed error messages with diagnostic information
- **Configuration Support**: Environment variables and config file support
- **System User Support**: Store LDAP credentials securely

## Installation

The LDAP module requires the `ldap3` library:

```bash
pip install ldap3
```

## Quick Start

### Anonymous Access (Default)

```python
from uio_api import ldap_client

# Create client with anonymous access
client = ldap_client()

# Search for users
users = client.users(user="radius")
print(f"Found {len(users)} user(s)")

# Search for people (students/employees)
people = client.people(name="Oistein")
for person in people:
    print(f"{person.get('cn', ['Unknown'])[0]}: {person.get('mail', [])}")

# Search for hosts
hosts = client.hosts(host="*.uio.no")
print(f"Found {len(hosts)} host(s)")
```

### Persistent Connections (Recommended)

```python
# Use context manager for persistent connection (more efficient)
with ldap_client(username="myuser", interactive=True) as client:
    users = client.users(user="radius")      # Reuses connection
    people = client.people(name="Oistein")   # Reuses connection
    hosts = client.hosts(host="*.uio.no")    # Reuses connection
# Connection automatically closed here
```

### Authenticated Access

```python
# Prompted auth (override prompts if desired)
client = ldap_client(username="your-username", interactive=True)

# Now you can access restricted areas
restricted_users = client.users(user="admin")
```

### Advanced Configuration

```python
# Custom LDAP server
client = ldap_client(
    url="ldap://custom.ldap.server:389",
    domain_controllers=["custom", "domain"],
    allow_anonymous=False  # Require authentication
)

## System User vs Token

- This LDAP module supports storing credentials via `add_system_user()`.
- LDAP does not use bearer tokens; calling `add_token()` will raise `NotImplementedError`.

### Store system user credentials

```python
client.add_system_user(
    username="ldap-service",
    password="service-password"
)
```
```

## Configuration

The LDAP module supports configuration via environment variables and config files:

### Environment Variables

- `UIO_API_LDAP_URL`: LDAP server URL (default: "ldap://ldap.uio.no")
- `UIO_API_LDAP_DOMAIN_CONTROLLERS`: Domain controllers (default: "uio,no")
- `UIO_API_LDAP_ALLOW_ANONYMOUS`: Allow anonymous binding (default: "true")
- `LDAP_URL`: Module-specific LDAP URL
- `LDAP_DOMAIN_CONTROLLERS`: Module-specific domain controllers
- `LDAP_ALLOW_ANONYMOUS`: Module-specific anonymous access setting

### Config File

Add to `~/.config/uio_api/config.toml`:

```toml
[ldap]
url = "ldap://ldap.uio.no"
domain_controllers = ["uio", "no"]
allow_anonymous = true

[user."your-username"]
[module.ldap]
url = "ldap://custom.ldap.uio.no"
allow_anonymous = false
```

## API Reference

### Client Methods

#### `users(user=None, uid=None, attributes=None, filter=None, username=None, password=None)`

Search for system user accounts.

**Parameters:**
- `user`: Username to search for
- `uid`: User ID to search for
- `attributes`: Specific attributes to return
- `filter`: Custom LDAP filter
- `username`: Bind username (overrides client default)
- `password`: Bind password (overrides client default)

**Returns:** List of user dictionaries

#### `people(name=None, surname=None, given_name=None, mail=None, phone=None, object_class=None, affiliation=None, uid=None, filter=None, attributes=None, username=None, password=None)`

Search for people (students and employees).

**Parameters:**
- `name`: Common name to search for
- `surname`: Family name
- `given_name`: First name
- `mail`: Email address
- `phone`: Telephone number
- `object_class`: LDAP object class
- `affiliation`: Educational affiliation
- `uid`: User ID
- `attributes`: Specific attributes to return
- `filter`: Custom LDAP filter

**Returns:** List of person dictionaries

#### `hosts(host=None, contact=None, comment=None, mac=None, filter=None, attributes=None, username=None, password=None)`

Search for host entries.

**Parameters:**
- `host`: Hostname pattern
- `contact`: Host contact person
- `comment`: Host comment
- `mac`: MAC address
- `attributes`: Specific attributes to return
- `filter`: Custom LDAP filter

**Returns:** List of host dictionaries

#### `organization(organization=None, mail=None, phone=None, org_number=None, attributes=None, filter=None, username=None, password=None)`

Search for organizational units.

**Parameters:**
- `organization`: Organization name (ou)
- `mail`: Email address
- `phone`: Telephone number
- `org_number`: Organization number
- `attributes`: Specific attributes to return
- `filter`: Custom LDAP filter

**Returns:** List of organization dictionaries

#### `netgroups(cn=None, object_class=None, attributes=None, filter=None, username=None, password=None)`

Search for NIS netgroups.

**Parameters:**
- `cn`: Common name of netgroup
- `object_class`: LDAP object class filter
- `attributes`: Specific attributes to return
- `filter`: Custom LDAP filter

**Returns:** List of netgroup dictionaries with processed member lists

#### `filegroups(cn=None, gid=None, uid=None, object_class=None, attributes=None, filter=None, username=None, password=None)`

Search for POSIX file groups.

**Parameters:**
- `cn`: Common name of filegroup
- `gid`: Group ID number
- `uid`: Member user ID
- `object_class`: LDAP object class filter
- `attributes`: Specific attributes to return
- `filter`: Custom LDAP filter

**Returns:** List of filegroup dictionaries with normalized member lists

#### `automount(cn=None, ou="auto.master", information=None, attributes=None, filter=None, username=None, password=None)`

Search for automount entries.

**Parameters:**
- `cn`: Common name
- `ou`: Organizational unit path (default: "auto.master")
- `information`: Automount information string
- `attributes`: Specific attributes to return
- `filter`: Custom LDAP filter

**Returns:** List of automount dictionaries with resolved symlinks

#### `search(base, filter, attributes=None, username=None, password=None)`

Perform raw LDAP search.

**Parameters:**
- `base`: Search base DN
- `filter`: LDAP filter string
- `attributes`: Attributes to return
- `username`: Bind username
- `password`: Bind password

**Returns:** List of search result dictionaries

## Factory Knobs (uniform with other modules)

```python
client = ldap_client(
    url="ldap://ldap.uio.no",
    domain_controllers=["uio", "no"],
    allow_anonymous=True,
    username="myuser",                # optional; used if interactive
    system_user="ldap-service",       # load password from storage
    interactive=True,                  # prompt if needed
    prompt_username=lambda: "myuser", # optional override for username prompt
    prompt_password=lambda u: "pwd",  # optional override for password prompt
    secrets_backend="toml",           # or "keyring"
)
```

Notes:
- `system_user` takes precedence; password is loaded from configured backend.
- If `interactive=True` and no `username` is set, a default username prompt is used.
- `add_token()` is not supported for LDAP and raises `NotImplementedError`.

## Error Handling

The LDAP module provides detailed error information:

```python
from uio_api.modules.ldap import LdapError

try:
    results = client.users(user="nonexistent")
except LdapError as e:
    print(f"LDAP Error: {e}")
    print(f"Error code: {e.code}")
    print(f"Diagnostic info: {e.info}")
```

## System User Management

Store LDAP credentials securely with `add_system_user()`. Attempting `add_token()`
is unsupported and will raise `NotImplementedError`.

## Security Notes

- Anonymous binding is enabled by default for basic queries
- Credentials are stored securely using the configured secrets backend (TOML or keyring)
- LDAP connections use TLS by default
- Sensitive data in logs is automatically redacted

## Examples

### Find all users in a department

```python
# Search for users with department info
users = client.users(attributes=["cn", "uid", "departmentNumber", "employeeType"])

for user in users:
    dept = user.get("departmentNumber", ["Unknown"])[0]
    print(f"{user['cn'][0]} ({user['uid'][0]}): Department {dept}")
```

### Find hosts by contact person

```python
# Find hosts maintained by a specific person
hosts = client.hosts(contact="admin@example.com")

for host in hosts:
    print(f"Host: {host.get('host', ['Unknown'])[0]}")
    print(f"Contact: {host.get('uioHostContact', ['N/A'])}")
```

### Complex people search

```python
# Find employees with specific criteria
employees = client.people(
    affiliation="employee",
    mail="*uio.no",
    attributes=["cn", "mail", "telephoneNumber", "eduPersonAffiliation"]
)

for emp in employees:
    print(f"Employee: {emp['cn'][0]}")
    print(f"Email: {emp.get('mail', ['N/A'])[0]}")
```

## Troubleshooting

### Common Issues

1. **Anonymous access denied**: Some LDAP operations require authentication
   ```python
   client = ldap_client(bind_user="your-user", bind_password="your-pass")
   ```

2. **Connection timeout**: Check network connectivity and LDAP server status
   ```python
   client = ldap_client(url="ldap://alternative.server:389")
   ```

3. **Invalid credentials**: Verify username/password combination
   ```python
   # Check if credentials work
   try:
       test = client.search("cn=people,dc=uio,dc=no", "(uid=your-user)")
   except LdapError as e:
       print(f"Authentication failed: {e}")
   ```

### Debug Logging

Enable debug logging to see LDAP operations:

```python
import loguru
from uio_api import setup_logging

# Enable logging
loguru.logger.enable("uio_api")
setup_logging(include_endpoints=True, level="DEBUG")

# Now LDAP operations will be logged
users = client.users(user="test")
```
