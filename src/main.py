import streamlit as st
from api.spotify import get_access_token, search_artists_by_genre, get_artists_details, get_top_tracks, get_audio_features
from api.lastfm import get_lastfm_artist_info
from api.wikipedia import generate_wikipedia
from utils.config import load_env_vars
from utils.charts import plot_radar_chart
import pandas as pd
import os

load_env_vars()
# spotify
spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
spotify_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
# lastfm
lastfm_api_key = os.getenv('LASTFM_API_KEY')

def main():
    image_path = "./makibao.png"
    st.image(image_path, caption='', width=200)
    st.title("DERBY's Artist Popularity and Streaming Data Tracker.v4")

    num_artists = st.slider("Number of Top Artists to Display", 5, 30, 10, 1)

    genre = 'k-pop'

    if spotify_client_id and spotify_client_secret:
        spotify_token = get_access_token(spotify_client_id, spotify_client_secret)
        if spotify_token:
            artists_data = search_artists_by_genre(genre, spotify_token)
            detailed_artists = get_artists_details(artists_data[:num_artists], spotify_token)
            #lastfm
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
                section_text = generate_wikipedia(artist_info['name'])
                st.subheader(f"ちょこっと'{artist_info['name']}'情報")
                st.write(section_text)

if __name__ == "__main__":
    main()
