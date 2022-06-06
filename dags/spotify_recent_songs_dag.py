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
    """DAG for fetching data about recently played songs from Spotify API"""
    @task()
    def get_recent_songs():
        """Get recently played songs from spotify API"""
        from helpers.spotify_helpers import get_request

        response = get_request('https://api.spotify.com/v1/me/player/recently-played', {})

        return response

    @task()
    def get_artists_data(data: dict):
        """Get artist data"""
        from helpers.spotify_helpers import get_request
        from glom import glom
        spec = ('items', [('track.artists', ['id'])])

        artists_list = glom(data, spec)
        artists_list = [artist for artists in artists_list for artist in artists]
        id_string = ','.join([artist for artist in artists_list])

        response = get_request(
            'https://api.spotify.com/v1/artists', 
            {
                    'ids': id_string,
            }
        )

        return response

    @task()
    def extract_artists(data: dict):
        from glom import glom
        spec = ('artists', [{
            'id': 'id',
            'name': 'name',
            'genres': 'genres',
            'popularity': 'popularity',
        }])

        artists = glom(data, spec)
        return artists

    @task()
    def extract_genres(artists: list):
        from glom import glom
        spec = [{'name': 'genres'}]
        genres = glom(artists, spec)
        return genres

    @task()
    def extract_albums(data: dict):
        """Extract album data from API response"""
        from glom import glom

        spec = ('items', [{
            'id': ('track.album', 'id'),
            'name': ('track.album', 'name'),
            'artists': ('track.artists', ['id']),
            'release_date': ('track.album', 'release_date'),
            'total_tracks': ('track.album', 'total_tracks'),
        }])

        albums = glom(data, spec)
        return albums
    
    @task()
    def extract_songs(data: dict):
        """Extract song data from API response"""
        from glom import glom

        spec = ('items', [{
            'id': ('track', 'id'),
            'name': ('track', 'name'),
            'artists': ('track.artists', ['id']),
            'duration': ('track', 'duration_ms'),
            'popularity': ('track', 'popularity'),
        }])

        songs = glom(data, spec)
        return songs

    @task()
    def save_songs(songs: list):
        """Save song data into Mongo"""
        from helpers.mongo_helpers import save_data
        save_data(songs, 'recent_songs')
    
    @task()
    def save_albums(albums: list):
        """Save album data into Mongo"""
        from helpers.mongo_helpers import save_data
        save_data(albums, 'recent_albums')
    
    @task()
    def save_artists(artists: list):
        """Save artist data into Mongo"""
        from helpers.mongo_helpers import save_data
        save_data(artists, 'recent_artists')

    @task()
    def save_genres(genres: list):
        """Save genre data into Mongo"""
        from helpers.mongo_helpers import save_data
        save_data(genres, 'recent_genres')

    data = get_recent_songs()

    songs = extract_songs(data)
    save_songs(songs)

    albums = extract_albums(data)
    save_albums(albums)

    artists = get_artists_data(data)
    artists = extract_artists(artists)

    genres = extract_genres(artists)

spotify_recent_songs_dag = spotify_recent_songs()