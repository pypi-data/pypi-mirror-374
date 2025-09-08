"""
Configuration module for LGEDV MCP Server
Quản lý tất cả các cấu hình và đường dẫn
"""
import os
import sys
import json
import logging
from pydantic import FileUrl
import mcp.types as types

# Thiết lập cấu hình logging
def setup_logging():
    """Setup logging configuration"""
    log_path = os.path.join(os.getcwd(), "mcp_simple_prompt.log")
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(sys.stderr),
            # logging.FileHandler(log_path) # disable file logging, uncomment to enable
        ]
    )
    return logging.getLogger(__name__)

# Load MCP configuration
def load_mcp_config():
    config = {}
    possible_paths = [
        os.path.join(os.getcwd(), "mcp.json"),
        os.path.join(os.path.dirname(__file__), "..", "..", "mcp.json"),
        os.path.join(os.path.expanduser("~"), ".vscode", "mcp.json"),
    ]
    for config_path in possible_paths:
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    data = json.load(f)
                    if "servers" in data and "lgedv" in data["servers"]:
                        server_config = data["servers"]["lgedv"]
                        if "env" in server_config:
                            config.update(server_config["env"])
                    break
            except Exception as e:
                logging.getLogger(__name__).error(f"Error loading {config_path}: {e}")
                continue
    return config

_mcp_config = load_mcp_config()

def get_config_value(key, default=None):
    # Ưu tiên biến môi trường, sau đó mcp.json, cuối cùng là default
    if os.environ.get(key):
        return os.environ.get(key)
    if key in _mcp_config:
        return _mcp_config[key]
    return default

def is_premium():
    val = get_config_value("premium", False)
    if isinstance(val, str):
        return val.lower() == "true"
    return bool(val)

# Đặt BASE_DIR là thư mục chứa file server.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Đường dẫn đến các file rule
RULE_PATHS = {
    "misra_cpp": os.path.join(BASE_DIR, "resources", "Misracpp2008Guidelines_en.md"),
    "lgedv": os.path.join(BASE_DIR, "resources", "LGEDVRuleGuide.md"),
    "lge_static": os.path.join(BASE_DIR, "resources", "StaticAnalysis.md"),
    "certcpp": os.path.join(BASE_DIR, "resources", "CertcppGuidelines_en.md"),
    "autosar": os.path.join(BASE_DIR, "resources", "AutosarCpp14RuleGuide.md"),
    "misra_c": os.path.join(BASE_DIR, "resources", "MisraC2023RuleGuide.md"),
    "custom": get_config_value("custom_path", os.path.join(BASE_DIR, "resources", "CustomRule.md"))
}

# Legacy compatibility
MISRA_CPP_RULE_URL = RULE_PATHS["misra_cpp"]
LGEDV_RULE_URL = RULE_PATHS["lgedv"]
CERTCPP_RULE_URL = RULE_PATHS["certcpp"]
AUTOSAR_RULE_URL = RULE_PATHS["autosar"]
MISRA_C_RULE_URL = RULE_PATHS["misra_c"]
CUSTOM_RULE_URL = RULE_PATHS["custom"]

RESOURCE_FILES = RULE_PATHS

def get_src_dir():
    """Get the CPP directory from environment or mcp.json or current working directory"""
    return get_config_value("src_dir", os.getcwd())

def get_req_dir():
    """Get the requirements directory from environment or mcp.json"""
    return get_config_value("req_dir")

def get_api_base_dirs():
    """Get the API base directories from environment or mcp.json"""
    return get_config_value("api_base_dirs")

def get_module_api():
    """Get the module API directory from environment or mcp.json"""
    return get_config_value("module_api")

def get_framework_dir():
    """Get the framework directory from environment or mcp.json"""
    return get_config_value("framework_dir")

def get_report_dir():
    """Get the report directory from environment or mcp.json"""
    return get_config_value("report_dir")


def get_prompt_lang():
    """Get prompt language from config"""
    return get_config_value("prompt_lang", "en")