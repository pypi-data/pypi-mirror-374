"""
腾讯云 TKE 服务主模块
"""
import os
import logging
from typing import Any
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
from . import tool_tke
from .mcpapi_loader import McpAPILoader
from .dynamic_tool_handler import DynamicToolHandler

# 设置日志记录
logger = logging.getLogger(__name__)

# 创建TKE MCP服务器实例
server = Server("tke")

# 全局变量存储动态工具处理器
dynamic_tool_handler = None

def _initialize_dynamic_tools():
    """初始化动态工具处理器"""
    global dynamic_tool_handler
    
    try:
        logger.info("开始初始化动态工具处理器")
        
        # 加载McpAPI文件，取代码同级目录下的mcpapi目录
        mcpapi_dir = os.path.join(os.path.dirname(__file__), "mcpapi")
        mcpapi_loader = McpAPILoader(mcpapi_dir)
        mcpapi_data = mcpapi_loader.load_mcpapi_files()
        
        # 创建动态工具处理器
        dynamic_tool_handler = DynamicToolHandler(mcpapi_data)
        
        # 构建工具缓存
        dynamic_tool_handler.generate_mcp_tools()
        
        logger.info("动态工具处理器初始化完成")
        
    except Exception as e:
        logger.warning(f"动态工具处理器初始化失败：{str(e)}")
        # 即使初始化失败，也继续运行，只是没有动态工具
        dynamic_tool_handler = None

# 在模块加载时初始化动态工具
_initialize_dynamic_tools()

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """处理工具列表请求，返回TKE可用的工具"""
    # 静态工具列表（保持现有功能）
    static_tools = [
        types.Tool(
            name="CreateCluster",
            description="创建TKE集群",
            inputSchema={
                "type": "object",
                "properties": {
                    "ClusterBasicSettings.ClusterName": {
                        "type": "string",
                        "description": "集群名称，可选参数"
                    },
                    "ClusterBasicSettings.ClusterLevel": {
                        "type": "string",
                        "description": "集群规格(L5、L50、L200、L1000、L5000)，默认L50",
                        "enum": ["L5", "L50", "L200", "L1000", "L5000"],
                        "default": "L50"
                    },
                    "Region": {
                        "type": "string",
                        "description": "地域(ap-guangzhou、ap-beijing、ap-shanghai)",
                        "enum": ["ap-guangzhou", "ap-beijing", "ap-shanghai"]
                    },
                    "ClusterBasicSettings.ClusterOs": {
                        "type": "string",
                        "description": "操作系统镜像ID，必须输入"
                    },
                    "ClusterBasicSettings.VpcId": {
                        "type": "string",
                        "description": "私有网络ID，必须输入"
                    },
                    "ClusterCIDRSettings.EniSubnetIds": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "子网ID集合，必须输入"
                    },
                    "ClusterCIDRSettings.ServiceCIDR": {
                        "type": "string",
                        "description": "Service CIDR，必须输入"
                    }
                },
                "required": [
                    "Region",
                    "ClusterBasicSettings.ClusterOs",
                    "ClusterBasicSettings.VpcId",
                    "ClusterCIDRSettings.EniSubnetIds",
                    "ClusterCIDRSettings.ServiceCIDR"
                ],
            },
        ),
    ]
    
    # 添加动态工具（如果动态工具处理器可用）
    tools = static_tools.copy()
    if dynamic_tool_handler is not None:
        try:
            dynamic_tools = dynamic_tool_handler.generate_mcp_tools()
            tools.extend(dynamic_tools)
            logger.info(f"添加了 {len(dynamic_tools)} 个动态工具")
        except Exception as e:
            logger.warning(f"获取动态工具失败：{str(e)}")
    
    return tools

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict[str, Any] | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """处理工具调用请求"""
    try:
        logger.info(f"处理工具调用: {name}, 参数: {arguments}")
        
        if arguments is None:
            arguments = {}
        
        # 首先尝试静态工具（保持现有功能）
        if name == "CreateCluster":
            result = tool_tke.create_cluster(arguments)
        else:
            # 尝试动态工具
            if dynamic_tool_handler is not None:
                try:
                    result = dynamic_tool_handler.handle_tool_call(name, arguments)
                except Exception as e:
                    # 如果动态工具也失败，抛出未知工具错误
                    if "未知的工具" in str(e) or "Unknown tool" in str(e):
                        raise ValueError(f"未知的工具: {name}")
                    else:
                        # 如果是其他错误，重新抛出
                        raise
            else:
                raise ValueError(f"未知的工具: {name}")
            
        logger.info(f"工具调用成功: {name}")
        return [types.TextContent(type="text", text=str(result))]
        
    except Exception as e:
        error_msg = f"错误: {str(e)}"
        logger.error(f"工具调用失败 {name}: {error_msg}")
        return [types.TextContent(type="text", text=error_msg)]

async def serve():
    """启动TKE MCP服务"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        logger.info("TKE MCP Server running with stdio transport")
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="tke",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
