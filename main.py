import requests, json, time, os

API_KEY = "6b8e3eaa1a03ebb45642e9531d8a76d2"  # remplace par ta clé TMDB
SOURCE_URL = "http://http://tv.livepremium.cc/get.php?username=7513446781&password=5494242123&type=m3u_plus&output=ts"
OUTPUT_FILE = "vod_enriched_from_server.m3u"
CACHE_FILE = "tmdb_cache.json"

# Charger le cache existant
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        cache = json.load(f)
else:
    cache = {}

def extract_entries_from_m3u(url):
    print("🔍 Extraction des entrées depuis la playlist...")
    lines = requests.get(url).text.splitlines()
    entries = []
    current_title = None
    for line in lines:
        if line.startswith("#EXTINF"):
            current_title = line.split(",")[-1].strip()
        elif line.startswith("http") and current_title:
            entries.append((current_title, line.strip()))
            current_title = None
    print(f"✅ {len(entries)} entrées trouvées.")
    return entries

def fetch_tmdb_data(title):
    # Vérifier si le titre est déjà dans le cache
    if title in cache:
        return cache[title]

    # Recherche film
    movie_url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={title}&language=fr"
    tv_url = f"https://api.themoviedb.org/3/search/tv?api_key={API_KEY}&query={title}&language=fr"
    movie_data = requests.get(movie_url).json()
    tv_data = requests.get(tv_url).json()

    data = None
    media_type = None
    if movie_data.get("results"):
        data = movie_data["results"][0]
        media_type = "Films"
    elif tv_data.get("results"):
        data = tv_data["results"][0]
        media_type = "Séries"

    if data:
        # Récupérer les genres
        genre_url = f"https://api.themoviedb.org/3/genre/{'movie' if media_type=='Films' else 'tv'}/list?api_key={API_KEY}&language=fr"
        genre_list = requests.get(genre_url).json().get("genres", [])
        genres = [g["name"] for g in genre_list if g["id"] in data.get("genre_ids", [])]

        info = {
            "title": data.get("title") or data.get("name"),
            "overview": data.get("overview", ""),  # déjà en français grâce à language=fr
            "poster": f"https://image.tmdb.org/t/p/w500{data['poster_path']}" if data.get("poster_path") else "",
            "year": data.get("release_date", data.get("first_air_date", ""))[:4],
            "genres": ", ".join(genres) if genres else "Autres",
            "type": media_type,
            "note": data.get("vote_average", 0)  # la note TMDB
        }

        # Sauvegarder dans le cache
        cache[title] = info
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)

        return info
    return None

def generate_m3u():
    entries = extract_entries_from_m3u(SOURCE_URL)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for title, link in entries:
            info = fetch_tmdb_data(title)
            if info:
                f.write(f'#EXTINF:-1 tvg-logo="{info["poster"]}" group-title="{info["type"]} | {info["genres"]}", {info["title"]} ({info["year"]}) ★{info["note"]}\n')
                f.write(f'#DESCRIPTION:{info["overview"]}\n')
                f.write(f"{link}\n")  # ⚡️ On garde ton lien original
                time.sleep(0.3)
    print(f"✅ Fichier enrichi généré : {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_m3u()
