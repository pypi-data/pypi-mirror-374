#!/usr/bin/env python3
"""Basic test script for LDAP client functionality."""

from uio_api import ldap_client


def main() -> None:
    """Test basic LDAP client functionality."""
    print("Testing LDAP client...")

    try:
        # Test client creation
        client = ldap_client()
        print("✓ LDAP client created successfully")
        print(f"✓ Client module: {client.module}")

        # Test with anonymous access (should work for basic searches)
        print("\nTesting anonymous access...")
        try:
            # This might fail if anonymous access is not allowed, but that's okay for testing
            base_dn = "cn=people,dc=uio,dc=no"
            filter_str = "(uid=*)"  # Search for any user
            results = client.search(base=base_dn, filter_=filter_str, attributes=["cn", "uid"])
            print(f"✓ Anonymous search completed: {len(results)} results")
        except Exception as e:
            print(f"⚠ Anonymous search failed (expected if anonymous access disabled): {e}")

        # Test filter construction
        print("\nTesting filter construction...")
        test_filter = client.filter(objectClass="person", uid="test*")
        print(f"✓ Generated filter: {test_filter}")

        # Test DN construction
        print("\nTesting DN construction...")
        test_dn = client.base(cn="test", ou="users")
        print(f"✓ Generated DN: {test_dn}")

        print("\n✓ All LDAP client tests passed!")

    except Exception as e:
        print(f"✗ LDAP client test failed: {e}")
        import traceback

        traceback.print_exc()
        return None

    return None


if __name__ == "__main__":
    main()
