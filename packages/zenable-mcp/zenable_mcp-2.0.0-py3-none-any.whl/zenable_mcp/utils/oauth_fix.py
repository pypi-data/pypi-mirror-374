"""Fix for FastMCP OAuth not working with cached tokens.

This module provides a workaround for a FastMCP bug where OAuth cached tokens
are not properly added as Authorization headers when making SSE requests.
"""

import json
from pathlib import Path

from fastmcp.client.auth import OAuth


def patch_oauth_for_cached_tokens(
    oauth: OAuth, base_url: str, cache_dir: Path
) -> OAuth:
    """
    Patch OAuth instance to properly use cached tokens.

    This is a workaround for FastMCP not properly adding Authorization headers
    when using cached OAuth tokens with SSE transport.
    """
    # Generate cache filename same way FastMCP does
    safe_name = (
        base_url.replace("://", "_")
        .replace(".", "_")
        .replace("/", "_")
        .replace(":", "_")
    )
    token_file = cache_dir / f"{safe_name}_tokens.json"

    # Try to load cached token
    if token_file.exists():
        try:
            with open(token_file) as f:
                token_data = json.load(f)
                access_token = token_data.get("token_payload", {}).get("access_token")

                if access_token:
                    # Patch auth_flow to add the Authorization header
                    def patched_auth_flow(request):
                        request.headers["Authorization"] = f"Bearer {access_token}"
                        yield request
                        return

                    # Patch async version too
                    async def patched_async_auth_flow(request):
                        request.headers["Authorization"] = f"Bearer {access_token}"
                        yield request
                        return

                    oauth.auth_flow = patched_auth_flow
                    oauth.async_auth_flow = patched_async_auth_flow
        except Exception:
            pass  # If anything fails, use normal OAuth flow

    return oauth
