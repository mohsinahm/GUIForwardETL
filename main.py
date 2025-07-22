from flet import *
import flet_fastapi
import GUILoginScreen as GLS

async def root_main(page: Page):
    await page.add_async(GLS.LoginScreen(page).LoginScreen)

app = flet_fastapi.FastAPI()

app.mount("/", flet_fastapi.app(root_main))