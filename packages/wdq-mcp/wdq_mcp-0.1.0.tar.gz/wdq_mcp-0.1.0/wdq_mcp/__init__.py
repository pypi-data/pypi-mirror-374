"""五洞桥社区'小五微网共治共享'微网实格管理智慧平台 MCP 服务包

这是一个基于 Model Context Protocol (MCP) 的服务包，
为五洞桥社区智慧平台提供数据查询和管理功能。

主要功能:
- 活动管理
- 社区管理
- 网格管理
- 人员管理
- 党建管理
- 政务服务
- 投诉管理
- 预警信息管理

使用方式:
    from wdq_mcp import WudongqiaoMCP
    
    # 创建MCP服务实例
    mcp_server = WudongqiaoMCP()
    
    # 启动服务
    mcp_server.run()
"""

__version__ = "0.1.0"
__author__ = "吴限明"
__email__ = "wifiming@example.com"
__description__ = "五洞桥社区智慧平台 MCP 服务包"

from .server import WudongqiaoMCP, main

__all__ = ["WudongqiaoMCP", "main", "__version__"]