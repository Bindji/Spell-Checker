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


def clean_text(t: str):
    return re.sub(r'[^a-z0-9]', '', t.lower())

async def correct_movie_name(query: str):
    query = query.strip()

    # 🔹 Extract year (1900–2099)
    year_match = re.search(r'(19|20)\d{2}', query)
    year = int(year_match.group()) if year_match else None

    # 🔹 Clean title (remove year)
    title = re.sub(r'(19|20)\d{2}', '', query).strip()
    clean_title = clean_text(title)

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

    matched = []

    for movie in results:
        release_date = movie.get("release_date")
        movie_title = movie.get("title", "")
        movie_clean = clean_text(movie_title)

        # 🔹 Year must match (if provided)
        if year:
            if not release_date or not release_date[:4].isdigit():
                continue
            if int(release_date[:4]) != year:
                continue

        # 🔹 Flexible title match (Salaar vs Salaar Part 1)
        if clean_title in movie_clean or movie_clean in clean_title:
            matched.append(movie)

    if not matched:
        return None

    # 🔥 Pick most popular
    matched.sort(
        key=lambda x: (x.get("vote_count", 0), x.get("popularity", 0)),
        reverse=True
    )

    return matched[0]["title"]
    

@Client.on_message(filters.text & filters.private)
async def movie_handler(client, message):
    wait = await message.reply("🔍 Searching correct name...")
    name = await correct_movie_name(message.text)

    if not name:
        return await wait.edit("❌ Movie not found")

    await wait.edit(f"✅ Correct Movie Name:\n\n🎬 **{name}**")
