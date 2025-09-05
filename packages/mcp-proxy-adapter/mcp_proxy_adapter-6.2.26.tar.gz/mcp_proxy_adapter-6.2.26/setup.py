from setuptools import setup, find_packages

setup(
    name="mcp-proxy-adapter",
    version="6.2.25",
    description="Powerful JSON-RPC microservices framework with built-in security, authentication, and proxy registration",
    long_description="""# MCP Proxy Adapter

[![PyPI version](https://badge.fury.io/py/mcp-proxy-adapter.svg)](https://pypi.org/project/mcp-proxy-adapter/)
[![Python versions](https://img.shields.io/pypi/pyversions/mcp-proxy-adapter.svg)](https://pypi.org/project/mcp-proxy-adapter/)
[![License](https://img.shields.io/pypi/l/mcp-proxy-adapter.svg)](https://github.com/maverikod/mcp-proxy-adapter/blob/main/LICENSE)

A powerful framework for creating JSON-RPC-enabled microservices with built-in security, authentication, and proxy registration capabilities.

## 🚀 Quick Install

```bash
pip install mcp-proxy-adapter
```

## ✨ Key Features

- **🔒 Security First**: Built-in mTLS, JWT, API Key authentication
- **🌐 JSON-RPC 2.0**: Complete protocol implementation
- **🔄 Proxy Registration**: Automatic service discovery and registration
- **⚡ High Performance**: Built on FastAPI with async support
- **🛡️ Role-Based Access**: Fine-grained permission control
- **📡 Universal Client**: Supports all authentication methods

## 🏃‍♂️ Quick Example

Create a secure JSON-RPC microservice in minutes:

```python
from mcp_proxy_adapter import create_app, Command, SuccessResult

# Create a custom command
class HelloCommand(Command):
    name = "hello"
    description = "Say hello"

    async def execute(self, **kwargs) -> SuccessResult:
        name = kwargs.get("name", "World")
        return SuccessResult(f"Hello, {name}!")

# Create and run the application
app = create_app()
```

## 📋 Configuration Types

### 1. Basic HTTP (No Authentication)

Perfect for development and internal services:

```json
{
  "server": {
    "host": "127.0.0.1",
    "port": 8000
  },
  "security": {
    "enabled": false
  },
  "protocols": {
    "enabled": true,
    "allowed_protocols": ["http", "jsonrpc"]
  }
}
```

### 2. HTTP with API Key Authentication

Simple token-based authentication:

```json
{
  "server": {
    "host": "127.0.0.1",
    "port": 8000
  },
  "security": {
    "enabled": true,
    "auth": {
      "enabled": true,
      "methods": ["api_key"],
      "api_keys": {
        "test-token-123": "admin",
        "readonly-token-456": "user"
      }
    }
  }
}
```

### 3. HTTPS with SSL/TLS

Secure HTTP with SSL certificates:

```json
{
  "server": {
    "host": "127.0.0.1",
    "port": 8443
  },
  "ssl": {
    "enabled": true,
    "cert_file": "./certs/server_cert.pem",
    "key_file": "./certs/server_key.pem",
    "ca_cert_file": "./certs/ca_cert.pem"
  }
}
```

### 4. Mutual TLS (mTLS) Authentication

Highest security with client certificates:

```json
{
  "server": {
    "host": "127.0.0.1",
    "port": 8443
  },
  "ssl": {
    "enabled": true,
    "cert_file": "./certs/server_cert.pem",
    "key_file": "./certs/server_key.pem",
    "ca_cert_file": "./certs/ca_cert.pem",
    "verify_client": true,
    "client_cert_required": true
  },
  "security": {
    "enabled": true,
    "auth": {
      "enabled": true,
      "methods": ["certificate"]
    }
  }
}
```

### 5. Full Security with Role-Based Access Control

Complete security setup with roles and permissions:

```json
{
  "server": {
    "host": "127.0.0.1",
    "port": 8443
  },
  "ssl": {
    "enabled": true,
    "cert_file": "./certs/server_cert.pem",
    "key_file": "./certs/server_key.pem",
    "ca_cert_file": "./certs/ca_cert.pem",
    "verify_client": true
  },
  "security": {
    "enabled": true,
    "auth": {
      "enabled": true,
      "methods": ["certificate"]
    },
    "permissions": {
      "enabled": true,
      "roles_file": "./roles.json"
    },
    "rate_limit": {
      "enabled": true,
      "default_requests_per_minute": 60
    }
  },
  "commands": {
    "auto_discovery": true,
    "enabled_commands": ["health", "echo", "list", "help"]
  }
}
```

## 🔄 Application Lifecycle

### 1. Initialization Phase

```python
from mcp_proxy_adapter import create_app
from mcp_proxy_adapter.config import Config

# Load configuration
config = Config("config.json")
app = create_app(config)
```

### 2. Middleware Setup

The framework automatically sets up middleware based on configuration:

- **ProtocolMiddleware**: Handles HTTP/JSON-RPC routing
- **UserInfoMiddleware**: Manages authentication and user context
- **UnifiedSecurityMiddleware**: Provides security features
- **ErrorHandlingMiddleware**: Handles exceptions
- **LoggingMiddleware**: Logs requests and responses

### 3. Command Registration

Commands are automatically discovered and registered:

- **Built-in commands**: health, echo, help, list, config
- **Custom commands**: Located in `./commands/` directory
- **Auto-discovery**: Enabled by default for dynamic loading

### 4. Server Startup

```python
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 🛠️ Command Types and Examples

### Built-in Commands

#### Health Check
```bash
# Via HTTP
curl http://localhost:8000/health

# Via JSON-RPC
curl -X POST http://localhost:8000/cmd \\
  -H "Content-Type: application/json" \\
  -d '{"jsonrpc": "2.0", "method": "health", "id": 1}'
```

#### Echo Command
```bash
curl -X POST http://localhost:8000/cmd \\
  -H "Content-Type: application/json" \\
  -d '{"jsonrpc": "2.0", "method": "echo", "params": {"message": "Hello World"}, "id": 2}'
```

### Custom Commands

Create custom commands by extending the base Command class:

```python
from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.core.result import SuccessResult

class CalculatorCommand(Command):
    name = "calculator"
    description = "Basic calculator operations"

    async def execute(self, operation: str, a: float, b: float) -> SuccessResult:
        if operation == "add":
            result = a + b
        elif operation == "subtract":
            result = a - b
        elif operation == "multiply":
            result = a * b
        elif operation == "divide":
            if b == 0:
                raise ValueError("Division by zero")
            result = a / b
        else:
            raise ValueError(f"Unknown operation: {operation}")

        return SuccessResult({
            "operation": operation,
            "a": a,
            "b": b,
            "result": result
        })
```

### Plugin/Loadable Commands

For more complex scenarios, create command plugins:

```python
# commands/my_plugin.py
from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.core.result import SuccessResult

class DatabaseQueryCommand(Command):
    name = "db_query"
    description = "Execute database queries"

    def __init__(self):
        super().__init__()
        self.db_connection = None

    async def execute(self, query: str, params: dict = None) -> SuccessResult:
        # Database logic here
        return SuccessResult({"query": query, "rows_affected": 42})
```

## 🔍 Auto-Discovery Configuration

### Required Options for Auto-Discovery

```json
{
  "commands": {
    "auto_discovery": true,
    "custom_commands_path": "./commands",
    "enabled_commands": ["*"],
    "disabled_commands": []
  },
  "protocols": {
    "enabled": true,
    "auto_discovery": true,
    "allowed_protocols": ["http", "jsonrpc"]
  }
}
```

### Auto-Discovery Behavior

1. **Command Discovery**:
   - Scans `./commands/` directory for Python files
   - Imports all classes that inherit from `Command`
   - Registers commands automatically
   - Supports hot-reloading in development mode

2. **Protocol Discovery**:
   - Automatically detects request types (HTTP vs JSON-RPC)
   - Routes requests to appropriate handlers
   - Supports custom protocol extensions

3. **Security Integration**:
   - Applies authentication to discovered commands
   - Enforces role-based permissions
   - Supports custom security plugins

## 📊 Usage Examples

### Basic Server Setup

```python
from mcp_proxy_adapter import create_app
import uvicorn

app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### With Security Configuration

```python
from mcp_proxy_adapter import create_app
from mcp_proxy_adapter.config import Config

# Load configuration
config = Config.from_file("config.json")
app = create_app(config)
```

### Client Usage

```python
from mcp_proxy_adapter.core.client import UniversalClient

async def main():
    async with UniversalClient({"server_url": "http://localhost:8000"}) as client:
        result = await client.execute_command("help")
        print(result)

import asyncio
asyncio.run(main())
```

## 🔧 Requirements

- **Python**: 3.9+
- **Dependencies**:
  - `fastapi` - Web framework
  - `pydantic` - Data validation
  - `hypercorn` - ASGI server
  - `mcp_security_framework` - Security components
  - `jsonrpc` - JSON-RPC protocol

## Features

- **JSON-RPC Framework**: Complete JSON-RPC 2.0 implementation
- **Security Integration**: Built-in support for mcp_security_framework
- **Authentication**: Multiple auth methods (API Key, JWT, Certificate, Basic Auth)
- **Proxy Registration**: Automatic registration and discovery of services
- **Command System**: Extensible command framework with role-based access control
- **SSL/TLS Support**: Full SSL/TLS support including mTLS
- **Async Support**: Built on FastAPI with full async support
- **Extensible**: Plugin system for custom commands and middleware

## 🤝 Support & Contributing

- **📧 Email**: vasilyvz@gmail.com
- **🐛 Issues**: [GitHub Issues](https://github.com/maverikod/mcp-proxy-adapter/issues)
- **📚 Documentation**: [GitHub Wiki](https://github.com/maverikod/mcp-proxy-adapter/wiki)
- **💬 Discussions**: [GitHub Discussions](https://github.com/maverikod/mcp-proxy-adapter/discussions)

## 📄 License

MIT License - see [LICENSE](https://github.com/maverikod/mcp-proxy-adapter/blob/main/LICENSE) file for details.

## 📊 Version

**6.2.24** - Production-ready release with comprehensive security, proxy registration, and PyPI optimization.

---

*Built with ❤️ for secure microservices development*

---

## API Reference

### Core Endpoints

- `GET /health` - Service health check
- `POST /cmd` - JSON-RPC endpoint
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /openapi.json` - OpenAPI specification

### Built-in JSON-RPC Methods

- `health` - Check service health
- `echo` - Echo back parameters
- `help` - List available commands
- `list` - List all registered commands
- `config` - Get configuration info

### Configuration Options

#### Server Configuration
```json
{
  "server": {
    "host": "127.0.0.1",
    "port": 8000,
    "debug": false,
    "log_level": "INFO"
  }
}
```

#### Security Configuration
```json
{
  "security": {
    "enabled": true,
    "auth": {
      "enabled": true,
      "methods": ["api_key", "certificate"],
      "api_keys": {"token": "role"},
      "jwt_secret": "secret",
      "certificate_auth": true
    },
    "permissions": {
      "enabled": true,
      "roles_file": "./roles.json"
    },
    "rate_limit": {
      "enabled": true,
      "default_requests_per_minute": 60
    }
  }
}
```

#### SSL/TLS Configuration
```json
{
  "ssl": {
    "enabled": true,
    "cert_file": "./certs/server.crt",
    "key_file": "./certs/server.key",
    "ca_cert_file": "./certs/ca.crt",
    "verify_client": true,
    "client_cert_required": true
  }
}
```

#### Commands Configuration
```json
{
  "commands": {
    "auto_discovery": true,
    "custom_commands_path": "./commands",
    "enabled_commands": ["health", "echo", "custom"],
    "disabled_commands": []
  }
}
```

#### Protocols Configuration
```json
{
  "protocols": {
    "enabled": true,
    "allowed_protocols": ["http", "jsonrpc"],
    "default_protocol": "http",
    "auto_discovery": true
  }
}
```

## Development

### Setup Development Environment

```bash
git clone https://github.com/maverikod/mcp-proxy-adapter.git
cd mcp-proxy-adapter
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest tests/
pytest --cov=mcp_proxy_adapter tests/
```

### Run Examples

```bash
python -m mcp_proxy_adapter.main --config examples/configs/http_simple.json
python examples/basic_framework/main.py --config configs/mtls_with_roles.json
```

## Author

**Vasiliy Zdanovskiy** - vasilyvz@gmail.com

---

🎉 **Ready to build secure JSON-RPC microservices with MCP Proxy Adapter!**""",
    long_description_content_type="text/markdown",
    author="Vasiliy Zdanovskiy",
    author_email="vasilyvz@gmail.com",
    url="https://github.com/maverikod/mcp-proxy-adapter",
    project_urls={
        "Homepage": "https://github.com/maverikod/mcp-proxy-adapter",
        "Documentation": "https://github.com/maverikod/mcp-proxy-adapter#readme",
        "Source": "https://github.com/maverikod/mcp-proxy-adapter",
        "Tracker": "https://github.com/maverikod/mcp-proxy-adapter/issues",
        "PyPI": "https://pypi.org/project/mcp-proxy-adapter/",
    },
    packages=find_packages(exclude=["mcp_sdk*", "test*", "tests*", ".venv*", "venv*", "build*", "dist*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: FastAPI",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=[
        "json-rpc",
        "microservices",
        "fastapi",
        "security",
        "authentication",
        "authorization",
        "proxy",
        "mcp",
        "mtls",
        "ssl",
        "rest",
        "api",
    ],
    python_requires=">=3.9",
    install_requires=[
        "fastapi>=0.95.0,<1.0.0",
        "pydantic>=2.0.0",
        "hypercorn>=0.15.0,<1.0.0",
        "docstring-parser>=0.15,<1.0.0",
        "typing-extensions>=4.5.0,<5.0.0",
        "jsonrpc>=1.2.0",
        "psutil>=5.9.0",
        "mcp_security_framework>=1.1.2",
        "packaging>=20.0",
        "aiohttp>=3.8.0,<4.0.0",
        "requests>=2.28.0,<3.0.0"
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.20.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
        ],
    },
    include_package_data=False,
) 