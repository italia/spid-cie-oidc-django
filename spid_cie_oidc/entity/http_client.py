import aiohttp
import asyncio


async def fetch(session, url, httpc_params: dict = {}):
    async with session.get(url, **httpc_params.get("connection", {})) as response:
        if response.status != 200: # pragma: no cover
            # response.raise_for_status()
            return ""
        return await response.text()


async def fetch_all(session, urls, httpc_params):
    tasks = []
    for url in urls:
        task = asyncio.create_task(fetch(session, url, httpc_params))
        tasks.append(task)
    results = await asyncio.gather(*tasks)
    return results


async def http_get(urls, httpc_params: dict = {}):
    async with aiohttp.ClientSession(**httpc_params.get("session", {})) as session:
        text = await fetch_all(session, urls, httpc_params)
        return text


if __name__ == "__main__": # pragma: no cover
    httpc_params = {
        "connection": {"ssl": True},
        "session": {"timeout": aiohttp.ClientTimeout(total=4)},
    }
    urls = [
        "http://127.0.0.1:8001/.well-known/openid-federation",
        "http://127.0.0.1:8000/.well-known/openid-federation",
        "http://asdasd.it",
        "http://127.0.0.1:8001/.well-known/openid-federation",
        "http://google.it",
    ]
    asyncio.run(http_get(urls, httpc_params=httpc_params))
