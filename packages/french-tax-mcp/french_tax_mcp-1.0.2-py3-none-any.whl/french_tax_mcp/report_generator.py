# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance
# with the License. A copy of the License is located at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# or in the 'license' file accompanying this file. This file is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions
# and limitations under the License.

"""Report generator for French tax information.

This module provides functions to generate comprehensive reports about French tax topics.
"""

import csv
import io
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from french_tax_mcp.static.templates.report_template import (
    BASE_REPORT_TEMPLATE,
    CALCULATION_GUIDE_TEMPLATE,
    FORM_GUIDE_TEMPLATE,
    TAX_DEADLINES_TEMPLATE,
    TAX_SCHEME_TEMPLATE,
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generator for French tax information reports."""

    def __init__(self):
        """Initialize the report generator."""
        pass

    async def generate_tax_report(
        self,
        tax_data: Dict[str, Any],
        topic_name: str,
        output_file: Optional[str] = None,
        format: str = "markdown",
    ) -> str:
        """Generate a tax information report.

        Args:
            tax_data: Tax information data
            topic_name: Name of the tax topic
            output_file: Optional path to save the report
            format: Output format ('markdown' or 'csv')

        Returns:
            The generated report
        """
        logger.info(f"Generating report for {topic_name}")

        try:
            # Determine report type based on tax_data
            report_type = self._determine_report_type(tax_data, topic_name)

            # Generate report based on type
            if format.lower() == "csv":
                report = self._generate_csv_report(tax_data, topic_name, report_type)
            else:
                report = self._generate_markdown_report(tax_data, topic_name, report_type)

            # Save to file if output_file is specified
            if output_file:
                try:
                    output_path = Path(output_file)
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(report)
                    logger.info(f"Report saved to {output_file}")
                except Exception as e:
                    logger.error(f"Failed to save report to {output_file}: {e}")

            return report

        except Exception as e:
            logger.error(f"Error generating tax report: {e}")
            return f"Error generating report: {str(e)}"

    def _determine_report_type(self, tax_data: Dict[str, Any], topic_name: str) -> str:
        """Determine the type of report to generate based on tax data.

        Args:
            tax_data: Tax information data
            topic_name: Name of the tax topic

        Returns:
            Report type
        """
        topic_lower = topic_name.lower()

        # Check for form guide
        if "form" in tax_data or any(keyword in topic_lower for keyword in ["form", "formulaire", "2042", "2044"]):
            return "form_guide"

        # Check for tax scheme
        if "scheme" in tax_data or any(keyword in topic_lower for keyword in ["pinel", "lmnp", "scheme", "dispositif"]):
            return "tax_scheme"

        # Check for tax deadlines (check before calculation guide to avoid "tax" keyword conflict)
        if "deadlines" in tax_data or any(
            keyword in topic_lower for keyword in ["deadline", "echeance", "échéance", "date"]
        ):
            return "tax_deadlines"

        # Check for calculation guide
        if "calculation" in tax_data or any(keyword in topic_lower for keyword in ["calcul", "impot", "tax"]):
            return "calculation_guide"

        # Default to base report
        return "base_report"

    def _generate_markdown_report(
        self,
        tax_data: Dict[str, Any],
        topic_name: str,
        report_type: str,
    ) -> str:
        """Generate a markdown report.

        Args:
            tax_data: Tax information data
            topic_name: Name of the tax topic
            report_type: Type of report to generate

        Returns:
            Markdown report
        """
        # Get current date for retrieval date
        retrieval_date = datetime.now().strftime("%d/%m/%Y")

        # Get source information
        source = tax_data.get("source", "Sources officielles françaises")

        if report_type == "form_guide":
            return self._generate_form_guide(tax_data, topic_name, source, retrieval_date)
        elif report_type == "tax_scheme":
            return self._generate_tax_scheme_report(tax_data, topic_name, source, retrieval_date)
        elif report_type == "calculation_guide":
            return self._generate_calculation_guide(tax_data, topic_name, source, retrieval_date)
        elif report_type == "tax_deadlines":
            return self._generate_tax_deadlines_report(tax_data, topic_name, source, retrieval_date)
        else:
            return self._generate_base_report(tax_data, topic_name, source, retrieval_date)

    def _generate_base_report(
        self,
        tax_data: Dict[str, Any],
        topic_name: str,
        source: str,
        retrieval_date: str,
    ) -> str:
        """Generate a base report.

        Args:
            tax_data: Tax information data
            topic_name: Name of the tax topic
            source: Source of the information
            retrieval_date: Date of retrieval

        Returns:
            Markdown report
        """
        # Extract data
        overview = tax_data.get("description", "Information sur ce sujet fiscal.")

        # Format details section
        details = ""
        for key, value in tax_data.items():
            if key not in ["status", "message", "source", "description", "title"]:
                if isinstance(value, dict):
                    details += f"### {key.replace('_', ' ').title()}\n\n"
                    for sub_key, sub_value in value.items():
                        details += f"- **{sub_key.replace('_', ' ').title()}**: {sub_value}\n"
                    details += "\n"
                elif isinstance(value, list):
                    details += f"### {key.replace('_', ' ').title()}\n\n"
                    for item in value:
                        if isinstance(item, dict):
                            for item_key, item_value in item.items():
                                details += f"- **{item_key.replace('_', ' ').title()}**: {item_value}\n"
                            details += "\n"
                        else:
                            details += f"- {item}\n"
                    details += "\n"
                else:
                    details += f"### {key.replace('_', ' ').title()}\n\n{value}\n\n"

        # Format practical info
        practical_info = tax_data.get("practical_info", "Aucune information pratique disponible.")

        # Format important dates
        important_dates = tax_data.get("important_dates", "Aucune date importante spécifiée.")

        # Format forms
        forms = ""
        if "forms" in tax_data:
            forms = "### Formulaires à utiliser\n\n"
            for form in tax_data["forms"]:
                forms += f"- {form}\n"
        else:
            forms = "Aucun formulaire spécifié."

        # Fill template
        return BASE_REPORT_TEMPLATE.format(
            title=topic_name,
            overview=overview,
            details=details,
            practical_info=practical_info,
            important_dates=important_dates,
            forms=forms,
            source=source,
            retrieval_date=retrieval_date,
        )

    def _generate_tax_scheme_report(
        self,
        tax_data: Dict[str, Any],
        topic_name: str,
        source: str,
        retrieval_date: str,
    ) -> str:
        """Generate a tax scheme report.

        Args:
            tax_data: Tax information data
            topic_name: Name of the tax topic
            source: Source of the information
            retrieval_date: Date of retrieval

        Returns:
            Markdown report
        """
        # Extract scheme name
        scheme_name = tax_data.get("scheme", topic_name)

        # Extract overview
        overview = tax_data.get("description", "Information sur ce dispositif fiscal.")

        # Extract benefits
        benefits = tax_data.get("advantages", "Aucun avantage fiscal spécifié.")

        # Extract eligibility
        eligibility = tax_data.get("eligibility", "Aucune condition d'éligibilité spécifiée.")

        # Extract commitments
        commitments = tax_data.get("commitments", "Aucun engagement spécifié.")

        # Extract calculation
        calculation = tax_data.get("calculation", "Aucune méthode de calcul spécifiée.")

        # Extract declaration
        declaration = tax_data.get("declaration", "Aucune information de déclaration spécifiée.")

        # Extract important dates
        important_dates = tax_data.get("important_dates", "Aucune date importante spécifiée.")

        # Extract forms
        forms = ""
        if "related_forms" in tax_data:
            forms = "### Formulaires à utiliser\n\n"
            for form in tax_data["related_forms"]:
                if isinstance(form, dict):
                    forms += f"- {form.get('number', '')}: {form.get('title', '')}\n"
                else:
                    forms += f"- {form}\n"
        else:
            forms = "Aucun formulaire spécifié."

        # Fill template
        return TAX_SCHEME_TEMPLATE.format(
            scheme_name=scheme_name,
            overview=overview,
            benefits=benefits,
            eligibility=eligibility,
            commitments=commitments,
            calculation=calculation,
            declaration=declaration,
            important_dates=important_dates,
            forms=forms,
            source=source,
            retrieval_date=retrieval_date,
        )

    def _generate_form_guide(
        self,
        tax_data: Dict[str, Any],
        topic_name: str,
        source: str,
        retrieval_date: str,
    ) -> str:
        """Generate a form guide.

        Args:
            tax_data: Tax information data
            topic_name: Name of the tax topic
            source: Source of the information
            retrieval_date: Date of retrieval

        Returns:
            Markdown report
        """
        # Extract form number
        form_number = tax_data.get("form", topic_name)

        # Extract description
        description = tax_data.get("description", "Information sur ce formulaire fiscal.")

        # Extract who should file
        who_should_file = tax_data.get("who_should_file", "Aucune information spécifiée.")

        # Extract main sections
        main_sections = tax_data.get("main_sections", "Aucune section spécifiée.")

        # Extract important boxes
        important_boxes = ""
        if "boxes" in tax_data:
            important_boxes = "### Cases importantes à remplir\n\n"
            for form_name, boxes in tax_data["boxes"].items():
                important_boxes += f"**Formulaire {form_name}:**\n\n"
                for box in boxes:
                    important_boxes += f"- Case {box}\n"
                important_boxes += "\n"
        else:
            important_boxes = "Aucune case importante spécifiée."

        # Extract supporting documents
        supporting_documents = tax_data.get("supporting_documents", "Aucun document justificatif spécifié.")

        # Extract deadline
        deadline = tax_data.get("deadline", "Consultez le calendrier fiscal pour connaître la date limite de dépôt.")

        # Extract related forms
        related_forms = ""
        if "related_forms" in tax_data:
            related_forms = "### Formulaires associés\n\n"
            for form in tax_data["related_forms"]:
                if isinstance(form, dict):
                    related_forms += f"- {form.get('number', '')}: {form.get('title', '')}\n"
                else:
                    related_forms += f"- {form}\n"
        else:
            related_forms = "Aucun formulaire associé spécifié."

        # Fill template
        return FORM_GUIDE_TEMPLATE.format(
            form_number=form_number,
            description=description,
            who_should_file=who_should_file,
            main_sections=main_sections,
            important_boxes=important_boxes,
            supporting_documents=supporting_documents,
            deadline=deadline,
            related_forms=related_forms,
            source=source,
            retrieval_date=retrieval_date,
        )

    def _generate_calculation_guide(
        self,
        tax_data: Dict[str, Any],
        topic_name: str,
        source: str,
        retrieval_date: str,
    ) -> str:
        """Generate a calculation guide.

        Args:
            tax_data: Tax information data
            topic_name: Name of the tax topic
            source: Source of the information
            retrieval_date: Date of retrieval

        Returns:
            Markdown report
        """
        # Extract calculation name
        calculation_name = topic_name

        # Extract description
        description = tax_data.get("description", "Information sur ce calcul fiscal.")

        # Extract formula
        formula = tax_data.get("formula", "Aucune formule spécifiée.")

        # Extract example
        example = tax_data.get("example", "Aucun exemple spécifié.")

        # Extract parameters
        parameters = ""
        if "data" in tax_data and isinstance(tax_data["data"], dict):
            parameters = "### Paramètres utilisés dans le calcul\n\n"
            for key, value in tax_data["data"].items():
                if isinstance(value, dict):
                    parameters += f"**{key.replace('_', ' ').title()}:**\n\n"
                    for sub_key, sub_value in value.items():
                        parameters += f"- {sub_key.replace('_', ' ').title()}: {sub_value}\n"
                    parameters += "\n"
                else:
                    parameters += f"- **{key.replace('_', ' ').title()}**: {value}\n"
        else:
            parameters = "Aucun paramètre spécifié."

        # Extract limits
        limits = tax_data.get("limits", "Aucune limite ou plafond spécifié.")

        # Extract optimization
        optimization = tax_data.get("optimization", "Aucune optimisation fiscale spécifiée.")

        # Fill template
        return CALCULATION_GUIDE_TEMPLATE.format(
            calculation_name=calculation_name,
            description=description,
            formula=formula,
            example=example,
            parameters=parameters,
            limits=limits,
            optimization=optimization,
            source=source,
            retrieval_date=retrieval_date,
        )

    def _generate_tax_deadlines_report(
        self,
        tax_data: Dict[str, Any],
        topic_name: str,
        source: str,
        retrieval_date: str,
    ) -> str:
        """Generate a tax deadlines report.

        Args:
            tax_data: Tax information data
            topic_name: Name of the tax topic
            source: Source of the information
            retrieval_date: Date of retrieval

        Returns:
            Markdown report
        """
        # Extract year
        year = tax_data.get("year", datetime.now().year)

        # Extract deadlines table
        deadlines_table = ""
        if "deadlines" in tax_data and isinstance(tax_data["deadlines"], list):
            deadlines_table = "| Date | Description |\n|------|-------------|\n"
            for deadline in tax_data["deadlines"]:
                if isinstance(deadline, dict):
                    date = deadline.get("date", "")
                    description = deadline.get("description", "")
                    deadlines_table += f"| {date} | {description} |\n"
        else:
            deadlines_table = "Aucune échéance spécifiée."

        # Extract income declaration
        income_declaration = tax_data.get("income_declaration", "Aucune information spécifiée.")

        # Extract tax payment
        tax_payment = tax_data.get("tax_payment", "Aucune information spécifiée.")

        # Extract other deadlines
        other_deadlines = tax_data.get("other_deadlines", "Aucune autre échéance spécifiée.")

        # Fill template
        return TAX_DEADLINES_TEMPLATE.format(
            year=year,
            deadlines_table=deadlines_table,
            income_declaration=income_declaration,
            tax_payment=tax_payment,
            other_deadlines=other_deadlines,
            source=source,
            retrieval_date=retrieval_date,
        )

    def _generate_csv_report(
        self,
        tax_data: Dict[str, Any],
        topic_name: str,
        report_type: str,
    ) -> str:
        """Generate a CSV report.

        Args:
            tax_data: Tax information data
            topic_name: Name of the tax topic
            report_type: Type of report to generate

        Returns:
            CSV report
        """
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(["French Tax Information Report"])
        writer.writerow([f"Topic: {topic_name}"])
        writer.writerow([f"Generated: {datetime.now().strftime('%d/%m/%Y')}"])
        writer.writerow([])

        # Write data based on report type
        if report_type == "form_guide":
            writer.writerow(["Form Information"])
            writer.writerow(["Form Number", tax_data.get("form", topic_name)])
            writer.writerow(["Description", tax_data.get("description", "")])
            writer.writerow([])

            # Write boxes information
            if "boxes" in tax_data:
                writer.writerow(["Important Boxes"])
                for form_name, boxes in tax_data["boxes"].items():
                    writer.writerow([f"Form {form_name}"])
                    for box in boxes:
                        writer.writerow(["", box])
                writer.writerow([])

            # Write related forms
            if "related_forms" in tax_data:
                writer.writerow(["Related Forms"])
                for form in tax_data["related_forms"]:
                    if isinstance(form, dict):
                        writer.writerow([form.get("number", ""), form.get("title", "")])
                    else:
                        writer.writerow([form])

        elif report_type == "tax_scheme":
            writer.writerow(["Tax Scheme Information"])
            writer.writerow(["Scheme Name", tax_data.get("scheme", topic_name)])
            writer.writerow(["Description", tax_data.get("description", "")])
            writer.writerow([])

            # Write benefits
            writer.writerow(["Benefits"])
            writer.writerow([tax_data.get("advantages", "")])
            writer.writerow([])

            # Write eligibility
            writer.writerow(["Eligibility"])
            writer.writerow([tax_data.get("eligibility", "")])
            writer.writerow([])

            # Write declaration
            writer.writerow(["Declaration"])
            writer.writerow([tax_data.get("declaration", "")])

        elif report_type == "calculation_guide":
            writer.writerow(["Tax Calculation Information"])
            writer.writerow(["Calculation Name", topic_name])
            writer.writerow([])

            # Write parameters
            if "data" in tax_data and isinstance(tax_data["data"], dict):
                writer.writerow(["Parameters"])
                for key, value in tax_data["data"].items():
                    if isinstance(value, dict):
                        writer.writerow([key.replace("_", " ").title()])
                        for sub_key, sub_value in value.items():
                            writer.writerow(["", sub_key.replace("_", " ").title(), sub_value])
                    else:
                        writer.writerow([key.replace("_", " ").title(), value])
                writer.writerow([])

        elif report_type == "tax_deadlines":
            writer.writerow(["Tax Deadlines"])
            writer.writerow(["Year", tax_data.get("year", datetime.now().year)])
            writer.writerow([])

            # Write deadlines
            if "deadlines" in tax_data and isinstance(tax_data["deadlines"], list):
                writer.writerow(["Date", "Description"])
                for deadline in tax_data["deadlines"]:
                    if isinstance(deadline, dict):
                        writer.writerow([deadline.get("date", ""), deadline.get("description", "")])
                writer.writerow([])

        else:
            # Generic data export
            for key, value in tax_data.items():
                if key not in ["status", "message", "source"]:
                    if isinstance(value, dict):
                        writer.writerow([key.replace("_", " ").title()])
                        for sub_key, sub_value in value.items():
                            writer.writerow(["", sub_key.replace("_", " ").title(), sub_value])
                        writer.writerow([])
                    elif isinstance(value, list):
                        writer.writerow([key.replace("_", " ").title()])
                        for item in value:
                            if isinstance(item, dict):
                                for item_key, item_value in item.items():
                                    writer.writerow(["", item_key.replace("_", " ").title(), item_value])
                                writer.writerow(["", ""])
                            else:
                                writer.writerow(["", item])
                        writer.writerow([])
                    else:
                        writer.writerow([key.replace("_", " ").title(), value])

        # Get the final CSV content
        csv_content = output.getvalue()
        output.close()

        return csv_content


# Create a singleton instance
report_generator = ReportGenerator()


async def generate_tax_report(
    tax_data: Dict[str, Any],
    topic_name: str,
    output_file: Optional[str] = None,
    format: str = "markdown",
) -> str:
    """Generate a tax information report.

    Args:
        tax_data: Tax information data
        topic_name: Name of the tax topic
        output_file: Optional path to save the report
        format: Output format ('markdown' or 'csv')

    Returns:
        The generated report
    """
    return await report_generator.generate_tax_report(tax_data, topic_name, output_file, format)
