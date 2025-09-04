"""
腾讯云 TKE MCP 服务器模块

TKE MCP服务器是一个基于Model Context Protocol (MCP) 的腾讯云容器服务（TKE）管理工具。
"""

__version__ = "0.1.0"
__author__ = "TKE MCP Server Team"
__description__ = "腾讯云容器服务(TKE) MCP服务器"

from .server import serve

def main():
    """
    命令行入口点
    """
    import asyncio
    asyncio.run(serve())

# 延迟导入以避免循环依赖
def get_server():
    """获取TKE MCP服务器实例"""
    from .server import server
    return server

def get_client():
    """获取TKE客户端工厂函数"""
    from .client import get_tke_client
    return get_tke_client

# 模块导出
__all__ = [
    "__version__",
    "__author__", 
    "__description__",
    "main",
    "get_server",
    "get_client"
]
