#!/usr/bin/env python3
"""
五洞桥社区 MCP 服务包主入口模块

这个模块允许使用 python -m wdq_mcp 的方式运行 MCP 服务
"""

from .server import main

if __name__ == "__main__":
    main()