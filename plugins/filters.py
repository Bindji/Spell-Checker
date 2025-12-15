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


ALLOWED_LANGS = {"hi", "te", "ta"}
MIN_VOTES = 500   # 🔥 random movies filter

def clean(text):
    return re.sub(r'[^a-z0-9]', '', text.lower())

async def correct_movie_name(query: str):
    query = query.strip()

    # 🎯 Year extract
    year_match = re.search(r'(19|20)\d{2}', query)
    year = year_match.group() if year_match else None

    # 🎯 Title extract
    title = re.sub(r'(19|20)\d{2}', '', query).strip()
    clean_title = clean(title)

    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": API_KEY,
        "query": title,
        "include_adult": "false",
        "region": "IN"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as r:
            data = await r.json()

    results = data.get("results", [])
    if not results:
        return None

    best = None
    best_score = 0

    for m in results:
        m_title = m.get("title", "")
        m_lang = m.get("original_language")
        votes = m.get("vote_count", 0)
        release = m.get("release_date", "")

        # ❌ Non-Indian language
        if m_lang not in ALLOWED_LANGS:
            continue

        # ❌ Low popularity random movies
        if votes < MIN_VOTES:
            continue

        # ❌ Year strict
        if year and (not release or not release.startswith(year)):
            continue

        score = 0
        ct = clean(m_title)

        # ✅ Strong title match
        if clean_title == ct:
            score += 100
        elif clean_title in ct:
            score += 70

        score += votes / 100   # popularity boost

        if score > best_score:
            best_score = score
            best = m_title

    return best

@Client.on_message(filters.text & filters.private)
async def movie_handler(client, message):
    wait = await message.reply("🔍 Searching correct name...")
    name = await correct_movie_name(message.text)

    if not name:
        return await wait.edit("❌ Movie not found")

    await wait.edit(f"✅ Correct Movie Name:\n\n🎬 **{name}**")
