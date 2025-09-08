# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance
# with the License. A copy of the License is located at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# or in the 'license' file accompanying this file. This file is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions
# and limitations under the License.

"""Business tax analyzer for French tax information.

This module provides functions to analyze business tax scenarios for individuals.
"""

import logging
from datetime import datetime
from typing import Dict, Optional

from french_tax_mcp.constants import (
    ACCRE_REDUCTION_RATE,
    MICRO_ENTERPRISE_ABATEMENT_RATES,
    MICRO_ENTERPRISE_SOCIAL_CHARGES,
    VERSEMENT_LIBERATOIRE_RATES,
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BusinessTaxAnalyzer:
    """Analyzer for French business tax calculations for individuals."""

    def __init__(self):
        """Initialize the business tax analyzer."""
        pass

    async def calculate_micro_enterprise_tax(
        self,
        annual_revenue: float,
        activity_type: str,
        accre_eligible: bool = False,
        year: Optional[int] = None,
    ) -> Dict:
        """Calculate taxes for micro-enterprise regime.

        Args:
            annual_revenue: Annual revenue in euros
            activity_type: Type of activity ('commercial', 'services', 'liberal')
            accre_eligible: Whether eligible for ACCRE (first-year entrepreneur)
            year: Tax year (defaults to current year)

        Returns:
            Dictionary containing tax calculation details
        """
        # Set default year to current year if not specified
        current_year = datetime.now().year
        tax_year = year or current_year

        logger.info(
            f"Calculating micro-enterprise tax for {annual_revenue}€ {activity_type} activity for year {tax_year}"
        )

        try:
            # Validate activity type
            if activity_type not in ["commercial", "services", "liberal"]:
                return {
                    "status": "error",
                    "message": f"Invalid activity type: {activity_type}. Must be 'commercial', 'services', or 'liberal'.",
                }

            # Get abatement rate based on activity type
            abatement_rate = self._get_abatement_rate(activity_type)

            # Calculate taxable income
            taxable_income = annual_revenue * (1 - abatement_rate)

            # Calculate social charges
            social_charges_rate = self._get_social_charges_rate(activity_type, accre_eligible, tax_year)
            social_charges = annual_revenue * social_charges_rate

            # Calculate income tax (simplified flat rate)
            # Note: In reality, this would be added to other income and taxed progressively
            # This is a simplified calculation for demonstration purposes
            income_tax_rate = 0.15  # Simplified flat rate for demonstration
            income_tax = taxable_income * income_tax_rate

            # Calculate total tax
            total_tax = social_charges + income_tax

            # Calculate net income
            net_income = annual_revenue - total_tax

            return {
                "status": "success",
                "data": {
                    "year": tax_year,
                    "annual_revenue": annual_revenue,
                    "activity_type": activity_type,
                    "accre_eligible": accre_eligible,
                    "abatement_rate": abatement_rate * 100,  # Convert to percentage
                    "taxable_income": taxable_income,
                    "social_charges": {
                        "rate": social_charges_rate * 100,  # Convert to percentage
                        "amount": social_charges,
                    },
                    "income_tax": {
                        "rate": income_tax_rate * 100,  # Convert to percentage
                        "amount": income_tax,
                    },
                    "total_tax": total_tax,
                    "net_income": net_income,
                    "declaration_info": self._get_micro_enterprise_declaration_info(activity_type),
                },
                "message": "Successfully calculated micro-enterprise tax",
            }

        except Exception as e:
            logger.error(f"Error calculating micro-enterprise tax: {e}")
            return {
                "status": "error",
                "message": f"Failed to calculate micro-enterprise tax: {str(e)}",
            }

    def _get_abatement_rate(self, activity_type: str) -> float:
        """Get abatement rate based on activity type.

        Args:
            activity_type: Type of activity

        Returns:
            Abatement rate as a decimal
        """
        return MICRO_ENTERPRISE_ABATEMENT_RATES.get(activity_type, 0.0)

    def _get_social_charges_rate(self, activity_type: str, accre_eligible: bool, year: int) -> float:
        """Get social charges rate based on activity type and ACCRE eligibility.

        Args:
            activity_type: Type of activity
            accre_eligible: Whether eligible for ACCRE
            year: Tax year

        Returns:
            Social charges rate as a decimal
        """
        base_rate = MICRO_ENTERPRISE_SOCIAL_CHARGES.get(activity_type, 0.0)

        # Apply ACCRE reduction if eligible
        if accre_eligible:
            return base_rate * ACCRE_REDUCTION_RATE
        else:
            return base_rate

    def _get_micro_enterprise_declaration_info(self, activity_type: str) -> Dict:
        """Get declaration information based on activity type.

        Args:
            activity_type: Type of activity

        Returns:
            Dictionary containing declaration information
        """
        if activity_type == "commercial":
            return {
                "forms": ["2042", "2042-C-PRO"],
                "boxes": {"2042-C-PRO": ["5KO", "5LO"]},
                "instructions": (
                    "Déclarez le montant total de votre chiffre d'affaires (avant abattement) "
                    "dans la case 5KO (vous) ou 5LO (conjoint) de la déclaration 2042-C-PRO. "
                    "L'abattement de 71% sera automatiquement appliqué."
                ),
            }
        elif activity_type == "services":
            return {
                "forms": ["2042", "2042-C-PRO"],
                "boxes": {"2042-C-PRO": ["5KP", "5LP"]},
                "instructions": (
                    "Déclarez le montant total de votre chiffre d'affaires (avant abattement) "
                    "dans la case 5KP (vous) ou 5LP (conjoint) de la déclaration 2042-C-PRO. "
                    "L'abattement de 50% sera automatiquement appliqué."
                ),
            }
        elif activity_type == "liberal":
            return {
                "forms": ["2042", "2042-C-PRO"],
                "boxes": {"2042-C-PRO": ["5HQ", "5IQ"]},
                "instructions": (
                    "Déclarez le montant total de vos recettes (avant abattement) "
                    "dans la case 5HQ (vous) ou 5IQ (conjoint) de la déclaration 2042-C-PRO. "
                    "L'abattement de 34% sera automatiquement appliqué."
                ),
            }
        else:
            return {}

    async def calculate_auto_entrepreneur_tax(
        self,
        annual_revenue: float,
        activity_type: str,
        versement_liberatoire: bool = False,
        accre_eligible: bool = False,
        year: Optional[int] = None,
    ) -> Dict:
        """Calculate taxes for auto-entrepreneur regime.

        Args:
            annual_revenue: Annual revenue in euros
            activity_type: Type of activity ('commercial', 'services', 'liberal')
            versement_liberatoire: Whether opted for versement libératoire (flat income tax)
            accre_eligible: Whether eligible for ACCRE (first-year entrepreneur)
            year: Tax year (defaults to current year)

        Returns:
            Dictionary containing tax calculation details
        """
        # Set default year to current year if not specified
        current_year = datetime.now().year
        tax_year = year or current_year

        logger.info(
            f"Calculating auto-entrepreneur tax for {annual_revenue}€ {activity_type} activity for year {tax_year}"
        )

        try:
            # Validate activity type
            if activity_type not in ["commercial", "services", "liberal"]:
                return {
                    "status": "error",
                    "message": f"Invalid activity type: {activity_type}. Must be 'commercial', 'services', or 'liberal'.",
                }

            # Get social charges rate based on activity type
            social_charges_rate = self._get_ae_social_charges_rate(activity_type, accre_eligible, tax_year)

            # Calculate social charges
            social_charges = annual_revenue * social_charges_rate

            # Calculate income tax
            if versement_liberatoire:
                # Flat income tax rate based on activity type
                income_tax_rate = self._get_versement_liberatoire_rate(activity_type)
                income_tax = annual_revenue * income_tax_rate
                income_tax_method = "versement_liberatoire"
            else:
                # Get abatement rate based on activity type
                abatement_rate = self._get_abatement_rate(activity_type)

                # Calculate taxable income
                taxable_income = annual_revenue * (1 - abatement_rate)

                # Simplified flat rate for demonstration purposes
                income_tax_rate = 0.15
                income_tax = taxable_income * income_tax_rate
                income_tax_method = "progressive"

            # Calculate total tax
            total_tax = social_charges + income_tax

            # Calculate net income
            net_income = annual_revenue - total_tax

            return {
                "status": "success",
                "data": {
                    "year": tax_year,
                    "annual_revenue": annual_revenue,
                    "activity_type": activity_type,
                    "versement_liberatoire": versement_liberatoire,
                    "accre_eligible": accre_eligible,
                    "social_charges": {
                        "rate": social_charges_rate * 100,  # Convert to percentage
                        "amount": social_charges,
                    },
                    "income_tax": {
                        "method": income_tax_method,
                        "rate": income_tax_rate * 100,  # Convert to percentage
                        "amount": income_tax,
                    },
                    "total_tax": total_tax,
                    "net_income": net_income,
                    "declaration_info": self._get_auto_entrepreneur_declaration_info(
                        activity_type, versement_liberatoire
                    ),
                },
                "message": "Successfully calculated auto-entrepreneur tax",
            }

        except Exception as e:
            logger.error(f"Error calculating auto-entrepreneur tax: {e}")
            return {
                "status": "error",
                "message": f"Failed to calculate auto-entrepreneur tax: {str(e)}",
            }

    def _get_ae_social_charges_rate(self, activity_type: str, accre_eligible: bool, year: int) -> float:
        """Get auto-entrepreneur social charges rate based on activity type and ACCRE eligibility.

        Args:
            activity_type: Type of activity
            accre_eligible: Whether eligible for ACCRE
            year: Tax year

        Returns:
            Social charges rate as a decimal
        """
        # Base rates for 2023
        if activity_type == "commercial":
            base_rate = 0.128  # 12.8%
        elif activity_type == "services":
            base_rate = 0.22  # 22%
        elif activity_type == "liberal":
            base_rate = 0.22  # 22%
        else:
            base_rate = 0.0

        # Apply ACCRE reduction if eligible
        if accre_eligible:
            return base_rate * 0.5  # 50% reduction
        else:
            return base_rate

    def _get_versement_liberatoire_rate(self, activity_type: str) -> float:
        """Get versement libératoire rate based on activity type.

        Args:
            activity_type: Type of activity

        Returns:
            Versement libératoire rate as a decimal
        """
        return VERSEMENT_LIBERATOIRE_RATES.get(activity_type, 0.0)

    def _get_auto_entrepreneur_declaration_info(self, activity_type: str, versement_liberatoire: bool) -> Dict:
        """Get declaration information based on activity type and versement libératoire option.

        Args:
            activity_type: Type of activity
            versement_liberatoire: Whether opted for versement libératoire

        Returns:
            Dictionary containing declaration information
        """
        if versement_liberatoire:
            return {
                "forms": ["2042", "2042-C-PRO"],
                "boxes": {"2042-C-PRO": ["5TA", "5UA"]},
                "instructions": (
                    "Cochez la case 5TA (vous) ou 5UA (conjoint) de la déclaration 2042-C-PRO "
                    "pour indiquer que vous avez opté pour le versement libératoire. "
                    "Vous n'avez pas à déclarer votre chiffre d'affaires sur la déclaration "
                    "de revenus car l'impôt sur le revenu a déjà été payé via le versement libératoire."
                ),
            }
        else:
            # Same as micro-enterprise
            return self._get_micro_enterprise_declaration_info(activity_type)


# Create a singleton instance
business_tax_analyzer = BusinessTaxAnalyzer()


async def calculate_micro_enterprise_tax(
    annual_revenue: float,
    activity_type: str,
    accre_eligible: bool = False,
    year: Optional[int] = None,
) -> Dict:
    """Calculate taxes for micro-enterprise regime.

    Args:
        annual_revenue: Annual revenue in euros
        activity_type: Type of activity ('commercial', 'services', 'liberal')
        accre_eligible: Whether eligible for ACCRE (first-year entrepreneur)
        year: Tax year (defaults to current year)

    Returns:
        Dictionary containing tax calculation details
    """
    return await business_tax_analyzer.calculate_micro_enterprise_tax(
        annual_revenue, activity_type, accre_eligible, year
    )


async def calculate_auto_entrepreneur_tax(
    annual_revenue: float,
    activity_type: str,
    versement_liberatoire: bool = False,
    accre_eligible: bool = False,
    year: Optional[int] = None,
) -> Dict:
    """Calculate taxes for auto-entrepreneur regime.

    Args:
        annual_revenue: Annual revenue in euros
        activity_type: Type of activity ('commercial', 'services', 'liberal')
        versement_liberatoire: Whether opted for versement libératoire (flat income tax)
        accre_eligible: Whether eligible for ACCRE (first-year entrepreneur)
        year: Tax year (defaults to current year)

    Returns:
        Dictionary containing tax calculation details
    """
    return await business_tax_analyzer.calculate_auto_entrepreneur_tax(
        annual_revenue, activity_type, versement_liberatoire, accre_eligible, year
    )
