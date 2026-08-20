import asyncio
import base64
import os
from playwright.async_api import async_playwright


class ImageGenerator:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.url = os.environ.get("TARGET_URL", "aHR0cHM6Ly9haWNyZWF0ZS5jb20vdGV4dC10by1pbWFnZS1nZW5lcmF0b3Iv")
        self.browser = None
        self.page = None

    async def start(self):
        url_decoded = base64.b64decode(self.url).decode()
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=["--incognito"]
        )
        context = await self.browser.new_context()
        self.page = await context.new_page()
        await self.page.goto(url_decoded, wait_until="networkidle")

    async def close(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def generate(self, prompt: str) -> dict:
        try:
            textarea = self.page.locator('textarea[placeholder*="futuristic"]')
            await textarea.wait_for(state="visible", timeout=10000)
            await textarea.fill(prompt)

            generate_btn = self.page.locator('button:has-text("Generate Image")')
            await generate_btn.click()

            await self._handle_modal()

            error_div = self.page.locator('[data-t2i-error="true"]')
            try:
                await error_div.wait_for(state="visible", timeout=5000)
                await error_div.evaluate("el => el.remove()")
                return {"success": False, "error": "Demasiadas solicitudes, intenta de nuevo en ~12 segundos."}
            except Exception:
                pass

            img_locator = self.page.locator('.flex.h-\\[20rem\\] img, .flex.h-\\[24rem\\] img').first
            await img_locator.wait_for(state="visible", timeout=60000)

            base64_image = await img_locator.evaluate('''async (img) => {
                const response = await fetch(img.src);
                const blob = await response.blob();
                return new Promise((resolve) => {
                    const reader = new FileReader();
                    reader.onloadend = () => resolve(reader.result.split(',')[1]);
                    reader.readAsDataURL(blob);
                });
            }''')

            return {"success": True, "image": base64_image}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _handle_modal(self):
        try:
            skip_btn = self.page.locator('button:has-text("Skip & continue")')
            await skip_btn.wait_for(state="visible", timeout=5000)
            await skip_btn.click()
        except Exception:
            pass
