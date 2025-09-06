"""
集成测试：测试McpAPI到MCP工具转换的完整流程
"""
import asyncio
import unittest
import tempfile
import shutil
import os
import sys
import json

# 添加src路径以便导入模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mcp_server_tke.mcpapi_loader import McpAPILoader
from mcp_server_tke.dynamic_tool_handler import DynamicToolHandler
from mcp_server_tke.server import handle_list_tools, handle_call_tool


class TestIntegration(unittest.TestCase):
    """集成测试类"""
    
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        
        # 创建测试McpAPI文件
        self.test_mcpapi_content = """
name: IntegrationTestTool
description: 集成测试工具
tools:
  - name: TestIntegrationAPI
    description: 集成测试API
    args:
      - name: RequiredParam
        type: string
        description: 必填参数
        required: true
      - name: OptionalParam
        type: integer
        description: 可选参数
        required: false
        default: 42
    requestTemplate:
      url: "/integration/test"
      method: POST
      body:
        Action: TestIntegrationAPI
        RequiredParam: "{{RequiredParam}}"
        OptionalParam: "{{OptionalParam}}"
"""
        
        # 保存到临时文件
        self.test_file_path = os.path.join(self.temp_dir, "integration_test.yaml")
        with open(self.test_file_path, 'w', encoding='utf-8') as f:
            f.write(self.test_mcpapi_content)
    
    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_end_to_end_workflow(self):
        """测试端到端工作流程"""
        # 1. 测试McpAPI文件加载
        loader = McpAPILoader(self.temp_dir)
        mcpapi_data = loader.load_mcpapi_files()
        
        self.assertEqual(len(mcpapi_data), 1)
        self.assertIn("integration_test", mcpapi_data)
        
        # 2. 测试工具处理器创建
        handler = DynamicToolHandler(mcpapi_data)
        tools = handler.generate_mcp_tools()
        
        self.assertEqual(len(tools), 1)
        tool = tools[0]
        self.assertEqual(tool.name, "TestIntegrationAPI")
        self.assertEqual(tool.description, "集成测试API")
        
        # 3. 测试输入模式生成
        schema = tool.inputSchema
        self.assertEqual(schema["type"], "object")
        self.assertIn("RequiredParam", schema["properties"])
        self.assertIn("OptionalParam", schema["properties"])
        self.assertEqual(schema["required"], ['Region', 'RequiredParam'])
        
        # 4. 测试工具调用 - 成功案例
        result = handler.handle_tool_call("TestIntegrationAPI", {
            "RequiredParam": "test_value"
        })
        
        self.assertIn("RequestId", result)
        
        # 5. 测试工具调用 - 失败案例（缺少必填参数）
        with self.assertRaises(ValueError) as context:
            handler.handle_tool_call("TestIntegrationAPI", {})
        
        self.assertIn("缺少必填参数", str(context.exception))
    
    def test_multiple_mcpapi_files(self):
        """测试多个McpAPI文件的处理"""
        # 创建第二个McpAPI文件
        second_content = """
name: SecondTestTool
description: 第二个测试工具
tools:
  - name: SecondAPI
    description: 第二个API
    args:
      - name: TestParam
        type: string
        required: true
    requestTemplate:
      url: "/second/api"
      method: GET
"""
        
        second_file = os.path.join(self.temp_dir, "second_test.yaml")
        with open(second_file, 'w', encoding='utf-8') as f:
            f.write(second_content)
        
        # 加载所有文件
        loader = McpAPILoader(self.temp_dir)
        mcpapi_data = loader.load_mcpapi_files()
        
        self.assertEqual(len(mcpapi_data), 2)
        self.assertIn("integration_test", mcpapi_data)
        self.assertIn("second_test", mcpapi_data)
        
        # 生成工具
        handler = DynamicToolHandler(mcpapi_data)
        tools = handler.generate_mcp_tools()
        
        self.assertEqual(len(tools), 2)
        tool_names = [tool.name for tool in tools]
        self.assertIn("TestIntegrationAPI", tool_names)
        self.assertIn("SecondAPI", tool_names)
    
    def test_error_handling(self):
        """测试错误处理"""
        # 创建格式错误的文件 - 完全损坏的YAML
        invalid_content = "invalid yaml content: [unclosed"
        
        invalid_file = os.path.join(self.temp_dir, "broken.yaml")
        with open(invalid_file, 'w', encoding='utf-8') as f:
            f.write(invalid_content)
        
        # 加载YAML文件
        loader = McpAPILoader(self.temp_dir)
        mcpapi_data = loader.load_mcpapi_files()
        
        # 应该只加载有效的文件，忽略损坏的文件
        self.assertEqual(len(mcpapi_data), 1)
        self.assertIn("integration_test", mcpapi_data)
        self.assertNotIn("broken", mcpapi_data)
        
        # 生成工具应该正常工作
        handler = DynamicToolHandler(mcpapi_data)
        tools = handler.generate_mcp_tools()
        
        self.assertEqual(len(tools), 1)
        self.assertEqual(tools[0].name, "TestIntegrationAPI")
        
    def test_empty_directory(self):
        """测试空目录处理"""
        empty_dir = tempfile.mkdtemp()
        try:
            loader = McpAPILoader(empty_dir)
            mcpapi_data = loader.load_mcpapi_files()
            
            self.assertEqual(len(mcpapi_data), 0)
            
            # 创建工具处理器应该也能正常工作
            handler = DynamicToolHandler(mcpapi_data)
            tools = handler.generate_mcp_tools()
            
            self.assertEqual(len(tools), 0)
        finally:
            shutil.rmtree(empty_dir, ignore_errors=True)
    
    def test_nonexistent_directory(self):
        """测试不存在目录的处理"""
        loader = McpAPILoader("/nonexistent/directory")
        mcpapi_data = loader.load_mcpapi_files()
        
        self.assertEqual(len(mcpapi_data), 0)
        
        # 创建工具处理器应该也能正常工作
        handler = DynamicToolHandler(mcpapi_data)
        tools = handler.generate_mcp_tools()
        
        self.assertEqual(len(tools), 0)


