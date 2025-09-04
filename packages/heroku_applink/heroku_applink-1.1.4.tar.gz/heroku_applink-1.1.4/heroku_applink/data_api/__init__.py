"""
Copyright (c) 2025, salesforce.com, inc.
All rights reserved.
SPDX-License-Identifier: BSD-3-Clause
For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause
"""

from typing import Any, TypeVar

import aiohttp
import orjson
from aiohttp.payload import BytesPayload

from heroku_applink.connection import Connection

from ._requests import (
    CompositeGraphRestApiRequest,
    CreateRecordRestApiRequest,
    DeleteRecordRestApiRequest,
    QueryNextRecordsRestApiRequest,
    QueryRecordsRestApiRequest,
    RestApiRequest,
    UpdateRecordRestApiRequest,
)
from .exceptions import ClientError, UnexpectedRestApiResponsePayload
from .record import Record, RecordQueryResult
from .reference_id import ReferenceId
from .unit_of_work import UnitOfWork

__all__ = ["DataAPI"]

T = TypeVar("T")


class DataAPI:
    """
    Data API client to interact with data in a Salesforce org.

    We provide a preconfigured instance of this client at `context.org.data_api`
    to make it easier for you to query, insert, and update records.
    """

    def __init__(
        self,
        *,
        org_domain_url: str,
        api_version: str,
        access_token: str,
        connection: Connection,
    ) -> None:
        self._api_version = api_version
        self._org_domain_url = org_domain_url
        self.access_token = access_token
        self._connection = connection

    async def query(self, soql: str, timeout: float|None=None) -> RecordQueryResult:
        """
        Query for records using the given SOQL string.

        For example:

        ```python
        result = await context.org.data_api.query("SELECT Id, Name FROM Account")

        for record in result.records:
            # ...
        ```

        If the returned `RecordQueryResult`'s `done` attribute is `False`, there are more
        records to be returned. To retrieve these, use `DataAPI.query_more()`.

        For more information, see the [Query REST API documentation](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_query.htm).
        """  # noqa: E501 pylint: disable=line-too-long
        return await self._execute(
            QueryRecordsRestApiRequest(soql, self._download_file),
            timeout=timeout,
        )

    async def query_more(self, result: RecordQueryResult, timeout: float|None=None) -> RecordQueryResult:
        """
        Query for more records, based on the given `RecordQueryResult`.

        For example:

        ```python
        result = await context.org.data_api.query("SELECT Id, Name FROM Account")

        if not result.done:
            query_more_result = await context.org.data_api.query_more(result)
        ```

        For more information, see the [Query More Results REST API documentation](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_query_more_results.htm).
        """  # noqa: E501 pylint: disable=line-too-long
        if result.next_records_url is None:
            return RecordQueryResult(
                done=True,
                total_size=result.total_size,
                records=[],
                next_records_url=None,
            )

        return await self._execute(
            QueryNextRecordsRestApiRequest(result.next_records_url, self._download_file),
            timeout=timeout,
        )

    async def create(self, record: Record, timeout: float|None=None) -> str:
        """
        Create a new record based on the given `Record` object.

        Returns the ID of the new record.

        For example:

        ```python
        record_id = await context.org.data_api.create(
            Record(
                type="Account",
                fields={
                    "Name": "Example Account",
                },
            )
        )
        ```
        """
        return await self._execute(
            CreateRecordRestApiRequest(record),
            timeout=timeout,
        )

    async def update(self, record: Record, timeout: float|None=None) -> str:
        """
        Update an existing record based on the given `Record` object.

        The given `Record` must contain an `Id` field. Returns the ID of the record that was updated.

        For example:

        ```python
        await context.org.data_api.update(
            Record(
                type="Account",
                fields={
                    "Id": "001B000001Lp1FxIAJ",
                    "Name": "New Name",
                },
            )
        )
        ```
        """
        return await self._execute(
            UpdateRecordRestApiRequest(record),
            timeout=timeout,
        )

    async def delete(self, object_type: str, record_id: str, timeout: float|None=None) -> str:
        """
        Delete an existing record of the given Salesforce object type and ID.

        Returns the ID of the record that was deleted.

        For example:

        ```python
        await data_api.delete("Account", "001B000001Lp1FxIAJ")
        ```
        """
        return await self._execute(
            DeleteRecordRestApiRequest(object_type, record_id),
            timeout=timeout,
        )

    async def commit_unit_of_work(
        self, unit_of_work: UnitOfWork, timeout: float|None=None
    ) -> dict[ReferenceId, str]:
        """
        Commit a `UnitOfWork`, which executes all operations registered with it.

        If any of these operations fail, the whole unit is rolled back. To examine results for a
        single operation, inspect the returned dict (which is keyed with `ReferenceId` objects
        returned from the `register*` functions on `UnitOfWork`).

        For example:

        ```python
        # Create a unit of work, against which multiple operations can be registered.
        unit_of_work = UnitOfWork()

        first_reference_id = unit_of_work.register_create(
            # ...
        )
        second_reference_id = unit_of_work.register_create(
            # ...
        )

        # Commit the unit of work, executing all of the operations registered above.
        result = await context.org.data_api.commit_unit_of_work(unit_of_work)

        # The result of each operation.
        first_record_id = result[first_create_reference_id]
        second_record_id = result[second_create_reference_id]
        ```
        """
        return await self._execute(
            CompositeGraphRestApiRequest(
                self._api_version,
                unit_of_work._sub_requests,  # pyright: ignore [reportPrivateUsage] pylint:disable=protected-access
            ),
            timeout=timeout,
        )

    async def _execute(self, rest_api_request: RestApiRequest[T], timeout: float|None=None) -> T:
        url: str = rest_api_request.url(self._org_domain_url, self._api_version)
        method: str = rest_api_request.http_method()
        body = rest_api_request.request_body()

        try:
            response = await self._connection.request(
                method,
                url,
                headers=self._default_headers(),
                data=None if body is None else _json_serialize(body),
                timeout=timeout,
            )

            # Using orjson for faster JSON deserialization over the stdlib.
            # This is not implemented using the `loads` argument to `Response.json` since:
            # - We don't want the content type validation, since some successful requests.py return 204
            #   (No Content) which will not have an `application/json`` content type header. However,
            #   these parse just fine as JSON helping to unify the interface to the REST request classes.
            # - Orjson's performance/memory usage is better if it is passed bytes directly instead of `str`.
            response_body = await response.read()
            json_body = orjson.loads(response_body) if response_body else None
        except aiohttp.ClientError as e:
            # https://docs.aiohttp.org/en/stable/client_reference.html#client-exceptions
            raise ClientError(
                f"An error occurred while making the request: {e.__class__.__name__}: {e}"
            ) from e
        except orjson.JSONDecodeError as e:
            raise UnexpectedRestApiResponsePayload(
                f"The server didn't respond with valid JSON: {e.__class__.__name__}: {e}"
            ) from e

        return await rest_api_request.process_response(response.status, json_body)

    async def _download_file(self, url: str) -> bytes:
        response = await self._connection.request(
            "GET", f"{self._org_domain_url}{url}", headers=self._default_headers()
        )

        return await response.read()

    def _default_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
        }


def _json_serialize(data: Any) -> BytesPayload:
    """
    JSON serialize the provided data to bytes.

    This is a replacement for aiohttp's default JSON implementation that uses `orjson` instead
    of the Python stdlib's `json` module, since `orjson` is faster:
    https://github.com/ijl/orjson#performance

    We can't just implement this by passing `json_serialize` to `ClientSession`, due to:
    https://github.com/aio-libs/aiohttp/issues/4482

    So instead this is based on `payload.JsonPayload`:
    https://github.com/aio-libs/aiohttp/blob/v3.8.3/aiohttp/payload.py#L386-L403
    """
    return BytesPayload(
        orjson.dumps(data), encoding="utf-8", content_type="application/json"
    )
