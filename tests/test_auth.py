import pytest
import time
from unittest.mock import patch, MagicMock

from eka_mcp_server.eka_interface import EkaMCP


@pytest.fixture
def mock_logger():
    return MagicMock()


@pytest.fixture
def mock_client():
    with patch('httpx.Client') as mock:
        client_instance = mock.return_value
        yield client_instance


class TestAuthentication:
    def test_get_client_token(self, mock_logger, mock_client):
        mock_client.post.return_value.status_code = 200
        mock_client.post.return_value.json.return_value = {"access_token": "test", "refresh_token": "test"}

        with patch('eka_mcp_server.eka_mcp.EkaMCP._get_client_token') as mock_refresh:
            mock_refresh.return_value = {"test": "value"}
            with EkaMCP("https://api.eka.care", "id", "secret", mock_logger) as client:
                mock_refresh.assert_called_once()

    def test_get_refresh_token(self, mock_logger, mock_client):
        mock_client.post.return_value.status_code = 200
        mock_client.post.return_value.json.return_value = {
            "access_token": "new_token",
            "refresh_token": "new_refresh",
            "expires_in": 3600
        }
        mock_client.post.return_value.raise_for_status.return_value = False

        with patch('time.time', return_value=1000):
            with patch('eka_mcp_server.eka_mcp.EkaMCP._get_client_token') as mock_token:
                with EkaMCP("https://api.eka.care", "id", "secret", mock_logger) as client:
                    result = client._get_refresh_token({
                        "access_token": "old_token",
                        "refresh_token": "old_refresh"
                    })

                    assert result["access_token"] == "new_token"
                    assert result["refresh_token"] == "new_refresh"
                    assert result["expires_at"] == 4600  # 1000 + 3600

    def test_refresh_auth_token(self, mock_logger, mock_client):
        with patch('eka_mcp_server.eka_mcp.EkaMCP._get_client_token') as mock_token:
            mock_token.return_value = {
                "access_token": "test_token",
                "refresh_token": "refresh_token",
                "expires_at": 9999999900  # Far future
            }

            client = EkaMCP("https://api.eka.care", "id", "secret", mock_logger)

            # Test token not expiring
            with patch('time.time', return_value=9999999999):
                with patch.object(client, '_get_refresh_token') as mock_refresh:
                    client._refresh_auth_token()
                    mock_refresh.assert_not_called()

            # Test token about to expire
            with patch('time.time', return_value=9999999950):
                with patch.object(client, '_get_refresh_token') as mock_refresh:
                    mock_refresh.return_value = {"access_token": "new_token", "refresh_token": "new", "expires_at": 10000000000}
                    client._refresh_auth_token()
                    mock_refresh.assert_called_once()