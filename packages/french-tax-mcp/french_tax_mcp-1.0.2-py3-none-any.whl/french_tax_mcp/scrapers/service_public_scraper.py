# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance
# with the License. A copy of the License is located at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# or in the 'license' file accompanying this file. This file is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions
# and limitations under the License.

"""Scraper for service-public.fr website.

This module provides functions to scrape tax information from the French public service website.
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
from french_tax_mcp.constants import (
    FRENCH_MONTHS,
)
from french_tax_mcp.constants import SERVICE_PUBLIC_BASE_URL as BASE_URL
from french_tax_mcp.constants import SERVICE_PUBLIC_DEADLINES_URL as DEADLINES_URL
from french_tax_mcp.constants import SERVICE_PUBLIC_INCOME_TAX_URL as INCOME_TAX_URL
from french_tax_mcp.constants import SERVICE_PUBLIC_PARTICULIERS_URL as PARTICULIERS_URL
from french_tax_mcp.constants import SERVICE_PUBLIC_PROPERTY_TAX_URL as PROPERTY_TAX_URL
from french_tax_mcp.constants import SERVICE_PUBLIC_TAX_SECTION_URL as TAX_SECTION_URL


class ServicePublicScraper(BaseScraper):
    """Scraper for service-public.fr website."""

    def __init__(self):
        """Initialize the service-public.fr scraper."""
        super().__init__(BASE_URL)

    async def get_tax_procedure(self, procedure_name: str) -> Dict:
        """Scrape information about a tax procedure from service-public.fr.

        Args:
            procedure_name: Name of the procedure (e.g., 'declaration_revenus', 'credit_impot')

        Returns:
            Dictionary containing information about the procedure
        """
        logger.info(f"Scraping information for procedure {procedure_name}")

        try:
            # Map procedure name to URL
            url = self._get_procedure_url(procedure_name)

            if not url:
                return self.format_result(
                    status="error",
                    message=f"Unknown procedure: {procedure_name}",
                    data={"procedure": procedure_name},
                )

            # Get the page
            response = await self.get_page(url)

            # Parse HTML
            soup = self.parse_html(response.text)

            # Extract procedure information
            procedure_info = self._extract_procedure_info(soup, procedure_name)

            return self.format_result(
                status="success",
                data=procedure_info,
                message=f"Successfully retrieved information for procedure {procedure_name}",
                source_url=f"{BASE_URL}{url}",
            )

        except Exception as e:
            logger.error(f"Error scraping procedure information: {e}")
            return self.format_result(
                status="error",
                message=f"Failed to retrieve procedure information: {str(e)}",
                data={"procedure": procedure_name},
                error=e,
            )

    def _get_procedure_url(self, procedure_name: str) -> Optional[str]:
        """Get the URL for a tax procedure.

        Args:
            procedure_name: Name of the procedure

        Returns:
            URL for the procedure or None if unknown
        """
        procedure_name = procedure_name.lower()

        # Map common procedure names to URLs
        procedure_map = {
            "declaration_revenus": "/particuliers/vosdroits/F358",
            "credit_impot": "/particuliers/vosdroits/F31201",
            "prelevement_source": "/particuliers/vosdroits/F34009",
            "taxe_habitation": "/particuliers/vosdroits/F42",
            "taxe_fonciere": "/particuliers/vosdroits/F59",
            "deadlines": DEADLINES_URL,
            "echeances": DEADLINES_URL,
            "dates_limites": DEADLINES_URL,
        }

        return procedure_map.get(procedure_name)

    def _extract_procedure_info(self, soup: BeautifulSoup, procedure_name: str) -> Dict:
        """Extract procedure information from HTML.

        Args:
            soup: BeautifulSoup object
            procedure_name: Procedure name

        Returns:
            Dictionary containing procedure information
        """
        # Extract procedure title
        title_element = soup.find("h1")
        title = title_element.get_text().strip() if title_element else f"Procédure {procedure_name}"

        # Extract main content
        content_element = soup.find("div", class_="main-content")
        content = content_element.get_text().strip() if content_element else ""

        # Extract steps
        steps = self._extract_steps(soup)

        # Extract requirements
        requirements = self._extract_section(soup, ["conditions", "qui est concerné", "pour qui"])

        # Extract deadlines
        deadlines = self._extract_section(soup, ["date", "délai", "échéance", "quand"])

        # Extract related procedures
        related_procedures = self._extract_related_procedures(soup)

        return {
            "procedure": procedure_name,
            "title": title,
            "description": content[:500] + "..." if len(content) > 500 else content,
            "steps": steps,
            "requirements": requirements,
            "deadlines": deadlines,
            "related_procedures": related_procedures,
        }

    def _extract_steps(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract procedure steps from HTML.

        Args:
            soup: BeautifulSoup object

        Returns:
            List of dictionaries containing step information
        """
        steps = []

        # Look for step elements
        step_elements = soup.find_all("div", class_="step")

        if step_elements:
            for i, step_element in enumerate(step_elements):
                title_element = step_element.find(["h2", "h3", "h4"])
                title = title_element.get_text().strip() if title_element else f"Étape {i+1}"

                content_element = step_element.find("div", class_="step-content")
                content = content_element.get_text().strip() if content_element else ""

                steps.append({"number": i + 1, "title": title, "content": content})
        else:
            # Alternative approach: look for numbered headings
            for heading in soup.find_all(["h2", "h3"]):
                heading_text = heading.get_text().strip()

                # Check if heading starts with a number or contains step-like words
                if re.match(r"^\d+\.", heading_text) or any(
                    word in heading_text.lower() for word in ["étape", "phase", "partie"]
                ):
                    content = []
                    for sibling in heading.next_siblings:
                        if sibling.name in ["h2", "h3"]:
                            break
                        if sibling.name:
                            content.append(sibling.get_text().strip())

                    steps.append(
                        {
                            "number": len(steps) + 1,
                            "title": heading_text,
                            "content": "\n".join(content),
                        }
                    )

        return steps

    def _extract_section(self, soup: BeautifulSoup, keywords: List[str]) -> str:
        """Extract a section from HTML based on keywords.

        Args:
            soup: BeautifulSoup object
            keywords: List of keywords to look for

        Returns:
            Extracted section text
        """
        # Look for headings containing keywords
        for heading in soup.find_all(["h2", "h3", "h4"]):
            heading_text = heading.get_text().lower()

            if any(keyword in heading_text for keyword in keywords):
                # Found a matching heading, extract the content until the next heading
                content = []
                for sibling in heading.next_siblings:
                    if sibling.name in ["h2", "h3", "h4"]:
                        break
                    if sibling.name:
                        content.append(sibling.get_text().strip())

                return "\n".join(content)

        # If no matching heading found, look for paragraphs containing keywords
        for paragraph in soup.find_all("p"):
            paragraph_text = paragraph.get_text().lower()

            if any(keyword in paragraph_text for keyword in keywords):
                return paragraph.get_text().strip()

        return ""

    def _extract_related_procedures(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract related procedures from HTML.

        Args:
            soup: BeautifulSoup object

        Returns:
            List of dictionaries containing related procedure information
        """
        related_procedures = []

        # Look for "See also" or "Related" sections
        for heading in soup.find_all(["h2", "h3", "h4"]):
            heading_text = heading.get_text().lower()

            if any(
                keyword in heading_text for keyword in ["voir aussi", "à voir également", "en lien", "liens utiles"]
            ):
                # Found a related links section, extract links
                for sibling in heading.next_siblings:
                    if sibling.name in ["h2", "h3", "h4"]:
                        break

                    for link in sibling.find_all("a") if sibling.name else []:
                        href = link.get("href", "")
                        text = link.get_text().strip()

                        if href.startswith("/particuliers/vosdroits/"):
                            related_procedures.append({"title": text, "url": href})

        # Also look for related links in the sidebar
        sidebar = soup.find("div", class_="sidebar")
        if sidebar:
            for link in sidebar.find_all("a"):
                href = link.get("href", "")
                text = link.get_text().strip()

                if href.startswith("/particuliers/vosdroits/") and text:
                    related_procedures.append({"title": text, "url": href})

        return related_procedures

    async def get_tax_deadlines(self, year: Optional[int] = None) -> Dict:
        """Scrape tax deadlines from service-public.fr.

        Args:
            year: The tax year to retrieve deadlines for. Defaults to current year.

        Returns:
            Dictionary containing tax deadlines
        """
        # Set default year to current year if not specified
        current_year = datetime.now().year
        tax_year = year or current_year

        logger.info(f"Scraping tax deadlines for year {tax_year}")

        try:
            # Get the page
            response = await self.get_page(DEADLINES_URL)

            # Parse HTML
            soup = self.parse_html(response.text)

            # Extract deadlines
            deadlines = self._extract_deadlines(soup, tax_year)

            return self.format_result(
                status="success",
                data={
                    "year": tax_year,
                    "deadlines": deadlines,
                },
                message=f"Successfully retrieved tax deadlines for {tax_year}",
                source_url=f"{BASE_URL}{DEADLINES_URL}",
            )

        except Exception as e:
            logger.error(f"Error scraping tax deadlines: {e}")
            return self.format_result(
                status="error",
                message=f"Failed to retrieve tax deadlines: {str(e)}",
                data={"year": tax_year},
                error=e,
            )

    def _extract_deadlines(self, soup: BeautifulSoup, year: int) -> List[Dict]:
        """Extract tax deadlines from HTML.

        Args:
            soup: BeautifulSoup object
            year: Tax year

        Returns:
            List of dictionaries containing deadline information
        """
        deadlines = []

        # Look for tables containing deadlines
        tables = soup.find_all("table")

        for table in tables:
            # Check if this table contains deadlines
            table_text = table.get_text().lower()
            if "date" in table_text and str(year) in table_text:
                rows = table.find_all("tr")

                # Skip header row
                for row in rows[1:]:
                    cells = row.find_all("td")

                    if len(cells) >= 2:
                        # Extract deadline information
                        date_cell = cells[0].get_text().strip()
                        description_cell = cells[1].get_text().strip()

                        # Parse date
                        date_match = re.search(r"(\d{1,2})\s+(\w+)\s+(\d{4})", date_cell)
                        if date_match:
                            day = date_match.group(1)
                            month = self._parse_french_month(date_match.group(2))
                            year = date_match.group(3)

                            deadlines.append(
                                {
                                    "date": f"{year}-{month:02d}-{int(day):02d}",
                                    "description": description_cell,
                                }
                            )

        # If no deadlines found in tables, look for lists
        if not deadlines:
            for list_element in soup.find_all(["ul", "ol"]):
                list_text = list_element.get_text().lower()

                if "date" in list_text and str(year) in list_text:
                    for item in list_element.find_all("li"):
                        item_text = item.get_text().strip()

                        # Look for date patterns
                        date_match = re.search(r"(\d{1,2})\s+(\w+)\s+(\d{4})", item_text)
                        if date_match:
                            day = date_match.group(1)
                            month = self._parse_french_month(date_match.group(2))
                            year = date_match.group(3)

                            # Extract description (text after the date)
                            description = item_text[date_match.end() :].strip()
                            if not description:
                                description = item_text

                            deadlines.append(
                                {
                                    "date": f"{year}-{month:02d}-{int(day):02d}",
                                    "description": description,
                                }
                            )

        return deadlines

    def _parse_french_month(self, month_name: str) -> int:
        """Parse a French month name to a month number.

        Args:
            month_name: French month name

        Returns:
            Month number (1-12)
        """
        month_name = month_name.lower()

        # Find the closest match
        for french_month, month_num in FRENCH_MONTHS.items():
            if french_month in month_name:
                return month_num

        # Default to January if no match found
        return 1


# Create a singleton instance
service_public_scraper = ServicePublicScraper()


async def get_tax_procedure(procedure_name: str) -> Dict:
    """Scrape information about a tax procedure from service-public.fr.

    Args:
        procedure_name: Name of the procedure (e.g., 'declaration_revenus', 'credit_impot')

    Returns:
        Dictionary containing information about the procedure
    """
    return await service_public_scraper.get_tax_procedure(procedure_name)


async def get_tax_deadlines(year: Optional[int] = None) -> Dict:
    """Scrape tax deadlines from service-public.fr.

    Args:
        year: The tax year to retrieve deadlines for. Defaults to current year.

    Returns:
        Dictionary containing tax deadlines
    """
    return await service_public_scraper.get_tax_deadlines(year)
