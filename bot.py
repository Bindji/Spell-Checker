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

async def handle(request):
    return web.Response(text="I'm alive!")

app = web.Application()
app.router.add_get("/", handle)

# --------- IMDb Name Corrector ----------
def correct_movie_name(query: str):
    query = query.strip()
    if not query:
        return None

    if query.lower() in CACHE:
        return CACHE[query.lower()]

    try:
        results = imdb.search_movie(query)
        if not results:
            return None

        title = results[0].get("title")
        CACHE[query.lower()] = title
        return title
    except Exception as e:
        print("IMDb Error:", e)
        return None

# ---------------- BOT -------------------
app = Client(
    "MovieCorrectorBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# /start
@Client.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        "🎬 **Movie Name Corrector Bot**\n\n"
        "बस movie का गलत नाम भेजो,\n"
        "मैं IMDb से सही नाम बता दूँगा ✅\n\n"
        "**Example:**\n"
        "`Dhurandar`\n"
        "`Pathan`\n"
        "`Bhool Bhulaiya``",
        quote=True
    )

# Movie name handler
@Client.on_message(filters.text & filters.private)
async def movie_handler(client, message):
    user_text = message.text.strip()

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

# Run bot
async def start_bots():
    await app.start()
    print("✅ bot started")
    asyncio.create_task(idle())
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, port=8080)
    await site.start()
    print("Web server started")

loop = asyncio.get_event_loop()
loop.run_until_complete(start_bots())
loop.run_forever()
