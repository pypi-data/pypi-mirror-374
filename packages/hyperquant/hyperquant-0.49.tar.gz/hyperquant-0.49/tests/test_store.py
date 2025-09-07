import asyncio
import pybotters


async def main():
    ds = pybotters.store.DataStore(keys=["id"])
    loop = asyncio.get_running_loop()

    wait_task = loop.create_task(ds.wait())
    loop.call_soon(
        ds._insert, [{"id": 1, "val": 1}, {"id": 2, "val": 2}, {"id": 3, "val": 3}]
    )
    await asyncio.wait_for(wait_task, timeout=5.0)

    ds._insert, [{"id": 1, "val": 1}, {"id": 2, "val": 2}, {"id": 3, "val": 3}]

