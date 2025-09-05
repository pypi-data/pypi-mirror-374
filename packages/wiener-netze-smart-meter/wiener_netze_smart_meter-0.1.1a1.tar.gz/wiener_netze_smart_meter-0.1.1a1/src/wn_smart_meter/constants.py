"""Constants for the Wiener Netze Smart Meter API client."""

# Production API URLs
DEFAULT_BASE_URL = "https://api.wienernetze.at/smart-meter/v1/"
DEFAULT_TOKEN_URL = "https://log.wien.gv.at/auth/realms/logwien/protocol/openid-connect/token"

# Token refresh buffer (seconds before expiry to refresh proactively)
TOKEN_REFRESH_BUFFER = 60
