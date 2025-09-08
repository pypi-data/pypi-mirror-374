"""
Tool handlers for MCP server operations
Xử lý các MCP tools (fetch rules, analyze files, etc.)
"""
import os
from typing import List, Union, Dict
from mcp import types
from mcp.types import TextContent

from lgedv.modules.rule_fetcher import (
    fetch_misra_cpp_rule, fetch_lgedv_rule, fetch_certcpp_rule,
    fetch_custom_rule, fetch_autosar_rule, fetch_misra_c_rule,
    fetch_static_analysis_rule
)
from lgedv.modules.file_utils import list_source_files

from lgedv.analyzers.race_analyzer import analyze_race_conditions_in_codebase
from lgedv.analyzers.memory_analyzer import MemoryAnalyzer, analyze_leaks
from lgedv.analyzers.resource_analyzer import ResourceAnalyzer
from lgedv.modules.config import setup_logging, get_src_dir
from lgedv.modules.persistent_storage import PersistentTracker
from lgedv.handlers.requirement_handler import handle_requirement_analysis
from lgedv.handlers.interface_handler import get_interface

import pprint
from datetime import datetime

logger = setup_logging()

import platform
import json
import sys
import subprocess
from lgedv.modules import report_rule,report_race, report_resource,report_leak

from lgedv.handlers.markitdown_handler import markitdown_handler

def get_lgedv_cache_dir():
    if platform.system().lower().startswith("win"):
        return r"C:\Program Files\MCP Server CodeGuard\tmp\lgedv"
    else:
        return "/tmp/lgedv"

  
