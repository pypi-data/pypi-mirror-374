"""
TKE工具模块单元测试
"""
import json
import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os
import tempfile
import shutil

# 添加src路径以便导入模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# 直接导入工具模块，避免通过__init__.py导入
import mcp_server_tke.tool_tke as tool_tke
from mcp_server_tke.mcpapi_loader import McpAPILoader
from mcp_server_tke.dynamic_tool_handler import DynamicToolHandler


class TestMcpAPILoader(unittest.TestCase):
    """McpAPI加载器测试类"""
    
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.loader = McpAPILoader(self.temp_dir)
    
    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init(self):
        """测试初始化"""
        loader = McpAPILoader("./test/")
        self.assertEqual(loader.mcpapi_dir, "./test/")
    
    def test_load_mcpapi_files_empty_directory(self):
        """测试空目录"""
        result = self.loader.load_mcpapi_files()
        self.assertEqual(result, {})
    
    def test_load_mcpapi_files_nonexistent_directory(self):
        """测试不存在的目录"""
        loader = McpAPILoader("/nonexistent/directory/")
        result = loader.load_mcpapi_files()
        self.assertEqual(result, {})
    
    def test_load_mcpapi_files_valid_yaml(self):
        """测试加载有效的YAML文件"""
        # 创建测试YAML文件
        yaml_content = """
name: TestTool
description: 测试工具
tools:
  - name: TestAPI
    description: 测试API
    args:
      - name: TestParam
        type: string
        required: true
"""
        yaml_file = os.path.join(self.temp_dir, "test.yaml")
        with open(yaml_file, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
        
        result = self.loader.load_mcpapi_files()
        
        self.assertIn("test", result)
        self.assertEqual(result["test"]["name"], "TestTool")
        self.assertEqual(len(result["test"]["tools"]), 1)
    
    def test_load_mcpapi_files_invalid_yaml(self):
        """测试加载无效的YAML文件"""
        # 创建格式错误的YAML文件
        yaml_content = """
name: TestTool
description: 测试工具
tools:
  - name: TestAPI
    description 缺少冒号的描述
"""
        yaml_file = os.path.join(self.temp_dir, "invalid.yaml")
        with open(yaml_file, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
        
        # 创建正常的YAML文件
        valid_content = """
name: ValidTool
description: 有效工具
"""
        valid_file = os.path.join(self.temp_dir, "valid.yaml")
        with open(valid_file, 'w', encoding='utf-8') as f:
            f.write(valid_content)
        
        result = self.loader.load_mcpapi_files()
        
        # 应该只加载有效的文件，忽略无效的文件
        self.assertIn("valid", result)
        self.assertNotIn("invalid", result)
    
    def test_load_mcpapi_files_mixed_extensions(self):
        """测试混合文件扩展名"""
        # 创建.yaml文件
        yaml_file = os.path.join(self.temp_dir, "file1.yaml")
        with open(yaml_file, 'w', encoding='utf-8') as f:
            f.write("name: YamlFile\n")
        
        # 创建.yml文件
        yml_file = os.path.join(self.temp_dir, "file2.yml")
        with open(yml_file, 'w', encoding='utf-8') as f:
            f.write("name: YmlFile\n")
        
        # 创建非YAML文件
        txt_file = os.path.join(self.temp_dir, "file3.txt")
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write("This is not a YAML file\n")
        
        result = self.loader.load_mcpapi_files()
        
        # 应该加载.yaml和.yml文件，忽略.txt文件
        self.assertEqual(len(result), 2)
        self.assertIn("file1", result)
        self.assertIn("file2", result)
        self.assertEqual(result["file1"]["name"], "YamlFile")
        self.assertEqual(result["file2"]["name"], "YmlFile")
    
    def test_parse_yaml_file_success(self):
        """测试成功解析YAML文件"""
        yaml_content = """
name: TestFile
description: 测试文件
data:
  key1: value1
  key2: 123
"""
        yaml_file = os.path.join(self.temp_dir, "test.yaml")
        with open(yaml_file, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
        
        result = self.loader._parse_yaml_file(yaml_file)
        
        self.assertEqual(result["name"], "TestFile")
        self.assertEqual(result["data"]["key1"], "value1")
        self.assertEqual(result["data"]["key2"], 123)
    
    def test_parse_yaml_file_not_found(self):
        """测试文件不存在"""
        with self.assertRaises(FileNotFoundError):
            self.loader._parse_yaml_file("/nonexistent/file.yaml")
    
    def test_parse_yaml_file_empty(self):
        """测试空YAML文件"""
        yaml_file = os.path.join(self.temp_dir, "empty.yaml")
        with open(yaml_file, 'w', encoding='utf-8') as f:
            f.write("")
        
        result = self.loader._parse_yaml_file(yaml_file)
        self.assertEqual(result, {})
    
    def test_parse_yaml_file_invalid_format(self):
        """测试无效的YAML格式"""
        yaml_file = os.path.join(self.temp_dir, "invalid.yaml")
        with open(yaml_file, 'w', encoding='utf-8') as f:
            f.write("invalid: yaml: format:")
        
        with self.assertRaises(ValueError):
            self.loader._parse_yaml_file(yaml_file)


class TestDynamicToolHandler(unittest.TestCase):
    """动态工具处理器测试类"""
    
    def setUp(self):
        """设置测试环境"""
        self.sample_mcpapi_data = {
            "test_tool": {
                "name": "TestTool",
                "description": "测试工具",
                "tools": [
                    {
                        "name": "SimpleAPI",
                        "description": "简单API",
                        "args": [
                            {
                                "name": "StringParam",
                                "type": "string",
                                "description": "字符串参数",
                                "required": True
                            },
                            {
                                "name": "IntParam",
                                "type": "integer",
                                "description": "整数参数",
                                "required": False,
                                "default": 100
                            }
                        ],
                        "requestTemplate": {
                            "url": "/test/simple",
                            "method": "POST"
                        }
                    },
                    {
                        "name": "ComplexAPI",
                        "description": "复杂API",
                        "args": [
                            {
                                "name": "ObjectParam",
                                "type": "object",
                                "description": "对象参数",
                                "required": True,
                                "properties": {
                                    "nested_string": {
                                        "type": "string",
                                        "description": "嵌套字符串",
                                        "required": True
                                    },
                                    "nested_number": {
                                        "type": "integer",
                                        "description": "嵌套数字",
                                        "required": False,
                                        "default": 42
                                    }
                                }
                            }
                        ],
                        "requestTemplate": {
                            "url": "/test/complex",
                            "method": "POST"
                        }
                    }
                ]
            }
        }
        self.handler = DynamicToolHandler(self.sample_mcpapi_data)
        # 构建工具缓存
        self.handler.generate_mcp_tools()
    
    def test_init(self):
        """测试初始化"""
        handler = DynamicToolHandler({})
        self.assertEqual(handler.mcpapi_data, {})
    
    def test_generate_mcp_tools(self):
        """测试生成MCP工具"""
        tools = self.handler.generate_mcp_tools()
        
        self.assertEqual(len(tools), 2)
        
        # 检查第一个工具
        simple_tool = tools[0]
        self.assertEqual(simple_tool.name, "SimpleAPI")
        self.assertEqual(simple_tool.description, "简单API")
        
        # 检查输入模式
        schema = simple_tool.inputSchema
        self.assertEqual(schema["type"], "object")
        self.assertIn("StringParam", schema["properties"])
        self.assertIn("IntParam", schema["properties"])
        self.assertEqual(schema["required"], ['Region', 'StringParam'])
        
        # 检查第二个工具
        complex_tool = tools[1]
        self.assertEqual(complex_tool.name, "ComplexAPI")
        self.assertEqual(complex_tool.description, "复杂API")
        
        # 检查嵌套对象
        complex_schema = complex_tool.inputSchema
        object_param = complex_schema["properties"]["ObjectParam"]
        self.assertEqual(object_param["type"], "object")
        self.assertIn("nested_string", object_param["properties"])
        self.assertIn("nested_number", object_param["properties"])
    
    def test_generate_mcp_tools_empty_data(self):
        """测试空数据生成工具"""
        handler = DynamicToolHandler({})
        tools = handler.generate_mcp_tools()
        self.assertEqual(len(tools), 0)
    
    def test_build_input_schema_simple_types(self):
        """测试构建简单类型的输入模式"""
        args = [
            {"name": "str_param", "type": "string", "description": "字符串", "required": True},
            {"name": "int_param", "type": "integer", "description": "整数", "required": False, "default": 10},
            {"name": "bool_param", "type": "boolean", "description": "布尔", "required": False}
        ]
        
        schema = self.handler._build_input_schema(args)
        
        self.assertEqual(schema["type"], "object")
        self.assertEqual(len(schema["properties"]), 4)
        self.assertEqual(schema["required"], ['Region', 'str_param'])
        
        # 检查字符串参数
        str_prop = schema["properties"]["str_param"]
        self.assertEqual(str_prop["type"], "string")
        self.assertEqual(str_prop["description"], "字符串")
        
        # 检查整数参数（有默认值）
        int_prop = schema["properties"]["int_param"]
        self.assertEqual(int_prop["type"], "integer")
        self.assertEqual(int_prop["default"], 10)
    
    def test_build_input_schema_array_type(self):
        """测试构建数组类型的输入模式"""
        args = [
            {
                "name": "array_param",
                "type": "array",
                "description": "数组参数",
                "required": True,
                "items": {"type": "string"}
            }
        ]
        
        schema = self.handler._build_input_schema(args)
        
        array_prop = schema["properties"]["array_param"]
        self.assertEqual(array_prop["type"], "array")
        self.assertEqual(array_prop["items"]["type"], "string")
    
    def test_build_input_schema_nested_object(self):
        """测试构建嵌套对象的输入模式"""
        args = [
            {
                "name": "nested_obj",
                "type": "object",
                "description": "嵌套对象",
                "required": True,
                "properties": {
                    "level1": {
                        "type": "object",
                        "description": "第一层",
                        "required": True,
                        "properties": {
                            "level2": {
                                "type": "string",
                                "description": "第二层",
                                "required": True
                            }
                        }
                    }
                }
            }
        ]
        
        schema = self.handler._build_input_schema(args)
        
        nested_prop = schema["properties"]["nested_obj"]
        self.assertEqual(nested_prop["type"], "object")
        
        level1_prop = nested_prop["properties"]["level1"]
        self.assertEqual(level1_prop["type"], "object")
        
        level2_prop = level1_prop["properties"]["level2"]
        self.assertEqual(level2_prop["type"], "string")
    
    def test_handle_tool_call_success(self):
        """测试成功的工具调用"""
        params = {"StringParam": "test_value"}
        
        result = self.handler.handle_tool_call("SimpleAPI", params)
        
        # 应该返回模拟响应（因为没有真实的TKE认证）
        self.assertIn("RequestId", result)
    
    def test_handle_tool_call_unknown_tool(self):
        """测试未知工具调用"""
        with self.assertRaises(ValueError) as context:
            self.handler.handle_tool_call("UnknownTool", {})
        
        self.assertIn("未知的动态工具", str(context.exception))
    
    def test_handle_tool_call_missing_required_param(self):
        """测试缺少必填参数"""
        with self.assertRaises(ValueError) as context:
            self.handler.handle_tool_call("SimpleAPI", {})
        
        self.assertIn("缺少必填参数", str(context.exception))
    
    def test_handle_tool_call_valid_optional_param(self):
        """测试有效的可选参数"""
        params = {"StringParam": "test_value", "IntParam": 200}
        
        result = self.handler.handle_tool_call("SimpleAPI", params)
        
        # 应该成功处理
        self.assertIn("RequestId", result)
    
    def test_validate_tool_params_success(self):
        """测试参数验证成功"""
        tool_spec = self.sample_mcpapi_data["test_tool"]["tools"][0]
        params = {"StringParam": "test", "IntParam": 123}
        
        # 不应该抛出异常
        self.handler._validate_tool_params(tool_spec, params)
    
    def test_validate_tool_params_missing_required(self):
        """测试缺少必填参数的验证"""
        tool_spec = self.sample_mcpapi_data["test_tool"]["tools"][0]
        params = {"IntParam": 123}  # 缺少StringParam
        
        with self.assertRaises(ValueError) as context:
            self.handler._validate_tool_params(tool_spec, params)
        
        self.assertIn("缺少必填参数", str(context.exception))
        self.assertIn("StringParam", str(context.exception))
    
    def test_build_api_request(self):
        """测试构建API请求"""
        tool_spec = self.sample_mcpapi_data["test_tool"]["tools"][0]
        params = {"StringParam": "test", "IntParam": 123}
        
        request = self.handler._build_api_request(tool_spec, params)
        
        self.assertEqual(request["action"], "SimpleAPI")
        self.assertEqual(request["url"], "/test/simple")
        self.assertEqual(request["method"], "POST")
        self.assertEqual(request["params"], params)


class TestTKETools(unittest.TestCase):
    """TKE工具函数测试类"""

    def test_validate_create_cluster_params_valid(self):
        """测试有效的创建集群参数验证"""
        params = {
            "Region": "ap-guangzhou",
            "ClusterBasicSettings.ClusterOs": "tlinux3.1x86_64",
            "ClusterBasicSettings.VpcId": "vpc-l51ixsi7",
            "ClusterCIDRSettings.EniSubnetIds": ["subnet-0jkfc3dk"],
            "ClusterCIDRSettings.ServiceCIDR": "10.1.0.0/16"
        }
        
        # 不应该抛出异常
        tool_tke._validate_create_cluster_params(params)

    def test_validate_create_cluster_params_missing_required(self):
        """测试缺少必填参数的验证"""
        params = {
            "Region": "ap-guangzhou"
            # 缺少其他必填参数
        }
        
        with self.assertRaises(ValueError) as context:
            tool_tke._validate_create_cluster_params(params)
        
        self.assertIn("必填参数", str(context.exception))

    def test_validate_create_cluster_params_invalid_region(self):
        """测试无效地域参数"""
        params = {
            "Region": "invalid-region",
            "ClusterBasicSettings.ClusterOs": "tlinux3.1x86_64",
            "ClusterBasicSettings.VpcId": "vpc-l51ixsi7",
            "ClusterCIDRSettings.EniSubnetIds": ["subnet-0jkfc3dk"],
            "ClusterCIDRSettings.ServiceCIDR": "10.1.0.0/16"
        }
        
        with self.assertRaises(ValueError) as context:
            tool_tke._validate_create_cluster_params(params)
        
        self.assertIn("Region必须是以下值之一", str(context.exception))

    def test_validate_create_cluster_params_invalid_cluster_level(self):
        """测试无效集群规格参数"""
        params = {
            "Region": "ap-guangzhou",
            "ClusterBasicSettings.ClusterLevel": "INVALID",
            "ClusterBasicSettings.ClusterOs": "tlinux3.1x86_64",
            "ClusterBasicSettings.VpcId": "vpc-l51ixsi7",
            "ClusterCIDRSettings.EniSubnetIds": ["subnet-0jkfc3dk"],
            "ClusterCIDRSettings.ServiceCIDR": "10.1.0.0/16"
        }
        
        with self.assertRaises(ValueError) as context:
            tool_tke._validate_create_cluster_params(params)
        
        self.assertIn("ClusterLevel必须是以下值之一", str(context.exception))

    def test_is_valid_cidr(self):
        """测试CIDR格式验证"""
        # 有效的CIDR
        self.assertTrue(tool_tke._is_valid_cidr("10.0.0.0/16"))
        self.assertTrue(tool_tke._is_valid_cidr("192.168.1.0/24"))
        self.assertTrue(tool_tke._is_valid_cidr("172.16.0.0/17"))
        
        # 无效的CIDR
        self.assertFalse(tool_tke._is_valid_cidr("10.0.0.0"))  # 缺少前缀
        self.assertFalse(tool_tke._is_valid_cidr("256.0.0.0/16"))  # 无效IP
        self.assertFalse(tool_tke._is_valid_cidr("10.0.0.0/33"))  # 无效前缀长度
        self.assertFalse(tool_tke._is_valid_cidr("invalid"))  # 完全无效

    def test_build_create_cluster_request(self):
        """测试构建创建集群请求参数"""
        params = {
            "ClusterBasicSettings.ClusterName": "test-cluster",
            "ClusterBasicSettings.ClusterLevel": "L200",
            "ClusterBasicSettings.ClusterOs": "tlinux3.1x86_64",
            "ClusterBasicSettings.VpcId": "vpc-l51ixsi7",
            "ClusterCIDRSettings.EniSubnetIds": ["subnet-0jkfc3dk", "subnet-87654321"],
            "ClusterCIDRSettings.ServiceCIDR": "10.1.0.0/16"
        }
        
        result = tool_tke._build_create_cluster_request(params)
        
        # 验证结构
        self.assertIn("ClusterBasicSettings", result)
        self.assertIn("ClusterCIDRSettings", result)
        
        # 验证集群基本设置
        basic = result["ClusterBasicSettings"]
        self.assertEqual(basic["ClusterName"], "test-cluster")
        self.assertEqual(basic["ClusterLevel"], "L200")
        self.assertEqual(basic["ClusterOs"], "tlinux3.1x86_64")
        self.assertEqual(basic["VpcId"], "vpc-l51ixsi7")
        
        # 验证CIDR设置
        cidr = result["ClusterCIDRSettings"]
        self.assertEqual(cidr["EniSubnetIds"], ["subnet-0jkfc3dk", "subnet-87654321"])
        self.assertEqual(cidr["ServiceCIDR"], "10.1.0.0/16")

    def test_build_create_cluster_request_default_level(self):
        """测试构建请求参数时使用默认集群规格"""
        params = {
            "ClusterBasicSettings.ClusterOs": "tlinux3.1x86_64",
            "ClusterBasicSettings.VpcId": "vpc-l51ixsi7",
            "ClusterCIDRSettings.EniSubnetIds": ["subnet-0jkfc3dk"],
            "ClusterCIDRSettings.ServiceCIDR": "10.1.0.0/16"
        }
        
        result = tool_tke._build_create_cluster_request(params)
        
        # 验证默认集群规格
        basic = result["ClusterBasicSettings"]
        self.assertEqual(basic["ClusterLevel"], "L5")  # 默认值

    def test_create_cluster_invalid_params(self):
        """测试无效参数创建集群"""
        params = {
            "Region": "invalid-region"
        }
        
        with self.assertRaises(ValueError):
            tool_tke.create_cluster(params)

    def test_create_cluster_with_optional_params(self):
        """测试包含可选参数的创建集群"""
        params = {
            "Region": "ap-guangzhou",
            "ClusterBasicSettings.ClusterName": "mcp-cluster",
            "ClusterBasicSettings.ClusterLevel": "L5",
            "ClusterBasicSettings.ClusterOs": "tlinux3.1x86_64",
            "ClusterBasicSettings.VpcId": "vpc-l51ixsi7",
            "ClusterCIDRSettings.EniSubnetIds": ["subnet-0jkfc3dk"],
            "ClusterCIDRSettings.ServiceCIDR": "192.168.0.0/17"
        }
        
        result = tool_tke.create_cluster(params)
        
        # 验证响应格式
        response = json.loads(result)
        self.assertIn("ClusterId", response)
        self.assertIn("RequestId", response)

if __name__ == '__main__':
    unittest.main()
