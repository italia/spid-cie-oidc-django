import asyncio
from pyppeteer import launch
import os
import json

BASE_FOLDER = os.path.join(".","spid_cie_oidc","relying_party_test","snippets","results")


class Crawler:

    def __init__(self, url: str, username: str, password: str, testname: str, browser=None):
        self.url = url
        self.username = username
        self.password = password
        self.testname = testname
        self.waiting = {"timeout": 60000, "waitUntil": "networkidle0"}
        if browser:
            self.browser = browser

    def make_dir_result(self):
        self.folder = os.path.join(BASE_FOLDER, self.testname)
        if not os.path.exists(self.folder):
            os.mkdir(self.folder)

    async def start(self, page= None):
        self.browser = await launch(headless=False, args= ['--start-maximized'])
        if page:
            self.page = page
        else:
            self.page = await self.browser.newPage()
            await self.page.setViewport({"width": 1866, "height": 900})

        page = await self.page.goto(self.url)
        self.status = page.status

    # async def init_browser(self):
    #         self.browser = await launch(headless=False, args= [ '--start-maximized' ])

    # async def make_page(self,page=None):
    #     if page:
    #         self.page = page
    #     else:
    #         self.page = await self.browser.newPage()
    #         await self.page.setViewport({ "width": 1866, "height": 900})

    # async def goto_url(self):
    #     await self.page.goto(self.url)

    async def goto_login_provider(self):
        spid_button = await self.page.querySelector(".italia-it-button-icon")
        await spid_button.click()
        provider = await self.page.querySelector("#provider-spid")
        await provider.click()
        await asyncio.ensure_future(self.page.waitForNavigation(self.waiting))

    async def login(self):
        lable1 = await self.page.querySelector("#label_username")
        await lable1.click()
        await lable1.type(self.username)
        lable2 = await self.page.querySelector("#label_password")
        await lable2.click()
        await lable2.type(self.password)
        submit = await self.page.querySelector("#submit")
        await submit.click()
        page = await asyncio.ensure_future(self.page.waitForNavigation(self.waiting))
        self.status = page.status

    async def consent(self, selector:str):
        button = await self.page.querySelector(selector)
        await button.click()
        page = await asyncio.ensure_future(self.page.waitForNavigation(self.waiting))
        self.status = page.status

    async def print_result(self, content, filename, extension):
        file_name = os.path.join(self.folder, f'{filename}{extension}')
        f = open(file_name, 'w')
        f.write(content)
        f.close()

    async def save_result(self):
        file_path = os.path.join(self.folder, f'{self.testname}.png')
        html = await self.page.content()
        status_code = {"status_code": self.status}
        await self.print_result(html, self.testname, ".html")
        await self.print_result(json.dumps(status_code), "status", ".json")
        await self.page.screenshot({'path': file_path})
