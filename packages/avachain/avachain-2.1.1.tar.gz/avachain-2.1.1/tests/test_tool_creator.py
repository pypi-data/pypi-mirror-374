"""
Unit tests for tool_creator module.

This module tests the tool creation and conversion utilities.
"""

import json
from typing import Optional
from unittest.mock import MagicMock, Mock, patch

import pytest
from pydantic import BaseModel, Field

from avachain import BaseTool
from avachain.tool_creator import (
    convert_tool_to_json,
    makePluginServerRequest,
    map_type_to_json,
)


class TestToolArgs(BaseModel):
    """Test tool arguments schema."""

    query: str = Field(description="Search query")
    limit: int = Field(default=10, description="Maximum results")
    category: str = Field(default="general", description="Search category")


class TestTool(BaseTool):
    """Test tool for conversion testing."""

    name: str = "test_search_tool"
    description: str = "A tool for searching information"
    args_schema: Optional[type] = TestToolArgs

    def _run(self, query: str, limit: int = 10, category: str = "general") -> str:
        """Execute the test tool."""
        return f"Search results for '{query}' (limit: {limit}, category: {category})"


class TestMapTypeToJson:
    """Test cases for map_type_to_json function."""

    def test_basic_types(self):
        """Test mapping of basic Python types."""
        assert map_type_to_json(int) == "number"
        assert map_type_to_json(float) == "number"
        assert map_type_to_json(str) == "string"
        assert map_type_to_json(bool) == "boolean"

    def test_unknown_types(self):
        """Test mapping of unknown types."""
        assert map_type_to_json(list) == "<class 'list'>"
        assert map_type_to_json(dict) == "<class 'dict'>"
        assert map_type_to_json(tuple) == "<class 'tuple'>"


class TestConvertToolToJson:
    """Test cases for convert_tool_to_json function."""

    @patch("avachain.tool_creator.inspect.getsource")
    @patch("avachain.tool_creator.print")
    def test_convert_tool_basic(self, mock_print, mock_getsource):
        """Test basic tool conversion to JSON."""
        mock_getsource.return_value = "def _run(self): return 'test'"

        tool = TestTool()
        result = convert_tool_to_json(
            tool=tool,
            tool_id="test_tool_v1",
            human_description="A test tool for searching",
            public_name="Test Search Tool",
            tags=["productivity"],
        )

        # Check basic structure
        assert result["title"] == "test_tool_v1"
        assert result["name"] == "Test Search Tool"
        assert result["human_description"] == "A test tool for searching"
        assert result["ai_description"] == "A tool for searching information"

        # Check OS support
        assert len(result["os"]) == 1

        # Check parameters structure
        assert "parameters" in result
        assert "tool_extras" in result["parameters"]
        assert "tool_parameters" in result["parameters"]

        # Check tool extras
        extras = result["parameters"]["tool_extras"]
        assert extras["name"] == "test_search_tool"
        assert extras["isDirect"] is False

    @patch("avachain.tool_creator.inspect.getsource")
    def test_convert_tool_with_parameters(self, mock_getsource):
        """Test tool conversion with parameters."""
        mock_getsource.return_value = "def _run(self, query, limit=10): pass"

        tool = TestTool()
        result = convert_tool_to_json(
            tool=tool,
            tool_id="test_tool",
            human_description="Test tool",
            public_name="Test Tool",
            tags=["productivity"],
        )

        # Check that parameters were extracted
        tool_params = result["parameters"]["tool_parameters"]
        assert "query" in tool_params
        assert "limit" in tool_params
        assert "category" in tool_params

        # Check parameter types
        assert tool_params["query"]["type"] == "string"
        assert tool_params["limit"]["type"] == "number"
        assert tool_params["category"]["type"] == "string"

        # Check descriptions
        assert tool_params["query"]["description"] == "Search query"
        assert tool_params["limit"]["description"] == "Maximum results"
        assert tool_params["category"]["description"] == "Search category"

        # Check default values
        assert tool_params["limit"]["default"] == 10
        assert tool_params["category"]["default"] == "general"

    @patch("avachain.tool_creator.inspect.getsource")
    def test_convert_tool_os_support_validation(self, mock_getsource):
        """Test OS support validation."""
        mock_getsource.return_value = "def _run(self): pass"

        tool = TestTool()

        # Should raise error when no OS is supported
        with pytest.raises(ValueError, match="at least one of 'android', 'windows'"):
            convert_tool_to_json(
                tool=tool,
                tool_id="test",
                human_description="Test",
                public_name="Test",
                tags=["productivity"],
                supports_android=False,
                supports_windows=False,
            )

    @patch("avachain.tool_creator.inspect.getsource")
    def test_convert_tool_android_support(self, mock_getsource):
        """Test tool conversion with Android support."""
        mock_getsource.return_value = "def _run(self): pass"

        tool = TestTool()
        result = convert_tool_to_json(
            tool=tool,
            tool_id="test",
            human_description="Test",
            public_name="Test",
            tags=["productivity"],
            supports_android=True,
            supports_windows=False,
        )

        assert result["os"] == ["android"]

    @patch("avachain.tool_creator.inspect.getsource")
    def test_convert_tool_windows_support(self, mock_getsource):
        """Test tool conversion with Windows support."""
        mock_getsource.return_value = "def _run(self): pass"

        tool = TestTool()
        result = convert_tool_to_json(
            tool=tool,
            tool_id="test",
            human_description="Test",
            public_name="Test",
            tags=["productivity"],
            supports_android=False,
            supports_windows=True,
        )

        # Should contain the current OS name
        import os

        assert os.name in result["os"]

    @patch("avachain.tool_creator.inspect.getsource")
    def test_convert_tool_all_options(self, mock_getsource):
        """Test tool conversion with all optional parameters."""
        mock_getsource.return_value = "def _run(self): pass"

        tool = TestTool()
        tool.return_direct = True  # Set return_direct for testing

        result = convert_tool_to_json(
            tool=tool,
            tool_id="advanced_tool",
            human_description="Advanced test tool",
            public_name="Advanced Tool",
            logo_url="https://example.com/logo.png",  # Changed from logo to logo_url
            isAnonymous=True,
            authentication_required=True,
            connection_url="https://api.example.com",
            isAuthenticated=True,
            isPublic=False,
            isMain=True,
            tags=["productivity", "utility"],
            supports_android=True,
            supports_windows=True,
        )

        # Check all options
        assert result["logo"] == "https://example.com/logo.png"
        assert result["isAnonymous"] is True
        assert result["authentication_required"] is True
        assert result["connection_url"] == "https://api.example.com"
        assert result["isAuthenticated"] is True
        assert result["isPublic"] is False
        assert result["tags"] == ["productivity", "utility"]
        assert result["parameters"]["tool_extras"]["isMain"] is True
        assert result["parameters"]["tool_extras"]["isDirect"] is True


