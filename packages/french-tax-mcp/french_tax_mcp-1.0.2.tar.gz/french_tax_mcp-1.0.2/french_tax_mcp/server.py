# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance
# with the License. A copy of the License is located at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# or in the 'license' file accompanying this file. This file is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions
# and limitations under the License.

"""French Tax MCP server implementation.

This server provides tools for French tax calculations and information retrieval.
"""

import argparse
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from mcp.server.fastmcp import Context, FastMCP
from pydantic import BaseModel, Field

from french_tax_mcp.analyzers.business_analyzer import calculate_micro_enterprise_tax
from french_tax_mcp.analyzers.income_analyzer import calculate_income_tax
from french_tax_mcp.analyzers.property_analyzer import (
    calculate_lmnp_benefit,
    calculate_pinel_benefit,
)
from french_tax_mcp.report_generator import generate_tax_report
# Import scrapers lazily to avoid initialization delays
# from french_tax_mcp.scrapers.impots_scraper import get_form_info, get_tax_brackets
# from french_tax_mcp.scrapers.legal_scraper import get_tax_article, search_tax_law
# from french_tax_mcp.scrapers.service_public_scraper import (
#     get_tax_deadlines,
#     get_tax_procedure,
# )

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP(
    name="french-tax-mcp",
    instructions="""Use this server for retrieving French tax information, with a focus on individual taxpayers.

    REQUIRED WORKFLOW:
    Retrieve tax information by following these steps in order:

    1. Primary Data Source:
       - MUST first invoke get_tax_info_from_web() to scrape information from official websites

    2. Fallback Mechanism:
       - If web scraping fails, MUST use get_cached_tax_info() to fetch previously cached data

    3. For Specific Tax Schemes:
       - When analyzing specific tax schemes (Pinel, LMNP, etc.), MUST use get_scheme_details()
       - This provides critical rules, eligibility criteria, and calculation methods

    4. Report Generation:
       - MUST generate tax information report using retrieved data via generate_tax_report()
       - The report includes sections for:
         * Overview of the tax scheme/rule
         * Eligibility criteria
         * Calculation methods
         * Important deadlines
         * Recent changes
         * Practical examples

    ACCURACY GUIDELINES:
    - When uncertain about tax rules or calculations, EXCLUDE them rather than making assumptions
    - Always cite the specific article of the tax code or official source
    - PROVIDING LESS INFORMATION IS BETTER THAN GIVING WRONG INFORMATION
    - Always include the effective date of the tax information
    """,
    dependencies=["pydantic", "beautifulsoup4", "httpx"],
)


class TaxInfoRequest(BaseModel):
    """Request model for tax information queries."""

    topic: str = Field(..., description="The tax topic to search for (e.g., 'tranches_impot', 'pinel', 'lmnp')")
    year: Optional[int] = Field(None, description="Tax year (defaults to current year if not specified)")


@mcp.tool(
    name="get_tax_info_from_web",
    description="Get tax information from official French government websites like impots.gouv.fr, service-public.fr, or legifrance.gouv.fr",
)
async def get_tax_info_from_web(tax_topic: str, ctx: Context, year: Optional[int] = None) -> Optional[Dict]:
    """Get tax information from official French government websites.

    Args:
        tax_topic: The tax topic to search for (e.g., 'tranches_impot', 'pinel', 'lmnp')
        year: Optional tax year (defaults to current year if not specified)
        ctx: MCP context for logging and state management

    Returns:
        Dict: Dictionary containing the tax information retrieved from the website
    """
    try:
        # This is a placeholder implementation
        # The actual implementation will be more complex and will use specialized scrapers

        # Set default year to current year if not specified
        if year is None:
            year = datetime.now().year

        await ctx.info(f"Retrieving information about {tax_topic} for year {year}")

        # Map topic to appropriate scraper
        if tax_topic.lower() in ["tranches_impot", "baremes", "tax_brackets"]:
            # Use tax brackets scraper (lazy import)
            from french_tax_mcp.scrapers.impots_scraper import get_tax_brackets
            result = await get_tax_brackets(year)
            return result
        else:
            # Generic response for now
            return {
                "status": "error",
                "message": f"Information for {tax_topic} not yet implemented",
                "year": year,
            }

    except Exception as e:
        await ctx.error(f"Failed to get tax information from web: {e}")
        return {
            "status": "error",
            "message": f"Error retrieving information: {str(e)}",
            "topic": tax_topic,
            "year": year,
        }


