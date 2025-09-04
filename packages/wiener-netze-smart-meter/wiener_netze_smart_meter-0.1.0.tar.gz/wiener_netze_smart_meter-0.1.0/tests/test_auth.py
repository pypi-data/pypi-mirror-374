import time
import httpx
import pytest
from pytest_httpx import HTTPXMock
import concurrent.futures

from wn_smart_meter.auth import LogWienTokenAuth
from wn_smart_meter.exceptions import WNAuthException


# Test constants
TEST_TOKEN_URL = "https://auth.example.com/oauth/token"
TEST_CLIENT_ID = "test_client_id"
TEST_CLIENT_SECRET = "test_client_secret"
TEST_API_KEY = "test_api_key"
TEST_TIMEOUT = 30.0

TEST_ACCESS_TOKEN = "test_access_token_12345"
TEST_TOKEN_TYPE = "Bearer"
TEST_EXPIRES_IN_DEFAULT = 3600
TEST_EXPIRES_IN_CUSTOM = 7200

TEST_API_URL = "https://api.example.com/test"
TEST_GRANT_TYPE = "client_credentials"

# Error messages
ERROR_MSG_UNAUTHORIZED = "Unauthorized"
ERROR_MSG_INVALID_JSON = "invalid json content"
ERROR_MSG_NETWORK_ERROR = "Network error"

# HTTP status codes
HTTP_OK = 200
HTTP_UNAUTHORIZED = 401

# Time constants
TIME_BUFFER = 60  # Should match LogWienTokenAuth.TOKEN_REFRESH_BUFFER
TIME_OFFSET_PAST = 100
TIME_OFFSET_FUTURE = 100
TIME_TOLERANCE = 1


@pytest.fixture
def auth_handler():
    """Create a LogWienTokenAuth instance for testing."""
    return LogWienTokenAuth(
        token_url=TEST_TOKEN_URL,
        client_id=TEST_CLIENT_ID,
        client_secret=TEST_CLIENT_SECRET,
        api_key=TEST_API_KEY,
        timeout=TEST_TIMEOUT
    )


@pytest.fixture
def mock_token_response():
    """Mock token response data."""
    return {
        "access_token": TEST_ACCESS_TOKEN,
        "token_type": TEST_TOKEN_TYPE,
        "expires_in": TEST_EXPIRES_IN_DEFAULT
    }