class ToolHandler:
    """Handler cho các MCP tools"""

    def __init__(self):
        self.memory_tracker = PersistentTracker(analysis_type="memory_analysis")
        
    async def handle_tool_call(self, name: str, arguments: dict) -> List[Union[
        types.TextContent, types.ImageContent, types.AudioContent, types.EmbeddedResource
    ]]:
        """
        Route và xử lý tool calls
        
        Args:
            name: Tên tool
            arguments: Arguments cho tool
            
        Returns:
            List content response
        """
        logger.info("=== handle_tool_call ENTERED ===")
        logger.info(f"Tool called: {name} with arguments: {arguments}")
        
        try:
            # Rule fetching tools
            if name == "fetch_misra_cpp_rule":
                return await self._handle_fetch_misra_cpp_rule(arguments)
            elif name == "fetch_lgedv_rule":
                return await self._handle_fetch_lgedv_rule(arguments)
            elif name == "fetch_static_analysis_rule":
                return await self._handle_fetch_static_analysis_rule(arguments)
            elif name == "fetch_certcpp_rule":
                return await self._handle_fetch_certcpp_rule(arguments)
            elif name == "fetch_custom_rule":
                return await self._handle_fetch_custom_rule(arguments)
            elif name == "fetch_autosar_rule":
                return await self._handle_fetch_autosar_rule(arguments)
            elif name == "fetch_misra_c_rule":
                return await self._handle_fetch_misra_c_rule(arguments)
            
            # File operations
            elif name == "list_source_files":
                return await self._handle_list_source_files(arguments)
            elif name == "get_src_context":
                logger.info(f"get_src_context called with arguments: {arguments}")
                return await self._handle_get_src_context(arguments)

            # Analysis tools
            elif name == "detect_races":
                return await self._handle_detect_races(arguments)
            elif name == "analyze_leaks":
                return await self._handle_memory_analysis(arguments)
            elif name == "analyze_resources":
                return await self._handle_resource_analysis(arguments)
            elif name == "reset_analysis":
                return await self._handle_reset_analysis(arguments)
            elif name == "report_rule_violation":
                return await self._handle_report_rule_violation(arguments)
            elif name == "report_mem_leak":
                return await self._handle_report_mem_leak(arguments)
            elif name == "report_race_condition":
                return await self._handle_report_race_condition(arguments)
            elif name == "report_resource_leak":
                return await self._handle_report_resource_leak(arguments)
            elif name == "analyze_requirement":
                return await self._handle_analyze_requirement(arguments)
            elif name == "get_interface":
                return await self._handle_get_interface(arguments)
            elif name == "convert_md":
                return await self._handle_convert_markitdown(arguments)
            else:
                logger.error(f"Unknown tool: {name}")
                raise ValueError(f"Unknown tool: {name}")
            
                
        except Exception as e:
            logger.exception(f"Error in tool handler for {name}: {e}")
            raise
    
    async def _handle_convert_markitdown(self, arguments: dict) -> List[types.TextContent]:
        """Handle markitdown conversion - supports both single file and batch directory conversion"""
        logger.info(f"Converting document(s) with markitdown: {arguments}")
        
        try:            
            result = await markitdown_handler.handle_convert_markitdown(arguments)
            
            if result and len(result) > 0:
                first_result = result[0]
                
                if "error" in first_result:
                    response_text = f"❌ Conversion Error: {first_result['error']}"
                    
                elif first_result.get('batch_conversion', False):
                    # Batch conversion result
                    directory = first_result.get('directory', 'unknown')
                    total_files = first_result.get('total_files_found', 0)
                    converted_count = first_result.get('converted_count', 0)
                    error_count = first_result.get('error_count', 0)
                    
                    response_text = f"📁 **Batch Conversion Completed**\n\n"
                    response_text += f"**Directory**: `{directory}`\n"
                    response_text += f"**Files Found**: {total_files}\n"
                    response_text += f"**✅ Successfully Converted**: {converted_count}\n"
                    response_text += f"**❌ Errors**: {error_count}\n\n"
                    
                    if converted_count > 0:
                        response_text += "**📝 Conversion Details:**\n\n"
                        
                        results = first_result.get('results', [])
                        for i, file_result in enumerate(results[:10], 1):  # Show first 10 results
                            if file_result.get('success', False):
                                input_file = os.path.basename(file_result.get('input_file', ''))
                                output_file = os.path.basename(file_result.get('output_file', ''))
                                content_length = file_result.get('content_length', 0)
                                response_text += f"{i}. ✅ `{input_file}` → `{output_file}` ({content_length} chars)\n"
                            else:
                                input_file = os.path.basename(file_result.get('input_file', ''))
                                error = file_result.get('error', 'Unknown error')
                                response_text += f"{i}. ❌ `{input_file}` - Error: {error}\n"
                        
                        if len(results) > 10:
                            response_text += f"\n... and {len(results) - 10} more files\n"
                            
                    else:
                        response_text += "**ℹ️ No files were converted successfully.**\n"
                        
                else:
                    # Single file conversion result  
                    uri = first_result.get('uri', 'unknown')
                    content_length = first_result.get('content_length', 0)
                    markdown_content = first_result.get('markdown_content', '')
                    metadata = first_result.get('metadata', {})
                    
                    response_text = f"✅ Successfully converted document from: {uri}\n\n"
                    response_text += f"📊 **Conversion Stats:**\n"
                    response_text += f"- Content length: {content_length} characters\n"
                    
                    if metadata:
                        response_text += f"- Metadata: {metadata}\n"
                    
                    response_text += f"\n📝 **Markdown Content:**\n\n{markdown_content}"
            else:
                response_text = "❌ No result returned from markitdown conversion"
                
            return [types.TextContent(type="text", text=response_text)]
            
        except Exception as e:
            logger.error(f"Error in _handle_convert_markitdown: {e}")
            return [types.TextContent(type="text", text=f"❌ Error during conversion: {str(e)}")]
    
    async def _handle_get_interface(self, arguments: dict):
        """
        Handle get interface tool call
        Nếu không có arguments hoặc không có 'dir', lấy từ module_api trong config
        """
        # Import config function để lấy module_api
        from lgedv.modules.config import get_module_api
        
        # Kiểm tra và lấy dir_path
        if not arguments or 'dir' not in arguments or not arguments.get('dir'):
            # Lấy từ module_api trong mcp.json
            dir_path = get_module_api()
            logger.info(f"[get_interface] No dir parameter provided, using module_api from config: {dir_path}")
        else:
            # Sử dụng dir từ arguments
            dir_path = arguments.get("dir")
            logger.info(f"[get_interface] Using dir from arguments: {dir_path}")
        
        # Kiểm tra dir_path có hợp lệ không
        if not dir_path:
            error_msg = "❌ Lỗi: Không có thư mục nào được chỉ định và không có module_api trong config"
            logger.error(error_msg)
            return [types.TextContent(type="text", text=error_msg)]
        
        # Gọi hàm get_interface với dir_path
        try:
            result = get_interface(dir_path)
            logger.info(f"[get_interface] Successfully analyzed interface in: {dir_path}")
            return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        except Exception as e:
            error_msg = f"❌ Lỗi khi phân tích interface: {str(e)}"
            logger.error(error_msg)
            return [types.TextContent(type="text", text=error_msg)]

    async def _handle_fetch_misra_cpp_rule(self, arguments: dict) -> List[types.TextContent]:
        """Handle fetch_misra_cpp_rule tool"""
        url = arguments.get("url")
        result = await fetch_misra_cpp_rule(url)
        logger.info(f"fetch_misra_cpp_rule completed for url: {url}")
        return result
    
    async def _handle_fetch_lgedv_rule(self, arguments: dict) -> List[types.TextContent]:
        """Handle fetch_lgedv_rule tool"""
        url = arguments.get("url")
        result = await fetch_lgedv_rule(url)
        logger.info(f"fetch_lgedv_rule completed for url: {url}")
        return result
    
    async def _handle_fetch_static_analysis_rule(self, arguments: dict) -> List[types.TextContent]:
        """Handle fetch_static_analysis_rule tool"""
        url = arguments.get("url")
        result = await fetch_static_analysis_rule(url)
        logger.info(f"fetch_static_analysis_rule completed for url: {url}")
        return result

    async def _handle_fetch_certcpp_rule(self, arguments: dict) -> List[types.TextContent]:
        """Handle fetch_certcpp_rule tool"""
        url = arguments.get("url")
        result = await fetch_certcpp_rule(url)
        logger.info(f"fetch_certcpp_rule completed for url: {url}")
        return result
    
    async def _handle_fetch_custom_rule(self, arguments: dict) -> List[types.TextContent]:
        """Handle fetch_custom_rule tool"""
        url = arguments.get("url")
        result = await fetch_custom_rule(url)
        logger.info(f"fetch_custom_rule completed for url: {url}")
        return result

    async def _handle_fetch_autosar_rule(self, arguments: dict) -> List[types.TextContent]:
        """Handle fetch_autosar_rule tool"""
        url = arguments.get("url")
        result = await fetch_autosar_rule(url)
        logger.info(f"fetch_autosar_rule completed for url: {url}")
        return result

    async def _handle_fetch_misra_c_rule(self, arguments: dict) -> List[types.TextContent]:
        """Handle fetch_misra_c_rule tool"""
        url = arguments.get("url")
        result = await fetch_misra_c_rule(url)
        logger.info(f"fetch_misra_c_rule completed for url: {url}")
        return result
    
    async def _handle_list_source_files(self, arguments: dict) -> List[types.TextContent]:
        """Handle list_source_files tool"""
        dir_path = get_src_dir()
        files = list_source_files(dir_path)
        logger.info(f"list_source_files found {len(files)} files")
        return [types.TextContent(type="text", text="\n".join(files))]

    
    
    async def _handle_get_src_context(self, arguments: dict) -> List[types.TextContent]:
        """
        Lấy toàn bộ code trong thư mục arguments.get("dir"), bao gồm cả thư mục con.
        Trả về hướng dẫn bằng tiếng Việt nếu prompt_lang=vi, còn lại tiếng Anh.
        """
        import os
        prompt_lang = os.environ.get("prompt_lang", "en")
        if prompt_lang == "vi":
            guide = (
                "Bạn là trợ lý ngữ cảnh mã nguồn. Nhiệm vụ của bạn là đọc và ghi nhớ toàn bộ nội dung, cấu trúc của tất cả các file mã nguồn (C++, Python, ...) trong thư mục chỉ định.\n"
                "Với mỗi file, hãy tóm tắt:\n"
                "- Tên file và đường dẫn tương đối\n"
                "- Liệt kê đầy đủ khai báo class, struct, enum, function (bao gồm tham số, kế thừa nếu có)\n"
                "- Trích xuất các docstring hoặc chú thích đầu class/function\n"
                "- Liệt kê biến toàn cục, hằng số, macro, cấu hình (kèm giá trị nếu có)\n"
                "- Tóm tắt các chú thích quan trọng hoặc tài liệu đầu file\n"
                "- Không thực hiện phân tích tĩnh hoặc kiểm tra rule ở bước này\n"
                "- Lưu ngữ cảnh này để dùng cho các truy vấn tiếp theo\n"
                "Hãy tóm tắt code context bằng tiếng Việt, trình bày rõ ràng từng mục.\n\n"
            )
        else:
            guide = (
                "You are a code context assistant. Your task is to read and remember the full content and structure of all source files (C++, Python, etc.) in the specified directory.\n"
                "For each file, extract and summarize:\n"
                "- File name and relative path\n"
                "- List full declarations of all classes, structs, enums, and functions (including parameters and inheritance)\n"
                "- Extract any docstrings or leading comments for each class/function\n"
                "- List all global variables, constants, macros, and configuration (with values if possible)\n"
                "- Summarize important block comments or documentation at the top of the file\n"
                "- Do not perform static analysis or rule checking in this step\n"
                "- Store this context for use in subsequent analysis or code-related queries\n"
                "Summarize code context in clear English, with each item presented explicitly.\n\n"
            )

        dir_path = arguments.get("dir")
        base_path = get_src_dir()
        logger.info(f"[get_context] Walking directory: {base_path}")

        # Xác định đường dẫn tuyệt đối
        if not dir_path:
            abs_path = base_path
        elif os.path.isabs(dir_path):
            abs_path = dir_path
        else:
            if "/" not in dir_path and "\\" not in dir_path:
                matches = []
                for root, dirs, files in os.walk(base_path):
                    for d in dirs:
                        if d == dir_path:
                            matches.append(os.path.join(root, d))
                if len(matches) == 1:
                    abs_path = matches[0]
                elif len(matches) == 0:
                    logger.error(f"Directory '{dir_path}' not found in {base_path}")
                    raise ValueError(f"Directory '{dir_path}' not found in {base_path}")
                else:
                    logger.error(f"Found multiple directories named '{dir_path}':\n" + "\n".join(matches))
                    raise ValueError(f"Found multiple directories named '{dir_path}':\n" + "\n".join(matches))
            else:
                abs_path = os.path.join(base_path, dir_path)

        # Kiểm tra tồn tại và là thư mục
        if not abs_path or not os.path.exists(abs_path):
            logger.error(f"Directory '{abs_path}' does not exist.")
            raise ValueError(f"Directory '{abs_path}' does not exist.")
        if not os.path.isdir(abs_path):
            logger.error(f"Path '{abs_path}' is not a directory.")
            raise ValueError(f"Path '{abs_path}' is not a directory.")

        logger.info(f"[get_context] Walking directory: {abs_path}")
        code_contents = []
        SRC_EXTENSIONS = ('.cpp', '.h', '.hpp', '.cc', '.cxx', '.py', '.java', '.js', '.jsx', '.ts')
        found_code_file = False
        for root, dirs, files in os.walk(abs_path):
            logger.info(f"[get_context] Current dir: {root}")
            logger.info(f"[get_context] Files in dir: {files}")
            for file in files:
                logger.info(f"[get_context] Checking file: {file}")
                if file.endswith(SRC_EXTENSIONS):
                    found_code_file = True
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, abs_path)
                    logger.info(f"[get_context] Found code file: {file_path} (rel: {rel_path})")
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            code_contents.append(f"// File: {rel_path}\n" + f.read())
                    except Exception as e:
                        logger.error(f"Error reading file {file_path}: {e}")
                        code_contents.append(f"// File: {rel_path}\n// Error reading file: {e}\n")

        if not found_code_file:
            logger.warning(f"No code files found in directory '{abs_path}'.")
            return [types.TextContent(type="text", text=f"// No code files found in directory '{abs_path}'.")]

        content = "\n\n".join(code_contents)
        return [types.TextContent(type="text", text=guide + content)]

    async def _handle_detect_races(self, arguments: dict) -> List[types.TextContent]:
        """Handle detect_races tool - sử dụng src_dir từ config"""
        dir_path = get_src_dir()
        logger.info(f"[detect_races] Using src_dir: {dir_path}")
        result = analyze_race_conditions_in_codebase(dir_path)
        logger.info(f"detect_races completed for dir: {dir_path}")
        # Log markdown report for each file
        markdown_reports = result.get('summary', {}).get('markdown_reports', {})
        # for file_path, markdown in markdown_reports.items():
        #     logger.info("[THREAD ENTRY MARKDOWN] File: %s\n%s", file_path, markdown)
        # Log file summaries (markdown + race info)
        file_summaries = result.get('summary', {}).get('file_summaries', {})
        for file_path, summary in file_summaries.items():
            logger.info("[RACE FILE SUMMARY] File: %s\n%s", file_path, summary)
        # Log detected races for debugging
        # detected_races = result.get('potential_race_conditions', [])
        # logger.info(f"[detect_races] detected_races: {detected_races}")
        # Log thread usage for debugging
        thread_usage = result.get('thread_usage', {})
        logger.info(f"[detect_races] thread_usage: {thread_usage}")
        # Create rich metadata prompt for AI analysis similar to memory analyzer
        metadata_section = self._create_race_analysis_metadata(result, dir_path)
        code_context_section = self._create_race_code_context_section(result, dir_path)
        # analysis_prompt = self._create_race_analysis_prompt_section(result)
       
        full_prompt = (
            f"You are an expert C++ concurrency analyst.\n\n"
            f"Please use the `detect_races` tool to manually analyze the C++ files in the directory: {dir_path}.\n\n"
            f"Then provide your expert analysis of race conditions, focusing on:\n"
            f"- Shared state accessed by multiple threads\n"
            f"- Unprotected shared state modifications\n"
            f"- Missing synchronization mechanisms (mutexes, locks, atomics)\n"
            f"- Thread-unsafe patterns\n"
            f"- Deadlock scenarios\n"
            f"- Review thread creation and join/detach logic\n"
            f"- Check for lock-free and concurrent data structure usage\n"
            f"- Provide before/after code examples for fixes\n\n"
            f"IMPORTANT: Only list race conditions or deadlocks if there is clear evidence " 
            f"in the code that a variable or resource is accessed from multiple threads "
            f"(e.g., thread creation, callback, or handler running on a different thread). "
            f"Do not warn about cases that are only speculative or lack evidence. "
            f"If no evidence is found, clearly state: 'No multi-threaded access detected for this variable in the current code.'"
            f" This will help ensure the analysis focuses on real issues and avoids unnecessary or speculative warnings.\n\n"
            f"# Automated Findings (for your review):\n"
            f"{metadata_section}\n\n"
            f"{code_context_section}\n\n"
            f"## 🔧 Please Provide\n"
            f"1. **Detailed Analysis**: Review each race condition with clear evidence and assess its validity\n"
            f"2. **Risk Assessment**: Categorize findings by severity and likelihood\n"
            f"3. **Synchronization Strategy**: Recommend appropriate locking mechanisms\n"
            f"4. **Code Examples**: Show before/after code with proper synchronization\n\n"
            f"**For each issue found, use this format:**\n\n"
            f"## 🚨 **RACE CONDITION #[number]**: [Brief Description]\n"
            f"**Type:** [data_race|deadlock|missing_sync]\n"
            f"**Severity:** [Critical|High|Medium|Low]\n"
            f"**Files Involved:** [list of files]\n"
            f"**Function Name:** [function name or global scope/unknown]\n"
            f"**Problem Description:** [explanation]\n"
            f"**Current Code:** [show the problematic code]\n"
            f"**Fix Recommendation:** [suggested solution]\n"
            f"\nFocus on actionable recommendations that can be immediately implemented.\n"
        )
        
        full_prompt += (
            f"\n---\n"
            f"**Note:** Files that have already been analyzed will not be re-analyzed in future runs. "
            f"To analyze all files again, please clear the analysis cache by running the `/reset_race_check` prompt."
        )
        
        return [types.TextContent(type="text", text=full_prompt)]
    

    def _create_memory_analysis_metadata(self, result: dict, dir_path: str) -> str:
        """Create rich metadata section for memory analysis"""
        summary = result.get('summary', {})
        leaks = result.get('detected_leaks', [])
        
        # Calculate detailed statistics
        total_allocations = sum(leak.get('allocations', 0) for leak in leaks)
        total_deallocations = sum(leak.get('deallocations', 0) for leak in leaks)
        ratio = total_deallocations / total_allocations if total_allocations > 0 else 0.0
        
        # Categorize leaks by severity
        critical_leaks = [l for l in leaks if l.get('severity') == 'critical']
        high_leaks = [l for l in leaks if l.get('severity') == 'high']
        medium_leaks = [l for l in leaks if l.get('severity') == 'medium']
        
        # Calculate leak types
        no_dealloc_leaks = [l for l in leaks if l.get('deallocations', 0) == 0]
        partial_dealloc_leaks = [l for l in leaks if l.get('deallocations', 0) > 0 and l.get('allocations', 0) > l.get('deallocations', 0)]
        
        # Get file statistics
        previously_checked_files = summary.get('previously_checked_files', 0)
        total_files_in_directory = summary.get('total_files_in_directory', 0)
        newly_remaining_files = summary.get('newly_analyzed_files', 0)
        files_analyzed = result.get('files_analyzed', 0)
        memory_flows = result.get('memory_flows', {})
        cross_file_flows = len([f for f in memory_flows.values() if f.get('is_cross_file', False)])
        
        metadata = (
            f"## 📊 Comprehensive Analysis Results:\n"
            f"### 🗂️ Project Overview:\n"
            f"- **Directory Analyzed**: `{dir_path}`\n"
            f"- **Total Files in Directory**: {total_files_in_directory}\n"
            f"- **Previously Checked Files**: {previously_checked_files}\n"            
            f"- **Remaining Files**: {newly_remaining_files}\n"           
            # f"- **Total Variables Tracked**: {len(memory_flows)}\n"
            # f"- **Analysis Scope**: Full codebase with dynamic grouping\n\n"
            # f"### 📈 Memory Operations Summary:\n"
            # f"- **Total Allocations Found**: {total_allocations}\n"
            # f"- **Total Deallocations Found**: {total_deallocations}\n"
            # f"- **Allocation/Deallocation Ratio**: {ratio:.2f} "
            # f"{'✅' if ratio >= 0.9 else '⚠️' if ratio >= 0.5 else '🔴'}\n"
            # f"- **Memory Operations Balance**: "
            # f"{'Good' if ratio >= 0.9 else 'Poor' if ratio < 0.5 else 'Fair'}\n\n"
            # f"### 🚨 Leak Severity Distribution:\n"
            # f"- **Critical**: {len(critical_leaks)} leaks (Immediate action required)\n"
            # f"- **High**: {len(high_leaks)} leaks (Review soon)\n"
            # f"- **Medium**: {len(medium_leaks)} leaks (Monitor and fix)\n"
            # f"- **Total Issues**: {len(leaks)} potential memory leaks\n\n"
            # f"### 🔍 Leak Pattern Analysis:\n"
            # f"- **Definite Leaks** (No cleanup): {len(no_dealloc_leaks)} cases 🔴\n"
            # f"- **Partial Leaks** (Incomplete cleanup): {len(partial_dealloc_leaks)} cases 🟡\n"
            # f"- **Cross-File Memory Flows**: {cross_file_flows} complex cases\n"
            # f"- **Single-File Leaks**: {len(leaks) - cross_file_flows} localized cases\n"
        )
        return metadata
    
    def _create_memory_code_context_section(self, result: dict, dir_path: str) -> str:
        """Create OPTIMIZED code context section with smart token management and file prioritization"""
        code_section = "## 📄 Relevant Code Context:\n\n"
        all_memory_ops = result.get('all_memory_ops', {})
        # Get files with memory leaks and prioritize them
        files_with_leaks = self._prioritize_files_by_leak_severity(result.get('detected_leaks', []), dir_path, all_memory_ops)

        # TOKEN OPTIMIZATION: Aggressive limits for better efficiency
        max_files = 3
        max_file_size = 50000
        processed_files = 0
        files_being_checked = []  # Track files being analyzed
        
        checked_filenames = [os.path.basename(f[0]) for f in files_with_leaks[:max_files]]
        code_section += f"### 📝 Files being checked in this session: {', '.join(checked_filenames)}\n\n"

        for file_path, leak_info in files_with_leaks[:max_files]:
            if processed_files >= max_files:
                code_section += f"### ⚠️ Additional Files ({len(files_with_leaks) - max_files} files truncated for token optimization)\n\n"
                break
                
            try:
                logger.info(f"[memory_leak] Reading file: {file_path}")
                if not os.path.isabs(file_path):
                    abs_path = os.path.join(dir_path, file_path)
                    relative_path = file_path  # Store relative path for tracking
                else:
                    abs_path = file_path
                    relative_path = os.path.relpath(file_path, dir_path)  # Convert to relative
                
                # Add to files being checked (use relative paths)
                files_being_checked.append(relative_path)
                
                with open(abs_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # SMART TRUNCATION: Limit file size
                if len(content) > max_file_size:
                    content = content[:max_file_size] + "\n\n// ... [TRUNCATED for token optimization] ..."
                
                filename = file_path.split('/')[-1]
                code_section += f"### 📁 {filename}\n"
                code_section += f"**Path**: `{file_path}`\n"

                all_lines = []
                for leak in leak_info['leaks']:
                    all_lines.extend(leak.get('leak_lines', []))
                if all_lines:
                    unique_lines = sorted(set(all_lines))
                    code_section += f"**Lines with Memory Operations**: {unique_lines}\n"
                else:
                    code_section += "**Lines with Memory Operations**: (not available)\n"

                # Add leak markers to content
                marked_content = self._add_leak_markers_to_content(content, leak_info['leaks'])
                code_section += f"```cpp\n{marked_content}\n```\n\n"
                
                processed_files += 1
                
            except Exception as e:
                filename = file_path.split('/')[-1] if file_path else "unknown"
                code_section += f"### 📁 {filename}\n"
                code_section += f"```\n// Error reading file: {e}\n```\n\n"
        
        # Save checked files to persistent storage
        if files_being_checked:
            logger.info(f"Saving {len(files_being_checked)} files to persistent storage: {files_being_checked}")
            self.memory_tracker.add_checked_files(dir_path, files_being_checked)
        
        return code_section
    
    def _create_memory_analysis_prompt_section(self, result: dict) -> str:
        """Create detailed analysis prompt section with complete leak information"""
        leaks = result.get('detected_leaks', [])
        
        prompt_section = "## 🔍 Detailed Memory Leak Findings:\n\n"
        prompt_section += f"**Total Detected Leaks**: {len(leaks)} issues requiring attention\n\n"
        
        # TOKEN OPTIMIZATION: Limit detailed findings to top 5 critical leaks
        max_detailed_leaks = 5
        leaks_to_show = sorted(leaks, key=lambda x: (
            x.get('severity') == 'critical',
            x.get('severity') == 'high', 
            x.get('deallocations', 0) == 0,  # Prioritize definite leaks
            x.get('allocations', 0)
        ), reverse=True)[:max_detailed_leaks]
        
        if len(leaks) > max_detailed_leaks:
            prompt_section += f"**Showing Top {max_detailed_leaks} Priority Leaks** (of {len(leaks)} total)\n\n"
        
        for i, leak in enumerate(leaks_to_show, 1):
            severity_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡"}.get(leak.get('severity', 'medium'), "🟡")
            
            prompt_section += f"### {severity_emoji} Leak #{i}: {leak.get('type', 'Unknown')} - {leak.get('severity', 'Medium')} Priority\n"
            prompt_section += f"- **Variable**: `{leak.get('variable', 'Unknown')}`\n"
            prompt_section += f"- **Files Involved**: {len(leak.get('files_involved', []))} file(s)\n"
            prompt_section += f"- **Allocations**: {leak.get('allocations', 0)}\n"
            prompt_section += f"- **Deallocations**: {leak.get('deallocations', 0)}\n"
            prompt_section += f"- **Leak Risk**: {'HIGH - No cleanup found!' if leak.get('deallocations', 0) == 0 else 'MEDIUM - Partial cleanup'}\n"
            
            # Show concise allocation information
            if leak.get('allocation_details'):
                prompt_section += f"- **🔴 Allocation Points** ({len(leak['allocation_details'])} locations):\n"
                for j, alloc in enumerate(leak['allocation_details'][:2], 1):  # Limit to first 2
                    file_short = alloc.get('file', 'Unknown').split('/')[-1]
                    prompt_section += f"  {j}. `{file_short}:{alloc.get('line', '?')}` - **{alloc.get('details', 'Unknown')}**\n"
                if len(leak['allocation_details']) > 2:
                    prompt_section += f"  ... and {len(leak['allocation_details']) - 2} more\n"
            else:
                prompt_section += f"- **🔴 Allocation Points**: No allocation details found\n"
            
            # Show concise deallocation information  
            if leak.get('deallocation_details'):
                prompt_section += f"- **🟢 Deallocation Points** ({len(leak['deallocation_details'])} locations):\n"
                for j, dealloc in enumerate(leak['deallocation_details'][:2], 1):  # Limit to first 2
                    file_short = dealloc.get('file', 'Unknown').split('/')[-1]
                    prompt_section += f"  {j}. `{file_short}:{dealloc.get('line', '?')}` - **{dealloc.get('details', 'Unknown')}**\n"
                if len(leak['deallocation_details']) > 2:
                    prompt_section += f"  ... and {len(leak['deallocation_details']) - 2} more\n"
            else:
                prompt_section += f"- **⚠️ NO DEALLOCATIONS FOUND** - This is a definite memory leak!\n"
            
            # Add file context for each leak
            if leak.get('files_involved'):
                prompt_section += f"- **Files to Review**: {', '.join([f.split('/')[-1] for f in leak.get('files_involved', [])])}\n"
            
            prompt_section += "\n" + "─" * 60 + "\n\n"
        
        
        return prompt_section
    
    
    def _prioritize_files_by_leak_severity(self, leaks: list, dir_path: str, all_memory_ops: dict) -> list:
        """
        Ưu tiên file memory leak:
        - Chỉ xét các file chưa check
        - Ưu tiên file có tổng số hoạt động allocation+deallocation cao hơn trước
        - Nếu bằng nhau, ưu tiên file dài hơn (nhiều dòng hơn)
        - Bao gồm cả file chưa check mà không có hoạt động leak nào
        - CHUẨN HÓA: luôn dùng relative path cho mọi key
        """
        checked_files = self.memory_tracker.get_checked_files(dir_path)
        src_files = list_source_files(dir_path)
        unchecked_files = [f for f in src_files if f not in checked_files]

        # Gom leak info như cũ
        file_leak_map = {}
        for leak in leaks:
            files_involved = leak.get('files_involved', [])
            for file_path in files_involved:
                rel_path = os.path.relpath(file_path, dir_path) if os.path.isabs(file_path) else file_path
                if rel_path not in file_leak_map:
                    file_leak_map[rel_path] = {'leaks': []}
                file_leak_map[rel_path]['leaks'].append(leak)

        prioritized_info = []
        for file_path in unchecked_files:
            # Tính tổng allocation+deallocation
            mem_ops = all_memory_ops.get(file_path, []) if all_memory_ops else []
            total_ops = sum(1 for op in mem_ops if op.operation_type in ('alloc', 'dealloc'))
            # Đếm số dòng
            abs_path = file_path if os.path.isabs(file_path) else os.path.join(dir_path, file_path)
            try:
                with open(abs_path, 'r', encoding='utf-8') as f:
                    line_count = sum(1 for _ in f)
            except Exception:
                line_count = 0
            leak_info = file_leak_map.get(file_path, {'leaks': []})
            prioritized_info.append((file_path, total_ops, line_count, leak_info))

        # Sắp xếp: tổng allocation+deallocation giảm dần, nếu bằng thì số dòng giảm dần
        sorted_files = sorted(
            prioritized_info,
            key=lambda x: (x[1], x[2]),
            reverse=True
        )

        # Log thông tin từng file
        for file_path, total_ops, line_count, leaks in sorted_files:
            logger.info("[taikt] File: %s | Total alloc+dealloc: %d | Lines: %d", file_path, total_ops, line_count)

        return [(f, l) for f, _, _, l in sorted_files]
    
    def _prioritize_files_by_resource_leak_severity(self, leaks: list, dir_path: str) -> list:
        """
        Ưu tiên file resource leak:
        - Chỉ xét các file chưa check
        - Ưu tiên file có tổng hoạt động đóng + mở cao hơn trước
        - Nếu bằng nhau, ưu tiên file dài hơn (nhiều dòng hơn)
        - Bao gồm cả file chưa check mà không có hoạt động resource nào
        - CHUẨN HÓA: luôn dùng relative path cho mọi key
        """
        resource_tracker = PersistentTracker(analysis_type="resource_analysis")
        checked_files = resource_tracker.get_checked_files(dir_path)
        logger.info(f"Previously checked files for resource analysis: {checked_files}")

        # Gom nhóm file chưa check và tính tổng open/close cho từng file (dùng relative path)
        file_op_counts = {}
        file_leak_map = {}
        for leak in leaks:
            open_ops = leak.get('open_operations', 0)
            close_ops = leak.get('close_operations', 0)
            files_involved = leak.get('files_involved', [])
            for file_path in files_involved:
                rel_path = os.path.relpath(file_path, dir_path) if os.path.isabs(file_path) else file_path
                if rel_path in checked_files:
                    continue
                if rel_path not in file_op_counts:
                    file_op_counts[rel_path] = {'open': 0, 'close': 0}
                file_op_counts[rel_path]['open'] += open_ops
                file_op_counts[rel_path]['close'] += close_ops
                if rel_path not in file_leak_map:
                    file_leak_map[rel_path] = {'leaks': []}
                file_leak_map[rel_path]['leaks'].append(leak)

        # Lấy toàn bộ file C++ chưa check (relative path)
        src_files = list_source_files(dir_path)
        unchecked_files = [f for f in src_files if f not in checked_files]

        # Tính số dòng cho từng file chưa check
        file_line_counts = {}
        for file_path in unchecked_files:
            abs_path = file_path if os.path.isabs(file_path) else os.path.join(dir_path, file_path)
            try:
                with open(abs_path, 'r', encoding='utf-8') as f:
                    line_count = sum(1 for _ in f)
            except Exception:
                line_count = 0
            file_line_counts[file_path] = line_count

        # Gom thông tin open/close và leak cho từng file chưa check (dùng relative path)
        prioritized_info = []
        for file_path in unchecked_files:
            ops = file_op_counts.get(file_path, {'open': 0, 'close': 0})
            leaks = file_leak_map.get(file_path, {'leaks': []})
            total_ops = ops['open'] + ops['close']
            prioritized_info.append((file_path, total_ops, file_line_counts[file_path], leaks))

        # Sắp xếp: tổng open+close giảm dần, nếu bằng thì số dòng giảm dần
        sorted_files = sorted(
            prioritized_info,
            key=lambda x: (x[1], x[2]),
            reverse=True
        )

        # Log thông tin từng file
        for file_path, total_ops, line_count, leaks in sorted_files:
            logger.info("[taikt] File: %s | Total open+close: %d | Lines: %d", file_path, total_ops, line_count)

        # Trả về [(file_path, leaks), ...]
        return [(f, l) for f, _, _, l in sorted_files]

    def _add_leak_markers_to_content(self, content: str, leaks: list) -> str:
        """Add visual markers to code content to highlight memory leaks"""
        lines = content.split('\n')
        # Create a map of line numbers to leak info
        line_markers = {}
        for leak in leaks:
            for alloc in leak.get('allocation_details', []):
                line_num = alloc.get('line')
                if line_num and 1 <= line_num <= len(lines):
                    marker = f"🔴 ALLOCATION: {leak.get('variable', 'unknown')} - {alloc.get('details', '')}"
                    line_markers[line_num] = marker
            for dealloc in leak.get('deallocation_details', []):
                line_num = dealloc.get('line')
                if line_num and 1 <= line_num <= len(lines):
                    marker = f"🟢 DEALLOCATION: {leak.get('variable', 'unknown')} - {dealloc.get('details', '')}"
                    line_markers[line_num] = marker
        # Add markers to lines
        marked_lines = []
        for i, line in enumerate(lines, 1):
            if i in line_markers:
                marked_lines.append(f"{line}  // {line_markers[i]}")
            else:
                marked_lines.append(line)
        return '\n'.join(marked_lines)
    
    def _summarize_resource_leaks(self, leaks: list) -> str:
        """
        Summarize resource leaks by type and severity
        
        Args:
            leaks: List of resource leak findings
            
        Returns:
            str: Formatted summary
        """
        summary = {}
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        
        for leak in leaks:
            leak_type = leak.get('resource_type', 'unknown')
            severity = leak.get('severity', 'medium')
            
            if leak_type not in summary:
                summary[leak_type] = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'total': 0}
            
            summary[leak_type][severity] += 1
            summary[leak_type]['total'] += 1
            severity_counts[severity] += 1
        
        result = f"Overall: {severity_counts['critical']} critical, {severity_counts['high']} high, {severity_counts['medium']} medium, {severity_counts['low']} low\n\n"
        
        for leak_type, counts in summary.items():
            result += f"• {leak_type.replace('_', ' ').title()}: {counts['total']} total "
            if counts['critical'] > 0:
                result += f"({counts['critical']} critical) "
            if counts['high'] > 0:
                result += f"({counts['high']} high) "
            result += "\n"
        
        return result
    
    async def _handle_memory_analysis(self, arguments: dict) -> List[types.TextContent]:
        """Handle AI-powered memory leak analysis - sử dụng src_dir từ config"""
        # Sử dụng src_dir trực tiếp, không nhận tham số dir_path nữa
        dir_path = get_src_dir()
        logger.info(f"[analyze_leaks] Using src_dir: {dir_path}")
        
        # Use the new MemoryAnalyzer
        analyzer = MemoryAnalyzer()
        result = analyzer.analyze_codebase(dir_path)
        logger.info(f"AI memory leak analysis v2 completed for dir: {dir_path}")
        
        # Create rich metadata prompt for AI analysis
        metadata_section = self._create_memory_analysis_metadata(result, dir_path)
        code_context_section = self._create_memory_code_context_section(result, dir_path)
        # disable analysis prompt for leaks
        # analysis_prompt = self._create_memory_analysis_prompt_section(result)
          
        full_prompt = (
            f"You are an expert C++ memory management analyst.\n\n"
            f"Please use the `analyze_leaks` tool to manually analyze the C++ files in the directory: {dir_path}.\n\n"
            f"Then provide your expert analysis of memory leaks, focusing on:\n"
            f"- **Unreleased memory allocations**\n"
            f"- **Dangling pointers**\n"
            f"- **Memory corruption issues**\n"
            f"- **Inefficient memory usage patterns**\n"
            f"- **Focus on leaks with 0 deallocations first:** These are guaranteed leaks\n"
            f"- **Check allocation/deallocation type mismatches:** `new`/`delete[]`, `malloc`/`delete`, etc.\n"
            f"- **Look for exception safety issues:** Leaks when exceptions occur\n"
            f"- **Verify RAII compliance:** Use smart pointers where possible\n"
            f"- **Check constructor/destructor pairs:** Ensure proper cleanup in class destructors\n\n"
            f"Only provide your expert analysis. Do not repeat the Automated Findings section.\n"
            f"Additionally, propose refactored code for all relevant C++ files.\n\n"

            f"# Automated Findings (for your review):\n"
            f"{metadata_section}\n\n"
            f"{code_context_section}\n\n"
            # f"{analysis_prompt}\n\n"
            f"## 🔧 Please Provide\n"
            f"1. **Detailed Analysis:** Review each memory leak with clear evidence and assess its validity\n"
            f"2. **Risk Assessment:** Categorize findings by severity and likelihood\n"
            f"3. **Fix Recommendations:** Specific code changes for each issue\n"
            f"4. **Best Practices:** Suggest modern C++ approaches (RAII, smart pointers)\n"
            f"5. **Prevention Strategies:** How to avoid similar issues in the future\n\n"
            f"**For each issue found, use this format:**\n\n"
            f"## 🚨 **MEMORY LEAK #[number]**: [Brief Description]\n"
            f"**Type:** [Missing delete|Mismatched allocation|etc]\n"
            f"**Severity:** [Critical|High|Medium|Low]\n"
            f"**Files Involved:** [list of files]\n"
            f"**Function Name:** [function name or global scope/unknown]\n"
            f"**Problem Description:** [explanation]\n"
            f"**Current Code**: Show the problematic code\n"
            f"**Fix Recommendation:** [suggested solution]\n"
            f"\nFocus on actionable recommendations that can be immediately implemented.\n"
        )
        
        full_prompt += (
            f"\n---\n"
            f"**Note:** Files that have already been analyzed will not be re-analyzed in future runs. "
            f"To analyze all files again, please clear the analysis cache by running the `/reset_mem_check` prompt."
        )

        return [types.TextContent(type="text", text=full_prompt)]
    
    # ham nay duoc goi tu prompt handler
    async def _handle_resource_analysis(self, arguments: dict) -> List[types.TextContent]:
        """
        Handle AI resource leak analysis - tạo rich prompt cho Copilot analysis
        Prioritize files by leak severity for code context (like memory analyzer)
        """
        src_dir = get_src_dir()
        logger.info(f"Starting AI resource leak analysis on directory: {src_dir}")

        analyzer = ResourceAnalyzer()
        result = analyzer.analyze_codebase()
        logger.info(f"AI resource leak analysis found {len(result.get('detected_leaks', []))} leaks in directory: {src_dir}")
        
        # Always create rich metadata and context (even when no leaks detected)
        logger.info("Creating metadata section for resource analysis")
        metadata_section = self._create_resource_analysis_metadata(result, src_dir)
        code_context_section = self._create_resource_code_context_section(result, src_dir)
        
        # Handle status message based on leaks found
        leaks_count = len(result.get('detected_leaks', []))
        status_message = f"{leaks_count} resource leaks detected" if leaks_count > 0 else "No resource leaks detected by automated analysis"
        
        full_prompt = (
            f"You are an expert Linux C++ resource management analyst.\n\n"
            f"**Task:**\n"
            f"Analyze the C++ files in `{src_dir}` for resource leaks using the `analyze_resources` tool.\n"
            f"**Status**: {status_message}.\n\n"
            f"Focus strictly on real, evidence-based issues. Do NOT include any hypothetical, speculative, or potential cases—report only resource leaks that are clearly demonstrated by the code and findings.\n\n"
            f"**Resource Types to Check:**\n"
            f"- File descriptors (open/close, FILE*/fclose)\n"
            f"- Sockets (socket/close, network connections)\n"
            f"- Memory mapping (mmap/munmap, shared memory cleanup)\n"
            f"- IPC (message queues, semaphores, shared memory detach)\n"
            f"- Directory handles (opendir/closedir)\n\n"
            f"**Instructions:**\n"
            f"- Only provide your expert analysis. Do NOT repeat the Automated Findings section.\n"
            f"- For each confirmed issue, use the format below.\n"
            f"- Propose refactored code for all relevant C++ files.\n"
            f"- Focus on actionable, immediately applicable recommendations.\n\n"
            f"# Automated Findings (for your review):\n"
            f"{metadata_section}\n\n"
            f"{code_context_section}\n\n"
            f"**For each issue, use this format:**\n"
            f"## 🚨 RESOURCE LEAK #[number]: [Brief Description]\n"
            f"- **Type:** [resource type]\n"
            f"- **Severity:** [Critical|High|Medium|Low]\n"
            f"- **Files Involved:** [list of files]\n"
            f"- **Location:** [function name or global scope/unknown]\n"
            f"- **Problem:** [explanation]\n"
            f"- **Current Code:** [show problematic code]\n"
            f"- **Fix Recommendation:** [suggested code or approach]\n\n"
            f"**Best Practices:**\n"
            f"- Suggest modern C++ approaches (RAII, smart pointers, std::fstream, etc.) where applicable.\n"
            f"- Recommend prevention strategies for future code.\n\n"
            f"Do NOT include any speculative, hypothetical, or potential warnings. Only analyze and report on actual, evidenced resource leaks found in the code and findings provided.\n"
        )

        full_prompt += (
            f"\n---\n"
            f"**Note:** Files that have already been analyzed will not be re-analyzed in future runs. "
            f"To analyze all files again, please clear the analysis cache by running the `/reset_resource_check` prompt."
        )
        
        return [types.TextContent(type="text", text=full_prompt)]
    
        
    def _create_resource_analysis_metadata(self, analysis_result: dict, src_dir: str) -> str:
        """Create metadata section for resource analysis"""
        detected_leaks = analysis_result.get("detected_leaks", [])
        summary = analysis_result.get("summary", {})
        logger.info(f"Creating metadata for resource analysis with {len(detected_leaks)} leaks")
        
        logger.info(
            f"Summary values: total_files_analyzed={summary.get('total_files_analyzed', 0)}, "
            f"resource_operations_found={summary.get('resource_operations_found', 0)}, "
            f"cross_file_flows={summary.get('cross_file_flows', 0)}"
        )
        files_analyzed = analysis_result.get('files_analyzed', 0)
        previously_checked_files = summary.get('previously_checked_files', 0)
        total_files_in_directory = summary.get('total_files_in_directory', 0)
        newly_remaining_files = summary.get('newly_analyzed_files', 0)
       
        # Create metadata section
        metadata = (
            f"## 📊 **Analysis Metadata**\n\n"
            f"- **Directory**: `{src_dir}`\n"
            f"- **Analysis Type**: Linux C++ Resource Leak Detection\n"
            f"- **Total Files in Directory**: {total_files_in_directory}\n"
            f"- **Previously Checked Files**: {previously_checked_files}\n"            
            f"- **Remaining Files**: {newly_remaining_files}\n" 
            f"- **Resource Operations Found**: {summary.get('resource_operations_found', 0)}\n"
            f"- **Cross-file Flows**: {summary.get('cross_file_flows', 0)}\n\n"
        )
        return metadata
    
    def _create_resource_code_context_section(self, analysis_result: dict, src_dir: str) -> str:
        code_section = "## 📄 Relevant Code Context:\n\n"
        # Get files with resource leaks and prioritize them
        files_with_leaks = self._prioritize_files_by_resource_leak_severity(analysis_result.get('detected_leaks', []), src_dir)
        
        # TOKEN OPTIMIZATION: Aggressive limits for better efficiency
        max_files = 3
        max_file_size = 50000
        processed_files = 0
        files_being_checked = []  # Track files being analyzed in THIS session
        
        checked_filenames = [os.path.basename(f[0]) for f in files_with_leaks[:max_files]]
        code_section += f"### 📝 Files being checked in this session: {', '.join(checked_filenames)}\n\n"

        for file_path, leak_info in files_with_leaks[:max_files]:
            if processed_files >= max_files:
                code_section += f"### ⚠️ Additional Files ({len(files_with_leaks) - max_files} files truncated for token optimization)\n\n"
                break
                
            try:
                logger.info(f"[resource_leak] Reading file: {file_path}")
                if not os.path.isabs(file_path):
                    abs_path = os.path.join(src_dir, file_path)
                    relative_path = file_path  # Store relative path for tracking
                else:
                    abs_path = file_path
                    relative_path = os.path.relpath(file_path, src_dir)  # Convert to relative
                
                # Add to files being checked in THIS session (use relative paths)
                files_being_checked.append(relative_path)
                
                with open(abs_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # SMART TRUNCATION: Limit file size
                if len(content) > max_file_size:
                    content = content[:max_file_size] + "\n\n// ... [TRUNCATED for token optimization] ..."
                
                filename = file_path.split('/')[-1]
                code_section += f"### 📁 {filename}\n"
                code_section += f"**Path**: `{file_path}`\n"

                # Show resource operation lines
                all_lines = []
                for leak in leak_info['leaks']:
                    all_lines.extend(leak.get('leak_lines', []))
                if all_lines:
                    unique_lines = sorted(set(all_lines))
                    code_section += f"**Lines with Resource Operations**: {unique_lines}\n"
                else:
                    code_section += "**Lines with Resource Operations**: (not available)\n"

                # Add resource leak markers to content
                # marked_content = self._add_resource_leak_markers_to_content(content, leak_info['leaks'])
                # code_section += f"```cpp\n{marked_content}\n```\n\n"
                code_section += f"```cpp\n{content}\n```\n\n"
                
                processed_files += 1
                
            except Exception as e:
                filename = file_path.split('/')[-1] if file_path else "unknown"
                code_section += f"### 📁 {filename}\n"
                code_section += f"```\n// Error reading file: {e}\n```\n\n"
        
        # Save ONLY files being checked in this session to persistent storage (incremental)
        if files_being_checked:
            resource_tracker = PersistentTracker(analysis_type="resource_analysis")
            logger.info(f"Incrementally saving {len(files_being_checked)} NEW resource files to persistent storage: {files_being_checked}")
            resource_tracker.add_checked_files(src_dir, files_being_checked)
        
        return code_section
    
    def _add_resource_leak_markers_to_content(self, content: str, leaks: list) -> str:
        """Add visual markers to code content to highlight resource leaks"""
        lines = content.split('\n')
        # Create a map of line numbers to leak info
        line_markers = {}
        for leak in leaks:
            for open_op in leak.get('open_details', []):
                line_num = open_op.get('line')
                if line_num and 1 <= line_num <= len(lines):
                    marker = f"🔴 RESOURCE OPEN: {leak.get('variable', 'unknown')} - {open_op.get('details', '')}"
                    line_markers[line_num] = marker
            for close_op in leak.get('close_details', []):
                line_num = close_op.get('line')
                if line_num and 1 <= line_num <= len(lines):
                    marker = f"🟢 RESOURCE CLOSE: {leak.get('variable', 'unknown')} - {close_op.get('details', '')}"
                    line_markers[line_num] = marker
        # Add markers to lines
        marked_lines = []
        for i, line in enumerate(lines, 1):
            if i in line_markers:
                marked_lines.append(f"{line}  // {line_markers[i]}")
            else:
                marked_lines.append(line)
        return '\n'.join(marked_lines)

    def _create_resource_findings_section(self, analysis_result: dict) -> str:
        """Create findings section with detected resource leaks"""
        detected_leaks = analysis_result.get("detected_leaks", [])
        
        if not detected_leaks:
            return "## ✅ **Analysis Results**: No resource leaks detected\n"
        
        findings_section = f"## 🚨 **Resource Leak Findings** ({len(detected_leaks)} total)\n\n"
        
        # Group by resource type
        leak_groups = {}
        for leak in detected_leaks:
            resource_type = leak.get('resource_type', 'unknown')
            if resource_type not in leak_groups:
                leak_groups[resource_type] = []
            leak_groups[resource_type].append(leak)
        
        for resource_type, type_leaks in leak_groups.items():
            display_type = resource_type.replace('_', ' ').title()
            findings_section += f"### 🔍 **{display_type} Leaks** ({len(type_leaks)} found)\n\n"
            
            # Show first 3 leaks of each type for token efficiency
            for i, leak in enumerate(type_leaks[:3], 1):
                variable = leak.get('variable', 'unknown')
                severity = leak.get('severity', 'medium')
                files_involved = leak.get('files_involved', [])
                file_names = [os.path.basename(f) for f in files_involved]
                
                findings_section += f"{i}. **Variable `{variable}`** - {severity} severity\n"
                findings_section += f"   - Files: {', '.join(file_names)}\n"
                findings_section += f"   - Opens: {leak.get('open_operations', 0)}, Closes: {leak.get('close_operations', 0)}\n"
                
                # Show open locations
                open_details = leak.get('open_details', [])
                if open_details:
                    findings_section += f"   - Open locations:\n"
                    for detail in open_details[:2]:  # Show first 2
                        file_name = os.path.basename(detail.get('file', ''))
                        line = detail.get('line', 'unknown')
                        findings_section += f"     • {file_name}:{line}\n"
                
                if leak.get('recommendation'):
                    findings_section += f"   - Fix: {leak['recommendation']}\n"
                
                findings_section += "\n"
            
            if len(type_leaks) > 3:
                findings_section += f"   ... and {len(type_leaks) - 3} more {display_type.lower()} leaks\n\n"
        
        return findings_section

    def _create_race_analysis_metadata(self, race_result: dict, dir_path: str) -> str:
        """Create metadata section for race condition analysis"""
        summary = race_result.get('summary', {})
        previously_checked_files = summary.get('previously_checked_files', 0)
        total_files_in_directory = summary.get('total_files_in_directory', 0)
        newly_remaining_files = summary.get('newly_analyzed_files', 0)
        files_with_threads = summary.get('files_with_threads', 0)

        metadata_section = "## 📊 Analysis Metadata\n\n"
        metadata_section += f"**Target Directory:** `{dir_path}`\n"
        metadata_section += f"**Total Files in Directory:** {total_files_in_directory}\n"
        metadata_section += f"**Previously Checked Files:** {previously_checked_files}\n"
        metadata_section += f"**Remaining Files:** {newly_remaining_files}\n"
        metadata_section += f"**Files with Thread Usage:** {files_with_threads}\n"
        metadata_section += "\n"
        return metadata_section
    
    
    def _create_race_code_context_section(self, result: dict, dir_path: str) -> str:
        import collections
        context_section = "## 📁 Source Code Context\n\n"
        summary = result.get('summary', {})
        detected_races = result.get('potential_race_conditions', [])
        markdown_reports = summary.get('markdown_reports', {})
        thread_usage = result.get('thread_usage', {})

        logger.info("==== [THREAD ENTRY MARKDOWN REPORTS] ====")
        # file_path: duong dan tuyet doi
        for file_path, markdown in markdown_reports.items():
            logger.info("[THREAD ENTRY MARKDOWN] File: %s\n%s", file_path, markdown)

        # Get previously checked files for race analysis
        race_tracker = PersistentTracker(analysis_type="race_analysis")
        checked_files = race_tracker.get_checked_files(dir_path)
        logger.info(f"Previously checked files for race analysis: {checked_files}")

        # Lấy danh sách tất cả file C++ đầu vào
        all_src_files = summary.get('all_src_files', [])
        if not all_src_files:
            all_src_files = list(summary.get('file_summaries', {}).keys())

        logger.info(f"taikt- [all_src_files] Total: {len(all_src_files)} files: {all_src_files}")

        # Chuyển tất cả file_path sang absolute path khi build unchecked_files
        unchecked_files = []
        for file_path in all_src_files:
            abs_path = file_path if os.path.isabs(file_path) else os.path.abspath(os.path.join(dir_path, file_path))
            relative_path = os.path.relpath(abs_path, dir_path)
            if relative_path not in checked_files:
                unchecked_files.append(abs_path)
            else:
                logger.info(f"Skipping already checked race file: {relative_path}")

        logger.info(f"Unchecked race files: {len(unchecked_files)}/{len(all_src_files)} files")

        # If no unchecked files, show message
        if not unchecked_files:
            context_section += "### ✅ All files have been checked in previous sessions.\n\n"
            return context_section

        # Nếu số lượng file unchecked <= 3 thì lấy hết
        if len(unchecked_files) <= 3:
            final_files = list(dict.fromkeys(unchecked_files))
        else:
            # Tính entry_points_count và số dòng code cho từng unchecked file
            file_stats = []
            for file_path in unchecked_files:
                markdown = markdown_reports.get(file_path, "")
                if markdown.strip() == "No detect thread entrypoint functions." or not markdown.strip():
                    entry_points_count = 0
                else:
                    entry_points_count = len([line for line in markdown.splitlines() if line.strip()])
                # Đếm số dòng code
                try:
                    if not os.path.isabs(file_path):
                        abs_path = os.path.join(dir_path, file_path)
                    else:
                        abs_path = file_path
                    with open(abs_path, 'r', encoding='utf-8') as f:
                        code_lines = sum(1 for _ in f)
                except Exception:
                    code_lines = 0
                file_stats.append((file_path, entry_points_count, code_lines))
            # Sắp xếp ưu tiên: entry_points_count giảm dần, nếu bằng thì code_lines giảm dần
            file_stats_sorted = sorted(
                file_stats,
                key=lambda x: (x[1], x[2]),
                reverse=True
            )
            final_files = [f[0] for f in file_stats_sorted[:3]]

            # Log selected files with entry_points_count and code_lines
            for file_path, entry_points_count, code_lines in file_stats_sorted[:3]:
                logger.info(
                    "[race_context_selection] File: %s | Entry points: %d | Code lines: %d",
                    file_path, entry_points_count, code_lines
                )

        # Track files being checked in THIS session
        files_being_checked = []

        # Build context_section
        file_count = 0
        max_file_size = 50000
        checked_filenames = [os.path.basename(f) for f in final_files]
        context_section += f"### 📝 Files being checked in this session: {', '.join(checked_filenames)}\n\n"
        
        for file_path in final_files:
            file_count += 1
            try:
                if not os.path.isabs(file_path):
                    abs_path = os.path.join(dir_path, file_path)
                    relative_path = file_path  # Store relative path for tracking
                else:
                    abs_path = file_path
                    relative_path = os.path.relpath(file_path, dir_path)  # Convert to relative
                
                # Add to files being checked in THIS session (use relative paths)
                files_being_checked.append(relative_path)
                
                with open(abs_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if len(content) > max_file_size:
                    content = content[:max_file_size] + "\n\n// ... [TRUNCATED FOR BREVITY] ..."
                filename = os.path.basename(file_path)
                context_section += f"### {file_count}. 📁 **{filename}**\n"
                context_section += f"**Path**: `{file_path}`\n"
                # Race summary
                file_races = [r for r in detected_races if file_path in r.get('files_involved', [])]
                if file_races:
                    context_section += f"**Race Conditions**: {len(file_races)} found\n"
                    for race in file_races[:2]:
                        context_section += f"- {race.get('type', 'unknown')}: {race.get('description', 'No description')}\n"
                # Thread usage summary
                file_threads = thread_usage.get(file_path, [])
                if file_threads:
                    context_section += f"**Thread Usage**: {len(file_threads)} thread-related operations\n"
                # Thread entry markdown
                markdown = markdown_reports.get(file_path, "")
                # logger.info(f"[THREAD ENTRY MARKDOWN - taikt] File: {file_path}\n{markdown}")
                # key = file_path if file_path in markdown_reports else os.path.abspath(file_path)
                markdown = markdown_reports.get(file_path, "")
                logger.info("[taikt- THREAD ENTRY] File: %s\n%s", file_path, markdown)

                if markdown:
                    context_section += f"**Thread Entry Points**:\n{markdown}\n"
                # Actual code
                context_section += f"\n```cpp\n{content}\n```\n\n"
            except Exception as e:
                filename = os.path.basename(file_path)
                context_section += f"### {file_count}. 📁 **{filename}** (Error reading: {e})\n\n"
        
        # Save ONLY files being checked in this session to persistent storage (incremental)
        if files_being_checked:
            logger.info(f"Incrementally saving {len(files_being_checked)} NEW race files to persistent storage: {files_being_checked}")
            race_tracker.add_checked_files(dir_path, files_being_checked)
        
        # Show remaining files info
        remaining_unchecked = len(unchecked_files) - len(final_files)
        if remaining_unchecked > 0:
            context_section += f"### 📊 **Additional Files**: {remaining_unchecked} more C++ files available for future analysis\n\n"
        
        return context_section

    def _create_race_analysis_prompt_section(self, race_result: dict) -> str:
        """Create analysis prompt section with only Priority Analysis Guidelines (comment out detailed findings)"""
        prompt_section = "## 🎯 Priority Analysis Guidelines:\n\n"
        prompt_section += "1. Focus on shared state accessed by multiple threads.\n"
        prompt_section += "2. Ensure proper synchronization (mutexes, locks, atomics).\n"
        prompt_section += "3. Review thread creation and join/detach logic.\n"
        prompt_section += "4. Check for lock-free and concurrent data structure usage.\n"
        prompt_section += "5. Provide before/after code examples for fixes.\n\n"
        return prompt_section

    async def _handle_reset_analysis(self, arguments: dict) -> List[types.TextContent]:
        """Reset analysis cache for fresh start"""
        import shutil
        try:
            cache_dir = get_lgedv_cache_dir()
            shutil.rmtree(cache_dir, ignore_errors=True)
            message = f"All analysis cache in {cache_dir} has been reset (directory deleted)."
            return [types.TextContent(type="text", text=message)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error resetting analysis cache: {e}")]

    async def _handle_reset_mem_check(self, arguments: dict) -> List[types.TextContent]:
        """
        Reset memory leak analysis cache (xóa file /tmp/lgedv/memory_analysis_checked.json).
        """
        import os
        file_path = os.path.join(get_lgedv_cache_dir(), "memory_analysis_checked.json")
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                message = "Memory leak analysis cache has been reset."
            else:
                message = "No memory leak analysis cache file found to reset."
            return [types.TextContent(type="text", text=message)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error resetting memory leak analysis cache: {e}")]


    async def _handle_reset_resource_check(self, arguments: dict) -> List[types.TextContent]:
        """
        Reset resource leak analysis cache (xóa file /tmp/lgedv/resource_analysis_checked.json).
        """
        import os
        file_path = os.path.join(get_lgedv_cache_dir(), "resource_analysis_checked.json")
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                message = "Resource leak analysis cache has been reset."
            else:
                message = "No resource leak analysis cache file found to reset."
            return [types.TextContent(type="text", text=message)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error resetting resource leak analysis cache: {e}")]
        
    
    async def _handle_reset_race_check(self, arguments: dict) -> List[types.TextContent]:
        """
        Reset race analysis cache (xóa file /tmp/lgedv/race_analysis_checked.json).
        """
        import os
        file_path = os.path.join(get_lgedv_cache_dir(), "race_analysis_checked.json")
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                message = "Race analysis cache has been reset."
            else:
                message = "No race analysis cache file found to reset."
            return [types.TextContent(type="text", text=message)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error resetting race analysis cache: {e}")]


    async def _handle_report_rule_violation(self, arguments: dict):
        """
        Quét tất cả file .md trong report_dir, tổng hợp tất cả rule violations vào 1 file rule_violation.html
        Luôn luôn xóa file báo cáo cũ và tạo mới để đảm bảo tính cập nhật
        """
        report_dir = os.environ.get("report_dir", "./report")
        
        # 🔥 BƯỚC 1: Xóa file HTML báo cáo cũ nếu tồn tại
        output_path = os.path.join(report_dir, "rule_violation.html")  # Đổi thành số nhiều để nhất quán
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
                logger.info("🗑️  Deleted existing rule violations report: %s", output_path)
            except Exception as e:
                logger.warning("Failed to delete existing rule violations report: %s", e)
        
        # 🔥 BƯỚC 2: Quét và phân tích lại TẤT CẢ file .md từ đầu
        all_violations = []
        processed_files = []
        
        logger.info("🔍 Re-analyzing ALL .md files for rule violations...")
        
        for fname in os.listdir(report_dir):
            if fname.endswith(".md"):
                input_path = os.path.join(report_dir, fname)
                try:
                    with open(input_path, 'r', encoding='utf-8') as f:
                        md_text = f.read()
                    logger.info("Processing rule violations from: %s", input_path)
                    violations = report_rule.extract_violations(md_text)
                    if violations:
                        # Thêm thông tin file nguồn vào mỗi violation
                        for violation in violations:
                            violation['source_file'] = fname
                        all_violations.extend(violations)
                        processed_files.append(fname)
                        logger.info("✅ Found %d rule violations in %s", len(violations), fname)
                    else:
                        logger.info("ℹ️  No rule violations found in %s", fname)
                except Exception as e:
                    logger.error("❌ Error processing %s: %s", fname, e)
                    continue
        
        # 🔥 BƯỚC 3: Tạo báo cáo HTML mới hoàn toàn
        if all_violations:
            report_rule.write_consolidated_html_table(all_violations, output_path, processed_files)
            return [types.TextContent(
                type="text", 
                text=f"🔄 Re-generated fresh rule violations report with {len(all_violations)} violations from {len(processed_files)} files: {output_path}\n"
                    f"📊 Processed files: {', '.join(processed_files)}\n"
                    f"🗑️  Previous report deleted and regenerated from scratch"
            )]
        else:
            # Tạo file HTML trống để báo hiệu không có rule violation
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("""<!DOCTYPE html>
    <html><head><meta charset="utf-8"><title>Rule Violations Report - No Issues Found</title></head>
    <body>
    <h1>Rule Violations Analysis Report</h1>
    <p><strong>Status:</strong> ✅ No rule violations detected</p>
    <p><strong>Files analyzed:</strong> {}</p>
    <p><strong>Generated on:</strong> {}</p>
    </body></html>""".format(len(processed_files), 
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            return [types.TextContent(
                type="text", 
                text=f"✅ No rule violations found in {len(processed_files)} processed files. Clean report generated: {output_path}"
            )]

    
    async def _handle_report_mem_leak(self, arguments: dict):
        """
        Quét tất cả file .md trong report_dir, tổng hợp tất cả memory leaks vào 1 file memory_leak.html
        Luôn luôn xóa file báo cáo cũ và tạo mới để đảm bảo tính cập nhật
        """
        report_dir = os.environ.get("report_dir", "./report")
        
        # 🔥 BƯỚC 1: Xóa file HTML báo cáo cũ nếu tồn tại
        output_path = os.path.join(report_dir, "memory_leak.html")  # KHÔNG CÓ 'S'
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
                logger.info("🗑️  Deleted existing memory leak report: %s", output_path)
            except Exception as e:
                logger.warning("Failed to delete existing memory leak report: %s", e)
        
        # 🔥 BƯỚC 2: Quét và phân tích lại TẤT CẢ file .md từ đầu
        all_leaks = []
        processed_files = []
        
        logger.info("🔍 Re-analyzing ALL .md files for memory leaks...")
        
        for fname in os.listdir(report_dir):
            if fname.endswith(".md"):
                input_path = os.path.join(report_dir, fname)
                try:
                    with open(input_path, 'r', encoding='utf-8') as f:
                        md_text = f.read()
                    logger.info("Processing memory leaks from: %s", input_path)
                    leaks = report_leak.extract_violations(md_text)  # DÙNG report_leak
                    if leaks:
                        for leak in leaks:
                            leak['source_file'] = fname
                        all_leaks.extend(leaks)
                        processed_files.append(fname)
                        logger.info("✅ Found %d memory leaks in %s", len(leaks), fname)
                    else:
                        logger.info("ℹ️  No memory leaks found in %s", fname)
                except Exception as e:
                    logger.error("❌ Error processing %s: %s", fname, e)
                    continue
        
        # 🔥 BƯỚC 3: Tạo báo cáo HTML mới hoàn toàn
        if all_leaks:
            report_leak.write_consolidated_html_table(all_leaks, output_path, processed_files)
            return [types.TextContent(
                type="text", 
                text=f"🔄 Re-generated fresh memory leak report with {len(all_leaks)} leaks from {len(processed_files)} files: {output_path}\n"
                    f"📊 Processed files: {', '.join(processed_files)}\n"
                    f"🗑️  Previous report deleted and regenerated from scratch"
            )]
        else:
            # Tạo file HTML trống để báo hiệu không có memory leak
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("""<!DOCTYPE html>
    <html><head><meta charset="utf-8"><title>Memory Leak Report - No Issues Found</title></head>
    <body>
    <h1>Memory Leak Analysis Report</h1>
    <p><strong>Status:</strong> ✅ No memory leaks detected</p>
    <p><strong>Files analyzed:</strong> {}</p>
    <p><strong>Generated on:</strong> {}</p>
    </body></html>""".format(len(processed_files), 
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            return [types.TextContent(
                type="text", 
                text=f"✅ No memory leaks found in {len(processed_files)} processed files. Clean report generated: {output_path}"
            )]


    async def _handle_report_race_condition(self, arguments: dict):
        """
        Quét tất cả file .md trong report_dir, tổng hợp tất cả race conditions vào 1 file race_condition.html
        Luôn luôn xóa file báo cáo cũ và tạo mới để đảm bảo tính cập nhật
        """
        report_dir = os.environ.get("report_dir", "./report")
        
        # 🔥 BƯỚC 1: Xóa file HTML báo cáo cũ nếu tồn tại
        output_path = os.path.join(report_dir, "race_condition.html")  # Đảm bảo tên file nhất quán
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
                logger.info("🗑️  Deleted existing race condition report: %s", output_path)
            except Exception as e:
                logger.warning("Failed to delete existing race condition report: %s", e)
        
        # 🔥 BƯỚC 2: Quét và phân tích lại TẤT CẢ file .md từ đầu
        all_races = []
        processed_files = []
        
        logger.info("🔍 Re-analyzing ALL .md files for race conditions...")
        
        for fname in os.listdir(report_dir):
            if fname.endswith(".md"):
                input_path = os.path.join(report_dir, fname)
                try:
                    with open(input_path, 'r', encoding='utf-8') as f:
                        md_text = f.read()
                    logger.info("Processing race conditions from: %s", input_path)
                    races = report_race.extract_races(md_text)
                    if races:
                        for race in races:
                            race['source_file'] = fname
                        all_races.extend(races)
                        processed_files.append(fname)
                        logger.info("✅ Found %d race conditions in %s", len(races), fname)
                    else:
                        logger.info("ℹ️  No race conditions found in %s", fname)
                except Exception as e:
                    logger.error("❌ Error processing %s: %s", fname, e)
                    continue
        
        # 🔥 BƯỚC 3: Tạo báo cáo HTML mới hoàn toàn
        if all_races:
            report_race.write_consolidated_html_table(all_races, output_path, processed_files)
            return [types.TextContent(
                type="text", 
                text=f"🔄 Re-generated fresh race condition report with {len(all_races)} races from {len(processed_files)} files: {output_path}\n"
                    f"📊 Processed files: {', '.join(processed_files)}\n"
                    f"🗑️  Previous report deleted and regenerated from scratch"
            )]
        else:
            # Tạo file HTML trống để báo hiệu không có race condition
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("""<!DOCTYPE html>
    <html><head><meta charset="utf-8"><title>Race Condition Report - No Issues Found</title></head>
    <body>
    <h1>Race Condition Analysis Report</h1>
    <p><strong>Status:</strong> ✅ No race conditions detected</p>
    <p><strong>Files analyzed:</strong> {}</p>
    <p><strong>Generated on:</strong> {}</p>
    </body></html>""".format(len(processed_files), 
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            return [types.TextContent(
                type="text", 
                text=f"✅ No race conditions found in {len(processed_files)} processed files. Clean report generated: {output_path}"
            )]


    async def _handle_report_resource_leak(self, arguments: dict):
        """
        Quét tất cả file .md trong report_dir, tổng hợp tất cả resource leaks vào 1 file resource_leaks.html
        Luôn luôn xóa file báo cáo cũ và tạo mới để đảm bảo tính cập nhật
        """
        report_dir = os.environ.get("report_dir", "./report")
        
        # 🔥 BƯỚC 1: Xóa file HTML báo cáo cũ nếu tồn tại
        output_path = os.path.join(report_dir, "resource_leak.html")  # Số nhiều cho nhất quán
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
                logger.info("🗑️  Deleted existing resource leak report: %s", output_path)
            except Exception as e:
                logger.warning("Failed to delete existing resource leak report: %s", e)
        
        # 🔥 BƯỚC 2: Quét và phân tích lại TẤT CẢ file .md từ đầu
        all_leaks = []
        processed_files = []
        
        logger.info("🔍 Re-analyzing ALL .md files for resource leaks...")
        
        for fname in os.listdir(report_dir):
            if fname.endswith(".md"):
                input_path = os.path.join(report_dir, fname)
                try:
                    with open(input_path, 'r', encoding='utf-8') as f:
                        md_text = f.read()
                    logger.info("Processing resource leaks from: %s", input_path)
                    leaks = report_resource.extract_violations(md_text)
                    if leaks:
                        for leak in leaks:
                            leak['source_file'] = fname
                        all_leaks.extend(leaks)
                        processed_files.append(fname)
                        logger.info("✅ Found %d resource leaks in %s", len(leaks), fname)
                    else:
                        logger.info("ℹ️  No resource leaks found in %s", fname)
                except Exception as e:
                    logger.error("❌ Error processing %s: %s", fname, e)
                    continue
        
        # 🔥 BƯỚC 3: Tạo báo cáo HTML mới hoàn toàn
        if all_leaks:
            report_resource.write_consolidated_html_table(all_leaks, output_path, processed_files)
            return [types.TextContent(
                type="text", 
                text=f"🔄 Re-generated fresh resource leak report with {len(all_leaks)} leaks from {len(processed_files)} files: {output_path}\n"
                    f"📊 Processed files: {', '.join(processed_files)}\n"
                    f"🗑️  Previous report deleted and regenerated from scratch"
            )]
        else:
            # Tạo file HTML trống để báo hiệu không có resource leak
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("""<!DOCTYPE html>
    <html><head><meta charset="utf-8"><title>Resource Leak Report - No Issues Found</title></head>
    <body>
    <h1>Resource Leak Analysis Report</h1>
    <p><strong>Status:</strong> ✅ No resource leaks detected</p>
    <p><strong>Files analyzed:</strong> {}</p>
    <p><strong>Generated on:</strong> {}</p>
    </body></html>""".format(len(processed_files), 
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            return [types.TextContent(
                type="text", 
                text=f"✅ No resource leaks found in {len(processed_files)} processed files. Clean report generated: {output_path}"
            )]
        
    async def _handle_analyze_requirement(self, arguments: dict) -> List[types.TextContent]:
        """Handle analyze_requirement tool"""
        try:
            # Import hàm lấy req_dir từ config
            from lgedv.modules.config import get_req_dir

            dir_path = arguments.get("dir")
            if not dir_path:
                dir_path = get_req_dir()
                logger.info(f"[analyze_requirement] No dir parameter provided, using req_dir from config: {dir_path}")

            if not dir_path:
                return [types.TextContent(type="text", text="Error: dir_path is required and req_dir not found in config")]

            result = handle_requirement_analysis(dir_path)
            return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        except Exception as e:
            logger.error(f"Error in analyze_requirement: {e}")
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
            
    