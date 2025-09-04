import time
from keycloak import KeycloakOpenID


class AdaptiveAuth:
    """Class to handle authentication with Keycloak for Adaptive OGC API."""

    _keycloak_openid: KeycloakOpenID
    _access_token: str | None
    _next_token_time: float

    def __init__(
        self, server_url: str, client_id: str, client_secret_key: str, realm_name: str
    ):
        """Initialize the AdaptiveAuth class.

        Args:
            server_url (str): The Keycloak server URL.
            client_id (str): The client ID for the Keycloak client.
            client_secret_key (str): The client secret key for the Keycloak client.
            realm_name (str): The realm name in Keycloak where the client is registered.
        """
        self._keycloak_openid = KeycloakOpenID(
            server_url=server_url,
            client_id=client_id,
            client_secret_key=client_secret_key,
            realm_name=realm_name,
        )
        self._access_token = None
        self._next_token_time = 0

    def _authenticate_client(self) -> str:
        token = self._keycloak_openid.token(grant_type="client_credentials")  # type: ignore

        self._next_token_time = time.time() + token["expires_in"] - 10
        self._access_token = token["access_token"]

        return self._access_token  # type: ignore

    def get_token(self) -> str:
        """Get or update access token.

        Returns:
            str: The existing or updated access token, depending on whether it was near expiration.
        """
        if self._access_token is None or time.time() > self._next_token_time:
            return self._authenticate_client()

        return self._access_token

    def get_token_renews_after(self) -> float | None:
        """Get the token renewal time.

        Returns:
            float | None: The time (in seconds since epoch) when the token will need to be renewed, or None if no token is set.
        """
        if self._access_token is None:
            return None

        return self._next_token_time
