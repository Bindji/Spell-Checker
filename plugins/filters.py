from pyrogram import Client, filters
import asyncio
from imdb import IMDb
from aiohttp import web

imdb = IMDb()
CACHE = {}

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
      
@Client.on_message(filters.text & filters.private)
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
