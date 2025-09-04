"""Tests for S3 Vectors feed storage."""

from __future__ import annotations

from io import BytesIO
from unittest import mock

from zope.interface.verify import verifyObject

from scrapy.extensions.feedexport import IFeedStorage
from scrapy.utils.test import get_crawler

from scrapy_vectors import S3VectorsFeedStorage


class TestS3VectorsFeedStorage:
    def test_parse_credentials(self):
        settings = {"AWS_REGION_NAME": "us-west-2"}
        crawler = get_crawler(settings_dict=settings)

        storage = S3VectorsFeedStorage.from_crawler(
            crawler, "s3-vectors://bucket/index"
        )
        assert storage.region_name == "us-west-2"
        assert storage.bucket == "bucket"
        assert storage.index == "index"

    def test_store(self):
        storage = S3VectorsFeedStorage(
            "s3-vectors://bucket/index", region_name="us-east-1"
        )
        verifyObject(IFeedStorage, storage)
        storage.client = mock.MagicMock()

        # Create test JSONL data with multiple records and empty line
        test_data = (
            b'{"id": "doc1", "values": [0.1, 0.2], '
            b'"metadata": {"source": "test"}}\n'
            b"\n"  # Empty line should be filtered out
            b'{"id": "doc2", "values": [0.3, 0.4], "metadata": '
            b'{"source": "file.pdf", "page": 5}}\n'
            b'{"id": "doc3", "values": [0.5, 0.6]}\n'  # No metadata
        )
        test_file = BytesIO(test_data)
        storage._store_in_thread(test_file)

        # Verify put_vectors was called with correct parameters
        storage.client.put_vectors.assert_called_once_with(
            vectorBucketName="bucket",
            indexName="index",
            vectors=[
                {
                    "key": "doc1",
                    "data": {"float32": [0.1, 0.2]},
                    "metadata": {"source": "test"},
                },
                {
                    "key": "doc2",
                    "data": {"float32": [0.3, 0.4]},
                    "metadata": {"source": "file.pdf", "page": 5},
                },
                {
                    "key": "doc3",
                    "data": {"float32": [0.5, 0.6]},
                    "metadata": {},
                },
            ],
        )
