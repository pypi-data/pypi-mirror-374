# 贡献指南

感谢您对TKE MCP服务器项目的关注！本指南将帮助您了解如何为项目做出贡献。

## 🤝 如何贡献

### 报告问题

如果您发现了bug或有功能建议，请：

1. **搜索已有的Issues**，避免重复报告
2. **使用Issue模板**，提供详细信息
3. **包含复现步骤**，帮助我们快速定位问题
4. **提供环境信息**（Python版本、操作系统等）

### 提交代码

1. **Fork项目**到您的GitHub账户
2. **创建特性分支**: `git checkout -b feature/amazing-feature`
3. **提交更改**: `git commit -m 'Add amazing feature'`
4. **推送分支**: `git push origin feature/amazing-feature`
5. **创建Pull Request**

## 📋 开发环境设置

### 环境要求

- Python 3.8+
- Git
- 腾讯云账号（可选，用于真实API测试）

### 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/your-username/tke-mcp.git
cd tke-mcp

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 3. 安装开发依赖
pip install -r requirements-dev.txt

# 4. 安装可选依赖
pip install tencentcloud-sdk-python  # 用于真实API测试
pip install model-context-protocol   # 用于MCP集成测试
```

### 环境配置

```bash
# 设置测试环境变量（可选）
export TENCENTCLOUD_SECRET_ID="test_secret_id"
export TENCENTCLOUD_SECRET_KEY="test_secret_key"
```

## 🧪 测试指南

### 运行测试

```bash
# 运行所有测试
python3 -m pytest tests/

# 运行特定测试文件
python3 tests/test_tool_tke.py

# 运行端到端测试
python3 tests/test_e2e.py

# 生成测试覆盖率报告
python3 -m pytest --cov=src tests/
```

### 测试要求

- **新功能**必须包含对应的单元测试
- **测试覆盖率**不得低于当前水平(90%+)
- **所有测试**必须通过才能合并
- **端到端测试**必须验证完整功能流程

### 测试最佳实践

```python
# 好的测试示例
def test_create_cluster_with_valid_params():
    """测试使用有效参数创建集群"""
    params = {
        "Region": "ap-guangzhou",
        "ClusterBasicSettings.ClusterOs": "ubuntu18.04.1x86_64",
        "ClusterBasicSettings.VpcId": "vpc-123456",
        "ClusterCIDRSettings.EniSubnetIds": ["subnet-123456"],
        "ClusterCIDRSettings.ServiceCIDR": "10.96.0.0/12"
    }
    
    result = create_cluster(params)
    
    # 验证返回结果
    assert result is not None
    assert isinstance(result, str)
    
    # 验证JSON格式
    data = json.loads(result)
    assert "Response" in data
    assert "ClusterId" in data["Response"]
```

## 📝 代码规范

### Python代码风格

遵循[PEP 8](https://www.python.org/dev/peps/pep-0008/)编码规范：

```python
# 函数命名：使用小写和下划线
def create_cluster(params: Dict[str, Any]) -> str:
    """创建TKE集群
    
    Args:
        params: 集群创建参数
        
    Returns:
        str: JSON格式的API响应
        
    Raises:
        ValueError: 当参数验证失败时
    """
    pass

# 常量命名：使用大写和下划线
DEFAULT_REGION = "ap-guangzhou"
VALID_REGIONS = ["ap-guangzhou", "ap-beijing", "ap-shanghai"]

# 类命名：使用驼峰命名法
class TKEClusterManager:
    """TKE集群管理器"""
    pass
```

### 文档字符串

使用Google风格的文档字符串：

```python
def validate_cluster_params(params: Dict[str, Any]) -> None:
    """验证集群参数
    
    Args:
        params: 包含集群配置的参数字典
            - Region (str): 地域标识
            - ClusterBasicSettings.ClusterOs (str): 操作系统
            
    Raises:
        ValueError: 当必填参数缺失或格式无效时
        
    Example:
        >>> params = {"Region": "ap-guangzhou"}
        >>> validate_cluster_params(params)
    """
    pass
```

### 类型注解

为所有公共函数添加类型注解：

```python
from typing import Dict, List, Any, Optional

