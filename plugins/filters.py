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

async def correct_movie_name(query: str):
    query = query.strip()

    # 🔹 Extract year (1900–2099)
    year_match = re.search(r'(19|20)\d{2}', query)
    year = int(year_match.group()) if year_match else None

    # 🔹 Remove year from title
    title = re.sub(r'(19|20)\d{2}', '', query).strip().lower()

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
        results = [
            m for m in results
            if m.get("release_date", "").startswith(str(year))
        ]
        if not results:
            return None

    # 🔥 SPELLING SIMILARITY FILTER
    scored = []
    for movie in results:
        tmdb_title = (movie.get("title") or "").lower()
        original_title = (movie.get("original_title") or "").lower()

        score1 = fuzz.ratio(title, tmdb_title)
        score2 = fuzz.ratio(title, original_title)

        best_score = max(score1, score2)

        # ❌ unrelated titles reject
        if best_score < 70:
            continue

        scored.append((best_score, movie))

    if not scored:
        return None

    # 🔥 Best match first
    scored.sort(
        key=lambda x: (
            x[0],                          # similarity
            x[1].get("vote_count", 0),
            x[1].get("popularity", 0)
        ),
        reverse=True
    )

    return scored[0][1]["title"]
    
@Client.on_message(filters.text & filters.private)
async def movie_handler(client, message):
    wait = await message.reply("🔍 Searching correct name...")
    name = await correct_movie_name(message.text)

    if not name:
        return await wait.edit("❌ Movie not found")

    await wait.edit(f"✅ Correct Movie Name:\n\n🎬 **{name}**")
