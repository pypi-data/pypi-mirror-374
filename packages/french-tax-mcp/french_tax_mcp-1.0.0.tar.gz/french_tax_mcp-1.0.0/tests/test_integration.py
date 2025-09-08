#!/usr/bin/env python3
"""Integration tests for the French Tax MCP Server."""

from unittest.mock import AsyncMock, patch

import pytest

from french_tax_mcp.analyzers.business_analyzer import calculate_micro_enterprise_tax
from french_tax_mcp.analyzers.income_analyzer import calculate_income_tax
from french_tax_mcp.analyzers.property_analyzer import (
    calculate_lmnp_benefit,
    calculate_pinel_benefit,
)
from french_tax_mcp.constants import TAX_BRACKETS


class TestIntegration:
    """Integration tests for the French Tax MCP Server."""

    @pytest.mark.asyncio
    async def test_income_tax_calculation_integration(self):
        """Test income tax calculation with real data."""
        # Test with a typical salary
        result = await calculate_income_tax(50000, 2.0, 2024)

        assert result["status"] == "success"
        assert "data" in result
        assert result["data"]["net_taxable_income"] == 50000
        assert result["data"]["household_parts"] == 2.0
        assert result["data"]["total_tax"] > 0
        assert result["data"]["average_tax_rate"] >= 0
        assert result["data"]["marginal_tax_rate"] > 0

    @pytest.mark.asyncio
    async def test_pinel_calculation_integration(self):
        """Test Pinel calculation with real data."""
        result = await calculate_pinel_benefit(250000, 9, "2024-01-01")

        assert result["status"] == "success"
        assert "data" in result
        assert result["data"]["property_price"] == 250000
        assert result["data"]["commitment_period"] == 9
        assert result["data"]["total_reduction"] > 0
        assert result["data"]["annual_reduction"] > 0

    @pytest.mark.asyncio
    async def test_lmnp_calculation_integration(self):
        """Test LMNP calculation with real data."""
        result = await calculate_lmnp_benefit(24000, 0, 0, 0, "micro")

        assert result["status"] == "success"
        assert "data" in result
        assert result["data"]["annual_rent"] == 24000
        assert result["data"]["regime"] == "micro"
        assert result["data"]["taxable_income"] == 12000  # 50% abatement

    @pytest.mark.asyncio
    async def test_micro_enterprise_calculation_integration(self):
        """Test micro-enterprise calculation with real data."""
        result = await calculate_micro_enterprise_tax(40000, "services", False, 2024)

        assert result["status"] == "success"
        assert "data" in result
        assert result["data"]["annual_revenue"] == 40000
        assert result["data"]["activity_type"] == "services"
        assert result["data"]["taxable_income"] == 20000  # 50% abatement
        assert result["data"]["total_tax"] > 0

    def test_tax_brackets_constants(self):
        """Test that tax brackets constants are properly defined."""
        assert 2024 in TAX_BRACKETS
        brackets_2024 = TAX_BRACKETS[2024]

        # Check structure
        assert len(brackets_2024) == 5
        assert brackets_2024[0]["rate"] == 0  # First bracket is 0%
        assert brackets_2024[-1]["rate"] == 45  # Last bracket is 45%

        # Check progression
        for i in range(len(brackets_2024) - 1):
            assert brackets_2024[i]["rate"] < brackets_2024[i + 1]["rate"]

    @pytest.mark.asyncio
    async def test_error_handling_integration(self):
        """Test error handling in calculations."""
        # Test with invalid commitment period for Pinel
        result = await calculate_pinel_benefit(250000, 5, "2024-01-01")
        assert result["status"] == "error"

        # Test with invalid activity type for micro-enterprise
        result = await calculate_micro_enterprise_tax(40000, "invalid", False, 2024)
        assert result["status"] == "error"

        # Test with invalid regime for LMNP
        result = await calculate_lmnp_benefit(24000, 0, 0, 0, "invalid")
        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_edge_cases_integration(self):
        """Test edge cases in calculations."""
        # Test with zero income
        result = await calculate_income_tax(0, 1.0, 2024)
        assert result["status"] == "success"
        assert result["data"]["total_tax"] == 0

        # Test with maximum Pinel investment
        result = await calculate_pinel_benefit(300000, 12, "2024-01-01")
        assert result["status"] == "success"
        assert result["data"]["eligible_amount"] == 300000

        # Test with investment above maximum
        result = await calculate_pinel_benefit(400000, 12, "2024-01-01")
        assert result["status"] == "success"
        assert result["data"]["eligible_amount"] == 300000  # Capped at maximum


if __name__ == "__main__":
    pytest.main([__file__])
