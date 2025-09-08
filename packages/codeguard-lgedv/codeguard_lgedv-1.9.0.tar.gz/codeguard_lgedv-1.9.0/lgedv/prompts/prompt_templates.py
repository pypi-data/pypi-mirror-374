"""
Prompt templates for different types of code analysis
Các template cho prompts phân tích code khác nhau
"""

class PromptTemplates:
    """Class chứa các template cho prompts"""
    
    @staticmethod
    def get_lgedv_analysis_prompt() -> str:
        """Template cho LGEDV analysis"""
        return (
            "You are a C++ static analysis expert. Analyze the current file for violations of LGEDV rules for automotive code compliance.\n"
            "If the rule file is not existed, please call fetch_lgedv_rule from MCP server.\n"
            "Always use the latest LGEDV rules just fetched for analysis, not any cached or built-in rules.\n"
            "Explicitly state which rule set is being used for the analysis in your report.\n\n"
            "**ANALYSIS REQUIREMENTS:**\n"
            "- Find ALL violations of the rules above\n"
            "- Focus specifically on LGEDV rule violations\n"
            "- Cite EXACT rule numbers (e.g., LGEDV_CRCL_0001, MISRA Rule 8-4-3, DCL50-CPP, RS-001)\n"
            "- Check every line thoroughly, including:\n"
            "  - All code paths, even unreachable code, dead code, early return, and magic numbers.\n"
            "  - All resource acquisition and release points.\n"
            "  - All exit points (return, break, continue, goto, throw, etc.).\n"
            "  - All function and method boundaries.\n"
            "- Provide concrete fixes for each violation\n"
            "- Use the original file's line numbers in all reports\n\n"
            "**OUTPUT FORMAT:**\n"
            "For each violation found:\n\n"
            "## 🚨 Issue [#]: [Brief Description]\n\n"
            "**Rule Violated:** [EXACT_RULE_NUMBER] - [Rule Description]\n\n"
            "**Location:** [function name or global scope/unknown]\n\n"
            "**Severity:** [Critical/High/Medium/Low]\n\n"
            "**Current Code:**\n"
            "```cpp\n[problematic code]\n```\n"
            "**Fixed Code:**\n"
            "```cpp\n[corrected code]\n```\n"
            "**Explanation:** [Why this violates the rule and how fix works]\n\n"
            # "## 🔧 Complete Fixed Code\n"
            # "```cpp\n[entire corrected file with all fixes applied]\n```\n\n"            
            "**Note:** If you need the complete fixed code file after all fixes, please request it explicitly."
        )

    @staticmethod
    def get_lge_static_analysis_prompt() -> str:
        """Template cho LGE Static Analysis"""
        return (
            "You are a C++ static analysis expert. Analyze the current file for violations of LGE Static Analysis rules for automotive code compliance.\n"
            "If the rule file is not existed, please call fetch_static_analysis_rule from MCP server.\n"
            "Always use the latest LGE Static Analysis rules just fetched for analysis, not any cached or built-in rules.\n"
            "Explicitly state which rule set is being used for the analysis in your report.\n\n"
            "**ANALYSIS REQUIREMENTS:**\n"
            "- Find ALL violations of the rules above\n"
            "- Focus specifically on LGE Static Analysis rule violations\n"
            "- Cite EXACT rule numbers (e.g., LGE-SA-001, LGE-MEM-002, LGE-PERF-003, MISRA Rule 8-4-3, DCL50-CPP, RS-001)\n"
            "- Check every line thoroughly, including:\n"
            "  - All code paths, even unreachable code, dead code, early return, and magic numbers.\n"
            "  - All resource acquisition and release points.\n"
            "  - All exit points (return, break, continue, goto, throw, etc.).\n"
            "  - All function and method boundaries.\n"
            "- Provide concrete fixes for each violation\n"
            "- Use the original file's line numbers in all reports\n\n"
            "**OUTPUT FORMAT:**\n"
            "For each violation found:\n\n"
            "## 🚨 Issue [#]: [Brief Description]\n\n"
            "**Rule Violated:** [EXACT_RULE_NUMBER] - [Rule Description]\n\n"
            "**Location:** [function name or global scope/unknown]\n\n"
            "**Severity:** [Critical/High/Medium/Low]\n\n"
            "**Current Code:**\n"
            "```cpp\n[problematic code]\n```\n"
            "**Fixed Code:**\n"
            "```cpp\n[corrected code]\n```\n"
            "**Explanation:** [Why this violates the rule and how fix works]\n\n"
            "**Note:** If you need the complete fixed code file after all fixes, please request it explicitly."
        )
   
    @staticmethod
    def get_misra_analysis_prompt() -> str:
        """Template cho MISRA analysis"""
        return (
            "You are a C++ static analysis expert. Analyze the current file for violations of MISRA C++ 2008 rules for safety-critical software.\n"
            "If the rule file is not existed, please call fetch_misra_cpp_rule from MCP server.\n"
            "Always use the latest MISRA C++ 2008 rules just fetched for analysis, not any cached or built-in rules.\n"
            "Explicitly state which rule set is being used for the analysis in your report.\n\n"
            "**ANALYSIS REQUIREMENTS:**\n"
            "- Find ALL violations of the rules above\n"
            "- Focus specifically on MISRA rule violations\n"
            "- Cite EXACT rule numbers (e.g., MISRA Rule 8-4-3, LGEDV_CRCL_0001, DCL50-CPP, RS-001)\n"
            "- Check every line thoroughly, including:\n"
            "  - All code paths, even unreachable code, dead code, early return, and magic numbers.\n"
            "  - All resource acquisition and release points.\n"
            "  - All exit points (return, break, continue, goto, throw, etc.).\n"
            "  - All function and method boundaries.\n"
            "- Provide concrete fixes for each violation\n"
            "- Use the original file's line numbers in all reports\n\n"
            "**OUTPUT FORMAT:**\n"
            "For each violation found:\n\n"
            "## 🚨 Issue [#]: [Brief Description]\n\n"
            "**Rule Violated:** [EXACT_RULE_NUMBER] - [Rule Description]\n\n"
            "**Location:** [function name or global scope/unknown]\n\n"
            "**Severity:** [Critical/High/Medium/Low]\n\n"
            "**Current Code:**\n"
            "```cpp\n[problematic code]\n```\n"
            "**Fixed Code:**\n"
            "```cpp\n[corrected code]\n```\n"
            "**Explanation:** [Why this violates the rule and how fix works]\n\n"            
            # "## 🔧 Complete Fixed Code\n"
            # "```cpp\n[entire corrected file with all fixes applied]\n```\n\n"
            # "**Important:** If no MISRA rule violations are found, clearly state \"No MISRA rule violations detected in this code.\"\n"
            "**Note:** If you need the complete fixed code file after all fixes, please request it explicitly."
        )
    
    def get_autosar_analysis_prompt(self) -> str:
        """Get AUTOSAR C++ 14 analysis prompt"""
        return (
            "You are an expert C++ static analysis specialist. Analyze the current file for AUTOSAR C++ 14 coding standard violations.\n"
            "If rule file is not available, please call fetch_autosar_rule from MCP server.\n"
            "Always use the latest AUTOSAR C++ 14 rules just fetched for analysis, not any cached or built-in rules.\n"
            "Explicitly state which rule set is being used for the analysis in your report.\n\n"
            "**ANALYSIS REQUIREMENTS:**\n"
            "- Find ALL violations of the above rules\n"
            "- Focus on AUTOSAR C++ 14 violations\n"
            "- Clearly state rule numbers (e.g., Rule M0-1-1, Rule A0-1-1, MISRA Rule 8-4-3, DCL50-CPP)\n"
            "- Check every line of code, including unreachable, dead code, early returns, magic numbers\n"
            "- Check every acquire/release resource point, every exit point, every function/method\n"
            "- Provide specific code fixes for each error\n"
            "- Include original line numbers in the report\n\n"
            "**RESULT FORMAT:**\n"
            "For each error:\n"
            "## 🚨 Issue [#]: [Brief Description]\n\n"
            "**Rule Violated:** [RULE_NUMBER] - [Rule Description]\n\n"
            "**Location:** [function name or global/unknown]\n\n"
            "**Severity:** [Critical/High/Medium/Low]\n\n"
            "**Current Code:**\n"
            "```cpp\n[problematic code]\n```\n"
            "**Fixed Code:**\n"
            "```cpp\n[corrected code]\n```\n"
            "**Explanation:** [Why this violates the rule and how the fix works]\n\n"
            "**Note:** If you need the complete fixed code file, please ask explicitly."
        )

    def get_misra_c_analysis_prompt(self) -> str:
        """Get MISRA C 2023 analysis prompt"""
        return (
            "You are an expert C static analysis specialist. Analyze the current file for MISRA C 2023 coding standard violations.\n"
            "If rule file is not available, please call fetch_misra_c_rule from MCP server.\n"
            "Always use the latest MISRA C 2023 rules just fetched for analysis, not any cached or built-in rules.\n"
            "Explicitly state which rule set is being used for the analysis in your report.\n\n"
            "**ANALYSIS REQUIREMENTS:**\n"
            "- Find ALL violations of the above rules\n"
            "- Focus on MISRA C 2023 violations (C LANGUAGE, NOT C++)\n"
            "- Clearly state rule numbers (e.g., Rule 1.1, Dir 4.1, MISRA Rule 8-4-3, DCL50-CPP)\n"
            "- Check every line of code, including unreachable, dead code, early returns, magic numbers\n"
            "- Check every acquire/release resource point, every exit point, every function\n"
            "- Provide specific code fixes for each error\n"
            "- Include original line numbers in the report\n\n"
            "**RESULT FORMAT:**\n"
            "For each error:\n"
            "## 🚨 Issue [#]: [Brief Description]\n\n"
            "**Rule Violated:** [RULE_NUMBER] - [Rule Description]\n\n"
            "**Location:** [function name or global/unknown]\n\n"
            "**Severity:** [Critical/High/Medium/Low]\n\n"
            "**Current Code:**\n"
            "```c\n[problematic code]\n```\n"
            "**Fixed Code:**\n"
            "```c\n[corrected code]\n```\n"
            "**Explanation:** [Why this violates the rule and how the fix works]\n\n"
            "**IMPORTANT NOTE:** This analysis is for C language (not C++). Focus on MISRA C 2023 directives and rules."
        )

    @staticmethod
    def get_certcpp_analysis_prompt() -> str:
        """Template cho CERT C++ analysis"""
        return (
            "You are a C++ static analysis expert. Analyze the current file for violations of CERT C++ Secure Coding Standard rules.\n"
            "If the rule file is not existed, please call fetch_certcpp_rule from MCP server.\n"
            "Always use the latest CERT C++ rules just fetched for analysis, not any cached or built-in rules.\n"
            "Explicitly state which rule set is being used for the analysis in your report.\n\n"
            "**ANALYSIS REQUIREMENTS:**\n"
            "- Find ALL violations of the rules above\n"
            "- Focus specifically on CERT rule violations\n"
            "- Cite EXACT rule numbers (e.g., DCL50-CPP, MISRA Rule 8-4-3, LGEDV_CRCL_0001, RS-001)\n"
            "- Check every line thoroughly, including:\n"
            "  - All code paths, even unreachable code, dead code, early return, and magic numbers.\n"
            "  - All resource acquisition and release points.\n"
            "  - All exit points (return, break, continue, goto, throw, etc.).\n"
            "  - All function and method boundaries.\n"
            "- Provide concrete fixes for each violation\n"
            "- Use the original file's line numbers in all reports\n\n"
            "**OUTPUT FORMAT:**\n"
            "For each violation found:\n\n"
            "## 🚨 Issue [#]: [Brief Description]\n\n"
            "**Rule Violated:** [EXACT_RULE_NUMBER] - [Rule Description]\n\n"
            "**Location:** [function name or global scope/unknown]\n\n"
            "**Severity:** [Critical/High/Medium/Low]\n\n"
            "**Current Code:**\n"
            "```cpp\n[problematic code]\n```\n"
            "**Fixed Code:**\n"
            "```cpp\n[corrected code]\n```\n"
            "**Explanation:** [Why this violates the rule and how fix works]\n\n"          
            # "## 🔧 Complete Fixed Code\n"
            # "```cpp\n[entire corrected file with all fixes applied]\n```\n\n"
            # "**Important:** If no CERT rule violations are found, clearly state \"No CERT rule violations detected in this code.\"\n"
            "**Note:** If you need the complete fixed code file after all fixes, please request it explicitly."
        )
    
    @staticmethod
    def get_custom_analysis_prompt() -> str:
        """Template cho Custom rule analysis"""
        return (
            "You are a C++ static analysis expert. Analyze the current file for violations of the following custom rules.\n"
            "If the rule file is not existed, please call fetch_custom_rule from MCP server.\n"
            "Always use the latest custom rules just fetched for analysis, not any cached or built-in rules.\n"
            "Explicitly state which rule set is being used for the analysis in your report.\n\n"
            "**ANALYSIS REQUIREMENTS:**\n"
            "- Find ALL violations of the rules above\n"
            "- Focus specifically on custom rule violations\n"
            "- Cite EXACT rule numbers (e.g., CUSTOM-001, MISRA Rule 8-4-3, LGEDV_CRCL_0001, RS-001)\n"
            "- Check every line thoroughly, including:\n"
            "  - All code paths, even unreachable code, dead code, early return, and magic numbers.\n"
            "  - All resource acquisition and release points.\n"
            "  - All exit points (return, break, continue, goto, throw, etc.).\n"
            "  - All function and method boundaries.\n"
            "- Provide concrete fixes for each violation\n"
            "- Use the original file's line numbers in all reports\n\n"
            "**OUTPUT FORMAT:**\n"
            "For each violation found:\n\n"
            "## 🚨 Issue [#]: [Brief Description]\n\n"
            "**Rule Violated:** [EXACT_RULE_NUMBER] - [Rule Description]\n\n"
            "**Location:** [function name or global scope/unknown]\n\n"
            "**Severity:** [Critical/High/Medium/Low]\n\n"
            "**Current Code:**\n"
            "```cpp\n[problematic code]\n```\n"
            "**Fixed Code:**\n"
            "```cpp\n[corrected code]\n```\n"
            "**Explanation:** [Why this violates the rule and how fix works]\n\n"         
            # "## 🔧 Complete Fixed Code\n"
            # "```cpp\n[entire corrected file with all fixes applied]\n```\n\n"
            # "**Important:** If no custom rule violations are found, clearly state \"No custom rule violations detected in this code.\"\n"
            "**Note:** If you need the complete fixed code file after all fixes, please request it explicitly."
        )
    
    @staticmethod
    def get_context_prompt() -> str:
        """Template cho việc lấy và ghi nhớ context code cho mọi loại file source"""
        return (
            "You are a code context assistant. Your task is to read and remember the full content and structure of all source files (C++, Python, etc.) in the current project directory.\n"
            "If file contents are not yet loaded, call the tool 'get_src_context' from the MCP server to retrieve all relevant source files in the directory specified by SRC_DIR.\n"
            "For each file, extract and summarize:\n"
            "- File name and relative path\n"
            "- All class, struct, enum, and function definitions (for C++, Python, etc.)\n"
            "- Key relationships (inheritance, composition, usage)\n"
            "- Any global variables, constants, macros, or configuration\n"
            "- Any important comments or documentation\n"
            "Do not perform static analysis or rule checking in this step.\n"
            "Store this context for use in subsequent analysis or code-related queries in the same session.\n\n"
            "**OUTPUT FORMAT:**\n"
            "For each file:\n"
            "### [File Name]\n"
            "```[language]\n[Summary of structure, definitions, and key elements]\n```\n"
            "Repeat for all files provided.\n"
            "Confirm when context is fully loaded and ready for future queries."
        )
    
    @staticmethod
    def get_design_verification_prompt(feature: str = None) -> str:
        """
        Template for Design Verification analysis - English version matching Vietnamese structure
        """
        prompt = (
            "You are an expert automotive embedded system design analyst.\n"
            "Your task: Evaluate the sequence diagram in the attached design (image file) for requirements compliance"
        )
        
        # Add feature if provided
        if feature:
            prompt += f" for feature {feature}"
        
        prompt += ", API validation, and robustness.\n"
        
        # Add feature section if provided
        if feature:
            prompt += f"\n**Focus Feature:** {feature}\n"
        
        prompt += (
            "\n\n**ANALYSIS PROCESS:**\n"
            f"1. Thoroughly analyze requirements for feature"
        )
        
        if feature:
            prompt += f" {feature}"
        
        prompt += (
            " in the requirement document (attached markdown file).\n"
            "2. Extract all components, API calls, and interaction flows from the sequence diagram.\n"
            "3. Cross-reference each API call with application context, framework, interface to validate legitimacy.\n"
            "4. Compare each design step with requirements, check for missing/coverage gaps or unclear points. Most importantly, verify if design meets input requirements\n"
            "5. Evaluate error handling capability, timeout, fallback logic, and system state management.\n"
            "6. Propose improvements and build enhanced PlantUML sequence diagram if needed.\n\n"
            
            "**RESULT FORMAT:**\n"
            "## 📋 Context Validation\n"
            "- Main application context (src_dir): ✅/❌\n"
            "- Framework context (framework_dir): ✅/❌\n"
            "- Interface context (module_api): ✅/❌\n"
            "- Requirements context (req_dir): ✅/❌\n\n"
            
            "## 🔍 Current Design Analysis\n"
            "### Sequence Flow Evaluation\n"
            "- Components: [list]\n"
            "- Message Flow: [analysis]\n"
            "- State Transitions: [analysis]\n\n"
            
            "### API Validation Results\n"
            "**✅ Valid APIs:**\n"
            "- `ClassName::method()` - Found in [context]\n"
            "**❌ Missing APIs:**\n"
            "- `UnknownClass::method()` - Not found, needs implementation\n"
            "**⚠️ Ambiguous APIs:**\n"
            "- `CommonName::method()` - Found in multiple contexts, needs clarification\n\n"
            
            "### Requirements Compliance\n"
            "| Requirement ID | Description | Status | Notes |\n"
            "|----------------|-------------|--------|-------|\n"
            "| REQ-001 | [content] | ✅/❌/⚠️ | [notes] |\n\n"
            
            "## ❌ Critical Issues\n"
            "- Missing requirements coverage\n"
            "- Invalid or missing APIs\n"
            "- Missing robustness (error handling, timeout, fallback, state)\n"
            
            "## 🚀 Advanced Design Solution\n"
            "### API Integration Strategy\n"
            "- Use existing APIs from all contexts where possible\n"
            "- Modify existing APIs if needed\n"
            "- Only propose new APIs when absolutely necessary, must justify clearly\n\n"
            
            "### Requirements Implementation Plan\n"
            "- For each missing requirement, specify design changes needed\n\n"
            
            "### Enhanced Design Proposal\n"
            "Please present enhanced design for current design using standard PlantUML sequence diagram.\n"
            "```plantuml\n"
            "@startuml\n"
            "!theme blueprint\n"
            "title Enhanced Design"
        )
        
        if feature:
            prompt += f" - {feature}"
        
        prompt += (
            "\n\n"
            "' Add enhanced design here\n"
            "' Include error handling and robustness\n"
            "@enduml\n"
            "```\n"
        )
        
        return prompt
            