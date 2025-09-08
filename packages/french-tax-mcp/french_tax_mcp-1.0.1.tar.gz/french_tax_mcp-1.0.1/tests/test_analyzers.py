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

"""Tests for the analyzers."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from french_tax_mcp.analyzers.business_analyzer import BusinessTaxAnalyzer
from french_tax_mcp.analyzers.income_analyzer import IncomeTaxAnalyzer
from french_tax_mcp.analyzers.property_analyzer import PropertyTaxAnalyzer


class TestIncomeTaxAnalyzer:
    """Tests for the IncomeTaxAnalyzer class."""

    @pytest.mark.asyncio
    async def test_calculate_income_tax(self):
        """Test the calculate_income_tax method."""
        analyzer = IncomeTaxAnalyzer()

        # Mock the get_tax_brackets function
        with patch(
            "french_tax_mcp.analyzers.income_analyzer.get_tax_brackets", new_callable=AsyncMock
        ) as mock_get_tax_brackets:
            # Set up the mock to return a valid response
            mock_get_tax_brackets.return_value = {
                "status": "success",
                "data": {
                    "brackets": [
                        {"min": 0, "max": 10000, "rate": 0},
                        {"min": 10001, "max": 30000, "rate": 11},
                        {"min": 30001, "max": 80000, "rate": 30},
                        {"min": 80001, "max": 170000, "rate": 41},
                        {"min": 170001, "max": None, "rate": 45},
                    ]
                },
            }

            result = await analyzer.calculate_income_tax(50000, 1.0, 2023)

            # Verify get_tax_brackets was called with the correct year
            mock_get_tax_brackets.assert_called_once_with(2023)

            # Verify result structure and content
            assert result["status"] == "success"
            assert "data" in result
            assert "year" in result["data"]
            assert result["data"]["year"] == 2023
            assert "net_taxable_income" in result["data"]
            assert result["data"]["net_taxable_income"] == 50000
            assert "household_parts" in result["data"]
            assert result["data"]["household_parts"] == 1.0
            assert "total_tax" in result["data"]
            assert "average_tax_rate" in result["data"]
            assert "marginal_tax_rate" in result["data"]
            assert "bracket_details" in result["data"]

    @pytest.mark.asyncio
    async def test_calculate_household_parts(self):
        """Test the calculate_household_parts method."""
        # Create a mock analyzer
        analyzer = IncomeTaxAnalyzer()

        # Call calculate_household_parts
        result = await analyzer.calculate_household_parts("married", 2, 1)

        # Check that the result was formatted correctly
        assert result["status"] == "success"
        assert "data" in result
        assert "marital_status" in result["data"]
        assert result["data"]["marital_status"] == "married"
        assert "num_children" in result["data"]
        assert result["data"]["num_children"] == 2
        assert "disabled_dependents" in result["data"]
        assert result["data"]["disabled_dependents"] == 1
        assert "total_parts" in result["data"]
        # French tax calculation: 2 parts (married couple) + 1 part (2 children) + 0.5 part (disabled dependent)
        assert result["data"]["total_parts"] == 3.5


class TestPropertyTaxAnalyzer:
    """Tests for the PropertyTaxAnalyzer class."""

    @pytest.mark.asyncio
    async def test_calculate_pinel_benefit(self):
        """Test the calculate_pinel_benefit method."""
        # Create a mock analyzer
        analyzer = PropertyTaxAnalyzer()

        # Call calculate_pinel_benefit
        result = await analyzer.calculate_pinel_benefit(200000, 9, "2023-01-01")

        # Check that the result was formatted correctly
        assert result["status"] == "success"
        assert "data" in result
        assert "property_price" in result["data"]
        assert result["data"]["property_price"] == 200000
        assert "commitment_period" in result["data"]
        assert result["data"]["commitment_period"] == 9
        assert "acquisition_date" in result["data"]
        assert result["data"]["acquisition_date"] == "2023-01-01"
        assert "rate" in result["data"]
        assert "eligible_amount" in result["data"]
        assert "total_reduction" in result["data"]
        assert "annual_reduction" in result["data"]
        assert "reduction_schedule" in result["data"]

    @pytest.mark.asyncio
    async def test_calculate_lmnp_benefit(self):
        """Test the calculate_lmnp_benefit method."""
        # Create a mock analyzer
        analyzer = PropertyTaxAnalyzer()

        # Call calculate_lmnp_benefit
        result = await analyzer.calculate_lmnp_benefit(12000, 3000, 150000, 10000, "micro")

        # Check that the result was formatted correctly
        assert result["status"] == "success"
        assert "data" in result
        assert "annual_rent" in result["data"]
        assert result["data"]["annual_rent"] == 12000
        assert "regime" in result["data"]
        assert result["data"]["regime"] == "micro"
        assert "taxable_income" in result["data"]
        assert "deduction_details" in result["data"]
        assert "total_deduction" in result["data"]
        assert "declaration_info" in result["data"]


class TestBusinessTaxAnalyzer:
    """Tests for the BusinessTaxAnalyzer class."""

    @pytest.mark.asyncio
    async def test_calculate_micro_enterprise_tax(self):
        """Test the calculate_micro_enterprise_tax method."""
        # Create a mock analyzer
        analyzer = BusinessTaxAnalyzer()

        # Call calculate_micro_enterprise_tax
        result = await analyzer.calculate_micro_enterprise_tax(50000, "services", False, 2023)

        # Check that the result was formatted correctly
        assert result["status"] == "success"
        assert "data" in result
        assert "year" in result["data"]
        assert result["data"]["year"] == 2023
        assert "annual_revenue" in result["data"]
        assert result["data"]["annual_revenue"] == 50000
        assert "activity_type" in result["data"]
        assert result["data"]["activity_type"] == "services"
        assert "accre_eligible" in result["data"]
        assert result["data"]["accre_eligible"] is False
        assert "abatement_rate" in result["data"]
        assert "taxable_income" in result["data"]
        assert "social_charges" in result["data"]
        assert "income_tax" in result["data"]
        assert "total_tax" in result["data"]
        assert "net_income" in result["data"]
        assert "declaration_info" in result["data"]

    @pytest.mark.asyncio
    async def test_calculate_auto_entrepreneur_tax(self):
        """Test the calculate_auto_entrepreneur_tax method."""
        # Create a mock analyzer
        analyzer = BusinessTaxAnalyzer()

        # Call calculate_auto_entrepreneur_tax
        result = await analyzer.calculate_auto_entrepreneur_tax(
            50000, "services", True, False, 2023
        )

        # Check that the result was formatted correctly
        assert result["status"] == "success"
        assert "data" in result
        assert "year" in result["data"]
        assert result["data"]["year"] == 2023
        assert "annual_revenue" in result["data"]
        assert result["data"]["annual_revenue"] == 50000
        assert "activity_type" in result["data"]
        assert result["data"]["activity_type"] == "services"
        assert "versement_liberatoire" in result["data"]
        assert result["data"]["versement_liberatoire"] is True
        assert "accre_eligible" in result["data"]
        assert result["data"]["accre_eligible"] is False
        assert "social_charges" in result["data"]
        assert "income_tax" in result["data"]
        assert "total_tax" in result["data"]
        assert "net_income" in result["data"]
        assert "declaration_info" in result["data"]
