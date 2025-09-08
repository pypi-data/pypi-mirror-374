import asyncio
import time
from typing import Optional, TypedDict, Literal

import pybotters
from hyperquant.broker.ourbit import OurbitSpot
from hyperquant.logkit import get_logger

logger = get_logger("alpine_test", "./data/alpine_smoke.log", True)


class Hold(TypedDict, total=False):
    symbol: str
    status: Literal["pending", "filled", "closing"]
    oid: str
    ts: float
    p: float
    q: float
    filled_ts: float


class AlpineSmokeTest:
    """
    仅针对 ALPINE_USDT：市价开仓 -> 持有 5 秒 -> 市价平仓。
    - 目的：测试 WS 事件链路与下单路径稳定性（不依赖价差/策略信号）。
    - 仅订阅 Ourbit 订单簿(可选) 和私有频道，验证参数与心跳。
    """

    SYMBOL = "SOL_USDT"

    def __init__(self, hold_seconds: float = 5.0, open_timeout_ms: int = 2000, close_timeout_ms: int = 3000):
        self.hold_seconds = hold_seconds
        self.open_timeout_ms = open_timeout_ms
        self.close_timeout_ms = close_timeout_ms
        self.client: Optional[pybotters.Client] = None
        self.ourbit: Optional[OurbitSpot] = None
        self.ob_store = None

    def _msg_debug(self,msg: dict, ws):

        if 'spot@private.orders' in msg.get("c", ""):
            logger.info(f"orders消息: {msg}")

    async def _msg_debug2(self):
        with self.ob_store.orders.watch() as stream:
            async for change in stream:
                print(change)

    async def __aenter__(self):
        self.client = pybotters.Client(apis="./apis.json")
        await self.client.__aenter__()

        self.ourbit = OurbitSpot(self.client)
        await self.ourbit.__aenter__()
        self.ob_store = self.ourbit.store

        # 仅订阅 ALPINE 订单簿与私有频道（用于测试 WS 参数与心跳）
        await self.ourbit.sub_orderbook([self.SYMBOL])
        await self.ourbit.sub_personal()
        logger.info("已就绪：仅订阅 Ourbit ALPINE 订单簿/私有频道")
        asyncio.create_task(self._msg_debug2())
        return self

    async def __aexit__(self, et, ev, tb):
        if self.client:
            await self.client.__aexit__(et, ev, tb)

    # ============ helpers ============
    async def _open_market_and_wait(self, symbol: str, usdt_amount: float, timeout_ms: int) -> Optional[Hold]:
        """以市价开仓并在本地流中等待终态。成功返回 Hold；失败/超时返回 None。"""
        start = time.time() * 1000
        with self.ob_store.orders.watch() as stream:
            try:
                oid = await self.ourbit.place_order(symbol, "buy", order_type="market", usdt_amount=usdt_amount)
                logger.info(f"准备开仓: {symbol} oid={oid}")
            except Exception as e:
                logger.error(f"开仓下单失败 {symbol}: {e}")
                return None

            while True:
                remain = timeout_ms - (time.time() * 1000 - start)
                if remain <= 0:
                    logger.warning(f"开仓超时: {symbol} oid={oid}")
                    return None
                try:
                    change = await asyncio.wait_for(stream.__anext__(), timeout=remain / 1000)
                except asyncio.TimeoutError:
                    logger.warning(f"开仓超时: {symbol} oid={oid}")
                    return None

                if change.operation != "delete":
                    continue
                data = change.data
                if data.get("order_id") != oid:
                    continue

                state = data.get("state")
                if state == "filled":
                    p = float(data["avg_price"]) ; q = float(data["deal_quantity"]) ; ts = time.time() * 1000
                    logger.ok(f"建仓成交: {symbol} p={p} q={q}")
                    return {"symbol": symbol, "status": "filled", "oid": oid, "p": p, "q": q, "filled_ts": ts}
                if state in ("canceled", "expired", "rejected", "failed"):
                    logger.warning(f"开仓失败: {symbol} state={state}")
                    return None

    async def _close_market_and_wait(self, symbol: str, qty: float, timeout_ms: int) -> bool:
        """以市价平仓并等待终态。成功返回 True。"""
        start = time.time() * 1000
        with self.ob_store.orders.watch() as stream:
            try:
                oid = await self.ourbit.place_order(symbol, "sell", order_type="market", quantity=qty)
                logger.info(f"触发平仓: {symbol} qty={qty} oid={oid}")
            except Exception as e:
                logger.error(f"平仓下单失败 {symbol}: {e}")
                return False

        
            while True:
                remain = timeout_ms - (time.time() * 1000 - start)
                if remain <= 0:
                    logger.error(f"平仓超时: {symbol} oid={oid}")
                    return False
                try:
                    change = await asyncio.wait_for(stream.__anext__(), timeout=remain / 1000)
                except asyncio.TimeoutError:
                    logger.error(f"平仓超时: {symbol} oid={oid}")
                    return False

                if change.operation != "delete":
                    continue
                data = change.data
                if data.get("order_id") != oid:
                    continue

                state = data.get("state")
                if state == "filled":
                    logger.ok(f"平仓完成: {symbol} close_p={data.get('avg_price')}")
                    return True
                if state in ("canceled", "expired", "rejected", "failed"):
                    logger.error(f"平仓失败: {symbol} state={state}")
                    return False

    # ============ one-shot test flow ============
    async def run_once(self, usdt_amount: float = 10.0):
        """一次性流程：开仓 -> 持有 N 秒 -> 平仓。"""
        # 1) 开仓
        hold = await self._open_market_and_wait(self.SYMBOL, usdt_amount, timeout_ms=self.open_timeout_ms)
        if not hold:
            logger.warning("开仓未成功，终止本次测试")
            return

        # 2) 持有 N 秒
        logger.info(f"开始持有 {self.hold_seconds}s: {self.SYMBOL} q={hold['q']} p={hold['p']}")
        await asyncio.sleep(self.hold_seconds)

        # 3) 平仓
        ok = await self._close_market_and_wait(self.SYMBOL, float(hold["q"]), timeout_ms=self.close_timeout_ms)
        if ok:
            logger.info("本次测试完成 ✅")
        else:
            logger.error("本次测试失败 ❌")

    async def run_loop(self, usdt_amount: float = 10.0, interval_seconds: float = 60.0):
        """循环执行 run_once，间隔 N 秒。"""
        while True:
            await self.run_once(usdt_amount)
            logger.info(f"等待 {interval_seconds}s 后进行下一轮测试")
            await asyncio.sleep(interval_seconds)


async def main():
    async with AlpineSmokeTest(hold_seconds=5.0) as test:
        # await test.run_once(usdt_amount=10.0)
        await test.run_loop(usdt_amount=10.0, interval_seconds=5)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 程序已退出")
    except Exception as e:
        print(f"❌ 程序异常: {e}")
