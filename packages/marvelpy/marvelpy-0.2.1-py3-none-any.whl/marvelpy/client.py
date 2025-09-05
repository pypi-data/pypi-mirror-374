"""Marvel API client for making authenticated requests."""

from __future__ import annotations

import asyncio
from typing import Any
from urllib.parse import urljoin

import httpx

from .utils.auth import generate_auth_params


class MarvelClient:
    """Client for interacting with the Marvel Comics API.

    This client handles authentication and provides methods for making
    authenticated requests to the Marvel API endpoints.

    Args:
        public_key: Marvel API public key
        private_key: Marvel API private key
        base_url: Base URL for the Marvel API (defaults to official API)
        timeout: Request timeout in seconds (default: 30)
        max_retries: Maximum number of retry attempts (default: 3)
    """

    BASE_URL = "https://gateway.marvel.com/v1/public/"

    def __init__(
        self,
        public_key: str,
        private_key: str,
        base_url: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 3,
    ) -> None:
        self.public_key = public_key
        self.private_key = private_key
        self.base_url = base_url or self.BASE_URL
        self.timeout = timeout
        self.max_retries = max_retries

        # Create HTTP client with default settings
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100),
        )

    async def __aenter__(self) -> MarvelClient:
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    def _get_auth_params(self) -> dict[str, str]:
        """Get authentication parameters for API requests."""
        return generate_auth_params(self.public_key, self.private_key)

    def _build_url(self, endpoint: str) -> str:
        """Build full URL for an API endpoint."""
        return urljoin(self.base_url, endpoint.lstrip("/"))

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Make an authenticated request to the Marvel API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            **kwargs: Additional arguments for httpx request

        Returns:
            JSON response data

        Raises:
            httpx.HTTPError: If the request fails
            httpx.RequestError: If there's a network error
        """
        # Build full URL
        url = self._build_url(endpoint)

        # Add authentication parameters
        auth_params = self._get_auth_params()
        if params is None:
            params = {}
        params.update(auth_params)

        # Make request with retries
        for attempt in range(self.max_retries + 1):
            try:
                response = await self._client.request(
                    method=method,
                    url=url,
                    params=params,
                    **kwargs,
                )
                response.raise_for_status()
                return response.json()  # type: ignore[no-any-return]

            except httpx.HTTPStatusError as e:
                if e.response.status_code >= 500 and attempt < self.max_retries:
                    # Retry on server errors
                    await asyncio.sleep(2**attempt)  # Exponential backoff
                    continue
                raise
            except httpx.RequestError:
                if attempt < self.max_retries:
                    await asyncio.sleep(2**attempt)
                    continue
                raise

        # This should never be reached, but mypy needs it
        raise httpx.RequestError("Max retries exceeded")

    async def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Make a GET request to the Marvel API.

        Args:
            endpoint: API endpoint path
            params: Query parameters
            **kwargs: Additional arguments for httpx request

        Returns:
            JSON response data
        """
        return await self._make_request("GET", endpoint, params, **kwargs)

    # Convenience methods for common operations
    async def health_check(self) -> dict[str, Any]:
        """Check if the Marvel API is accessible.

        Returns:
            API status information
        """
        # Use characters endpoint with limit=1 as a health check
        return await self.get("characters", params={"limit": 1})

    async def get_characters(self, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Get characters from the Marvel API.

        Args:
            params: Query parameters for filtering characters

        Returns:
            Characters data from the API
        """
        return await self.get("characters", params)
