"""
TKE客户端模块单元测试
"""
import os
import unittest
from unittest.mock import patch, MagicMock
import sys

# 添加src路径以便导入模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from mcp_server_tke.client import get_tke_client, get_common_client
    TENCENTCLOUD_AVAILABLE = True
except ImportError:
    TENCENTCLOUD_AVAILABLE = False


class TestTKEClient(unittest.TestCase):
    """TKE客户端测试类"""

    def setUp(self):
        """测试前设置"""
        # 清理环境变量
        self.original_env = {}
        for key in ['TENCENTCLOUD_SECRET_ID', 'TENCENTCLOUD_SECRET_KEY']:
            self.original_env[key] = os.environ.get(key)
            if key in os.environ:
                del os.environ[key]

    def tearDown(self):
        """测试后清理"""
        # 恢复环境变量
        for key, value in self.original_env.items():
            if value is not None:
                os.environ[key] = value

    @unittest.skipUnless(TENCENTCLOUD_AVAILABLE, "TencentCloud SDK not available")
    @patch('mcp_server_tke.client.tke_client.TkeClient')
    @patch('mcp_server_tke.client.credential.Credential')
    def test_get_tke_client_with_region(self, mock_credential, mock_tke_client):
        """测试带地域参数创建TKE客户端"""
        
        # 模拟返回值
        mock_cred_instance = MagicMock()
        mock_credential.return_value = mock_cred_instance
        mock_client_instance = MagicMock()
        mock_tke_client.return_value = mock_client_instance
        
        # 调用函数
        result = get_tke_client('ap-guangzhou')
        
        # 验证调用
        mock_tke_client.assert_called_once()
        self.assertEqual(result, mock_client_instance)

    @unittest.skipUnless(TENCENTCLOUD_AVAILABLE, "TencentCloud SDK not available")
    @patch('mcp_server_tke.client.tke_client.TkeClient')
    @patch('mcp_server_tke.client.credential.Credential')
    def test_get_tke_client_default_region(self, mock_credential, mock_tke_client):
        """测试使用默认地域创建TKE客户端"""
        # 模拟返回值
        mock_cred_instance = MagicMock()
        mock_credential.return_value = mock_cred_instance
        mock_client_instance = MagicMock()
        mock_tke_client.return_value = mock_client_instance
        
        # 调用函数（传入空地域）
        result = get_tke_client('')
        
        # 验证调用
        mock_tke_client.assert_called_once()
        self.assertEqual(result, mock_client_instance)

    @unittest.skipUnless(TENCENTCLOUD_AVAILABLE, "TencentCloud SDK not available")
    @patch('mcp_server_tke.client.CommonClient')
    @patch('mcp_server_tke.client.credential.Credential')
    def test_get_common_client(self, mock_credential, mock_common_client):
        """测试创建通用客户端"""
        # 模拟返回值
        mock_cred_instance = MagicMock()
        mock_credential.return_value = mock_cred_instance
        mock_client_instance = MagicMock()
        mock_common_client.return_value = mock_client_instance
        
        # 调用函数
        result = get_common_client('ap-guangzhou')
        
        # 验证调用
        mock_common_client.assert_called_once()
        self.assertEqual(result, mock_client_instance)

if __name__ == '__main__':
    unittest.main()
