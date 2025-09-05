"""
Autogen utility functions for Flotorch integration.

This module provides utility functions for creating MCP tools, processing LLM messages,
and converting tool schemas for use with the Autogen framework.
"""
from typing import Dict, Any, Sequence, List, cast
from autogen_ext.tools.mcp import SseServerParams, StreamableHttpServerParams, mcp_server_tools
from autogen_core.models import (
    UserMessage,
    SystemMessage,
    FunctionExecutionResultMessage,
    AssistantMessage,
    LLMMessage,
)
from autogen_core.tools import Tool, ToolSchema
from openai.types.chat import ChatCompletionToolParam
from openai.types.shared_params import FunctionDefinition, FunctionParameters
import re

def sanitize_name(name: str) -> str:
    """
    Sanitize agent name to be a valid identifier.
    Replaces invalid characters with underscores and ensures it starts with a letter or underscore.
    """
    
    # Replace invalid characters with underscores
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    
    # Ensure it starts with a letter or underscore
    if sanitized and not sanitized[0].isalpha() and sanitized[0] != '_':
        sanitized = f"agent_{sanitized}"
    
    # Remove consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    
    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')
    
    # Ensure it's not empty
    if not sanitized:
        sanitized = "agent"
    
    return sanitized


async def create_stream_tool(tool_config: Dict[str, Any]) -> List[Any]:
    """
    Creates a streamable HTTP MCP tool from the tool configuration.
    """
    config = tool_config.get("config", {})
    server_params = StreamableHttpServerParams(
        url=config["url"],
        headers=config.get("headers"),
        timeout=config.get("timeout", 30.0),
        sse_read_timeout=config.get("sse_read_timeout", 300.0),
        terminate_on_close=config.get("terminate_on_close", True),
    )
    # We will await this in our thread
    tools = await mcp_server_tools(server_params=server_params)
    tool_name = sanitize_name(tool_config.get("name"))
    for tool in tools:
        if tool.name == tool_name:
            return [tool]
    return []

async def create_sse_tool(tool_config: Dict[str, Any]) -> List[Any]:
    """
    Creates a SSE MCP tool from the tool configuration.
    """
    config = tool_config.get("config", {})
    server_params = SseServerParams(
        url=config["url"],
        headers=config.get("headers"),
        timeout=config.get("timeout", 5.0),
        sse_read_timeout=config.get("sse_read_timeout", 300.0),
    )

    tools = await mcp_server_tools(server_params=server_params)
    tool_name = sanitize_name(tool_config.get("name"))
    for tool in tools:
        if tool.name == tool_name:
            return [tool]
    return []


def process_llmmessage(messages: Sequence[LLMMessage]) -> List[Dict]:
    """
    Processes a list of LLM messages and converts them to a list of dictionaries.
    Merges all SystemMessages into a single system prompt and places it at the top.
    """
    processed_messages = []
    system_message_content = ""

    # First pass: collect system messages and merge them
    for msg in messages:
        if isinstance(msg, SystemMessage):
            system_message_content += msg.content.strip() + "\n\n"

    # If there were any system messages, add the merged one at the top
    if system_message_content.strip():
        processed_messages.append({
            "role": "system",
            "content": system_message_content.strip()
        })

    # Second pass: process other message types
    for msg in messages:
        if isinstance(msg, SystemMessage):
            continue  # already handled

        elif isinstance(msg, UserMessage) and isinstance(msg.content, str):
            processed_messages.append({"role": "user", "content": msg.content})

        elif isinstance(msg, AssistantMessage):
            # Include assistant text responses in history for better coherence
            if isinstance(msg.content, str):
                processed_messages.append({"role": "assistant", "content": msg.content})
            elif isinstance(msg.content, list) and msg.content:  # tool calls
                tool_calls = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.name, "arguments": tc.arguments},
                    }
                    for tc in msg.content
                ]
                processed_messages.append({
                    "role": "assistant",
                    "content": "",
                    "tool_calls": tool_calls
                })

        elif isinstance(msg, FunctionExecutionResultMessage):
            for result in msg.content:
                processed_messages.append({
                    "role": "tool",
                    "tool_call_id": result.call_id,
                    "content": result.content
                })

    return processed_messages



def convert_tools(
    tools: Sequence[Tool | ToolSchema],
) -> List[ChatCompletionToolParam]:
    """
    This function converts a list of tools to a list of ChatCompletionToolParam.
    """
    result: List[ChatCompletionToolParam] = []
    for tool in tools:
        if isinstance(tool, Tool):
            tool_schema = tool.schema
        else:
            assert isinstance(tool, dict)
            tool_schema = tool

        result.append(
            ChatCompletionToolParam(
                type="function",
                function=FunctionDefinition(
                    name=tool_schema["name"],
                    description=(
                        tool_schema["description"]
                        if "description" in tool_schema
                        else ""
                    ),
                    parameters=(
                        cast(FunctionParameters, tool_schema["parameters"])
                        if "parameters" in tool_schema
                        else {}
                    ),
                    strict=(
                        tool_schema["strict"] if "strict" in tool_schema else False
                    ),
                ),
            )
        )
    return result