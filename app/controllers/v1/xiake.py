"""虾壳平台 API 接口 — 认证、用户信息、扣费"""

import os
from typing import Optional

from fastapi import Header, Request
from loguru import logger

from app.controllers.v1.base import new_router
from app.xiake_client import XiakeClient, XiakeAPIError
from app.xiake_auth import XiakeAuthManager
from app.xiake_billing import XiakeBillingManager
from app.utils import utils

router = new_router()
router.tags = ["V1", "Xiake"]

# ── 全局单例初始化 ──────────────────────────────────────────

_xiake_base_url = os.getenv("XIAKE_BASE_URL", "https://api.xiake.com/openapi")
_xiake_app_key = os.getenv("XIAKE_APP_KEY", "")
_xiake_app_secret = os.getenv("XIAKE_APP_SECRET", "")

xiake_client = XiakeClient(
    base_url=_xiake_base_url,
    app_key=_xiake_app_key,
    app_secret=_xiake_app_secret,
)
xiake_auth_manager = XiakeAuthManager(client=xiake_client)
xiake_billing_manager = XiakeBillingManager(client=xiake_client)

# ── 统一响应格式 ────────────────────────────────────────────


def _success(data=None):
    """成功响应: {"code": 0, "data": ...}"""
    resp = {"code": 0}
    if data is not None:
        resp["data"] = data
    return resp


def _error(code: int, message: str):
    """错误响应: {"code": xxx, "message": "..."}"""
    return {"code": code, "message": message}


def _extract_bearer_token(authorization: Optional[str]) -> str:
    """从 Authorization 头提取 Bearer token"""
    if not authorization:
        return ""
    parts = authorization.split(" ", 1)
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1].strip()
    return ""


# ── 接口1: POST /api/v1/xiake/auth ─────────────────────────


@router.post("/xiake/auth", summary="虾壳平台认证登录")
async def xiake_auth(request: Request, body: dict):
    """用 session_key 换取 accessToken + 用户信息

    请求体: {"session_key": "xxx"}
    """
    session_key = body.get("session_key", "")
    if not session_key:
        return _error(code=400, message="session_key 不能为空")

    try:
        result = await xiake_auth_manager.authenticate(session_key)
        return _success(data=result)
    except XiakeAPIError as e:
        logger.warning(f"虾壳认证失败: code={e.code}, message={e.message}")
        return _error(code=40100, message="认证失败")
    except Exception as e:
        logger.error(f"虾壳认证异常: {e}")
        return _error(code=500, message=f"认证服务异常: {str(e)}")


# ── 接口2: GET /api/v1/xiake/user ──────────────────────────


@router.get("/xiake/user", summary="获取虾壳用户信息")
async def xiake_user(request: Request, authorization: Optional[str] = Header(None)):
    """获取当前登录用户信息

    请求头: Authorization: Bearer {accessToken}
    """
    access_token = _extract_bearer_token(authorization)
    if not access_token:
        return _error(code=40100, message="缺少 Authorization 头或 token 无效")

    try:
        user_info = await xiake_client.get_user_info(access_token)
        return _success(data=user_info)
    except XiakeAPIError as e:
        logger.warning(f"获取用户信息失败: code={e.code}, message={e.message}")
        return _error(code=e.code, message=e.message)
    except Exception as e:
        logger.error(f"获取用户信息异常: {e}")
        return _error(code=500, message=f"用户服务异常: {str(e)}")


# ── 接口3: POST /api/v1/xiake/deduct ───────────────────────


@router.post("/xiake/deduct", summary="虾壳平台扣费")
async def xiake_deduct(
    request: Request,
    body: dict,
    authorization: Optional[str] = Header(None),
):
    """扣除用户费用

    请求头: Authorization: Bearer {accessToken}
    请求体: {"amount": 0.30, "remark": "AI视频生成"}  (amount 可选，默认0.30)
    """
    access_token = _extract_bearer_token(authorization)
    if not access_token:
        return _error(code=40100, message="缺少 Authorization 头或 token 无效")

    amount = body.get("amount", 0.30)
    remark = body.get("remark", "AI视频生成")

    # 先检查余额
    try:
        balance = await xiake_billing_manager.check_balance(access_token)
        if balance < amount:
            return _error(code=40101, message="余额不足，请充值后使用")
    except XiakeAPIError as e:
        logger.warning(f"余额检查失败: code={e.code}, message={e.message}")
        return _error(code=e.code, message=e.message)
    except Exception as e:
        logger.error(f"余额检查异常: {e}")
        return _error(code=500, message=f"余额查询异常: {str(e)}")

    # 执行扣费
    try:
        result = await xiake_billing_manager.deduct(
            access_token=access_token,
            amount=amount,
            remark=remark,
        )
        return _success(data=result)
    except XiakeAPIError as e:
        logger.warning(f"扣费失败: code={e.code}, message={e.message}")
        return _error(code=e.code, message=e.message)
    except Exception as e:
        logger.error(f"扣费异常: {e}")
        return _error(code=500, message=f"扣费服务异常: {str(e)}")
