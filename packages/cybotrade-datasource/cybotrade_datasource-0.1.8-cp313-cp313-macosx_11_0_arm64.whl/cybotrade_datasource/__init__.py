# import the contents of the Rust library into the Python extension
from .cybotrade_datasource import *

from datetime import datetime
from typing import Literal, TypedDict


class Data(TypedDict):
    start_time: datetime


PaginationMode = Literal["start_time_end_time", "start_time_limit", "end_time_limit"]


class Pagination(TypedDict):
    start_time: datetime
    end_time: datetime
    limit: int
    mode: PaginationMode


class Response(TypedDict):
    data: list[Data]
    page: Pagination


class SubscriptionResponse(TypedDict):
    conn_id: str
    success: bool
    message: str


CollectedDataType = Literal["snapshot", "delta"]


class CollectedData(TypedDict):
    topic: str
    data: list[Data]
    local_timestamp_ms: int
    type: CollectedDataType


Message = SubscriptionResponse | CollectedData
