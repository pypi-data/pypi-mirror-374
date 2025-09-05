import asyncio
import random
import time
import pybotters
import hyperquant
from hyperquant.broker.models.ourbit import OurbitSpotDataStore
from hyperquant.broker.ourbit import OurbitSpot
from hyperquant.core import Exchange


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
        await ob_spot.update('balance')

        e = Exchange([], fee=0, initial_balance=0)

        print(ob_spot.store.balance.find())

        for info in ob_spot.store.balance.find():
            coin = info['currency']
            if info['currency'] == 'USDT':
                e.account['USDT']['total'] = float(info['available'])
            else:
                if coin not in e.account:
                    e.account[coin] = e._act_template
                e.account[coin]['amount'] = float(info['available'])
                e.account[coin]['hold_price'] = float(info['avg_price'])
                e.account[coin]['price'] = float(info['avg_price'])
                e.account[coin]['value'] = float(info['avg_price']) * float(info['available'])

        # "amount": 1,
        # "hold_price": 1000.0,
        # "value": 1000.0,
        # "price": 1000.0,
        print(e.account)


asyncio.run(main())
# e = Exchange([], fee=0)
# e.Buy('btc', 1000, 1)
# e.Update({'btc':1500})
# print(e.account)
# print(e.available_margin)