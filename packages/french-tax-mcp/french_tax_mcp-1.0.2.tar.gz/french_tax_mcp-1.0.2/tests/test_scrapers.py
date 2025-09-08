# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance
# with the License. A copy of the License is located at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# or in the 'license' file accompanying this file. This file is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions
# and limitations under the License.

"""Tests for the scrapers."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from french_tax_mcp.scrapers.base_scraper import BaseScraper
from french_tax_mcp.scrapers.impots_scraper import ImpotsScraper
from french_tax_mcp.scrapers.legal_scraper import LegalScraper
from french_tax_mcp.scrapers.service_public_scraper import ServicePublicScraper


class TestBaseScraper:
    """Tests for the BaseScraper class."""

    @pytest.mark.asyncio
    async def test_get_page(self):
        """Test the get_page method."""
        # Create a mock response
        mock_response = MagicMock()
        mock_response.text = "<html>Test</html>"
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "text/html"}

        # Create a mock client context manager
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None

        # Patch the AsyncClient
        with patch("french_tax_mcp.scrapers.base_scraper.AsyncClient", return_value=mock_client):
            # Create a scraper
            scraper = BaseScraper("https://example.com")

            # Call get_page with caching disabled
            response = await scraper.get_page("/test", use_cache=False)

            # Check that the client was called with the correct URL
            mock_client.get.assert_called_once()
            args, kwargs = mock_client.get.call_args
            assert args[0] == "https://example.com/test"

            # Check that the response was returned
            assert response.text == "<html>Test</html>"

    def test_parse_html(self):
        """Test the parse_html method."""
        # Create a scraper
        scraper = BaseScraper("https://example.com")

        # Call parse_html
        soup = scraper.parse_html("<html><body><h1>Test</h1></body></html>")

        # Check that the HTML was parsed correctly
        assert soup.h1.text == "Test"

    def test_format_result(self):
        """Test the format_result method."""
        # Create a scraper
        scraper = BaseScraper("https://example.com")

        # Call format_result
        result = scraper.format_result(
            status="success",
            data={"test": "value"},
            message="Test message",
            source_url="https://example.com/test",
        )

        # Check that the result was formatted correctly
        assert result["status"] == "success"
        assert result["data"] == {"test": "value"}
        assert result["message"] == "Test message"
        assert result["source"] == "https://example.com/test"
        assert "timestamp" in result


class TestImpotsScraper:
    """Tests for the ImpotsScraper class."""

    @pytest.mark.asyncio
    async def test_get_tax_brackets(self, mock_tax_brackets_response):
        """Test the get_tax_brackets method."""
        # Create a mock scraper
        scraper = ImpotsScraper()

        # Mock the get_page method
        scraper.get_page = AsyncMock(return_value=MagicMock(text=mock_tax_brackets_response))

        # Call get_tax_brackets
        result = await scraper.get_tax_brackets(2023)

        # Check that get_page was called with the correct URL
        scraper.get_page.assert_called_once_with("/particulier/baremes-impot-revenu")

        # Check that the result was formatted correctly
        assert result["status"] == "success"
        assert "data" in result
        assert "year" in result["data"]
        assert result["data"]["year"] == 2023
        assert "brackets" in result["data"]

    @pytest.mark.asyncio
    async def test_get_form_info(self, mock_form_response):
        """Test the get_form_info method."""
        # Create a mock scraper
        scraper = ImpotsScraper()

        # Mock the get_page method
        scraper.get_page = AsyncMock(return_value=MagicMock(text=mock_form_response))

        # Call get_form_info
        result = await scraper.get_form_info("2042", 2023)

        # Check that get_page was called with the correct URL
        scraper.get_page.assert_called_once_with("/formulaires/formulaire-2042.html")

        # Check that the result was formatted correctly
        assert result["status"] == "success"
        assert "data" in result
        assert "form" in result["data"]
        assert result["data"]["form"] == "2042"
        assert "year" in result["data"]
        assert result["data"]["year"] == 2023

    @pytest.mark.asyncio
    async def test_get_scheme_details(self, mock_scheme_response):
        """Test the get_scheme_details method."""
        # Create a mock scraper
        scraper = ImpotsScraper()

        # Mock the get_page method
        scraper.get_page = AsyncMock(return_value=MagicMock(text=mock_scheme_response))

        # Mock the _get_scheme_url method
        scraper._get_scheme_url = MagicMock(
            return_value="/particulier/questions/comment-beneficier-du-dispositif-pinel"
        )

        # Call get_scheme_details
        result = await scraper.get_scheme_details("pinel", 2023)

        # Check that get_page was called with the correct URL
        scraper.get_page.assert_called_once_with(
            "/particulier/questions/comment-beneficier-du-dispositif-pinel"
        )

        # Check that the result was formatted correctly
        assert result["status"] == "success"
        assert "data" in result
        assert "scheme" in result["data"]
        assert result["data"]["scheme"] == "pinel"
        assert "year" in result["data"]
        assert result["data"]["year"] == 2023


class TestServicePublicScraper:
    """Tests for the ServicePublicScraper class."""

    @pytest.mark.asyncio
    async def test_get_tax_procedure(self):
        """Test the get_tax_procedure method."""
        # Create a mock scraper
        scraper = ServicePublicScraper()

        # Mock the get_page method
        scraper.get_page = AsyncMock(
            return_value=MagicMock(text="<html><body><h1>Test</h1></body></html>")
        )

        # Mock the _get_procedure_url method
        scraper._get_procedure_url = MagicMock(return_value="/particuliers/vosdroits/F358")

        # Call get_tax_procedure
        result = await scraper.get_tax_procedure("declaration_revenus")

        # Check that get_page was called with the correct URL
        scraper.get_page.assert_called_once_with("/particuliers/vosdroits/F358")

        # Check that the result was formatted correctly
        assert result["status"] == "success"
        assert "data" in result
        assert "procedure" in result["data"]
        assert result["data"]["procedure"] == "declaration_revenus"

    @pytest.mark.asyncio
    async def test_get_tax_deadlines(self, mock_deadlines_response):
        """Test the get_tax_deadlines method."""
        # Create a mock scraper
        scraper = ServicePublicScraper()

        # Mock the get_page method
        scraper.get_page = AsyncMock(return_value=MagicMock(text=mock_deadlines_response))

        # Call get_tax_deadlines
        result = await scraper.get_tax_deadlines(2023)

        # Check that get_page was called with the correct URL
        scraper.get_page.assert_called_once_with("/particuliers/vosdroits/F34974")

        # Check that the result was formatted correctly
        assert result["status"] == "success"
        assert "data" in result
        assert "year" in result["data"]
        assert result["data"]["year"] == 2023
        assert "deadlines" in result["data"]


class TestLegalScraper:
    """Tests for the LegalScraper class."""

    @pytest.mark.asyncio
    async def test_get_tax_article(self, mock_article_response):
        """Test the get_tax_article method."""
        # Create a mock scraper
        scraper = LegalScraper()

        # Mock the get_page method
        scraper.get_page = AsyncMock(return_value=MagicMock(text=mock_article_response))

        # Call get_tax_article
        result = await scraper.get_tax_article("12345")

        # Check that get_page was called with the correct URL
        scraper.get_page.assert_called_once_with("/codes/id/LEGITEXT000006069577/LEGIARTI00012345")

        # Check that the result was formatted correctly
        assert result["status"] == "success"
        assert "data" in result
        assert "article_id" in result["data"]
        assert result["data"]["article_id"] == "12345"

    @pytest.mark.asyncio
    async def test_search_tax_law(self):
        """Test the search_tax_law method."""
        # Create a mock scraper
        scraper = LegalScraper()

        # Mock the get_page method
        scraper.get_page = AsyncMock(
            return_value=MagicMock(
                text="<html><body><div class='search-result'><h3>Test</h3></div></body></html>"
            )
        )

        # Call search_tax_law
        result = await scraper.search_tax_law("test")

        # Check that get_page was called with the correct URL
        scraper.get_page.assert_called_once()
        args, kwargs = scraper.get_page.call_args
        assert "/recherche/code?query=test" in args[0]

        # Check that the result was formatted correctly
        assert result["status"] == "success"
        assert "data" in result
        assert "query" in result["data"]
        assert result["data"]["query"] == "test"
        assert "results" in result["data"]