@mcp.tool(
    name="get_tax_brackets",
    description="Get income tax brackets (tranches d'imposition) for a specific year",
)
async def get_tax_brackets_wrapper(ctx: Context, year: Optional[int] = None) -> Optional[Dict]:
    """Get income tax brackets for a specific year.

    Args:
        year: Tax year (defaults to current year if not specified)
        ctx: MCP context for logging and state management

    Returns:
        Dict: Dictionary containing the tax brackets and rates
    """
    try:
        # Set default year to current year if not specified
        if year is None:
            year = datetime.now().year

        await ctx.info(f"Retrieving tax brackets for year {year}")

        # Call the implementation from impots_scraper.py (lazy import)
        from french_tax_mcp.scrapers.impots_scraper import get_tax_brackets
        result = await get_tax_brackets(year)
        return result
    except Exception as e:
        await ctx.error(f"Failed to get tax brackets: {e}")
        return {
            "status": "error",
            "message": f"Error retrieving tax brackets: {str(e)}",
            "year": year,
        }


@mcp.tool(
    name="get_scheme_details",
    description="Get detailed information about a specific tax scheme like Pinel, LMNP, etc.",
)
async def get_scheme_details_wrapper(scheme_name: str, ctx: Context, year: Optional[int] = None) -> Optional[Dict]:
    """Get detailed information about a specific tax scheme.

    Args:
        scheme_name: Name of the tax scheme (e.g., 'pinel', 'lmnp', 'ptz')
        year: Tax year (defaults to current year if not specified)
        ctx: MCP context for logging and state management

    Returns:
        Dict: Dictionary containing detailed information about the tax scheme
    """
    try:
        # Set default year to current year if not specified
        if year is None:
            year = datetime.now().year

        await ctx.info(f"Retrieving details for scheme {scheme_name} for year {year}")

        # Try to get information from the scraper first
        try:
            # Use fallback data since web scraping is not implemented yet
            result = None
            if result.get("status") == "success":
                return result
        except Exception as e:
            await ctx.warning(f"Failed to get scheme details from web: {e}. Using fallback data.")

        # If web scraping fails or returns an error, use fallback data
        scheme_name = scheme_name.lower()

        # Provide fallback data for known schemes
        if scheme_name == "lmnp":
            return {
                "status": "success",
                "message": f"Retrieved fallback information for LMNP scheme for {year}",
                "data": {
                    "scheme": "LMNP (Location Meublée Non Professionnelle)",
                    "year": year,
                    "description": "Le statut de Loueur en Meublé Non Professionnel (LMNP) permet de percevoir des revenus locatifs issus de la location meublée non professionnelle.",
                    "eligibility": [
                        "Louer un logement meublé",
                        "Les recettes annuelles de location meublée ne dépassent pas 23 000 € ou ne représentent pas plus de 50% des revenus du foyer fiscal",
                        "Ne pas être inscrit au Registre du Commerce et des Sociétés (RCS) en tant que loueur professionnel",
                    ],
                    "advantages": [
                        "Amortissement du bien immobilier et des meubles",
                        "Déduction des charges liées à la location",
                        "Possibilité d'opter pour le régime micro-BIC si les recettes sont inférieures à 72 600 €",
                        "Pas de cotisations sociales sur les revenus locatifs",
                    ],
                    "taxation": {
                        "regime_reel": "Imposition sur le bénéfice après déduction des charges et amortissements",
                        "micro_bic": "Abattement forfaitaire de 50% sur les recettes brutes",
                    },
                    "declaration": {
                        "forms": ["2042", "2042-C-PRO", "2031 (régime réel)"],
                        "deadline": "31 mai (déclaration en ligne)",
                    },
                    "recent_changes": [
                        f"Pour {year}, le plafond du régime micro-BIC reste fixé à 72 600 €",
                        "La déduction des intérêts d'emprunt reste possible en LMNP",
                    ],
                },
                "source": "Fallback data",
            }
        elif scheme_name == "pinel":
            return {
                "status": "success",
                "message": f"Retrieved fallback information for Pinel scheme for {year}",
                "data": {
                    "scheme": "Dispositif Pinel",
                    "year": year,
                    "description": "Le dispositif Pinel est un mécanisme de défiscalisation immobilière permettant de bénéficier d'une réduction d'impôt pour l'investissement dans un logement neuf destiné à la location.",
                    "eligibility": [
                        "Acquérir un logement neuf ou en VEFA (Vente en l'État Futur d'Achèvement)",
                        "Louer le logement nu comme résidence principale",
                        "Respecter des plafonds de loyers et de ressources des locataires",
                        "Engagement de location de 6, 9 ou 12 ans",
                        "Respect des normes énergétiques (RE2020 ou BBC)",
                    ],
                    "advantages": [
                        "Réduction d'impôt de 10.5% pour 6 ans, 15% pour 9 ans, 17.5% pour 12 ans (taux 2023-2024)",
                        "Pour 2025, réduction à 9% pour 6 ans, 12% pour 9 ans, 14% pour 12 ans",
                        "Plafond d'investissement de 300 000 € et 5 500 €/m²",
                    ],
                    "zones": {
                        "A bis": "Paris et communes limitrophes",
                        "A": "Grande couronne parisienne, Côte d'Azur, Genevois français",
                        "B1": "Grandes agglomérations et villes chères",
                        "B2 et C": "Non éligibles depuis 2018 (sauf dérogation)",
                    },
                    "declaration": {
                        "forms": ["2042", "2042-C"],
                        "deadline": "31 mai (déclaration en ligne)",
                    },
                    "recent_changes": [
                        f"Pour {year}, le dispositif Pinel est en phase de réduction progressive",
                        "Le dispositif Pinel+ (ou Pinel Denormandie) offre des taux plus avantageux pour les logements respectant des critères de performance énergétique supérieurs",
                    ],
                },
                "source": "Fallback data",
            }
        elif scheme_name in ["lmp", "loueur_meuble_professionnel"]:
            return {
                "status": "success",
                "message": f"Retrieved fallback information for LMP scheme for {year}",
                "data": {
                    "scheme": "LMP (Loueur en Meublé Professionnel)",
                    "year": year,
                    "description": "Le statut de Loueur en Meublé Professionnel (LMP) concerne les personnes qui exercent l'activité de location meublée à titre professionnel.",
                    "eligibility": [
                        "Les recettes annuelles de location meublée dépassent 23 000 €",
                        "Ces recettes représentent plus de 50% des revenus du foyer fiscal",
                        "Inscription au Registre du Commerce et des Sociétés (RCS)",
                    ],
                    "advantages": [
                        "Amortissement du bien immobilier et des meubles",
                        "Déduction de toutes les charges liées à l'activité",
                        "Imputation des déficits sur le revenu global",
                        "Exonération des plus-values sous conditions",
                    ],
                    "taxation": {
                        "regime": "Bénéfices Industriels et Commerciaux (BIC)",
                        "cotisations_sociales": "Assujettissement aux cotisations sociales des travailleurs indépendants",
                    },
                    "declaration": {
                        "forms": ["2042", "2042-C-PRO", "2031"],
                        "deadline": "31 mai (déclaration en ligne)",
                    },
                    "recent_changes": [
                        f"Pour {year}, les critères de qualification du LMP restent inchangés",
                        "Vigilance sur la requalification en activité commerciale par l'administration fiscale",
                    ],
                },
                "source": "Fallback data",
            }
        else:
            # For unknown schemes, return a more informative error
            return {
                "status": "error",
                "message": f"Information for scheme {scheme_name} not available",
                "scheme": scheme_name,
                "year": year,
                "available_schemes": ["lmnp", "pinel", "lmp"],
            }
    except Exception as e:
        await ctx.error(f"Failed to get scheme details: {e}")
        return {
            "status": "error",
            "message": f"Error retrieving scheme details: {str(e)}",
            "scheme": scheme_name,
            "year": year,
        }
        return {
            "status": "error",
            "message": f"Error retrieving scheme details: {str(e)}",
            "scheme": scheme_name,
            "year": year,
        }


