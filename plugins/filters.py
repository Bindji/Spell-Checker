from pyrogram import Client, filters
import asyncio
from imdb import IMDb
from aiohttp import web
import re
from imdb import IMDb
import asyncio
import json

import aiohttp

API_KEY = "6311677ef041038470aae345cd71bb78"

async def correct_movie_name(query):
    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": API_KEY,
        "query": query,
        "language": "en-US"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as r:
            data = await r.json()

    if not data.get("results"):
        return None

    # 🔥 Sort by popularity (HIGH → LOW)
    results = sorted(
        data["results"],
        key=lambda x: x.get("popularity", 0),
        reverse=True
    )

    return results[0]["title"]
    
"""async def correct_movie_name(query):
    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": API_KEY,
        "query": query,
        "language": "en-US"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as r:
            data = await r.json()

    if not data.get("results"):
        return None

    return data["results"][0]["title"]"""



@Client.on_message(filters.text & filters.private)
async def movie_handler(client, message):
    wait = await message.reply("🔍 Searching correct name...")
    name = await correct_movie_name(message.text)

    if not name:
        return await wait.edit("❌ Movie not found")

    await wait.edit(f"✅ Correct Movie Name:\n\n🎬 **{name}**")
