"""
OpenFiles Tools - Framework-agnostic AI tool definitions

Provides provider-specific tool definitions and automatic execution
for file operations. Only handles OpenFiles tools, ignoring others.
"""

import json
from typing import Any, Dict, List, Optional

from ..core import OpenFilesClient
from ..utils.logger import Logger

logger = Logger()


class ToolDefinition:
    """OpenAI-compatible tool definition"""

    def __init__(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        strict: bool = True,
    ):
        self.type = "function"
        self.function = {
            "name": name,
            "description": description,
            "strict": strict,
            "parameters": parameters,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for OpenAI API"""
        return {"type": self.type, "function": self.function}


class ToolResult:
    """Result of tool execution"""

    def __init__(
        self,
        tool_call_id: str,
        function: str,
        status: str = "success",
        data: Any = None,
        error: Optional[str] = None,
        args: Optional[Dict[str, Any]] = None,
    ):
        self.tool_call_id = tool_call_id
        self.function = function
        self.status = status  # 'success' or 'error'
        self.data = data
        self.error = error
        self.args = args or {}


class ProcessedToolCalls:
    """Result of processing OpenAI tool calls"""

    def __init__(self, handled: bool = False, results: Optional[List[ToolResult]] = None):
        self.handled = handled
        self.results = results or []
        self.tool_messages = []

        # Generate tool messages for OpenAI API
        for result in self.results:
            if result.status == "success":
                # Convert Pydantic models to dict for JSON serialization
                data = result.data
                if hasattr(data, "model_dump"):
                    data = data.model_dump(mode="json")
                elif hasattr(data, "dict"):
                    data = data.dict()

                content = json.dumps({"success": True, "data": data, "operation": result.function})
            else:
                content = json.dumps(
                    {
                        "success": False,
                        "error": {"code": "EXECUTION_ERROR", "message": result.error},
                        "operation": result.function,
                    }
                )

            self.tool_messages.append(
                {"role": "tool", "tool_call_id": result.tool_call_id, "content": content}
            )


class AnthropicProcessedToolCalls:
    """Result of processing Anthropic tool calls"""

    def __init__(self, handled: bool = False, results: Optional[List[ToolResult]] = None):
        self.handled = handled
        self.results = results or []
        self.tool_messages = []

        # Generate tool result messages for Anthropic API
        if self.results:
            tool_results = []
            for result in self.results:
                if result.status == "success":
                    # Convert Pydantic models to dict for JSON serialization
                    data = result.data
                    if hasattr(data, "model_dump"):
                        data = data.model_dump(mode="json")
                    elif hasattr(data, "dict"):
                        data = data.dict()

                    content = json.dumps({"success": True, "data": data, "operation": result.function})
                else:
                    content = json.dumps(
                        {
                            "success": False,
                            "error": {"code": "EXECUTION_ERROR", "message": result.error},
                            "operation": result.function,
                        }
                    )

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": result.tool_call_id,
                    "content": content
                })

            self.tool_messages.append({
                "role": "user",
                "content": tool_results
            })


class ToolCall:
    """Represents a tool call from OpenAI API"""

    def __init__(self, id: str, function_name: str, arguments: str):
        self.id = id
        self.function = {"name": function_name, "arguments": arguments}


class OpenFilesTools:
    """
    OpenFiles Tools for AI Agents
    
    Provider-specific tool definitions and automatic execution
    for file operations. Only handles OpenFiles tools, ignoring others.

    Example:
        ```python
        from openfiles import OpenFilesClient
        from openfiles.tools import OpenFilesTools

        client = OpenFilesClient(api_key='oa_...')
        tools = OpenFilesTools(client)

        # Use with OpenAI
        import openai
        response = openai.chat.completions.create(
            model='gpt-4',
            messages=[...],
            tools=[tool.to_dict() for tool in tools.openai.definitions]
        )
        processed = await tools.openai.process_tool_calls(response)

        # Use with Anthropic
        import anthropic
        response = anthropic.messages.create(
            model='claude-sonnet-4-20250514',
            messages=[...],
            tools=tools.anthropic.definitions
        )
        processed = await tools.anthropic.process_tool_calls(response)
        ```
    """

    def __init__(self, client: OpenFilesClient, base_path: Optional[str] = None):
        """
        Initialize OpenFiles tools

        Args:
            client: OpenFiles client instance
            base_path: Base path prefix for all file operations
        """
        self.client = client
        self.base_path = base_path
        self.openai = OpenAIProvider(client, base_path)
        self.anthropic = AnthropicProvider(client, base_path)

    def with_base_path(self, base_path: str) -> "OpenFilesTools":
        """
        Create a new OpenFilesTools instance with a base path prefix
        All file operations will automatically prefix paths with the base path

        Args:
            base_path: The base path to prefix to all operations

        Returns:
            New OpenFilesTools instance with the specified base path

        Example:
            ```python
            tools = OpenFilesTools(client)
            project_tools = tools.with_base_path('projects/website')

            # AI operations will create files under 'projects/website/'
            ```
        """
        return OpenFilesTools(self.client, base_path)


class OpenAIProvider:
    """OpenAI provider for OpenFiles tools"""
    
    def __init__(self, client: OpenFilesClient, base_path: Optional[str] = None):
        self.client = client.with_base_path(base_path) if base_path else client
        self.base_path = base_path
    
    def _strip_base_path(self, result: Any) -> Any:
        """Strip base_path from response to make it transparent to AI"""
        if not self.base_path or not result:
            return result
        
        # Handle FileMetadata objects
        if hasattr(result, 'path') and result.path:
            if result.path.startswith(f"{self.base_path}/"):
                result.path = result.path[len(self.base_path) + 1:]
        
        # Handle dict with path key
        elif isinstance(result, dict) and 'path' in result:
            if result['path'] and result['path'].startswith(f"{self.base_path}/"):
                result['path'] = result['path'][len(self.base_path) + 1:]
        
        # Handle file list responses
        if hasattr(result, 'files') and result.files:
            for file in result.files:
                if hasattr(file, 'path') and file.path:
                    if file.path.startswith(f"{self.base_path}/"):
                        file.path = file.path[len(self.base_path) + 1:]
        elif isinstance(result, dict) and 'files' in result:
            for file in result['files']:
                if isinstance(file, dict) and 'path' in file:
                    if file['path'] and file['path'].startswith(f"{self.base_path}/"):
                        file['path'] = file['path'][len(self.base_path) + 1:]
        
        # Handle file versions response
        if hasattr(result, 'versions') and result.versions:
            for version in result.versions:
                if hasattr(version, 'path') and version.path:
                    if version.path.startswith(f"{self.base_path}/"):
                        version.path = version.path[len(self.base_path) + 1:]
        elif isinstance(result, dict) and 'versions' in result:
            for version in result['versions']:
                if isinstance(version, dict) and 'path' in version:
                    if version['path'] and version['path'].startswith(f"{self.base_path}/"):
                        version['path'] = version['path'][len(self.base_path) + 1:]
        
        return result

    @property
    def definitions(self) -> List[ToolDefinition]:
        """OpenAI-compatible tool definitions"""
        return [
            ToolDefinition(
                name="write_file",
                description="CREATE a NEW file (fails if file exists). Use when user wants to: create, generate, make, or write a new file. For existing files, use edit_file, append_to_file, or overwrite_file instead.",
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File path (S3-style, no leading slash)",
                            "example": "document.md",
                        },
                        "content": {"type": "string", "description": "File content to write"},
                        "contentType": {
                            "type": "string",
                            "description": "MIME type of file content. Provide specific type (e.g., text/plain, text/markdown, application/json) or use application/octet-stream as default",
                            "default": "application/octet-stream",
                            "example": "text/markdown",
                        },
                    },
                    "required": ["path", "content", "contentType"],
                    "additionalProperties": False,
                },
            ),
            ToolDefinition(
                name="read_file",
                description="READ and DISPLAY existing file content. Use when user asks to: see, show, read, view, display, or retrieve file content. Returns the actual content to show the user.",
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File path (S3-style, no leading slash)",
                            "example": "document.md",
                        },
                        "version": {
                            "type": "number",
                            "description": "Specific version to read (use 0 or omit for latest version)",
                            "default": 0,
                        },
                    },
                    "required": ["path", "version"],
                    "additionalProperties": False,
                },
            ),
            ToolDefinition(
                name="edit_file",
                description="MODIFY parts of an existing file by replacing specific text. Use when user wants to: update, change, fix, or edit specific portions while keeping the rest.",
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File path (S3-style, no leading slash)",
                            "example": "document.md",
                        },
                        "oldString": {
                            "type": "string",
                            "description": "Exact string to find and replace",
                        },
                        "newString": {
                            "type": "string",
                            "description": "Replacement string",
                        },
                    },
                    "required": ["path", "oldString", "newString"],
                    "additionalProperties": False,
                },
            ),
            ToolDefinition(
                name="list_files",
                description="LIST files. Use when user wants to: browse files, see what exists, explore contents, or find available files. IMPORTANT: Always use recursive=true unless user explicitly asks for a specific directory only.",
                parameters={
                    "type": "object",
                    "properties": {
                        "directory": {
                            "type": "string",
                            "description": "Directory path to list files from",
                            "example": "folder/",
                            "default": "/",
                        },
                        "recursive": {
                            "type": "boolean",
                            "description": "IMPORTANT: Use true to search all directories (recommended for 'list all files'), false only for specific directory browsing",
                            "default": True,
                        },
                        "limit": {
                            "type": "number",
                            "description": "Maximum number of files to return",
                            "default": 10,
                            "minimum": 1,
                            "maximum": 100,
                        },
                    },
                    "required": ["directory", "recursive", "limit"],
                    "additionalProperties": False,
                },
            ),
            ToolDefinition(
                name="append_to_file",
                description="ADD content to the END of existing file. Use for: adding to logs, extending lists, continuing documents, or accumulating data without losing existing content.",
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File path (S3-style, no leading slash)",
                            "example": "logs/daily-operations.log",
                        },
                        "content": {
                            "type": "string",
                            "description": "Content to append to the file",
                        },
                    },
                    "required": ["path", "content"],
                    "additionalProperties": False,
                },
            ),
            ToolDefinition(
                name="overwrite_file",
                description="REPLACE ALL content in existing file. Use when user wants to: completely rewrite, reset, or replace entire file content. Keeps the file but changes everything inside.",
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File path (S3-style, no leading slash)",
                            "example": "policies/employee-handbook.md",
                        },
                        "content": {
                            "type": "string",
                            "description": "New content to replace existing content",
                        },
                        "isBase64": {
                            "type": "boolean",
                            "description": "Whether the content is base64 encoded",
                            "default": False,
                        },
                    },
                    "required": ["path", "content", "isBase64"],
                    "additionalProperties": False,
                },
            ),
            ToolDefinition(
                name="get_file_metadata",
                description="GET file information (size, version, dates) WITHOUT content. Use for: checking file stats, properties, or metadata when content is not needed.",
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File path (S3-style, no leading slash)",
                            "example": "document.md",
                        },
                        "version": {
                            "type": "number",
                            "description": "Specific version to get metadata for (use 0 for latest version)",
                            "default": 0,
                        },
                    },
                    "required": ["path", "version"],
                    "additionalProperties": False,
                },
            ),
            ToolDefinition(
                name="get_file_versions",
                description="GET version history of a file. Use when user wants to: see file history, list all versions, or access previous versions.",
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File path (S3-style, no leading slash)",
                            "example": "document.md",
                        },
                        "limit": {
                            "type": "number",
                            "description": "Maximum number of versions to return",
                            "default": 10,
                            "minimum": 1,
                            "maximum": 100,
                        },
                        "offset": {
                            "type": "number",
                            "description": "Number of versions to skip for pagination",
                            "default": 0,
                            "minimum": 0,
                        },
                    },
                    "required": ["path", "limit", "offset"],
                    "additionalProperties": False,
                },
            ),
        ]

    async def process_tool_calls(self, response: Any) -> ProcessedToolCalls:
        """Process OpenAI tool calls"""
        results = []
        handled = False

        # OpenAI format: response.choices[0].message.tool_calls
        for choice in getattr(response, "choices", []):
            tool_calls = getattr(choice.message, "tool_calls", [])
            
            for tool_call in tool_calls:
                if self._is_openfiles_tool(tool_call.function.name):
                    handled = True
                    
                    try:
                        args = json.loads(tool_call.function.arguments)
                        result = await self._execute_tool(tool_call.function.name, args)
                        
                        results.append(ToolResult(
                            tool_call_id=tool_call.id,
                            function=tool_call.function.name,
                            status="success",
                            data=result,
                            args=args
                        ))
                    except Exception as error:
                        results.append(ToolResult(
                            tool_call_id=tool_call.id,
                            function=tool_call.function.name,
                            status="error",
                            error=str(error),
                            args=json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}
                        ))

        return ProcessedToolCalls(handled=handled, results=results)

    def _is_openfiles_tool(self, name: str) -> bool:
        """Check if tool name is an OpenFiles tool"""
        return name in [
            'write_file', 'read_file', 'edit_file', 'list_files',
            'append_to_file', 'overwrite_file', 'get_file_metadata', 'get_file_versions'
        ]

    async def _execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """Execute a tool call"""
        result = None
        
        if tool_name == "write_file":
            result = await self.client.write_file(
                path=args["path"],
                content=args["content"],
                content_type=args["contentType"],
            )
        elif tool_name == "read_file":
            response = await self.client.read_file(
                path=args["path"],
                version=args["version"] if args["version"] != 0 else None,
            )
            return {"path": args["path"], "content": response.data.content, "version": args["version"]}
        elif tool_name == "edit_file":
            result = await self.client.edit_file(
                path=args["path"],
                old_string=args["oldString"],
                new_string=args["newString"],
            )
        elif tool_name == "list_files":
            list_params = {
                "directory": args["directory"],
                "recursive": args.get("recursive", True),
                "limit": args["limit"],
            }
            logger.debug(f"list_files params: {json.dumps(list_params, indent=2)}")
            result = await self.client.list_files(**list_params)
        elif tool_name == "append_to_file":
            result = await self.client.append_file(
                path=args["path"],
                content=args["content"],
            )
        elif tool_name == "overwrite_file":
            result = await self.client.overwrite_file(
                path=args["path"],
                content=args["content"],
                is_base64=args["isBase64"],
            )
        elif tool_name == "get_file_metadata":
            result = await self.client.get_metadata(
                path=args["path"],
                version=args["version"] if args["version"] != 0 else None,
            )
        elif tool_name == "get_file_versions":
            result = await self.client.get_versions(
                path=args["path"],
                limit=args["limit"],
                offset=args["offset"],
            )
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        # Strip base path from result to make it transparent to AI  
        return self._strip_base_path(result)
        
        # Strip base path from result to make it transparent to AI
        return self._strip_base_path(result)


class AnthropicProvider:
    """Anthropic provider for OpenFiles tools"""
    
    def __init__(self, client: OpenFilesClient, base_path: Optional[str] = None):
        self.client = client.with_base_path(base_path) if base_path else client
        self.base_path = base_path
    
    def _strip_base_path(self, result: Any) -> Any:
        """Strip base_path from response to make it transparent to AI"""
        if not self.base_path or not result:
            return result
        
        # Handle FileMetadata objects
        if hasattr(result, 'path') and result.path:
            if result.path.startswith(f"{self.base_path}/"):
                result.path = result.path[len(self.base_path) + 1:]
        
        # Handle dict with path key
        elif isinstance(result, dict) and 'path' in result:
            if result['path'] and result['path'].startswith(f"{self.base_path}/"):
                result['path'] = result['path'][len(self.base_path) + 1:]
        
        # Handle file list responses
        if hasattr(result, 'files') and result.files:
            for file in result.files:
                if hasattr(file, 'path') and file.path:
                    if file.path.startswith(f"{self.base_path}/"):
                        file.path = file.path[len(self.base_path) + 1:]
        elif isinstance(result, dict) and 'files' in result:
            for file in result['files']:
                if isinstance(file, dict) and 'path' in file:
                    if file['path'] and file['path'].startswith(f"{self.base_path}/"):
                        file['path'] = file['path'][len(self.base_path) + 1:]
        
        # Handle file versions response
        if hasattr(result, 'versions') and result.versions:
            for version in result.versions:
                if hasattr(version, 'path') and version.path:
                    if version.path.startswith(f"{self.base_path}/"):
                        version.path = version.path[len(self.base_path) + 1:]
        elif isinstance(result, dict) and 'versions' in result:
            for version in result['versions']:
                if isinstance(version, dict) and 'path' in version:
                    if version['path'] and version['path'].startswith(f"{self.base_path}/"):
                        version['path'] = version['path'][len(self.base_path) + 1:]
        
        return result

    @property
    def definitions(self) -> List[Dict[str, Any]]:
        """Anthropic-compatible tool definitions"""
        return [
            {
                "name": "write_file",
                "description": "CREATE a NEW file (fails if file exists). Use when user wants to: create, generate, make, or write a new file. For existing files, use edit_file, append_to_file, or overwrite_file instead.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File path (S3-style, no leading slash)"
                        },
                        "content": {
                            "type": "string",
                            "description": "File content to write"
                        },
                        "contentType": {
                            "type": "string",
                            "description": "MIME type of file content. Provide specific type (e.g., text/plain, text/markdown, application/json) or use application/octet-stream as default",
                            "default": "application/octet-stream"
                        }
                    },
                    "required": ["path", "content", "contentType"]
                }
            },
            {
                "name": "read_file",
                "description": "READ and DISPLAY existing file content. Use when user asks to: see, show, read, view, display, or retrieve file content. Returns the actual content to show the user.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File path (S3-style, no leading slash)"
                        },
                        "version": {
                            "type": "number",
                            "description": "Specific version to read (use 0 or omit for latest version)",
                            "default": 0
                        }
                    },
                    "required": ["path", "version"]
                }
            },
            {
                "name": "edit_file",
                "description": "MODIFY parts of an existing file by replacing specific text. Use when user wants to: update, change, fix, or edit specific portions while keeping the rest.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File path (S3-style, no leading slash)"
                        },
                        "oldString": {
                            "type": "string",
                            "description": "Exact string to find and replace"
                        },
                        "newString": {
                            "type": "string",
                            "description": "Replacement string"
                        }
                    },
                    "required": ["path", "oldString", "newString"]
                }
            },
            {
                "name": "list_files",
                "description": "LIST files. Use when user wants to: browse files, see what exists, explore contents, or find available files. By default searches recursively across all directories unless user specifies a specific directory.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "directory": {
                            "type": "string",
                            "description": "Directory path to list files from",
                            "default": "/"
                        },
                        "recursive": {
                            "type": "boolean",
                            "description": "IMPORTANT: Use true to search all directories (recommended for 'list all files'), false only for specific directory browsing",
                            "default": True
                        },
                        "limit": {
                            "type": "number",
                            "description": "Maximum number of files to return",
                            "default": 10,
                            "minimum": 1,
                            "maximum": 100
                        }
                    },
                    "required": ["directory", "recursive", "limit"]
                }
            },
            {
                "name": "append_to_file",
                "description": "ADD content to the END of existing file. Use for: adding to logs, extending lists, continuing documents, or accumulating data without losing existing content.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File path (S3-style, no leading slash)"
                        },
                        "content": {
                            "type": "string",
                            "description": "Content to append to the file"
                        }
                    },
                    "required": ["path", "content"]
                }
            },
            {
                "name": "overwrite_file",
                "description": "REPLACE ALL content in existing file. Use when user wants to: completely rewrite, reset, or replace entire file content. Keeps the file but changes everything inside.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File path (S3-style, no leading slash)"
                        },
                        "content": {
                            "type": "string",
                            "description": "New content to replace existing content"
                        },
                        "isBase64": {
                            "type": "boolean",
                            "description": "Whether the content is base64 encoded",
                            "default": False
                        }
                    },
                    "required": ["path", "content", "isBase64"]
                }
            },
            {
                "name": "get_file_metadata",
                "description": "GET file information (size, version, dates) WITHOUT content. Use for: checking file stats, properties, or metadata when content is not needed.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File path (S3-style, no leading slash)"
                        },
                        "version": {
                            "type": "number",
                            "description": "Specific version to get metadata for (use 0 for latest version)",
                            "default": 0
                        }
                    },
                    "required": ["path", "version"]
                }
            },
            {
                "name": "get_file_versions",
                "description": "GET version history of a file. Use when user wants to: see file history, list all versions, or access previous versions.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File path (S3-style, no leading slash)"
                        },
                        "limit": {
                            "type": "number",
                            "description": "Maximum number of versions to return",
                            "default": 10,
                            "minimum": 1,
                            "maximum": 100
                        },
                        "offset": {
                            "type": "number",
                            "description": "Number of versions to skip for pagination",
                            "default": 0,
                            "minimum": 0
                        }
                    },
                    "required": ["path", "limit", "offset"]
                }
            }
        ]

    async def process_tool_calls(self, response: Any) -> AnthropicProcessedToolCalls:
        """Process Anthropic tool calls"""
        results = []
        handled = False

        # Anthropic format: response.content is an array with tool_use objects
        content = getattr(response, "content", [])
        
        for item in content:
            if getattr(item, "type", None) == "tool_use" and self._is_openfiles_tool(item.name):
                handled = True
                
                try:
                    result = await self._execute_tool(item.name, item.input)
                    
                    results.append(ToolResult(
                        tool_call_id=item.id,
                        function=item.name,
                        status="success",
                        data=result,
                        args=item.input
                    ))
                except Exception as error:
                    results.append(ToolResult(
                        tool_call_id=item.id,
                        function=item.name,
                        status="error",
                        error=str(error),
                        args=getattr(item, 'input', {})
                    ))

        return AnthropicProcessedToolCalls(handled=handled, results=results)

    def _is_openfiles_tool(self, name: str) -> bool:
        """Check if tool name is an OpenFiles tool"""
        return name in [
            'write_file', 'read_file', 'edit_file', 'list_files',
            'append_to_file', 'overwrite_file', 'get_file_metadata', 'get_file_versions'
        ]

    async def _execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """Execute a tool call"""
        result = None
        
        if tool_name == "write_file":
            result = await self.client.write_file(
                path=args["path"],
                content=args["content"],
                content_type=args["contentType"],
            )
        elif tool_name == "read_file":
            response = await self.client.read_file(
                path=args["path"],
                version=args["version"] if args["version"] != 0 else None,
            )
            return {"path": args["path"], "content": response.data.content, "version": args["version"]}
        elif tool_name == "edit_file":
            result = await self.client.edit_file(
                path=args["path"],
                old_string=args["oldString"],
                new_string=args["newString"],
            )
        elif tool_name == "list_files":
            list_params = {
                "directory": args["directory"],
                "recursive": args.get("recursive", True),
                "limit": args["limit"],
            }
            logger.debug(f"list_files params: {json.dumps(list_params, indent=2)}")
            result = await self.client.list_files(**list_params)
        elif tool_name == "append_to_file":
            result = await self.client.append_file(
                path=args["path"],
                content=args["content"],
            )
        elif tool_name == "overwrite_file":
            result = await self.client.overwrite_file(
                path=args["path"],
                content=args["content"],
                is_base64=args["isBase64"],
            )
        elif tool_name == "get_file_metadata":
            result = await self.client.get_metadata(
                path=args["path"],
                version=args["version"] if args["version"] != 0 else None,
            )
        elif tool_name == "get_file_versions":
            result = await self.client.get_versions(
                path=args["path"],
                limit=args["limit"],
                offset=args["offset"],
            )
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        # Strip base path from result to make it transparent to AI  
        return self._strip_base_path(result)