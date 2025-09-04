"""
AppCan Helper MCP Package

提供 AppCan 官方文档查询功能的 MCP 服务器
"""

__version__ = "1.0.0"
__author__ = "zhangyipeng"
__email__ = "sandy1108@163.com"

from .server import mcp, main

__all__ = ["mcp", "main"]
