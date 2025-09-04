"""
腾讯云 TKE 相关操作工具模块
"""

# 常量定义
DEFAULT_REGION = "ap-guangzhou"
DEFAULT_CLUSTER_LEVEL = "L50"
VALID_REGIONS = ["ap-guangzhou", "ap-beijing", "ap-shanghai"]
VALID_CLUSTER_LEVELS = ["L5", "L50", "L200", "L1000", "L5000"]

import json
import logging
from typing import Dict, Any

# 设置日志记录
logger = logging.getLogger(__name__)

try:
    from tencentcloud.tke.v20180525 import tke_client, models as tke_models
    from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
    from .client import get_tke_client, get_common_client, has_credentials
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


def create_cluster(params: Dict[str, Any]) -> str:
    """创建TKE集群
    
    Args:
        params: 集群创建参数，包含：
            - ClusterBasicSettings.ClusterName: 集群名称(可选)
            - ClusterBasicSettings.ClusterLevel: 集群规格(可选,默认L50)
            - Region: 地域(必填)
            - ClusterBasicSettings.ClusterOs: 操作系统镜像ID(必填)
            - ClusterBasicSettings.VpcId: 私有网络ID(必填)
            - ClusterCIDRSettings.EniSubnetIds: 子网ID集合(必填)
            - ClusterCIDRSettings.ServiceCIDR: Service CIDR(必填)
    
    Returns:
        str: API响应结果的JSON字符串，格式：
        {
            "Response": {
                "ClusterId": "cls-7ph3twqe",
                "RequestId": "eac6b301-a322-493a-8e36-83b295459397"
            }
        }
    
    Raises:
        Exception: 当API调用失败时抛出异常
    """
    try:
        logger.info(f"开始创建TKE集群，参数: {params}")
        
        # 参数验证
        _validate_create_cluster_params(params)
        
        if not TENCENTCLOUD_AVAILABLE or not has_credentials():
            # 模拟模式：返回模拟响应
            logger.info("使用模拟模式创建集群")
            return _mock_create_cluster_response(params)
        
        # 实际API调用
        region = params.get("Region")
        client = get_tke_client(region)
        
        # 构建请求参数
        req_params = _build_create_cluster_request(params)
        
        # 调用API
        req = tke_models.CreateClusterRequest()
        req.from_json_string(json.dumps(req_params))
        resp = client.CreateCluster(req)
        
        logger.info("TKE集群创建成功")
        return resp.to_json_string()
        
    except TencentCloudSDKException as e:
        logger.error(f"TKE API调用失败: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"创建TKE集群失败: {str(e)}")
        raise e


def delete_cluster(params: Dict[str, Any]) -> str:
    """删除TKE集群
    
    Args:
        params: 删除参数，包含：
            - ClusterId: 集群ID(必填)
    
    Returns:
        str: API响应结果的JSON字符串，格式：
        {
            "Response": {
                "RequestId": "eac6b301-a322-493a-8e36-83b295459397"
            }
        }
    
    Raises:
        Exception: 当API调用失败时抛出异常
    """
    try:
        logger.info(f"开始删除TKE集群，参数: {params}")
        
        # 参数验证
        _validate_delete_cluster_params(params)
        
        if not TENCENTCLOUD_AVAILABLE or not has_credentials():
            # 模拟模式：返回模拟响应
            logger.info("使用模拟模式删除集群")
            return _mock_delete_cluster_response(params)
        
        # 实际API调用
        cluster_id = params.get("ClusterId")
        # 从集群ID推断地域（这里使用默认地域，实际应该从集群ID解析）
        region = "ap-guangzhou"  # 默认地域
        client = get_tke_client(region)
        
        # 调用API
        req = tke_models.DeleteClusterRequest()
        req.ClusterId = cluster_id
        req.InstanceDeleteMode = "terminate"
        resp = client.DeleteCluster(req)
        
        logger.info("TKE集群删除成功")
        return resp.to_json_string()
        
    except TencentCloudSDKException as e:
        logger.error(f"TKE API调用失败: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"删除TKE集群失败: {str(e)}")
        raise e


def _validate_create_cluster_params(params: Dict[str, Any]) -> None:
    """验证创建集群参数"""
    required_fields = [
        "Region",
        "ClusterBasicSettings.ClusterOs",
        "ClusterBasicSettings.VpcId",
        "ClusterCIDRSettings.EniSubnetIds",
        "ClusterCIDRSettings.ServiceCIDR"
    ]
    
    for field in required_fields:
        if field not in params or not params[field]:
            raise ValueError(f"必填参数 {field} 不能为空")
    
    # 验证地域
    region = params.get("Region")
    valid_regions = ["ap-guangzhou", "ap-beijing", "ap-shanghai"]
    if region not in valid_regions:
        raise ValueError(f"参数Region必须是以下值之一: {', '.join(valid_regions)}")
    
    # 验证集群规格
    cluster_level = params.get("ClusterBasicSettings.ClusterLevel")
    if cluster_level:
        valid_levels = ["L5", "L50", "L200", "L1000", "L5000"]
        if cluster_level not in valid_levels:
            raise ValueError(f"参数ClusterLevel必须是以下值之一: {', '.join(valid_levels)}")
    
    # 验证子网ID格式
    subnet_ids = params.get("ClusterCIDRSettings.EniSubnetIds", [])
    if not isinstance(subnet_ids, list) or len(subnet_ids) == 0:
        raise ValueError("参数EniSubnetIds必须是非空数组")
    
    # 简单的CIDR格式验证
    service_cidr = params.get("ClusterCIDRSettings.ServiceCIDR")
    if not _is_valid_cidr(service_cidr):
        raise ValueError("参数ServiceCIDR格式无效")


def _validate_delete_cluster_params(params: Dict[str, Any]) -> None:
    """验证删除集群参数"""
    cluster_id = params.get("ClusterId")
    if not cluster_id:
        raise ValueError("必填参数ClusterId不能为空")
    
    if not cluster_id.startswith("cls-"):
        raise ValueError("参数ClusterId格式无效，应以cls-开头")


def _is_valid_cidr(cidr: str) -> bool:
    """验证CIDR格式"""
    if not cidr or "/" not in cidr:
        return False
    try:
        ip, prefix = cidr.split("/")
        # 简单验证IP和前缀长度
        parts = ip.split(".")
        if len(parts) != 4:
            return False
        for part in parts:
            if not (0 <= int(part) <= 255):
                return False
        prefix_len = int(prefix)
        if not (0 <= prefix_len <= 32):
            return False
        return True
    except (ValueError, AttributeError):
        return False


def _build_create_cluster_request(params: Dict[str, Any]) -> Dict[str, Any]:
    """构建创建集群请求参数"""
    req_params = {
        "ClusterType": "MANAGED_CLUSTER",
    }
    
    # 集群基本设置
    cluster_basic = {}
    if params.get("ClusterBasicSettings.ClusterName"):
        cluster_basic["ClusterName"] = params["ClusterBasicSettings.ClusterName"]
    
    cluster_basic["ClusterLevel"] = params.get("ClusterBasicSettings.ClusterLevel", "L5")
    cluster_basic["ClusterOs"] = params["ClusterBasicSettings.ClusterOs"]
    cluster_basic["VpcId"] = params["ClusterBasicSettings.VpcId"]
    
    req_params["ClusterBasicSettings"] = cluster_basic
    
    # 集群CIDR设置
    cluster_cidr = {
        "EniSubnetIds": params["ClusterCIDRSettings.EniSubnetIds"],
        "ServiceCIDR": params["ClusterCIDRSettings.ServiceCIDR"]
    }
    req_params["ClusterCIDRSettings"] = cluster_cidr

    # 集群CIDR设置
    cluster_advanced_settings = {
        "NetworkType": "VPC-CNI",
    }
    req_params["ClusterAdvancedSettings"] = cluster_advanced_settings
    
    return req_params


def _mock_create_cluster_response(params: Dict[str, Any]) -> str:
    """模拟创建集群响应"""
    import uuid
    cluster_id = f"cls-{uuid.uuid4().hex[:8]}"
    request_id = str(uuid.uuid4())
    
    response = {
        "Response": {
            "ClusterId": cluster_id,
            "RequestId": request_id
        }
    }
    return json.dumps(response, ensure_ascii=False)


def _mock_delete_cluster_response(params: Dict[str, Any]) -> str:
    """模拟删除集群响应"""
    import uuid
    request_id = str(uuid.uuid4())
    
    response = {
        "Response": {
            "RequestId": request_id
        }
    }
    return json.dumps(response, ensure_ascii=False)
