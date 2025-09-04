import os
from dotenv import load_dotenv
from test_adaptive_auth import get_auth_instance
from pyadaptive.adaptive_batch import AdaptiveBatch
from pyadaptive.adaptive_oapif import AdaptiveOapif
from utils import is_success

load_dotenv()

DATASET_ALIAS = os.getenv("DATASET_ALIAS", "py-adaptive-test-dataset")


def get_instances(
    with_auth: bool = True, tenant: str | None = None
) -> tuple[AdaptiveBatch, AdaptiveOapif]:
    url = os.getenv("ADAPTIVE_URL")
    assert url is not None

    if not with_auth:
        return (AdaptiveBatch(url=url), AdaptiveOapif(url=url))

    auth = get_auth_instance()
    assert auth is not None

    return (
        AdaptiveBatch(url=url, adaptive_auth=auth, tenant=tenant),
        AdaptiveOapif(url=url, adaptive_auth=auth, tenant=tenant),
    )


def test_batch_create():
    batch, oapif = get_instances(with_auth=True, tenant="master")

    operations = [
        batch.operation_post(ident=DATASET_ALIAS, data={"title": "Test Item 1"}),
        batch.operation_post(ident=DATASET_ALIAS, data={"title": "Test Item 2"}),
    ]

    response = batch.batch(operations=operations)
    assert is_success(response.status_code)

    response_data = response.json()
    assert len(response_data) == 2

    item_ids: list[int] = []
    for result in response_data:
        assert result["status"] == 201
        item_ids.append(result["data"]["id"])

    for item_id in item_ids:
        get_response = oapif.get_item(ident=DATASET_ALIAS, id=item_id)
        assert is_success(get_response.status_code)
        item_data = get_response.json()
        assert item_data["id"] == item_id
        assert "title" in item_data
        assert item_data["title"] in ["Test Item 1", "Test Item 2"]


def test_batch_update_and_delete():
    batch, oapif = get_instances(with_auth=True, tenant="master")

    # First, create an item to update and delete
    create_response = batch.batch(
        operations=[
            batch.operation_post(ident=DATASET_ALIAS, data={"title": "Item to Update"}),
            batch.operation_post(ident=DATASET_ALIAS, data={"title": "Item to Delete"}),
        ]
    )
    assert is_success(create_response.status_code)
    created_items = create_response.json()
    item_to_update_id = created_items[0]["data"]["id"]
    item_to_delete_id = created_items[1]["data"]["id"]

    # Now, update and delete the items using batch operations
    operations = [
        batch.operation_patch(
            ident=DATASET_ALIAS,
            id=item_to_update_id,
            data={"title": "Updated Item Name"},
        ),
        batch.operation_delete(ident=DATASET_ALIAS, id=item_to_delete_id),
    ]

    response = batch.batch(operations=operations)
    assert is_success(response.status_code)

    response_data = response.json()
    assert len(response_data) == 2

    # Verify the update operation
    update_result = response_data[0]
    assert is_success(update_result["status"])

    get_response = oapif.get_item(ident=DATASET_ALIAS, id=item_to_update_id)
    assert is_success(get_response.status_code)
    item_data = get_response.json()
    assert item_data["id"] == item_to_update_id
    assert item_data["title"] == "Updated Item Name"

    # Verify the delete operation
    delete_result = response_data[1]
    assert delete_result["status"] == 204

    get_response = oapif.get_item(ident=DATASET_ALIAS, id=item_to_delete_id)
    assert get_response.status_code == 404
