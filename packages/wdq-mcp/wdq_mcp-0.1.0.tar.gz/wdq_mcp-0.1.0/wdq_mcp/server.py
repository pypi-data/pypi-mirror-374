"""
五洞桥项目 MCP 独立版服务

使用方式（示例）：
  cd /Users/wifiming/code/wdq/wdq_mcp
  uv run server.py stdio

环境变量：
  - MCP_ADMIN_BASE_URL: 后端 Django 服务地址
  - MCP_SECRET_KEY:     与后端拦截器一致的密钥，默认与后端中间件相同
  - ADMIN_API_TIMEOUT:  请求超时秒数，默认 15

本服务基于 mcp.server.fastmcp.FastMCP，提供多组只读工具
根据 /api/app/middleware/_mcpIntercept.py 的白名单接口发起请求，
并自动携带 X-MCP-Auth 和 X-MCP-Secret 请求头，以通过后端拦截器。
"""

from __future__ import annotations

import json
import os
import ssl
import sys
from typing import Any, Dict, Optional
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------
DEFAULT_BASE_URL: str = os.getenv("MCP_ADMIN_BASE_URL", "")
MCP_SECRET_KEY: str = os.getenv("MCP_SECRET_KEY", "")
REQUEST_TIMEOUT: float = float(os.getenv("ADMIN_API_TIMEOUT", "15"))

# 仅用于本地快速排错输出
DEBUG: bool = os.getenv("MCP_DEBUG", "1") in ("1", "true", "True")


def _debug(msg: str) -> None:
    if DEBUG:
        print(f"[MCP] {msg}", file=sys.stderr)


# ---------------------------------------------------------------------------
# HTTP 辅助函数（使用标准库，避免额外依赖）
# ---------------------------------------------------------------------------


def _http_get(
    path: str,
    params: Optional[Dict[str, Any]] = None,
    *,
    base_url: Optional[str] = None,
) -> Dict[str, Any]:
    """以 GET 方式请求后端接口。

    - 自动拼接 ADMIN_API_BASE_URL + path
    - 自动附加 X-MCP-Auth / X-MCP-Secret 头
    - 解析 JSON 响应并返回
    - 出错时抛出带详细信息的异常
    """
    if not path.startswith("/api/admin/v1/"):
        raise ValueError("path 必须以 /api/admin/v1/ 开头")

    base: str = base_url or DEFAULT_BASE_URL
    query: str = urlencode({k: v for k, v in (params or {}).items() if v is not None})
    # 保持原始路径，不随意添加尾斜杠，与拦截器白名单精确匹配
    full_path: str = path
    url: str = urljoin(base, full_path)
    if query:
        url = f"{url}?{query}"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        # MCP 拦截器需要的请求头（Auth 值只要存在即可，Secret 必须匹配）
        "X-MCP-Auth": "enabled",
        "X-MCP-Secret": MCP_SECRET_KEY,
    }

    _debug(f"GET {url}")
    req = Request(url=url, headers=headers, method="GET")

    # 创建忽略SSL验证的上下文（用于处理自签名证书等情况）
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    try:
        with urlopen(req, timeout=REQUEST_TIMEOUT, context=ssl_context) as resp:
            raw: bytes = resp.read()
            text: str = raw.decode("utf-8", errors="replace")
            _debug(f"<- {resp.status} bytes={len(raw)}")
            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                # 有些接口可能直接返回文本，这里做兜底
                data = {"code": 200, "data": text, "msg": "ok(text)"}
            return (
                data
                if isinstance(data, dict)
                else {"code": 200, "data": data, "msg": "ok"}
            )
    except HTTPError as e:
        body = (
            e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else str(e)
        )
        _debug(f"HTTPError {e.code}: {body}")
        raise RuntimeError(f"HTTP {e.code} {url}: {body}")
    except URLError as e:
        _debug(f"URLError: {e}")
        raise RuntimeError(f"URL error for {url}: {e}")
    except Exception as e:  # 防御性兜底
        _debug(f"Unexpected error: {e}")
        raise RuntimeError(f"Unexpected error for {url}: {e}")


