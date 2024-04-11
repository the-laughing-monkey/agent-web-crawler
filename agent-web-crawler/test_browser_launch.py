import asyncio
from playwright.async_api import async_playwright

async def launch_browser():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            executable_path='/usr/bin/google-chrome-stable',
            args=[
                '--no-sandbox',
                '--disable-background-networking',
                '--disable-default-apps',
                '--disable-extensions',
                '--disable-sync',
                '--disable-translate',
                '--mute-audio',
                '--safebrowsing-disable-auto-update',
                '--ignore-certificate-errors',
                '--ignore-ssl-errors',
                '--ignore-certificate-errors-spki-list',
                '--no-zygote',
                '--disable-gpu'
            ],
        )
        page = await browser.new_page()
        await page.goto('https://google.com')
        await page.screenshot(path='google.png')
        print("Successfully opened the web page and created the screenshot 'google.png'.")
        await browser.close()

asyncio.run(launch_browser())