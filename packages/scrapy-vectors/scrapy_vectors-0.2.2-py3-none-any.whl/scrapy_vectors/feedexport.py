"""
Feed export storage for vector embeddings.
"""

from __future__ import annotations

import json
import logging
from typing import IO, TYPE_CHECKING, Any
from urllib.parse import urlparse

from scrapy.exceptions import NotConfigured
from scrapy.extensions.feedexport import BlockingFeedStorage, IFeedStorage, FeedExporter
from zope.interface import implementer

if TYPE_CHECKING:
    from scrapy.crawler import Crawler

logger = logging.getLogger(__name__)


@implementer(IFeedStorage)
class S3VectorsFeedStorage(BlockingFeedStorage):
    """
    Store on Amazon S3 Vectors using Pinecone schema.
    File input is jsonl-pinecone (id, values, metadata).
    """

    def __init__(
        self,
        uri: str,
        *,
        feed_options: dict[str, Any] | None = None,  # pylint: disable=unused-argument
        region_name: str | None = None,
    ):
        try:
            import boto3  # noqa: PLC0415
        except ImportError as exc:
            raise NotConfigured("missing boto3 library") from exc

        u = urlparse(uri)
        if not u.hostname:
            raise NotConfigured(
                f"invalid S3 vectors URI: missing bucket name in '{uri}'"
            )
        index_path = u.path.lstrip("/")
        if not index_path:
            raise NotConfigured(
                f"invalid S3 vectors URI: missing index name in '{uri}'"
            )
        if not region_name:
            raise NotConfigured(
                "S3 Vectors requires a region to be specified. "
                "Set AWS_REGION_NAME in settings or pass "
                "region_name parameter."
            )

        self.region_name: str = region_name
        self.index: str = index_path
        self.bucket: str = u.hostname
        # S3 Vectors type stubs available in mypy-boto3-s3vectors,
        # but not in base boto3-stubs
        self.client = boto3.client(
            "s3vectors", region_name=region_name
        )  # type: ignore[call-overload]

    @classmethod
    def from_crawler(
        cls,
        crawler: Crawler,
        uri: str,
        *,
        feed_options: dict[str, Any] | None = None,
    ) -> S3VectorsFeedStorage:
        return cls(
            uri,
            feed_options=feed_options,
            region_name=crawler.settings.get("AWS_REGION_NAME"),
        )

    def _store_in_thread(self, file: IO[bytes]) -> None:
        file.seek(0)
        vectors = [
            parsed for raw in file if (parsed := self._parse_line(raw)) is not None
        ]
        if vectors:
            self.client.put_vectors(
                vectorBucketName=self.bucket,
                indexName=self.index,
                vectors=vectors,
            )
        file.close()

    def _parse_line(self, raw: bytes) -> dict[str, Any] | None:
        if not raw or not raw.strip():
            return None
        line = raw.decode("utf-8")
        rec = json.loads(line)
        return {
            "key": rec["id"],
            "data": {"float32": rec["values"]},
            # Metadata automatically becomes filterable in S3 Vectors
            # by default
            # Supports queries like: {"source": "file.pdf"},
            # {"year": {"$gte": 2020}}
            "metadata": rec.get("metadata", {}),
        }


class S3VectorsFeedExporter(FeedExporter):
    def _settings_are_valid(self):
        for uri_template, _ in self.feeds.items():
            if not uri_template.startswith("s3-vectors://"):
                logger.error("Invalid URI: %s", uri_template)
                return False
        return True
