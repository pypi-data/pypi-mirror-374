# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance
# with the License. A copy of the License is located at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# or in the 'license' file accompanying this file. This file is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions
# and limitations under the License.

"""Income tax analyzer for French tax information.

This module provides functions to analyze income tax scenarios and calculate taxes.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

from french_tax_mcp.constants import (
    HOUSEHOLD_PARTS_BASE,
    HOUSEHOLD_PARTS_CHILDREN,
    HOUSEHOLD_PARTS_DISABLED,
)
from french_tax_mcp.scrapers.impots_scraper import get_tax_brackets

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IncomeTaxAnalyzer:
    """Analyzer for French income tax calculations."""

    def __init__(self):
        """Initialize the income tax analyzer."""
        self.tax_brackets_cache = {}

    async def calculate_income_tax(
        self,
        net_taxable_income: float,
        household_parts: float = 1.0,
        year: Optional[int] = None,
    ) -> Dict:
        """Calculate income tax based on net taxable income and household composition.

        Args:
            net_taxable_income: Net taxable income in euros
            household_parts: Number of household parts (quotient familial)
            year: Tax year (defaults to current year)

        Returns:
            Dictionary containing tax calculation details
        """
        # Set default year to current year if not specified
        current_year = datetime.now().year
        tax_year = year or current_year - 1  # Default to previous year for tax declarations

        logger.info(
            f"Calculating income tax for {net_taxable_income}€ with {household_parts} parts for year {tax_year}"
        )

        try:
            # Get tax brackets
            brackets_response = await get_tax_brackets(tax_year)

            if brackets_response["status"] != "success":
                return {
                    "status": "error",
                    "message": f"Failed to retrieve tax brackets: {brackets_response.get('message', 'Unknown error')}",
                    "year": tax_year,
                }

            brackets = brackets_response["data"]["brackets"]

            # Calculate income tax
            tax_result = self._calculate_tax(net_taxable_income, household_parts, brackets)

            return {
                "status": "success",
                "data": {
                    "year": tax_year,
                    "net_taxable_income": net_taxable_income,
                    "household_parts": household_parts,
                    "income_per_part": tax_result["income_per_part"],
                    "tax_per_part": tax_result["tax_per_part"],
                    "total_tax": tax_result["total_tax"],
                    "average_tax_rate": tax_result["average_tax_rate"],
                    "marginal_tax_rate": tax_result["marginal_tax_rate"],
                    "bracket_details": tax_result["bracket_details"],
                },
                "message": f"Successfully calculated income tax for {tax_year}",
            }

        except Exception as e:
            logger.error(f"Error calculating income tax: {e}")
            return {
                "status": "error",
                "message": f"Failed to calculate income tax: {str(e)}",
                "year": tax_year,
            }

    def _calculate_tax(
        self,
        net_taxable_income: float,
        household_parts: float,
        brackets: List[Dict],
    ) -> Dict:
        """Calculate income tax based on brackets.

        Args:
            net_taxable_income: Net taxable income in euros
            household_parts: Number of household parts (quotient familial)
            brackets: List of tax brackets

        Returns:
            Dictionary containing tax calculation details
        """
        # Calculate income per part
        income_per_part = net_taxable_income / household_parts

        # Calculate tax per part
        tax_per_part = 0
        bracket_details = []
        marginal_tax_rate = 0

        for i, bracket in enumerate(brackets):
            min_value = bracket["min"]
            max_value = bracket["max"] if bracket["max"] is not None else float("inf")
            rate = bracket["rate"] / 100  # Convert percentage to decimal

            if income_per_part > min_value:
                # Calculate taxable amount in this bracket
                taxable_in_bracket = min(income_per_part, max_value) - min_value
                tax_in_bracket = taxable_in_bracket * rate

                tax_per_part += tax_in_bracket

                bracket_details.append(
                    {
                        "bracket": i + 1,
                        "min": min_value,
                        "max": max_value if max_value != float("inf") else None,
                        "rate": bracket["rate"],
                        "taxable_amount": taxable_in_bracket,
                        "tax_amount": tax_in_bracket,
                    }
                )

                # Update marginal tax rate if this is the highest bracket used
                if income_per_part <= max_value or max_value == float("inf"):
                    marginal_tax_rate = bracket["rate"]

        # Calculate total tax
        total_tax = tax_per_part * household_parts

        # Calculate average tax rate
        average_tax_rate = (total_tax / net_taxable_income) * 100 if net_taxable_income > 0 else 0

        return {
            "income_per_part": income_per_part,
            "tax_per_part": tax_per_part,
            "total_tax": total_tax,
            "average_tax_rate": average_tax_rate,
            "marginal_tax_rate": marginal_tax_rate,
            "bracket_details": bracket_details,
        }

    async def calculate_household_parts(
        self,
        marital_status: str,
        num_children: int = 0,
        disabled_dependents: int = 0,
    ) -> Dict:
        """Calculate the number of household parts (quotient familial) based on household composition.

        Args:
            marital_status: Marital status ('single', 'married', 'pacs', 'widowed')
            num_children: Number of children
            disabled_dependents: Number of disabled dependents

        Returns:
            Dictionary containing household parts calculation details
        """
        logger.info(
            f"Calculating household parts for {marital_status} with {num_children} children and {disabled_dependents} disabled dependents"
        )

        try:
            # Base parts based on marital status
            base_parts = self._get_base_parts(marital_status)

            # Additional parts for children
            child_parts = self._calculate_child_parts(num_children)

            # Additional parts for disabled dependents
            disabled_parts = disabled_dependents * 0.5

            # Total parts
            total_parts = base_parts + child_parts + disabled_parts

            return {
                "status": "success",
                "data": {
                    "marital_status": marital_status,
                    "num_children": num_children,
                    "disabled_dependents": disabled_dependents,
                    "base_parts": base_parts,
                    "child_parts": child_parts,
                    "disabled_parts": disabled_parts,
                    "total_parts": total_parts,
                },
                "message": "Successfully calculated household parts",
            }

        except Exception as e:
            logger.error(f"Error calculating household parts: {e}")
            return {"status": "error", "message": f"Failed to calculate household parts: {str(e)}"}

    def _get_base_parts(self, marital_status: str) -> float:
        """Get base household parts based on marital status.

        Args:
            marital_status: Marital status ('single', 'married', 'pacs', 'widowed')

        Returns:
            Base household parts
        """
        marital_status = marital_status.lower()

        if marital_status in HOUSEHOLD_PARTS_BASE:
            return HOUSEHOLD_PARTS_BASE[marital_status]
        else:
            raise ValueError(f"Unknown marital status: {marital_status}")

    def _calculate_child_parts(self, num_children: int) -> float:
        """Calculate additional household parts for children.

        Args:
            num_children: Number of children

        Returns:
            Additional household parts for children
        """
        if num_children in HOUSEHOLD_PARTS_CHILDREN:
            return HOUSEHOLD_PARTS_CHILDREN[num_children]
        elif num_children > 2:
            # First two children count as 0.5 parts each, subsequent children as 1 part each
            return HOUSEHOLD_PARTS_CHILDREN[2] + (num_children - 2)
        else:
            return 0.0


# Create a singleton instance
income_tax_analyzer = IncomeTaxAnalyzer()


async def calculate_income_tax(
    net_taxable_income: float,
    household_parts: float = 1.0,
    year: Optional[int] = None,
) -> Dict:
    """Calculate income tax based on net taxable income and household composition.

    Args:
        net_taxable_income: Net taxable income in euros
        household_parts: Number of household parts (quotient familial)
        year: Tax year (defaults to current year)

    Returns:
        Dictionary containing tax calculation details
    """
    return await income_tax_analyzer.calculate_income_tax(net_taxable_income, household_parts, year)


async def calculate_household_parts(
    marital_status: str,
    num_children: int = 0,
    disabled_dependents: int = 0,
) -> Dict:
    """Calculate the number of household parts (quotient familial) based on household composition.

    Args:
        marital_status: Marital status ('single', 'married', 'pacs', 'widowed')
        num_children: Number of children
        disabled_dependents: Number of disabled dependents

    Returns:
        Dictionary containing household parts calculation details
    """
    return await income_tax_analyzer.calculate_household_parts(marital_status, num_children, disabled_dependents)
