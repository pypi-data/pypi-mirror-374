# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance
# with the License. A copy of the License is located at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# or in the 'license' file accompanying this file. This file is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions
# and limitations under the License.

"""Helper functions for the French tax MCP server."""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

from french_tax_mcp.constants import IMPOTS_BASE_URL, IMPOTS_FORMS_BASE_URL, TAX_SCHEMES

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaxHelper:
    """Helper class for French tax information."""

    @staticmethod
    def format_currency(amount: float) -> str:
        """Format a currency amount.

        Args:
            amount: Amount to format

        Returns:
            Formatted currency string
        """
        return f"{amount:,.2f} €".replace(",", " ").replace(".", ",")

    @staticmethod
    def format_percentage(value: float) -> str:
        """Format a percentage value.

        Args:
            value: Percentage value to format

        Returns:
            Formatted percentage string
        """
        return f"{value:.2f}%".replace(".", ",")

    @staticmethod
    def format_date(date_str: str) -> str:
        """Format a date string.

        Args:
            date_str: Date string in format 'YYYY-MM-DD'

        Returns:
            Formatted date string in format 'DD/MM/YYYY'
        """
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            return date.strftime("%d/%m/%Y")
        except ValueError:
            return date_str

    @staticmethod
    def get_tax_year() -> int:
        """Get the current tax year.

        In France, the tax year is the previous calendar year.

        Returns:
            Current tax year
        """
        return datetime.now().year - 1

    @staticmethod
    def get_declaration_year() -> int:
        """Get the current declaration year.

        In France, taxes are declared in the year following the tax year.

        Returns:
            Current declaration year
        """
        return datetime.now().year

    @staticmethod
    def get_tax_form_url(form_number: str) -> str:
        """Get the URL for a tax form.

        Args:
            form_number: Form number

        Returns:
            URL for the form
        """
        return f"{IMPOTS_BASE_URL}{IMPOTS_FORMS_BASE_URL}/download/pdf/{form_number}"

    @staticmethod
    def get_tax_calendar() -> Dict[str, str]:
        """Get the tax calendar for the current year.

        Returns:
            Dictionary mapping event names to dates
        """
        current_year = datetime.now().year

        # This is a simplified calendar
        # In a real implementation, this would be retrieved from an official source
        return {
            "declaration_online_start": f"April 1, {current_year}",
            "declaration_online_end": f"June 8, {current_year}",
            "declaration_paper": f"May 21, {current_year}",
            "tax_notice": f"July-August, {current_year}",
            "payment_deadline": f"September 15, {current_year}",
        }

    @staticmethod
    def map_topic_to_url(topic: str) -> str:
        """Map a tax topic to a URL.

        Args:
            topic: Tax topic

        Returns:
            URL for the topic
        """
        topic_lower = topic.lower()

        # Check if it's a known tax scheme
        for scheme_key, scheme_info in TAX_SCHEMES.items():
            if scheme_key in topic_lower:
                return f"{IMPOTS_BASE_URL}{scheme_info['url']}"

        # Map other common topics to URLs
        topic_map = {
            "impot_revenu": f"{IMPOTS_BASE_URL}/particulier/questions/comment-declarer-mes-revenus",
            "micro_entreprise": f"{IMPOTS_BASE_URL}/professionnel/questions/je-cree-mon-entreprise-quel-regime-fiscal-choisir",
            "auto_entrepreneur": f"{IMPOTS_BASE_URL}/professionnel/questions/je-cree-mon-entreprise-quel-regime-fiscal-choisir",
            "credit_impot": f"{IMPOTS_BASE_URL}/particulier/questions/puis-je-beneficier-de-credits-ou-de-reductions-dimpot",
            "prelevement_source": f"{IMPOTS_BASE_URL}/particulier/questions/comment-fonctionne-le-prelevement-la-source",
        }

        # Try to find a match
        for key, url in topic_map.items():
            if key in topic_lower:
                return url

        # Default to the main page
        return f"{IMPOTS_BASE_URL}/particulier"
