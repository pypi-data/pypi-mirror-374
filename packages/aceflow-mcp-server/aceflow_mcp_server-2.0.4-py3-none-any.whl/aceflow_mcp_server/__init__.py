"""AceFlow MCP Server

AI-driven workflow management through Model Context Protocol.
"""

__version__ = "2.0.4"
__author__ = "AceFlow Team"
__email__ = "team@aceflow.dev"

# Import only the essentials to avoid dependency issues
try:
    from .server import AceFlowMCPServer
    __all__ = ["AceFlowMCPServer"]
except ImportError:
    # Fall back to core functionality only
    __all__ = []