@mcp.tool(
    name="get_form_details",
    description="Get detailed information about a specific tax form including fields and instructions",
)
async def get_form_details_wrapper(form_number: str, ctx: Context, year: Optional[int] = None) -> Optional[Dict]:
    """Get detailed information about a specific tax form.

    Args:
        form_number: The form number (e.g., '2042', '2044', '2072')
        year: Tax year (defaults to current year if not specified)
        ctx: MCP context for logging and state management

    Returns:
        Dict: Dictionary containing detailed information about the tax form
    """
    try:
        # Set default year to current year if not specified
        if year is None:
            year = datetime.now().year

        await ctx.info(f"Retrieving details for form {form_number} for year {year}")

        # Try to get information from the scraper first
        try:
            from french_tax_mcp.scrapers.impots_scraper import get_form_info
            result = await get_form_info(form_number, year)
            if result.get("status") == "success":
                return result
        except Exception as e:
            await ctx.warning(f"Failed to get form details from web: {e}. Using fallback data.")

        # If web scraping fails or returns an error, use fallback data
        form_number = form_number.strip()

        # Provide fallback data for common forms
        if form_number == "2042":
            return {
                "status": "success",
                "message": f"Retrieved fallback information for form 2042 for {year}",
                "data": {
                    "form": "2042",
                    "year": year,
                    "title": "Déclaration des revenus",
                    "description": "Formulaire principal de déclaration des revenus des personnes physiques.",
                    "sections": [
                        "État civil et situation de famille",
                        "Traitements, salaires, pensions et rentes",
                        "Revenus de capitaux mobiliers",
                        "Plus-values et gains divers",
                        "Revenus fonciers",
                        "Charges déductibles",
                        "Réductions et crédits d'impôt",
                    ],
                    "deadline": f"31 mai {year} (déclaration en ligne)",
                    "related_forms": [
                        {"number": "2042-C", "title": "Déclaration complémentaire"},
                        {"number": "2042-RICI", "title": "Réductions d'impôt et crédits d'impôt"},
                        {"number": "2044", "title": "Revenus fonciers"},
                    ],
                    "download_link": "https://www.impots.gouv.fr/formulaire/2042/declaration-des-revenus",
                },
                "source": "Fallback data",
            }
        elif form_number == "2044":
            return {
                "status": "success",
                "message": f"Retrieved fallback information for form 2044 for {year}",
                "data": {
                    "form": "2044",
                    "year": year,
                    "title": "Déclaration des revenus fonciers",
                    "description": "Formulaire de déclaration des revenus fonciers (locations non meublées).",
                    "sections": [
                        "Propriétés rurales et urbaines",
                        "Recettes brutes",
                        "Frais et charges",
                        "Intérêts d'emprunt",
                        "Détermination du revenu ou déficit",
                    ],
                    "deadline": f"31 mai {year} (avec la déclaration principale)",
                    "related_forms": [
                        {"number": "2042", "title": "Déclaration des revenus"},
                        {
                            "number": "2044-SPE",
                            "title": "Déclaration des revenus fonciers spéciaux",
                        },
                    ],
                    "download_link": "https://www.impots.gouv.fr/formulaire/2044/declaration-des-revenus-fonciers",
                },
                "source": "Fallback data",
            }
        elif form_number == "2031":
            return {
                "status": "success",
                "message": f"Retrieved fallback information for form 2031 for {year}",
                "data": {
                    "form": "2031",
                    "year": year,
                    "title": "Déclaration des résultats BIC",
                    "description": "Formulaire de déclaration des bénéfices industriels et commerciaux (BIC) au régime réel.",
                    "sections": [
                        "Identification de l'entreprise",
                        "Résultat fiscal",
                        "Immobilisations et amortissements",
                        "Provisions",
                        "Plus-values et moins-values",
                    ],
                    "deadline": f"Début mai {year} (entreprises soumises à l'IR)",
                    "related_forms": [
                        {"number": "2033-A à G", "title": "Régime simplifié"},
                        {"number": "2042-C-PRO", "title": "Report des revenus professionnels"},
                    ],
                    "download_link": "https://www.impots.gouv.fr/formulaire/2031-sd/declaration-de-resultats",
                },
                "source": "Fallback data",
            }
        else:
            # For unknown forms, return a more informative error
            return {
                "status": "error",
                "message": f"Information for form {form_number} not available",
                "form": form_number,
                "year": year,
                "available_forms": ["2042", "2044", "2031"],
            }
    except Exception as e:
        await ctx.error(f"Failed to get form details: {e}")
        return {
            "status": "error",
            "message": f"Error retrieving form details: {str(e)}",
            "form": form_number,
            "year": year,
        }