class TestServerIntegration(unittest.TestCase):
    """服务器集成测试类"""
    
    def test_tool_list_includes_dynamic_tools(self):
        """测试工具列表包含动态工具"""
        async def run_test():
            tools = await handle_list_tools()
            
            # 应该包含静态工具和动态工具
            tool_names = [tool.name for tool in tools]
            
            # 静态工具
            self.assertIn("CreateCluster", tool_names)
            self.assertIn("DeleteCluster", tool_names)
            
            # 动态工具
            self.assertIn("ModifyClusterAttribute", tool_names)
            self.assertIn("DescribeClusters", tool_names)
            
            # 验证总数量大于静态工具数量
            self.assertGreaterEqual(len(tools), 4)
        
        asyncio.run(run_test())
    
    def test_static_tool_call_still_works(self):
        """测试静态工具调用仍然有效"""
        async def run_test():
            # 测试静态工具调用
            result = await handle_call_tool("DeleteCluster", {"ClusterId": "cls-test123","InstanceDeleteMode": "terminate"})
            
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].type, "text")
            
            # 验证返回的是JSON格式
            response_text = result[0].text
            self.assertIn("RequestId", response_text)
        
        asyncio.run(run_test())
    
    def test_dynamic_tool_call_works(self):
        """测试动态工具调用有效"""
        async def run_test():
            # 测试动态工具调用
            result = await handle_call_tool("ModifyClusterAttribute", {
                "ClusterId": "cls-test123",
                "ClusterName": "mcp-tke"
            })
            
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].type, "text")
            
            # 验证返回的是JSON格式
            response_text = result[0].text
            self.assertIn("Response", response_text)
        
        asyncio.run(run_test())
    
    def test_unknown_tool_handling(self):
        """测试未知工具处理"""
        async def run_test():
            # 测试未知工具调用
            result = await handle_call_tool("NonExistentTool", {})
            
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].type, "text")
            
            # 应该返回错误信息
            response_text = result[0].text
            self.assertIn("错误", response_text)
            self.assertIn("未知", response_text)  # 更宽泛的匹配
        
        asyncio.run(run_test())


if __name__ == '__main__':
    unittest.main()
