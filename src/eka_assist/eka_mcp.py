from logging import Logger
from typing import Dict, Any, Optional

import httpx


class EkaMCP:
    def __init__(self, api_url: str, api_token: str, logger: Logger, pool_limits: Optional[Dict[str, int]] = None):
        """
        Initialize the EkaAssist client with connection pooling.

        Args:
            api_url: Base URL for the API
            api_token: API token for authentication
            pool_limits: Optional dict with pool configuration (max_connections, max_keepalive_connections)
            logger: Logger to log information
        """
        self.logger = logger
        self.api_url = api_url
        self.api_token = api_token

        if pool_limits is None:
            pool_limits = {
                "max_connections": 10,
                "max_keepalive_connections": 5,
            }

        limits = httpx.Limits(
            max_connections=pool_limits["max_connections"],
            max_keepalive_connections=pool_limits["max_keepalive_connections"]
        )

        self.client = httpx.Client(
            timeout=30.0,
            limits=limits,
            http2=False
        )

        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

    def close(self):
        """Close the HTTP client and its connection pool when done"""
        self.client.close()

    def __enter__(self):
        """Support for context manager usage with 'with' statement"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensure connection pool is closed when exiting context"""
        self.close()

    def _make_request(self, method: str, endpoint: str, **kwargs):
        """
        Helper method to make HTTP requests and handle errors consistently.

        Args:
            method: HTTP method (get, post, etc.)
            endpoint: API endpoint to call
            **kwargs: Additional arguments to pass to the request

        Returns:
            JSON response data

        Raises:
            httpx.HTTPStatusError: If the request fails
        """

        url = f"{self.api_url}{endpoint}"
        self.logger.info(f"This is the url: {url}")
        try:
            if method.lower() == "get":
                response = self.client.get(url, headers=self.headers, **kwargs)
            elif method.lower() == "post":
                response = self.client.post(url, headers=self.headers, **kwargs)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            self.logger.error(f"API request failed: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during API request: {e}")
            raise

    # Protocol endpoints
    def get_all_supported_tags(self):
        """Gets a list of supported medical conditions from the API."""
        return self._make_request("get", "/protocols/v1/tags")

    def get_all_supported_publishers(self):
        """Gets a list of publishers from the API."""
        return self._make_request("get", "/protocols/v1/publishers")

    def get_protocols(self, arguments: Dict[str, Any]):
        """Get a list of protocols from the API."""
        return self._make_request("post", "/protocols/v1/search", json=arguments)

    def get_protocol_publisher(self, arguments: Dict[str, Any]):
        """Get the list of all publishers for given conditions/tag."""
        return self._make_request("get", "/protocols/v1/publishers/tag", params=arguments)

    # Medication endpoints
    def get_suggested_drugs(self, arguments: Dict[str, Any]):
        """Gets a list of all drugs matching with given name from the API."""
        return self._make_request("get", "/medications/v1/understanding", params=arguments)

    def get_drug_interactions(self, arguments: Dict[str, Any]):
        """Gets a list of all drugs that interact with each other from the API."""
        return self._make_request("post", "/medications/v1/interaction", json=arguments)

    def get_supported_tags(self):
        """
        Gets a list of supported tags/condition names in lowercase.

        Returns:
            List of tags/condition names as strings
        """
        tags = self.get_all_supported_tags()

        supported_tags = []
        for tag in tags:
            # Fixed the method call order: strip() then lower()
            text = tag.get("text", "")
            if not text:
                continue
            supported_tags.append(text)

        self.logger.info(f"Available conditions/tags: {supported_tags}")
        return supported_tags