@mcp.tool(
    name="get_cached_tax_info",
    description="Get cached tax information when web scraping fails",
)
async def get_cached_tax_info(tax_topic: str, ctx: Context, year: Optional[int] = None) -> Optional[Dict]:
    """Get cached tax information when web scraping fails.

    Args:
        tax_topic: The tax topic to search for (e.g., 'tranches_impot', 'pinel', 'lmnp')
        year: Optional tax year (defaults to current year if not specified)
        ctx: MCP context for logging and state management

    Returns:
        Dict: Dictionary containing the cached tax information
    """
    try:
        # Set default year to current year if not specified
        if year is None:
            year = datetime.now().year

        await ctx.info(f"Retrieving cached information for {tax_topic} for year {year}")

        # Map topic to appropriate cached data
        if tax_topic.lower() in ["tranches_impot", "baremes", "tax_brackets"]:
            # Use tax brackets fallback data (lazy import)
            from french_tax_mcp.scrapers.impots_scraper import ImpotsScraper

            scraper = ImpotsScraper()
            brackets = scraper._get_fallback_brackets(year)

            return {
                "status": "success",
                "message": f"Retrieved cached tax brackets for {year}",
                "data": {
                    "year": year,
                    "brackets": brackets,
                },
                "source": "cache",
            }
        else:
            # Generic response for now
            return {
                "status": "error",
                "message": f"Cached information for {tax_topic} not yet implemented",
                "topic": tax_topic,
                "year": year,
                "source": "cache",
            }

    except Exception as e:
        await ctx.error(f"Failed to get cached tax information: {e}")
        return {
            "status": "error",
            "message": f"Error retrieving cached information: {str(e)}",
            "topic": tax_topic,
            "year": year,
        }


