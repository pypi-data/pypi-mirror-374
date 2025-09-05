from __future__ import annotations

from typing import Optional, List
from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class OIDCProvider(BaseModel):
    name: str
    issuer: str                     # e.g., "https://dev-abc123.okta.com" or "https://YOUR_DOMAIN.auth0.com"
    client_id: str
    client_secret: SecretStr
    scope: str = "openid email profile"

class AuthSettings(BaseSettings):
    jwt_secret: SecretStr = Field(..., description="JWT secret")
    jwt_lifetime_seconds: int = 60 * 60 * 24 * 7

    # Built-ins (all optional)
    google_client_id: Optional[str] = None
    google_client_secret: Optional[SecretStr] = None

    github_client_id: Optional[str] = None
    github_client_secret: Optional[SecretStr] = None

    # Microsoft Entra ID (Azure AD) – needs a tenant
    ms_client_id: Optional[str] = None
    ms_client_secret: Optional[SecretStr] = None
    ms_tenant: Optional[str] = None  # e.g. "organizations" | "common" | "<tenant_id>"

    # LinkedIn (non-OIDC)
    li_client_id: Optional[str] = None
    li_client_secret: Optional[SecretStr] = None

    # Generic OIDC providers (Okta, Auth0, Keycloak, Azure AD via issuer, etc.)
    oidc_providers: List[OIDCProvider] = Field(default_factory=list)

    model_config = SettingsConfigDict(env_prefix="AUTH_", env_file=".env", extra="ignore")

_settings: AuthSettings | None = None

def get_auth_settings() -> AuthSettings:
    global _settings
    if _settings is None:
        _settings = AuthSettings
    return _settings