class TestMakePluginServerRequest:
    """Test cases for makePluginServerRequest function."""

    @patch("avachain.tool_creator._create_or_update_tool_plugin")
    @patch("avachain.tool_creator.print")
    def test_create_request(self, mock_print, mock_create_update):
        """Test making a create request to plugin server."""
        mock_create_update.return_value = {"status": "success"}

        tool = TestTool()
        token = "test_token_123"

        result = makePluginServerRequest(
            action="create",
            token=token,
            tool_id="test_tool",
            tool=tool,
            human_description="Test tool description",
            public_name="Test Tool",
            tags=["productivity"],
        )

        # Check that create_or_update was called correctly
        mock_create_update.assert_called_once_with(
            action="create",
            token=token,
            tool=tool,
            tool_id="test_tool",
            human_description="Test tool description",
            public_name="Test Tool",
            logo=None,
            isAnonymous=False,
            authentication_required=False,
            connection_url="",
            isAuthenticated=False,
            isPublic=True,
            isMain=False,
            tags=["productivity"],
            supports_android=False,
            supports_windows=True,
        )

        assert result == {"status": "success"}

    @patch("avachain.tool_creator._create_or_update_tool_plugin")
    @patch("avachain.tool_creator.print")
    def test_update_request(self, mock_print, mock_create_update):
        """Test making an update request to plugin server."""
        mock_create_update.return_value = {"status": "updated"}

        tool = TestTool()
        token = "test_token_123"

        result = makePluginServerRequest(
            action="update",
            token=token,
            tool_id="test_tool",
            tool=tool,
            human_description="Updated test tool description",
            public_name="Updated Test Tool",
            tags=["productivity"],
        )

        # Check that create_or_update was called correctly
        mock_create_update.assert_called_once_with(
            action="update",
            token=token,
            tool=tool,
            tool_id="test_tool",
            human_description="Updated test tool description",
            public_name="Updated Test Tool",
            logo=None,
            isAnonymous=False,
            authentication_required=False,
            connection_url="",
            isAuthenticated=False,
            isPublic=True,
            isMain=False,
            tags=["productivity"],
            supports_android=False,
            supports_windows=True,
        )

        assert result == {"status": "updated"}

    @patch("avachain.tool_creator._delete_tool_plugin")
    @patch("avachain.tool_creator.print")
    def test_delete_request(self, mock_print, mock_delete):
        """Test making a delete request to plugin server."""
        mock_delete.return_value = {"status": "deleted"}

        token = "test_token_123"

        result = makePluginServerRequest(
            action="delete", token=token, tool_id="test_plugin"
        )

        # Check that delete was called correctly
        mock_delete.assert_called_once_with("test_plugin", token)

        assert result == {"status": "deleted"}

    def test_unknown_action(self):
        """Test making request with unknown action (requires tool object)."""
        tool = TestTool()
        token = "test_token_123"

        # Unknown action should still require tool object for create/update validation
        with patch(
            "avachain.tool_creator._create_or_update_tool_plugin"
        ) as mock_create_update:
            mock_create_update.return_value = {"status": "success"}

            result = makePluginServerRequest(
                action="unknown_action",
                token=token,
                tool_id="test_tool",
                tool=tool,
                human_description="Test description",
                public_name="Test Tool",
                tags=["productivity"],
            )

            # Should call create_or_update (defaults to create-like behavior)
            mock_create_update.assert_called_once()
            assert result == {"status": "success"}


