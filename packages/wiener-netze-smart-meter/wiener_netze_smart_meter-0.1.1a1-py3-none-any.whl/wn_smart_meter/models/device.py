from pydantic import BaseModel, Field


class Device(BaseModel):
    """Represents a physical metering device.

    Contains details about the physical hardware. Corresponds to the 'Geraet'
    model from the API.
    """

    id: str = Field(..., alias="geraetenummer")
    equipment_number: str = Field(..., alias="equipmentnummer")
