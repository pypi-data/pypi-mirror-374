#!/usr/bin/env python3
"""
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
Script for generating test configurations for MCP Proxy Adapter.
Generates 6 different configuration types for testing various security scenarios.
"""
import json
import os
import argparse
from typing import Dict, Any


def generate_http_simple_config(
    port: int = 20000, certs_dir: str = "certs", keys_dir: str = "keys"
) -> Dict[str, Any]:
    """Generate HTTP configuration without authorization."""
    return {
        "server": {"host": "127.0.0.1", "port": port},
        "ssl": {"enabled": False},
        "security": {"enabled": False},
        "registration": {
            "enabled": False,
            "auth_method": "token",
            "server_url": "http://127.0.0.1:3004/proxy",
            "token": {"enabled": True, "token": "proxy_registration_token_123"},
            "proxy_info": {
                "name": "mcp_example_server",
                "capabilities": ["jsonrpc", "rest", "proxy_registration"],
                "endpoints": {
                    "jsonrpc": "/api/jsonrpc",
                    "rest": "/cmd",
                    "health": "/health"
                }
            },
            "heartbeat": {"enabled": True, "interval": 30}
        },
        "protocols": {
            "enabled": True,
            "allowed_protocols": ["http"]
        }
    }


def generate_http_token_config(
    port: int = 20001,
    certs_dir: str = "certs",
    keys_dir: str = "keys",
    roles_file: str = "configs/roles.json"
) -> Dict[str, Any]:
    """Generate HTTP configuration with token authorization."""
    return {
        "server": {"host": "127.0.0.1", "port": port},
        "ssl": {"enabled": False},
        "security": {
            "enabled": True,
            "auth": {
                "enabled": True,
                "methods": ["api_key"],
                # Map API tokens to roles for testing
                "api_keys": {
                    "test-token-123": "admin",
                    "user-token-456": "user",
                    "readonly-token-123": "readonly",
                    "guest-token-123": "guest",
                    "proxy-token-123": "proxy"
                }
            },
            "permissions": {"enabled": True, "roles_file": roles_file}
        },
        "registration": {
            "enabled": True,
            "url": "http://127.0.0.1:3004/proxy",
            "name": "http_token_adapter",
            "capabilities": ["http", "token_auth"],
            "retry_count": 3,
            "retry_delay": 5,
            "heartbeat": {"enabled": True, "interval": 30}
        },
        "protocols": {
            "enabled": True,
            "allowed_protocols": ["http"]
        }
    }


def generate_https_simple_config(
    port: int = 20002, certs_dir: str = "certs", keys_dir: str = "keys"
) -> Dict[str, Any]:
    """Generate HTTPS configuration without client certificate verification and authorization."""
    return {
        "server": {"host": "127.0.0.1", "port": port},
        "ssl": {
            "enabled": True,
            "cert_file": f"{certs_dir}/localhost_server.crt",
            "key_file": f"{keys_dir}/localhost_server.key"
        },
        "security": {"enabled": False},
        "registration": {
            "enabled": True,
            "url": "http://127.0.0.1:3004/proxy",
            "name": "https_simple_adapter",
            "capabilities": ["https"],
            "retry_count": 3,
            "retry_delay": 5,
            "heartbeat": {"enabled": True, "interval": 30}
        },
        "protocols": {
            "enabled": True,
            "allowed_protocols": ["http", "https"]
        }
    }


def generate_https_token_config(
    port: int = 20003, certs_dir: str = "certs", keys_dir: str = "keys"
) -> Dict[str, Any]:
    """Generate HTTPS configuration without client certificate verification with token authorization."""
    return {
        "server": {"host": "127.0.0.1", "port": port},
        "ssl": {
            "enabled": True,
            "cert_file": f"{certs_dir}/localhost_server.crt",
            "key_file": f"{keys_dir}/localhost_server.key"
        },
        "security": {
            "enabled": True,
            "auth": {
                "enabled": True,
                "methods": ["api_key"],
                "api_keys": {
                    "test-token-123": "admin",
                    "user-token-456": "user",
                    "readonly-token-123": "readonly",
                    "guest-token-123": "guest",
                    "proxy-token-123": "proxy"
                }
            },
            "permissions": {"enabled": True, "roles_file": "./configs/roles.json"}
        },
        "registration": {
            "enabled": True,
            "url": "http://127.0.0.1:3004/proxy",
            "name": "https_token_adapter",
            "capabilities": ["https", "token_auth"],
            "retry_count": 3,
            "retry_delay": 5,
            "heartbeat": {"enabled": True, "interval": 30}
        },
        "protocols": {
            "enabled": True,
            "allowed_protocols": ["http", "https"]
        }
    }