def _http_post(
    path: str,
    data: Optional[Dict[str, Any]] = None,
    *,
    base_url: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """以 POST 方式请求后端接口。

    - 自动拼接 ADMIN_API_BASE_URL + path
    - 自动附加 X-MCP-Auth / X-MCP-Secret 头
    - 将 data 作为 JSON 发送到请求体
    - 解析 JSON 响应并返回
    - 出错时抛出带详细信息的异常
    """
    if not path.startswith("/api/admin/v1/"):
        raise ValueError("path 必须以 /api/admin/v1/ 开头")

    base: str = base_url or DEFAULT_BASE_URL
    # 保持原始路径，不随意添加尾斜杠，与拦截器白名单精确匹配
    full_path: str = path
    url: str = urljoin(base, full_path)

    # 如果提供了查询参数，则拼接到 URL 上
    if params:
        query: str = urlencode({k: v for k, v in params.items() if v is not None})
        if query:
            url = f"{url}?{query}"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        # MCP 拦截器需要的请求头（Auth 值只要存在即可，Secret 必须匹配）
        "X-MCP-Auth": "enabled",
        "X-MCP-Secret": MCP_SECRET_KEY,
    }

    # 准备请求体数据（默认使用空对象，避免出现空字节的情况）
    request_data = data or {}
    json_data = json.dumps(request_data).encode("utf-8")

    _debug(f"POST {url} with data: {request_data}")
    req = Request(url=url, headers=headers, method="POST", data=json_data)
    # 输出实际请求方法与请求体长度，便于排查是否发生方法降级
    try:
        _debug(
            f"实际请求方法: {req.get_method()}, 请求体长度: {len(json_data) if json_data else 0}"
        )
    except Exception:
        # 防御性兜底，避免调试输出影响主流程
        pass

    # 创建忽略SSL验证的上下文（用于处理自签名证书等情况）
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    try:
        with urlopen(req, timeout=REQUEST_TIMEOUT, context=ssl_context) as resp:
            raw: bytes = resp.read()
            text: str = raw.decode("utf-8", errors="replace")
            _debug(f"<- {resp.status} bytes={len(raw)}")
            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                # 有些接口可能直接返回文本，这里做兜底
                data = {"code": 200, "data": text, "msg": "ok(text)"}
            return (
                data
                if isinstance(data, dict)
                else {"code": 200, "data": data, "msg": "ok"}
            )
    except HTTPError as e:
        body = (
            e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else str(e)
        )
        _debug(f"HTTPError {e.code}: {body}")
        raise RuntimeError(f"HTTP {e.code} {url}: {body}")
    except URLError as e:
        _debug(f"URLError: {e}")
        raise RuntimeError(f"URL error for {url}: {e}")
    except Exception as e:  # 防御性兜底
        _debug(f"Unexpected error: {e}")
        raise RuntimeError(f"Unexpected error for {url}: {e}")


# ---------------------------------------------------------------------------
# MCP Server 定义
# ---------------------------------------------------------------------------

mcp = FastMCP("Wudongqiao-MCP")


class WudongqiaoMCP:
    """五洞桥社区 MCP 服务类"""
    
    def __init__(self, base_url: Optional[str] = None, secret_key: Optional[str] = None):
        """初始化 MCP 服务
        
        Args:
            base_url: 后端服务地址，如果不提供则使用环境变量
            secret_key: 密钥，如果不提供则使用环境变量
        """
        global DEFAULT_BASE_URL, MCP_SECRET_KEY
        if base_url:
            DEFAULT_BASE_URL = base_url
        if secret_key:
            MCP_SECRET_KEY = secret_key
    
    def run(self, transport: str = "stdio"):
        """运行 MCP 服务
        
        Args:
            transport: 传输方式，默认为 stdio
        """
        if transport == "stdio":
            mcp.run()
        else:
            raise ValueError(f"不支持的传输方式: {transport}")
    
    @property
    def server(self):
        """获取底层的 FastMCP 服务器实例"""
        return mcp


def _ok(data: Any) -> Dict[str, Any]:
    return {"code": 200, "data": data, "msg": "ok"}


