"""
McpAPI文件加载器模块

该模块负责扫描和加载./mcpapi/目录下的YAML文件，
并将其解析为Python字典格式供后续处理。
"""

import os
import logging
import yaml
from typing import Dict, Any

# 设置日志记录
logger = logging.getLogger(__name__)


class McpAPILoader:
    """McpAPI文件加载器
    
    负责从指定目录加载和解析McpAPI YAML文件
    """
    
    def __init__(self, mcpapi_dir: str = "./mcpapi/"):
        """初始化McpAPI加载器
        
        Args:
            mcpapi_dir: McpAPI文件存放目录，默认为"./mcpapi/"
        """
        self.mcpapi_dir = mcpapi_dir
        logger.info(f"McpAPI加载器初始化完成，目录：{mcpapi_dir}")
    
    def load_mcpapi_files(self) -> Dict[str, Dict[str, Any]]:
        """加载所有McpAPI文件
        
        扫描mcpapi目录下的所有.yaml和.yml文件，
        解析并返回文件名到解析结果的映射字典。
        
        Returns:
            Dict[str, Dict[str, Any]]: 文件名到解析结果的映射字典
                键为文件名（不含扩展名），值为解析后的字典数据
        """
        logger.info("开始加载McpAPI文件")
        mcpapi_data = {}
        
        # 检查目录是否存在
        if not os.path.exists(self.mcpapi_dir):
            logger.info(f"McpAPI目录不存在：{self.mcpapi_dir}，返回空结果")
            return mcpapi_data
        
        if not os.path.isdir(self.mcpapi_dir):
            logger.warning(f"McpAPI路径不是目录：{self.mcpapi_dir}，返回空结果")
            return mcpapi_data
        
        try:
            # 扫描目录中的所有文件
            file_count = 0
            for filename in os.listdir(self.mcpapi_dir):
                file_path = os.path.join(self.mcpapi_dir, filename)
                
                # 只处理.yaml和.yml文件
                if not (filename.lower().endswith('.yaml') or filename.lower().endswith('.yml')):
                    logger.debug(f"跳过非YAML文件：{filename}")
                    continue
                
                # 跳过目录
                if os.path.isdir(file_path):
                    logger.debug(f"跳过目录：{filename}")
                    continue
                
                try:
                    # 解析YAML文件
                    parsed_data = self._parse_yaml_file(file_path)
                    
                    # 使用文件名（不含扩展名）作为键
                    file_key = os.path.splitext(filename)[0]
                    mcpapi_data[file_key] = parsed_data
                    file_count += 1
                    
                    logger.info(f"成功加载McpAPI文件：{filename}")
                    
                except (FileNotFoundError, PermissionError, ValueError) as e:
                    # 忽略格式错误的文件，记录警告日志
                    logger.warning(f"忽略无法解析的文件 {filename}：{str(e)}")
                    continue
                    
                except Exception as e:
                    # 其他未预期的错误也记录警告并继续
                    logger.warning(f"处理文件 {filename} 时发生未知错误：{str(e)}")
                    continue
            
            logger.info(f"McpAPI文件加载完成，共加载 {file_count} 个文件")
            
        except PermissionError as e:
            logger.error(f"无权限访问McpAPI目录：{self.mcpapi_dir}，错误：{str(e)}")
        except Exception as e:
            logger.error(f"扫描McpAPI目录时发生错误：{str(e)}")
        
        return mcpapi_data
    
    def _parse_yaml_file(self, file_path: str) -> Dict[str, Any]:
        """解析单个YAML文件
        
        Args:
            file_path: YAML文件的完整路径
            
        Returns:
            Dict[str, Any]: 解析后的字典数据
            
        Raises:
            FileNotFoundError: 文件不存在
            PermissionError: 文件权限错误
            ValueError: 文件格式错误
        """
        logger.debug(f"开始解析YAML文件：{file_path}")
        
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"YAML文件不存在：{file_path}")
            
            # 读取并解析YAML文件
            with open(file_path, 'r', encoding='utf-8') as file:
                try:
                    parsed_data = yaml.safe_load(file)
                    if parsed_data is None:
                        logger.warning(f"YAML文件为空：{file_path}")
                        return {}
                    
                    if not isinstance(parsed_data, dict):
                        raise ValueError(f"YAML文件根节点必须是字典类型：{file_path}")
                    
                    logger.debug(f"YAML文件解析成功：{file_path}")
                    return parsed_data
                    
                except yaml.YAMLError as e:
                    raise ValueError(f"YAML格式错误：{file_path}, 错误：{str(e)}")
                    
        except PermissionError as e:
            logger.error(f"读取YAML文件权限错误：{file_path}, 错误：{str(e)}")
            raise PermissionError(f"无权限读取文件：{file_path}")
            
        except Exception as e:
            logger.error(f"解析YAML文件失败：{file_path}, 错误：{str(e)}")
            raise
