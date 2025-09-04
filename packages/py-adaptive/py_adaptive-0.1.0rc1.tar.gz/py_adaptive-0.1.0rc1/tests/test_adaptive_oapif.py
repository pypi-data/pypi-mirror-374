import os
from dotenv import load_dotenv
from test_adaptive_auth import get_auth_instance
from pyadaptive.adaptive_oapif import AdaptiveOapif
from utils import is_success

load_dotenv()

DATASET_ALIAS = os.getenv("DATASET_ALIAS", "py-adaptive-test-dataset")


def get_instance(with_auth: bool = True, tenant: str | None = None) -> AdaptiveOapif:
    url = os.getenv("ADAPTIVE_URL")
    assert url is not None

    if not with_auth:
        return AdaptiveOapif(url=url)

    auth = get_auth_instance()
    assert auth is not None

    return AdaptiveOapif(url=url, adaptive_auth=auth, tenant=tenant)


def test_header_with_auth():
    api = get_instance(with_auth=True)
    assert api is not None

    headers = api._get_headers()  # type: ignore
    assert "Authorization" in headers
    assert headers["Authorization"].startswith("Bearer ")
    assert len(headers["Authorization"]) > 10


def test_header_with_tenant():
    api = get_instance(with_auth=True, tenant="master")
    assert api is not None

    headers = api._get_headers()  # type: ignore
    assert "X-Gaia-Tenant" in headers
    assert headers["X-Gaia-Tenant"] == "master"


def test_get_collections():
    api = get_instance(with_auth=True)
    assert api is not None

    response = api.get_collections()
    assert is_success(response.status_code)

    response = response.json()

    assert "collections" in response
    assert isinstance(response["collections"], list)


def test_get_schema():
    api = get_instance(with_auth=True)
    assert api is not None

    response = api.get_schema(ident=DATASET_ALIAS)
    assert is_success(response.status_code)

    response = response.json()
    assert "properties" in response
    assert isinstance(response["properties"], dict)


def test_get_items():
    api = get_instance(with_auth=True)
    assert api is not None

    response = api.get_items(ident=DATASET_ALIAS)
    assert is_success(response.status_code)

    response = response.json()
    assert "data" in response
    assert isinstance(response["data"], list)


def test_post_item():
    api = get_instance(with_auth=True)
    assert api is not None

    item_data = {
        "title": "Testing",
        "description": "This is a description",
        "point": "POINT(58.45961 8.77323)",
    }
    response = api.post_item(ident=DATASET_ALIAS, data=item_data)

    assert is_success(response.status_code)

    json = response.json()
    assert "id" in json

    item_id = json.get("id")
    get_response = api.get_item(ident=DATASET_ALIAS, id=item_id)
    assert is_success(get_response.status_code)

    get_data = get_response.json()
    assert get_data["title"] == "Testing"
    assert get_data["description"] == "This is a description"
    assert get_data["point"] == "POINT(58.45961 8.77323)"


def test_put_item():
    api = get_instance(with_auth=True)
    assert api is not None

    # First, create an item to update
    item_data = {
        "title": "Testing for PUT",
        "description": "This is a description for PUT",
        "point": "POINT(58.45961 8.77323)",
    }
    post_response = api.post_item(ident=DATASET_ALIAS, data=item_data)
    assert is_success(post_response.status_code)
    item_id = post_response.json().get("id")
    assert item_id is not None

    # Now, update the created item
    updated_data = {
        "title": "Updated Title",
        "description": "Updated description",
        "point": "POINT(59 9)",
    }
    put_response = api.put_item(ident=DATASET_ALIAS, id=item_id, data=updated_data)
    assert is_success(put_response.status_code)

    get_response = api.get_item(ident=DATASET_ALIAS, id=item_id)
    assert is_success(get_response.status_code)

    item = get_response.json()

    assert item["title"] == "Updated Title"
    assert item["description"] == "Updated description"
    assert item["point"] == "POINT(59 9)"


def test_delete_item():
    api = get_instance(with_auth=True)
    assert api is not None

    # First, create an item to delete
    item_data = {
        "title": "Testing for DELETE",
        "description": "This is a description for DELETE",
        "point": "POINT(58.45961 8.77323)",
    }
    post_response = api.post_item(ident=DATASET_ALIAS, data=item_data)
    assert is_success(post_response.status_code)
    item_id = post_response.json().get("id")
    assert item_id is not None

    # Now, delete the created item
    delete_response = api.delete_item(ident=DATASET_ALIAS, id=item_id)
    assert is_success(delete_response.status_code)

    # Verify the item has been deleted
    get_response = api.get_item(ident=DATASET_ALIAS, id=item_id)
    assert get_response.status_code == 404
