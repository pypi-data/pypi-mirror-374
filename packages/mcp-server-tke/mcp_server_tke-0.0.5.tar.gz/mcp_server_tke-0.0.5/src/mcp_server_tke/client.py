"""
腾讯云TKE客户端创建模块
"""
import os
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.common_client import CommonClient
from tencentcloud.tke.v20180525 import tke_client

# 从环境变量中读取认证信息
secret_id = os.getenv("TENCENTCLOUD_SECRET_ID")
secret_key = os.getenv("TENCENTCLOUD_SECRET_KEY")

def has_credentials() -> bool:
    """检查是否有有效的认证信息"""
    return secret_id is not None and secret_key is not None and secret_id.strip() != "" and secret_key.strip() != ""

def get_tke_client(region: str) -> tke_client.TkeClient:
    """
    创建并返回TKE客户端

    Args:
        region: 地域信息

    Returns:
        TkeClient: TKE客户端实例
    """
    cred = credential.Credential(secret_id, secret_key)

    http_profile = HttpProfile()
    http_profile.endpoint = "tke.tencentcloudapi.com"

    client_profile = ClientProfile()
    client_profile.httpProfile = http_profile
    client_profile.request_client = "MCP-Server"

    return tke_client.TkeClient(cred, region, client_profile)

def get_common_client(region: str, product="tke", version="2018-05-25") -> CommonClient:
    """
    创建并返回通用客户端实例

    Args:
        region: 地域信息
        product: 产品名称
        version: 产品版本

    Returns:
        CommonClient: 通用客户端实例
    """
    cred = credential.Credential(secret_id, secret_key)

    http_profile = HttpProfile()
    http_profile.endpoint = "tke.tencentcloudapi.com"

    client_profile = ClientProfile()
    client_profile.httpProfile = http_profile
    client_profile.request_client = "MCP-Server"

    return CommonClient(product, version, cred, region, profile=client_profile)
