import asyncio
import random
import time
import pybotters
import hyperquant
from hyperquant.broker.models.ourbit import OurbitSpotDataStore
from hyperquant.broker.ourbit import OurbitSpot


async def main():
    store = OurbitSpotDataStore()

    async with pybotters.Client(
        apis={
            "ourbit": [
                "WEB3bf088f8b2f2fae07592fe1a6240e2d798100a9cb2a91f8fda1056b6865ab3ee"
            ]
        }
    ) as client:
        res = await client.fetch("POST", "https://www.ourbit.com/ucenter/api/user_info")

        ob_spot = OurbitSpot(client)
        await ob_spot.__aenter__()
        await ob_spot.sub_personal()
        # await ob_spot.update('ticker')
        # print(ob_spot.store.ticker.find())

        # await ob_spot.sub_orderbook('DOLO_USDT')
        # print(ob_spot.store.book.find())
        await ob_spot.update('balance')
        # symbols = [d['symbol'] for d in ob_spot.store.ticker.find()][:5]

        # await ob_spot.sub_orderbook(symbols)

        # # print(len(ob_spot.store.book.find()))
        # import pandas as pd 
        # print(pd.DataFrame(ob_spot.store.book.find({'S': 'a'})))


        # while True:
        #     await ob_spot.store.book.wait()
        #     print(len(ob_spot.store.book.find()))


        while True:
            await ob_spot.store.balance.wait()
            print(ob_spot.store.balance.find())
        
        return

        await store.initialize(
            client.get("https://www.ourbit.com/api/platform/spot/market/v2/tickers")
        )

        print(store.ticker.find())

        return

        await store.initialize(
            client.get(
                "https://www.ourbit.com/api/platform/spot/market/depth?symbol=XRP_USDT"
            )
        )

        print(store.book.find())

        client.ws_connect(
            "wss://www.ourbit.com/ws?platform=web",
            send_json={
                "method": "SUBSCRIPTION",
                "params": ["spot@public.increase.aggre.depth@XRP_USDT"],
                "id": 3,
            },
            hdlr_json=store.onmessage,
        )
        while True:
            await store.book.wait()
            # await asyncio.sleep(1)
            print(store.book.find())
            # print(store.book.find({'s': 'XRP_USDT', 'S': 'a'}))
            # print(store.book.find({'s': 'XRP_USDT', 'S': 'b' }))
            # print(store.book.find())
            # ts = time.time()*1000
            # book = store.book.sorted({'s': 'XRP_USDT'}, 1)
            # print(f'排序耗时: {time.time()*1000 - ts:.2f} ms')

async def test_watch_order():


    async def watch_orders(ob_spot: OurbitSpot):
        with ob_spot.store.orders.watch() as stream:
            async for change in stream:
                print(change.data)
                # data = change.data
                # if change.operation == 'delete':
                #     state = data['state']
                #     if state == 'filled':
                #         price = float(data['avg_price'])
                #         quantity = float(data['deal_quantity'])
                #         ts = time.time() * 1000
                #         symbol = data['symbol']
                #         print(price, quantity, ts, symbol, '@@@@')

    async with pybotters.Client(apis={
        "ourbit": [
            "WEB3bf088f8b2f2fae07592fe1a6240e2d798100a9cb2a91f8fda1056b6865ab3ee"
        ]
    }) as client:
        ob_spot = OurbitSpot(client)
        await ob_spot.__aenter__()
        await ob_spot.sub_personal()
        await watch_orders(ob_spot)

        # with ob_spot.store.orders.watch() as stream:
        #     oid = await ob_spot.place_order('SOL_USDT', 'buy',  order_type='market', price=205, quantity=0.03 )
        #     print(oid)
        #     async for change in stream:
        #         print(change)


        # await asyncio.sleep(1)
        # order = ob_spot.store.orders.get({'order_id': oid})
        # print(order)

async def test_cancel_order():
    async with pybotters.Client(apis={
        "ourbit": [
            "WEB3bf088f8b2f2fae07592fe1a6240e2d798100a9cb2a91f8fda1056b6865ab3ee"
        ]
    }) as client:
        ob_spot = OurbitSpot(client)
        await ob_spot.__aenter__()
        # await ob_spot.sub_personal()
        # await ob_spot.update('all')

        # oid = await ob_spot.place_order('SOL_USDT', 'sell',  order_type='market', quantity=0.03 )
        # print(oid)
        await ob_spot.cancel_order('C01__592652131010363393')


async def test_orderbook():
    async with pybotters.Client(apis={
        "ourbit": [
            "WEB3bf088f8b2f2fae07592fe1a6240e2d798100a9cb2a91f8fda1056b6865ab3ee"
        ]
    }) as client:
        ob_spot = OurbitSpot(client)
        await ob_spot.__aenter__()
        await ob_spot.update('ticker')
        # symbols = [d['symbol'] for d in ob_spot.store.ticker.find()][:30]
        symbols = ['ETC_USDT']

        await ob_spot.sub_orderbook(symbols)
        while True:
            await ob_spot.store.book.wait()
            print(ob_spot.store.book.find())

async def close_spot():
    async with pybotters.Client(apis={
        "ourbit": [
            "WEB3bf088f8b2f2fae07592fe1a6240e2d798100a9cb2a91f8fda1056b6865ab3ee"
        ]
    }) as client:
        ob_spot = OurbitSpot(client)
        await ob_spot.__aenter__()
        await ob_spot.update('balance')
        print(ob_spot.store.balance.find())
        # await ob_spot.place_order('FLOKI_USDT', 'sell', order_type='market', quantity=216574)
        for b in ob_spot.store.balance.find():
            if  b['currency'] != 'USDT':
                symbol = f"{b['currency']}_USDT"
                try:
                    oid = await ob_spot.place_order(symbol, 'sell', order_type='market', quantity=float(b['available']))
                    print(f'已下单 {oid}')
                except Exception as e:
                    print(f'下单失败 {e}')

if __name__ == "__main__":
    asyncio.run(close_spot())


