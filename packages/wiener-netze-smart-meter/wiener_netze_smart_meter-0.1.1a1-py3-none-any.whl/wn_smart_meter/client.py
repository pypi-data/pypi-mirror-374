from typing import List
import httpx

from pydantic_core import ValidationError

from .exceptions import WNApiException
from .models import MeteringPoint
from .base_client import BaseClient
from .auth import LogWienTokenAuth
from .constants import DEFAULT_BASE_URL


class WNClient(BaseClient):
    """Asynchronous client for the Wiener Netze Smart Meter API."""

    def __init__(self, session: httpx.AsyncClient):
        """Initialize with an existing httpx.AsyncClient session.

        Args:
            session: Pre-configured httpx.AsyncClient instance
        """
        super().__init__(session)

    @classmethod
    def with_auth(
        cls,
        *,
        client_id: str,
        client_secret: str,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        **kwargs
    ) -> "WNClient":
        """Create a WNClient with authentication configured.

        Args:
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret
            api_key: API gateway key
            base_url: Base URL for the API (defaults to production)
            **kwargs: Additional arguments passed to httpx.AsyncClient (e.g., timeout, follow_redirects)

        Returns:
            WNClient: Configured client instance
        """
        auth = LogWienTokenAuth(
            client_id=client_id,
            client_secret=client_secret,
            api_key=api_key
        )

        session = httpx.AsyncClient(
            base_url=base_url,
            auth=auth,
            **kwargs
        )

        return cls(session)

    async def get_metering_points(self) -> List[MeteringPoint]:
        response = await self._request("GET", "zaehlpunkte")

        try:
            data = response.json()
            return [MeteringPoint.model_validate(item) for item in data]

        except (ValidationError, TypeError) as e:
            raise WNApiException(
                f"Failed to parse metering points: {str(e)}") from e
