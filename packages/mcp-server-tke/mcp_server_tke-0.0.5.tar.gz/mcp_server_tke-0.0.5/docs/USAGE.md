# TKE MCP服务器使用指南

本文档提供了TKE MCP服务器的完整使用指南，包括安装、配置和使用说明。

## 快速开始

### 1. 环境准备

确保你的系统满足以下要求：
- Python 3.8+
- 腾讯云账号和API密钥

### 2. 安装依赖

```bash
# 安装腾讯云SDK（可选，不安装将使用模拟模式）
pip install tencentcloud-sdk-python

# 安装MCP库（生产环境需要）
pip install model-context-protocol
```

### 3. 配置环境变量

```bash
export TENCENTCLOUD_SECRET_ID="your_secret_id"
export TENCENTCLOUD_SECRET_KEY="your_secret_key"
```

### 4. 启动服务器

```bash
# 方法1: 直接运行模块
python3 -m mcp_server_tke

# 方法2: 运行启动脚本
python3 src/mcp_server_tke/server.py
```

## 功能说明

### 支持的工具

TKE MCP服务器提供以下工具：

#### 1. create_cluster - 创建TKE集群

**功能**: 创建腾讯云容器服务(TKE)集群

**参数**:
- `Region` (必填): 地域，如 "ap-guangzhou"
- `ClusterBasicSettings.ClusterName` (可选): 集群名称
- `ClusterBasicSettings.ClusterLevel` (可选): 集群规格，默认L50
- `ClusterBasicSettings.ClusterOs` (必填): 操作系统镜像ID
- `ClusterBasicSettings.VpcId` (必填): 私有网络ID
- `ClusterCIDRSettings.EniSubnetIds` (必填): 子网ID列表
- `ClusterCIDRSettings.ServiceCIDR` (必填): Service CIDR

**返回值**: JSON格式的API响应，包含集群ID

**示例**:
```json
{
  "Region": "ap-guangzhou",
  "ClusterBasicSettings.ClusterName": "my-tke-cluster",
  "ClusterBasicSettings.ClusterLevel": "L50",
  "ClusterBasicSettings.ClusterOs": "ubuntu18.04.1x86_64",
  "ClusterBasicSettings.VpcId": "vpc-12345678",
  "ClusterCIDRSettings.EniSubnetIds": ["subnet-12345678"],
  "ClusterCIDRSettings.ServiceCIDR": "10.96.0.0/12"
}
```

#### 2. delete_cluster - 删除TKE集群

**功能**: 删除指定的TKE集群

**参数**:
- `ClusterId` (必填): 集群ID，格式为 cls-xxxxxxxx
- `InstanceDeleteMode` (可选): 实例删除模式，默认 "retain"
- `ResourceDeleteOptions.0.ResourceType` (可选): 资源类型
- `ResourceDeleteOptions.0.DeleteMode` (可选): 删除模式

**返回值**: JSON格式的API响应

**示例**:
```json
{
  "ClusterId": "cls-12345678",
  "InstanceDeleteMode": "retain"
}
```

## 使用示例

### 基本用法

```python
from mcp_server_tke.tool_tke import create_cluster, delete_cluster

# 创建集群
create_params = {
    "Region": "ap-guangzhou",
    "ClusterBasicSettings.ClusterName": "test-cluster",
    "ClusterBasicSettings.ClusterOs": "ubuntu18.04.1x86_64",
    "ClusterBasicSettings.VpcId": "vpc-example",
    "ClusterCIDRSettings.EniSubnetIds": ["subnet-example"],
    "ClusterCIDRSettings.ServiceCIDR": "10.96.0.0/12"
}

result = create_cluster(create_params)
print(result)

# 删除集群
delete_params = {
    "ClusterId": "cls-12345678"
}

result = delete_cluster(delete_params)
print(result)
```

### 错误处理

```python
try:
    result = create_cluster(params)
    print("集群创建成功:", result)
except ValueError as e:
    print("参数验证错误:", e)
except Exception as e:
    print("API调用失败:", e)
```

### 客户端配置

```python
import os
from mcp_server_tke.client import get_tke_client

# 设置环境变量
os.environ["TENCENTCLOUD_SECRET_ID"] = "your_secret_id"
os.environ["TENCENTCLOUD_SECRET_KEY"] = "your_secret_key"

# 获取客户端
client = get_tke_client("ap-guangzhou")
```

## 测试和验证

### 运行测试套件

```bash
# 运行所有测试
python3 tests/test_tool_tke.py
python3 tests/test_client.py
python3 tests/test_mcp_integration.py

# 运行端到端测试
python3 tests/test_e2e.py

# 运行架构一致性验证
python3 tests/test_architecture_consistency.py

# 运行完整验证
python3 scripts/verify_server.py
```

### 运行示例

```bash
# 运行使用示例
python3 examples/usage_examples.py
```

## 生产环境部署

### Docker部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install -r requirements.txt

# 复制源码
COPY src/ ./src/

# 设置环境变量
ENV TENCENTCLOUD_SECRET_ID=""
ENV TENCENTCLOUD_SECRET_KEY=""

# 启动服务
CMD ["python3", "-m", "mcp_server_tke"]
```

### 系统服务

```ini
# /etc/systemd/system/tke-mcp-server.service
[Unit]
Description=TKE MCP Server
After=network.target

[Service]
Type=simple
User=mcp
WorkingDirectory=/opt/tke-mcp-server
Environment=TENCENTCLOUD_SECRET_ID=your_secret_id
Environment=TENCENTCLOUD_SECRET_KEY=your_secret_key
ExecStart=/usr/bin/python3 -m mcp_server_tke
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## 故障排除

### 常见问题

1. **模块导入错误**
   - 确保Python路径正确
   - 检查依赖是否安装

2. **腾讯云API调用失败**
   - 检查访问密钥配置
   - 确认地域参数正确
   - 验证网络连接

3. **参数验证失败**
   - 检查必填参数是否提供
   - 验证参数格式是否正确

### 日志配置

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## API参考

详细的API参考请参见：
- [腾讯云TKE API文档](https://cloud.tencent.com/document/product/457)
- [MCP协议规范](https://spec.modelcontextprotocol.io/)

## 支持和反馈

如有问题或建议，请通过以下方式联系：
- 提交Issue到项目仓库
- 查看测试报告和验证结果
- 参考示例代码和文档
