import time

from param_server.client import AsyncParameterClient

HOST = "localhost"
PORT = 8888
TIMEOUT = 2.0


PATH = "camera.gain"
VALUE = 2.5


async def main():
    client = AsyncParameterClient(HOST, PORT)
    await client.connect()

    async def set_fn():
        await client.set(PATH, VALUE)

    async def get_fn():
        await client.get(PATH)

    async def ping_fn():
        await client.ping()

    for cmd, fn in [
        ("set", set_fn),
        ("get", get_fn),
        ("ping", ping_fn),
    ]:
        t0 = time.perf_counter()
        for i in range(1000):
            await fn()
        t1 = time.perf_counter()
        print(f"{cmd} took {(t1-t0):.2f} ms")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
