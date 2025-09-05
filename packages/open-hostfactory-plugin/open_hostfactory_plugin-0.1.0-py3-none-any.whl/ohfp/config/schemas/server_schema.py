"""Server configuration schema for REST API server."""

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class AuthConfig(BaseModel):
    """Authentication configuration."""

    model_config = ConfigDict(extra="allow")  # Allow provider-specific auth configs

    enabled: bool = Field(False, description="Enable authentication")
    strategy: str = Field(
        "none",
        description="Authentication strategy (none, bearer_token, iam, cognito, oauth)",
    )

    # Bearer token configuration
    bearer_token: Optional[dict[str, Any]] = Field(
        None, description="Bearer token strategy configuration"
    )

    # AWS IAM configuration
    iam: Optional[dict[str, Any]] = Field(None, description="AWS IAM strategy configuration")

    # AWS Cognito configuration
    cognito: Optional[dict[str, Any]] = Field(
        None, description="AWS Cognito strategy configuration"
    )

    # OAuth configuration
    oauth: Optional[dict[str, Any]] = Field(None, description="OAuth strategy configuration")

    # Provider-specific auth configurations
    provider_auth: Optional[dict[str, Any]] = Field(
        None, description="Provider-specific auth configuration"
    )


class CORSConfig(BaseModel):
    """CORS configuration."""

    enabled: bool = Field(True, description="Enable CORS")
    origins: list[str] = Field(["*"], description="Allowed origins")
    methods: list[str] = Field(
        ["GET", "POST", "PUT", "DELETE", "OPTIONS"], description="Allowed methods"
    )
    headers: list[str] = Field(["*"], description="Allowed headers")
    credentials: bool = Field(False, description="Allow credentials")


class ServerConfig(BaseModel):
    """REST API server configuration."""

    model_config = ConfigDict(extra="forbid")

    enabled: bool = Field(False, description="Enable REST API server")
    # Intentional binding for server deployment
    host: str = Field("0.0.0.0", description="Server host")  # nosec B104
    port: int = Field(8000, description="Server port")
    workers: int = Field(1, description="Number of worker processes")
    reload: bool = Field(False, description="Enable auto-reload for development")
    log_level: str = Field("info", description="Server log level")
    access_log: bool = Field(True, description="Enable access logging")

    # Documentation
    docs_enabled: bool = Field(True, description="Enable API documentation")
    docs_url: str = Field("/docs", description="Swagger UI URL")
    redoc_url: str = Field("/redoc", description="ReDoc URL")
    openapi_url: str = Field("/openapi.json", description="OpenAPI schema URL")

    # Authentication and CORS
    auth: AuthConfig = Field(default=AuthConfig(), description="Authentication configuration")
    cors: CORSConfig = Field(default=CORSConfig(), description="CORS configuration")

    # Security
    require_https: bool = Field(False, description="Require HTTPS for all requests")
    trusted_hosts: list[str] = Field(["*"], description="Trusted host headers")

    # Performance
    request_timeout: int = Field(30, description="Request timeout in seconds")
    max_request_size: int = Field(16 * 1024 * 1024, description="Maximum request size in bytes")

    # Rate limiting (for future implementation)
    rate_limiting: Optional[dict[str, Any]] = Field(None, description="Rate limiting configuration")
