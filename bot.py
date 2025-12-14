
import asyncio
from pyrogram import Client, filters, idle
from imdb import IMDb
from aiohttp import web

# ---------------- CONFIG ----------------
API_ID = 21692958
API_HASH = "7aafe6264759352e9459eb434457c8f3"
BOT_TOKEN = "7140468132:AAEBJRdQLmBbeYh1Us-LpU2NlKaG1fK-8AY"

# ---------------------------------------

imdb = IMDb()
CACHE = {}

# ---------- Web Server (Koyeb / Render) ----------
async def handle(request):
    return web.Response(text="I'm alive!")

app = web.Application()
app.router.add_get("/", handle)

# ---------------- BOT -------------------
bot = Client(
    "MovieCorrectorBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# /start command
@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    await message.reply_text(
        "🎬 **Movie Name Corrector Bot**\n\n"
        "गलत movie name भेजो,\n"
        "मैं IMDb से सही नाम बता दूँगा ✅\n\n"
        "**Example:**\n"
        "`Dhurandar`\n"
        "`Pathan`\n"
        "`Bhool Bhulaiya`",
        quote=True
    )

# Movie name handler
@bot.on_message(filters.text & filters.private)
async def movie_handler(client, message):
    user_text = message.text.strip()
    if not user_text:
        return

    wait = await message.reply_text("🔎 Searching IMDb...")

    correct_name = await asyncio.to_thread(correct_movie_name, user_text)

    if not correct_name:
        return await wait.edit(
            f"❌ IMDb पर कोई result नहीं मिला\n\n"
            f"Search: `{user_text}`"
        )

    await wait.edit(
        f"✅ **Correct Movie Name Found**\n\n"
        f"📝 Your Input: `{user_text}`\n"
        f"🎬 IMDb Name: **{correct_name}**"
    )

# -------- IMDb Corrector --------
def correct_movie_name(query: str):
    query = query.strip()
    if not query:
        return None

    key = query.lower()
    if key in CACHE:
        return CACHE[key]

    try:
        results = imdb.search_movie(query)
        if not results:
            return None
        title = results[0].get("title")
        CACHE[key] = title
        return title
    except Exception as e:
        print("IMDb Error:", e)
        return None

# -------- Run Everything --------
async def main():
    await bot.start()
    print("🤖 Bot Started")

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, port=8080)
    await site.start()
    print("🌐 Web Server Started")

    await idle()   # ✅ correct usage

asyncio.run(main())
