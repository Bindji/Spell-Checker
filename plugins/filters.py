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


def phonetic_normalize(text: str) -> str:
    text = text.lower()

    replacements = {
        "aa": "a",
        "ee": "i",
        "oo": "u",
        "ph": "f",
        "bh": "b",
        "dh": "d",
        "th": "t",
        "kh": "k",
        "gh": "g",
        "sh": "s",
        "ch": "c",
        "zh": "j",
        "y": "i"
    }

    for k, v in replacements.items():
        text = text.replace(k, v)
    # remove non letters
    text = re.sub(r'[^a-z]', '', text)
    # remove repeated letters
    text = re.sub(r'(.)\1+', r'\1', text)
    return text

def smart_score(user_title, tmdb_title):
    # raw score
    s1 = fuzz.ratio(user_title, tmdb_title)
    s2 = fuzz.token_sort_ratio(user_title, tmdb_title)

    # phonetic score
    p1 = phonetic_normalize(user_title)
    p2 = phonetic_normalize(tmdb_title)
    s3 = fuzz.ratio(p1, p2)

    return max(s1, s2, s3)
    
# 🎬 Movie name corrector
async def correct_movie_name(query: str):
    query = query.strip()
    if not query:
        return None

    # 🔹 Extract year
    year_match = re.search(r'(19|20)\d{2}', query)
    year = int(year_match.group()) if year_match else None

    # 🔹 Clean title
    title = re.sub(r'(19|20)\d{2}', '', query).strip().lower()
    if not title:
        return None

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

    # 🔥 Strict year match
    if year:
        results = [
            m for m in results
            if m.get("release_date", "").startswith(str(year))
        ]
        if not results:
            return None

    scored = []
    for movie in results:
        tmdb_title = (movie.get("title") or "").lower()
        original_title = (movie.get("original_title") or "").lower()

        score = max(
            smart_score(title, tmdb_title),
            smart_score(title, original_title)
        )

        if score < 60:
            continue

        scored.append((score, movie))

    if not scored:
        return None

    scored.sort(
        key=lambda x: (
            x[0],
            x[1].get("vote_count", 0),
            x[1].get("popularity", 0)
        ),
        reverse=True
    )

    movie = scored[0][1]
    year = movie.get("release_date", "")[:4]

    return f"{movie['title']} ({year})" if year else movie["title"]


@Client.on_message(filters.text & filters.private)
async def movie_handler(client, message):
    wait = await message.reply("🔍 Searching correct name...")
    name = await correct_movie_name(message.text)

    if not name:
        return await wait.edit("❌ Movie not found")

    await wait.edit(f"✅ Correct Movie Name:\n\n🎬 **{name}**")
