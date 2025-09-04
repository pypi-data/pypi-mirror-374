# scrapy-vectors

[![Tests](https://github.com/kyleissuper/scrapy-vectors/actions/workflows/tests.yml/badge.svg)](https://github.com/kyleissuper/scrapy-vectors/actions/workflows/tests.yml)
[![Code Quality](https://github.com/kyleissuper/scrapy-vectors/actions/workflows/checks.yml/badge.svg)](https://github.com/kyleissuper/scrapy-vectors/actions/workflows/checks.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: ISC](https://img.shields.io/badge/License-ISC-blue.svg)](https://opensource.org/licenses/ISC)
[![PyPI version](https://badge.fury.io/py/scrapy-vectors.svg)](https://badge.fury.io/py/scrapy-vectors)

Vector embeddings generation and storage for Scrapy spiders.

## Features

- **Embeddings Pipeline**: Generate vector embeddings using LiteLLM (supports OpenAI, Cohere, and other providers)
- **S3 Vectors Storage**: Store embeddings in AWS S3 Vectors service

## Installation

```bash
pip install scrapy-vectors
```

## Quick Start

In your `scrapy_settings.py`:
```python
ITEM_PIPELINES = {
    # Outputs as jsonlines in Pinecone format, which s3-vectors can use
    "scrapy_vectors.EmbeddingsLiteLLMPipeline": 300,
}
EXTENSIONS = {
    "scrapy.extensions.feedexport.FeedExporter": None,  # Disable standard
    "scrapy_vectors.S3VectorsFeedExporter": 300,        # Use custom
}
FEED_STORAGES = {
    "s3-vectors": "scrapy_vectors.S3VectorsFeedStorage",
}
FEEDS = {
    "s3-vectors://vectors-bucket/vectors-index": {
        "format": "jsonlines",
        "batch_item_count": 100,
    }
}

# LiteLLM will route for you
LITELLM_API_KEY = "your_provider_api_key"          # (e.g. OpenAI API Key)
LITELLM_EMBEDDING_MODEL = "text-embedding-3-small" # This is default when unspecified

AWS_REGION_NAME = "us-east-1"
AWS_ACCESS_KEY_ID = "access_key_id"
AWS_SECRET_ACCESS_KEY = "access_key"
```

In your scraper:
```python
import scrapy


class MySpider(scrapy.Spider):
    name = "example"
    start_urls = ["https://example.com"]

    # Must yield with: id, page_content, and metadata
    def parse(self, response):
        yield {
            "id": response.url,
            "page_content": response.css("article::text").get(),
            "metadata": {
                "title": response.css("h1::text").get(),
                "url": response.url,
            }
        }
```

## Configuration

### Embeddings Pipeline Settings

- `LITELLM_API_KEY`: API key for your embedding provider (required)
- `LITELLM_EMBEDDING_MODEL`: Model to use (default: OpenAI's `text-embedding-3-small`)

### S3 Vectors Storage Settings

- `AWS_REGION_NAME`: AWS region (required)
- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
