"""Pydantic models for MCP configuration validatoon."""

import os
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

ZENABLE_MCP_ENDPOINT = (
    os.environ.get("ZENABLE_MCP_ENDPOINT", "https://mcp.www.zenable.app/").rstrip("/")
    + "/"
)


class _GenericMcpServerConfig(BaseModel):
    """Generic MCP server configuration for use when making other generic configs."""

    disabled: Optional[bool] = Field(
        default=None, description="Whether the server is disabled"
    )
    alwaysAllow: Optional[list[str]] = Field(
        default=None, description="Tools to always allow without prompting"
    )
    autoApprove: Optional[list[str]] = Field(
        default=None, description="Tools to auto-approve"
    )
    trust: Optional[bool] = Field(
        default=None, description="Whether to trust this server"
    )

    model_config = ConfigDict(
        strict=False, extra="allow"
    )  # Allow additional fields for flexibility


class _GenericMCPRemoteServerConfig(_GenericMcpServerConfig):
    """Generic MCP Remote server configuration for all IDEs with OAuth format."""

    type: Literal["http", "streamable-http", "sse"] = Field(
        default="sse", description="Server type"
    )
    url: str = Field(default=ZENABLE_MCP_ENDPOINT, description="URL for the server")

    model_config = ConfigDict(strict=False, extra="forbid")


class _GenericMCPStdioServerConfig(_GenericMcpServerConfig):
    """Generic MCP Stdio server configuration for all IDEs with OAuth format."""

    command: Literal["npx"] = Field(
        default="npx", description="Command to execute for stdio server"
    )
    args: list[str] = Field(
        # We don't use mcp-remote@latest because the OAuth creds are per-mcp-remote version and we want them cached as long as possible
        # while we work on making this no longer necessary
        default_factory=lambda: ["-y", "--", "mcp-remote", ZENABLE_MCP_ENDPOINT],
        description="Arguments for the command",
    )

    model_config = ConfigDict(strict=False, extra="forbid")

    @field_validator("command")
    def validate_command(cls, v):
        if v != "npx":
            raise ValueError(f"Zenable MCP must use 'npx' command, got '{v}'")
        return v

    @field_validator("args")
    def validate_args(cls, v):
        if not v:
            raise ValueError("Args cannot be empty")

        # Check for required components
        args_str = " ".join(v)

        if "mcp-remote" not in args_str:
            raise ValueError("Args must include 'mcp-remote'")

        if ZENABLE_MCP_ENDPOINT not in args_str:
            raise ValueError(
                f"Args must include Zenable MCP endpoint: {ZENABLE_MCP_ENDPOINT}"
            )

        return v


class _RooMCPConfig(_GenericMCPStdioServerConfig):
    """Roo-specific MCP configuration with strict requirements."""

    # This can move to OAuth when this issue is fixed: https://github.com/RooCodeInc/Roo-Code/issues/7296

    disabled: bool = Field(default=False, description="Must be explicitly set to false")
    alwaysAllow: list[str] = Field(
        default_factory=lambda: ["conformance_check"],
        description="Must include conformance_check",
    )

    @field_validator("disabled")
    def validate_disabled(cls, v):
        if v is not False:
            raise ValueError(f"Roo MCP must have disabled=false, got {v}")
        return v

    @field_validator("alwaysAllow")
    def validate_always_allow(cls, v):
        if "conformance_check" not in v:
            raise ValueError("Roo MCP must have 'conformance_check' in alwaysAllow")
        return v


# Kiro is temporarily not supported because as of 2025-09-04, Kiro explicitly documents that they only support stdio MCP servers and to use npx
# mcp-remote to support remote servers
# https://kiro.dev/docs/mcp/servers/#remote-mcp-servers
# class _KiroMCPConfig(_GenericMCPStdioServerConfig):
#     """Kiro-specific MCP configuration."""
#
#
#     disabled: bool = Field(default=False, description="Must be explicitly set to false")
#     autoApprove: list[str] = Field(
#         default_factory=lambda: ["conformance_check"],
#         description="Must include conformance_check",
#     )
#
#     @field_validator("disabled")
#     def validate_disabled(cls, v):
#         if v is not False:
#             raise ValueError(f"Kiro MCP must have disabled=false, got {v}")
#         return v
#
#     @field_validator("autoApprove")
#     def validate_auto_approve(cls, v):
#         if "conformance_check" not in v:
#             raise ValueError("Kiro MCP must have 'conformance_check' in autoApprove")
#         return v
#
#     @field_validator("args")
#     def validate_no_api_key(cls, v):
#         """Ensure args don't contain API_KEY"""
#         if any("API_KEY:" in str(arg) for arg in v):
#             raise ValueError("Kiro MCP must not include API_KEY in args - we use OAuth")
#         return v


class _WindsurfMCPConfig(BaseModel):
    """Windsurf-specific MCP configuration.

    Windsurf uses 'serverUrl' instead of 'url' for the server endpoint.
    Note: Windsurf does not support the 'type' field.
    """

    serverUrl: str = Field(
        default=ZENABLE_MCP_ENDPOINT, description="URL for the server"
    )

    model_config = ConfigDict(strict=False, extra="forbid")

    @field_validator("serverUrl")
    def validate_server_url(cls, v):
        if not v:
            raise ValueError("serverUrl cannot be empty")
        if ZENABLE_MCP_ENDPOINT not in v:
            raise ValueError(
                f"serverUrl must be Zenable MCP endpoint: {ZENABLE_MCP_ENDPOINT}, got '{v}'"
            )
        return v


class _GeminiMCPConfig(_GenericMCPRemoteServerConfig):
    """Gemini CLI-specific MCP configuration with OAuth format."""

    oauth: dict[str, bool] = Field(
        default={"enabled": True}, description="OAuth configuration"
    )
    trust: bool = Field(default=True, description="Must be set to true")

    @field_validator("trust")
    def validate_trust(cls, v):
        if v is not True:
            raise ValueError(f"Gemini MCP must have trust=true, got {v}")
        return v

    @field_validator("oauth")
    def validate_oauth(cls, v):
        if not isinstance(v, dict):
            raise ValueError("oauth must be a dictionary")
        if v.get("enabled") is not True:
            raise ValueError("oauth.enabled must be true")
        return v


class _ClaudeCodeMCPConfig(_GenericMCPRemoteServerConfig):
    """Claude Code-specific MCP server configuration with OAuth."""

    # We just use the defaults


class _VSCodeMCPConfig(_GenericMCPRemoteServerConfig):
    """VS Code-specific MCP server configuration with OAuth."""

    # We just use the defaults


class _AmazonQMCPConfig(_GenericMCPStdioServerConfig):
    """Amazon Q-specific MCP configuration for OAuth authentication."""

    disabled: bool = Field(default=False, description="Whether the server is disabled")
    timeout: int = Field(default=5000, description="Timeout in milliseconds")

    @field_validator("disabled")
    def validate_disabled(cls, v):
        if v is not False:
            raise ValueError(f"Amazon Q MCP must have disabled=false, got {v}")
        return v


class _MCPConfigFile(BaseModel):
    """Model for the complete MCP configuration file."""

    mcpServers: dict[str, dict[str, Any]] = Field(
        default_factory=dict, description="MCP server configurations"
    )

    model_config = ConfigDict(
        strict=False, extra="allow"
    )  # Allow additional top-level fields
