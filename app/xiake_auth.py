"""虾壳平台认证模块 — session_key 换 token 及令牌管理"""

import logging
import os
import time
from typing import Any

from app.xiake_client import XiakeAPIError, XiakeClient

logger = logging.getLogger(__name__)

MOCK_MODE: bool = os.getenv("XIAKE_MOCK_MODE", "true").lower() in ("true", "1", "yes")

# ── Mock 数据 ──────────────────────────────────────────────

_MOCK_AUTH_RESULT: dict[str, Any] = {
    "accessToken": "mock_access_token_xxx",
    "refreshToken": "mock_refresh_token_xxx",
    "expiresIn": 7200,
    "refreshExpiresIn": 172800,
    "userId": 999,
    "nickname": "测试用户",
    "avatar": "",
    "balance": 10.00,
    "level": "normal",
}


class XiakeAuthManager:
    """虾壳平台认证管理器

    负责 session_key 换 token、令牌缓存及自动刷新。
    MOCK_MODE=True 时直接返回 Mock 数据，不调虾壳 API。
    """

    def __init__(self, client: XiakeClient) -> None:
        self._client = client
        # 内存令牌缓存: user_id -> {accessToken, refreshToken, expires_at}
        self._token_cache: dict[int, dict[str, Any]] = {}

    # ── 认证 ────────────────────────────────────────────────

    async def authenticate(self, session_key: str) -> dict[str, Any]:
        """用 session_key 换取 accessToken + 用户信息

        返回:
            {"accessToken": str, "userInfo": {userId, nickname, avatar, balance, level}}
        """
        if MOCK_MODE:
            logger.info("[MOCK] authenticate, session_key=%s", session_key[:8] + "...")
            token_data = _MOCK_AUTH_RESULT.copy()
            user_id: int = token_data["userId"]
            self._cache_token(user_id, token_data)
            return {
                "accessToken": token_data["accessToken"],
                "userInfo": {
                    "userId": user_id,
                    "nickname": token_data["nickname"],
                    "avatar": token_data["avatar"],
                    "balance": token_data["balance"],
                    "level": token_data["level"],
                },
            }

        # 真实调用
        token_data = await self._client.get_token(session_key)
        user_id = token_data["userId"]
        self._cache_token(user_id, token_data)

        # 获取用户信息
        access_token = token_data["accessToken"]
        user_info = await self._client.get_user_info(access_token)

        return {
            "accessToken": access_token,
            "userInfo": user_info,
        }

    # ── 令牌获取 / 刷新 ─────────────────────────────────────

    async def get_valid_token(self, user_id: int) -> str:
        """获取有效 access_token，过期前 5 分钟自动刷新"""
        if MOCK_MODE:
            logger.info("[MOCK] get_valid_token, user_id=%s", user_id)
            return self._token_cache.get(user_id, {}).get(
                "accessToken", "mock_access_token_xxx"
            )

        await self.refresh_if_needed(user_id)
        entry = self._token_cache.get(user_id)
        if entry is None:
            raise XiakeAPIError(code=40100, message="用户未认证，请先登录")
        return entry["accessToken"]

    async def refresh_if_needed(self, user_id: int) -> None:
        """检查并刷新即将过期的 token（内部方法）"""
        entry = self._token_cache.get(user_id)
        if entry is None:
            return

        # 过期前 5 分钟刷新（300 秒）
        if time.time() >= entry["expires_at"] - 300:
            logger.info("token 即将过期，刷新中, user_id=%s", user_id)
            new_data = await self._client.refresh_token(entry["refreshToken"])
            self._cache_token(user_id, new_data)

    # ── 内部工具 ─────────────────────────────────────────────

    def _cache_token(self, user_id: int, data: dict[str, Any]) -> None:
        """将 token 数据写入内存缓存"""
        self._token_cache[user_id] = {
            "accessToken": data["accessToken"],
            "refreshToken": data["refreshToken"],
            "expires_at": time.time() + data.get("expiresIn", 7200),
        }
        logger.debug("token 已缓存, user_id=%s, expires_at=%.0f", user_id, self._token_cache[user_id]["expires_at"])
