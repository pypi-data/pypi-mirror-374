# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance
# with the License. A copy of the License is located at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# or in the 'license' file accompanying this file. This file is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions
# and limitations under the License.

"""Scraper for impots.gouv.fr website.

This module provides functions to scrape tax information from the French tax administration website.
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
    ERROR_MESSAGES,
)
from french_tax_mcp.constants import IMPOTS_BASE_URL as BASE_URL
from french_tax_mcp.constants import IMPOTS_BRACKETS_URL as BRACKETS_URL
from french_tax_mcp.constants import IMPOTS_FORMS_BASE_URL as FORMS_BASE_URL
from french_tax_mcp.constants import IMPOTS_LMNP_URL as LMNP_URL
from french_tax_mcp.constants import IMPOTS_PINEL_URL as PINEL_URL
from french_tax_mcp.constants import (
    SUCCESS_MESSAGES,
    TAX_BRACKETS,
)


class ImpotsScraper(BaseScraper):
    """Scraper for impots.gouv.fr website."""

    def __init__(self):
        """Initialize the impots.gouv.fr scraper."""
        super().__init__(BASE_URL)

    async def get_tax_brackets(self, year: Optional[int] = None) -> Dict:
        """Scrape income tax brackets from impots.gouv.fr.

        Args:
            year: The tax year to retrieve brackets for. Defaults to current year.

        Returns:
            Dictionary containing the tax brackets and rates
        """
        # Set default year to current year if not specified
        current_year = datetime.now().year
        tax_year = year or current_year - 1  # Default to previous year for tax declarations

        logger.info(f"Scraping tax brackets for year {tax_year}")

        try:
            # Try to get the page
            try:
                response = await self.get_page(BRACKETS_URL)

                # Parse HTML
                soup = self.parse_html(response.text)

                # Find the tax brackets table
                # In a real implementation, we would use more robust selectors
                # This is a simplified implementation that looks for tables with specific content
                brackets = []
                tables = soup.find_all("table")

                for table in tables:
                    # Check if this table contains tax brackets
                    if self._is_tax_bracket_table(table):
                        brackets = self._extract_brackets_from_table(table)
                        break

                # If we couldn't find the table, use hardcoded data as fallback
                if not brackets:
                    logger.warning("Could not find tax brackets table, using fallback data")
                    brackets = self._get_fallback_brackets(tax_year)

                return self.format_result(
                    status="success",
                    data={
                        "year": tax_year,
                        "brackets": brackets,
                    },
                    message=f"Successfully retrieved tax brackets for {tax_year}",
                    source_url=f"{BASE_URL}{BRACKETS_URL}",
                )
            except Exception as e:
                logger.warning(f"Failed to scrape tax brackets from web: {e}. Using fallback data.")
                # Use fallback data if web scraping fails
                brackets = self._get_fallback_brackets(tax_year)

                return self.format_result(
                    status="success",
                    data={"year": tax_year, "brackets": brackets, "source": "fallback_data"},
                    message=f"Retrieved fallback tax brackets for {tax_year}",
                    source_url="Internal fallback data",
                )

        except Exception as e:
            logger.error(f"Error retrieving tax brackets: {e}")
            return self.format_result(
                status="error",
                message=f"Failed to retrieve tax brackets: {str(e)}",
                data={"year": tax_year},
                error=e,
            )

    def _get_fallback_brackets(self, year: int) -> List[Dict]:
        """Get fallback tax brackets for a specific year.

        Args:
            year: Tax year

        Returns:
            List of dictionaries containing tax brackets
        """
        # Use the closest year we have data for
        available_years = sorted(TAX_BRACKETS.keys())
        if year in TAX_BRACKETS:
            return TAX_BRACKETS[year]
        elif year < available_years[0]:
            return TAX_BRACKETS[available_years[0]]
        else:
            return TAX_BRACKETS[available_years[-1]]

    def _is_tax_bracket_table(self, table: Tag) -> bool:
        """Check if a table contains tax brackets.

        Args:
            table: BeautifulSoup Tag object for the table

        Returns:
            True if the table contains tax brackets, False otherwise
        """
        # Look for headers or content that would indicate this is a tax bracket table
        text = table.get_text().lower()
        return "tranche" in text and "taux" in text and "%" in text

    def _extract_brackets_from_table(self, table: Tag) -> List[Dict]:
        """Extract tax brackets from a table.

        Args:
            table: BeautifulSoup Tag object for the table

        Returns:
            List of dictionaries containing tax brackets
        """
        brackets = []
        rows = table.find_all("tr")

        # Skip header row
        for row in rows[1:]:
            cells = row.find_all("td")
            if len(cells) >= 2:
                # Extract bracket range and rate
                bracket_range = cells[0].get_text().strip()
                rate_text = cells[1].get_text().strip()

                # Parse bracket range
                min_value, max_value = self._parse_bracket_range(bracket_range)

                # Parse rate
                rate = self._parse_rate(rate_text)

                brackets.append({"min": min_value, "max": max_value, "rate": rate})

        return brackets

    def _parse_bracket_range(self, range_text: str) -> Tuple[int, Optional[int]]:
        """Parse a bracket range string.

        Args:
            range_text: String containing the bracket range (e.g., "0 à 10 777 €")

        Returns:
            Tuple of (min_value, max_value)
        """
        # Remove currency symbol and spaces
        range_text = range_text.replace("€", "").replace(" ", "")

        # Check for different patterns
        if "à" in range_text:
            parts = range_text.split("à")
            min_value = int(parts[0].replace(" ", "").replace("\xa0", ""))
            max_value = int(parts[1].replace(" ", "").replace("\xa0", ""))
            return min_value, max_value
        elif "supérieurà" in range_text or "plusde" in range_text:
            # Handle "supérieur à X" or "plus de X" pattern
            match = re.search(r"(\d+)", range_text)
            if match:
                min_value = int(match.group(1).replace(" ", "").replace("\xa0", ""))
                return min_value, None

        # Default fallback
        return 0, None

    def _parse_rate(self, rate_text: str) -> float:
        """Parse a tax rate string.

        Args:
            rate_text: String containing the tax rate (e.g., "45 %")

        Returns:
            Tax rate as a float
        """
        # Remove % symbol and spaces
        rate_text = rate_text.replace("%", "").strip()

        try:
            return float(rate_text)
        except ValueError:
            return 0.0

    async def get_form_info(self, form_number: str, year: Optional[int] = None) -> Dict:
        """Scrape information about a specific tax form from impots.gouv.fr.

        Args:
            form_number: The form number (e.g., '2042', '2044')
            year: The tax year. Defaults to current year.

        Returns:
            Dictionary containing information about the form
        """
        # Set default year to current year if not specified
        current_year = datetime.now().year
        tax_year = year or current_year

        logger.info(f"Scraping information for form {form_number} for year {tax_year}")

        try:
            # Construct URL
            url = f"{FORMS_BASE_URL}/formulaire-{form_number}.html"

            # Get the page
            response = await self.get_page(url)

            # Parse HTML
            soup = self.parse_html(response.text)

            # Extract form information
            form_info = self._extract_form_info(soup, form_number, tax_year)

            return self.format_result(
                status="success",
                data=form_info,
                message=f"Successfully retrieved information for form {form_number}",
                source_url=f"{BASE_URL}{url}",
            )

        except Exception as e:
            logger.error(f"Error scraping form information: {e}")
            return self.format_result(
                status="error",
                message=f"Failed to retrieve form information: {str(e)}",
                data={"form": form_number, "year": tax_year},
                error=e,
            )

    def _extract_form_info(self, soup: BeautifulSoup, form_number: str, year: int) -> Dict:
        """Extract form information from HTML.

        Args:
            soup: BeautifulSoup object
            form_number: Form number
            year: Tax year

        Returns:
            Dictionary containing form information
        """
        # Extract form title
        title_element = soup.find("h1")
        title = title_element.get_text().strip() if title_element else f"Formulaire {form_number}"

        # Extract form description
        description_element = soup.find("div", class_="description")
        description = description_element.get_text().strip() if description_element else ""

        # Extract download link
        download_link = None
        for link in soup.find_all("a"):
            href = link.get("href", "")
            if ".pdf" in href and form_number in href:
                download_link = href
                break

        # Extract related forms
        related_forms = []
        for link in soup.find_all("a"):
            href = link.get("href", "")
            text = link.get_text().strip()
            if "formulaire-" in href and form_number not in href:
                form_match = re.search(r"formulaire-(\d+)", href)
                if form_match:
                    related_form = form_match.group(1)
                    related_forms.append({"number": related_form, "title": text})

        return {
            "form": form_number,
            "year": year,
            "title": title,
            "description": description,
            "download_link": download_link,
            "related_forms": related_forms,
        }

    async def get_scheme_details(self, scheme_name: str, year: Optional[int] = None) -> Dict:
        """Scrape information about a specific tax scheme from impots.gouv.fr.

        Args:
            scheme_name: Name of the tax scheme (e.g., 'pinel', 'lmnp')
            year: The tax year. Defaults to current year.

        Returns:
            Dictionary containing information about the scheme
        """
        # Set default year to current year if not specified
        current_year = datetime.now().year
        tax_year = year or current_year

        logger.info(f"Scraping information for scheme {scheme_name} for year {tax_year}")

        try:
            # Map scheme name to URL
            url = self._get_scheme_url(scheme_name)

            if not url:
                return self.format_result(
                    status="error",
                    message=f"Unknown scheme: {scheme_name}",
                    data={"scheme": scheme_name, "year": tax_year},
                )

            # Get the page
            response = await self.get_page(url)

            # Parse HTML
            soup = self.parse_html(response.text)

            # Extract scheme information
            scheme_info = self._extract_scheme_info(soup, scheme_name, tax_year)

            return self.format_result(
                status="success",
                data=scheme_info,
                message=f"Successfully retrieved information for scheme {scheme_name}",
                source_url=f"{BASE_URL}{url}",
            )

        except Exception as e:
            logger.error(f"Error scraping scheme information: {e}")
            return self.format_result(
                status="error",
                message=f"Failed to retrieve scheme information: {str(e)}",
                data={"scheme": scheme_name, "year": tax_year},
                error=e,
            )

    def _get_scheme_url(self, scheme_name: str) -> Optional[str]:
        """Get the URL for a tax scheme.

        Args:
            scheme_name: Name of the tax scheme

        Returns:
            URL for the scheme or None if unknown
        """
        scheme_name = scheme_name.lower()

        if scheme_name == "pinel":
            return PINEL_URL
        elif scheme_name in ["lmnp", "location_meublee"]:
            return LMNP_URL
        else:
            return None

    def _extract_scheme_info(self, soup: BeautifulSoup, scheme_name: str, year: int) -> Dict:
        """Extract scheme information from HTML.

        Args:
            soup: BeautifulSoup object
            scheme_name: Scheme name
            year: Tax year

        Returns:
            Dictionary containing scheme information
        """
        # Extract scheme title
        title_element = soup.find("h1")
        title = title_element.get_text().strip() if title_element else f"Dispositif {scheme_name}"

        # Extract main content
        content_element = soup.find("div", class_="main-content")
        content = content_element.get_text().strip() if content_element else ""

        # Extract eligibility criteria
        eligibility = self._extract_section(soup, ["éligibilité", "conditions", "qui peut"])

        # Extract tax advantages
        advantages = self._extract_section(soup, ["avantage", "réduction", "bénéfice"])

        # Extract declaration instructions
        declaration = self._extract_section(soup, ["déclaration", "déclarer", "formulaire"])

        # Extract related forms
        related_forms = []
        for link in soup.find_all("a"):
            href = link.get("href", "")
            text = link.get_text().strip()
            if "formulaire-" in href:
                form_match = re.search(r"formulaire-(\d+)", href)
                if form_match:
                    related_form = form_match.group(1)
                    related_forms.append({"number": related_form, "title": text})

        return {
            "scheme": scheme_name,
            "year": year,
            "title": title,
            "description": content[:500] + "..." if len(content) > 500 else content,
            "eligibility": eligibility,
            "advantages": advantages,
            "declaration": declaration,
            "related_forms": related_forms,
        }

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


# Create a singleton instance
impots_scraper = ImpotsScraper()


async def get_tax_brackets(year: Optional[int] = None) -> Dict:
    """Scrape income tax brackets from impots.gouv.fr.

    Args:
        year: The tax year to retrieve brackets for. Defaults to current year.

    Returns:
        Dictionary containing the tax brackets and rates
    """
    return await impots_scraper.get_tax_brackets(year)


async def get_form_info(form_number: str, year: Optional[int] = None) -> Dict:
    """Scrape information about a specific tax form from impots.gouv.fr.

    Args:
        form_number: The form number (e.g., '2042', '2044')
        year: The tax year. Defaults to current year.

    Returns:
        Dictionary containing information about the form
    """
    return await impots_scraper.get_form_info(form_number, year)


async def get_scheme_details(scheme_name: str, year: Optional[int] = None) -> Dict:
    """Scrape information about a specific tax scheme from impots.gouv.fr.

    Args:
        scheme_name: Name of the tax scheme (e.g., 'pinel', 'lmnp')
        year: The tax year. Defaults to current year.

    Returns:
        Dictionary containing information about the scheme
    """
    return await impots_scraper.get_scheme_details(scheme_name, year)
