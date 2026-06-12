"""虾壳平台 API 客户端封装"""

import hashlib
import hmac
import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# MOCK_MODE=True 时，所有方法直接返回 Mock 数据，不发真实 HTTP 请求
MOCK_MODE: bool = os.getenv("XIAKE_MOCK_MODE", "true").lower() in ("true", "1", "yes")

# ── Mock 数据 ──────────────────────────────────────────────

_MOCK_GET_TOKEN: dict[str, Any] = {
    "accessToken": "mock_at_xxx",
    "refreshToken": "mock_rt_xxx",
    "expiresIn": 7200,
    "refreshExpiresIn": 172800,
}

_MOCK_REFRESH_TOKEN: dict[str, Any] = {
    "accessToken": "mock_at_xxx",
    "refreshToken": "mock_rt_xxx",
    "expiresIn": 7200,
    "refreshExpiresIn": 172800,
}

_MOCK_USER_INFO: dict[str, Any] = {
    "userId": 999,
    "nickname": "测试用户",
    "avatar": "",
    "balance": 10.00,
    "level": "normal",
}

_MOCK_DEDUCT: dict[str, Any] = {
    "success": True,
    "balance": 9.70,
}


class XiakeAPIError(Exception):
    """虾壳平台 API 异常"""

    def __init__(self, code: int, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"XiakeAPIError(code={code}, message={message})")


class XiakeClient:
    """虾壳平台 API 客户端"""

    def __init__(self, base_url: str, app_key: str, app_secret: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.app_key = app_key
        self.app_secret = app_secret
        self._client: httpx.AsyncClient | None = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient()
        return self._client

    async def close(self) -> None:
        """关闭底层 HTTP 客户端"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> "XiakeClient":
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.close()

    # ── 签名 ──────────────────────────────────────────────

    def _sign(self, params: dict[str, Any]) -> str:
        """HMAC-SHA256 签名

        将请求参数(不含 sign 字段)按 key 字母升序排列，
        拼接成 key1=value1&key2=value2 格式后签名，返回 hex 编码结果。
        """
        filtered = {k: v for k, v in params.items() if k != "sign"}
        sorted_keys = sorted(filtered.keys())
        sign_str = "&".join(f"{k}={filtered[k]}" for k in sorted_keys)
        logger.debug("签名原串: %s", sign_str)
        return hmac.new(
            self.app_secret.encode("utf-8"),
            sign_str.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def _build_signed_params(self, params: dict[str, Any]) -> dict[str, Any]:
        """构造带签名的请求参数"""
        params = {**params, "appKey": self.app_key}
        params["sign"] = self._sign(params)
        return params

    # ── 通用响应处理 ────────────────────────────────────────

    @staticmethod
    def _parse_response(resp_data: dict[str, Any]) -> Any:
        """解析响应，code != 0 时抛出 XiakeAPIError"""
        code = resp_data.get("code", -1)
        if code != 0:
            message = resp_data.get("message", resp_data.get("msg", "unknown error"))
            raise XiakeAPIError(code=code, message=message)
        return resp_data.get("data")

    # ── 认证接口 ────────────────────────────────────────────

    async def get_token(self, session_key: str) -> dict[str, Any]:
        """用 session_key 换 accessToken + refreshToken

        POST /openapi/auth/token
        """
        if MOCK_MODE:
            logger.info("[MOCK] get_token, session_key=%s", session_key[:8] + "...")
            return _MOCK_GET_TOKEN.copy()

        params = self._build_signed_params({"sessionKey": session_key})
        client = self._get_client()
        logger.info("请求获取 token")
        resp = await client.post(f"{self.base_url}/auth/token", json=params)
        resp.raise_for_status()
        data = self._parse_response(resp.json())
        logger.info("获取 token 成功, expiresIn=%s", data.get("expiresIn"))
        return data

    async def refresh_token(self, refresh_token: str) -> dict[str, Any]:
        """用 refreshToken 刷新 accessToken

        POST /openapi/auth/refresh
        """
        if MOCK_MODE:
            logger.info("[MOCK] refresh_token")
            return _MOCK_REFRESH_TOKEN.copy()

        params = self._build_signed_params({"refreshToken": refresh_token})
        client = self._get_client()
        logger.info("请求刷新 token")
        resp = await client.post(f"{self.base_url}/auth/refresh", json=params)
        resp.raise_for_status()
        data = self._parse_response(resp.json())
        logger.info("刷新 token 成功, expiresIn=%s", data.get("expiresIn"))
        return data

    # ── 用户接口 ────────────────────────────────────────────

    async def get_user_info(self, access_token: str) -> dict[str, Any]:
        """获取用户信息

        GET /openapi/user/info
        """
        if MOCK_MODE:
            logger.info("[MOCK] get_user_info")
            return _MOCK_USER_INFO.copy()

        client = self._get_client()
        headers = {"Authorization": f"Bearer {access_token}"}
        logger.info("请求获取用户信息")
        resp = await client.get(f"{self.base_url}/user/info", headers=headers)
        resp.raise_for_status()
        data = self._parse_response(resp.json())
        logger.info("获取用户信息成功, userId=%s", data.get("userId"))
        return data

    # ── 扣费接口 ────────────────────────────────────────────

    async def deduct(
        self,
        access_token: str,
        amount: float,
        app_order_no: str,
        remark: str,
    ) -> dict[str, Any]:
        """扣费

        POST /openapi/consumption/deduct
        """
        if MOCK_MODE:
            logger.info("[MOCK] deduct, amount=%s, orderNo=%s", amount, app_order_no)
            return _MOCK_DEDUCT.copy()

        params = self._build_signed_params({
            "amount": amount,
            "appOrderNo": app_order_no,
            "remark": remark,
        })
        client = self._get_client()
        headers = {"Authorization": f"Bearer {access_token}"}
        logger.info("请求扣费, amount=%s, orderNo=%s", amount, app_order_no)
        resp = await client.post(
            f"{self.base_url}/consumption/deduct",
            json=params,
            headers=headers,
        )
        resp.raise_for_status()
        data = self._parse_response(resp.json())
        logger.info("扣费成功, balance=%s", data.get("balance"))
        return data