def get_cluster_info(cluster_id: str, region: Optional[str] = None) -> Dict[str, Any]:
    """获取集群信息"""
    pass

def list_clusters(region: str) -> List[Dict[str, Any]]:
    """列出集群"""
    pass
```

## 🏗️ 架构指南

### 项目结构

```
tke-mcp/
├── src/mcp_server_tke/      # 源代码
│   ├── __init__.py          # 模块初始化
│   ├── server.py            # MCP协议层
│   ├── client.py            # 客户端层
│   ├── tool_tke.py          # 业务逻辑层
│   └── config.py            # 配置管理（计划中）
├── tests/                   # 测试代码
├── examples/                # 使用示例
├── scripts/                 # 工具脚本
└── docs/                    # 文档
```

### 设计原则

1. **单一职责**: 每个模块只负责一个功能
2. **依赖注入**: 通过参数传递依赖，便于测试
3. **错误处理**: 统一的错误处理和日志记录
4. **向后兼容**: 新版本保持API兼容性

### 添加新功能

遵循以下步骤添加新的TKE工具：

1. **定义工具接口**（在`tool_tke.py`中）
2. **添加参数验证**
3. **实现业务逻辑**
4. **注册MCP工具**（在`server.py`中）
5. **编写单元测试**
6. **更新文档**

示例：添加"获取集群信息"工具

```python
# 1. tool_tke.py - 添加工具函数
def get_cluster_info(params: Dict[str, Any]) -> str:
    """获取TKE集群信息"""
    _validate_get_cluster_params(params)
    # 实现逻辑...

# 2. server.py - 注册工具
TOOLS = [
    # ... 现有工具
    {
        "name": "get_cluster_info",
        "description": "获取TKE集群详细信息",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ClusterId": {"type": "string", "description": "集群ID"}
            },
            "required": ["ClusterId"]
        }
    }
]
```

## 📚 文档更新

### 文档类型

- **README.md**: 项目概述和快速开始
- **docs/USAGE.md**: 详细使用指南
- **docs/API.md**: API参考文档
- **CHANGELOG.md**: 版本更新记录
- **代码注释**: 函数和类的文档字符串

### 文档要求

- **保持同步**: 代码更改时同步更新文档
- **示例丰富**: 提供完整的使用示例
- **格式统一**: 使用标准的Markdown格式
- **语言规范**: 使用简洁明了的中文

## 🔍 代码审查

### Pull Request要求

- **描述清晰**: 说明修改的目的和影响
- **测试充分**: 包含相应的测试用例
- **文档完整**: 更新相关文档
- **风格一致**: 遵循项目代码规范

### 审查清单

- [ ] 代码风格符合PEP 8
- [ ] 所有函数都有文档字符串
- [ ] 新功能包含单元测试
- [ ] 测试覆盖率没有下降
- [ ] 相关文档已更新
- [ ] 没有引入安全问题
- [ ] 性能没有明显下降

## 🚀 发布流程

### 版本号规范

使用[语义化版本控制](https://semver.org/)：
- `MAJOR.MINOR.PATCH`
- 例如：`1.2.3`

### 发布步骤

1. **更新版本号**
   ```python
   # src/mcp_server_tke/__init__.py
   __version__ = "0.2.0"
   ```

2. **更新CHANGELOG.md**
   ```markdown
   ## [0.2.0] - 2025-09-04
   
   ### ✨ 新增功能
   - 添加获取集群信息工具
   ```

3. **运行完整测试**
   ```bash
   python3 scripts/verify_server.py
   ```

4. **提交并打标签**
   ```bash
   git add .
   git commit -m "Release v0.2.0"
   git tag v0.2.0
   git push origin main --tags
   ```

## 🤔 需要帮助？

- 📖 查看[文档目录](docs/)
- 🐛 [报告问题](https://github.com/your-repo/issues)
- 💬 [讨论区](https://github.com/your-repo/discussions)
- 📧 联系维护团队

## 📄 许可证

本项目采用MIT许可证，详见[LICENSE](LICENSE)文件。

感谢您的贡献！🎉
