import pytest
from wn_smart_meter import WNClient
from wn_smart_meter.auth import LogWienTokenAuth


class TestWNClientAuth:
    """Test authentication integration in WNClient."""

    def test_with_auth_creates_authenticated_client(self):
        """Test that with_auth creates a client with proper authentication."""
        client = WNClient.with_auth(
            client_id="test_client",
            client_secret="test_secret",
            api_key="test_key",
            base_url="https://api.test.com/v1/",
        )

        # Verify client is created correctly
        assert isinstance(client, WNClient)
        assert client._session is not None
        assert client._session.base_url == "https://api.test.com/v1/"
        assert isinstance(client._session.auth, LogWienTokenAuth)

    def test_with_auth_passes_additional_kwargs(self):
        """Test that additional kwargs are passed to httpx.AsyncClient."""
        client = WNClient.with_auth(
            client_id="test_client",
            client_secret="test_secret",
            api_key="test_key",
            base_url="https://api.test.com/v1/",
            follow_redirects=True
        )

        # Verify additional kwargs were passed
        assert client._session.follow_redirects is True

    @pytest.mark.asyncio
    async def test_traditional_initialization_still_works(self):
        """Test that the traditional way of initializing WNClient still works."""
        import httpx

        async with httpx.AsyncClient(base_url="https://api.test.com/v1/") as session:
            client = WNClient(session)
            assert isinstance(client, WNClient)
            assert client._session is session

    def test_auth_instance_configuration(self):
        """Test that the auth instance is properly configured."""
        client = WNClient.with_auth(
            client_id="test_client",
            client_secret="test_secret",
            api_key="test_key",
            base_url="https://api.test.com/v1/",
        )

        auth = client._session.auth
        assert isinstance(auth, LogWienTokenAuth)
        assert auth._client_id == "test_client"
        assert auth._client_secret == "test_secret"
        assert auth._api_key == "test_key"

    def test_with_auth_uses_production_defaults(self):
        """Test that with_auth uses production URLs by default."""
        client = WNClient.with_auth(
            client_id="test_client",
            client_secret="test_secret",
            api_key="test_key"
        )

        # Verify production defaults are used
        assert client._session.base_url == "https://api.wienernetze.at/smart-meter/v1/"

        auth = client._session.auth
        assert auth._token_url == "https://log.wien.gv.at/auth/realms/logwien/protocol/openid-connect/token"

    def test_with_auth_minimal_usage(self):
        """Test that with_auth works with minimal required parameters."""
        client = WNClient.with_auth(
            client_id="my_client",
            client_secret="my_secret",
            api_key="my_key"
        )

        # Verify client is properly configured
        assert isinstance(client, WNClient)
        assert isinstance(client._session.auth, LogWienTokenAuth)
        assert client._session.auth._client_id == "my_client"
        assert client._session.auth._client_secret == "my_secret"
        assert client._session.auth._api_key == "my_key"
