"""
API context extraction handler
Xử lý việc trích xuất context từ các API directories đã detect
"""

import logging
from typing import List, Dict, Any
from mcp import types
from lgedv.modules.api_detector import APIDetector

logger = logging.getLogger(__name__)

class APIContextHandler:
    """Handler for extracting API context"""
    
    def __init__(self, tool_handler=None):
        self.tool_handler = tool_handler
        self.api_detector = APIDetector()
    
    async def extract_configured_apis_context(self) -> str:
        """Extract API context from configured base directories"""
        # Detect all APIs
        found_apis = self.api_detector.detect_all_apis()
        
        if not found_apis:
            return self.api_detector.create_detection_summary(found_apis)
        
        # Extract context from found APIs (limit to top 6 to avoid token overflow)
        context_sections = []
        for api_info in found_apis[:6]:
            api_path = api_info['path']
            try:
                result = await self.tool_handler._handle_get_src_context({"dir": api_path})
                if result and result[0].text:
                    confidence_emoji = "🔥" if api_info['confidence'] == 'high' else "🟡"
                    context_sections.append(
                        f"## {confidence_emoji} API Context: {api_path}\n"
                        f"**Source**: {api_info['type']} from `{api_info.get('base_dir', 'unknown')}`\n"
                        f"{result[0].text}"
                    )
            except Exception as e:
                logger.warning(f"Failed to extract context from {api_path}: {e}")
        
        # Create final result
        summary = self.api_detector.create_detection_summary(found_apis)
        
        if context_sections:
            return summary + "\n\n" + "\n\n".join(context_sections)
        else:
            return summary + "\n\n**Note**: No context could be extracted from detected APIs."
    
    async def extract_manual_apis_context(self, api_modules: List[str]) -> str:
        """Extract API context from user-specified modules"""
        context_sections = []
        
        for module_path in api_modules:
            try:
                result = await self.tool_handler._handle_get_src_context({"dir": module_path})
                if result and result[0].text:
                    context_sections.append(f"## 🎯 User-Specified API: {module_path}\n{result[0].text}")
            except Exception as e:
                context_sections.append(f"## ❌ Error extracting {module_path}: {e}")
        
        return "\n\n".join(context_sections)