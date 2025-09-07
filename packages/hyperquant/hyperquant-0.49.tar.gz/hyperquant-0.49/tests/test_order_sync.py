import asyncio
from hyperquant.broker.ourbit import OurbitSpot
import pybotters


# 等待指定 oid 的最终 delete，超时抛 TimeoutError
async def wait_delete(stream: pybotters.StoreStream, oid: str, seconds: float):
    async with asyncio.timeout(seconds):
        while True:
            change = await stream.__anext__()
            if change.operation == "delete" and change.data.get("order_id") == oid:
                return change.data  # 内含 state / avg_price / deal_quantity 等累计字段


async def order_sync(
    ob: OurbitSpot,
    symbol: str = "SOL_USDT",
    side: str = "buy",
    order_type: str = "market",  # "market" / "limit"
    usdt_amount: float | None = None,  # 市价可填
    quantity: float | None = None,  # 市价可填
    price: float | None = None,  # 限价必填
    window_sec: float = 2.0,  # 主等待窗口（限价可设为 5.0）
    grace_sec: float = 1.0,  # 撤单后宽限
):
    with ob.store.orders.watch() as stream:
        # 下单（只保留最简两种入参形态）
        try:
            oid = await ob.place_order(
                symbol,
                side,
                order_type=order_type,
                usdt_amount=usdt_amount,
                quantity=quantity,
                price=price,
            )
        except Exception as e:
            return {"symbol": symbol, "state": "error", "error": str(e)}

        # 步骤1：主窗口内等待这单的最终 delete
        try:
            return await wait_delete(stream, oid, window_sec)
        except TimeoutError:
            # 步骤2：到点撤单（市价通常用不到；限价才有意义）
            try:
                await ob.cancel_order(oid)
            except Exception:
                pass
            # 固定宽限内再等“迟到”的最终 delete
            try:
                return await wait_delete(stream, oid, grace_sec)
            except TimeoutError:
                return {"order_id": oid, "symbol": symbol, "state": "timeout"}


async def main():
    async with pybotters.Client(
        apis={
            "ourbit": [
                "WEB3bf088f8b2f2fae07592fe1a6240e2d798100a9cb2a91f8fda1056b6865ab3ee"
            ]
        }
    ) as client:
        ob = OurbitSpot(client)
        await ob.__aenter__()
        await ob.sub_personal()  # 私有频道
        ob.store.book.limit = 3
        await ob.sub_orderbook(["SOL_USDT"])  # 订单簿频道
        # # 示例：市价
        # result = await order_sync( ob, symbol="SOL_USDT", side="buy", order_type="limit", quantity=0.04, price=200, window_sec=2)
        # print(result)
        while True:
            asks = ob.store.book.find({'s': 'SOL_USDT', 'S': 'a'})
            bids = ob.store.book.find({'s': 'SOL_USDT', 'S': 'b'})
            if asks and bids:
                best_ask = float(asks[1]['p'])
                best_bid = float(bids[1]['p'])
            
                result = await order_sync( ob, symbol="SOL_USDT", side="buy", order_type="limit", quantity=0.04, price=best_bid, window_sec=1)
                print(result)
                await asyncio.sleep(5)
                



if __name__ == "__main__":
    asyncio.run(main())

