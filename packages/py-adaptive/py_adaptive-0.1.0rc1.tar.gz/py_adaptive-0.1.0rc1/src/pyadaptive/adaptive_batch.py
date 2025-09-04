from typing import Iterable
import json
import requests
from enum import StrEnum
from .adaptive_types import JsonObject, RecordId
from .adaptive_auth import AdaptiveAuth


class BatchOperationMethod(StrEnum):
    """Enum for batch operations."""

    post = "post"
    put = "put"
    patch = "patch"
    delete = "delete"


JsonRef = dict[str, str]  # {"$ref": "<resultId>"}


class BatchOperation:
    """Class representing a single batch operation."""

    operation: BatchOperationMethod
    dataset: str
    data: JsonObject | None
    id: RecordId | JsonRef | None
    resultId: str | None

    def __init__(
        self,
        operation: BatchOperationMethod,
        dataset: str,
        data: JsonObject | None = None,
        id: RecordId | JsonRef | None = None,
        resultId: str | None = None,
    ):
        self.operation = operation
        self.dataset = dataset
        self.data = data
        self.id = id
        self.resultId = resultId

    def to_dict(self) -> JsonObject:
        result: JsonObject = {
            "operation": self.operation.value,
            "dataset": self.dataset,
        }
        if self.data is not None:
            result["data"] = self.data
        if self.id is not None:
            result["id"] = self.id
        if self.resultId is not None:
            result["$resultId"] = self.resultId
        return result


class AdaptiveBatch:
    """Class to handle batch operations with Adaptive."""

    _adaptive_auth: AdaptiveAuth | None
    _tenant: str | None
    _url: str

    def __init__(
        self,
        url: str,
        adaptive_auth: AdaptiveAuth | None = None,
        tenant: str | None = None,
    ):
        """Initialize the AdaptiveBatch class.

        Args:
            url (str): The base URL for the Adaptive OGC API.
            adaptive_auth (AdaptiveAuth | None, optional): An instance of AdaptiveAuth for authentication. Defaults to None.
            tenant (str | None, optional): The tenant identifier for multi-tenant setups. Defaults to None.
        """
        self._url = url.rstrip("/") + "/api/core/v1/ogc/features/collections"
        self._adaptive_auth = adaptive_auth
        self._tenant = tenant

    def batch_raw(self, data: str) -> requests.Response:
        """Sends prepared batch operations in NDJSON format.

        Args:
            data (str): The batch operations in NDJSON format.

        Returns:
            requests.Response: The response object from the batch request.
        """
        headers = {"Content-Type": "application/ndjson"}

        if self._adaptive_auth is not None:
            token = self._adaptive_auth.get_token()
            headers["Authorization"] = f"Bearer {token}"

        return requests.patch(self._url, headers=headers, data=data)

    def batch(self, operations: Iterable[BatchOperation]) -> requests.Response:
        """Sends batch operations.

        Args:
            operations (Iterable[BatchOperation]): An iterable of BatchOperation instances.

        Returns:
            requests.Response: The response object from the batch request.
        """

        data = "\n".join([json.dumps(op.to_dict()) for op in operations])
        return self.batch_raw(data)

    def operation_post(
        self, ident: str, data: JsonObject, resultId: str | None = None
    ) -> BatchOperation:
        """Create a BatchOperation for POST (create item).

        Args:
            ident (str): The dataset alias.
            data (JsonDict): The item data to create.
            resultId (str | None, optional): An optional resultId to reference the result of this operation in subsequent operations with JSON References, and to identify result in the response. Defaults to None.

        Returns:
            BatchOperation: The created BatchOperation instance.
        """
        return BatchOperation(
            operation=BatchOperationMethod.post,
            dataset=ident,
            data=data,
            resultId=resultId,
        )

    def operation_put(
        self, ident: str, id: str | JsonRef, data: JsonObject
    ) -> BatchOperation:
        """Create a BatchOperation for PUT (update item).

        Args:
            ident (str): The dataset alias.
            id (str): The ID of the item to update.
            data (JsonDict): The updated item data.

        Returns:
            BatchOperation: The created BatchOperation instance.
        """
        return BatchOperation(
            operation=BatchOperationMethod.put, dataset=ident, id=id, data=data
        )

    def operation_patch(
        self, ident: str, id: str | JsonRef, data: JsonObject
    ) -> BatchOperation:
        """Create a BatchOperation for PATCH (partially update item).

        Args:
            ident (str): The dataset alias.
            id (str): The ID of the item to partially update.
            data (JsonDict): The partial item data.

        Returns:
            BatchOperation: The created BatchOperation instance.
        """
        return BatchOperation(
            operation=BatchOperationMethod.patch, dataset=ident, id=id, data=data
        )

    def operation_delete(self, ident: str, id: str | JsonRef) -> BatchOperation:
        """Create a BatchOperation for DELETE (delete item).

        Args:
            ident (str): The dataset alias.
            id (str): The ID of the item to delete.

        Returns:
            BatchOperation: The created BatchOperation instance.
        """
        return BatchOperation(
            operation=BatchOperationMethod.delete, dataset=ident, id=id
        )