@mcp.tool(
    name="calculate_income_tax",
    description="Calculate French income tax based on net taxable income and household composition",
)
async def calculate_income_tax_wrapper(
    net_taxable_income: float,
    household_parts: float = 1.0,
    year: Optional[int] = None,
    ctx: Optional[Context] = None,
) -> Optional[Dict]:
    """Calculate income tax based on net taxable income and household composition.

    Args:
        net_taxable_income: Net taxable income in euros
        household_parts: Number of household parts (quotient familial)
        year: Tax year (defaults to current year)
        ctx: MCP context for logging

    Returns:
        Dict: Dictionary containing tax calculation details
    """
    try:
        if ctx:
            await ctx.info(f"Calculating income tax for {net_taxable_income}€ with {household_parts} parts")

        result = await calculate_income_tax(net_taxable_income, household_parts, year)
        return result
    except Exception as e:
        if ctx:
            await ctx.error(f"Failed to calculate income tax: {e}")
        return {
            "status": "error",
            "message": f"Error calculating income tax: {str(e)}",
        }


@mcp.tool(
    name="calculate_pinel_benefit",
    description="Calculate Pinel tax benefit for real estate investment",
)
async def calculate_pinel_benefit_wrapper(
    property_price: float,
    commitment_period: int,
    acquisition_date: str,
    ctx: Optional[Context] = None,
) -> Optional[Dict]:
    """Calculate Pinel tax benefit based on property price and commitment period.

    Args:
        property_price: Property price in euros
        commitment_period: Commitment period in years (6, 9, or 12)
        acquisition_date: Acquisition date in format 'YYYY-MM-DD'
        ctx: MCP context for logging

    Returns:
        Dict: Dictionary containing Pinel benefit calculation details
    """
    try:
        if ctx:
            await ctx.info(f"Calculating Pinel benefit for {property_price}€ property")

        result = await calculate_pinel_benefit(property_price, commitment_period, acquisition_date)
        return result
    except Exception as e:
        if ctx:
            await ctx.error(f"Failed to calculate Pinel benefit: {e}")
        return {
            "status": "error",
            "message": f"Error calculating Pinel benefit: {str(e)}",
        }


