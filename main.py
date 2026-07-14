import requests, json
from datetime import datetime
import os

API_KEY = os.getenv("TMDB_API_KEY")  # clé API stockée dans GitHub Secrets
OUTPUT_FILE = "vod_enriched.m3u"

def fetch_tmdb_data(title, media_type="movie"):
    url = f"https://api.themoviedb.org/3/search/{media_type}?api_key={API_KEY}&query={title}&language=fr"
    data = requests.get(url).json()
    if data["results"]:
        item = data["results"][0]
        return {
            "title": item["name"] if media_type == "tv" else item["title"],
            "overview": item["overview"],
            "poster": f"https://image.tmdb.org/t/p/w500{item['poster_path']}" if item.get("poster_path") else "",
            "year": item["first_air_date"][:4] if media_type == "tv" else item["release_date"][:4],
            "type": "Série" if media_type == "tv" else "Film"
        }
    return None

def generate_m3u():
    with open("vod_list.json", "r", encoding="utf-8") as f:
        vod_data = json.load(f)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        f.write(f"# Mise à jour : {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")

        for title in vod_data["movies"]:
            info = fetch_tmdb_data(title, "movie")
            if info:
                f.write(f'#EXTINF:-1 tvg-logo="{info["poster"]}" group-title="Films", {info["title"]} ({info["year"]})\n')
                f.write(f'#DESCRIPTION:{info["overview"]}\n')
                f.write(f"http://tonserveur.com/vod/{title.replace(' ', '_')}.mp4\n")

        for title in vod_data["series"]:
            info = fetch_tmdb_data(title, "tv")
            if info:
                f.write(f'#EXTINF:-1 tvg-logo="{info["poster"]}" group-title="Séries", {info["title"]} ({info["year"]})\n')
                f.write(f'#DESCRIPTION:{info["overview"]}\n')
                f.write(f"http://tonserveur.com/vod/{title.replace(' ', '_')}.mp4\n")

    print(f"✅ Fichier M3U généré : {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_m3u()
