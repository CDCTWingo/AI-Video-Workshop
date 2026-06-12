"""虾壳平台扣费模块 — 余额检查与扣费"""

import logging
import os
import random
import time
from typing import Any

from app.xiake_client import XiakeAPIError, XiakeClient

logger = logging.getLogger(__name__)

MOCK_MODE: bool = os.getenv("XIAKE_MOCK_MODE", "true").lower() in ("true", "1", "yes")

# 每次扣费金额（元）
DEDUCT_AMOUNT: float = 0.30

# Mock 用户余额（从 auth 模块的 mock 用户初始化）
_mock_balances: dict[str, float] = {"mock_access_token_xxx": 10.00}


class XiakeBillingManager:
    """虾壳平台扣费管理器

    负责余额检查、幂等订单号生成和扣费。
    MOCK_MODE=True 时在内存中模拟扣费逻辑。
    """

    def __init__(self, client: XiakeClient) -> None:
        self._client = client

    # ── 余额查询 ────────────────────────────────────────────

    async def check_balance(self, access_token: str) -> float:
        """查询用户余额，返回可用金额（元）"""
        if MOCK_MODE:
            balance = _mock_balances.get(access_token, 0.0)
            logger.info("[MOCK] check_balance, balance=%.2f", balance)
            return balance

        user_info = await self._client.get_user_info(access_token)
        balance: float = float(user_info.get("balance", 0))
        logger.info("check_balance, balance=%.2f", balance)
        return balance

    # ── 扣费 ────────────────────────────────────────────────

    async def deduct(
        self, access_token: str, amount: float = DEDUCT_AMOUNT, remark: str = "AI视频生成"
    ) -> dict[str, Any]:
        """扣费

        Args:
            access_token: 用户访问令牌
            amount: 扣费金额（元），默认 0.30
            remark: 扣费备注

        Returns:
            {"success": True, "balance": float}

        Raises:
            XiakeAPIError: 余额不足时 code=40101
        """
        order_no = self.generate_order_no()

        if MOCK_MODE:
            balance = _mock_balances.get(access_token, 0.0)
            if balance < amount:
                logger.warning("[MOCK] 余额不足, balance=%.2f, amount=%.2f", balance, amount)
                raise XiakeAPIError(code=40101, message="余额不足，请充值后使用")
            balance -= amount
            _mock_balances[access_token] = round(balance, 2)
            logger.info("[MOCK] deduct, amount=%.2f, balance=%.2f, orderNo=%s", amount, balance, order_no)
            return {"success": True, "balance": balance}

        # 真实调用
        data = await self._client.deduct(
            access_token=access_token,
            amount=amount,
            app_order_no=order_no,
            remark=remark,
        )
        logger.info("deduct success, orderNo=%s, balance=%s", order_no, data.get("balance"))
        return data

    # ── 订单号生成 ──────────────────────────────────────────

    @staticmethod
    def generate_order_no() -> str:
        """生成幂等订单号: avw-{timestamp}-{random6}"""
        ts = int(time.time())
        rand = random.randint(100000, 999999)
        return f"avw-{ts}-{rand}"
