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

"""Tests for the report generator."""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from french_tax_mcp.report_generator import ReportGenerator


class TestReportGenerator:
    """Tests for the ReportGenerator class."""

    @pytest.mark.asyncio
    async def test_generate_tax_report_markdown(self):
        """Test the generate_tax_report method with markdown format."""
        generator = ReportGenerator()

        # Mock the _determine_report_type method
        generator._determine_report_type = MagicMock(return_value="base_report")

        # Mock the _generate_markdown_report method
        generator._generate_markdown_report = MagicMock(return_value="# Test Report")

        # Call generate_tax_report
        result = await generator.generate_tax_report(
            {"test": "data"}, "Test Topic", None, "markdown"
        )

        # Check that _determine_report_type was called with the correct arguments
        generator._determine_report_type.assert_called_once_with({"test": "data"}, "Test Topic")

        # Check that _generate_markdown_report was called with the correct arguments
        generator._generate_markdown_report.assert_called_once_with(
            {"test": "data"}, "Test Topic", "base_report"
        )

        # Check that the result is correct
        assert result == "# Test Report"

    @pytest.mark.asyncio
    async def test_generate_tax_report_csv(self):
        """Test the generate_tax_report method with CSV format."""
        # Create a mock generator
        generator = ReportGenerator()

        # Mock the _determine_report_type method
        generator._determine_report_type = MagicMock(return_value="base_report")

        # Mock the _generate_csv_report method
        generator._generate_csv_report = MagicMock(return_value="Test,Report")

        # Call generate_tax_report
        result = await generator.generate_tax_report({"test": "data"}, "Test Topic", None, "csv")

        # Check that _determine_report_type was called with the correct arguments
        generator._determine_report_type.assert_called_once_with({"test": "data"}, "Test Topic")

        # Check that _generate_csv_report was called with the correct arguments
        generator._generate_csv_report.assert_called_once_with(
            {"test": "data"}, "Test Topic", "base_report"
        )

        # Check that the result is correct
        assert result == "Test,Report"

    @pytest.mark.asyncio
    async def test_generate_tax_report_with_output_file(self, tmp_path):
        """Test the generate_tax_report method with an output file."""
        # Create a mock generator
        generator = ReportGenerator()

        # Mock the _determine_report_type method
        generator._determine_report_type = MagicMock(return_value="base_report")

        # Mock the _generate_markdown_report method
        generator._generate_markdown_report = MagicMock(return_value="# Test Report")

        # Create a temporary file path
        output_file = tmp_path / "test_report.md"

        # Call generate_tax_report
        result = await generator.generate_tax_report(
            {"test": "data"}, "Test Topic", str(output_file), "markdown"
        )

        # Check that _determine_report_type was called with the correct arguments
        generator._determine_report_type.assert_called_once_with({"test": "data"}, "Test Topic")

        # Check that _generate_markdown_report was called with the correct arguments
        generator._generate_markdown_report.assert_called_once_with(
            {"test": "data"}, "Test Topic", "base_report"
        )

        # Check that the result is correct
        assert result == "# Test Report"

        # Check that the file was created
        assert output_file.exists()

        # Check that the file contains the correct content
        with open(output_file, "r") as f:
            assert f.read() == "# Test Report"

    def test_determine_report_type(self):
        """Test the _determine_report_type method."""
        # Create a generator
        generator = ReportGenerator()

        # Test form guide detection
        assert generator._determine_report_type({"form": "2042"}, "Form 2042") == "form_guide"
        assert generator._determine_report_type({}, "formulaire 2042") == "form_guide"

        # Test tax scheme detection
        assert generator._determine_report_type({"scheme": "pinel"}, "Pinel Scheme") == "tax_scheme"
        assert generator._determine_report_type({}, "dispositif pinel") == "tax_scheme"

        # Test calculation guide detection
        assert (
            generator._determine_report_type(
                {"calculation": "income_tax"}, "Income Tax Calculation"
            )
            == "calculation_guide"
        )
        assert generator._determine_report_type({}, "calcul impot") == "calculation_guide"

        # Test tax deadlines detection
        assert (
            generator._determine_report_type({"deadlines": []}, "Tax Deadlines") == "tax_deadlines"
        )
        assert generator._determine_report_type({}, "échéances fiscales") == "tax_deadlines"

        # Test default
        assert generator._determine_report_type({}, "Unknown Topic") == "base_report"

    def test_generate_base_report(self):
        """Test the _generate_base_report method."""
        # Create a generator
        generator = ReportGenerator()

        # Call _generate_base_report
        result = generator._generate_base_report(
            {
                "description": "Test description",
                "key1": "value1",
                "key2": {"subkey1": "subvalue1"},
                "key3": ["item1", "item2"],
                "forms": ["2042", "2044"],
            },
            "Test Topic",
            "https://example.com",
            "01/01/2023",
        )

        # Check that the result contains the expected sections
        assert "# Rapport Fiscal : Test Topic" in result
        assert "Test description" in result
        assert "key1" in result
        assert "value1" in result
        assert "Key2" in result
        assert "Subkey1" in result
        assert "subvalue1" in result
        assert "Key3" in result
        assert "item1" in result
        assert "item2" in result
        assert "2042" in result
        assert "2044" in result
        assert "https://example.com" in result
        assert "01/01/2023" in result

    def test_generate_tax_scheme_report(self):
        """Test the _generate_tax_scheme_report method."""
        # Create a generator
        generator = ReportGenerator()

        # Call _generate_tax_scheme_report
        result = generator._generate_tax_scheme_report(
            {
                "scheme": "pinel",
                "description": "Test description",
                "advantages": "Test advantages",
                "eligibility": "Test eligibility",
                "commitments": "Test commitments",
                "calculation": "Test calculation",
                "declaration": "Test declaration",
                "important_dates": "Test dates",
                "related_forms": [{"number": "2042", "title": "Form 2042"}],
            },
            "Pinel",
            "https://example.com",
            "01/01/2023",
        )

        # Check that the result contains the expected sections
        assert "# Dispositif Fiscal : pinel" in result
        assert "Test description" in result
        assert "Test advantages" in result
        assert "Test eligibility" in result
        assert "Test commitments" in result
        assert "Test calculation" in result
        assert "Test declaration" in result
        assert "Test dates" in result
        assert "2042" in result
        assert "Form 2042" in result
        assert "https://example.com" in result
        assert "01/01/2023" in result

    def test_generate_form_guide(self):
        """Test the _generate_form_guide method."""
        # Create a generator
        generator = ReportGenerator()

        # Call _generate_form_guide
        result = generator._generate_form_guide(
            {
                "form": "2042",
                "description": "Test description",
                "who_should_file": "Test who should file",
                "main_sections": "Test main sections",
                "boxes": {"2042": ["1AJ", "1BJ"]},
                "supporting_documents": "Test supporting documents",
                "deadline": "Test deadline",
                "related_forms": [{"number": "2044", "title": "Form 2044"}],
            },
            "Form 2042",
            "https://example.com",
            "01/01/2023",
        )

        # Check that the result contains the expected sections
        assert "# Guide du Formulaire : 2042" in result
        assert "Test description" in result
        assert "Test who should file" in result
        assert "Test main sections" in result
        assert "Formulaire 2042" in result
        assert "1AJ" in result
        assert "1BJ" in result
        assert "Test supporting documents" in result
        assert "Test deadline" in result
        assert "2044" in result
        assert "Form 2044" in result
        assert "https://example.com" in result
        assert "01/01/2023" in result