@mcp.tool(
    name="calculate_lmnp_benefit",
    description="Calculate LMNP (furnished rental) tax benefit",
)
async def calculate_lmnp_benefit_wrapper(
    annual_rent: float,
    expenses: float = 0,
    property_value: float = 0,
    furniture_value: float = 0,
    regime: str = "micro",
    ctx: Optional[Context] = None,
) -> Optional[Dict]:
    """Calculate LMNP (Location Meublée Non Professionnelle) tax benefit.

    Args:
        annual_rent: Annual rental income in euros
        expenses: Annual expenses in euros (only used for 'reel' regime)
        property_value: Property value in euros (only used for 'reel' regime)
        furniture_value: Furniture value in euros (only used for 'reel' regime)
        regime: Tax regime ('micro' or 'reel')
        ctx: MCP context for logging

    Returns:
        Dict: Dictionary containing LMNP benefit calculation details
    """
    try:
        if ctx:
            await ctx.info(f"Calculating LMNP benefit for {annual_rent}€ annual rent")

        result = await calculate_lmnp_benefit(annual_rent, expenses, property_value, furniture_value, regime)
        return result
    except Exception as e:
        if ctx:
            await ctx.error(f"Failed to calculate LMNP benefit: {e}")
        return {
            "status": "error",
            "message": f"Error calculating LMNP benefit: {str(e)}",
        }


@mcp.tool(
    name="calculate_micro_enterprise_tax",
    description="Calculate taxes for micro-enterprise regime",
)
async def calculate_micro_enterprise_tax_wrapper(
    annual_revenue: float,
    activity_type: str,
    accre_eligible: bool = False,
    year: Optional[int] = None,
    ctx: Optional[Context] = None,
) -> Optional[Dict]:
    """Calculate taxes for micro-enterprise regime.

    Args:
        annual_revenue: Annual revenue in euros
        activity_type: Type of activity ('commercial', 'services', 'liberal')
        accre_eligible: Whether eligible for ACCRE (first-year entrepreneur)
        year: Tax year (defaults to current year)
        ctx: MCP context for logging

    Returns:
        Dict: Dictionary containing tax calculation details
    """
    try:
        if ctx:
            await ctx.info(f"Calculating micro-enterprise tax for {annual_revenue}€ {activity_type} activity")

        result = await calculate_micro_enterprise_tax(annual_revenue, activity_type, accre_eligible, year)
        return result
    except Exception as e:
        if ctx:
            await ctx.error(f"Failed to calculate micro-enterprise tax: {e}")
        return {
            "status": "error",
            "message": f"Error calculating micro-enterprise tax: {str(e)}",
        }


@mcp.tool(
    name="get_tax_procedure",
    description="Get information about a tax procedure from service-public.fr",
)
async def get_tax_procedure_wrapper(
    procedure_name: str,
    ctx: Optional[Context] = None,
) -> Optional[Dict]:
    """Get information about a tax procedure from service-public.fr.

    Args:
        procedure_name: Name of the procedure (e.g., 'declaration_revenus', 'credit_impot')
        ctx: MCP context for logging

    Returns:
        Dict: Dictionary containing procedure information
    """
    try:
        if ctx:
            await ctx.info(f"Getting tax procedure information for {procedure_name}")

        from french_tax_mcp.scrapers.service_public_scraper import get_tax_procedure
        result = await get_tax_procedure(procedure_name)
        return result
    except Exception as e:
        if ctx:
            await ctx.error(f"Failed to get tax procedure: {e}")
        return {
            "status": "error",
            "message": f"Error getting tax procedure: {str(e)}",
        }


@mcp.tool(
    name="get_tax_deadlines",
    description="Get tax deadlines from service-public.fr",
)
async def get_tax_deadlines_wrapper(
    year: Optional[int] = None,
    ctx: Optional[Context] = None,
) -> Optional[Dict]:
    """Get tax deadlines from service-public.fr.

    Args:
        year: The tax year to retrieve deadlines for (defaults to current year)
        ctx: MCP context for logging

    Returns:
        Dict: Dictionary containing tax deadlines
    """
    try:
        if ctx:
            await ctx.info(f"Getting tax deadlines for year {year or 'current'}")

        from french_tax_mcp.scrapers.service_public_scraper import get_tax_deadlines
        result = await get_tax_deadlines(year)
        return result
    except Exception as e:
        if ctx:
            await ctx.error(f"Failed to get tax deadlines: {e}")
        return {
            "status": "error",
            "message": f"Error getting tax deadlines: {str(e)}",
        }


