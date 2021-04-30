import asyncio


def retry(on: Exception, retries: int):
    def wrapper(fn):
        async def wrapped(*args, **kwargs):
            for _ in range(3):
                try:
                    await fn(*args, **kwargs)
                except on:
                    print('retrying in 3 seconds')
                    await asyncio.sleep(3)
                    continue
                else:
                    break
        return wrapped
    return wrapper
