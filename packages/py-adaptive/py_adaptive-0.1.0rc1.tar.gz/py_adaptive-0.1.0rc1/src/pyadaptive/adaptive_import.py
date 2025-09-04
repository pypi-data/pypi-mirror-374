from typing import Iterable, Dict, Tuple
import json
import requests

from .adaptive_types import JsonObject
from .adaptive_auth import AdaptiveAuth

FileTuple = Tuple[str, str | bytes, str]  # (filename, filecontent, mimetype)


class AdaptiveImport:
    """Class to handle data import operations with Adaptive."""

    _tenant: str | None
    _adaptive_auth: AdaptiveAuth | None
    _url: str

    def __init__(
        self,
        url: str,
        adaptive_auth: AdaptiveAuth | None = None,
        tenant: str | None = None,
    ):
        """Initialize the AdaptiveImport class.

        Args:
            url (str): The base URL for the Adaptive OGC API.
            adaptive_auth (AdaptiveAuth): An instance of AdaptiveAuth for authentication.
            tenant (str | None, optional): The tenant identifier for multi-tenant setups. Defaults to None.
        """
        self._url = url.rstrip("/") + "/api/import/v1/dataset/"
        self._adaptive_auth = adaptive_auth
        self._tenant = tenant

    def _get_headers(self) -> Dict[str, str]:
        headers: Dict[str, str] = {}
        if self._adaptive_auth is not None:
            token = self._adaptive_auth.get_token()
            headers["Authorization"] = f"Bearer {token}"

        if self._tenant is not None:
            headers["X-Gaia-Tenant"] = self._tenant

        return headers

    def import_items(
        self,
        dataset: str,
        items: Iterable[JsonObject],
        options: JsonObject | None = None,
    ) -> requests.Response:
        """Import items to a specified dataset. The items are plain JSON features. Geometries need to be WKT.

        Args:
            dataset (str): The dataset alias to import the items into.
            items (Iterable[JsonDict]): An iterable of items (features) to be imported.
            options (JsonDict): Additional import options as a dictionary.

        Returns:
            requests.Response: The response object from the import request.
        """
        file = ("data.json", json.dumps(items), "application/json")
        return self.import_file(dataset, file, options)

    def import_file(
        self,
        dataset: str,
        files: FileTuple | list[FileTuple],
        options: JsonObject | None = None,
    ) -> requests.Response:
        """Import a geodata file (or files, for unzipped Shapefile) to a specified dataset.

        Args:
            dataset (str): The dataset alias to import the file(s) into.
            files (FileTuple | list[FileTuple]): A single file tuple or a list of file tuples to be imported.
            options (JsonDict): Additional import options as a dictionary.

        Returns:
            requests.Response: The response object from the import request.
        """
        url = self._url + dataset
        headers = self._get_headers()

        files_req = {}
        if isinstance(files, tuple):
            files_req["files"] = files
        elif len(files) == 1:
            files_req["files"] = files[0]
        else:
            for i, file in enumerate(files):
                files_req[f"files[{i}]"] = file

        data = {"options": json.dumps(options or {})}

        req = requests.Request(
            "POST",
            url,
            headers=headers,
            files=files_req,
            data=data,
        )
        prepared = req.prepare()

        response = requests.Session().send(prepared)
        return response
