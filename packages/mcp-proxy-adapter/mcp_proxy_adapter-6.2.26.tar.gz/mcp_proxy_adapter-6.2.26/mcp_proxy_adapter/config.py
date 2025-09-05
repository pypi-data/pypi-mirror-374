"""
Module for microservice configuration management.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

import json
import os
from typing import Any, Dict, Optional, List


class Config:
    """
    Configuration management class for the microservice.
    Allows loading settings from configuration file and environment variables.
    Supports optional features that can be enabled/disabled.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration.

        Args:
            config_path: Path to configuration file. If not specified,
                        "./config.json" is used.
        """
        self.config_path = config_path or "./config.json"
        self.config_data: Dict[str, Any] = {}
        self.load_config()

    def load_config(self) -> None:
        """
        Load configuration from file and environment variables.
        """
        # Set default config values
        self.config_data = {
            "server": {
                "host": "0.0.0.0",
                "port": 8000,
                "debug": False,
                "log_level": "INFO"
            },
            "logging": {
                "level": "INFO",
                "file": None,
                "log_dir": "./logs",
                "log_file": "mcp_proxy_adapter.log",
                "error_log_file": "mcp_proxy_adapter_error.log",
                "access_log_file": "mcp_proxy_adapter_access.log",
                "max_file_size": "10MB",
                "backup_count": 5,
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "date_format": "%Y-%m-%d %H:%M:%S",
                "console_output": True,
                "file_output": True
            },
            "commands": {
                "auto_discovery": True,
                "commands_directory": "./commands",
                "catalog_directory": "./catalog",
                "plugin_servers": [],
                "auto_install_dependencies": True,
                "enabled_commands": ["health", "echo", "list", "help"],
                "disabled_commands": [],
                "custom_commands_path": "./commands"
            },
            "ssl": {
                "enabled": False,
                "mode": "https_only",
                "cert_file": None,
                "key_file": None,
                "ca_cert": None,
                "verify_client": False,
                "client_cert_required": False,
                "cipher_suites": [
                    "TLS_AES_256_GCM_SHA384",
                    "TLS_CHACHA20_POLY1305_SHA256"
                ],
                "min_tls_version": "TLSv1.2",
                "max_tls_version": "1.3",
                "token_auth": {
                    "enabled": False,
                    "header_name": "Authorization",
                    "token_prefix": "Bearer",
                    "tokens_file": "tokens.json",
                    "token_expiry": 3600,
                    "jwt_secret": "",
                    "jwt_algorithm": "HS256"
                }
            },
            "roles": {
                "enabled": False,
                "config_file": None,
                "default_policy": {
                    "deny_by_default": False,
                    "require_role_match": False,
                    "case_sensitive": False,
                    "allow_wildcard": False
                },
                "auto_load": False,
                "validation_enabled": False
            },
            "transport": {
                "type": "http",
                "port": None,
                "ssl": {
                    "enabled": False,
                    "cert_file": None,
                    "key_file": None,
                    "ca_cert": None,
                    "verify_client": False,
                    "client_cert_required": False
                }
            },
            "proxy_registration": {
                "enabled": False,
                "proxy_url": "http://localhost:3004",
                "server_id": "mcp_proxy_adapter",
                "server_name": "MCP Proxy Adapter",
                "description": "JSON-RPC API for interacting with MCP Proxy",
                "registration_timeout": 30,
                "retry_attempts": 3,
                "retry_delay": 5,
                "auto_register_on_startup": True,
                "auto_unregister_on_shutdown": True
            },
            "debug": {
                "enabled": False,
                "level": "WARNING"
            },
            "security": {
                "framework": "mcp_security_framework",
                "enabled": False,
                "debug": False,
                "environment": "dev",
                "version": "1.0.0",
                "auth": {
                    "enabled": False,
                    "methods": ["api_key"],
                    "api_keys": {},
                    "user_roles": {},
                    "jwt_secret": "",
                    "jwt_algorithm": "HS256",
                    "jwt_expiry_hours": 24,
                    "certificate_auth": False,
                    "certificate_roles_oid": "1.3.6.1.4.1.99999.1.1",
                    "certificate_permissions_oid": "1.3.6.1.4.1.99999.1.2",
                    "basic_auth": False,
                    "oauth2_config": None,
                    "public_paths": ["/health", "/docs", "/openapi.json"],
                    "security_headers": None
                },
                "ssl": {
                    "enabled": False,
                    "cert_file": None,
                    "key_file": None,
                    "ca_cert_file": None,
                    "client_cert_file": None,
                    "client_key_file": None,
                    "verify_mode": "CERT_NONE",
                    "min_tls_version": "TLSv1.2",
                    "max_tls_version": None,
                    "cipher_suite": None,
                    "check_hostname": True,
                    "check_expiry": True,
                    "expiry_warning_days": 30
                },
                "certificates": {
                    "enabled": False,
                    "ca_cert_path": None,
                    "ca_key_path": None,
                    "cert_storage_path": "./certs",
                    "key_storage_path": "./keys",
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
                    "roles": None
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
                    "file_path": None,
                    "max_file_size": 10,
                    "backup_count": 5,
                    "console_output": True,
                    "json_format": False,
                    "include_timestamp": True,
                    "include_level": True,
                    "include_module": True
                }
            },
            "protocols": {
                "enabled": True,
                "allowed_protocols": ["http", "jsonrpc"],
                "default_protocol": "http",
                "auto_discovery": True
            }
        }

        # Try to load configuration from file
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    self._update_nested_dict(self.config_data, file_config)
            except Exception as e:
                print(f"Error loading config from {self.config_path}: {e}")

        # Load configuration from environment variables
        self._load_env_variables()

    def load_from_file(self, config_path: str) -> None:
        """
        Load configuration from the specified file.

        Args:
            config_path: Path to configuration file.
        """
        self.config_path = config_path
        self.load_config()

    def _load_env_variables(self) -> None:
        """
        Load configuration from environment variables.
        Environment variables should be in format SERVICE_SECTION_KEY=value.
        For example, SERVICE_SERVER_PORT=8080.
        """
        prefix = "SERVICE_"
        for key, value in os.environ.items():
            if key.startswith(prefix):
                parts = key[len(prefix):].lower().split("_", 1)
                if len(parts) == 2:
                    section, param = parts
                    if section not in self.config_data:
                        self.config_data[section] = {}
                    self.config_data[section][param] = self._convert_env_value(value)

    def _convert_env_value(self, value: str) -> Any:
        """
        Convert environment variable value to appropriate type.

        Args:
            value: Value as string

        Returns:
            Converted value
        """
        # Try to convert to appropriate type
        if value.lower() == "true":
            return True
        elif value.lower() == "false":
            return False
        elif value.isdigit():
            return int(value)
        else:
            try:
                return float(value)
            except ValueError:
                return value

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value for key.

        Args:
            key: Configuration key in format "section.param"
            default: Default value if key not found

        Returns:
            Configuration value
        """
        parts = key.split(".")

        # Get value from config
        value = self.config_data
        for part in parts:
            if not isinstance(value, dict) or part not in value:
                return default
            value = value[part]

        return value

    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration values.

        Returns:
            Dictionary with all configuration values
        """
        return self.config_data.copy()

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value for key.

        Args:
            key: Configuration key in format "section.param"
            value: Configuration value
        """
        parts = key.split(".")
        if len(parts) == 1:
            self.config_data[key] = value
        else:
            section = parts[0]
            param_key = ".".join(parts[1:])

            if section not in self.config_data:
                self.config_data[section] = {}

            current = self.config_data[section]
            for part in parts[1:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]

            current[parts[-1]] = value

    def save(self, path: Optional[str] = None) -> None:
        """
        Save configuration to file.

        Args:
            path: Path to configuration file. If not specified,
                  self.config_path is used.
        """
        save_path = path or self.config_path
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(self.config_data, f, indent=2)

    def _update_nested_dict(self, d: Dict, u: Dict) -> Dict:
        """
        Update nested dictionary recursively.

        Args:
            d: Dictionary to update
            u: Dictionary with new values

        Returns:
            Updated dictionary
        """
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                self._update_nested_dict(d[k], v)
            else:
                d[k] = v
        return d

    def enable_feature(self, feature: str) -> None:
        """
        Enable a specific feature in the configuration.

        Args:
            feature: Feature to enable (ssl, auth, roles, proxy_registration,
                     security)
        """
        if feature == "ssl":
            self.set("ssl.enabled", True)
            self.set("security.ssl.enabled", True)
        elif feature == "auth":
            self.set("security.auth.enabled", True)
        elif feature == "roles":
            self.set("security.permissions.enabled", True)
            self.set("roles.enabled", True)
        elif feature == "proxy_registration":
            self.set("proxy_registration.enabled", True)
        elif feature == "security":
            self.set("security.enabled", True)
        elif feature == "rate_limit":
            self.set("security.rate_limit.enabled", True)
        elif feature == "certificates":
            self.set("security.certificates.enabled", True)
        else:
            raise ValueError(f"Unknown feature: {feature}")

    def disable_feature(self, feature: str) -> None:
        """
        Disable a specific feature in the configuration.

        Args:
            feature: Feature to disable (ssl, auth, roles, proxy_registration,
                     security)
        """
        if feature == "ssl":
            self.set("ssl.enabled", False)
            self.set("security.ssl.enabled", False)
        elif feature == "auth":
            self.set("security.auth.enabled", False)
        elif feature == "roles":
            self.set("security.permissions.enabled", False)
            self.set("roles.enabled", False)
        elif feature == "proxy_registration":
            self.set("proxy_registration.enabled", False)
        elif feature == "security":
            self.set("security.enabled", False)
        elif feature == "rate_limit":
            self.set("security.rate_limit.enabled", False)
        elif feature == "certificates":
            self.set("security.certificates.enabled", False)
        else:
            raise ValueError(f"Unknown feature: {feature}")

    def is_feature_enabled(self, feature: str) -> bool:
        """
        Check if a specific feature is enabled.

        Args:
            feature: Feature to check (ssl, auth, roles, proxy_registration,
                     security)

        Returns:
            True if feature is enabled, False otherwise
        """
        if feature == "ssl":
            return (self.get("ssl.enabled", False) or
                    self.get("security.ssl.enabled", False))
        elif feature == "auth":
            return self.get("security.auth.enabled", False)
        elif feature == "roles":
            return (self.get("security.permissions.enabled", False) or
                    self.get("roles.enabled", False))
        elif feature == "proxy_registration":
            return self.get("proxy_registration.enabled", False)
        elif feature == "security":
            return self.get("security.enabled", False)
        elif feature == "rate_limit":
            return self.get("security.rate_limit.enabled", False)
        elif feature == "certificates":
            return self.get("security.certificates.enabled", False)
        else:
            raise ValueError(f"Unknown feature: {feature}")

    def get_enabled_features(self) -> List[str]:
        """
        Get list of all enabled features.

        Returns:
            List of enabled feature names
        """
        features = []
        if self.is_feature_enabled("ssl"):
            features.append("ssl")
        if self.is_feature_enabled("auth"):
            features.append("auth")
        if self.is_feature_enabled("roles"):
            features.append("roles")
        if self.is_feature_enabled("proxy_registration"):
            features.append("proxy_registration")
        if self.is_feature_enabled("security"):
            features.append("security")
        if self.is_feature_enabled("rate_limit"):
            features.append("rate_limit")
        if self.is_feature_enabled("certificates"):
            features.append("certificates")
        return features

    def configure_auth_mode(self, mode: str, **kwargs) -> None:
        """
        Configure authentication mode.

        Args:
            mode: Authentication mode (api_key, jwt, certificate, basic, oauth2)
            **kwargs: Additional configuration parameters
        """
        if mode == "api_key":
            self.set("security.auth.methods", ["api_key"])
            if "api_keys" in kwargs:
                self.set("security.auth.api_keys", kwargs["api_keys"])
        elif mode == "jwt":
            self.set("security.auth.methods", ["jwt"])
            if "jwt_secret" in kwargs:
                self.set("security.auth.jwt_secret", kwargs["jwt_secret"])
        elif mode == "certificate":
            self.set("security.auth.methods", ["certificate"])
            self.set("security.auth.certificate_auth", True)
        elif mode == "basic":
            self.set("security.auth.methods", ["basic"])
            self.set("security.auth.basic_auth", True)
        elif mode == "oauth2":
            self.set("security.auth.methods", ["oauth2"])
            if "oauth2_config" in kwargs:
                self.set("security.auth.oauth2_config", kwargs["oauth2_config"])
        else:
            raise ValueError(f"Unknown authentication mode: {mode}")

    def configure_proxy_registration_mode(self, mode: str, **kwargs) -> None:
        """
        Configure proxy registration mode.

        Args:
            mode: Registration mode (token, certificate, api_key, none)
            **kwargs: Additional configuration parameters
        """
        if mode == "none":
            self.set("proxy_registration.enabled", False)
        else:
            self.set("proxy_registration.enabled", True)

            if mode == "token":
                self.set("proxy_registration.auth_method", "token")
                if "token" in kwargs:
                    self.set("proxy_registration.token.token", kwargs["token"])
            elif mode == "certificate":
                self.set("proxy_registration.auth_method", "certificate")
                if "cert_file" in kwargs:
                    self.set("proxy_registration.certificate.cert_file",
                             kwargs["cert_file"])
                if "key_file" in kwargs:
                    self.set("proxy_registration.certificate.key_file",
                             kwargs["key_file"])
            elif mode == "api_key":
                self.set("proxy_registration.auth_method", "api_key")
                if "key" in kwargs:
                    self.set("proxy_registration.api_key.key", kwargs["key"])

    def create_minimal_config(self) -> Dict[str, Any]:
        """
        Create minimal configuration with only essential features.

        Returns:
            Minimal configuration dictionary
        """
        minimal_config = self.config_data.copy()

        # Disable all optional features
        minimal_config["ssl"]["enabled"] = False
        minimal_config["security"]["enabled"] = False
        minimal_config["security"]["auth"]["enabled"] = False
        minimal_config["security"]["permissions"]["enabled"] = False
        minimal_config["security"]["rate_limit"]["enabled"] = False
        minimal_config["security"]["certificates"]["enabled"] = False
        minimal_config["proxy_registration"]["enabled"] = False
        minimal_config["roles"]["enabled"] = False

        return minimal_config

    def create_secure_config(self) -> Dict[str, Any]:
        """
        Create secure configuration with all security features enabled.

        Returns:
            Secure configuration dictionary
        """
        secure_config = self.config_data.copy()

        # Enable all security features
        secure_config["ssl"]["enabled"] = True
        secure_config["security"]["enabled"] = True
        secure_config["security"]["auth"]["enabled"] = True
        secure_config["security"]["permissions"]["enabled"] = True
        secure_config["security"]["rate_limit"]["enabled"] = True
        secure_config["security"]["certificates"]["enabled"] = True
        secure_config["proxy_registration"]["enabled"] = True
        secure_config["roles"]["enabled"] = True

        return secure_config


# Singleton instance
config = Config()
