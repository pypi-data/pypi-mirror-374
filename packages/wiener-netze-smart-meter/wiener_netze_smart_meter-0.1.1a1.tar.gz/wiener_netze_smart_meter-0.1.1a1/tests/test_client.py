import httpx
import pytest
from pytest_httpx import HTTPXMock

BASE_URL = "https://api.test.com/v1/"

MOCK_METERING_POINTS_RESPONSE = [
    {
        "anlage": {
            "anlage": "ANONYMIZED_ANLAGE",
            "sparte": "STROM",
            "typ": "TAGSTROM",
            "vertraege": [
                {
                    "auszugsdatum": "2024-01-08",
                    "einzugsdatum": "2020-09-03",
                    "vertrag": "ANONYMIZED_VERTRAG_1",
                    "vertragskonto": "ANONYMIZED_KONTO_1"
                },
                {
                    "auszugsdatum": "9999-12-31",
                    "einzugsdatum": "2024-01-09",
                    "vertrag": "ANONYMIZED_VERTRAG_2",
                    "vertragskonto": "ANONYMIZED_KONTO_2"
                }
            ]
        },
        "geraet": {
            "equipmentnummer": "ANONYMIZED_EQUIPMENTNUMMER",
            "geraetenummer": "ANONYMIZED_GERAETENUMMER"
        },
        "verbrauchsstelle": {
            "haus": "ANONYMIZED_HAUS",
            "hausnummer1": "XX",
            "hausnummer2": "",
            "land": "AT",
            "ort": "ANONYMIZED_ORT",
            "postleitzahl": "XXXX",
            "stockwerk": "",
            "strasse": "ANONYMIZED_STRASSE",
            "strasseZusatz": "XX",
            "tuernummer": "XX"
        },
        "idex": {
            "displayLocked": True,
            "customerInterface": "active",
            "granularity": "QUARTER_HOUR"
        },
        "zaehlpunktnummer": "ANONYMIZED_ZAEHLPUNKTNUMMER"
    }
]


@pytest.mark.asyncio
async def test_get_metering_points_success(httpx_mock: HTTPXMock):
    """Test a successfull call to get metering points."""

    httpx_mock.add_response(
        method="GET",
        url=f"{BASE_URL}zaehlpunkte",
        json=MOCK_METERING_POINTS_RESPONSE,
        status_code=200
    )

    async with httpx.AsyncClient(base_url=BASE_URL) as session:
        from wn_smart_meter import WNClient
        from wn_smart_meter.models import MeteringPoint

        client = WNClient(session)

        metering_points = await client.get_metering_points()

        assert isinstance(metering_points, list)
        assert len(metering_points) == 1

        mp = metering_points[0]
        assert isinstance(mp, MeteringPoint)
        assert mp.id == "ANONYMIZED_ZAEHLPUNKTNUMMER"
        assert mp.name is None


@pytest.mark.asyncio
async def test_get_metering_points_unauthorized(httpx_mock: HTTPXMock):
    """Test an unauthorized call to get metering points."""

    httpx_mock.add_response(
        method="GET",
        url=f"{BASE_URL}zaehlpunkte",
        text="Invalid credentials",
        status_code=401
    )

    async with httpx.AsyncClient(base_url=BASE_URL) as session:
        from wn_smart_meter import WNClient
        from wn_smart_meter.exceptions import WNAuthException

        client = WNClient(session)

        with pytest.raises(WNAuthException):
            await client.get_metering_points()
