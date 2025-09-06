from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from typing import Any

import httpx
from pydantic import AwareDatetime, BaseModel


class PapertrailLogEvent(BaseModel):
    """unique Papertrail event ID (64-bit integer as JSON string)

    The id values for a series of events indicate relative event order and will only increase, but id values are not sequential.
    """

    id: str
    """time that the log event was generated (ISO 8601 timestamp)"""
    generated_at: AwareDatetime
    """time that Papertrail received the log event (ISO 8601 timestamp)

    received_at and display_received_at are in the time zone of the API token owner (set in the profile).
    """
    received_at: AwareDatetime
    """time that Papertrail received the log event (formatted date-time string)

    received_at and display_received_at are in the time zone of the API token owner (set in the profile).
    """
    display_received_at: str
    """sender name in Papertrail (string)"""
    source_name: str
    """hostname of the message (string)"""
    hostname: str
    """unique Papertrail sender ID (32-bit integer)"""
    source_id: int
    """IP address that originated this log event (string)"""
    source_ip: str
    """syslog facility (string)"""
    facility: str
    """syslog severity (string)"""
    severity: str
    """syslog “tag” field, more commonly called program (string)"""
    program: str
    """log event message (string)"""
    message: str


class SearchResult(BaseModel):
    """Search result from Papertrail API

    The search endpoint returns a JSON object containing these keys:

        events: an array of hashes of log events (one hash per event)
        min_id: the lowest event ID examined
        max_id: the highest event ID examined

    In addition to min_id and max_id, the response object may also contain min_time_at or max_time_at. These are the oldest or newest timestamps searched during this request. These keys are useful for displaying the time the search spanned in a human-friendly way, but since multiple events may have occured during the same second, they should not be used to select a time range for subsequent queries.

    Each search query will return one of three types of result sets. The client can use the type to decide what to do next. The 3 possible types are:

        * when searching backward: a full set of matching log messages with reached_beginning set to true. All matching events from the set max_id or max_time back to the beginning of searchable retention were examined.
        * when searching forward: a full set of matching log messages with reached_end set to true. All matching events from the set min_id or min_time up to the present were examined.
        * limit-size set of matching log messages (default 1000). The events array contains these elements, and reached_record_limit is included in the result.
        * partial set of matching messages with reached_time_limit set to true. Papertrail's per-request time limit was reached before a full set of events was found.

    Papertrail's workload varies significantly based on the number of possible events and the complexity of the query. To ensure that the caller does not block forever, the search API automatically enforces a per-request time limit of about 5 seconds. When the response contains reached_time_limit, this time limit expired before the full set of results was returned.
    """

    """An array of hashes of log events (one hash per event)"""
    events: list[PapertrailLogEvent]
    """the lowest event ID examined"""
    min_id: str
    """the highest event ID examined"""
    max_id: str
    """In addition to min_id and max_id, the response object may also contain min_time_at or max_time_at. These are the oldest or newest timestamps searched during this request. These keys are useful for displaying the time the search spanned in a human-friendly way, but since multiple events may have occured during the same second, they should not be used to select a time range for subsequent queries."""
    min_time_at: AwareDatetime | None = None
    """In addition to min_id and max_id, the response object may also contain min_time_at or max_time_at. These are the oldest or newest timestamps searched during this request. These keys are useful for displaying the time the search spanned in a human-friendly way, but since multiple events may have occured during the same second, they should not be used to select a time range for subsequent queries."""
    max_time_at: AwareDatetime | None = None
    """When searching backward: a full set of matching log messages with reached_beginning set to true. All matching events from the set max_id or max_time back to the beginning of searchable retention were examined."""
    reached_beginning: bool = False
    """When searching forward: a full set of matching log messages with reached_end set to true. All matching events from the set min_id or min_time up to the present were examined."""
    reached_end: bool = False
    """A limit-size set of matching log messages (default 1000). The events array contains these elements, and reached_record_limit is included in the result."""
    reached_record_limit: bool = False
    """A partial set of matching messages with reached_time_limit set to true. Papertrail's per-request time limit was reached before a full set of events was found.

    Papertrail's workload varies significantly based on the number of possible events and the complexity of the query. To ensure that the caller does not block forever, the search API automatically enforces a per-request time limit of about 5 seconds. When the response contains reached_time_limit, this time limit expired before the full set of results was returned.
    """
    reached_time_limit: bool = False


class PapertrailClient(httpx.AsyncClient):
    """Papertrail API client

    https://www.papertrail.com/help/search-api/
    """

    BASE_URL = "https://papertrailapp.com/api/v1"

    def __init__(self, token: str, connection_limit: int = 10, base_url: str = BASE_URL) -> None:
        self._token = token
        super().__init__(
            base_url=base_url,
            headers={
                "X-Papertrail-Token": self._token,
            },
            timeout=httpx.Timeout(10),
            limits=httpx.Limits(max_connections=connection_limit),
        )

    async def verify_connection(self) -> None:
        response = await self.get("/events/search.json", params={"limit": 1})
        response.raise_for_status()
        SearchResult.model_validate(response.json())

    async def search(
        self,
        query: str,
        min_time: AwareDatetime,
        max_time: AwareDatetime,
        max_results: int = 10000,
    ) -> AsyncGenerator[PapertrailLogEvent, None]:
        max_id = None
        logs_found = 0
        while True:
            params: dict[str, Any] = {
                "q": query,
                "tail": False,
                **(
                    {
                        "min_time": int(min_time.timestamp()),
                        "max_time": int(max_time.timestamp()),
                        "limit": 100,
                    }
                    if max_id is None
                    else {
                        "max_id": max_id,
                        "limit": 1000,
                    }
                ),
            }
            response = await self.get("/events/search.json", params=params)
            response.raise_for_status()
            result = SearchResult.model_validate(response.json())
            event_before_min_time = False
            for event in result.events:
                if event.generated_at >= min_time or event.received_at >= min_time:
                    yield event
                else:
                    event_before_min_time = True
            max_id = result.min_id
            if event_before_min_time:
                break
            logs_found += len(result.events)
            if result.reached_end:
                break
            if result.reached_beginning:
                break
            if result.min_time_at is not None and result.min_time_at < min_time:
                break
            if logs_found >= max_results:
                now = datetime.now(UTC)
                yield PapertrailLogEvent(
                    id="daydream_mcp_internal",
                    generated_at=now,
                    received_at=now,
                    display_received_at="",
                    source_name="daydream_mcp",
                    hostname="",
                    source_id=0,
                    source_ip="",
                    facility="",
                    severity="",
                    program="daydream_mcp",
                    message=f"NOTICE: Already found {max_results} results, stopping search. Try a shorter time range or a more specific filter.",
                )
                break
