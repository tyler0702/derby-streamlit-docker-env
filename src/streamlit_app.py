import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import openai
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import urllib.parse
import json

load_dotenv()
# 環境変数からSpotifyのClient IDを取得
spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
spotify_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
# lastfm
lastfm_api_key = os.getenv('LASTFM_API_KEY')

def get_lastfm_artist_info(artist_name, lastfm_api_key):
    """Retrieve artist information from Last.fm API using the provided API key."""
    url = f"http://ws.audioscrobbler.com/2.0/?method=artist.getinfo&artist={artist_name}&api_key={lastfm_api_key}&format=json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'artist' in data:
            return {
                'lastfm_listeners': int(data['artist']['stats']['listeners']),
                'lastfm_playcount': int(data['artist']['stats']['playcount'])
            }
    return {'lastfm_listeners': 0, 'lastfm_playcount': 0}

def get_access_token(client_id, client_secret):
    """Authenticate with the Spotify API and get an access token"""
    auth_url = 'https://accounts.spotify.com/api/token'
    response = requests.post(auth_url, data={
        'grant_type': 'client_credentials',
        'client_id': spotify_client_id,
        'client_secret': spotify_client_secret,
    })
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        st.error("Failed to authenticate with Spotify API")
        return None

def search_artists_by_genre(genre, not_genres, token):
    """Search for artists by genre"""
    not_genres_query = " NOT ".join(not_genres) if not_genres else ""
    url = f"https://api.spotify.com/v1/search?q=genre%3A{genre}%20{not_genres_query}&type=artist&limit=50"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        artists = response.json()['artists']['items']
        artist_data = [{
            "id": artist['id'],
            "name": artist['name']
        } for artist in artists]
        return artist_data
    else:
        return []

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
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        tracks = response.json()['tracks']
        return sorted(tracks, key=lambda x: x['popularity'], reverse=True)[:5]
    else:
        return []

def openai_query(artist_name, api_key):
    """Query OpenAI API for detailed K-POP artist information using the chat completions endpoint"""
    try:
        openai.api_key = api_key
        response = openai.ChatCompletion.create(
            # model="gpt-3.5-turbo",
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a knowledgeable assistant specializing in K-POP artists. Provide detailed information in Japanese."},
                {"role": "user", "content": f"以下の詳細を提供してください。アーティスト名：{artist_name}\n・概要：{artist_name}の音楽スタイルや特徴を500文字以内で説明してください。\n・メンバー：全メンバーの名前、年齢、役割（例：メインボーカル、リーダーなど）を含めてください。\n・デビュー日：{artist_name}の正式なデビュー日を教えてください。\n・所属レーベル：{artist_name}が所属するレーベル名を教えてください。\n・人気の秘訣：{artist_name}の人気の秘訣をいくつか挙げてください。"}
            ]
        )
        return response['choices'][0]['message']['content'].strip()
    except openai.error.OpenAIError as e:
        st.error(f"OpenAI APIからの問い合わせに失敗しました: {str(e)}")
        return None

def get_audio_features(track_id, token):
    """Get audio features for a given track"""
    url = f"https://api.spotify.com/v1/audio-features/{track_id}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def plot_radar_chart(features):
    """Plot a radar chart for the audio features of a track"""
    labels = np.array(['Danceability', 'Energy', 'Speechiness', 'Acousticness', 'Instrumentalness', 'Liveness', 'Valence'])
    stats = np.array([features['danceability'], features['energy'], features['speechiness'],
                      features['acousticness'], features['instrumentalness'], features['liveness'], features['valence']])
    
    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
    stats = np.concatenate((stats,[stats[0]]))
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.fill(angles, stats, color='red', alpha=0.25)
    ax.plot(angles, stats, color='red', linewidth=2)  # Plot the data
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)

    return fig