def _wrap_call(path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    try:
        # 对特定接口强制使用 POST（兼容历史实现误用 GET 的情况）
        if path.rstrip("/") == "/api/admin/v1/officer/list":
            # 将分页等参数放到查询串，POST 体保持为空对象
            return _wrap_call_post(path, data=None, params=params)
        resp = _http_get(path, params=params)
        # 统一返回为对象结构，确保 code/data/msg 存在
        code = resp.get("code", 200)
        msg = resp.get("msg", "ok")
        data = resp.get("data", resp)
        return {"code": code, "data": data, "msg": msg}
    except Exception as e:
        # 与后端规范保持一致：返回对象结构，code 非 200
        return {"code": 10500, "data": None, "msg": f"请求失败: {e}"}


def _wrap_call_post(
    path: str,
    data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """使用 POST 方法调用后端接口的包装函数"""
    try:
        resp = _http_post(path, data=data, params=params)
        # 统一返回为对象结构，确保 code/data/msg 存在
        code = resp.get("code", 200)
        msg = resp.get("msg", "ok")
        data = resp.get("data", resp)
        return {"code": code, "data": data, "msg": msg}
    except Exception as e:
        # 与后端规范保持一致：返回对象结构，code 非 200
        return {"code": 10500, "data": None, "msg": f"请求失败: {e}"}


# ----------------------------- 诊断信息 -----------------------------------


@mcp.tool()
def mcp_config() -> Dict[str, Any]:
    """查看当前 MCP 客户端配置（用于本地调试）"""
    return _ok(
        {
            "base_url": DEFAULT_BASE_URL,
            "timeout": REQUEST_TIMEOUT,
            "secret_len": len(MCP_SECRET_KEY),
            "debug": DEBUG,
        }
    )


@mcp.tool()
def test_post_method() -> Dict[str, Any]:
    """测试 POST 方法是否正常工作"""
    try:
        # 直接调用 _http_post 测试
        result = _http_post("/api/admin/v1/officer/list", {"page": 1, "page_size": 2})
        return {
            "code": 200,
            "data": {"method": "POST", "success": True, "result": result},
            "msg": "POST 方法测试成功",
        }
    except Exception as e:
        return {
            "code": 10500,
            "data": {"method": "POST", "success": False, "error": str(e)},
            "msg": "POST 方法测试失败",
        }


# ----------------------------- 实际可供调用的工具 -----------------------------------


# 活动管理
@mcp.tool()
def list_activity(page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """获取活动列表 /api/admin/v1/activity/list"""
    return _wrap_call(
        "/api/admin/v1/activity/list", {"page": page, "page_size": page_size}
    )


@mcp.tool()
def list_activity_signin(
    activity_id: int, page: int = 1, page_size: int = 20
) -> Dict[str, Any]:
    """获取活动签到（报名到场）列表 /api/admin/v1/activity/signin/list"""
    return _wrap_call(
        "/api/admin/v1/activity/signin/list",
        {"activity_id": activity_id, "page": page, "page_size": page_size},
    )


@mcp.tool()
def activity_signin_statistics(activity_id: int) -> Dict[str, Any]:
    """活动签到统计 /api/admin/v1/activity/signin/statistics"""
    return _wrap_call(
        "/api/admin/v1/activity/signin/statistics", {"activity_id": activity_id}
    )


# 小区与建筑管理
@mcp.tool()
def list_community(
    keyword: Optional[str] = None, page: int = 1, page_size: int = 20
) -> Dict[str, Any]:
    """获取小区列表 /api/admin/v1/community/list"""
    return _wrap_call(
        "/api/admin/v1/community/list",
        {"keyword": keyword, "page": page, "page_size": page_size},
    )


@mcp.tool()
def get_community_type() -> Dict[str, Any]:
    """获取社区住宅类型 /api/admin/v1/community-type"""
    return _wrap_call("/api/admin/v1/community-type")


@mcp.tool()
def list_building(
    community_id: int, page: int = 1, page_size: int = 20
) -> Dict[str, Any]:
    """根据小区ID获取单元信息 /api/admin/v1/building/list"""
    return _wrap_call(
        "/api/admin/v1/building/list",
        {"community_id": community_id, "page": page, "page_size": page_size},
    )


@mcp.tool()
def list_community_building(
    community_id: int, page: int = 1, page_size: int = 20
) -> Dict[str, Any]:
    """根据小区ID获取单元信息（社区下级） /api/admin/v1/community/building/list"""
    return _wrap_call(
        "/api/admin/v1/community/building/list",
        {"community_id": community_id, "page": page, "page_size": page_size},
    )


@mcp.tool()
def list_house(building_id: int, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """根据单元ID分页查询房屋号 /api/admin/v1/house/list"""
    return _wrap_call(
        "/api/admin/v1/house/list",
        {"building_id": building_id, "page": page, "page_size": page_size},
    )


# 投诉管理
@mcp.tool()
def list_complaints(
    page: int = 1, page_size: int = 20, status: Optional[str] = None
) -> Dict[str, Any]:
    """获取投诉列表 /api/admin/v1/complaints/"""
    return _wrap_call(
        "/api/admin/v1/complaints/",
        {"page": page, "page_size": page_size, "status": status},
    )


@mcp.tool()
def complaints_statistics() -> Dict[str, Any]:
    """获取社区投诉统计数据 /api/admin/v1/complaints/statistics/"""
    return _wrap_call("/api/admin/v1/complaints/statistics/")


# 信息管理（公告、辟谣、预警）
@mcp.tool()
def list_bulletin(page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """获取社区公告列表 /api/admin/v1/bulletin/list"""
    return _wrap_call(
        "/api/admin/v1/bulletin/list", {"page": page, "page_size": page_size}
    )


@mcp.tool()
def list_debunking_rumors(page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """获取辟谣列表 /api/admin/v1/debunking-rumors/list"""
    return _wrap_call(
        "/api/admin/v1/debunking-rumors/list", {"page": page, "page_size": page_size}
    )


@mcp.tool()
def list_forewarn(
    dispatch_type: Optional[str] = None,
    urgency: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Dict[str, Any]:
    """获取预警信息列表 /api/admin/v1/forewarn/list
    - 可筛选派发方式（dispatch_type）与紧急状态（urgency）
    """
    return _wrap_call(
        "/api/admin/v1/forewarn/list",
        {
            "dispatch_type": dispatch_type,
            "urgency": urgency,
            "page": page,
            "page_size": page_size,
        },
    )


@mcp.tool()
def forewarn_statistics() -> Dict[str, Any]:
    """获取预警信息统计数据 /api/admin/v1/forewarn/statistics"""
    return _wrap_call("/api/admin/v1/forewarn/statistics")


@mcp.tool()
def list_forewarn_tasks(page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """获取预警定时任务列表 /api/admin/v1/forewarn/task/list"""
    return _wrap_call(
        "/api/admin/v1/forewarn/task/list", {"page": page, "page_size": page_size}
    )


# 政务服务
@mcp.tool()
def list_government(
    page: int = 1,
    page_size: int = 20,
    keyword: Optional[str] = None,
    type_id: Optional[int] = None,
) -> Dict[str, Any]:
    """获取政务服务事项列表 /api/admin/v1/government/list"""
    return _wrap_call(
        "/api/admin/v1/government/list",
        {"page": page, "page_size": page_size, "keyword": keyword, "type_id": type_id},
    )


@mcp.tool()
def list_government_type() -> Dict[str, Any]:
    """获取政务服务分类列表 /api/admin/v1/government/type/list"""
    return _wrap_call("/api/admin/v1/government/type/list")


# 网格管理
@mcp.tool()
def list_grid_type() -> Dict[str, Any]:
    """获取网格类型列表 /api/admin/v1/grid-type/list"""
    return _wrap_call("/api/admin/v1/grid-type/list")


@mcp.tool()
def list_grid_mini(page: int = 1, page_size: int = 50) -> Dict[str, Any]:
    """获取微网格列表 /api/admin/v1/grid/mini/list"""
    return _wrap_call(
        "/api/admin/v1/grid/mini/list", {"page": page, "page_size": page_size}
    )


@mcp.tool()
def list_grid_ordinary(page: int = 1, page_size: int = 50) -> Dict[str, Any]:
    """获取一般网格列表 /api/admin/v1/grid/ordinary/list"""
    return _wrap_call(
        "/api/admin/v1/grid/ordinary/list", {"page": page, "page_size": page_size}
    )


@mcp.tool()
def list_grid_total(page: int = 1, page_size: int = 50) -> Dict[str, Any]:
    """获取总网格列表 /api/admin/v1/total-grid/list"""
    return _wrap_call(
        "/api/admin/v1/total-grid/list", {"page": page, "page_size": page_size}
    )


# 网格员管理
@mcp.tool()
def list_grider(page: int = 1, page_size: int = 50) -> Dict[str, Any]:
    """获取网格员列表 /api/admin/v1/grider/list"""
    return _wrap_call(
        "/api/admin/v1/grider/list", {"page": page, "page_size": page_size}
    )


@mcp.tool()
def get_grider_by_name(name: str) -> Dict[str, Any]:
    """根据姓名获取网格员 /api/admin/v1/grider/name"""
    return _wrap_call("/api/admin/v1/grider/name", {"name": name})


@mcp.tool()
def get_grider_by_phone(phone: str) -> Dict[str, Any]:
    """根据手机号获取网格员 /api/admin/v1/grider/phone"""
    return _wrap_call("/api/admin/v1/grider/phone", {"phone": phone})


@mcp.tool()
def list_grider_relationship(page: int = 1, page_size: int = 50) -> Dict[str, Any]:
    """获取网格员与网格关系列表 /api/admin/v1/griderRelationship/list"""
    return _wrap_call(
        "/api/admin/v1/griderRelationship/list", {"page": page, "page_size": page_size}
    )


# 人员管理
@mcp.tool()
def list_people_base(
    keyword: Optional[str] = None, page: int = 1, page_size: int = 20
) -> Dict[str, Any]:
    """获取基础群众信息列表 /api/admin/v1/people/base/list"""
    return _wrap_call(
        "/api/admin/v1/people/base/list",
        {"keyword": keyword, "page": page, "page_size": page_size},
    )


@mcp.tool()
def find_people_data(
    keyword: str, archive_type: Optional[str] = None
) -> Dict[str, Any]:
    """查找群众数据 /api/admin/v1/people/find

    参数说明:
    - keyword: 查找关键词（姓名、身份证、手机号等）
    - archive_type: 档案类型，可选值包括：
      * ordinary: 普通群众
      * setright: 矫正人员
      * ethnic: 少数民族
      * gowster: 涉黑涉恶
      * evil_cult: 邪教人员
      * petition: 信访人员
      * release_personnel: 刑释人员
      * risk_personnel: 风险人员
      * mental_patient: 精神病患者
      * cpc: 党员
      * special_support: 特殊扶持
      * disabled: 残疾人

    注意：如果不提供 people_id，则 archive_type 参数不能为空
    """
    # 将 keyword 作为 name 参数传递，这是后端接口期望的参数名
    params = {"name": keyword}
    if archive_type:
        params["archive_type"] = archive_type
    return _wrap_call("/api/admin/v1/people/find", params)


@mcp.tool()
def list_officer(page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """获取社区干部列表 /api/admin/v1/officer/list"""
    return _wrap_call_post(
        "/api/admin/v1/officer/list", {"page": page, "page_size": page_size}
    )


@mcp.tool()
def list_users(
    keyword: Optional[str] = None, page: int = 1, page_size: int = 20
) -> Dict[str, Any]:
    """获取用户列表 /api/admin/v1/users/"""
    return _wrap_call(
        "/api/admin/v1/users/",
        {"keyword": keyword, "page": page, "page_size": page_size},
    )


# 党建管理
@mcp.tool()
def list_party_deeds(page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """获取党员事迹列表 /api/admin/v1/party/deeds/list"""
    return _wrap_call(
        "/api/admin/v1/party/deeds/list", {"page": page, "page_size": page_size}
    )


@mcp.tool()
def list_party_learn(page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """获取党建学习列表 /api/admin/v1/party/learn/list"""
    return _wrap_call(
        "/api/admin/v1/party/learn/list", {"page": page, "page_size": page_size}
    )


@mcp.tool()
def list_party_life(page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """获取党员组织生活列表 /api/admin/v1/party/life/list"""
    return _wrap_call(
        "/api/admin/v1/party/life/list", {"page": page, "page_size": page_size}
    )


# 投票与商户
@mcp.tool()
def list_poll(page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """获取投票列表 /api/admin/v1/poll/list"""
    return _wrap_call("/api/admin/v1/poll/list", {"page": page, "page_size": page_size})


@mcp.tool()
def list_store(
    page: int = 1, page_size: int = 20, keyword: Optional[str] = None
) -> Dict[str, Any]:
    """获取商户列表 /api/admin/v1/store/list"""
    return _wrap_call(
        "/api/admin/v1/store/list",
        {"page": page, "page_size": page_size, "keyword": keyword},
    )


# 通讯录
@mcp.tool()
def list_phonebook_contacts(page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """获取通讯录联系人列表 /api/admin/v1/phonebook/contacts"""
    return _wrap_call(
        "/api/admin/v1/phonebook/contacts", {"page": page, "page_size": page_size}
    )


def main():
    """命令行入口点"""
    import sys
    
    # 检查环境变量配置
    if not DEFAULT_BASE_URL:
        print("错误: 请设置环境变量 MCP_ADMIN_BASE_URL", file=sys.stderr)
        sys.exit(1)
    
    if not MCP_SECRET_KEY:
        print("错误: 请设置环境变量 MCP_SECRET_KEY", file=sys.stderr)
        sys.exit(1)
    
    # 创建并运行服务
    server = WudongqiaoMCP()
    server.run()


if __name__ == "__main__":
    main()
