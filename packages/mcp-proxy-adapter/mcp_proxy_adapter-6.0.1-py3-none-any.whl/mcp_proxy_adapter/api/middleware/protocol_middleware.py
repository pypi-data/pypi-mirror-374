"""
Protocol middleware module.

This module provides middleware for validating protocol access based on configuration.
"""

from typing import Callable, Dict, Any, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from mcp_proxy_adapter.core.protocol_manager import get_protocol_manager
from mcp_proxy_adapter.core.logging import logger


class ProtocolMiddleware(BaseHTTPMiddleware):
    """
    Middleware for protocol validation.
    
    This middleware checks if the incoming request protocol is allowed
    based on the protocol configuration.
    """
    
    def __init__(self, app, app_config: Optional[Dict[str, Any]] = None):
        """
        Initialize protocol middleware.

        Args:
            app: FastAPI application
            app_config: Application configuration dictionary (optional)
        """
        super().__init__(app)
        # Normalize config to dictionary
        normalized_config: Optional[Dict[str, Any]]
        if app_config is None:
            normalized_config = None
        elif hasattr(app_config, 'get_all'):
            try:
                normalized_config = app_config.get_all()
            except Exception as e:
                logger.debug(f"ProtocolMiddleware - Error calling get_all(): {e}, type: {type(app_config)}")
                normalized_config = None
        elif hasattr(app_config, 'keys'):
            normalized_config = app_config  # Already dict-like
        else:
            logger.debug(f"ProtocolMiddleware - app_config is not dict-like, type: {type(app_config)}, value: {repr(app_config)}")
            normalized_config = None

        logger.debug(f"ProtocolMiddleware - normalized_config type: {type(normalized_config)}")
        if normalized_config:
            logger.debug(f"ProtocolMiddleware - protocols in config: {'protocols' in normalized_config}")
            if 'protocols' in normalized_config:
                logger.debug(f"ProtocolMiddleware - protocols type: {type(normalized_config['protocols'])}")

        self.app_config = normalized_config
        # Get protocol manager with current configuration
        self.protocol_manager = get_protocol_manager(normalized_config)
    
    def update_config(self, new_config: Dict[str, Any]):
        """
        Update configuration and reload protocol manager.
        
        Args:
            new_config: New configuration dictionary
        """
        # Normalize new config
        if hasattr(new_config, 'get_all'):
            try:
                self.app_config = new_config.get_all()
            except Exception:
                self.app_config = None
        elif hasattr(new_config, 'keys'):
            self.app_config = new_config
        else:
            self.app_config = None
        self.protocol_manager = get_protocol_manager(self.app_config)
        logger.info("Protocol middleware configuration updated")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request through protocol middleware.

        Args:
            request: Incoming request
            call_next: Next middleware/endpoint function

        Returns:
            Response object
        """
        logger.debug(f"ProtocolMiddleware.dispatch called for {request.method} {request.url.path}")
        try:
            # Get protocol from request
            protocol = self._get_request_protocol(request)
            
            # Check if protocol is allowed
            if not self.protocol_manager.is_protocol_allowed(protocol):
                logger.warning(f"Protocol '{protocol}' not allowed for request to {request.url.path}")
                return JSONResponse(
                    status_code=403,
                    content={
                        "error": "Protocol not allowed",
                        "message": f"Protocol '{protocol}' is not allowed. Allowed protocols: {self.protocol_manager.get_allowed_protocols()}",
                        "allowed_protocols": self.protocol_manager.get_allowed_protocols()
                    }
                )
            
            # Continue processing
            response = await call_next(request)
            return response
            
        except Exception as e:
            logger.error(f"Protocol middleware error: {e}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Protocol validation error",
                    "message": str(e)
                }
            )
    
    def _get_request_protocol(self, request: Request) -> str:
        """
        Extract protocol from request.
        
        Args:
            request: FastAPI request object
            
        Returns:
            Protocol name (http, https, mtls)
        """
        # Check if request is secure (HTTPS)
        if request.url.scheme:
            scheme = request.url.scheme.lower()
            
            # If HTTPS, check if client certificate is provided (MTLS)
            if scheme == "https":
                # Check for client certificate in headers or SSL context
                if hasattr(request, 'scope') and 'ssl' in request.scope:
                    ssl_context = request.scope.get('ssl')
                    if ssl_context and hasattr(ssl_context, 'getpeercert'):
                        try:
                            cert = ssl_context.getpeercert()
                            if cert:
                                return "mtls"
                        except:
                            pass
                
                # Check for client certificate in headers
                if request.headers.get("ssl-client-cert") or request.headers.get("x-client-cert"):
                    return "mtls"
                
                return "https"
            
            return scheme
        
        # Fallback to checking headers
        if request.headers.get("x-forwarded-proto"):
            return request.headers.get("x-forwarded-proto").lower()
        
        # Default to HTTP
        return "http"


def setup_protocol_middleware(app, app_config: Optional[Dict[str, Any]] = None):
    """
    Setup protocol middleware for FastAPI application.

    Args:
        app: FastAPI application
        app_config: Application configuration dictionary (optional)
    """
    logger.debug(f"setup_protocol_middleware - app_config type: {type(app_config)}")

    # Check if protocol management is enabled
    if app_config is None:
        from mcp_proxy_adapter.config import config
        app_config = config.get_all()
        logger.debug(f"setup_protocol_middleware - loaded from global config, type: {type(app_config)}")

    logger.debug(f"setup_protocol_middleware - final app_config type: {type(app_config)}")

    if hasattr(app_config, 'get'):
        logger.debug(f"setup_protocol_middleware - app_config keys: {list(app_config.keys()) if hasattr(app_config, 'keys') else 'no keys'}")
        protocols_config = app_config.get("protocols", {})
        logger.debug(f"setup_protocol_middleware - protocols_config type: {type(protocols_config)}")
        enabled = protocols_config.get("enabled", True) if hasattr(protocols_config, 'get') else True
    else:
        logger.debug(f"setup_protocol_middleware - app_config is not dict-like: {repr(app_config)}")
        enabled = True

    logger.debug(f"setup_protocol_middleware - protocol management enabled: {enabled}")

    if enabled:
        # Create protocol middleware with current configuration
        logger.debug(f"setup_protocol_middleware - creating ProtocolMiddleware with config type: {type(app_config)}")
        middleware = ProtocolMiddleware(app, app_config)
        logger.debug(f"setup_protocol_middleware - adding middleware to app")
        app.add_middleware(ProtocolMiddleware, app_config=app_config)
        logger.info("Protocol middleware added to application")
    else:
        logger.info("Protocol management is disabled, skipping protocol middleware") 