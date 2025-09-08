"""
Interface API extraction tool for MCP server
Scan all subfolders named 'interface' under the given dir and extract API definitions (.h, .hpp, .cpp)
"""

import os
import re
from typing import Dict, List

def get_interface(dir_path: str) -> Dict[str, List[str]]:
    """
    Scan all subfolders named 'interface' under dir_path and extract API definitions from .h, .hpp, .cpp files.
    Returns a dict: {module_name: [api_signatures]}
    """
    api_map = {}
    func_decl_pattern = r'(virtual\s+)?[\w:<>&*\s]+\s+\w+\s*\([^;{)]*\)\s*;'
    func_def_pattern = r'^[\w:<>&*\s]+\s+\w+\s*\([^)]*\)\s*{'
    for root, dirs, files in os.walk(dir_path):
        for d in dirs:
            if d.lower() == "interface":
                interface_dir = os.path.join(root, d)
                module_name = os.path.basename(root)
                api_map[module_name] = []
                for f in os.listdir(interface_dir):
                    if f.endswith(('.h', '.hpp')):
                        file_path = os.path.join(interface_dir, f)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as file:
                                content = file.read()
                                # Lấy các khai báo hàm (thường là API public)
                                for match in re.findall(func_decl_pattern, content, re.MULTILINE):
                                    api_map[module_name].append(match.strip())
                        except Exception as e:
                            api_map[module_name].append(f"// Error reading {file_path}: {e}")
                    elif f.endswith('.cpp'):
                        file_path = os.path.join(interface_dir, f)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as file:
                                content = file.read()
                                # Lấy các định nghĩa hàm (function definitions)
                                for match in re.findall(func_def_pattern, content, re.MULTILINE):
                                    api_map[module_name].append(match.strip())
                        except Exception as e:
                            api_map[module_name].append(f"// Error reading {file_path}: {e}")
    return api_map