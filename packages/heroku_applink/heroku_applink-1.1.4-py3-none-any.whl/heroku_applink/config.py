"""
Copyright (c) 2025, salesforce.com, inc.
All rights reserved.
SPDX-License-Identifier: BSD-3-Clause
For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause
"""

import importlib.metadata

from dataclasses import dataclass

@dataclass
class Config:
    """
    Configuration for the Salesforce Data API client.
    """

    request_timeout: float = 5
    """
    Timeout for requests to the Salesforce Data API. In most cases, you'll only
    need to set this value. Connection Timeout, Socket Connect, and Socket Read
    are optional and only used in special cases.
    """

    connect_timeout: float|None = None
    """
    Timeout for connecting to the Salesforce Data API.
    """

    socket_connect: float|None = None
    """
    Timeout for connecting to the Salesforce Data API.
    """

    socket_read: float|None = None
    """
    Timeout for reading from the Salesforce Data API.
    """

    @classmethod
    def default(cls) -> "Config":
        return cls(
            request_timeout=5,
            connect_timeout=None,
            socket_connect=None,
            socket_read=None,
        )

    def user_agent(self) -> str:
        version = importlib.metadata.version("heroku_applink")

        return f"heroku-applink-python-sdk/{version}"
