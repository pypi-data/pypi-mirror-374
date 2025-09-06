"""
动态工具处理器模块

该模块负责将McpAPI定义转换为MCP工具schema，
并处理动态工具的调用请求。
"""

# 常量定义
DEFAULT_REGION = "ap-guangzhou"

import json
import logging
from typing import Dict, Any, List
import mcp.types as types

# 设置日志记录
logger = logging.getLogger(__name__)

try:
    from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
    from .client import get_common_client, has_credentials
    TENCENTCLOUD_AVAILABLE = True
except ImportError:
    logger.warning("腾讯云SDK未安装，TKE功能将使用模拟模式")
    TENCENTCLOUD_AVAILABLE = False
    # 定义模拟的异常类
    class TencentCloudSDKException(Exception):
        pass
    # 定义模拟的认证检查函数
    def has_credentials():
        return False

class DynamicToolHandler:
    """动态工具处理器
    
    负责将McpAPI定义转换为MCP工具并处理调用请求
    """
    
    def __init__(self, mcpapi_data: Dict[str, Dict[str, Any]]):
        """初始化动态工具处理器
        
        Args:
            mcpapi_data: McpAPI文件名到解析结果的映射字典
        """
        self.mcpapi_data = mcpapi_data
        self.tools_cache = {}  # 缓存生成的工具
        logger.info(f"动态工具处理器初始化完成，McpAPI文件数量：{len(mcpapi_data)}")
    
    def generate_mcp_tools(self) -> List[types.Tool]:
        """生成MCP工具列表
        
        从McpAPI数据生成符合MCP协议的工具定义列表
        
        Returns:
            List[types.Tool]: MCP工具列表
        """
        logger.info("开始生成MCP工具列表")
        
        mcp_tools = []
        tool_count = 0
        
        # 遍历所有McpAPI文件
        for file_key, file_data in self.mcpapi_data.items():
            try:
                # 检查文件是否包含tools字段
                if 'tools' not in file_data or not isinstance(file_data['tools'], list):
                    logger.warning(f"McpAPI文件 {file_key} 缺少tools字段或格式不正确")
                    continue
                
                # 遍历文件中的所有工具
                for tool_spec in file_data['tools']:
                    try:
                        # 转换单个工具
                        mcp_tool = self._convert_to_mcp_tool(tool_spec)
                        mcp_tools.append(mcp_tool)
                        tool_count += 1
                        
                        # 缓存工具规范，供后续调用使用
                        tool_name = tool_spec.get('name')
                        if tool_name:
                            self.tools_cache[tool_name] = tool_spec
                        
                        logger.debug(f"成功转换工具：{tool_name}")
                        
                    except Exception as e:
                        tool_name = tool_spec.get('name', 'unknown')
                        logger.warning(f"转换工具 {tool_name} 失败：{str(e)}")
                        continue
                        
            except Exception as e:
                logger.warning(f"处理McpAPI文件 {file_key} 失败：{str(e)}")
                continue
        
        logger.info(f"MCP工具生成完成，共生成 {tool_count} 个工具")
        return mcp_tools
    
    def handle_tool_call(self, tool_name: str, params: Dict[str, Any]) -> str:
        """处理动态工具调用
        
        Args:
            tool_name: 工具名称
            params: 调用参数
            
        Returns:
            str: API响应结果的JSON字符串
            
        Raises:
            ValueError: 工具不存在或参数验证失败
            Exception: API调用失败
        """
        logger.info(f"处理动态工具调用：{tool_name}")
        
        # 检查工具是否存在
        if tool_name not in self.tools_cache:
            raise ValueError(f"未知的动态工具：{tool_name}")
        
        tool_spec = self.tools_cache[tool_name]
        
        try:
            # 验证参数
            self._validate_tool_params(tool_spec, params)
            
            # 构建API请求
            api_request = self._build_api_request(tool_spec, params)
            
            # 调用TKE API
            result = self._call_tke_api(tool_spec, api_request)
            response = json.loads(result)

            response_template = tool_spec.get('responseTemplate', {})
            prepend_body = response_template.get('prependBody', {})
            
            logger.info(f"动态工具调用成功：{tool_name}")
            return f"{prepend_body}{response['Response']}"
            
        except Exception as e:
            logger.error(f"动态工具调用失败 {tool_name}：{str(e)}")
            raise
    
    def _validate_tool_params(self, tool_spec: Dict[str, Any], params: Dict[str, Any]) -> None:
        """验证工具参数
        
        Args:
            tool_spec: 工具规范
            params: 调用参数
            
        Raises:
            ValueError: 参数验证失败
        """
        logger.debug("开始验证工具参数")

        if params["Region"] is None or params["Region"] == "":
            raise ValueError(f"参数 Region 不能为空")
        
        tool_args = tool_spec.get('args', [])
        
        # 检查必填参数
        for arg in tool_args:
            arg_name = arg.get('name')
            is_required = arg.get('required', False)
            
            if is_required and (arg_name not in params or params[arg_name] is None):
                raise ValueError(f"缺少必填参数：{arg_name}")
        
        logger.debug("参数验证通过")
    
    def _build_api_request(self, tool_spec: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """构建API请求
        
        Args:
            tool_spec: 工具规范
            params: 调用参数
            
        Returns:
            Dict[str, Any]: API请求参数
        """
        logger.debug("构建API请求")
        
        # 获取请求模板
        request_template = tool_spec.get('requestTemplate', {})
        api_url = request_template.get('url', '/')
        api_method = request_template.get('method', 'POST')
        
        # 构建请求参数（简化处理，直接使用传入的参数）
        api_request = {
            'action': tool_spec.get('name'),
            'url': api_url,
            'method': api_method,
            'params': params
        }
        
        logger.debug(f"API请求构建完成：{api_url}")
        return api_request
    
    def _call_tke_api(self, tool_spec: Dict[str, Any], api_request: Dict[str, Any]) -> str:
        """调用TKE API
        
        Args:
            tool_spec: 工具规范
            api_request: API请求参数
            
        Returns:
            str: API响应结果的JSON字符串
        """
        logger.debug("开始调用TKE API")
        
        # 如果没有认证信息，返回模拟响应
        if not TENCENTCLOUD_AVAILABLE or not has_credentials():
            logger.info("未配置TKE认证信息，返回模拟响应")
            return self._mock_api_response(tool_spec, api_request)
        
        try:
            # 使用通用客户端调用API
            action_name = api_request['action']
            params = api_request['params']
            
            # 默认使用广州地域，实际应该根据参数决定
            region = params.get('Region')
            params.pop('Region', None)
            client = get_common_client(region)
            
            # 调用API
            response = client.call(action_name, params)
            
            logger.debug("TKE API调用成功")
            return response
            
        except Exception as e:
            logger.error(f"调用{action_name}失败: {str(e)}")
            raise e
    
    def _mock_api_response(self, tool_spec: Dict[str, Any], api_request: Dict[str, Any]) -> str:
        """生成模拟API响应
        
        Args:
            tool_spec: 工具规范
            api_request: API请求参数
            
        Returns:
            str: 模拟的API响应JSON字符串
        """
        import uuid
        
        tool_name = tool_spec.get('name', 'unknown')
        
        # 构建模拟响应
        mock_response = {
            "Response": {
                "RequestId": str(uuid.uuid4()),
                "Result": f"{tool_name} 操作成功（模拟响应）",
                "Message": "操作完成"
            }
        }
        
        logger.debug(f"生成模拟响应：{tool_name}")
        return json.dumps(mock_response, ensure_ascii=False)
    
    def _convert_to_mcp_tool(self, tool_spec: Dict[str, Any]) -> types.Tool:
        """将工具规范转换为MCP工具
        
        Args:
            tool_spec: McpAPI工具规范
            
        Returns:
            types.Tool: MCP工具定义
            
        Raises:
            ValueError: 工具规范格式错误
        """
        logger.debug(f"转换工具规范：{tool_spec.get('name', 'unknown')}")
        
        # 检查必需字段
        if 'name' not in tool_spec:
            raise ValueError("工具规范缺少name字段")
        
        tool_name = tool_spec['name']
        tool_description = tool_spec.get('description', '')
        
        # 生成输入schema
        tool_args = tool_spec.get('args', [])
        input_schema = self._build_input_schema(tool_args)
        
        # 创建MCP工具
        tool = types.Tool(
            name=tool_name,
            description=tool_description,
            inputSchema=input_schema
        )
        
        logger.debug(f"工具转换成功：{tool_name}")
        return tool
    
    def _build_input_schema(self, args: List[Dict[str, Any]]) -> Dict[str, Any]:
        """构建输入schema
        
        Args:
            args: McpAPI参数列表
            
        Returns:
            Dict[str, Any]: JSON Schema格式的输入schema
        """
        logger.debug("构建输入schema")
        
        schema = {
            "type": "object",
            "properties": {
                "Region": {
                    "type": "string",
                    "description": "地域，如 ap-guangzhou，默认为广州",
                },
            },
            "required": ["Region"]
        }
        
        if not args or not isinstance(args, list):
            logger.debug("参数列表为空或格式不正确")
            return schema
        
        # 遍历所有参数
        for arg in args:
            try:
                # 检查参数必需字段
                if 'name' not in arg:
                    logger.warning("参数缺少name字段，跳过")
                    continue
                
                param_name = arg['name']
                param_type = arg.get('type', 'string')
                param_description = arg.get('description', '')
                param_default = arg.get('default')
                param_enum = arg.get('enum')
                is_required = arg.get('required', False)
                
                # 映射类型
                json_schema_type = self._map_mcpapi_type_to_json_schema(param_type)
                
                # 构建参数schema
                param_schema = {
                    "type": json_schema_type,
                    "description": param_description
                }
                
                # 添加默认值
                if param_default is not None:
                    param_schema["default"] = param_default

                # 添加枚举值
                if param_enum is not None and isinstance(param_enum, list):
                    param_schema["enum"] = param_enum
                
                # 处理对象类型的properties
                if param_type == 'object' and 'properties' in arg:
                    param_schema["properties"] = self._build_object_properties(arg['properties'])
                
                # 处理数组类型
                if param_type == 'array' and 'items' in arg:
                    items_def = arg['items']
                    if isinstance(items_def, dict):
                        items_type = items_def.get('type', 'string')
                        param_schema["items"] = {
                            "type": self._map_mcpapi_type_to_json_schema(items_type)
                        }
                        
                        # 如果数组项目是对象，递归处理
                        if items_type == 'object' and 'properties' in items_def:
                            param_schema["items"]["properties"] = self._build_object_properties(items_def['properties'])
                
                # 添加到schema
                schema["properties"][param_name] = param_schema
                
                # 如果是必填参数，添加到required列表
                if is_required:
                    schema["required"].append(param_name)
                
                logger.debug(f"成功处理参数：{param_name}, 类型：{param_type}")
                
            except Exception as e:
                param_name = arg.get('name', 'unknown')
                logger.warning(f"处理参数 {param_name} 时发生错误：{str(e)}")
                continue
        
        logger.debug(f"输入schema构建完成，参数数量：{len(schema['properties'])}")
        return schema
    
    def _map_mcpapi_type_to_json_schema(self, mcpapi_type: str) -> str:
        """映射McpAPI类型到JSON Schema类型
        
        Args:
            mcpapi_type: McpAPI类型
            
        Returns:
            str: JSON Schema类型
        """
        type_mapping = {
            'string': 'string',
            'integer': 'integer',
            'boolean': 'boolean',
            'object': 'object',
            'array': 'array',
            'number': 'number'
        }
        
        return type_mapping.get(mcpapi_type.lower(), 'string')
    
    def _build_object_properties(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """构建对象类型的properties（支持递归嵌套）
        
        Args:
            properties: 对象属性定义
            
        Returns:
            Dict[str, Any]: JSON Schema格式的properties
        """
        json_properties = {}
        
        for prop_name, prop_def in properties.items():
            try:
                if isinstance(prop_def, dict):
                    prop_type = prop_def.get('type', 'string')
                    prop_description = prop_def.get('description', '')
                    prop_default = prop_def.get('default')
                    prop_enum = prop_def.get('enum')
                    
                    json_prop = {
                        "type": self._map_mcpapi_type_to_json_schema(prop_type),
                        "description": prop_description
                    }
                    
                    # 添加默认值
                    if prop_default is not None:
                        json_prop["default"] = prop_default

                    # 添加枚举值
                    if prop_enum is not None and isinstance(prop_enum, list):
                        json_prop["enum"] = prop_enum
                    
                    # 递归处理嵌套对象
                    if prop_type == 'object' and 'properties' in prop_def:
                        json_prop["properties"] = self._build_object_properties(prop_def['properties'])
                    
                    # 处理数组类型
                    if prop_type == 'array' and 'items' in prop_def:
                        items_def = prop_def['items']
                        if isinstance(items_def, dict):
                            items_type = items_def.get('type', 'string')
                            json_prop["items"] = {
                                "type": self._map_mcpapi_type_to_json_schema(items_type)
                            }
                            
                            # 如果数组项目是对象，递归处理
                            if items_type == 'object' and 'properties' in items_def:
                                json_prop["items"]["properties"] = self._build_object_properties(items_def['properties'])
                    
                    json_properties[prop_name] = json_prop
                    logger.debug(f"成功处理对象属性：{prop_name}, 类型：{prop_type}")
                    
            except Exception as e:
                logger.warning(f"处理对象属性 {prop_name} 时发生错误：{str(e)}")
                continue
        
        return json_properties
