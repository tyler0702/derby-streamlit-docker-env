import requests

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

