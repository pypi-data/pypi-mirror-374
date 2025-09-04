"""
Copyright (c) 2025, salesforce.com, inc.
All rights reserved.
SPDX-License-Identifier: BSD-3-Clause
For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause
"""

import aiohttp
import asyncio
import uuid

from contextvars import ContextVar

from .config import Config

request_id: ContextVar[str] = ContextVar("request_id")

def get_request_id() -> str:
    """
    Get the request ID for the current request.
    """
    return request_id.get(str(uuid.uuid4()))

def set_request_id(new_request_id: str):
    """
    Set the request ID for the current request.
    """
    request_id.set(new_request_id)

class Connection:
    """
    A connection for making asynchronous HTTP requests.
    """

    def __init__(self, config: Config):
        self._config = config
        self._session = None

    def _decode_headers(self, headers: dict) -> dict:
        """
        Decode headers from bytes to strings, similar to how Node.js handles headers automatically.
        """
        if not headers:
            return {}

        return {
            k.decode('latin1') if isinstance(k, bytes) else k:
            v.decode('latin1') if isinstance(v, bytes) else v
            for k, v in headers.items()
        }

    def request(
        self,
        method,
        url,
        params=None,
        headers=None,
        data=None,
        timeout: float|None=None
    ) -> aiohttp.ClientResponse:
        """
        Make an HTTP request to the given URL.

        If a timeout is provided, it will be used to set the timeout for the request.
        """

        if timeout is not None:
            timeout = aiohttp.ClientTimeout(total=timeout)

        default_headers = {
            # Always include the user-agent header in all outbound requests.
            # This is so we can track SDK versions across all of our customers.
            "User-Agent": self._config.user_agent(),
            # Always include a request-id header in all outbound requests.
            # This will be helpful for debugging and tracking requests.
            #
            # Using `request_id` we can get any request-id set by the middleware.
            # If no request-id is set, we generate a new one.
            "X-Request-Id": get_request_id(),
        }

        # Start with custom headers, then override with default headers
        # This ensures our default headers (User-Agent, X-Request-Id) always take precedence
        # Decode headers and merge with defaults
        headers = self._decode_headers(headers)
        headers = {**(headers or {}), **default_headers}

        response = self._client().request(
            method,
            url,
            params=params,
            headers=headers,
            data=data,
            timeout=timeout
        )

        return response

    async def close(self):
        """
        Close the connection.
        """
        if self._session:
            await self._session.close()
            self._session = None

    def __del__(self):
        """
        Close the connection when the object is deleted.
        """
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.close())
        except RuntimeError:
            asyncio.run(self.close())

    def _client(self) -> aiohttp.ClientSession:
        """
        Lazily get the underlying `aiohttp.ClientSession`. This session is
        persisted so we can take advantage of connection pooling.
        """
        if self._session is None:
            self._session = aiohttp.ClientSession(
                # Disable cookie storage using `DummyCookieJar`, given that we
                # don't need cookie support.
                cookie_jar=aiohttp.DummyCookieJar(),
                timeout=aiohttp.ClientTimeout(
                    total=self._config.request_timeout,
                    connect=self._config.connect_timeout,
                    sock_connect=self._config.socket_connect,
                    sock_read=self._config.socket_read,
                ),
            )
        return self._session
