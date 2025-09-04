"""
TKE MCP服务器集成测试
"""
import asyncio
import json
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# 添加src路径以便导入模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    # 尝试导入MCP相关模块，如果失败则跳过测试
    import mcp.types as types
    from mcp.server import Server
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False


class TestTKEMCPServer(unittest.TestCase):
    """TKE MCP服务器集成测试类"""

    def setUp(self):
        """测试前设置"""
        if not MCP_AVAILABLE:
            self.skipTest("MCP库未安装")

    def test_server_initialization(self):
        """测试服务器初始化"""
        try:
            from mcp_server_tke.server import server
            self.assertIsInstance(server, Server)
            self.assertEqual(server.name, "tke")
        except ImportError:
            self.skipTest("MCP依赖未安装，跳过服务器初始化测试")

    @unittest.skipUnless(MCP_AVAILABLE, "MCP not available")
    def test_list_tools_schema(self):
        """测试工具列表定义的Schema正确性"""
        try:
            from mcp_server_tke.server import handle_list_tools
            
            # 运行异步函数
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                tools = loop.run_until_complete(handle_list_tools())
            finally:
                loop.close()
            
            # 验证工具数量
            self.assertEqual(len(tools), 2)
            
            # 验证CreateCluster工具
            create_tool = next((t for t in tools if t.name == "CreateCluster"), None)
            self.assertIsNotNone(create_tool)
            self.assertEqual(create_tool.description, "创建TKE集群")
            
            # 验证CreateCluster的Schema
            schema = create_tool.inputSchema
            self.assertEqual(schema["type"], "object")
            self.assertIn("properties", schema)
            self.assertIn("required", schema)
            
            # 验证必填参数
            required_fields = schema["required"]
            expected_required = [
                "Region",
                "ClusterBasicSettings.ClusterOs",
                "ClusterBasicSettings.VpcId",
                "ClusterCIDRSettings.EniSubnetIds",
                "ClusterCIDRSettings.ServiceCIDR"
            ]
            for field in expected_required:
                self.assertIn(field, required_fields)
            
            # 验证Region枚举值
            region_prop = schema["properties"]["Region"]
            self.assertEqual(region_prop["type"], "string")
            self.assertIn("enum", region_prop)
            self.assertEqual(set(region_prop["enum"]), {"ap-guangzhou", "ap-beijing", "ap-shanghai"})
            
            # 验证ClusterLevel枚举值和默认值
            cluster_level_prop = schema["properties"]["ClusterBasicSettings.ClusterLevel"]
            self.assertEqual(cluster_level_prop["type"], "string")
            self.assertIn("enum", cluster_level_prop)
            self.assertEqual(set(cluster_level_prop["enum"]), {"L5", "L50", "L200", "L1000", "L5000"})
            self.assertEqual(cluster_level_prop["default"], "L50")
            
            # 验证DeleteCluster工具
            delete_tool = next((t for t in tools if t.name == "DeleteCluster"), None)
            self.assertIsNotNone(delete_tool)
            self.assertEqual(delete_tool.description, "删除TKE集群")
            
            # 验证DeleteCluster的Schema
            delete_schema = delete_tool.inputSchema
            self.assertEqual(delete_schema["type"], "object")
            self.assertIn("ClusterId", delete_schema["properties"])
            self.assertEqual(delete_schema["required"], ["ClusterId"])
            
        except ImportError:
            self.skipTest("MCP依赖未安装，跳过工具列表测试")

    @unittest.skipUnless(MCP_AVAILABLE, "MCP not available")
    def test_call_tool_create_cluster(self):
        """测试CreateCluster工具调用"""
        try:
            from mcp_server_tke.server import handle_call_tool
            
            # 准备有效参数
            arguments = {
                "Region": "ap-guangzhou",
                "ClusterBasicSettings.ClusterName": "mcp-cluster",
                "ClusterBasicSettings.ClusterLevel": "L5",
                "ClusterBasicSettings.ClusterOs": "tlinux3.1x86_64",
                "ClusterBasicSettings.VpcId": "vpc-l51ixsi7",
                "ClusterCIDRSettings.EniSubnetIds": ["subnet-0jkfc3dk"],
                "ClusterCIDRSettings.ServiceCIDR": "192.168.0.0/17"
            }
            
            # 运行异步函数
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(handle_call_tool("CreateCluster", arguments))
            finally:
                loop.close()
            
            # 验证返回结果
            self.assertEqual(len(result), 1)
            self.assertIsInstance(result[0], types.TextContent)
            
            # 验证响应格式
            response_text = result[0].text
            response = json.loads(response_text)
            self.assertIn("ClusterId", response)
            self.assertIn("RequestId", response)

            """测试DeleteCluster工具调用"""

            # 准备有效参数
            arguments = {
                "ClusterId": response["ClusterId"]
            }
            
            # 运行异步函数
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(handle_call_tool("DeleteCluster", arguments))
            finally:
                loop.close()
            
            # 验证返回结果
            self.assertEqual(len(result), 1)
            self.assertIsInstance(result[0], types.TextContent)
            
            # 验证响应格式
            response_text = result[0].text
            response = json.loads(response_text)
            self.assertIn("RequestId", response)
            
        except ImportError:
            self.skipTest("MCP依赖未安装，跳过CreateCluster调用测试")

    @unittest.skipUnless(MCP_AVAILABLE, "MCP not available")
    def test_call_tool_invalid_name(self):
        """测试无效工具名称调用"""
        try:
            from mcp_server_tke.server import handle_call_tool
            
            # 运行异步函数
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(handle_call_tool("InvalidTool", {}))
            finally:
                loop.close()
            
            # 验证错误响应
            self.assertEqual(len(result), 1)
            self.assertIsInstance(result[0], types.TextContent)
            self.assertIn("错误", result[0].text)
            self.assertIn("未知的工具", result[0].text)
            
        except ImportError:
            self.skipTest("MCP依赖未安装，跳过无效工具测试")

    @unittest.skipUnless(MCP_AVAILABLE, "MCP not available")
    def test_call_tool_invalid_params(self):
        """测试无效参数调用"""
        try:
            from mcp_server_tke.server import handle_call_tool
            
            # 准备无效参数（缺少必填字段）
            arguments = {
                "Region": "invalid-region"
            }
            
            # 运行异步函数
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(handle_call_tool("CreateCluster", arguments))
            finally:
                loop.close()
            
            # 验证错误响应
            self.assertEqual(len(result), 1)
            self.assertIsInstance(result[0], types.TextContent)
            self.assertIn("错误", result[0].text)
            
        except ImportError:
            self.skipTest("MCP依赖未安装，跳过无效参数测试")

    @unittest.skipUnless(MCP_AVAILABLE, "MCP not available")
    def test_call_tool_none_arguments(self):
        """测试空参数调用"""
        try:
            from mcp_server_tke.server import handle_call_tool
            
            # 运行异步函数，传入None参数
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(handle_call_tool("CreateCluster", None))
            finally:
                loop.close()
            
            # 验证错误响应
            self.assertEqual(len(result), 1)
            self.assertIsInstance(result[0], types.TextContent)
            self.assertIn("错误", result[0].text)
            
        except ImportError:
            self.skipTest("MCP依赖未安装，跳过空参数测试")

    def test_serve_function_exists(self):
        """测试serve函数存在性"""
        try:
            from mcp_server_tke.server import serve
            self.assertTrue(callable(serve))
        except ImportError:
            self.skipTest("MCP依赖未安装，跳过serve函数测试")

if __name__ == '__main__':
    unittest.main()