class TestLogWienTokenAuth:
    """Test suite for LogWienTokenAuth class."""

    def test_initialization(self, auth_handler):
        """Test proper initialization of LogWienTokenAuth."""
        assert auth_handler._token_url == TEST_TOKEN_URL
        assert auth_handler._client_id == TEST_CLIENT_ID
        assert auth_handler._client_secret == TEST_CLIENT_SECRET
        assert auth_handler._api_key == TEST_API_KEY
        assert auth_handler._timeout == TEST_TIMEOUT
        assert auth_handler._access_token is None
        assert auth_handler._token_expires_at == 0

    def test_auth_flow_with_token_refresh(self, auth_handler, mock_token_response, httpx_mock: HTTPXMock):
        """Test complete auth flow including token refresh."""
        # Mock successful token refresh
        httpx_mock.add_response(
            method="POST",
            url=TEST_TOKEN_URL,
            json=mock_token_response,
            status_code=HTTP_OK
        )

        # Create and authenticate a request
        request = httpx.Request("GET", TEST_API_URL)
        auth_generator = auth_handler.auth_flow(request)
        authenticated_request = next(auth_generator)

        # Verify headers were added correctly
        assert authenticated_request.headers[
            "Authorization"] == f"Bearer {TEST_ACCESS_TOKEN}"
        assert authenticated_request.headers["x-Gateway-APIKey"] == TEST_API_KEY

        # Verify token was stored and request was made
        assert auth_handler._access_token == TEST_ACCESS_TOKEN
        assert auth_handler._token_expires_at > time.time()

    def test_auth_flow_with_existing_valid_token(self, auth_handler):
        """Test auth flow when token is already valid (no refresh needed)."""
        # Set valid token
        auth_handler._access_token = "existing_token"
        auth_handler._token_expires_at = time.time() + TIME_BUFFER + TIME_OFFSET_FUTURE

        # Create and authenticate a request
        request = httpx.Request("GET", TEST_API_URL)
        auth_generator = auth_handler.auth_flow(request)
        authenticated_request = next(auth_generator)

        # Verify headers were added correctly
        assert authenticated_request.headers["Authorization"] == "Bearer existing_token"
        assert authenticated_request.headers["x-Gateway-APIKey"] == TEST_API_KEY

    def test_token_refresh_error_handling(self, auth_handler, httpx_mock: HTTPXMock):
        """Test error handling during token refresh."""
        # Test HTTP error
        httpx_mock.add_response(
            method="POST",
            url=TEST_TOKEN_URL,
            text=ERROR_MSG_UNAUTHORIZED,
            status_code=HTTP_UNAUTHORIZED
        )

        with pytest.raises(WNAuthException) as exc_info:
            auth_handler._refresh_token()

        assert f"Token refresh failed with status {HTTP_UNAUTHORIZED}" in str(
            exc_info.value)
        assert ERROR_MSG_UNAUTHORIZED in str(exc_info.value)

    def test_token_refresh_network_error(self, auth_handler, httpx_mock: HTTPXMock):
        """Test network error handling during token refresh."""
        httpx_mock.add_exception(
            httpx.RequestError(ERROR_MSG_NETWORK_ERROR),
            method="POST",
            url=TEST_TOKEN_URL
        )

        with pytest.raises(WNAuthException) as exc_info:
            auth_handler._refresh_token()

        assert "Network error during token refresh" in str(exc_info.value)

    def test_token_refresh_invalid_response(self, auth_handler, httpx_mock: HTTPXMock):
        """Test handling of invalid token response."""
        # Test invalid JSON
        httpx_mock.add_response(
            method="POST",
            url=TEST_TOKEN_URL,
            text=ERROR_MSG_INVALID_JSON,
            status_code=HTTP_OK
        )

        with pytest.raises(WNAuthException) as exc_info:
            auth_handler._refresh_token()

        assert "Invalid token response format" in str(exc_info.value)

    def test_token_refresh_missing_access_token(self, auth_handler, httpx_mock: HTTPXMock):
        """Test handling of response missing access_token."""
        httpx_mock.add_response(
            method="POST",
            url=TEST_TOKEN_URL,
            json={"token_type": TEST_TOKEN_TYPE,
                  "expires_in": TEST_EXPIRES_IN_DEFAULT},
            status_code=HTTP_OK
        )

        with pytest.raises(WNAuthException) as exc_info:
            auth_handler._refresh_token()

        assert "Token response missing 'access_token' field" in str(
            exc_info.value)

    def test_token_expiry_handling(self, auth_handler):
        """Test token expiry detection and refresh logic."""
        # Test no token (needs refresh)
        assert auth_handler._needs_token_refresh() is True

        # Test expired token (needs refresh)
        auth_handler._access_token = "expired_token"
        auth_handler._token_expires_at = time.time() - TIME_OFFSET_PAST
        assert auth_handler._needs_token_refresh() is True

        # Test valid token (no refresh needed)
        auth_handler._access_token = "valid_token"
        auth_handler._token_expires_at = time.time() + TIME_BUFFER + TIME_OFFSET_FUTURE
        assert auth_handler._needs_token_refresh() is False

        # Test token near expiry (needs refresh due to buffer)
        auth_handler._token_expires_at = time.time() + TIME_BUFFER - 10
        assert auth_handler._needs_token_refresh() is True

    def test_token_management_operations(self, auth_handler, mock_token_response, httpx_mock: HTTPXMock):
        """Test token storage, clearing, and authentication status."""
        # Initially not authenticated
        assert auth_handler.is_authenticated is False

        # Mock token refresh and get token
        httpx_mock.add_response(
            method="POST",
            url=TEST_TOKEN_URL,
            json=mock_token_response,
            status_code=HTTP_OK
        )
        auth_handler._refresh_token()

        # Should be authenticated after successful token refresh
        assert auth_handler.is_authenticated is True
        assert auth_handler._access_token == TEST_ACCESS_TOKEN

        # Clear token
        auth_handler.clear_token()
        assert auth_handler._access_token is None
        assert auth_handler._token_expires_at == 0
        assert auth_handler.is_authenticated is False

    def test_custom_expires_in_handling(self, auth_handler, httpx_mock: HTTPXMock):
        """Test handling of custom expires_in values and defaults."""
        # Test custom expires_in
        custom_response = {
            "access_token": "custom_token",
            "expires_in": TEST_EXPIRES_IN_CUSTOM
        }
        httpx_mock.add_response(
            method="POST",
            url=TEST_TOKEN_URL,
            json=custom_response,
            status_code=HTTP_OK
        )

        start_time = time.time()
        auth_handler._refresh_token()
        expected_expiry = start_time + TEST_EXPIRES_IN_CUSTOM
        assert abs(auth_handler._token_expires_at -
                   expected_expiry) < TIME_TOLERANCE

        # Clear and test default expires_in
        auth_handler.clear_token()
        default_response = {"access_token": "default_token"}
        httpx_mock.add_response(
            method="POST",
            url=TEST_TOKEN_URL,
            json=default_response,
            status_code=HTTP_OK
        )

        start_time = time.time()
        auth_handler._refresh_token()
        expected_expiry = start_time + TEST_EXPIRES_IN_DEFAULT
        assert abs(auth_handler._token_expires_at -
                   expected_expiry) < TIME_TOLERANCE

    def test_thread_safety(self, auth_handler, mock_token_response, httpx_mock: HTTPXMock):
        """Test thread safety of concurrent token operations."""
        httpx_mock.add_response(
            method="POST",
            url=TEST_TOKEN_URL,
            json=mock_token_response,
            status_code=HTTP_OK
        )

        def trigger_auth_flow():
            """Function to trigger auth flow in a thread."""
            request = httpx.Request("GET", TEST_API_URL)
            auth_generator = auth_handler.auth_flow(request)
            return next(auth_generator)

        # Run multiple threads that should trigger token refresh
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(trigger_auth_flow) for _ in range(3)]
            results = [future.result()
                       for future in concurrent.futures.as_completed(futures)]

        # All requests should have the same token
        tokens = [req.headers["Authorization"] for req in results]
        assert len(set(tokens)) == 1  # All tokens should be the same
        assert tokens[0] == f"Bearer {TEST_ACCESS_TOKEN}"
