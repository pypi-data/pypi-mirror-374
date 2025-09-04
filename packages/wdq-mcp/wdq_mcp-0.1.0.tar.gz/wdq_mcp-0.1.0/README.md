# 五洞桥社区 MCP 服务包 (wdq-mcp)

[![PyPI version](https://badge.fury.io/py/wdq-mcp.svg)](https://badge.fury.io/py/wdq-mcp)
[![Python Support](https://img.shields.io/pypi/pyversions/wdq-mcp.svg)](https://pypi.org/project/wdq-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

五洞桥社区'小五微网共治共享'微网实格管理智慧平台的 Model Context Protocol (MCP) 服务包。

## 项目简介

本项目是为四川省成都双流区东升街道五洞桥社区开发的智慧平台 MCP 服务，基于 Model Context Protocol 协议，提供社区管理、网格管理、人员管理等多种功能的数据查询和管理接口。

### 主要功能模块

- **活动管理**: 社区活动列表、签到统计等
- **社区管理**: 小区信息、建筑单元、房屋管理
- **网格管理**: 微网格、一般网格、总网格管理
- **人员管理**: 群众档案、网格员管理、社区干部
- **党建管理**: 党员事迹、党建学习、组织生活
- **政务服务**: 政务事项、服务分类
- **投诉管理**: 投诉处理、统计分析
- **预警信息**: 预警发布、任务管理
- **信息发布**: 社区公告、辟谣信息
- **通讯录**: 联系人管理
- **商户管理**: 商户信息查询
- **投票管理**: 投票活动管理
- **用户管理**: 用户信息管理

## 安装

### 从 PyPI 安装

```bash
pip install wdq-mcp
```

### 从源码安装

```bash
git clone https://github.com/wifiming/wdq-mcp.git
cd wdq-mcp
pip install -e .
```

## 配置

使用前需要设置以下环境变量：

```bash
# 后端 Django 服务地址
export MCP_ADMIN_BASE_URL="https://your-backend-url.com"

# 与后端拦截器一致的密钥
export MCP_SECRET_KEY="your-secret-key"

# 可选：请求超时时间（秒），默认 15
export ADMIN_API_TIMEOUT="15"

# 可选：调试模式，默认开启
export MCP_DEBUG="1"
```

## 使用方法

### 作为命令行工具

安装后可以直接使用命令行工具：

```bash
wdq-mcp
```

### 作为 Python 包

```python
from wdq_mcp import WudongqiaoMCP

# 创建 MCP 服务实例
mcp_server = WudongqiaoMCP(
    base_url="https://your-backend-url.com",
    secret_key="your-secret-key"
)

# 启动服务
mcp_server.run()
```

### 在 MCP 客户端中使用

在支持 MCP 的客户端（如 Claude Desktop）中配置：

```json
{
  "mcpServers": {
    "wdq-mcp": {
      "command": "wdq-mcp",
      "env": {
        "MCP_ADMIN_BASE_URL": "https://your-backend-url.com",
        "MCP_SECRET_KEY": "your-secret-key"
      }
    }
  }
}
```

## API 功能列表

### 诊断工具
- `mcp_config()`: 查看当前 MCP 配置
- `test_post_method()`: 测试 POST 方法连通性

### 活动管理
- `list_activity()`: 获取活动列表
- `list_activity_signin()`: 获取活动签到列表
- `activity_signin_statistics()`: 活动签到统计

### 社区管理
- `list_community()`: 获取小区列表
- `get_community_type()`: 获取社区住宅类型
- `list_building()`: 获取单元信息
- `list_house()`: 获取房屋信息

### 网格管理
- `list_grid_type()`: 获取网格类型
- `list_grid_mini()`: 获取微网格列表
- `list_grid_ordinary()`: 获取一般网格列表
- `list_grid_total()`: 获取总网格列表

### 人员管理
- `list_people_base()`: 获取基础群众信息
- `find_people_data()`: 查找群众数据
- `list_grider()`: 获取网格员列表
- `get_grider_by_name()`: 根据姓名获取网格员
- `get_grider_by_phone()`: 根据手机号获取网格员
- `list_officer()`: 获取社区干部列表
- `list_users()`: 获取用户列表

### 更多功能

详细的 API 文档请参考源码中的函数注释。

## 开发

### 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/wifiming/wdq-mcp.git
cd wdq-mcp

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码格式化
black wdq_mcp/
isort wdq_mcp/

# 类型检查
mypy wdq_mcp/
```

### 构建和发布

```bash
# 构建包
python -m build

# 发布到 PyPI
python -m twine upload dist/*
```

## 技术架构

- **基础框架**: Model Context Protocol (MCP)
- **HTTP 客户端**: Python 标准库 urllib
- **数据格式**: JSON
- **认证方式**: 自定义请求头 (X-MCP-Auth, X-MCP-Secret)
- **Python 版本**: 3.8+

## 项目信息

- **项目名称**: 五洞桥社区'小五微网共治共享'微网实格管理智慧平台建设项目
- **项目地址**: 四川省成都双流区东升街道五洞桥社区
- **开发公司**: 四川省校霆光明峰大数据科技有限公司
- **开发人员**: 吴限明
- **测试人员**: 李燕

## 许可证

本项目采用 MIT 许可证。详情请参阅 [LICENSE](LICENSE) 文件。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题或建议，请通过以下方式联系：

- 邮箱: wifiming@example.com
- GitHub Issues: https://github.com/wifiming/wdq-mcp/issues