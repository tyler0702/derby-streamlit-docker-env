import streamlit as st
import requests
import urllib.parse
import os
import json

def get_access_token(client_id, client_secret):
    """Authenticate with the Spotify API and get an access token"""
    auth_url = 'https://accounts.spotify.com/api/token'
    response = requests.post(auth_url, data={
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    })
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        st.error("Failed to authenticate with Spotify API")
        return None

def search_artists_by_genre(genre, token):
    """Search for artists by genre and exclude specific artists from the results."""
    genre_encoded = urllib.parse.quote(genre)  # ジャンルをURLエンコード
    url = f"https://api.spotify.com/v1/search?q=genre%3A{genre_encoded}&type=artist&limit=50"
    headers = {"Authorization": f"Bearer {token}"}

    # 現在のファイルのディレクトリを取得
    base_dir = os.path.dirname(__file__)
    # 'src/api' から 'src/data' に移動するための相対パスを使用
    file_path = os.path.join(base_dir, '..', 'data', 'artist.json')
    with open(file_path, 'r', encoding='utf-8') as file:
        jsondata = json.load(file)
        excluded_artists = jsondata.get("excluded", {})

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        artists = response.json()['artists']['items']
        # 除外するアーティスト名をリストから除外
        filtered_artists = [artist for artist in artists if artist['name'] not in excluded_artists]
        artist_data = [{
            "id": artist['id'],
            "name": artist['name']
        } for artist in filtered_artists]
        return artist_data
    else:
        return []

# その他のSpotify関連の関数...
def get_artists_details(artists, token):
    """Get detailed information for each artist and sort by popularity"""
    artist_details = []
    for artist in artists:
        url = f"https://api.spotify.com/v1/artists/{artist['id']}"
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            artist_details.append({
                "id": data['id'],
                "name": data['name'],
                "popularity": data['popularity'],
                "followers": data['followers']['total'],
                "image": data['images'][0]['url'] if data['images'] else None
            })
    # Sort the artists by popularity before returning
    return sorted(artist_details, key=lambda x: x['popularity'], reverse=True)

def get_top_tracks(artist_id, token):
    """Get top tracks of the artist by artist ID"""
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?market=US"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        tracks = response.json()['tracks']
        return sorted(tracks, key=lambda x: x['popularity'], reverse=True)[:5]
    else:
        return []
    
def get_audio_features(track_id, token):
    """Get audio features for a given track"""
    url = f"https://api.spotify.com/v1/audio-features/{track_id}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None