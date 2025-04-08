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
        mock_client.post.return_value.json.return_value = {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
            "refresh_token": "c1d5f87725084e69abe00731bb696758"
        }

        with patch('eka_mcp_server.eka_interface.EkaMCP._get_client_token') as mock_refresh:
            mock_refresh.return_value = {"access_token": "value", "refresh_token": "value"}
            with EkaMCP("https://api.eka.care", "id", "secret", mock_logger) as client:
                mock_refresh.assert_called_once()

    def test_get_refresh_token(self, mock_logger, mock_client):
        mock_client.post.return_value.status_code = 200
        mock_client.post.return_value.json.return_value = {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
            "refresh_token": "c1d5f87725084e69abe00731bb696758"
        }

        with patch('time.time', return_value=1000):
            with patch('eka_mcp_server.eka_interface.EkaMCP._get_client_token') as mock_token:
                with EkaMCP("https://api.eka.care", "id", "secret", mock_logger) as client:
                    result = client._get_refresh_token({
                        "access_token": "old_token",
                        "refresh_token": "old_refresh"
                    })

                    assert result["access_token"] == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
                    assert result["refresh_token"] == "c1d5f87725084e69abe00731bb696758"