"""
TKE工具模块单元测试
"""
import json
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# 添加src路径以便导入模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# 直接导入工具模块，避免通过__init__.py导入
import mcp_server_tke.tool_tke as tool_tke


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

    def test_validate_delete_cluster_params_valid(self):
        """测试有效的删除集群参数验证"""
        params = {
            "ClusterId": "cls-12345678"
        }
        
        # 不应该抛出异常
        tool_tke._validate_delete_cluster_params(params)

    def test_validate_delete_cluster_params_missing(self):
        """测试缺少集群ID参数"""
        params = {}
        
        with self.assertRaises(ValueError) as context:
            tool_tke._validate_delete_cluster_params(params)
        
        self.assertIn("ClusterId不能为空", str(context.exception))

    def test_validate_delete_cluster_params_invalid_format(self):
        """测试无效的集群ID格式"""
        params = {
            "ClusterId": "invalid-id"
        }
        
        with self.assertRaises(ValueError) as context:
            tool_tke._validate_delete_cluster_params(params)
        
        self.assertIn("ClusterId格式无效", str(context.exception))

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

    def test_delete_cluster_invalid_params(self):
        """测试无效参数删除集群"""
        params = {
            "ClusterId": "invalid-id"
        }
        
        with self.assertRaises(ValueError):
            tool_tke.delete_cluster(params)

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

        """测试模拟模式下的删除集群"""
        params = {
            "ClusterId": response["ClusterId"]
        }
        
        result = tool_tke.delete_cluster(params)
        
        # 验证响应格式
        response = json.loads(result)
        self.assertIn("RequestId", response)


if __name__ == '__main__':
    unittest.main()
