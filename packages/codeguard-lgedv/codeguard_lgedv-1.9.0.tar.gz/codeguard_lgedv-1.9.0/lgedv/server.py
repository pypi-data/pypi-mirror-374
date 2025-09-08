"""
LGEDV MCP Server - Modular Architecture
Main server file với cấu trúc module đã được tối ưu
"""
import anyio
import click
import mcp.types as types
from mcp.server.lowlevel import Server
from pydantic import FileUrl
import os
import sys
import json
# Import modules từ package structure mới
from lgedv.modules.config import RESOURCE_FILES, CUSTOM_RULE_URL, setup_logging
from lgedv.handlers.tool_handlers import ToolHandler
from lgedv.handlers.prompt_handlers import PromptHandler
from lgedv.handlers.resource_handler import get_all_resources
from lgedv.modules.persistent_storage import PersistentTracker, reset_all_analysis

from lgedv.modules.config import is_premium

# Setup logging
logger = setup_logging()

@click.command()
@click.option("--port", default=8000, help="Port to listen on for SSE")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport type",
)

def main(port: int, transport: str):
    """Main entry point for the MCP server"""
    try:
        premium_enabled = is_premium()
        logger.info(f"Premium mode: {'enabled' if premium_enabled else 'disabled'}")
        logger.info("Server started and ready to receive requests")
        logger.info(f"Starting server with transport: {transport}, port: {port}")
        
        # Check environment variable for reset
        reset_cache = os.getenv('reset_cache', 'false').lower() == 'true'
        
        if reset_cache:
            logger.info("🗑️  Resetting all analysis cache...")
            reset_all_analysis()
            logger.info("✅ Analysis cache reset completed")

        # Initialize server and handlers
        app = Server("mcp-misra-tool")
        tool_handler = ToolHandler()
        prompt_handler = PromptHandler()
        
        logger.debug("App server object created")

        # Register tool handler
        @app.call_tool()
        async def fetch_tool(name: str, arguments: dict) -> list[
            types.TextContent | types.ImageContent | types.AudioContent | types.EmbeddedResource
        ]:
            """Route tool calls to appropriate handler"""
            # Danh sách premium tools
            premium_tools = ["convert_md", "get_interface", "analyze_requirement"]
            
            # Kiểm tra premium cho các premium tools
            if name in premium_tools and not premium_enabled:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Tool '{name}' requires premium subscription. Please set 'premium': true in mcp.json env section."
                )]
            
            return await tool_handler.handle_tool_call(name, arguments)

        # Register tool list handler
        @app.list_tools()
        async def list_tools() -> list[types.Tool]:
            """List all available tools"""
            logger.info("list_tools called")
            tools = [
                # Các tool miễn phí
                types.Tool(
                    name="fetch_misra_cpp_rule",
                    description="Fetches the MISRA C++ 2008 rule markdown from remote server.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "URL to fetch MISRA rule (optional, default is preset)",
                            }
                        },
                    },
                ),
                types.Tool(
                    name="fetch_lgedv_rule",
                    description="Fetches the LGEDV rule markdown from remote server.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "URL to fetch LGEDV rule (optional, default is preset)",
                            }
                        },
                    },
                ),
                types.Tool(
                    name="fetch_static_analysis_rule",
                    description="Fetches the Static Analysis rule markdown from remote server.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "URL to fetch LGE Static Analysis rule (optional, default is preset)",
                            }
                        },                        
                    },
                ),
                types.Tool(
                    name="fetch_certcpp_rule",
                    description="Fetches the CERT C++ rule markdown from remote server.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "URL to fetch CERT C++ rule (optional, default is preset)",
                            }
                        },
                    },
                ),
                types.Tool(
                    name="fetch_custom_rule",
                    description="Fetches the Custom rule markdown from remote server.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "URL to fetch Custom rule (optional, default is preset)",
                            }
                        },
                    },
                ),
                types.Tool(
                    name="fetch_autosar_rule",
                    description="Fetches the AUTOSAR C++ 14 rule markdown from remote server.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "URL to fetch AUTOSAR rule (optional, default is preset)",
                            }
                        },
                    },
                ),
                types.Tool(
                    name="fetch_misra_c_rule",
                    description="Fetches the MISRA C 2023 rule markdown from remote server.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "URL to fetch MISRA C rule (optional, default is preset)",
                            }
                        },
                    },
                ),
                # types.Tool(
                #     name="list_source_files",
                #     description="List all .cpp files in the current src_dir or given directory.",
                #     inputSchema={
                #         "type": "object",
                #         "properties": {
                #             "dir_path": {
                #                 "type": "string",
                #                 "description": "Directory to search for .cpp files (optional, default is src_dir or cwd)",
                #             }
                #         },
                #     },
                # ),
                types.Tool(
                    name="get_src_context",
                    description="Get the content of all files in the current given directory as a single response for context.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "dir": {
                                "type": "string",
                                "description": "Directory to search for code files.",
                            }
                        },
                        "required": []
                    },                    
                ),
                types.Tool(
                    name="detect_races",
                    description="Detect potential race conditions in the codebase using src_dir.",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
                types.Tool(
                    name="analyze_leaks",
                    description="AI-powered memory leak detection in C++ codebase using src_dir.",
                    inputSchema={
                        "type": "object", 
                        "properties": {},
                    },
                ),
                types.Tool(
                    name="analyze_resources",
                    description="AI-powered resource leak detection in Linux C++ codebase using src_dir.",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
                types.Tool(
                    name="reset_analysis",
                    description="Reset analysis cache for fresh start",
                    inputSchema={
                        "type": "object", 
                        "properties": {
                            "analysis_type": {
                                "type": "string",
                                "description": "Type of analysis to reset (memory_analysis, race_analysis, resource_analysis, or 'all')",
                                "enum": ["memory_analysis", "race_analysis", "resource_analysis", "all"],
                                "default": "all"
                            },
                            "directory": {
                                "type": "string",
                                "description": "Target directory (optional, uses src_dir if not provided)"
                            }
                        },
                        "required": []
                    },
                ),
                types.Tool(
                    name="report_rule_violation",
                    description="Generate .http (HTML) report for rule violations from all .md files in report_dir.",
                    inputSchema={"type": "object", "properties": {}}
                ),
                types.Tool(
                    name="report_mem_leak",
                    description="Generate .html report for memory leak analysis from .md files in report_dir.",
                    inputSchema={"type": "object", "properties": {}}
                ),
                types.Tool(
                    name="report_race_condition",
                    description="Generate .html report for race condition analysis from .md files in report_dir.",
                    inputSchema={"type": "object", "properties": {}}
                ),
                types.Tool(
                    name="report_resource_leak", 
                    description="Generate .html report for resource leak analysis from .md files in report_dir.",
                    inputSchema={"type": "object", "properties": {}}
                ),
            ]
            
            # Premium tools - chỉ thêm nếu premium enabled
            if premium_enabled:
                premium_tools = [
                    types.Tool(
                        name="convert_md",
                        description="Convert documents (PDF, PowerPoint, Excel, Word) to markdown format - supports single file or batch directory conversion with advanced filtering",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "uri": {
                                    "type": "string",
                                    "description": "URI to convert single file (http:, https:, file:, or data: scheme)",
                                },
                                "dir": {
                                    "type": "string", 
                                    "description": "Directory path for batch conversion of all supported documents"
                                },
                                "ext": {
                                    "type": "string",
                                    "description": "Comma-separated extensions to filter (e.g., 'pdf,docx,pptx')"
                                },
                                "recursive": {
                                    "type": "boolean",
                                    "description": "Scan subdirectories recursively (default: false)"
                                },
                                "output": {
                                    "type": "string",
                                    "description": "Custom output directory path (default: same as input directory)"
                                }
                            },
                            "anyOf": [
                                {"required": ["uri"]},
                                {"required": ["dir"]}
                            ]
                        },
                    ),
                    types.Tool(
                        name="get_interface",
                        description="Quét tất cả thư mục interface, trích xuất API từ .h, .hpp, .cpp",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "dir": {
                                    "type": "string",
                                    "description": "Thư mục chứa các file interface để quét API",
                                }
                            },
                            "required": []
                        }
                    ),
                    types.Tool(
                        name="analyze_requirement",
                        description="analyze requirement from .md files in specified directory",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "dir": {
                                    "type": "string",
                                    "description": "path to directory containing .md files",
                                }
                            },
                            "required": []
                        }
                    ),
                ]
                tools.extend(premium_tools)
                
            return tools

        # Register prompt list handler
        @app.list_prompts()
        async def list_prompts() -> list[types.Prompt]:
            """List all available prompts"""
            logger.info("list_prompts called")
            prompts = [
                # Free prompts
                types.Prompt(
                    name="check_lgedv",
                    description="check code violations based on LGEDV rule guide for current file."
                ),
                types.Prompt(
                    name="check_static_analysis",
                    description="Analyze code for Static Analysis rule violations."
                ),
                types.Prompt(
                    name="check_misra_cpp",
                    description="check code violations based on MISRA C++ 2008 rule guide for current file."
                ),
                types.Prompt(
                    name="check_autosar",
                    description="check code violations based on AUTOSAR C++ 14 rule guide for current file."
                ),
                types.Prompt(
                    name="check_misra_c",
                    description="check code violations based on MISRA C 2023 rule guide for current file."
                ),
                types.Prompt(
                    name="check_certcpp",
                    description="check code violations based on CERT C++ rule guide for current file."
                ),
                types.Prompt(
                    name="check_custom",
                    description="check code violations based on Custom rule guide for current file."
                ),
                types.Prompt(
                    name="check_races",
                    description="Analyze potential race conditions in C++ codebase using AI.",
                ),
                types.Prompt(
                    name="check_leaks",
                    description="Analyze potential memory leaks in C++ codebase using AI.",
                ),
                types.Prompt(
                    name="check_resources",
                    description="Analyze potential resource leaks (file/socket/handle).",
                ),
                types.Prompt(
                    name="get_code_context",
                    description="Load content for all source files in the current directory."
                ),
                types.Prompt(
                    name="reset_analysis",
                    description="Reset all analysis cache for a fresh start."
                ),
                types.Prompt(
                    name="reset_mem_check",
                    description="Reset memory leak analysis cache."
                ),
                types.Prompt(
                    name="reset_resource_check",
                    description="Reset resource leak analysis cache."
                ),
                types.Prompt(
                    name="reset_race_check",
                    description="Reset race analysis cache."
                ),
            ]
            
            # Premium prompts - chỉ thêm nếu premium enabled
            if premium_enabled:
                premium_prompts = [
                    types.Prompt(
                        name="check_design",                        
                        description="System design verification",
                        arguments=[
                            types.PromptArgument(
                                name="feature",
                                description="Feature name to focus analysis on (e.g., 'callback waiting')",
                                required=False,
                            ),
                        ],
                    ),
                ]
                prompts.extend(premium_prompts)
                
            return prompts
        
        # Register prompt handler
        @app.get_prompt()
        async def get_prompt(name: str, arguments: dict[str, str] | None = None) -> types.GetPromptResult:
            """Route prompt calls to appropriate handler"""
            # Danh sách premium prompts
            premium_prompts = ["check_design"]
            
            # Kiểm tra premium cho các premium prompts
            if name in premium_prompts and not premium_enabled:
                return types.GetPromptResult(
                    description="Premium Feature Required",
                    messages=[
                        types.PromptMessage(
                            role="user",
                            content=types.TextContent(
                                type="text",
                                text=f"❌ Prompt '{name}' requires premium subscription. Please set 'premium': true in mcp.json env section."
                            ),
                        ),
                    ],
                )
            
            return await prompt_handler.handle_prompt(name, arguments)

        # Register resource list handler
        @app.list_resources()
        async def list_resources() -> list[types.Resource]:
            """List all available resources"""
            logger.info("list_resources called")
            return get_all_resources()

        logger.info("All handlers registered. Entering main event loop...")
        
        # Start server based on transport type
        if transport == "sse":
            _run_sse_server(app, port)
        else:
            _run_stdio_server(app)
            
        logger.info("Server stopped")
        return 0
        
    except Exception as e:
        logger.exception(f"Fatal error in main: {e}")
        print(f"Fatal error in main: {e}", file=sys.stderr)
        raise

def _run_sse_server(app: Server, port: int):
    """Run SSE server (if needed)"""
    try:
        from mcp.server.sse import SseServerTransport
        from starlette.applications import Starlette
        from starlette.responses import Response
        
        sse = SseServerTransport("/messages/")
        
        async def handle_sse(request):
            logger.info("Handling SSE connection")
            async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
                await app.run(streams[0], streams[1], app.create_initialization_options())
            return Response()
            
        # Note: Full SSE implementation would need Starlette app setup
        logger.warning("SSE transport not fully implemented in this refactored version")
        
    except ImportError as e:
        logger.error(f"SSE dependencies not available: {e}")
        raise

def _run_stdio_server(app: Server):
    """Run stdio server"""
    async def arun():
        logger.info("Running stdio server")
        try:
            import mcp.server.stdio
            async with mcp.server.stdio.stdio_server() as streams:
                await app.run(streams[0], streams[1], app.create_initialization_options())
            logger.info("stdio server run completed")
        except Exception as e:
            logger.exception(f"Exception in stdio server: {e}")
    
    anyio.run(arun)

if __name__ == "__main__":
    main()
