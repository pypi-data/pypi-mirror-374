from typing import Generator, Optional
import httpx
import time
import logging
from threading import Lock

from .exceptions import WNAuthException
from .constants import DEFAULT_TOKEN_URL, TOKEN_REFRESH_BUFFER


logger = logging.getLogger(__name__)


class LogWienTokenAuth(httpx.Auth):
    """Custom httpx Auth class for handling log wien token authentication.

    This class handles OAuth2 client credentials flow for the Wiener Netze API,
    automatically refreshing tokens when they expire and ensuring thread-safe
    token management.
    """

    def __init__(
        self,
        *,
        token_url: str = DEFAULT_TOKEN_URL,
        client_id: str,
        client_secret: str,
        api_key: str
    ):
        """Initialize the authentication handler.

        Args:
            token_url: OAuth2 token endpoint URL
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret
            api_key: API gateway key
        """
        self._token_url = token_url
        self._client_id = client_id
        self._client_secret = client_secret
        self._api_key = api_key
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0
        self._lock = Lock()  # Thread safety for token refresh

    def auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response, None]:
        """The main authentication flow.

        Automatically refreshes the token if it's expired or about to expire,
        then adds the necessary headers to the request.
        """
        with self._lock:
            if self._needs_token_refresh():
                self._refresh_token()

        request.headers["Authorization"] = f"Bearer {self._access_token}"
        request.headers["x-Gateway-APIKey"] = self._api_key
        yield request

    def _needs_token_refresh(self) -> bool:
        """Check if the token needs to be refreshed."""
        return (
            self._access_token is None or
            self._token_expires_at < (time.time() + TOKEN_REFRESH_BUFFER)
        )

    def _refresh_token(self) -> None:
        """Refresh the access token using OAuth2 client credentials flow.

        Raises:
            WNAuthException: If token refresh fails
        """
        logger.debug("Refreshing access token")

        payload = {
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "grant_type": "client_credentials"
        }

        try:
            response = httpx.post(
                self._token_url,
                data=payload,
            )
            response.raise_for_status()
            token_data = response.json()

        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error during token refresh: {e.response.status_code}")
            raise WNAuthException(
                f"Token refresh failed with status {e.response.status_code}: {e.response.text}"
            ) from e
        except httpx.RequestError as e:
            logger.error(f"Network error during token refresh: {e}")
            raise WNAuthException(
                f"Network error during token refresh: {e}") from e
        except (KeyError, ValueError) as e:
            logger.error(f"Invalid token response format: {e}")
            raise WNAuthException(f"Invalid token response format: {e}") from e

        # Validate response structure
        if "access_token" not in token_data:
            raise WNAuthException(
                "Token response missing 'access_token' field")

        self._access_token = token_data["access_token"]
        expires_in = token_data.get("expires_in", 3600)
        self._token_expires_at = time.time() + expires_in

        logger.debug(
            f"Access token refreshed, expires in {expires_in} seconds")

    def clear_token(self) -> None:
        """Clear the stored token, forcing a refresh on next request."""
        with self._lock:
            self._access_token = None
            self._token_expires_at = 0
            logger.debug("Access token cleared")

    @property
    def is_authenticated(self) -> bool:
        """Check if currently authenticated with a valid token."""
        with self._lock:
            return not self._needs_token_refresh()
