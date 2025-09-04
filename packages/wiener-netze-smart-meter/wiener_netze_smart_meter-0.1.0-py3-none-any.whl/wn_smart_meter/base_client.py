from abc import ABC
from typing import Any
from typing_extensions import Literal

import httpx

from .exceptions import WNApiException, WNAuthException, WNNetworkException

HttpMethods = Literal["GET", "POST", "PUT", "DELETE", "PATCH"]


class BaseClient(ABC):
    """An abstract base class for building asynchronous API clients."""

    def __init__(self, session: httpx.AsyncClient):
        self._session = session

    async def _request(self, method: HttpMethods, endpoint: str, *, params: dict[str, Any] | None = None, json: dict[str, Any] | None = None) -> httpx.Response:
        """Make an HTTP request to the specified endpoint.

        Args:
            method (HttpMethods): The HTTP method to use (GET, POST, etc.).
            endpoint (str): The API endpoint to target.
            params (dict[str, any] | None): Query parameters for the request.
            json (dict[str, any] | None): JSON body for the request.

        Returns:
            httpx.Response: The response from the API.

        Raises:
            WNAuthException: For authentication errors (401, 403).
        """
        try:
            response = await self._session.request(method, endpoint, params=params, json=json)

            if response.status_code in {401, 403}:
                raise WNAuthException(
                    f"Authentication failed: {response.status_code} - {response.text}")

            response.raise_for_status()

            return response
        except httpx.HTTPStatusError as e:
            raise WNApiException(
                f"API error: {e.response.status_code} - {e.response.text}") from e
        except httpx.RequestError as e:
            raise WNNetworkException(f"Network error: {str(e)}") from e