@mcp.tool(
    name="health_check",
    description="Simple health check to verify the server is responsive",
)
async def health_check(ctx: Optional[Context] = None) -> Dict:
    """Simple health check to verify the server is responsive.
    
    Returns:
        Dict: Status information about the server
    """
    if ctx:
        await ctx.info("Health check requested")
    
    return {
        "status": "success",
        "message": "French Tax MCP Server is running",
        "timestamp": datetime.now().isoformat(),
        "available_tools": [
            "calculate_income_tax",
            "get_tax_brackets", 
            "get_scheme_details",
            "calculate_pinel_benefit",
            "calculate_lmnp_benefit"
        ]
    }


@mcp.tool(
    name="get_tax_article",
    description="Get information about a tax law article from legifrance.gouv.fr",
)
async def get_tax_article_wrapper(
    article_id: str,
    ctx: Optional[Context] = None,
) -> Optional[Dict]:
    """Get information about a tax law article from legifrance.gouv.fr.

    Args:
        article_id: Article identifier (e.g., '200', '4B')
        ctx: MCP context for logging

    Returns:
        Dict: Dictionary containing article information
    """
    try:
        if ctx:
            await ctx.info(f"Getting tax article information for {article_id}")

        result = await get_tax_article(article_id)
        return result
    except Exception as e:
        if ctx:
            await ctx.error(f"Failed to get tax article: {e}")
        return {
            "status": "error",
            "message": f"Error getting tax article: {str(e)}",
        }


@mcp.tool(
    name="search_tax_law",
    description="Search for tax law articles on legifrance.gouv.fr",
)
async def search_tax_law_wrapper(
    query: str,
    ctx: Optional[Context] = None,
) -> Optional[Dict]:
    """Search for tax law articles on legifrance.gouv.fr.

    Args:
        query: Search query
        ctx: MCP context for logging

    Returns:
        Dict: Dictionary containing search results
    """
    try:
        if ctx:
            await ctx.info(f"Searching tax law for: {query}")

        result = await search_tax_law(query)
        return result
    except Exception as e:
        if ctx:
            await ctx.error(f"Failed to search tax law: {e}")
        return {
            "status": "error",
            "message": f"Error searching tax law: {str(e)}",
        }


@mcp.tool(
    name="generate_tax_report",
    description="Generate a detailed report about a specific tax topic",
)
async def generate_tax_report_wrapper(
    tax_data: Dict[str, Any],
    topic_name: str,
    output_file: Optional[str] = None,
    format: str = "markdown",
    ctx: Optional[Context] = None,
) -> str:
    """Generate a tax information report.

    Args:
        tax_data: Tax information data
        topic_name: Name of the tax topic
        output_file: Optional path to save the report
        format: Output format ('markdown' or 'csv')
        ctx: MCP context for logging

    Returns:
        str: The generated report
    """
    try:
        if ctx:
            await ctx.info(f"Generating report for {topic_name}")

        report = await generate_tax_report(tax_data, topic_name, output_file, format)
        return report
    except Exception as e:
        if ctx:
            await ctx.error(f"Failed to generate tax report: {e}")
        return f"Error generating report: {str(e)}"


def main():
    """Run the MCP server with CLI argument support."""
    parser = argparse.ArgumentParser(description="French Tax MCP Server")
    parser.add_argument("--sse", action="store_true", help="Use SSE transport")
    parser.add_argument("--streamable-http", action="store_true", help="Use StreamableHTTP transport (default)")
    parser.add_argument("--port", type=int, default=8888, help="Port to run the server on")

    args = parser.parse_args()

    # Set the port
    mcp.settings.port = args.port

    # Run server with appropriate transport
    if args.sse:
        mcp.run(transport="sse")
    elif args.streamable_http:
        # Use StreamableHTTP only when explicitly requested
        mcp.run(transport="streamable-http")
    else:
        # Default to stdio transport (faster and more reliable for MCP)
        mcp.run()


if __name__ == "__main__":
    main()