def generate_mtls_no_roles_config(
    port: int = 20004, certs_dir: str = "certs", keys_dir: str = "keys"
) -> Dict[str, Any]:
    """Generate mTLS configuration without roles."""
    return {
        "server": {"host": "127.0.0.1", "port": port},
        "ssl": {
            "enabled": True,
            "cert_file": f"{certs_dir}/localhost_server.crt",
            "key_file": f"{keys_dir}/localhost_server.key",
            "ca_cert": f"{certs_dir}/mcp_proxy_adapter_ca_ca.crt",
            "verify_client": True,
            "client_cert_required": True
        },
        "security": {
            "enabled": True,
            "auth": {"enabled": True, "methods": ["certificate"]},
            "permissions": {"enabled": False}
        },
        "registration": {
            "enabled": False
        },
        "protocols": {
            "enabled": True,
            "allowed_protocols": ["https", "mtls"]
        }
    }


def generate_mtls_with_roles_config(
    port: int = 20005,
    certs_dir: str = "certs",
    keys_dir: str = "keys",
    roles_file: str = "configs/roles.json"
) -> Dict[str, Any]:
    """Generate mTLS configuration with roles."""
    return {
        "server": {"host": "127.0.0.1", "port": port},
        "ssl": {
            "enabled": True,
            "cert_file": f"{certs_dir}/localhost_server.crt",
            "key_file": f"{keys_dir}/localhost_server.key",
            "ca_cert": f"{certs_dir}/mcp_proxy_adapter_ca_ca.crt",
            "verify_client": True
        },
        "registration": {
            "enabled": True,
            "auth_method": "token",
            "server_url": "http://127.0.0.1:3004/proxy",
            "token": {"enabled": True, "token": "proxy_registration_token_123"},
            "proxy_info": {
                "name": "mcp_example_server",
                "capabilities": ["jsonrpc", "rest", "security", "proxy_registration"],
                "endpoints": {
                    "jsonrpc": "/api/jsonrpc",
                    "rest": "/cmd",
                    "health": "/health"
                }
            },
            "heartbeat": {"enabled": True, "interval": 30}
        },
        "security": {
            "enabled": True,
            "auth": {"enabled": True, "methods": ["certificate"]},
            "permissions": {"enabled": True, "roles_file": roles_file}
        },
        "protocols": {
            "enabled": True,
            "allowed_protocols": ["https", "mtls"]
        }
    }


def generate_roles_config() -> Dict[str, Any]:
    """Generate roles configuration for testing."""
    return {
        "admin": {
            "description": "Administrator role with full access",
            "permissions": [
                "read",
                "write",
                "execute",
                "delete",
                "admin",
                "register",
                "unregister",
                "heartbeat",
                "discover"
            ],
            "tokens": ["test-token-123"]
        },
        "user": {
            "description": "User role with limited access",
            "permissions": [
                "read",
                "execute",
                "register",
                "unregister",
                "heartbeat",
                "discover"
            ],
            "tokens": ["user-token-456"]
        },
        "readonly": {
            "description": "Read-only role",
            "permissions": [
                "read",
                "discover"
            ],
            "tokens": ["readonly-token-123"]
        },
        "guest": {
            "description": "Guest role with read-only access",
            "permissions": [
                "read",
                "discover"
            ],
            "tokens": ["guest-token-123"]
        },
        "proxy": {
            "description": "Proxy role for registration",
            "permissions": [
                "register",
                "unregister",
                "heartbeat",
                "discover"
            ],
            "tokens": ["proxy-token-123"]
        }
    }


