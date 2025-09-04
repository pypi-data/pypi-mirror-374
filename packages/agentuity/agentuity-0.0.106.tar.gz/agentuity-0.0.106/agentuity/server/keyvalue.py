import httpx
from typing import Union, Optional
from .data import DataResult, Data, dataLikeToData
from opentelemetry.propagate import inject
from agentuity import __version__
from opentelemetry import trace


class KeyValueStore:
    """
    A key-value store client for storing and retrieving key-value pairs. This class provides
    methods to interact with a key-value storage service, supporting operations like getting,
    setting, and deleting values with optional TTL (Time To Live) and content type specifications.
    """

    def __init__(
        self,
        base_url: str,
        api_key: str,
        tracer: trace.Tracer,
    ):
        """
        Initialize the KeyValueStore client.

        Args:
            base_url: The base URL of the key-value storage service
            api_key: The API key for authentication
            tracer: OpenTelemetry tracer for distributed tracing
        """
        self.base_url = base_url
        self.api_key = api_key
        self.tracer = tracer

    async def get(self, name: str, key: str) -> DataResult:
        """
        Retrieve a value from the key-value storage.

        Args:
            name: The name of the key-value collection
            key: The key to retrieve

        Returns:
            DataResult: A container containing the retrieved data if found, or None if not found

        Raises:
            Exception: If the retrieval operation fails
        """
        with self.tracer.start_as_current_span("agentuity.keyvalue.get") as span:
            span.set_attribute("name", name)
            span.set_attribute("key", key)
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": f"Agentuity Python SDK/{__version__}",
            }
            inject(headers)
            response = httpx.get(
                f"{self.base_url}/kv/2025-03-17/{name}/{key}",
                headers=headers,
            )
            match response.status_code:
                case 200:
                    span.add_event("hit")
                    span.set_status(trace.StatusCode.OK)
                    import asyncio

                    reader = asyncio.StreamReader()
                    reader.feed_data(response.content)
                    reader.feed_eof()

                    content_type = response.headers.get(
                        "Content-Type", "application/octet-stream"
                    )
                    return DataResult(Data(content_type, reader))
                case 404:
                    span.add_event("miss")
                    span.set_status(trace.StatusCode.OK)
                    return DataResult(None)
                case _:
                    span.set_status(trace.StatusCode.ERROR, "Failed to get key value")
                    span.record_exception(Exception(response.content.decode("utf-8")))
                    raise Exception(f"Failed to get key value: {response.status_code}")

    async def set(
        self,
        name: str,
        key: str,
        value: Union[str, int, float, bool, list, dict, bytes, "Data"],
        params: Optional[dict] = None,
    ):
        """
        Store a value in the key-value storage.

        Args:
            name: The name of the key-value collection
            key: The key to store the value under
            value: The value to store. Can be:
                - Data object
                - bytes
                - str, int, float, bool
                - list or dict (will be converted to JSON)
            params: Optional dictionary containing:
                - ttl: Time to live in seconds (minimum 60 seconds)
                - contentType: The MIME type of the value

        Raises:
            ValueError: If TTL is less than 60 seconds
            Exception: If the storage operation fails or value encoding fails
        """
        with self.tracer.start_as_current_span("agentuity.keyvalue.set") as span:
            span.set_attribute("name", name)
            span.set_attribute("key", key)
            ttl = None
            if params is None:
                params = {}
                ttl = params.get("ttl", None)
            if ttl is not None and ttl < 60:
                raise ValueError("ttl must be at least 60 seconds")
            content_type = params.get("contentType", None)
            payload = None

            try:
                data = dataLikeToData(value, content_type)
                content_type = data.content_type
                payload = await data.binary()
            except Exception as e:
                span.set_status(trace.StatusCode.ERROR, "Failed to encode value")
                raise e

            ttlstr = ""
            if ttl is not None:
                ttlstr = f"/{ttl}"
                span.set_attribute("ttl", ttlstr)

            span.set_attribute("contentType", content_type)
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": f"Agentuity Python SDK/{__version__}",
                "Content-Type": content_type,
            }
            inject(headers)

            response = httpx.put(
                f"{self.base_url}/kv/2025-03-17/{name}/{key}{ttlstr}",
                headers=headers,
                content=payload,
            )

            if response.status_code != 201:
                span.set_status(trace.StatusCode.ERROR, "Failed to set key value")
                span.record_exception(Exception(response.content.decode("utf-8")))
                raise Exception(f"Failed to set key value: {response.status_code}")
            else:
                span.set_status(trace.StatusCode.OK)

    async def delete(self, name: str, key: str):
        """
        Delete a value from the key-value storage.

        Args:
            name: The name of the key-value collection
            key: The key to delete

        Raises:
            Exception: If the deletion operation fails
        """
        with self.tracer.start_as_current_span("agentuity.keyvalue.delete") as span:
            span.set_attribute("name", name)
            span.set_attribute("key", key)
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": f"Agentuity Python SDK/{__version__}",
            }
            inject(headers)
            response = httpx.delete(
                f"{self.base_url}/kv/2025-03-17/{name}/{key}",
                headers=headers,
            )
            if response.status_code != 200:
                span.set_status(trace.StatusCode.ERROR, "Failed to delete key value")
                span.record_exception(Exception(response.content.decode("utf-8")))
                raise Exception(f"Failed to delete key value: {response.status_code}")
            else:
                span.set_status(trace.StatusCode.OK)
