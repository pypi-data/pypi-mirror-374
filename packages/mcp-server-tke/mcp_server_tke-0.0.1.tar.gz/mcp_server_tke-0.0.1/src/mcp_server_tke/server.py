"""
腾讯云 TKE 服务主模块
"""
import logging
from typing import Any
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
from . import tool_tke

# 设置日志记录
logger = logging.getLogger(__name__)

# 创建TKE MCP服务器实例
server = Server("tke")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """处理工具列表请求，返回TKE可用的工具"""
    return [
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
        types.Tool(
            name="DeleteCluster",
            description="删除TKE集群",
            inputSchema={
                "type": "object",
                "properties": {
                    "ClusterId": {
                        "type": "string",
                        "description": "集群ID，必须输入"
                    }
                },
                "required": ["ClusterId"],
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict[str, Any] | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """处理工具调用请求"""
    try:
        logger.info(f"处理工具调用: {name}, 参数: {arguments}")
        
        if arguments is None:
            arguments = {}
        
        if name == "CreateCluster":
            result = tool_tke.create_cluster(arguments)
        elif name == "DeleteCluster":
            result = tool_tke.delete_cluster(arguments)
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
