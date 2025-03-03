import sys
import time
from logging import Logger
from typing import Dict, Any, Optional

import httpx


class EkaMCP:
    def __init__(self, client_id: str, client_token: str, logger: Logger, pool_limits: Optional[Dict[str, int]] = None):
        """
        Initialize the EkaAssist client with connection pooling.

        Args:
            api_url: Base URL for the API
            api_token: API token for authentication
            pool_limits: Optional dict with pool configuration (max_connections, max_keepalive_connections)
            logger: Logger to log information
        """
        self.logger = logger
        self.api_url = "https://api.dev.eka.care"
        self.client_id = client_id
        self.client_token = client_token

        self.auth_creds = self._get_client_token()

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

    def close(self):
        """Close the HTTP client and its connection pool when done"""
        self.client.close()

    def __enter__(self):
        """Support for context manager usage with 'with' statement"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensure connection pool is closed when exiting context"""
        self.close()


    def _get_refresh_token(self, auth_creds):
        """
        Refresh the authentication token using the provided credentials.

        Args:
            auth_creds: Dictionary containing access_token and refresh_token

        Returns:
            Dictionary containing refreshed authentication credentials with expiration time

        Raises:
            SystemExit: If the refresh token request fails
        """

        url = f"{self.api_url}/connect-auth/v1/account/refresh"
        data = {
            "access_token": auth_creds["access_token"],
            "refresh_token": auth_creds["refresh_token"],
        }

        current_time = int(time.time())
        resp = self.client.post(url, json=data)
        if resp.status_code != 200:
            self.logger.error(f"Failed to Get Eka Refresh token: {resp.text}")
            sys.exit(1)

        creds = resp.json()
        creds["expires_at"] = current_time + creds["expires_in"]
        return creds

    def _get_client_token(self):
        """
       Authenticate with the Eka API using client credentials and obtain a valid token.

       Returns:
           Dictionary containing authentication credentials with expiration time

       Raises:
           SystemExit: If authentication fails due to invalid credentials
       """

        url = f"{self.api_url}/connect-auth/v1/account/login"
        data = {
            "client_id": {self.client_id},
            "client_secret": {self.client_token}
        }

        resp = self.client.post(url, json=data)
        if resp.status_code != 200:
            self.logger.error(f"Invalid Eka MCP credentials: {resp.text}")
            sys.exit(1)

        return self._get_refresh_token(resp.json())


    def _refresh_auth_token(self):
        """
        Validate the current authentication token and refresh it if it's about to expire.

        Updates self.auth_creds with new credentials if the current token is expiring within 60 seconds.
        """

        auth_creds = self.auth_creds
        current_time = int(time.time())

        if current_time - auth_creds["expires_at"] <= 60:
            self.auth_creds = self._get_refresh_token(auth_creds)

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

        self._refresh_auth_token()

        headers = {
            "Authorization": f"Bearer {self.auth_creds['access_token']}",
            "Content-Type": "application/json"
        }
        url = f"{self.api_url}/eka_mcp/{endpoint}"
        self.logger.info(f"This is the url: {url}")
        try:
            if method.lower() == "get":
                response = self.client.get(url, headers=headers, **kwargs)
            elif method.lower() == "post":
                response = self.client.post(url, headers=headers, **kwargs)
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
        return self._make_request("get", "protocols/v1/tags")

    def get_all_supported_publishers(self):
        """Gets a list of publishers from the API."""
        return self._make_request("get", "protocols/v1/publishers")

    def get_protocols(self, arguments: Dict[str, Any]):
        """Get a list of protocols from the API."""
        return self._make_request("post", "protocols/v1/search", json=arguments)

    def get_protocol_publisher(self, arguments: Dict[str, Any]):
        """Get the list of all publishers for given conditions/tag."""
        return self._make_request("get", "protocols/v1/publishers/tag", params=arguments)

    # Medication endpoints
    def get_suggested_drugs(self, arguments: Dict[str, Any]):
        """Gets a list of all drugs matching with given name from the API."""
        return self._make_request("get", "medications/v1/understanding", params=arguments)

    def get_drug_interactions(self, arguments: Dict[str, Any]):
        """Gets a list of all drugs that interact with each other from the API."""
        return self._make_request("post", "medications/v1/interaction", json=arguments)

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