def generate_all_configs(
    output_dir: str,
    certs_dir: str = "certs",
    keys_dir: str = "keys",
    roles_file: str = "configs/roles.json"
) -> None:
    """Generate all 6 configuration types and save them to files."""
    # Ensure output directory exists first
    os.makedirs(output_dir, exist_ok=True)

    configs = {
        "http_simple": generate_http_simple_config(20000, certs_dir, keys_dir),
        "http_token": generate_http_token_config(20001, certs_dir, keys_dir, roles_file),
        "https_simple": generate_https_simple_config(20002, certs_dir, keys_dir),
        "https_token": generate_https_token_config(20003, certs_dir, keys_dir),
        "mtls_no_roles": generate_mtls_no_roles_config(20004, certs_dir, keys_dir),
        "mtls_with_roles": generate_mtls_with_roles_config(20005, certs_dir, keys_dir, roles_file)
    }

    # Generate each configuration
    for name, config in configs.items():
        filename = os.path.join(output_dir, f"{name}.json")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"Generated: {filename}")

    # Generate roles configuration
    roles_config = generate_roles_config()

    # Create roles.json in the root directory (test environment root) for compatibility
    # When running as module, we need to create roles.json in the current working directory
    # This is the directory where the user is running the command from
    try:
        # Get the current working directory where the user is running the command
        current_dir = os.getcwd()
        root_roles_filename = os.path.join(current_dir, "roles.json")

        # Create roles.json in the current working directory
        with open(root_roles_filename, 'w', encoding='utf-8') as f:
            json.dump(roles_config, f, indent=2, ensure_ascii=False)
        print(f"Generated: {root_roles_filename}")

        # Also create a copy in the output directory for reference
        backup_roles_filename = os.path.join(output_dir, "roles_backup.json")
        with open(backup_roles_filename, 'w', encoding='utf-8') as f:
            json.dump(roles_config, f, indent=2, ensure_ascii=False)
        print(f"Generated backup: {backup_roles_filename}")

    except Exception as e:
        print(f"Warning: Could not create roles.json in current directory: {e}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Script directory: {os.path.dirname(os.path.abspath(__file__))}")

    # Also create roles.json in configs directory for reference
    roles_filename = os.path.join(output_dir, "roles.json")
    with open(roles_filename, 'w', encoding='utf-8') as f:
        json.dump(roles_config, f, indent=2, ensure_ascii=False)
    print(f"Generated: {roles_filename}")
    print(f"\nGenerated {len(configs)} configuration files and roles.json in {output_dir}")

    print("\n" + "=" * 60)
    print("✅ CONFIGURATION GENERATION COMPLETED SUCCESSFULLY")
    print("=" * 60)
    print("\n📋 NEXT STEPS:")
    print("1. Run security tests:")
    print("   python -m mcp_proxy_adapter.examples.run_security_tests")
    print("\n2. Start basic framework example:")
    print("   python -m mcp_proxy_adapter.examples.basic_framework.main --config configs/https_simple.json")
    print("\n3. Start full application example:")
    print("   python -m mcp_proxy_adapter.examples.full_application.main --config configs/mtls_with_roles.json")
    print("=" * 60)


def main() -> int:
    """Main function for command line execution."""
    parser = argparse.ArgumentParser(
        description="Generate test configurations for MCP Proxy Adapter"
    )
    parser.add_argument(
        "--output-dir",
        default="configs",
        help="Output directory for configuration files (default: configs)"
    )
    parser.add_argument(
        "--certs-dir",
        default="certs",
        help="Certificates directory (default: certs)"
    )
    parser.add_argument(
        "--keys-dir",
        default="keys",
        help="Keys directory (default: keys)"
    )
    parser.add_argument(
        "--roles-file",
        default="configs/roles.json",
        help="Roles file path (default: configs/roles.json)"
    )
    args = parser.parse_args()

    try:
        generate_all_configs(args.output_dir, args.certs_dir, args.keys_dir, args.roles_file)
        print("Configuration generation completed successfully!")
    except Exception as e:
        print(f"\n❌ CONFIGURATION GENERATION FAILED: {e}")
        print("=" * 60)
        print("\n🔧 TROUBLESHOOTING:")
        print("1. Check if output directory is writable")
        print("2. Verify JSON encoding support")
        print("3. Check available disk space")
        print("=" * 60)
        return 1
    return 0


if __name__ == "__main__":
    exit(main())
