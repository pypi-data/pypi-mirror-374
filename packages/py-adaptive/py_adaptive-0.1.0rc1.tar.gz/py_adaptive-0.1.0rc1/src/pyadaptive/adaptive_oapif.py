from typing import Iterable, Dict
import requests
from .adaptive_types import JsonObject, RecordId, RecordIdList
from .adaptive_auth import AdaptiveAuth


class AdaptiveOapif:
    """Class to interact with Adaptive OGC API - Features endpoints."""

    _tenant: str | None
    _adaptive_auth: AdaptiveAuth | None
    _url: str

    def __init__(
        self,
        url: str,
        adaptive_auth: AdaptiveAuth | None = None,
        tenant: str | None = None,
    ):
        """Initialize the AdaptiveOgcApi class.

        Args:
            url (str): The base URL for the API.
            adaptive_auth (AdaptiveAuth, optional): AdaptiveAuth object configured with the necessary credentials. Defaults to None.
            tenant (str, optional): Adaptive tenant ID. Only required with internal URL.
        """
        self._url = url.rstrip("/") + "/api/core/v1/ogc/features/collections/"
        self._adaptive_auth = adaptive_auth
        self._tenant = tenant

    def _get_headers(self) -> Dict[str, str]:
        head = {"Content-Type": "application/json"}
        if self._adaptive_auth is not None:
            token = self._adaptive_auth.get_token()
            head["Authorization"] = f"Bearer {token}"

        if self._tenant is not None:
            head["X-Gaia-Tenant"] = self._tenant

        return head

    def get_collections(
        self,
    ):
        """Get collections from OGC API

        Returns:
            requests.Response: HTTPS response containing the available collections in the OGC API based on permissions.
        """
        headers = self._get_headers()
        return requests.get(self._url, headers=headers)

    def get_schema(
        self,
        ident: str,
    ) -> requests.Response:
        """Get schema for a specific collection

        Args:
            ident (str): Dataset alias or id

        Returns:
            requests.Response: HTTP response containing the schema for the specified collection.
        """
        headers = self._get_headers()

        return requests.get(
            self._url + ident + "/schema",
            headers=headers,
            timeout=10,
        )

    def get_items_geojson(
        self,
        ident: str,
        bbox: Iterable[float] | None = None,
        bbox_crs: str | None = None,
        datetime: str | None = None,
        filter: str | None = None,
        filter_crs: str | None = None,
        limit: int = 1000,
        offset: int = 0,
        crs: str | None = None,
        properties: Iterable[str] | None = None,
    ) -> requests.Response:
        """Get items from a collection in GeoJSON format

        Args:
            ident (str): Dataset alias or id
            bbox (Iterable[float], optional): Bounding box to filter items. Defaults to None.
            bbox_crs (str, optional): CRS of the bounding box. Defaults to None.
            datetime (str, optional): DateTime filter in ISO 8601 format. Defaults to None.
            filter (str, optional): Additional filter expression.
            filter_crs (str, optional): CRS for the filter expression. Defaults to None.
            limit (int, optional): Maximum number of items to return. Defaults to 1000.
            offset (int, optional): Offset for pagination. Defaults to 0.
            crs (str, optional): Desired CRS for the returned items. Defaults to None, which implies EPSG:4326.
            properties (Iterable[str], optional): List of properties to include in the response. Defaults to None.

        Returns:
            requests.Response: HTTP response containing the items from the specified collection in GeoJSON format.
        """
        headers = self._get_headers()

        return requests.get(
            self._url + ident + "/items",
            headers=headers,
            timeout=10,
            params={
                "bbox": bbox,
                "bbox-crs": bbox_crs,
                "datetime": datetime,
                "filter": filter,
                "filter-crs": filter_crs,
                "limit": limit,
                "offset": offset,
                "crs": crs,
                "properties": ",".join(properties) if properties else None,
            },
        )

    def get_items(
        self,
        ident: str,
        bbox: Iterable[float] | None = None,
        bbox_crs: str | None = None,
        datetime: str | None = None,
        filter: str | None = None,
        filter_crs: str | None = None,
        limit: int = 1000,
        offset: int = 0,
        crs: str | None = None,
        properties: Iterable[str] | None = None,
    ) -> requests.Response:
        """Get items from a collection

        Args:
            ident (str): Dataset alias or id
            bbox (Iterable[float], optional): Bounding box to filter items. Defaults to None.
            bbox_crs (str, optional): CRS of the bounding box. Defaults to None.
            datetime (str, optional): DateTime filter in ISO 8601 format. Defaults to None.
            filter (str, optional): Additional filter expression. Defaults to None.
            filter_crs (str, optional): CRS for the filter expression. Defaults to None.
            limit (int, optional): Maximum number of items to return. Defaults to 1000.
            offset (int, optional): Offset for pagination. Defaults to 0.
            crs (str, optional): Desired CRS for the returned items. Defaults to None, which returns the geometries in their native CRS (schema lookup is necessary).
            properties (Iterable[str], optional): List of properties to include in the response. Defaults to None.

        Returns:
            requests.Response: HTTP response containing the items from the specified collection.
        """
        headers = self._get_headers()

        return requests.get(
            self._url + ident + "/items.json",
            headers=headers,
            timeout=10,
            params={
                "bbox": bbox,
                "bbox-crs": bbox_crs,
                "datetime": datetime,
                "filter": filter,
                "filter-crs": filter_crs,
                "limit": limit,
                "offset": offset,
                "crs": crs,
                "properties": ",".join(properties) if properties else None,
            },
        )

    def get_item_geojson(
        self,
        ident: str,
        id: RecordId,
        crs: str | None = None,
        include_geometries: bool = False,
        properties: Iterable[str] | None = None,
        geometry: str | None = None,
    ) -> requests.Response:
        """Get a specific item from a collection in GeoJSON format

        Args:
            ident (str): Dataset alias or id
            id (RecordId): The ID of the item to retrieve.
            crs (str, optional): Desired CRS for the returned item. Defaults to None.
            include_geometries (bool, optional): Whether to include non-primary geometries in the response. Defaults to False. If True, additional geometries will be included as properties in the GeoJSON response, as GeoJSON geometries.
            properties (Iterable[str], optional): List of properties to include in the response. Defaults to None, which includes all properties.
            geometry (str, optional): Geometry filter in WKT format. Defaults to None.

        Returns:
            requests.Response: HTTP response containing the specified item in GeoJSON format.
        """
        headers = self._get_headers()

        return requests.get(
            self._url + ident + "/items/" + str(id),
            headers=headers,
            params={
                "crs": crs,
                "include-geometries": include_geometries,
                "properties": properties,
                "geometry": geometry,
            },
        )

    def get_item(
        self,
        ident: str,
        id: RecordId,
        crs: str | None = None,
        include_geometries: bool = True,
        properties: Iterable[str] | None = None,
        geometry: str | None = None,
    ) -> requests.Response:
        """Get a specific item from a collection

        Args:
            ident (str): Dataset alias or id
            id (RecordId): The ID of the item to retrieve.
            crs (str, optional): Desired CRS for the returned item. Defaults to None.
            include_geometries (bool, optional): Whether to include geometries in the response. Defaults to True.
            properties (Iterable[str], optional): List of properties to include in the response. Defaults to None, which includes all properties.
            geometry (str, optional): Geometry filter in WKT format. Defaults to None.

        Returns:
            requests.Response: HTTP response containing the specified item.
        """
        headers = self._get_headers()

        return requests.get(
            self._url + ident + "/items/" + str(id) + ".json",
            headers=headers,
            params={
                "crs": crs,
                "include-geometries": include_geometries,
                "properties": properties,
                "geometry": geometry,
            },
        )

    def post_item(self, ident: str, data: JsonObject) -> requests.Response:
        """Create a new item in the specified collection.

        Args:
            ident (str): Dataset alias or id
            data (dict): The item data to create. This must be a JSON object with properties matching the collection schema.

        Returns:
            requests.Response: HTTP response containing the created item id.
        """
        headers = self._get_headers()

        return requests.post(
            self._url + ident + "/items.json", headers=headers, json=data
        )

    def put_item(self, ident: str, id: RecordId, data: JsonObject):
        """Replace an existing item in the specified collection. Note: This will overwrite the entire item.

        Args:
            ident (str): Dataset alias or id
            id (RecordId): The ID of the item to replace.
            data (dict): The new item data. This must be a JSON object with properties matching the collection schema.

        Returns:
            requests.Response: HTTP response containing the updated item.
        """
        headers = self._get_headers()

        return requests.put(
            self._url + ident + "/items/" + str(id) + ".json",
            headers=headers,
            json=data,
        )

    def patch_item(self, ident: str, id: RecordId, data: JsonObject):
        """Update an existing item in the specified collection. Note: This will only update the provided properties, properties set to None will be set to null.

        Args:
            ident (str): Dataset alias or id
            id (RecordId): The ID of the item to update.
            data (dict): The item data to update. This must be a JSON object with properties matching the collection schema.

        Returns:
            requests.Response: HTTP response containing the updated item.
        """
        headers = self._get_headers()

        return requests.patch(
            self._url + ident + "/items/" + str(id) + ".json",
            headers=headers,
            json=data,
        )

    def delete_item(self, ident: str, id: RecordId):
        """Delete an item from the specified collection. Note: Please use the delete_items method for bulk deletes.

        Args:
            ident (str): Dataset alias or id
            id (RecordId): The ID of the item to delete.

        Returns:
            requests.Response: HTTP response indicating the result of the delete operation.
        """
        headers = self._get_headers()

        return requests.delete(self._url + ident + "/items/" + str(id), headers=headers)

    def delete_items(self, alias: str, ids: RecordIdList):
        """Delete multiple items from the specified collection.

        Args:
            alias (str): Dataset alias or id
            ids (list): List of item IDs to delete.

        Returns:
            requests.Response: HTTP response indicating the result of the bulk delete operation.
        """
        headers = self._get_headers()

        jsondata = {"ids": ids}
        url = self._url + alias + "/items/delete/"
        return requests.post(url, headers=headers, json=jsondata)
