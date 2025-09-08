# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance
# with the License. A copy of the License is located at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# or in the 'license' file accompanying this file. This file is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions
# and limitations under the License.

"""Scraper for legifrance.gouv.fr website.

This module provides functions to scrape tax law information from the French legal website.
"""

import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from bs4 import BeautifulSoup, Tag

from french_tax_mcp.scrapers.base_scraper import BaseScraper

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import constants
from french_tax_mcp.constants import LEGIFRANCE_BASE_URL as BASE_URL
from french_tax_mcp.constants import LEGIFRANCE_CGI_URL as CGI_URL
from french_tax_mcp.constants import LEGIFRANCE_SEARCH_URL as SEARCH_URL


class LegalScraper(BaseScraper):
    """Scraper for legifrance.gouv.fr website."""

    def __init__(self):
        """Initialize the legifrance.gouv.fr scraper."""
        super().__init__(BASE_URL)

    async def get_tax_article(self, article_id: str) -> Dict:
        """Scrape information about a tax law article from legifrance.gouv.fr.

        Args:
            article_id: Article identifier (e.g., '200', '4B')

        Returns:
            Dictionary containing information about the article
        """
        logger.info(f"Scraping information for article {article_id}")

        try:
            # Construct URL
            url = f"/codes/id/LEGITEXT000006069577/LEGIARTI000{article_id}"

            # Get the page
            response = await self.get_page(url)

            # Parse HTML
            soup = self.parse_html(response.text)

            # Extract article information
            article_info = self._extract_article_info(soup, article_id)

            return self.format_result(
                status="success",
                data=article_info,
                message=f"Successfully retrieved information for article {article_id}",
                source_url=f"{BASE_URL}{url}",
            )

        except Exception as e:
            logger.error(f"Error scraping article information: {e}")
            return self.format_result(
                status="error",
                message=f"Failed to retrieve article information: {str(e)}",
                data={"article": article_id},
                error=e,
            )

    def _extract_article_info(self, soup: BeautifulSoup, article_id: str) -> Dict:
        """Extract article information from HTML.

        Args:
            soup: BeautifulSoup object
            article_id: Article identifier

        Returns:
            Dictionary containing article information
        """
        # Extract article title
        title_element = soup.find("h1")
        title = title_element.get_text().strip() if title_element else f"Article {article_id}"

        # Extract article content
        content_element = soup.find("div", class_="article-content")
        content = content_element.get_text().strip() if content_element else ""

        # Extract article number
        article_number = ""
        article_number_element = soup.find("div", class_="article-number")
        if article_number_element:
            article_number = article_number_element.get_text().strip()
        else:
            # Try to extract from title
            match = re.search(r"Article\s+(\w+)", title)
            if match:
                article_number = match.group(1)

        # Extract effective date
        effective_date = ""
        date_element = soup.find("div", class_="article-date")
        if date_element:
            date_text = date_element.get_text().strip()
            match = re.search(r"(\d{2}/\d{2}/\d{4})", date_text)
            if match:
                effective_date = match.group(1)

        # Extract related articles
        related_articles = self._extract_related_articles(soup)

        return {
            "article_id": article_id,
            "article_number": article_number,
            "title": title,
            "content": content,
            "effective_date": effective_date,
            "related_articles": related_articles,
        }

    def _extract_related_articles(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract related articles from HTML.

        Args:
            soup: BeautifulSoup object

        Returns:
            List of dictionaries containing related article information
        """
        related_articles = []

        # Look for "See also" or "Related" sections
        for heading in soup.find_all(["h2", "h3", "h4"]):
            heading_text = heading.get_text().lower()

            if any(keyword in heading_text for keyword in ["voir aussi", "articles liés", "références"]):
                # Found a related links section, extract links
                for sibling in heading.next_siblings:
                    if sibling.name in ["h2", "h3", "h4"]:
                        break

                    for link in sibling.find_all("a") if sibling.name else []:
                        href = link.get("href", "")
                        text = link.get_text().strip()

                        if "LEGIARTI" in href:
                            article_match = re.search(r"LEGIARTI000(\d+)", href)
                            if article_match:
                                article_id = article_match.group(1)
                                related_articles.append({"article_id": article_id, "title": text, "url": href})

        return related_articles

    async def search_tax_law(self, query: str) -> Dict:
        """Search for tax law articles on legifrance.gouv.fr.

        Args:
            query: Search query

        Returns:
            Dictionary containing search results
        """
        logger.info(f"Searching for tax law articles with query: {query}")

        try:
            # Construct search URL with comprehensive parameters for tax code articles
            # This includes all article types (L, R, T, A, D, M, V, etc.) and specific tax codes
            # Build URL parameters
            base_params = (
                f"query={query}&corpus=CODES&typePagination=DEFAUT&pageSize=10&page=1"
                "&tab_selection=code&searchField=ALL&searchType=ALL"
            )

            # Article scope parameters (all types: L, R, T, A, D, M, V, etc.)
            article_scopes = [
                "CODE_ARTICLE",
                "CODE_ARTICLE_C",
                "CODE_ARTICLE_L",
                "CODE_ARTICLE_R",
                "CODE_ARTICLE_T",
                "CODE_ARTICLE_A",
                "CODE_ARTICLE_D",
                "CODE_ARTICLE_M",
                "CODE_ARTICLE_V",
                "CODE_ARTICLE_LO",
                "CODE_ARTICLE_LP",
                "CODE_ARTICLE_LR",
                "CODE_ARTICLE_LD",
                "CODE_ARTICLE_LM",
                "CODE_ARTICLE_LV",
                "CODE_ARTICLE_RO",
                "CODE_ARTICLE_RP",
                "CODE_ARTICLE_RR",
                "CODE_ARTICLE_RD",
                "CODE_ARTICLE_RM",
                "CODE_ARTICLE_RV",
                "CODE_ARTICLE_TO",
                "CODE_ARTICLE_TP",
                "CODE_ARTICLE_TR",
                "CODE_ARTICLE_TD",
                "CODE_ARTICLE_TM",
                "CODE_ARTICLE_TV",
                "CODE_ARTICLE_AO",
                "CODE_ARTICLE_AP",
                "CODE_ARTICLE_AR",
                "CODE_ARTICLE_AD",
                "CODE_ARTICLE_AM",
                "CODE_ARTICLE_AV",
                "CODE_ARTICLE_DO",
                "CODE_ARTICLE_DP",
                "CODE_ARTICLE_DR",
                "CODE_ARTICLE_DD",
                "CODE_ARTICLE_DM",
                "CODE_ARTICLE_DV",
                "CODE_ARTICLE_MO",
                "CODE_ARTICLE_MP",
                "CODE_ARTICLE_MR",
                "CODE_ARTICLE_MD",
                "CODE_ARTICLE_MM",
                "CODE_ARTICLE_MV",
                "CODE_ARTICLE_VO",
                "CODE_ARTICLE_VP",
                "CODE_ARTICLE_VR",
                "CODE_ARTICLE_VD",
                "CODE_ARTICLE_VM",
                "CODE_ARTICLE_VV",
            ]
            scope_params = "&".join([f"searchScope={scope}" for scope in article_scopes])

            # Code parameters
            codes = [
                "CGIAN2",
                "CGIAN3",
                "CGIAN4",
                "CGICT",
                "CGILEGIARTI000006308740",
                "CGIPENAL",
                "CGISUBDIV",
                "CGITM",
                "LEGITEXT000006069577",
            ]
            code_params = "&".join([f"code={code}" for code in codes])

            url = f"{SEARCH_URL}/code?{base_params}&{scope_params}&{code_params}"

            # Get the page
            response = await self.get_page(url)

            # Parse HTML
            soup = self.parse_html(response.text)

            # Extract search results
            search_results = self._extract_search_results(soup)

            return self.format_result(
                status="success",
                data={
                    "query": query,
                    "results": search_results,
                },
                message=f"Successfully searched for tax law articles with query: {query}",
                source_url=f"{BASE_URL}{url}",
            )

        except Exception as e:
            logger.error(f"Error searching tax law: {e}")
            return self.format_result(
                status="error",
                message=f"Failed to search tax law: {str(e)}",
                data={"query": query},
                error=e,
            )

    def _extract_search_results(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract search results from HTML.

        Args:
            soup: BeautifulSoup object

        Returns:
            List of dictionaries containing search result information
        """
        results = []

        # Look for search result elements
        result_elements = soup.find_all("div", class_="search-result")

        for result_element in result_elements:
            # Extract title
            title_element = result_element.find("h3")
            title = title_element.get_text().strip() if title_element else ""

            # Extract URL
            url = ""
            link_element = result_element.find("a")
            if link_element:
                url = link_element.get("href", "")

            # Extract snippet
            snippet_element = result_element.find("div", class_="snippet")
            snippet = snippet_element.get_text().strip() if snippet_element else ""

            # Extract article ID
            article_id = ""
            if url:
                article_match = re.search(r"LEGIARTI000(\d+)", url)
                if article_match:
                    article_id = article_match.group(1)

            results.append({"title": title, "url": url, "snippet": snippet, "article_id": article_id})

        return results


# Create a singleton instance
legal_scraper = LegalScraper()


async def get_tax_article(article_id: str) -> Dict:
    """Scrape information about a tax law article from legifrance.gouv.fr.

    Args:
        article_id: Article identifier (e.g., '200', '4B')

    Returns:
        Dictionary containing information about the article
    """
    return await legal_scraper.get_tax_article(article_id)


async def search_tax_law(query: str) -> Dict:
    """Search for tax law articles on legifrance.gouv.fr.

    Args:
        query: Search query

    Returns:
        Dictionary containing search results
    """
    return await legal_scraper.search_tax_law(query)
