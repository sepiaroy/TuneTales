from dotenv import load_dotenv
import os
import base64
import requests
import json
from collections import Counter
import detectMoods

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")


def get_token():
    auth_string = f"{client_id}:{client_secret}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {"grant_type": "client_credentials"}
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]


def get_auth_header(token):
    return {"Authorization": "Bearer " + token}


def get_playlists_for_mood(mood, limit=3):
    token = get_token()
    headers = get_auth_header(token)

    search_url = "https://api.spotify.com/v1/search"
    params = {
        "q": mood,
        "type": "playlist",
        "limit": limit
    }

    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()

    data = response.json()['playlists']['items']
    playlists = []

    for item in data:
        if item and "name" in item and "id" in item:
            playlists.append({
                "name": item["name"],
                "id": item["id"],
                "url": item["external_urls"]["spotify"],
                "owner": item["owner"]["display_name"]
            })

    return playlists


def get_tracks_from_playlist(playlist_id, limit=50):
    token = get_token()
    headers = get_auth_header(token)

    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    params = {"limit": limit}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    data = response.json()['items']
    tracks = []

    for item in data:
        track = item.get('track')
        if track and track.get("id"):
            artist_names = [
                str(a["name"]) for a in track.get("artists", [])
                if a and "name" in a and a["name"] is not None
            ]
            tracks.append({
                "id": track["id"],
                "name": track.get("name", "Unknown Title"),
                "artists": ", ".join(artist_names),
                "url": track["external_urls"]["spotify"],
                "preview_url": track.get("preview_url")
            })

    return tracks


def get_top_7_tracks_for_mood(mood, playlists_per_mood=3, track_limit=20):
    track_counter = Counter()
    track_details = {}

    playlists = get_playlists_for_mood(mood, limit=playlists_per_mood)

    for pl in playlists:
        tracks = get_tracks_from_playlist(pl["id"], limit=track_limit)
        for tr in tracks:
            track_counter[tr["id"]] += 1
            track_details[tr["id"]] = tr

    most_common = track_counter.most_common()

    # 7 tracks
    top_tracks = []
    for track_id, count in most_common:
        if len(top_tracks) >= 7:
            break
        top_tracks.append(track_details[track_id])

    return top_tracks


def recommend_songs_per_mood(moods):
    all_tracks = []
    used_ids = set()

    for mood in moods:
        mood_tracks = get_top_7_tracks_for_mood(mood)  # still returns up to 7
        unique_tracks = [t for t in mood_tracks if t["id"] not in used_ids]

        for t in unique_tracks:
            used_ids.add(t["id"])

        all_tracks.extend(unique_tracks)

    return all_tracks


def findSongs(book_title, book_author):
    moods = detectMoods.get_top_moods_for_book(book_title, book_author)

    if not moods:
        print("Moods not found.")
        return []

    print(f"Top 3 moods for '{book_title}' by {book_author}: {moods}")
    return recommend_songs_per_mood(moods)


# 🔹 Example usage
if __name__ == "__main__":
    book_title = "Twilight"
    book_author = "Stephenie Meyers"

    songs = findSongs(book_title, book_author)

    if not songs:
        print("Songs not found for these moods.")
    else:
        print("\n🎵 Top Recommended Songs 🎵\n")
        for i, tr in enumerate(songs, 1):
            print(f"{i}. {tr['name']} by {tr['artists']}")
            print(f"   ▶️ {tr['url']}\n")
