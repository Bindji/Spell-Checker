from pyrogram import Client, filters
import asyncio
from imdb import IMDb
from aiohttp import web
import re
from imdb import IMDb
import asyncio
import json
import aiohttp
from rapidfuzz import fuzz

import requests
from bs4 import BeautifulSoup


API_KEY = "6311677ef041038470aae345cd71bb78"

"""async def correct_movie_name(query: str):
    query = query.strip()

    # 🔹 Extract year (1900–2099)
    year_match = re.search(r'(19|20)\d{2}', query)
    year = int(year_match.group()) if year_match else None

    # 🔹 Remove year from title
    title = re.sub(r'(19|20)\d{2}', '', query).strip()

    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": API_KEY,
        "query": title,
        "language": "en-US",
        "include_adult": "false"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as r:
            data = await r.json()

    results = data.get("results", [])
    if not results:
        return None

    # 🔥 STRICT YEAR FILTER
    if year:
        year_matched = []
        for movie in results:
            release_date = movie.get("release_date")
            if release_date and release_date[:4].isdigit():
                if int(release_date[:4]) == year:
                    year_matched.append(movie)

        if year_matched:
            results = year_matched
        else:
            return None  # ❌ year दिया है लेकिन match नहीं मिला

    # 🔥 Sort by popularity + votes
    results.sort(
        key=lambda x: (x.get("vote_count", 0), x.get("popularity", 0)),
        reverse=True
    )

    return results[0]["title"]"""


# ---------------- GOOGLE SUGGEST ----------------
def google_suggest(query):
    url = f"https://www.google.com/search?q={query}"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")

    # Google का "Did you mean" suggestion पकड़ना
    suggestion = soup.find("a", attrs={"class": "gL9Hy"})
    if suggestion:
        return suggestion.text
    return None


# ---------------- TELEGRAM BOT ----------------
@Client.on_message(filters.command("alive"))
async def alive(client, message):
    await message.reply_text("✅ Bot is Alive and Running!")


# Command: /suggest <word>
@Client.on_message(filters.command("suggest"))
async def suggest_command(client, message):
    if len(message.command) < 2:
        return await message.reply_text("❌ Usage: /suggest <word>")
    
    query = message.command[1]
    result = google_suggest(query)
    if result:
        await message.reply_text(f"Search: {query}\nResult: {result}")
    else:
        await message.reply_text(f"Search: {query}\nResult: No suggestion found")


@Client.on_message(filters.text & filters.private)
async def movie_handler(client, message):
    wait = await message.reply("🔍 Searching correct name...")
    name = await correct_movie_name(message.text)

    if not name:
        return await wait.edit("❌ Movie not found")

    await wait.edit(f"✅ Correct Movie Name:\n\n🎬 **{name}**")
