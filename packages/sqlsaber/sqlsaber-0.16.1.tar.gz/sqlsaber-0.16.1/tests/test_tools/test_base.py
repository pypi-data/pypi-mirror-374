"""Tests for the base tool class."""

import pytest

from sqlsaber.tools.base import Tool
from sqlsaber.tools.enums import ToolCategory, WorkflowPosition


class MockTool(Tool):
    """Mock tool for testing."""

    @property
    def name(self) -> str:
        return "mock_tool"

    @property
    def description(self) -> str:
        return "A mock tool for testing"

    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "message": {"type": "string"},
            },
            "required": ["message"],
        }

    async def execute(self, **kwargs) -> str:
        message = kwargs.get("message", "")
        return f'{{"result": "{message}"}}'


class TestBaseTool:
    """Test the base Tool class."""

    def test_tool_properties(self):
        """Test tool properties."""
        tool = MockTool()
        assert tool.name == "mock_tool"
        assert tool.description == "A mock tool for testing"
        assert tool.category == ToolCategory.GENERAL
        assert tool.get_workflow_position() == WorkflowPosition.OTHER
        assert "message" in tool.input_schema["properties"]

    def test_to_definition(self):
        """Test converting tool to ToolDefinition."""
        tool = MockTool()
        definition = tool.to_definition()

        assert definition.name == "mock_tool"
        assert definition.description == "A mock tool for testing"
        assert definition.input_schema == tool.input_schema

    @pytest.mark.asyncio
    async def test_execute(self):
        """Test tool execution."""
        tool = MockTool()
        result = await tool.execute(message="Hello, World!")
        assert result == '{"result": "Hello, World!"}'
