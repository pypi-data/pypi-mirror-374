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

"""Test fixtures for the French tax MCP server."""

import os
from pathlib import Path

import pytest


@pytest.fixture
def mock_data_dir() -> Path:
    """Get the path to the mock data directory.

    Returns:
        Path to the mock data directory
    """
    return Path(__file__).parent / "mock_data"


@pytest.fixture
def mock_html_response(mock_data_dir: Path) -> str:
    """Get a mock HTML response.

    Args:
        mock_data_dir: Path to the mock data directory

    Returns:
        Mock HTML response
    """
    with open(mock_data_dir / "mock_response.html", "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def mock_tax_brackets_response(mock_data_dir: Path) -> str:
    """Get a mock tax brackets response.

    Args:
        mock_data_dir: Path to the mock data directory

    Returns:
        Mock tax brackets response
    """
    with open(mock_data_dir / "tax_brackets.html", "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def mock_form_response(mock_data_dir: Path) -> str:
    """Get a mock form response.

    Args:
        mock_data_dir: Path to the mock data directory

    Returns:
        Mock form response
    """
    with open(mock_data_dir / "form_2042.html", "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def mock_scheme_response(mock_data_dir: Path) -> str:
    """Get a mock scheme response.

    Args:
        mock_data_dir: Path to the mock data directory

    Returns:
        Mock scheme response
    """
    with open(mock_data_dir / "pinel_scheme.html", "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def mock_deadlines_response(mock_data_dir: Path) -> str:
    """Get a mock deadlines response.

    Args:
        mock_data_dir: Path to the mock data directory

    Returns:
        Mock deadlines response
    """
    with open(mock_data_dir / "tax_deadlines.html", "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def mock_article_response(mock_data_dir: Path) -> str:
    """Get a mock article response.

    Args:
        mock_data_dir: Path to the mock data directory

    Returns:
        Mock article response
    """
    with open(mock_data_dir / "tax_article.html", "r", encoding="utf-8") as f:
        return f.read()
