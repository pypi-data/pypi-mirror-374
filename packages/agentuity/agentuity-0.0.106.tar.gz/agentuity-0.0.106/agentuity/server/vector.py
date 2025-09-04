import httpx
from typing import Optional
from agentuity import __version__
from opentelemetry import trace
from opentelemetry.propagate import inject


class VectorSearchResult:
    """
    a result from a vector search

    @param id: the id of the vector
    @param key: the key of the vector
    @param similarity: the distance of the vector from 0.0 to 1.0
    @param metadata: the metadata of the vector or None if no metadata provided
    """

    def __init__(self, doc: Optional[dict] = None, **kwargs):
        if doc is not None:
            self.id = doc.get("id", "")
            self.key = doc.get("key", "")
            self.similarity = doc.get("similarity", 0)
            self.metadata = doc.get("metadata", None)
        else:
            self.id = kwargs.get("id", "")
            self.key = kwargs.get("key", "")
            self.similarity = kwargs.get("similarity", 0)
            self.metadata = kwargs.get("metadata", None)


class VectorStore:
    """
    A vector store for storing and searching vectors. This class provides methods to interact
    with a vector storage service, supporting operations like upserting, retrieving, searching,
    and deleting vectors.
    """

    def __init__(self, base_url: str, api_key: str, tracer: trace.Tracer):
        """
        Initialize the VectorStore client.

        Args:
            base_url: The base URL of the vector storage service
            api_key: The API key for authentication
            tracer: OpenTelemetry tracer for distributed tracing
        """
        self.base_url = base_url
        self.api_key = api_key
        self.tracer = tracer

    async def upsert(self, name: str, documents: list[dict]) -> list[str]:
        """
        Upsert vectors into the vector storage.

        Args:
            name: The name of the vector collection
            documents: List of documents to upsert. Each document must contain:
                - key: Required field identifying the document
                - Either 'document' or 'embeddings' field

        Returns:
            list[str]: List of IDs of the upserted documents

        Raises:
            ValueError: If documents are missing required fields
            Exception: If the upsert operation fails
        """
        with self.tracer.start_as_current_span("agentuity.vector.upsert") as span:
            span.set_attribute("name", name)
            for document in documents:
                if "key" not in document:
                    raise ValueError("document must have a key")
            if "document" not in document and "embeddings" not in document:
                raise ValueError("document must have either a document or embeddings")
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": f"Agentuity Python SDK/{__version__}",
            }
            inject(headers)
            response = httpx.put(
                f"{self.base_url}/vector/2025-03-17/{name}",
                headers=headers,
                json=documents,
            )
            if response.status_code == 200:
                result = response.json()
                if "success" in result and result["success"]:
                    ids = []
                    for doc in result["data"]:
                        ids.append(doc["id"])
                    span.add_event("upsert_count", attributes={"count": len(ids)})
                    span.set_status(trace.StatusCode.OK)
                    return ids
                else:
                    span.set_status(
                        trace.StatusCode.ERROR, "Failed to upsert documents"
                    )
                    raise Exception(f"Failed to upsert documents: {result['message']}")
            else:
                span.set_status(trace.StatusCode.ERROR, "Failed to upsert documents")
                span.record_exception(Exception(response.content.decode("utf-8")))
                raise Exception(f"Failed to upsert documents: {response.status_code}")

    async def get(self, name: str, key: str) -> VectorSearchResult:
        """
        Retrieve vectors from the vector storage by key.

        Args:
            name: The name of the vector collection
            key: The key to search for

        Returns:
            VectorSearchResult: matching vector search results. Returns None
                if no matches found.

        Raises:
            Exception: If the retrieval operation fails
        """
        with self.tracer.start_as_current_span("agentuity.vector.get") as span:
            span.set_attribute("name", name)
            span.set_attribute("key", key)
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": f"Agentuity Python SDK/{__version__}",
            }
            inject(headers)
            response = httpx.get(
                f"{self.base_url}/vector/2025-03-17/{name}/{key}",
                headers=headers,
            )
            match response.status_code:
                case 200:
                    result = response.json()
                    if result["success"]:
                        span.add_event("hit")
                        span.set_status(trace.StatusCode.OK)
                        if "data" in result:
                            return VectorSearchResult(**result["data"])
                        else:
                            return None
                    else:
                        span.set_status(
                            trace.StatusCode.ERROR, "Failed to get documents"
                        )
                        raise Exception(f"Failed to get documents: {result['message']}")
                case 404:
                    span.add_event("miss")
                    span.set_status(trace.StatusCode.OK)
                    return None
                case _:
                    span.set_status(trace.StatusCode.ERROR, "Failed to get documents")
                    span.record_exception(Exception(response.content.decode("utf-8")))
                    raise Exception(f"Failed to get documents: {response.status_code}")

    async def search(
        self,
        name: str,
        query: str,
        limit: int = 10,
        similarity: float = 0.5,
        metadata: Optional[dict] = {},
    ) -> list[VectorSearchResult]:
        """
        Search for vectors in the vector storage using semantic similarity.

        Args:
            name: The name of the vector collection
            query: The search query string
            limit: Maximum number of results to return (default: 10)
            similarity: Minimum similarity threshold between 0.0 and 1.0 (default: 0.5)
            metadata: Optional metadata filters to apply to the search

        Returns:
            list[VectorSearchResult]: List of matching vector search results. Returns empty list
                if no matches found.

        Raises:
            Exception: If the search operation fails
        """
        with self.tracer.start_as_current_span("agentuity.vector.search") as span:
            span.set_attribute("name", name)
            span.set_attribute("query", query)
            span.set_attribute("limit", limit)
            span.set_attribute("similarity", similarity)
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": f"Agentuity Python SDK/{__version__}",
            }
            inject(headers)
            response = httpx.post(
                f"{self.base_url}/vector/2025-03-17/search/{name}",
                headers=headers,
                json={
                    "query": query,
                    "limit": limit,
                    "similarity": similarity,
                    "metadata": metadata,
                },
            )
            match response.status_code:
                case 200:
                    result = response.json()
                    if "success" in result and result["success"]:
                        span.add_event("hit")
                        span.set_status(trace.StatusCode.OK)
                        return [VectorSearchResult(**doc) for doc in result["data"]]
                    elif "message" in result:
                        span.set_status(
                            trace.StatusCode.ERROR, "Failed to search documents"
                        )
                        raise Exception(
                            f"Failed to search documents: {result['message']}"
                        )
                    else:
                        span.set_status(
                            trace.StatusCode.ERROR, "Failed to search documents"
                        )
                        raise Exception(
                            f"Failed to search documents: {response.status_code}"
                        )
                case 404:
                    span.add_event("miss")
                    span.set_status(trace.StatusCode.OK)
                    return []
                case _:
                    span.set_status(
                        trace.StatusCode.ERROR, "Failed to search documents"
                    )
                    span.record_exception(Exception(response.content.decode("utf-8")))
                    raise Exception(
                        f"Failed to search documents: {response.status_code}"
                    )

    async def delete(self, name: str, key: str) -> int:
        """
        Delete vectors from the vector storage by key.

        Args:
            name: The name of the vector collection
            key: The key of the vectors to delete

        Returns:
            int: Number of vectors deleted

        Raises:
            Exception: If the deletion operation fails
        """
        with self.tracer.start_as_current_span("agentuity.vector.delete") as span:
            span.set_attribute("name", name)
            span.set_attribute("key", key)
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": f"Agentuity Python SDK/{__version__}",
            }
            inject(headers)
            response = httpx.delete(
                f"{self.base_url}/vector/2025-03-17/{name}/{key}",
                headers=headers,
            )
            if response.status_code == 200:
                result = response.json()
                if result["success"]:
                    count = result["data"] if "data" in result else 0
                    span.add_event("delete_count", attributes={"count": count})
                    span.set_status(trace.StatusCode.OK)
                    return count
                else:
                    span.set_status(
                        trace.StatusCode.ERROR, "Failed to delete documents"
                    )
                    raise Exception(f"Failed to delete documents: {result['message']}")
            else:
                span.set_status(trace.StatusCode.ERROR, "Failed to delete documents")
                span.record_exception(Exception(response.content.decode("utf-8")))
                raise Exception(f"Failed to delete documents: {response.status_code}")
