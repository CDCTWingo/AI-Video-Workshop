"""
虾壳平台 — 计费扣费服务（预留接口）
Xiake Platform — Billing Service (Stub)

当虾壳平台提供计费API后，替换下面的pass为实际实现。
当前模式：免费使用，不扣费。
"""

from loguru import logger
from app.config import config


class XiakeBillingService:
    """虾壳计费扣费服务"""

    def __init__(self):
        self._enabled = config.app.get("xiake", {}).get("enabled", False)
        self._billing_url = config.app.get("xiake", {}).get("billing_url", "")
        self._api_key = config.app.get("xiake", {}).get("api_key", "")

    @property
    def enabled(self) -> bool:
        return self._enabled

    def check_balance(self, user_id: str) -> float:
        """
        查询用户余额
        
        Args:
            user_id: 用户唯一ID
        
        Returns:
            float: 余额(USD)
        """
        if not self._enabled:
            # 免费模式：返回无限余额
            return 999.0

        # TODO: 对接虾壳余额查询API
        # import requests
        # resp = requests.get(
        #     f"{self._billing_url}/balance",
        #     headers={"Authorization": f"Bearer {self._api_key}"},
        #     params={"user_id": user_id}
        # )
        # return resp.json().get("balance", 0.0)

        logger.warning("Xiake billing enabled but not implemented yet")
        return 999.0

    def deduct(self, user_id: str, amount: float, description: str = "") -> bool:
        """
        扣费
        
        Args:
            user_id: 用户唯一ID
            amount: 扣费金额(USD)
            description: 扣费描述
        
        Returns:
            bool: 是否扣费成功
        """
        if not self._enabled:
            # 免费模式：始终返回成功
            logger.info(f"[FREE MODE] Deduct ${amount:.2f} from {user_id}: {description}")
            return True

        # TODO: 对接虾壳扣费API
        # import requests
        # resp = requests.post(
        #     f"{self._billing_url}/deduct",
        #     headers={"Authorization": f"Bearer {self._api_key}"},
        #     json={"user_id": user_id, "amount": amount, "description": description}
        # )
        # return resp.status_code == 200

        logger.warning("Xiake deduct enabled but not implemented yet")
        return True

    def get_consumption_log(self, user_id: str, limit: int = 20) -> list:
        """
        获取消费记录
        
        Args:
            user_id: 用户唯一ID
            limit: 返回条数
        
        Returns:
            list: 消费记录列表
        """
        if not self._enabled:
            return []

        # TODO: 对接虾壳消费日志API
        logger.warning("Xiake get_consumption_log not implemented yet")
        return []

    def estimate_cost(self, video_duration: float, quality: str = "hd") -> float:
        """
        估算视频生成费用
        
        Args:
            video_duration: 视频时长(秒)
            quality: 视频质量 (sd/hd)
        
        Returns:
            float: 预估费用(USD)
        """
        # 基础定价策略（可调整）
        base_price = 0.10  # 每条视频基础费用 $0.10
        duration_price = 0.01 * video_duration  # 每秒 $0.01
        quality_multiplier = 1.0 if quality == "sd" else 1.5

        return (base_price + duration_price) * quality_multiplier


# Singleton instance
xiake_billing = XiakeBillingService()
