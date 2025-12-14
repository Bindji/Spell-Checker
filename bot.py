
import asyncio
from pyrogram import Client, filters, idle
from imdb import IMDb
from aiohttp import web

# ---------------- CONFIG ----------------
API_ID = 21692958
API_HASH = "7aafe6264759352e9459eb434457c8f3"
BOT_TOKEN = "7140468132:AAEBJRdQLmBbeYh1Us-LpU2NlKaG1fK-8AY"

# ---------- Web Server (Koyeb / Render) ----------
"""async def handle(request):
    return web.Response(text="I'm alive!")

app = web.Application()
app.router.add_get("/", handle)"""

# ---------------- BOT -------------------
bot = Client(
    "MovieCorrectorBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins={"root": "plugins"}
)

# -------- Run Everything --------
"""async def main():
    await bot.start()
    print("🤖 Bot Started")

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, port=8080)
    await site.start()
    print("🌐 Web Server Started")

    await idle()   # ✅ correct usage

asyncio.run(main())"""
bot.run()
