import asyncio
from crawler import Crawler

OIDC_RP_REQUESTS = {
    "full_authentication_ok": "http://localhost:8000/oidc/rp/landing",
}


class Pypper:

    def __init__(self) -> None:
        pass

    async def authentication_ok():
        c = Crawler(OIDC_RP_REQUESTS["full_authentication_ok"],
                    "user",
                    "oidcuser",
                    "authentication_ok"
        )
        c.make_dir_result()
        await c.start()
        await c.goto_login_provider()
        await c.login()
        await c.consent("#agree")
        await c.save_result()
        await c.browser.close()

    async def test2():
        c = Crawler(OIDC_RP_REQUESTS["request_ok"],
                    "user",
                    "oidcuser",
                    "send_request_ok"
        )
        c.make_dir_result()
        await c.start()
        await c.save_result()
        await c.browser.close()

    if __name__ == "__main__":
        asyncio.run(authentication_ok())
