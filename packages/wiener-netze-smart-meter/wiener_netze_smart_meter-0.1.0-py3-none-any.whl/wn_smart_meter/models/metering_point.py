from typing import Optional
from pydantic import BaseModel, Field

from .device import Device


class MeteringPoint(BaseModel):
    """Represents a single, unique metering point.

    This is the central model that ties together the location, device,
    and installation details. Corresponds to the 'Zaehlpunkt' model from the API.
    """

    id: str = Field(..., alias="zaehlpunktnummer")
    name: Optional[str] = Field(None, alias="zaehlpunktname")
    device: Device = Field(..., alias="geraet")
