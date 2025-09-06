"""Test script for UIO API Wrapper MREG client functionality.

This script:
- Prints effective configuration paths and logging settings (resolved from env + config).
- Runs a few sanity tests against the MREG client.
- Respects the package logging policy (silent unless enabled via config/env).
"""

from pathlib import Path
from typing import Optional

from . import mreg_client
from .config.base import base_settings
from .config.paths import resolve_config_dir, secrets_toml_path
from .modules.mreg.endpoints import Endpoint


def _bool_str(v: bool) -> str:
    return "true" if v else "false"


def _maybe(path: Optional[Path]) -> str:
    return str(path) if path else "(default ~/.config/uio_api/logs/uio_api.log)"


def _print_header() -> None:
    print("Testing UIO API Wrapper MREG client...")
    cfg_dir = resolve_config_dir()
    secrets_file = secrets_toml_path(cfg_dir)
    cfg_file = Path(cfg_dir) / "config.toml"

    print(f"Configuration directory: {cfg_dir}")
    print(f"Secrets file location: {secrets_file}")
    print(f"Secrets file exists: {secrets_file.exists()}")
    print(f"Config file: {cfg_file}")
    print(f"Config file exists: {cfg_file.exists()}")
    print()

    # Effective logging settings (from env + config, already merged in base_settings)
    print("Effective logging settings (env overrides config):")
    print(f"  logging_enabled         = {_bool_str(base_settings.logging_enabled)}")
    print(f"  logging_console_enabled = {_bool_str(base_settings.logging_console_enabled)}")
    print(f"  logging_file_enabled    = {_bool_str(base_settings.logging_file_enabled)}")
    print(f"  logging_level (console) = {base_settings.logging_level}")
    print(f"  logging_file_level      = {base_settings.logging_file_level}")
    print(f"  logging_file_path       = {_maybe(base_settings.logging_file_path)}")
    print()

    if not base_settings.logging_enabled:
        print("NOTE: Logging is disabled (set UIO_API_LOGGING_ENABLED=true to enable).")
        print()

    # If there is no config file, show a minimal example to help the user
    if not cfg_file.exists():
        print("Tip: Create a minimal config at ~/.config/uio_api/config.toml")
        print("with the following to enable both sinks and set levels:")
        print()
        print("  [default]")
        print("  logging_enabled = true")
        print("  logging_console_enabled = true")
        print("  logging_file_enabled = true")
        print('  logging_level = "SUCCESS"      # console level')
        print('  logging_file_level = "WARNING"  # file level')
        print('  # logging_file_path = "/var/log/uio_api/uio_api.log"  # optional')
        print()


def main() -> int:
    """Test basic UIO API Wrapper MREG client functionality."""
    _print_header()

    try:
        with mreg_client(username="oistes-drift", interactive=True, persist=True) as m:
            # logger.info("Client created successfully")
            print("✓ Client created successfully")

            # Test getting a specific host
            print("Testing host retrieval...")
            # logger.info("Testing host retrieval for bybanen.uio.no")
            host = m.get(Endpoint.Hosts.with_id("bybanen.uio.no"))
            print(f"✓ Host retrieved: {host}")
            # logger.info(f"Retrieved host data: {host}")

            # Test getting all hosts (with pagination)
            print("Testing host retrieval with pagination...")
            # logger.info("Testing host retrieval with name filter")
            hosts = m.get(Endpoint.Hosts, params={"name__startswith": "login"})
            results = hosts.get("results", []) if isinstance(hosts, dict) else []
            total = hosts.get("count", 0) if isinstance(hosts, dict) else len(results)
            print(f"✓ Retrieved {len(results)} hosts")
            print(f"Total count: {total}")
            # logger.info(f"Retrieved {len(results)} hosts out of {total} total")

            # Test endpoint parameterization
            print("Testing endpoint parameterization...")
            test_endpoint = Endpoint.HostGroupsAddHosts.with_params("test-group")
            print(f"✓ Parameterized endpoint: {test_endpoint}")
            # logger.info(f"Created parameterized endpoint: {test_endpoint}")

            # Test getting hosts with get_all method (limited to avoid 10k+ hosts)
            print("Testing get_all method with limit...")
            # logger.info("Testing get_all method for hosts with limit")
            limited_hosts = m.get_all(Endpoint.Hosts, params={"name__startswith": "login"})
            print(f"✓ Retrieved {len(limited_hosts)} hosts using get_all with filter")
            # logger.info(f"Retrieved {len(limited_hosts)} hosts using get_all method with filter")

            # Test pagination with smaller page size
            print("Testing pagination with small page size...")
            # logger.info(
            #     "Testing pagination with small page size to demonstrate page X of Y logging"
            # )
            paginated_hosts = m.get_all(
                Endpoint.Hosts, page_size=5, params={"name__startswith": "login"}
            )
            print(f"✓ Retrieved {len(paginated_hosts)} hosts using get_all with small page size")
            # logger.info(
            #     "Retrieved %d hosts using get_all with small page size", len(paginated_hosts)
            # )

    except Exception as e:
        # logger.error(f"Test failed: {e}")
        print(f"✗ Test failed: {e}")
        return 1

    # logger.info("All tests passed successfully")
    print("✓ All tests passed!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
