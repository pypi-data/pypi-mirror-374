import time
import os
from dotenv import load_dotenv
from pyadaptive.adaptive_auth import AdaptiveAuth

load_dotenv()


def get_auth_instance() -> AdaptiveAuth:
    url = os.getenv("KEYCLOAK_URL")
    client_id = os.getenv("KEYCLOAK_CLIENT_ID")
    client_secret = os.getenv("KEYCLOAK_CLIENT_SECRET")
    realm_name = os.getenv("KEYCLOAK_REALM_NAME")

    assert url is not None
    assert client_id is not None
    assert client_secret is not None
    assert realm_name is not None

    auth = AdaptiveAuth(
        server_url=url,
        client_id=client_id,
        client_secret_key=client_secret,
        realm_name=realm_name,
    )
    return auth


def test_update_token():
    auth = get_auth_instance()
    initial_token = auth.get_token()
    assert initial_token is not None

    # Check if the token returned is the same as initial token since it isn't expired
    token2 = auth.get_token()
    assert token2 is not None
    assert token2 == initial_token

    # Force token to be considered expired
    auth._next_token_time = time.time() - 1  # type: ignore
    # Simulate waiting for the token to expire
    time.sleep(2)

    updated_token = auth.get_token()
    assert updated_token is not None
    assert updated_token != initial_token