class TestTagValidation:
    """Test cases for tag validation functionality."""

    @patch("avachain.tool_creator.inspect.getsource")
    def test_valid_tags_accepted(self, mock_getsource):
        """Test that valid tags are accepted."""
        mock_getsource.return_value = "def _run(self): pass"

        tool = TestTool()

        # Test each allowed tag
        for tag in ["entertainment", "media", "productivity", "device", "settings"]:
            result = convert_tool_to_json(
                tool=tool,
                tool_id="test",
                human_description="Test",
                public_name="Test",
                tags=[tag],
            )
            assert result["tags"] == [tag]

    @patch("avachain.tool_creator.inspect.getsource")
    def test_mixed_case_tags_accepted(self, mock_getsource):
        """Test that mixed case tags are accepted."""
        mock_getsource.return_value = "def _run(self): pass"

        tool = TestTool()
        result = convert_tool_to_json(
            tool=tool,
            tool_id="test",
            human_description="Test",
            public_name="Test",
            tags=["PRODUCTIVITY", "custom_tag"],
        )
        assert result["tags"] == ["PRODUCTIVITY", "custom_tag"]

    def test_empty_tags_rejected(self):
        """Test that empty tags are rejected."""
        tool = TestTool()

        with pytest.raises(ValueError, match="At least one tag is required"):
            convert_tool_to_json(
                tool=tool,
                tool_id="test",
                human_description="Test",
                public_name="Test",
                tags=[],
            )

    def test_none_tags_rejected(self):
        """Test that None tags are rejected."""
        tool = TestTool()

        with pytest.raises(ValueError, match="At least one tag is required"):
            convert_tool_to_json(
                tool=tool,
                tool_id="test",
                human_description="Test",
                public_name="Test",
                tags=None,
            )

    def test_invalid_tags_only_rejected(self):
        """Test that tags with no allowed categories are rejected."""
        tool = TestTool()

        with pytest.raises(
            ValueError, match="At least one tag must be from the allowed categories"
        ):
            convert_tool_to_json(
                tool=tool,
                tool_id="test",
                human_description="Test",
                public_name="Test",
                tags=["invalid", "wrong", "notallowed"],
            )

    def test_non_list_tags_rejected(self):
        """Test that non-list tags are rejected."""
        tool = TestTool()

        with pytest.raises(ValueError, match="Tags must be provided as a list"):
            convert_tool_to_json(
                tool=tool,
                tool_id="test",
                human_description="Test",
                public_name="Test",
                tags="productivity",
            )

    @patch("avachain.tool_creator.inspect.getsource")
    def test_mixed_valid_invalid_tags_accepted(self, mock_getsource):
        """Test that a mix of valid and invalid tags is accepted if at least one is valid."""
        mock_getsource.return_value = "def _run(self): pass"

        tool = TestTool()
        result = convert_tool_to_json(
            tool=tool,
            tool_id="test",
            human_description="Test",
            public_name="Test",
            tags=["productivity", "custom_tag", "another_custom"],
        )
        assert result["tags"] == ["productivity", "custom_tag", "another_custom"]

    def test_makePluginServerRequest_tag_validation(self):
        """Test that makePluginServerRequest validates tags."""
        tool = TestTool()

        with pytest.raises(ValueError, match="At least one tag is required"):
            makePluginServerRequest(
                action="create",
                token="test_token",
                tool_id="test",
                tool=tool,
                human_description="Test",
                public_name="Test",
                tags=None,
            )