######
# Wikipediaスクレイピング処理
######
def load_artist_mappings(filename):
    try:
    # ファイルのフルパスを生成
        base_dir = os.path.dirname(__file__)  # 現在のファイルのディレクトリ
        file_path = os.path.join(base_dir, filename)  # artist.jsonへのパスを組み立てる
        with open(filename, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError("The file 'artist.json' was not found. Please check the file path.")
    except Exception as e:
        raise Exception(f"An error occurred: {str(e)}")


def generate_wikipedia_url(artist_name, mappings):
    # アーティスト名に対応するエントリがあればそれを使用し、なければ通常の名前をURLエンコードする
    wiki_title = mappings.get(artist_name, artist_name)
    encoded_name = urllib.parse.quote(wiki_title)
    return f"https://ja.wikipedia.org/wiki/{encoded_name}"


def fetch_wikipedia_summary(url, start_heading, end_heading):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # `<sup>` タグを除去
    for sup_tag in soup.find_all('sup'):
        sup_tag.extract()

    content = []
    start_tag = soup.find('span', id=start_heading)
    if not start_tag:
        return f"ごめんなさい '{start_heading}' なかったよー"

    current_tag = start_tag.parent  # Start from the parent of the span tag

    while current_tag:
        # Find next sibling and check if it's the end tag
        next_sibling = current_tag.find_next_sibling()
        
        if current_tag.name == 'p' or current_tag.name == 'ul':
            content.append(current_tag.text)
        if next_sibling and next_sibling.find('span', id=end_heading):
            break
        
        current_tag = next_sibling

    return '\n'.join(content) if content else "見つからなかったよ〜〜."    




def main():
    image_path = "makibao.png"
    st.image(image_path, caption='', width=100)
    st.title("DERBY's Artist Popularity and Streaming Data Tracker.v4")

    # client_id = st.sidebar.text_input("Spotify Client ID")
    # client_secret = st.sidebar.text_input("Spotify Client Secret")
    # lastfm_api_key = st.sidebar.text_input("Last.fm API Key")
    genre = st.sidebar.text_input("Genre", value='k-pop')
    not_genres = st.sidebar.text_input("Not Genres (comma-separated)")
    openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
    num_artists = st.sidebar.slider("Number of Top Artists to Display", 5, 30, 10, 1)

    if spotify_client_id and spotify_client_secret:
        spotify_token = get_access_token(spotify_client_id, spotify_client_secret)
        if spotify_token:
            artists_data = search_artists_by_genre(genre, not_genres.split(','), spotify_token)
            detailed_artists = get_artists_details(artists_data[:num_artists], spotify_token)

            for artist in detailed_artists:
                lastfm_info = get_lastfm_artist_info(artist['name'], lastfm_api_key)
                artist.update(lastfm_info)

            df = pd.DataFrame(detailed_artists)
            df.index = df.index + 1
            st.dataframe(df[['name', 'popularity', 'followers', 'lastfm_listeners', 'lastfm_playcount']])

            artist_choice = st.selectbox("Select an artist for more details", df['name'])
            if artist_choice:
                artist_info = df[df['name'] == artist_choice].iloc[0]

                st.subheader("Artist Details:")
                st.write(f"Name: {artist_info['name']}")
                st.write(f"Spotify Popularity: {artist_info['popularity']}")
                st.write(f"Spotify Followers: {artist_info['followers']}")
                st.write(f"Lastfm Listeners: {artist_info['lastfm_listeners']}")
                st.write(f"Lastfm Play Count: {artist_info['lastfm_playcount']}")
                if artist_info['image']:
                    st.image(artist_info['image'], width=200)

                top_tracks = get_top_tracks(artist_info['id'], spotify_token)
                if top_tracks:
                    st.subheader("Top 5 Tracks:")
                    for track in top_tracks:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"{track['name']} (Popularity: {track['popularity']})")
                            st.write(f"[Listen on Spotify]({track['external_urls']['spotify']})")
                            if 'album' in track and track['album']['images']:
                                st.image(track['album']['images'][0]['url'], width=200)
                        with col2:
                            track_features = get_audio_features(track['id'], spotify_token)
                            if track_features:
                                fig = plot_radar_chart(track_features)
                                st.pyplot(fig)
                
                
                #wikipedia
                # URLエンコードされたアーティスト名
                # encoded_name = urllib.parse.quote(artist_info['name'])

                # Wikipediaの検索URLを構築
                # url = f"https://ja.wikipedia.org/wiki/{encoded_name}"
                # アーティストのマッピングを読み込む
                artist_mappings = load_artist_mappings('artist.json')

                # ユーザーからの入力
                artist_input = artist_info['name']

                url = generate_wikipedia_url(artist_input, artist_mappings)

                start_heading = '概要'
                end_heading = '来歴'
                section_text = fetch_wikipedia_summary(url, start_heading, end_heading)
                st.subheader(f"ちょこっと'{artist_info['name']}'情報")
                st.write(section_text)

                if openai_api_key:
                    openai_info = openai_query(artist_info['name'], openai_api_key)
                    st.subheader("Additional Artist Info from OpenAI")
                    st.write(openai_info)

if __name__ == "__main__":
    main()
