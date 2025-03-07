import sys
import time
from logging import Logger
from typing import Dict, Any, Optional

import httpx

class RefreshTokenError(Exception):
    pass

class CreateTokenError(Exception):
    pass

class EkaMCP:
    def __init__(self, eka_api_host: str, client_id: str, client_secret: str, logger: Logger):
        """
        Initialize the EkaAssist client with connection pooling.

        Args:
            eka_api_host: Base URL for the API
            client_id: Client ID
            client_secret: Client client_secret for authentication
            logger: Logger to log information
        """

        self.logger = logger
        self.client = httpx.Client(
            timeout=30.0,
            limits=httpx.Limits(
                max_connections=10,
                max_keepalive_connections=5
            ),
            http2=False
        )

        self.api_url = eka_api_host
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_creds = self._get_client_token()

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
            RefreshTokenError: If the refresh token request fails
        """
        url = f"{self.api_url}/connect-auth/v1/account/refresh"
        data = {
            "access_token": auth_creds["access_token"],
            "refresh_token": auth_creds["refresh_token"],
        }

        current_time = int(time.time())
        try:
            resp = self.client.post(url, json=data)
            resp.raise_for_status()

            creds = resp.json()
            creds["expires_at"] = current_time + creds["expires_in"]
            return creds
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Token refresh failed: {e}")
            raise RefreshTokenError(f"Failed to refresh token: {str(e)}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error during token refresh: {e}")
            raise RefreshTokenError(f"Unexpected error: {str(e)}") from e

    def _get_client_token(self):
        """
        Authenticate with the Eka API using client credentials and obtain a valid token.

        Returns:
            Dictionary containing authentication credentials with expiration time

        Raises:
            CreateTokenError: If the request to create a token fails
        """
        url = f"{self.api_url}/connect-auth/v1/account/login"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        try:
            resp = self.client.post(url, json=data)
            resp.raise_for_status()
            return self._get_refresh_token(resp.json())
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Client token creation failed: {e}")
            raise CreateTokenError(f"Failed to create token: {str(e)}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error during token creation: {e}")
            raise CreateTokenError(f"Unexpected error: {str(e)}") from e


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
        url = f"{self.api_url}/eka-mcp/{endpoint}"
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
        return self._make_request("get", "medications/v1/search", params=arguments)

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

        self.logger.info(f"Available tags: {supported_tags}")
        return supported_tags
