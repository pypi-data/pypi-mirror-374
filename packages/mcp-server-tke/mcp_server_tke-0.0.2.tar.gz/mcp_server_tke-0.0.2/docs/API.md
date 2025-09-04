# API 参考文档

本文档提供TKE MCP服务器的详细API参考信息。

## 概述

TKE MCP服务器通过Model Context Protocol提供标准化的腾讯云容器服务接口。所有API调用都遵循MCP协议规范。

## 工具列表

### 1. create_cluster

**功能**: 创建腾讯云TKE集群

**MCP调用格式**:
```json
{
  "method": "tools/call",
  "params": {
    "name": "create_cluster",
    "arguments": {
      // 参数详见下方
    }
  }
}
```

**参数说明**:

| 参数名 | 类型 | 必填 | 描述 | 示例值 |
|--------|------|------|------|--------|
| `Region` | string | ✅ | 地域标识 | "ap-guangzhou" |
| `ClusterBasicSettings.ClusterName` | string | ❌ | 集群名称 | "my-tke-cluster" |
| `ClusterBasicSettings.ClusterLevel` | string | ❌ | 集群规格，默认L50 | "L50" |
| `ClusterBasicSettings.ClusterOs` | string | ✅ | 操作系统镜像ID | "ubuntu18.04.1x86_64" |
| `ClusterBasicSettings.VpcId` | string | ✅ | 私有网络ID | "vpc-12345678" |
| `ClusterCIDRSettings.EniSubnetIds` | array | ✅ | 子网ID列表 | ["subnet-12345678"] |
| `ClusterCIDRSettings.ServiceCIDR` | string | ✅ | Service网段 | "10.96.0.0/12" |

**支持的地域**:
- `ap-guangzhou`: 广州
- `ap-beijing`: 北京
- `ap-shanghai`: 上海

**支持的集群规格**:
- `L5`: 5节点
- `L50`: 50节点（默认）
- `L200`: 200节点
- `L1000`: 1000节点
- `L5000`: 5000节点

**返回格式**:
```json
{
  "Response": {
    "ClusterId": "cls-7ph3twqe",
    "RequestId": "eac6b301-a322-493a-8e36-83b295459397"
  }
}
```

**错误示例**:
```json
{
  "error": "必填参数 Region 不能为空"
}
```

### 2. delete_cluster

**功能**: 删除指定的TKE集群

**MCP调用格式**:
```json
{
  "method": "tools/call", 
  "params": {
    "name": "delete_cluster",
    "arguments": {
      "ClusterId": "cls-12345678"
    }
  }
}
```

**参数说明**:

| 参数名 | 类型 | 必填 | 描述 | 示例值 |
|--------|------|------|------|--------|
| `ClusterId` | string | ✅ | 集群ID，以cls-开头 | "cls-12345678" |
| `InstanceDeleteMode` | string | ❌ | 实例删除模式，默认retain | "retain" |
| `ResourceDeleteOptions.0.ResourceType` | string | ❌ | 资源类型 | "CBS" |
| `ResourceDeleteOptions.0.DeleteMode` | string | ❌ | 删除模式 | "retain" |

**返回格式**:
```json
{
  "Response": {
    "RequestId": "eac6b301-a322-493a-8e36-83b295459397"
  }
}
```

**错误示例**:
```json
{
  "error": "参数ClusterId格式无效，应以cls-开头"
}
```

## 参数验证规则

### 地域验证
- 必须是支持的地域之一
- 不能为空字符串

### 集群ID验证
- 必须以"cls-"开头
- 不能为空

### 网络配置验证
- VpcId必须以"vpc-"开头
- SubnetIds必须是非空数组
- ServiceCIDR必须是有效的CIDR格式

### CIDR格式验证
有效的CIDR格式示例:
- `10.0.0.0/16`
- `172.16.0.0/12`
- `192.168.0.0/16`
- `10.96.0.0/12`

## 错误处理

### 错误类型

1. **参数验证错误** (ValueError)
   ```json
   {
     "error": "必填参数 Region 不能为空",
     "type": "ValidationError"
   }
   ```

2. **API调用错误** (TencentCloudSDKException)
   ```json
   {
     "error": "权限不足",
     "code": "AuthFailure",
     "type": "APIError"
   }
   ```

3. **系统错误** (Exception)
   ```json
   {
     "error": "内部服务器错误",
     "type": "InternalError"
   }
   ```

### 常见错误码

| 错误码 | 描述 | 解决方案 |
|--------|------|----------|
| `AuthFailure` | 认证失败 | 检查AccessKey配置 |
| `InvalidParameter` | 参数无效 | 检查参数格式和值 |
| `ResourceNotFound` | 资源不存在 | 确认资源ID正确 |
| `LimitExceeded` | 超出配额限制 | 联系腾讯云提升配额 |

## 使用示例

### Python SDK调用

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

try:
    result = create_cluster(create_params)
    print("集群创建成功:", result)
except ValueError as e:
    print("参数错误:", e)
except Exception as e:
    print("系统错误:", e)

# 删除集群
delete_params = {
    "ClusterId": "cls-example123"
}

try:
    result = delete_cluster(delete_params)
    print("集群删除成功:", result)
except Exception as e:
    print("删除失败:", e)
```

### cURL调用示例

```bash
# 通过MCP协议调用
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "create_cluster",
      "arguments": {
        "Region": "ap-guangzhou",
        "ClusterBasicSettings.ClusterName": "api-test-cluster",
        "ClusterBasicSettings.ClusterOs": "ubuntu18.04.1x86_64",
        "ClusterBasicSettings.VpcId": "vpc-12345678",
        "ClusterCIDRSettings.EniSubnetIds": ["subnet-12345678"],
        "ClusterCIDRSettings.ServiceCIDR": "10.96.0.0/12"
      }
    }
  }'
```

## 最佳实践

### 1. 参数准备
- 提前准备好VPC和子网资源
- 选择合适的地域和集群规格
- 确保ServiceCIDR不与VPC冲突

### 2. 错误处理
- 始终包装API调用在try-catch块中
- 记录详细的错误信息用于调试
- 实现适当的重试机制

### 3. 资源管理
- 记录创建的集群ID用于后续管理
- 及时清理不需要的集群资源
- 监控集群状态和资源使用

### 4. 安全建议
- 使用最小权限原则配置AccessKey
- 定期轮换访问密钥
- 不要在代码中硬编码密钥信息

## 限制和配额

### API调用限制
- 每秒最多10次API调用
- 单个账号最多创建100个集群
- 集群名称最长63个字符

### 资源限制
- 单个集群最多5000个节点
- ServiceCIDR最小为/24网段
- 集群名称必须在地域内唯一

## 版本兼容性

| API版本 | 支持状态 | 说明 |
|---------|----------|------|
| 2018-05-25 | ✅ 支持 | 当前使用版本 |
| 2022-05-01 | 🚧 计划中 | 未来版本 |

## 更新日志

### v0.1.0 (2025-09-03)
- ✅ 实现create_cluster工具
- ✅ 实现delete_cluster工具
- ✅ 添加完整参数验证
- ✅ 支持模拟模式
- ✅ 完整的错误处理
