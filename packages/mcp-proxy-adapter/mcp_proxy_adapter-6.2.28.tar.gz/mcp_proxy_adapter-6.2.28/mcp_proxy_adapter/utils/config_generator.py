"""
Configuration Generator Utility

This module provides utilities for generating comprehensive configuration files
that combine mcp_proxy_adapter and mcp_security_framework configurations.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Use standard logging instead of project logger to avoid circular imports
logger = logging.getLogger(__name__)


class ConfigGenerator:
    """
    Configuration generator for unified mcp_proxy_adapter and mcp_security_framework configs.
    
    Generates comprehensive configuration files with detailed comments and examples
    for both the proxy adapter and security framework components.
    """
    
    def __init__(self):
        """Initialize configuration generator."""
        self.template_config = self._get_template_config()
    
    def _get_template_config(self) -> Dict[str, Any]:
        """Get template configuration with all available options."""
        return {
            "server": {
                "host": "0.0.0.0",
                "port": 8000,
                "debug": False,
                "log_level": "INFO",
                "workers": 1,
                "reload": False
            },
            "ssl": {
                "enabled": False,
                "cert_file": None,
                "key_file": None,
                "ca_cert": None,
                "verify_client": False,
                "client_cert_required": False,
                "cipher_suites": ["TLS_AES_256_GCM_SHA384", "TLS_CHACHA20_POLY1305_SHA256"],
                "min_tls_version": "TLSv1.2",
                "max_tls_version": "1.3"
            },
            "security": {
                "framework": "mcp_security_framework",
                "enabled": True,
                "debug": False,
                "environment": "dev",
                "version": "1.0.0",
                
                "ssl": {
                    "enabled": False,
                    "cert_file": None,
                    "key_file": None,
                    "ca_cert_file": None,
                    "client_cert_file": None,
                    "client_key_file": None,
                    "verify_mode": "CERT_REQUIRED",
                    "min_tls_version": "TLSv1.2",
                    "max_tls_version": None,
                    "cipher_suite": None,
                    "check_hostname": True,
                    "check_expiry": True,
                    "expiry_warning_days": 30
                },
                
                "auth": {
                    "enabled": False,
                    "methods": [],
                    "api_keys": {},
                    "user_roles": {},
                    "jwt_secret": None,
                    "jwt_algorithm": "HS256",
                    "jwt_expiry_hours": 24,
                    "certificate_auth": False,
                    "certificate_roles_oid": "1.3.6.1.4.1.99999.1.1",
                    "certificate_permissions_oid": "1.3.6.1.4.1.99999.1.2",
                    "basic_auth": False,
                    "oauth2_config": None,
                    "public_paths": ["/health", "/docs", "/openapi.json"],
                    "security_headers": {
                        "X-Content-Type-Options": "nosniff",
                        "X-Frame-Options": "DENY",
                        "X-XSS-Protection": "1; mode=block",
                        "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
                    }
                },
                
                "certificates": {
                    "enabled": False,
                    "ca_cert_path": None,
                    "ca_key_path": None,
                    "cert_storage_path": "mcp_proxy_adapter/examples/certs",
                    "key_storage_path": "mcp_proxy_adapter/examples/keys",
                    "default_validity_days": 365,
                    "key_size": 2048,
                    "hash_algorithm": "sha256",
                    "crl_enabled": False,
                    "crl_path": None,
                    "crl_validity_days": 30,
                    "auto_renewal": False,
                    "renewal_threshold_days": 30
                },
                
                "permissions": {
                    "enabled": False,
                    "roles_file": None,
                    "default_role": "guest",
                    "admin_role": "admin",
                    "role_hierarchy": {},
                    "permission_cache_enabled": False,
                    "permission_cache_ttl": 300,
                    "wildcard_permissions": False,
                    "strict_mode": False,
                    "roles": {}
                },
                
                "rate_limit": {
                    "enabled": False,
                    "default_requests_per_minute": 60,
                    "default_requests_per_hour": 1000,
                    "burst_limit": 2,
                    "window_size_seconds": 60,
                    "storage_backend": "memory",
                    "redis_config": None,
                    "cleanup_interval": 300,
                    "exempt_paths": ["/health", "/docs", "/openapi.json"],
                    "exempt_roles": ["admin"]
                },
                
                "logging": {
                    "enabled": True,
                    "level": "INFO",
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    "date_format": "%Y-%m-%d %H:%M:%S",
                    "file_path": "./logs/security.log",
                    "max_file_size": 10,
                    "backup_count": 5,
                    "console_output": True,
                    "json_format": False,
                    "include_timestamp": True,
                    "include_level": True,
                    "include_module": True
                }
            },
            
            "registration": {
                "enabled": False,
                "server_url": "https://proxy-registry.example.com",
                "auth_method": "certificate",
                "certificate": {
                    "enabled": False,
                    "cert_file": "mcp_proxy_adapter/examples/certs/proxy_client.crt",
                    "key_file": "mcp_proxy_adapter/examples/keys/proxy_client.key",
                    "ca_cert_file": "mcp_proxy_adapter/examples/certs/ca.crt",
                    "verify_server": True
                },
                "token": {
                    "enabled": False,
                    "token": "proxy_registration_token_123",
                    "token_type": "bearer",
                    "refresh_interval": 3600
                },
                "api_key": {
                    "enabled": False,
                    "key": "proxy_api_key_456",
                    "key_header": "X-Proxy-API-Key"
                },
                "proxy_info": {
                    "name": "mcp_proxy_adapter",
                    "version": "1.0.0",
                    "description": "MCP Proxy Adapter with security framework",
                    "capabilities": ["jsonrpc", "rest", "security", "certificates"],
                    "endpoints": {
                        "jsonrpc": "/api/jsonrpc",
                        "rest": "/cmd",
                        "health": "/health"
                    }
                },
                "heartbeat": {
                    "enabled": True,
                    "interval": 300,
                    "timeout": 30,
                    "retry_attempts": 3,
                    "retry_delay": 60
                },
                "auto_discovery": {
                    "enabled": False,
                    "discovery_urls": [],
                    "discovery_interval": 3600,
                    "register_on_discovery": True
                }
            },
            
            "logging": {
                "level": "INFO",
                "console_output": True,
                "file_output": False,
                "file_path": None,
                "max_file_size": 10,
                "backup_count": 5,
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            
            "commands": {
                "auto_discovery": True,
                "commands_directory": "./commands",
                "builtin_commands": ["echo", "health", "config"],
                "custom_commands": [],
                "command_timeout": 30
            },
            
            "hooks": {
                "enabled": True,
                "application_hooks": {
                    "on_startup": [],
                    "on_shutdown": [],
                    "before_request": [],
                    "after_request": [],
                    "on_error": []
                },
                "command_hooks": {
                    "before_echo_command": [],
                    "after_echo_command": [],
                    "before_health_command": [],
                    "after_health_command": [],
                    "before_config_command": [],
                    "after_config_command": []
                }
            },
            
            "protocols": {
                "enabled": True,
                "allowed_protocols": ["http", "https"],
                "default_protocol": "http",
                "strict_mode": False
            }
        }
    
    def generate_config_with_comments(self, config_type: str = "full") -> str:
        """
        Generate configuration with detailed comments.
        
        Args:
            config_type: Type of configuration to generate
                - "full": Complete configuration with all options
                - "minimal": Minimal working configuration
                - "secure": Secure configuration with all security features
                - "development": Development configuration with debug enabled
                - "basic_http": Basic HTTP configuration
                - "http_token": HTTP with token authentication
                - "https": HTTPS configuration
                - "https_token": HTTPS with token authentication
                - "mtls": mTLS configuration
                - "optional_ssl": Configuration with optional SSL
                - "optional_auth": Configuration with optional authentication
                - "optional_proxy_reg": Configuration with optional proxy registration
                - "custom": Custom configuration with specified features

        Returns:
            JSON configuration string with comments
        """
        config = self._get_config_by_type(config_type)
        
        # Convert to JSON with comments
        json_str = json.dumps(config, indent=2, ensure_ascii=False)
        
        # Add comments
        commented_config = self._add_comments(json_str, config_type)
        
        return commented_config
    
    def _get_config_by_type(self, config_type: str) -> Dict[str, Any]:
        """Get configuration based on type."""
        base_config = self.template_config.copy()
        
        if config_type == "minimal":
            return self._get_minimal_config(base_config)
        elif config_type == "secure":
            return self._get_secure_config(base_config)
        elif config_type == "development":
            return self._get_development_config(base_config)
        elif config_type == "basic_http":
            return self._get_basic_http_config(base_config)
        elif config_type == "http_token":
            return self._get_http_token_config(base_config)
        elif config_type == "https":
            return self._get_https_config(base_config)
        elif config_type == "https_token":
            return self._get_https_token_config(base_config)
        elif config_type == "https_no_protocol_middleware":
            return self._get_https_no_protocol_middleware_config(base_config)
        elif config_type == "mtls":
            return self._get_mtls_config(base_config)
        elif config_type == "mtls_no_protocol_middleware":
            return self._get_mtls_no_protocol_middleware_config(base_config)
        elif config_type == "optional_ssl":
            return self._get_optional_ssl_config(base_config)
        elif config_type == "optional_auth":
            return self._get_optional_auth_config(base_config)
        elif config_type == "optional_proxy_reg":
            return self._get_optional_proxy_reg_config(base_config)
        elif config_type == "custom":
            return self._get_custom_config(base_config)
        else:  # full
            return base_config
    
    def _get_minimal_config(self, base_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get minimal working configuration."""
        config = base_config.copy()
        
        # Disable security for minimal config
        config["security"]["enabled"] = False
        config["security"]["auth"]["enabled"] = False
        config["security"]["permissions"]["enabled"] = False
        config["security"]["rate_limit"]["enabled"] = False
        
        # Disable registration for minimal config
        config["registration"]["enabled"] = False
        
        # Keep only essential settings
        config["server"]["port"] = 8000
        config["server"]["debug"] = False
        
        return config
    
    def _get_basic_http_config(self, base_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get basic HTTP configuration."""
        config = base_config.copy()
        
        # Basic HTTP settings
        config["server"]["port"] = 8000
        config["ssl"]["enabled"] = False
        config["security"]["ssl"]["enabled"] = False
        config["security"]["auth"]["enabled"] = False
        config["security"]["permissions"]["enabled"] = False
        config["security"]["permissions"]["roles_file"] = None
        config["protocols"]["enabled"] = True
        config["protocols"]["allowed_protocols"] = ["http"]
        config["protocols"]["default_protocol"] = "http"

        # Enable local proxy registration by default for examples
        config["registration"]["enabled"] = True
        config["registration"]["auth_method"] = "token"
        config["registration"]["token"]["enabled"] = True
        config["registration"]["token"]["token"] = "proxy_registration_token_123"
        config["registration"]["server_url"] = "http://127.0.0.1:3004/proxy"
        config["registration"]["proxy_info"]["name"] = "mcp_example_server"
        config["registration"]["proxy_info"]["capabilities"] = [
            "jsonrpc", "rest", "security", "proxy_registration"
        ]
        config["registration"]["heartbeat"]["enabled"] = True
        config["registration"]["heartbeat"]["interval"] = 30
        
        return config
    
    def _get_http_token_config(self, base_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get HTTP with token authentication configuration."""
        config = base_config.copy()
        
        # HTTP with token auth
        config["server"]["port"] = 8001
        config["ssl"]["enabled"] = False
        config["security"]["ssl"]["enabled"] = False
        config["security"]["auth"]["enabled"] = True
        config["security"]["auth"]["methods"] = ["api_key"]
        config["security"]["auth"]["api_keys"] = {
            "test-token-123": {
                "roles": ["admin"],
                "permissions": ["*"],
                "expires": None
            },
            "user-token-456": {
                "roles": ["user"],
                "permissions": ["read", "execute"],
                "expires": None
            }
        }
        config["security"]["permissions"]["enabled"] = True
        config["security"]["permissions"]["roles_file"] = "mcp_proxy_adapter/examples/server_configs/roles.json"
        config["protocols"]["enabled"] = True
        config["protocols"]["allowed_protocols"] = ["http"]
        config["protocols"]["default_protocol"] = "http"
        
        return config
    
    def _get_https_config(self, base_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get HTTPS configuration."""
        config = base_config.copy()
        
        # HTTPS settings
        config["server"]["port"] = 8443
        config["ssl"]["enabled"] = True
        config["ssl"]["cert_file"] = "mcp_proxy_adapter/examples/certs/server_cert.pem"
        config["ssl"]["key_file"] = "mcp_proxy_adapter/examples/certs/server_key.pem"
        config["ssl"]["ca_cert"] = "mcp_proxy_adapter/examples/certs/ca_cert.pem"
        
        config["security"]["ssl"]["enabled"] = True
        config["security"]["ssl"]["cert_file"] = "mcp_proxy_adapter/examples/certs/server_cert.pem"
        config["security"]["ssl"]["key_file"] = "mcp_proxy_adapter/examples/certs/server_key.pem"
        config["security"]["ssl"]["ca_cert_file"] = "mcp_proxy_adapter/examples/certs/ca_cert.pem"
        
        config["security"]["auth"]["enabled"] = False
        config["security"]["permissions"]["enabled"] = False
        config["security"]["permissions"]["roles_file"] = None
        config["protocols"]["enabled"] = True
        config["protocols"]["allowed_protocols"] = ["http", "https"]
        config["protocols"]["default_protocol"] = "https"
        
        return config
    
    def _get_https_token_config(self, base_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get HTTPS with token authentication configuration."""
        config = base_config.copy()
        
        # HTTPS with token auth
        config["server"]["port"] = 8444
        config["ssl"]["enabled"] = True
        config["ssl"]["cert_file"] = "mcp_proxy_adapter/examples/certs/server_cert.pem"
        config["ssl"]["key_file"] = "mcp_proxy_adapter/examples/certs/server_key.pem"
        config["ssl"]["ca_cert"] = "mcp_proxy_adapter/examples/certs/ca_cert.pem"
        
        config["security"]["ssl"]["enabled"] = True
        config["security"]["ssl"]["cert_file"] = "mcp_proxy_adapter/examples/certs/server_cert.pem"
        config["security"]["ssl"]["key_file"] = "mcp_proxy_adapter/examples/certs/server_key.pem"
        config["security"]["ssl"]["ca_cert_file"] = "mcp_proxy_adapter/examples/certs/ca_cert.pem"
        
        config["security"]["auth"]["enabled"] = True
        config["security"]["auth"]["methods"] = ["api_key"]
        config["security"]["auth"]["api_keys"] = {
            "test-token-123": {
                "roles": ["admin"],
                "permissions": ["*"],
                "expires": None
            },
            "user-token-456": {
                "roles": ["user"],
                "permissions": ["read", "execute"],
                "expires": None
            }
        }
        config["security"]["permissions"]["enabled"] = True
        config["security"]["permissions"]["roles_file"] = "mcp_proxy_adapter/examples/server_configs/roles.json"
        config["protocols"]["enabled"] = True
        config["protocols"]["allowed_protocols"] = ["http", "https"]
        config["protocols"]["default_protocol"] = "https"
        
        return config
    
    def _get_mtls_config(self, base_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get mTLS configuration."""
        config = base_config.copy()
        
        # mTLS settings
        config["server"]["port"] = 8445
        config["ssl"]["enabled"] = True
        config["ssl"]["cert_file"] = "mcp_proxy_adapter/examples/certs/server_cert.pem"
        config["ssl"]["key_file"] = "mcp_proxy_adapter/examples/certs/server_key.pem"
        config["ssl"]["ca_cert"] = "mcp_proxy_adapter/examples/certs/ca_cert.pem"
        config["ssl"]["verify_client"] = True
        config["ssl"]["client_cert_required"] = True
        
        config["security"]["ssl"]["enabled"] = True
        config["security"]["ssl"]["cert_file"] = "mcp_proxy_adapter/examples/certs/server_cert.pem"
        config["security"]["ssl"]["key_file"] = "mcp_proxy_adapter/examples/certs/server_key.pem"
        config["security"]["ssl"]["ca_cert_file"] = "mcp_proxy_adapter/examples/certs/ca_cert.pem"
        config["security"]["ssl"]["client_cert_file"] = "mcp_proxy_adapter/examples/certs/client_cert.pem"
        config["security"]["ssl"]["client_key_file"] = "mcp_proxy_adapter/examples/certs/client_key.pem"
        config["security"]["ssl"]["verify_mode"] = "CERT_REQUIRED"
        
        config["security"]["auth"]["enabled"] = True
        config["security"]["auth"]["methods"] = ["certificate"]
        config["security"]["auth"]["certificate_auth"] = True
        config["security"]["permissions"]["enabled"] = True
        config["security"]["permissions"]["roles_file"] = "mcp_proxy_adapter/examples/server_configs/roles.json"
        config["protocols"]["enabled"] = True
        config["protocols"]["allowed_protocols"] = ["https", "mtls"]
        config["protocols"]["default_protocol"] = "https"
        
        return config
    
    def _get_https_no_protocol_middleware_config(self, base_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get HTTPS configuration without ProtocolMiddleware."""
        config = base_config.copy()
        
        # HTTPS settings
        config["server"]["port"] = 8445
        config["ssl"]["enabled"] = True
        config["ssl"]["cert_file"] = "mcp_proxy_adapter/examples/certs/server_cert.pem"
        config["ssl"]["key_file"] = "mcp_proxy_adapter/examples/certs/server_key.pem"
        config["ssl"]["ca_cert"] = "mcp_proxy_adapter/examples/certs/ca_cert.pem"
        
        config["security"]["ssl"]["enabled"] = True
        config["security"]["ssl"]["cert_file"] = "mcp_proxy_adapter/examples/certs/server_cert.pem"
        config["security"]["ssl"]["key_file"] = "mcp_proxy_adapter/examples/certs/server_key.pem"
        config["security"]["ssl"]["ca_cert_file"] = "mcp_proxy_adapter/examples/certs/ca_cert.pem"
        
        config["security"]["auth"]["enabled"] = True
        config["security"]["auth"]["methods"] = ["api_key"]
        config["security"]["auth"]["api_keys"] = {
            "test-token-123": {
                "roles": ["admin"],
                "permissions": ["*"],
                "expires": None
            },
            "user-token-456": {
                "roles": ["user"],
                "permissions": ["read", "execute"],
                "expires": None
            }
        }
        config["security"]["permissions"]["enabled"] = True
        config["security"]["permissions"]["roles_file"] = "mcp_proxy_adapter/examples/server_configs/roles.json"
        config["protocols"]["enabled"] = False  # Disable ProtocolMiddleware
        
        return config
    
    def _get_mtls_no_protocol_middleware_config(self, base_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get mTLS configuration without ProtocolMiddleware."""
        config = base_config.copy()
        
        # mTLS settings
        config["server"]["port"] = 8447
        config["ssl"]["enabled"] = True
        config["ssl"]["cert_file"] = "mcp_proxy_adapter/examples/certs/server_cert.pem"
        config["ssl"]["key_file"] = "mcp_proxy_adapter/examples/certs/server_key.pem"
        config["ssl"]["ca_cert"] = "mcp_proxy_adapter/examples/certs/ca_cert.pem"
        config["ssl"]["verify_client"] = True
        config["ssl"]["client_cert_required"] = True
        
        config["security"]["ssl"]["enabled"] = True
        config["security"]["ssl"]["cert_file"] = "mcp_proxy_adapter/examples/certs/server_cert.pem"
        config["security"]["ssl"]["key_file"] = "mcp_proxy_adapter/examples/certs/server_key.pem"
        config["security"]["ssl"]["ca_cert_file"] = "mcp_proxy_adapter/examples/certs/ca_cert.pem"
        config["security"]["ssl"]["client_cert_file"] = "mcp_proxy_adapter/examples/certs/client_cert.pem"
        config["security"]["ssl"]["client_key_file"] = "mcp_proxy_adapter/examples/certs/client_key.pem"
        config["security"]["ssl"]["verify_mode"] = "CERT_REQUIRED"
        
        config["security"]["auth"]["enabled"] = True
        config["security"]["auth"]["methods"] = ["certificate"]
        config["security"]["auth"]["certificate_auth"] = True
        config["security"]["permissions"]["enabled"] = True
        config["security"]["permissions"]["roles_file"] = "mcp_proxy_adapter/examples/server_configs/roles.json"
        config["protocols"]["enabled"] = False  # Disable ProtocolMiddleware
        
        return config
    
    def _get_optional_ssl_config(self, base_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get configuration with optional SSL support."""
        config = base_config.copy()
        
        # Server configuration
        config["server"]["port"] = 8000
        
        # SSL configuration - can be enabled/disabled via environment or config
        config["ssl"]["enabled"] = False  # Default disabled, can be enabled
        config["ssl"]["cert_file"] = "mcp_proxy_adapter/examples/certs/server_cert.pem"
        config["ssl"]["key_file"] = "mcp_proxy_adapter/examples/certs/server_key.pem"
        config["ssl"]["ca_cert"] = "mcp_proxy_adapter/examples/certs/ca_cert.pem"
        config["ssl"]["verify_client"] = False  # Can be enabled for mTLS
        
        # Security framework SSL - mirrors main SSL config
        config["security"]["ssl"]["enabled"] = False  # Default disabled
        config["security"]["ssl"]["cert_file"] = "mcp_proxy_adapter/examples/certs/server_cert.pem"
        config["security"]["ssl"]["key_file"] = "mcp_proxy_adapter/examples/certs/server_key.pem"
        config["security"]["ssl"]["ca_cert_file"] = "mcp_proxy_adapter/examples/certs/ca_cert.pem"
        config["security"]["ssl"]["client_cert_file"] = "mcp_proxy_adapter/examples/certs/client_cert.pem"
        config["security"]["ssl"]["client_key_file"] = "mcp_proxy_adapter/examples/certs/client_key.key"
        
        # Protocols support both HTTP and HTTPS
        config["protocols"]["enabled"] = True
        config["protocols"]["allowed_protocols"] = ["http", "https"]
        config["protocols"]["default_protocol"] = "http"
        
        # Enable proxy registration with token auth
        config["registration"]["enabled"] = True
        config["registration"]["auth_method"] = "token"
        config["registration"]["token"]["enabled"] = True
        config["registration"]["token"]["token"] = "proxy_registration_token_123"
        config["registration"]["server_url"] = "http://127.0.0.1:3004/proxy"
        
        return config
    
    def _get_optional_auth_config(self, base_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get configuration with optional authentication support."""
        config = base_config.copy()
        
        # Server configuration
        config["server"]["port"] = 8001
        
        # SSL disabled by default
        config["ssl"]["enabled"] = False
        config["security"]["ssl"]["enabled"] = False
        
        # Authentication configuration - can be enabled/disabled
        config["security"]["auth"]["enabled"] = False  # Default disabled
        config["security"]["auth"]["methods"] = ["api_key", "jwt"]  # Available methods
        
        # API keys configuration
        config["security"]["auth"]["api_keys"] = {
            "admin-token": {
                "roles": ["admin"],
                "permissions": ["*"],
                "expires": None
            },
            "user-token": {
                "roles": ["user"],
                "permissions": ["read", "execute"],
                "expires": None
            },
            "guest-token": {
                "roles": ["guest"],
                "permissions": ["read"],
                "expires": None
            }
        }
        
        # JWT configuration
        config["security"]["auth"]["jwt_secret"] = "your_jwt_secret_here"
        config["security"]["auth"]["jwt_algorithm"] = "HS256"
        config["security"]["auth"]["jwt_expiry_hours"] = 24
        
        # User roles mapping
        config["security"]["auth"]["user_roles"] = {
            "admin": ["admin"],
            "user": ["user"],
            "guest": ["guest"]
        }
        
        # Permissions configuration - can be enabled/disabled
        config["security"]["permissions"]["enabled"] = False  # Default disabled
        config["security"]["permissions"]["roles_file"] = "mcp_proxy_adapter/examples/server_configs/roles.json"
        config["security"]["permissions"]["default_role"] = "guest"
        config["security"]["permissions"]["admin_role"] = "admin"
        
        # Protocols
        config["protocols"]["enabled"] = True
        config["protocols"]["allowed_protocols"] = ["http"]
        config["protocols"]["default_protocol"] = "http"
        
        # Enable proxy registration
        config["registration"]["enabled"] = True
        config["registration"]["auth_method"] = "token"
        config["registration"]["token"]["enabled"] = True
        config["registration"]["token"]["token"] = "proxy_registration_token_123"
        
        return config
    
    def _get_optional_proxy_reg_config(self, base_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get configuration with optional proxy registration support."""
        config = base_config.copy()
        
        # Server configuration
        config["server"]["port"] = 8002
        
        # SSL disabled by default
        config["ssl"]["enabled"] = False
        config["security"]["ssl"]["enabled"] = False
        
        # Authentication disabled by default
        config["security"]["auth"]["enabled"] = False
        config["security"]["permissions"]["enabled"] = False
        
        # Proxy registration configuration - can be enabled/disabled
        config["registration"]["enabled"] = False  # Default disabled
        config["registration"]["server_url"] = "http://127.0.0.1:3004/proxy"
        config["registration"]["server_id"] = "mcp_proxy_adapter"
        config["registration"]["server_name"] = "MCP Proxy Adapter"
        config["registration"]["description"] = "JSON-RPC API for interacting with MCP Proxy"
        
        # Multiple authentication methods for proxy registration
        config["registration"]["auth_method"] = "token"  # Default method
        
        # Token authentication
        config["registration"]["token"]["enabled"] = True
        config["registration"]["token"]["token"] = "proxy_registration_token_123"
        config["registration"]["token"]["token_type"] = "bearer"
        config["registration"]["token"]["refresh_interval"] = 3600
        
        # Certificate authentication
        config["registration"]["certificate"]["enabled"] = False
        config["registration"]["certificate"]["cert_file"] = "mcp_proxy_adapter/examples/certs/proxy_client.crt"
        config["registration"]["certificate"]["key_file"] = "mcp_proxy_adapter/examples/keys/proxy_client.key"
        config["registration"]["certificate"]["ca_cert_file"] = "mcp_proxy_adapter/examples/certs/ca.crt"
        config["registration"]["certificate"]["verify_server"] = True
        
        # API key authentication
        config["registration"]["api_key"]["enabled"] = False
        config["registration"]["api_key"]["key"] = "proxy_api_key_456"
        config["registration"]["api_key"]["key_header"] = "X-Proxy-API-Key"
        
        # Proxy information
        config["registration"]["proxy_info"]["name"] = "mcp_proxy_adapter"
        config["registration"]["proxy_info"]["version"] = "1.0.0"
        config["registration"]["proxy_info"]["description"] = "MCP Proxy Adapter with optional features"
        config["registration"]["proxy_info"]["capabilities"] = ["jsonrpc", "rest", "optional_features"]
        config["registration"]["proxy_info"]["endpoints"] = {
            "jsonrpc": "/api/jsonrpc",
            "rest": "/cmd",
            "health": "/health"
        }
        
        # Heartbeat configuration
        config["registration"]["heartbeat"]["enabled"] = True
        config["registration"]["heartbeat"]["interval"] = 300
        config["registration"]["heartbeat"]["timeout"] = 30
        config["registration"]["heartbeat"]["retry_attempts"] = 3
        config["registration"]["heartbeat"]["retry_delay"] = 60
        
        # Auto-discovery
        config["registration"]["auto_discovery"]["enabled"] = False
        config["registration"]["auto_discovery"]["discovery_urls"] = []
        config["registration"]["auto_discovery"]["discovery_interval"] = 3600
        config["registration"]["auto_discovery"]["register_on_discovery"] = True
        
        # Protocols
        config["protocols"]["enabled"] = True
        config["protocols"]["allowed_protocols"] = ["http"]
        config["protocols"]["default_protocol"] = "http"
        
        return config
    
    def _get_custom_config(self, base_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get custom configuration with configurable features."""
        config = base_config.copy()
        
        # Server configuration
        config["server"]["port"] = 8003
        
        # SSL configuration - configurable
        config["ssl"]["enabled"] = False  # Can be enabled via config
        config["ssl"]["cert_file"] = "mcp_proxy_adapter/examples/certs/server_cert.pem"
        config["ssl"]["key_file"] = "mcp_proxy_adapter/examples/certs/server_key.pem"
        config["ssl"]["ca_cert"] = "mcp_proxy_adapter/examples/certs/ca_cert.pem"
        config["ssl"]["verify_client"] = False  # Can be enabled for mTLS
        
        # Security framework - configurable
        config["security"]["enabled"] = False  # Can be enabled via config
        config["security"]["ssl"]["enabled"] = False  # Mirrors main SSL
        config["security"]["ssl"]["cert_file"] = "mcp_proxy_adapter/examples/certs/server_cert.pem"
        config["security"]["ssl"]["key_file"] = "mcp_proxy_adapter/examples/certs/server_key.pem"
        config["security"]["ssl"]["ca_cert_file"] = "mcp_proxy_adapter/examples/certs/ca_cert.pem"
        
        # Authentication - configurable
        config["security"]["auth"]["enabled"] = False  # Can be enabled via config
        config["security"]["auth"]["methods"] = ["api_key", "jwt", "certificate"]
        config["security"]["auth"]["api_keys"] = {
            "custom-admin": {
                "roles": ["admin"],
                "permissions": ["*"],
                "expires": None
            },
            "custom-user": {
                "roles": ["user"],
                "permissions": ["read", "execute"],
                "expires": None
            }
        }
        
        # Permissions - configurable
        config["security"]["permissions"]["enabled"] = False  # Can be enabled via config
        config["security"]["permissions"]["roles_file"] = "mcp_proxy_adapter/examples/server_configs/roles.json"
        
        # Rate limiting - configurable
        config["security"]["rate_limit"]["enabled"] = False  # Can be enabled via config
        config["security"]["rate_limit"]["default_requests_per_minute"] = 60
        config["security"]["rate_limit"]["default_requests_per_hour"] = 1000
        
        # Certificates - configurable
        config["security"]["certificates"]["enabled"] = False  # Can be enabled via config
        config["security"]["certificates"]["cert_storage_path"] = "./certs"
        config["security"]["certificates"]["key_storage_path"] = "./keys"
        
        # Proxy registration - configurable
        config["registration"]["enabled"] = False  # Can be enabled via config
        config["registration"]["auth_method"] = "token"
        config["registration"]["token"]["enabled"] = True
        config["registration"]["token"]["token"] = "custom_proxy_token"
        
        # Protocols
        config["protocols"]["enabled"] = True
        config["protocols"]["allowed_protocols"] = ["http", "https"]
        config["protocols"]["default_protocol"] = "http"
        
        return config
    
    def _get_secure_config(self, base_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get secure configuration with all security features enabled."""
        config = base_config.copy()
        
        # Enable all security features
        config["security"]["enabled"] = True
        config["security"]["ssl"]["enabled"] = True
        config["security"]["auth"]["enabled"] = True
        config["security"]["permissions"]["enabled"] = True
        config["security"]["rate_limit"]["enabled"] = True
        
        # Enable registration with certificate auth
        config["registration"]["enabled"] = True
        config["registration"]["auth_method"] = "certificate"
        config["registration"]["certificate"]["enabled"] = True
        
        # Set secure defaults
        config["security"]["ssl"]["min_tls_version"] = "TLSv1.2"
        config["security"]["auth"]["methods"] = ["api_key", "jwt"]
        config["security"]["permissions"]["strict_mode"] = True
        config["security"]["rate_limit"]["burst_limit"] = 1
        
        return config
    
    def _get_development_config(self, base_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get development configuration with debug enabled."""
        config = base_config.copy()
        
        # Enable debug features
        config["server"]["debug"] = True
        config["security"]["debug"] = True
        config["logging"]["level"] = "DEBUG"
        
        # Enable registration with token auth for development
        config["registration"]["enabled"] = True
        config["registration"]["auth_method"] = "token"
        config["registration"]["token"]["enabled"] = True
        
        # Relax security for development
        config["security"]["rate_limit"]["default_requests_per_minute"] = 1000
        config["security"]["permissions"]["strict_mode"] = False
        
        return config
    
    def _add_comments(self, json_str: str, config_type: str) -> str:
        """Add comments to JSON configuration."""
        comments = self._get_comments_for_type(config_type)
        
        # Add header comment
        commented_config = f"""/**
 * MCP Proxy Adapter Configuration
 * 
 * This configuration file combines settings for both mcp_proxy_adapter
 * and mcp_security_framework in a unified format.
 * 
 * Configuration Type: {config_type.title()}
 * Generated by: ConfigGenerator
 * 
 * IMPORTANT: This is a template configuration. Please customize it
 * according to your specific requirements and security needs.
 */

"""
        
        # Add section comments
        for section, comment in comments.items():
            if section in json_str:
                # Find the section and add comment before it
                section_start = json_str.find(f'"{section}":')
                if section_start != -1:
                    # Find the line start
                    line_start = json_str.rfind('\n', 0, section_start) + 1
                    json_str = (
                        json_str[:line_start] +
                        f"  // {comment}\n" +
                        json_str[line_start:]
                    )
        
        return commented_config + json_str
    
    def _get_comments_for_type(self, config_type: str) -> Dict[str, str]:
        """Get comments for configuration sections."""
        base_comments = {
            "server": "Server configuration for FastAPI application",
            "ssl": "SSL/TLS configuration for secure connections",
            "security": "Security framework configuration (mcp_security_framework)",
            "registration": "Proxy registration configuration for secure proxy discovery",
            "logging": "Logging configuration for the application",
            "commands": "Command management and discovery settings",
            "hooks": "Application and command hooks configuration",
            "protocols": "Protocol endpoints and settings"
        }
        
        if config_type == "minimal":
            base_comments["security"] = "Security framework configuration (disabled for minimal setup)"
            base_comments["registration"] = "Proxy registration configuration (disabled for minimal setup)"
        elif config_type == "secure":
            base_comments["security"] = "Security framework configuration (all features enabled)"
            base_comments["registration"] = "Proxy registration configuration (certificate authentication enabled)"
        elif config_type == "development":
            base_comments["security"] = "Security framework configuration (development mode with relaxed settings)"
            base_comments["registration"] = "Proxy registration configuration (token authentication for development)"
        elif config_type in ["basic_http", "http_token"]:
            base_comments["ssl"] = "SSL/TLS configuration (disabled for HTTP)"
            base_comments["security"] = f"Security framework configuration ({config_type} mode)"
        elif config_type in ["https", "https_token"]:
            base_comments["ssl"] = "SSL/TLS configuration (enabled for HTTPS)"
            base_comments["security"] = f"Security framework configuration ({config_type} mode)"
        elif config_type == "mtls":
            base_comments["ssl"] = "SSL/TLS configuration (enabled for mTLS with client certificate verification)"
            base_comments["security"] = "Security framework configuration (mTLS mode with certificate authentication)"
        elif config_type == "https_no_protocol_middleware":
            base_comments["ssl"] = "SSL/TLS configuration (enabled for HTTPS without ProtocolMiddleware)"
            base_comments["security"] = "Security framework configuration (HTTPS mode without ProtocolMiddleware)"
        elif config_type == "mtls_no_protocol_middleware":
            base_comments["ssl"] = "SSL/TLS configuration (enabled for mTLS without ProtocolMiddleware)"
            base_comments["security"] = "Security framework configuration (mTLS mode without ProtocolMiddleware)"
        elif config_type == "optional_ssl":
            base_comments["ssl"] = "SSL/TLS configuration (optional, can be enabled/disabled)"
            base_comments["security"] = "Security framework SSL configuration (mirrors main SSL)"
        elif config_type == "optional_auth":
            base_comments["ssl"] = "SSL/TLS configuration (disabled for optional auth)"
            base_comments["security"] = "Security framework authentication configuration (optional, can be enabled/disabled)"
        elif config_type == "optional_proxy_reg":
            base_comments["ssl"] = "SSL/TLS configuration (disabled for optional proxy reg)"
            base_comments["security"] = "Security framework proxy registration configuration (optional, can be enabled/disabled)"
        elif config_type == "custom":
            base_comments["ssl"] = "SSL/TLS configuration (configurable)"
            base_comments["security"] = "Security framework configuration (configurable)"
            base_comments["registration"] = "Proxy registration configuration (configurable)"
            base_comments["protocols"] = "Protocol endpoints and settings (configurable)"
        
        return base_comments
    
    def generate_config_file(self, output_path: str, config_type: str = "full") -> None:
        """
        Generate configuration file and save to disk.

        Args:
            output_path: Path to save the configuration file
            config_type: Type of configuration to generate
        """
        try:
            # Get configuration without comments for file generation
            config = self._get_config_by_type(config_type)
            
            # Create directory if it doesn't exist
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write configuration file as clean JSON
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Configuration file generated: {output_path}")
            logger.info(f"Configuration type: {config_type}")
            
        except Exception as e:
            logger.error(f"Failed to generate configuration file: {e}")
            raise
    
    def generate_all_configs(self, output_dir: str) -> None:
        """
        Generate all configuration types.
        
        Args:
            output_dir: Directory to save configuration files
        """
        config_types = [
            "minimal", "development", "secure", "full",
            "basic_http", "http_token", "https", "https_token", "mtls",
            "https_no_protocol_middleware", "mtls_no_protocol_middleware",
            "optional_ssl", "optional_auth", "optional_proxy_reg", "custom"
        ]
        
        for config_type in config_types:
            output_path = Path(output_dir) / f"config_{config_type}.json"
            self.generate_config_file(str(output_path), config_type)
        
        logger.info(f"Generated {len(config_types)} configuration files in {output_dir}")


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate MCP Proxy Adapter configuration files")
    parser.add_argument("--type", 
                       choices=["minimal", "development", "secure", "full", 
                               "basic_http", "http_token", "https", "https_token", "mtls",
                               "https_no_protocol_middleware", "mtls_no_protocol_middleware",
                               "optional_ssl", "optional_auth", "optional_proxy_reg", "custom"], 
                       default="full", help="Configuration type to generate")
    parser.add_argument("--output", default="./config.json", 
                       help="Output file path")
    parser.add_argument("--all", action="store_true", 
                       help="Generate all configuration types")
    parser.add_argument("--output-dir", default="./configs", 
                       help="Output directory for all configs")
    
    args = parser.parse_args()
    
    generator = ConfigGenerator()
    
    if args.all:
        generator.generate_all_configs(args.output_dir)
    else:
        generator.generate_config_file(args.output, args.type)


if __name__ == "__main__":
    main()
