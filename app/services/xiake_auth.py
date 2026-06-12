"""
虾壳平台 — 用户认证服务（预留接口）
Xiake Platform — User Authentication Service (Stub)

当虾壳平台提供认证API后，替换下面的pass为实际实现。
当前模式：无账号登录，所有用户默认为diamond级别。
"""

from loguru import logger
from app.config import config


class XiakeAuthService:
    """虾壳用户认证服务"""

    def __init__(self):
        self._enabled = config.app.get("xiake", {}).get("enabled", False)
        self._auth_url = config.app.get("xiake", {}).get("auth_url", "")
        self._api_key = config.app.get("xiake", {}).get("api_key", "")

    @property
    def enabled(self) -> bool:
        return self._enabled

    def verify_user(self, token: str) -> dict:
        """
        验证用户身份，返回用户信息
        
        Args:
            token: 虾壳平台用户token (从URL参数或Header获取)
        
        Returns:
            dict: {
                "user_id": str,        # 用户唯一ID
                "username": str,       # 用户名
                "level": str,          # normal / member / diamond
                "balance": float,      # 充值账户余额(USD)
                "commission": float,   # 佣金账户余额(USD)
            }
        """
        if not self._enabled:
            # 无账号模式：返回默认diamond用户
            return {
                "user_id": "anonymous",
                "username": "Anonymous User",
                "level": "diamond",
                "balance": 999.0,
                "commission": 0.0,
            }

        # TODO: 对接虾壳认证API
        # 示例实现:
        # import requests
        # resp = requests.post(
        #     f"{self._auth_url}/verify",
        #     headers={"Authorization": f"Bearer {self._api_key}"},
        #     json={"token": token}
        # )
        # if resp.status_code == 200:
        #     return resp.json()
        # raise AuthenticationError("Invalid token")

        logger.warning("Xiake auth enabled but not implemented yet")
        return {
            "user_id": "anonymous",
            "username": "Anonymous User",
            "level": "diamond",
            "balance": 999.0,
            "commission": 0.0,
        }

    def get_user_info(self, user_id: str) -> dict:
        """
        获取用户详情
        
        Args:
            user_id: 用户唯一ID
        
        Returns:
            dict: 用户详细信息
        """
        if not self._enabled:
            return {
                "user_id": user_id,
                "username": "Anonymous User",
                "level": "diamond",
                "balance": 999.0,
                "commission": 0.0,
            }

        # TODO: 对接虾壳用户信息API
        logger.warning("Xiake get_user_info not implemented yet")
        return {}

    def check_permission(self, user_level: str, required_level: str = "normal") -> bool:
        """
        检查用户权限等级
        
        Args:
            user_level: 用户等级 (normal/member/diamond)
            required_level: 所需最低等级
        
        Returns:
            bool: 是否有权限
        """
        level_hierarchy = {"normal": 0, "member": 1, "diamond": 2}
        return level_hierarchy.get(user_level, 0) >= level_hierarchy.get(required_level, 0)


# Singleton instance
xiake_auth = XiakeAuthService()
