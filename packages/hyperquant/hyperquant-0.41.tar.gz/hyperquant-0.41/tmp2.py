import asyncio
from pybotters.store import DataStore

store = DataStore(keys=['oid'])

async def place():
    # 模拟服务器返回
    store._insert([{'oid': 1}])
    # store._delete([{'oid': 1}])
    store._find_and_delete({'oid':1})
    await asyncio.sleep(0.1)
    return

async def loop_orders():
    with store.watch() as stream:
        async for change in stream:
            print('loop_orders', change)

async def main():
    asyncio.create_task(loop_orders())


    with store.watch() as stream:
        await place()
        print('下单完成')
        async for change in stream:
            print(change)

if __name__ == "__main__":
    asyncio.run(main())


