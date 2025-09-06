# 腾讯云 TKE MCP Server（中文版）

腾讯云容器服务(TKE) Model Context Protocol (MCP) 服务器，提供标准化的TKE集群管理接口。

## 功能特性
- **集群生命周期管理**：创建、删除

## 工具列表（Tools）

### 集群生命周期
| 工具名称 | 功能说明 |
|---|---|
| `CreateCluster` | 创建集群 |
| `DeleteCluster` | 删除集群 |
| `ModifyClusterAttribute` | 修改集群属性 |
| `DescribeClusters` | 查询集群列表 |

## 快速开始
### 1. 准备腾讯云凭证
- 登录 [腾讯云控制台](https://console.cloud.tencent.com/)，进入「访问管理」→「访问密钥」获取 `SecretId` 与 `SecretKey`

### 2. 配置环境变量
```bash
export TENCENTCLOUD_SECRET_ID=你的SecretId
export TENCENTCLOUD_SECRET_KEY=你的SecretKey
```

### 3. Claude Desktop 配置
编辑 `claude_desktop_config.json`（Mac 默认路径 `~/Library/Application Support/Claude/claude_desktop_config.json`），加入：

```json
{
  "mcpServers": {
    "tencent-tke": {
      "command": "uv",
      "args": ["run", "mcp-server-tke"],
      "env": {
        "TENCENTCLOUD_SECRET_ID": "你的SecretId",
        "TENCENTCLOUD_SECRET_KEY": "你的SecretKey",
      }
    }
  }
}
```

### 4. 安装
```bash
pip install mcp-server-tke
```

### 5. 贡献
#### 通过云API转化成MCP API文件
1. 通过云API导出OpenAPI格式的json文件，放到`openapi/`目录下。
2. 使用 `openapi-to-mcp-tools` 工具将OpenAPI json文件转换为MCP API yaml文件，放置在 `./mcpapi/` 目录下。
```bash
# 安装工具
go install github.com/higress-group/openapi-to-mcpserver/cmd/openapi-to-mcp@latest

# 转换示例
openapi-to-mcp --input openapi/tke_2018-05-25_DeleteCluster.json --output mcpapi/2018-05-25_DeleteCluster.yaml
```
3. 为了让AI有更好的体验，适当的删除`2018-05-25_DeleteCluster.yaml`不需要的API参数，并补充必要的描述信息。
4. 启动 `mcp-server-tke`，程序自动加载文件，即可通过Claude调用新增的MCP工具。

## 许可证
MIT License，详见 LICENSE 文件。
