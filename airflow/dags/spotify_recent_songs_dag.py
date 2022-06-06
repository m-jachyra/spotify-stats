import pendulum
import json
from airflow.decorators import dag, task

@dag(
    schedule_interval=None,
    start_date=pendulum.datetime(2022, 6, 1, tz='UTC'),
    catchup=False,
    tags=['testy'],
)
def spotify_recent_songs():
    @task()
    def get_recent_songs():
        import requests
        from helpers.spotify_helpers import refresh_token

        response = requests.get(
            'https://api.spotify.com/v1/me/player/recently-played',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {refresh_token()}',
            },
        )

        return response.json()

    @task()
    def extract_albums(data: dict):
        from glom import glom

        spec = ('items', [{
            'id': ('track.album', 'id'),
            'name': ('track.album', 'name'),
            'artists': ('track.album.artists', ['name']),
            'release_date': ('track.album', 'release_date'),
            'total_tracks': ('track.album', 'total_tracks'),
        }])

        albums = glom(data, spec)
        return albums
    
    @task()
    def extract_songs(data: dict):
        from glom import glom

        spec = ('items', [{
            'id': ('track', 'id'),
            'name': ('track', 'name'),
            'artists': ('track.artists', ['name']),
            'duration': ('track', 'duration_ms'),
            'popularity': ('track', 'popularity'),
        }])

        songs = glom(data, spec)
        return songs

    @task()
    def save_songs(songs: dict):
        from helpers.mongo_helpers import get_database
        from pymongo import MongoClient
        import pymongo

        spotify_db = get_database()
        recent_songs = spotify_db['recent_songs']
        recent_songs.insert_many(songs)
    
    @task()
    def save_albums(albums: dict):
        from helpers.mongo_helpers import get_database
        from pymongo import MongoClient
        import pymongo

        spotify_db = get_database()
        recent_albums = spotify_db['recent_albums']
        recent_albums.insert_many(albums)

    data = get_recent_songs()

    songs = extract_songs(data)
    save_songs(songs)

    albums = extract_albums(data)
    save_albums(albums)

spotify_recent_songs_dag = spotify_recent_songs()