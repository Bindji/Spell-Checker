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

"""async def correct_movie_name(query: str):
    query = query.strip()

    # 🔹 year extract
    year_match = re.search(r'(19|20)\d{2}', query)
    year = year_match.group() if year_match else None
    title = re.sub(r'(19|20)\d{2}', '', query).strip()

    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": API_KEY,
        "query": title,
        "language": "en-US",
        "include_adult": "false"
    }

    if year:
        params["primary_release_year"] = year

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as r:
            data = await r.json()

    if not data.get("results"):
        return None

    # 🔥 Filter Indian / popular movies
    results = sorted(
        data["results"],
        key=lambda x: (
            x.get("vote_count", 0),
            x.get("popularity", 0)
        ),
        reverse=True
    )

    return results[0]["title"]"""
    
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


INDIAN_LANGS = {"hi", "te", "ta", "ml", "kn"}

def normalize(text: str):
    return re.sub(r'[^a-z0-9]', '', text.lower())

async def correct_movie_name(query: str):
    query = query.strip()

    # 🎯 Year extract
    year_match = re.search(r'(19|20)\d{2}', query)
    year = int(year_match.group()) if year_match else None

    # 🎯 Title extract
    title = re.sub(r'(19|20)\d{2}', '', query).strip()
    norm_title = normalize(title)

    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": API_KEY,
        "query": title,
        "include_adult": "false"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as r:
            data = await r.json()

    results = data.get("results", [])
    if not results:
        return None

    scored = []

    for m in results:
        m_title = m.get("title", "")
        m_norm = normalize(m_title)
        lang = m.get("original_language")
        vote = m.get("vote_count", 0)
        pop = m.get("popularity", 0)
        release = m.get("release_date", "")

        # ❌ Year strict
        if year:
            if not release or release[:4] != str(year):
                continue

        score = 0

        # ✅ Title similarity
        if norm_title in m_norm:
            score += 50
        if m_norm.startswith(norm_title):
            score += 20

        # ✅ Indian language boost
        if lang in INDIAN_LANGS:
            score += 40

        # ✅ Popularity
        score += min(vote / 1000, 30)
        score += min(pop / 10, 30)

        scored.append((score, m_title))

    if not scored:
        return None

    scored.sort(reverse=True, key=lambda x: x[0])
    return scored[0][1]
    

@Client.on_message(filters.text & filters.private)
async def movie_handler(client, message):
    wait = await message.reply("🔍 Searching correct name...")
    name = await correct_movie_name(message.text)

    if not name:
        return await wait.edit("❌ Movie not found")

    await wait.edit(f"✅ Correct Movie Name:\n\n🎬 **{name}**")
