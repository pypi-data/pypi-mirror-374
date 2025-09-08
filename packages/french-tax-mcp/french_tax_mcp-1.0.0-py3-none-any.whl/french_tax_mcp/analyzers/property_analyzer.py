# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance
# with the License. A copy of the License is located at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# or in the 'license' file accompanying this file. This file is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions
# and limitations under the License.

"""Property tax analyzer for French tax information.

This module provides functions to analyze property tax scenarios and calculate tax benefits.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

from french_tax_mcp.constants import (
    DECLARATION_BOXES,
    LMNP_FURNITURE_DEPRECIATION_YEARS,
    LMNP_MICRO_ABATEMENT_RATE,
    LMNP_PROPERTY_DEPRECIATION_YEARS,
    PINEL_MAX_INVESTMENT,
    PINEL_RATES,
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PropertyTaxAnalyzer:
    """Analyzer for French property tax calculations."""

    def __init__(self):
        """Initialize the property tax analyzer."""
        pass

    async def calculate_pinel_benefit(
        self,
        property_price: float,
        commitment_period: int,
        acquisition_date: str,
    ) -> Dict:
        """Calculate Pinel tax benefit based on property price and commitment period.

        Args:
            property_price: Property price in euros
            commitment_period: Commitment period in years (6, 9, or 12)
            acquisition_date: Acquisition date in format 'YYYY-MM-DD'

        Returns:
            Dictionary containing Pinel benefit calculation details
        """
        logger.info(
            f"Calculating Pinel benefit for {property_price}€ property with {commitment_period} year commitment"
        )

        try:
            # Validate commitment period
            if commitment_period not in [6, 9, 12]:
                return {
                    "status": "error",
                    "message": f"Invalid commitment period: {commitment_period}. Must be 6, 9, or 12 years.",
                }

            # Parse acquisition date
            acquisition_year = int(acquisition_date.split("-")[0])

            # Get rate based on acquisition date and commitment period
            rate = self._get_pinel_rate(acquisition_year, commitment_period)

            # Calculate maximum eligible amount (capped at PINEL_MAX_INVESTMENT)
            eligible_amount = min(property_price, PINEL_MAX_INVESTMENT)

            # Calculate total tax reduction
            total_reduction = eligible_amount * rate

            # Calculate annual reduction
            annual_reduction = total_reduction / commitment_period

            return {
                "status": "success",
                "data": {
                    "property_price": property_price,
                    "commitment_period": commitment_period,
                    "acquisition_date": acquisition_date,
                    "acquisition_year": acquisition_year,
                    "rate": rate * 100,  # Convert to percentage
                    "eligible_amount": eligible_amount,
                    "total_reduction": total_reduction,
                    "annual_reduction": annual_reduction,
                    "reduction_schedule": self._generate_reduction_schedule(
                        annual_reduction, commitment_period, acquisition_date
                    ),
                },
                "message": "Successfully calculated Pinel benefit",
            }

        except Exception as e:
            logger.error(f"Error calculating Pinel benefit: {e}")
            return {"status": "error", "message": f"Failed to calculate Pinel benefit: {str(e)}"}

    def _get_pinel_rate(self, acquisition_year: int, commitment_period: int) -> float:
        """Get Pinel rate based on acquisition year and commitment period.

        Args:
            acquisition_year: Year of property acquisition
            commitment_period: Commitment period in years

        Returns:
            Pinel rate as a decimal
        """
        # Check if we have rates for this specific year
        if acquisition_year in PINEL_RATES:
            return PINEL_RATES[acquisition_year].get(commitment_period, 0.0)

        # Use default rates for years not specifically defined
        return PINEL_RATES["default"].get(commitment_period, 0.0)

    def _generate_reduction_schedule(
        self,
        annual_reduction: float,
        commitment_period: int,
        acquisition_date: str,
    ) -> List[Dict]:
        """Generate a schedule of tax reductions over the commitment period.

        Args:
            annual_reduction: Annual tax reduction amount
            commitment_period: Commitment period in years
            acquisition_date: Acquisition date in format 'YYYY-MM-DD'

        Returns:
            List of dictionaries containing reduction schedule details
        """
        schedule = []

        # Parse acquisition date
        acquisition_year = int(acquisition_date.split("-")[0])

        # First tax reduction applies in the year following acquisition
        first_reduction_year = acquisition_year + 1

        for i in range(commitment_period):
            tax_year = first_reduction_year + i
            schedule.append(
                {
                    "year": tax_year,
                    "reduction_amount": annual_reduction,
                    "declaration_year": tax_year + 1,  # Declaration is made the following year
                }
            )

        return schedule

    async def calculate_lmnp_benefit(
        self,
        annual_rent: float,
        expenses: float,
        property_value: float,
        furniture_value: float,
        regime: str = "micro",
    ) -> Dict:
        """Calculate LMNP (Location Meublée Non Professionnelle) tax benefit.

        Args:
            annual_rent: Annual rental income in euros
            expenses: Annual expenses in euros (only used for 'reel' regime)
            property_value: Property value in euros (only used for 'reel' regime)
            furniture_value: Furniture value in euros (only used for 'reel' regime)
            regime: Tax regime ('micro' or 'reel')

        Returns:
            Dictionary containing LMNP benefit calculation details
        """
        logger.info(f"Calculating LMNP benefit for {annual_rent}€ annual rent with {regime} regime")

        try:
            # Validate regime
            if regime not in ["micro", "reel"]:
                return {
                    "status": "error",
                    "message": f"Invalid regime: {regime}. Must be 'micro' or 'reel'.",
                }

            if regime == "micro":
                # Micro-BIC regime: flat-rate deduction
                taxable_income = annual_rent * (1 - LMNP_MICRO_ABATEMENT_RATE)
                deduction = annual_rent * LMNP_MICRO_ABATEMENT_RATE
                deduction_details = [
                    {
                        "type": "flat_rate",
                        "description": "Abattement forfaitaire de 50%",
                        "amount": deduction,
                    }
                ]
            else:
                # Réel regime: actual expenses and depreciation

                # Calculate property depreciation
                property_depreciation = property_value / LMNP_PROPERTY_DEPRECIATION_YEARS

                # Calculate furniture depreciation
                furniture_depreciation = furniture_value / LMNP_FURNITURE_DEPRECIATION_YEARS

                # Total deductions
                total_deduction = expenses + property_depreciation + furniture_depreciation

                # Taxable income
                taxable_income = max(0, annual_rent - total_deduction)

                deduction_details = [
                    {"type": "expenses", "description": "Charges déductibles", "amount": expenses},
                    {
                        "type": "property_depreciation",
                        "description": "Amortissement du bien immobilier (sur 30 ans)",
                        "amount": property_depreciation,
                    },
                    {
                        "type": "furniture_depreciation",
                        "description": "Amortissement des meubles (sur 7 ans)",
                        "amount": furniture_depreciation,
                    },
                ]

            return {
                "status": "success",
                "data": {
                    "annual_rent": annual_rent,
                    "regime": regime,
                    "taxable_income": taxable_income,
                    "deduction_details": deduction_details,
                    "total_deduction": annual_rent - taxable_income,
                    "declaration_info": self._get_lmnp_declaration_info(regime),
                },
                "message": "Successfully calculated LMNP benefit",
            }

        except Exception as e:
            logger.error(f"Error calculating LMNP benefit: {e}")
            return {"status": "error", "message": f"Failed to calculate LMNP benefit: {str(e)}"}

    def _get_lmnp_declaration_info(self, regime: str) -> Dict:
        """Get LMNP declaration information based on regime.

        Args:
            regime: Tax regime ('micro' or 'reel')

        Returns:
            Dictionary containing declaration information
        """
        if regime == "micro":
            return {
                "forms": ["2042", "2042-C-PRO"],
                "boxes": {"2042-C-PRO": ["5ND", "5OD"]},
                "instructions": "Déclarez le montant total des loyers perçus (avant abattement) dans la case 5ND (vous) ou 5OD (conjoint) de la déclaration 2042-C-PRO. L'abattement de 50% sera automatiquement appliqué.",
            }
        else:
            return {
                "forms": ["2042", "2042-C-PRO", "2031"],
                "boxes": {"2042-C-PRO": ["5NA", "5OA"]},
                "instructions": "Déclarez le résultat net (après déduction des charges et amortissements) dans la case 5NA (vous) ou 5OA (conjoint) de la déclaration 2042-C-PRO. Vous devez également remplir la déclaration 2031 pour le détail des revenus et charges.",
            }


# Create a singleton instance
property_tax_analyzer = PropertyTaxAnalyzer()


async def calculate_pinel_benefit(
    property_price: float,
    commitment_period: int,
    acquisition_date: str,
) -> Dict:
    """Calculate Pinel tax benefit based on property price and commitment period.

    Args:
        property_price: Property price in euros
        commitment_period: Commitment period in years (6, 9, or 12)
        acquisition_date: Acquisition date in format 'YYYY-MM-DD'

    Returns:
        Dictionary containing Pinel benefit calculation details
    """
    return await property_tax_analyzer.calculate_pinel_benefit(property_price, commitment_period, acquisition_date)


async def calculate_lmnp_benefit(
    annual_rent: float,
    expenses: float,
    property_value: float,
    furniture_value: float,
    regime: str = "micro",
) -> Dict:
    """Calculate LMNP (Location Meublée Non Professionnelle) tax benefit.

    Args:
        annual_rent: Annual rental income in euros
        expenses: Annual expenses in euros (only used for 'reel' regime)
        property_value: Property value in euros (only used for 'reel' regime)
        furniture_value: Furniture value in euros (only used for 'reel' regime)
        regime: Tax regime ('micro' or 'reel')

    Returns:
        Dictionary containing LMNP benefit calculation details
    """
    return await property_tax_analyzer.calculate_lmnp_benefit(
        annual_rent, expenses, property_value, furniture_value, regime
    )
