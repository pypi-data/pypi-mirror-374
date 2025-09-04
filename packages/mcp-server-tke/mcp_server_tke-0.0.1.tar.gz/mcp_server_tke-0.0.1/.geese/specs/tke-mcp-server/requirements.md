# TKE MCP服务器需求文档

## 功能概述

TKE MCP服务器是一个基于Model Context Protocol (MCP) 的腾讯云容器服务（TKE）管理工具，模拟现有 `mcp_server_cvm` 的代码结构和逻辑，为用户提供TKE集群的创建和删除功能。该服务通过MCP协议与外部系统交互，简化TKE集群管理操作。

## 需求列表

### 1. TKE集群创建功能

**用户故事**: 作为一名云运维工程师，我希望能够通过MCP协议创建TKE集群，以便快速部署Kubernetes环境来运行容器化应用。

**验收标准**:
1. **WHEN** 用户调用 `CreateCluster` 工具，**THEN** 系统应接受以下参数：
   - `ClusterBasicSettings.ClusterName` (string, 可选) - 集群名称
   - `ClusterBasicSettings.ClusterLevel` (string, 可选, 默认L50) - 集群规格，可选值：L5、L50、L200、L1000、L5000
   - `Region` (string, 必填) - 地域，可选值：ap-guangzhou、ap-beijing、ap-shanghai
   - `ClusterBasicSettings.ClusterOs` (string, 必填) - 操作系统镜像ID
   - `ClusterBasicSettings.VpcId` (string, 必填) - 私有网络ID
   - `ClusterCIDRSettings.EniSubnetIds` ([]string, 必填) - 子网ID集合
   - `ClusterCIDRSettings.ServiceCIDR` (string, 必填) - Service CIDR

2. **WHEN** 用户未提供可选参数，**THEN** 系统应使用默认值（ClusterLevel默认为L50）

3. **WHEN** 用户未提供必填参数，**THEN** 系统应返回明确的错误提示

4. **WHEN** 集群创建成功，**THEN** 系统应返回包含以下字段的JSON响应：
   ```json
   {
     "Response": {
       "ClusterId": "cls-7ph3twqe",
       "RequestId": "eac6b301-a322-493a-8e36-83b295459397"
     }
   }
   ```

5. **WHEN** 创建过程中发生错误，**THEN** 系统应返回包含错误信息的响应

### 2. TKE集群删除功能

**用户故事**: 作为一名云运维工程师，我希望能够通过MCP协议删除不需要的TKE集群，以便释放云资源并控制成本。

**验收标准**:
1. **WHEN** 用户调用 `DeleteCluster` 工具，**THEN** 系统应接受以下参数：
   - `ClusterId` (string, 必填) - 集群ID

2. **WHEN** 用户未提供集群ID，**THEN** 系统应返回明确的错误提示

3. **WHEN** 集群删除成功，**THEN** 系统应返回包含以下字段的JSON响应：
   ```json
   {
     "Response": {
       "RequestId": "eac6b301-a322-493a-8e36-83b295459397"
     }
   }
   ```

4. **WHEN** 删除过程中发生错误，**THEN** 系统应返回包含错误信息的响应

### 3. MCP服务器架构兼容性

**用户故事**: 作为一名开发人员，我希望TKE MCP服务器能够与现有的MCP基础设施无缝集成，以便复用现有的工具和流程。

**验收标准**:
1. **WHEN** 启动TKE MCP服务器，**THEN** 系统应使用与CVM MCP服务器相同的基础架构模式

2. **WHEN** 外部系统请求工具列表，**THEN** 系统应返回包含 `CreateCluster` 和 `DeleteCluster` 的工具定义

3. **WHEN** 接收到工具调用请求，**THEN** 系统应按照MCP协议标准处理并响应

4. **WHEN** 系统初始化，**THEN** 应正确设置服务器名称、版本和能力描述

### 4. 代码结构一致性

**用户故事**: 作为一名维护人员，我希望TKE MCP服务器的代码结构与现有CVM MCP服务器保持一致，以便降低维护成本和学习曲线。

**验收标准**:
1. **WHEN** 查看项目结构，**THEN** 应包含类似的模块组织：
   - `server.py` - 主服务器文件
   - `tool_tke.py` - TKE相关工具实现
   - `client.py` - 客户端封装（如需要）

2. **WHEN** 查看代码实现，**THEN** 应遵循与CVM服务器相同的：
   - 错误处理模式
   - 日志记录方式
   - 参数验证逻辑
   - 响应格式标准化

3. **WHEN** 添加新功能，**THEN** 应能够轻松扩展现有架构

### 5. 参数验证和错误处理

**用户故事**: 作为一名API用户，我希望在传递无效参数时能够收到清晰的错误信息，以便快速定位和修复问题。

**验收标准**:
1. **WHEN** 用户传递无效的地域值，**THEN** 系统应返回支持的地域列表

2. **WHEN** 用户传递无效的集群规格，**THEN** 系统应返回支持的规格选项

3. **WHEN** 用户传递空的必填参数，**THEN** 系统应明确指出哪个参数缺失

4. **WHEN** 用户传递格式错误的CIDR，**THEN** 系统应返回CIDR格式要求

5. **WHEN** 系统出现内部错误，**THEN** 应记录详细日志并返回用户友好的错误信息

### 6. 工具Schema定义

**用户故事**: 作为一名集成开发者，我希望能够通过标准的JSON Schema了解工具的输入要求，以便正确构建调用请求。

**验收标准**:
1. **WHEN** 查询 `CreateCluster` 工具Schema，**THEN** 应包含所有参数的类型、描述和必填标记

2. **WHEN** 查询 `DeleteCluster` 工具Schema，**THEN** 应包含集群ID参数的完整定义

3. **WHEN** 参数有枚举值限制，**THEN** Schema应明确列出所有可接受的值

4. **WHEN** 参数有默认值，**THEN** Schema应在描述中说明默认行为

### 7. 响应数据格式标准化

**用户故事**: 作为一名API消费者，我希望所有响应都遵循一致的格式标准，以便编写通用的响应处理逻辑。

**验收标准**:
1. **WHEN** 任何工具执行成功，**THEN** 响应应包含 `Response` 顶级对象

2. **WHEN** 任何工具执行，**THEN** 响应应包含唯一的 `RequestId` 字段

3. **WHEN** 创建操作成功，**THEN** 响应应包含相关资源的ID字段

4. **WHEN** 操作失败，**THEN** 响应格式应与腾讯云API错误响应保持一致

5. **WHEN** 返回列表数据，**THEN** 应包含适当的分页信息（如适用）
