import requests, re, time

API_KEY = "TA_CLE_TMDB"
SOURCE_URL = "https://raw.githubusercontent.com/jromero88/iptv/master/VOD.m3u"
OUTPUT_FILE = "6b8e3eaa1a03ebb45642e9531d8a76d2"

def extract_titles_from_m3u(url):
    print("🔍 Extraction des titres depuis la playlist...")
    lines = requests.get(url).text.splitlines()
    titles = []
    for line in lines:
        if line.startswith("#EXTINF"):
            title = line.split(",")[-1].strip()
            if title and not title.lower().startswith("http"):
                titles.append(title)
    print(f"✅ {len(titles)} titres trouvés.")
    return titles

def fetch_tmdb_data(title):
    # Recherche film
    movie_url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={title}&language=fr"
    tv_url = f"https://api.themoviedb.org/3/search/tv?api_key={API_KEY}&query={title}&language=fr"
    movie_data = requests.get(movie_url).json()
    tv_data = requests.get(tv_url).json()

    data = None
    media_type = None
    if movie_data["results"]:
        data = movie_data["results"][0]
        media_type = "Films"
    elif tv_data["results"]:
        data = tv_data["results"][0]
        media_type = "Séries"

    if data:
        genres = [g["name"] for g in requests.get(
            f"https://api.themoviedb.org/3/genre/{'movie' if media_type=='Films' else 'tv'}/list?api_key={API_KEY}&language=fr"
        ).json()["genres"] if g["id"] in data.get("genre_ids", [])]
        return {
            "title": data.get("title") or data.get("name"),
            "overview": data.get("overview", ""),
            "poster": f"https://image.tmdb.org/t/p/w500{data['poster_path']}" if data.get("poster_path") else "",
            "year": data.get("release_date", data.get("first_air_date", ""))[:4],
            "genres": ", ".join(genres) if genres else "Autres",
            "type": media_type
        }
    return None

def generate_m3u():
    titles = extract_titles_from_m3u(SOURCE_URL)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for title in titles:
            info = fetch_tmdb_data(title)
            if info:
                f.write(f'#EXTINF:-1 tvg-logo="{info["poster"]}" group-title="{info["type"]} | {info["genres"]}", {info["title"]} ({info["year"]})\n')
                f.write(f'#DESCRIPTION:{info["overview"]}\n')
                f.write(f"http://tonserveur.com/vod/{title.replace(' ', '_')}.mp4\n")
                time.sleep(0.3)
    print(f"✅ Fichier enrichi généré : {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_m3u()
