from datetime import datetime
from typing import Optional, AsyncIterator

from cybotrade_datasource import Data, Response, Message

async def query_paginated(
    api_key: str,
    topic: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: Optional[int] = None,
    flatten: Optional[bool] = None,
    api_url: Optional[str] = None,
) -> list[Data]:
    """
    Query Datasource API in a paginated manner.
    This function might call the server several times until it completes collecting data according to the
    parameters specified.

    You can only specify parameters in the combination of (start_time, end_time) or (limit).
    """

async def query(
    api_key: str,
    topic: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: Optional[int] = None,
    flatten: Optional[bool] = None,
    api_url: Optional[str] = None,
) -> Response:
    """
    Query Datasource API without pagination.
    This function will always make only one call to the server.

    You can only specify parameters in the combination of (start_time, end_time), (start_time, limit) or (end_time, limit).
    """

async def stream(
    api_key: str, topics: list[str], url: Optional[str] = None
) -> AsyncIterator[Message]:
    """
    Connect to the websocket server with the provided topics to listen for live updates.
    """
