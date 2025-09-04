from typing import List

from pydantic_core import ValidationError

from .exceptions import WNApiException
from .models import MeteringPoint
from .base_client import BaseClient


class WNClient(BaseClient):
    """Asynchronous client for the Wiener Netze Smart Meter API."""

    async def get_metering_points(self) -> List[MeteringPoint]:
        response = await self._request("GET", "zaehlpunkte")

        try:
            data = response.json()
            return [MeteringPoint.model_validate(item) for item in data]

        except (ValidationError, TypeError) as e:
            raise WNApiException(
                f"Failed to parse metering points: {str(e)}") from e
