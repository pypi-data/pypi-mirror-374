# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance
# with the License. A copy of the License is located at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# or in the 'license' file accompanying this file. This file is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions
# and limitations under the License.

"""Base scraper class for French tax information websites.

This module provides a base class with common functionality for scraping tax information
from official French government websites.
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union

from bs4 import BeautifulSoup
from httpx import AsyncClient, Response

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import constants
from french_tax_mcp.constants import (
    DEFAULT_CACHE_DIR,
    DEFAULT_CACHE_EXPIRY,
    DEFAULT_MIN_REQUEST_INTERVAL,
    DEFAULT_REQUESTS_PER_MINUTE,
    DEFAULT_RETRY_ATTEMPTS,
    DEFAULT_RETRY_DELAY,
    DEFAULT_TIMEOUT,
    DEFAULT_USER_AGENT,
)


class BaseScraper:
    """Base class for French tax information scrapers.

    This class provides common functionality for scraping tax information from
    official French government websites, including:
    - Rate limiting
    - Caching
    - Retries
    - Error handling
    """

    def __init__(
        self,
        base_url: str,
        cache_dir: Optional[str] = None,
        cache_expiry: int = DEFAULT_CACHE_EXPIRY,
        requests_per_minute: int = DEFAULT_REQUESTS_PER_MINUTE,
        timeout: float = DEFAULT_TIMEOUT,
        retry_attempts: int = DEFAULT_RETRY_ATTEMPTS,
        retry_delay: float = DEFAULT_RETRY_DELAY,
    ):
        """Initialize the scraper.

        Args:
            base_url: Base URL for the website to scrape
            cache_dir: Directory to store cached data (defaults to ~/.french_tax_mcp_cache)
            cache_expiry: Cache expiry time in seconds (defaults to 24 hours)
            requests_per_minute: Maximum number of requests per minute (for rate limiting)
            timeout: Request timeout in seconds
            retry_attempts: Number of retry attempts for failed requests
            retry_delay: Delay between retry attempts in seconds
        """
        self.base_url = base_url
        self.cache_dir = cache_dir or os.path.join(os.path.expanduser(DEFAULT_CACHE_DIR), ".french_tax_mcp_cache")
        self.cache_expiry = cache_expiry
        self.min_request_interval = 60 / requests_per_minute
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.last_request_time = 0

        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)

        logger.info(f"Initialized scraper for {base_url}")
        logger.info(f"Cache directory: {self.cache_dir}")
        logger.info(f"Rate limiting: {requests_per_minute} requests per minute")

    async def get_page(self, url: str, use_cache: bool = True) -> Response:
        """Get a page from the website with rate limiting and caching.

        Args:
            url: URL to fetch
            use_cache: Whether to use cached data if available

        Returns:
            Response object
        """
        # Construct full URL if relative
        if not url.startswith("http"):
            full_url = f"{self.base_url}{url}"
        else:
            full_url = url

        # Check cache first if enabled
        if use_cache:
            cached_data = self._get_from_cache(full_url)
            if cached_data:
                logger.info(f"Using cached data for {full_url}")
                return cached_data

        # Apply rate limiting
        await self._apply_rate_limiting()

        # Make request with retries
        for attempt in range(self.retry_attempts):
            try:
                logger.info(f"Fetching {full_url} (attempt {attempt + 1}/{self.retry_attempts})")

                async with AsyncClient() as client:
                    headers = {
                        "User-Agent": DEFAULT_USER_AGENT,
                        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
                    }

                    response = await client.get(full_url, headers=headers, follow_redirects=True, timeout=self.timeout)

                    # Update last request time
                    self.last_request_time = time.time()

                    # Check if request was successful
                    response.raise_for_status()

                    # Cache the response if successful
                    if use_cache:
                        self._save_to_cache(full_url, response)

                    return response

            except Exception as e:
                logger.warning(f"Error fetching {full_url}: {e}")

                # If this was the last attempt, raise the exception
                if attempt == self.retry_attempts - 1:
                    raise

                # Otherwise, wait and retry
                logger.info(f"Retrying in {self.retry_delay} seconds...")
                await asyncio.sleep(self.retry_delay)

    async def _apply_rate_limiting(self) -> None:
        """Apply rate limiting to avoid overloading the website."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.min_request_interval:
            wait_time = self.min_request_interval - time_since_last_request
            logger.info(f"Rate limiting: waiting {wait_time:.2f} seconds")
            await asyncio.sleep(wait_time)

    def _get_cache_path(self, url: str) -> Path:
        """Get the cache file path for a URL.

        Args:
            url: URL to get cache path for

        Returns:
            Path object for the cache file
        """
        # Create a filename from the URL
        import hashlib

        url_hash = hashlib.md5(url.encode()).hexdigest()
        return Path(self.cache_dir) / f"{url_hash}.json"

    def _get_from_cache(self, url: str) -> Optional[Response]:
        """Get cached data for a URL.

        Args:
            url: URL to get cached data for

        Returns:
            Response object if cache hit, None otherwise
        """
        cache_path = self._get_cache_path(url)

        # Check if cache file exists
        if not cache_path.exists():
            return None

        try:
            # Read cache file
            with open(cache_path, "r") as f:
                cache_data = json.load(f)

            # Check if cache is expired
            cache_time = cache_data.get("cache_time", 0)
            if time.time() - cache_time > self.cache_expiry:
                logger.info(f"Cache expired for {url}")
                return None

            # Create a mock response object
            class MockResponse:
                def __init__(self, data):
                    self.text = data.get("text", "")
                    self.status_code = data.get("status_code", 200)
                    self.headers = data.get("headers", {})
                    self.url = data.get("url", url)

                def raise_for_status(self):
                    if self.status_code >= 400:
                        from httpx import HTTPStatusError, Request, Response

                        mock_request = Request("GET", self.url)
                        mock_response = Response(self.status_code, request=mock_request)
                        raise HTTPStatusError(
                            f"HTTP Error: {self.status_code}",
                            request=mock_request,
                            response=mock_response,
                        )

            return MockResponse(cache_data)

        except Exception as e:
            logger.warning(f"Error reading cache for {url}: {e}")
            return None

    def _save_to_cache(self, url: str, response: Response) -> None:
        """Save response data to cache.

        Args:
            url: URL to save cache for
            response: Response object to cache
        """
        cache_path = self._get_cache_path(url)

        try:
            # Create cache data
            cache_data = {
                "url": url,
                "text": response.text,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "cache_time": time.time(),
            }

            # Write cache file
            with open(cache_path, "w") as f:
                json.dump(cache_data, f)

            logger.info(f"Cached data for {url}")

        except Exception as e:
            logger.warning(f"Error caching data for {url}: {e}")

    def parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML content.

        Args:
            html: HTML content to parse

        Returns:
            BeautifulSoup object
        """
        return BeautifulSoup(html, "html.parser")

    def format_result(
        self,
        status: str,
        data: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None,
        source_url: Optional[str] = None,
        error: Optional[Exception] = None,
    ) -> Dict[str, Any]:
        """Format a result dictionary.

        Args:
            status: Status of the result ("success" or "error")
            data: Data to include in the result
            message: Message to include in the result
            source_url: Source URL for the data
            error: Exception if an error occurred

        Returns:
            Formatted result dictionary
        """
        result = {
            "status": status,
            "timestamp": datetime.now().isoformat(),
        }

        if data:
            result["data"] = data

        if message:
            result["message"] = message

        if source_url:
            result["source"] = source_url

        if error:
            result["error"] = str(error)

        return result
