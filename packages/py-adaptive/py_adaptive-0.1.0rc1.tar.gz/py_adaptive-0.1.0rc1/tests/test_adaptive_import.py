import os
from dotenv import load_dotenv
from test_adaptive_auth import get_auth_instance
from pyadaptive.adaptive_import import AdaptiveImport
from pyadaptive.adaptive_oapif import AdaptiveOapif
from utils import is_success

load_dotenv()

DATASET_ALIAS = os.getenv("DATASET_ALIAS", "py-adaptive-test-dataset")


def get_instances(
    with_auth: bool = True, tenant: str | None = None
) -> tuple[AdaptiveImport, AdaptiveOapif]:
    url = os.getenv("ADAPTIVE_URL")
    assert url is not None

    if not with_auth:
        return (AdaptiveImport(url=url), AdaptiveOapif(url=url))

    auth = get_auth_instance()
    assert auth is not None

    return (
        AdaptiveImport(url=url, adaptive_auth=auth, tenant=tenant),
        AdaptiveOapif(url=url, adaptive_auth=auth, tenant=tenant),
    )


def test_import_items():
    importer, oapif = get_instances(with_auth=True)

    items_to_import = [
        {"title": "Import Test Item 1"},
        {"title": "Import Test Item 2"},
    ]

    response = importer.import_items(
        dataset=DATASET_ALIAS,
        items=items_to_import,
        options={"truncate": True, "resetSerialPrimaryKey": True},
    )
    assert is_success(response.status_code)

    get_items_response = oapif.get_items(ident=DATASET_ALIAS)
    assert is_success(get_items_response.status_code)

    items = get_items_response.json()
    assert "data" in items
    assert len(items["data"]) == 2

    titles = [item["title"] for item in items["data"]]
    assert "Import Test Item 1" in titles
    assert "Import Test Item 2" in titles
