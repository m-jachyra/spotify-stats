from datetime import datetime, timedelta
from airflow.decorators import dag, task

from airflow.providers.http.operators.http import SimpleHttpOperator

def refresh_token():
    import base64
    from airflow.models import Variable
    import requests
    uri = 'https://accounts.spotify.com/api/token'
    refresh_token = Variable.get('REFRESH_TOKEN')
    client_id = Variable.get('CLIENT_ID')
    client_secret = Variable.get('CLIENT_SECRET')
    encoded_string = base64.urlsafe_b64encode((client_id + ':' + client_secret).encode())
    response = requests.post(
        uri, 
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        },
        headers={
            "Authorization": "Basic " + encoded_string.decode()
        }
    )
    return response.json()['access_token']

@dag(
    default_args={'retries': 1},
    tags=['testy'],
    start_date=datetime(2022, 6, 1),
    catchup=False,
    schedule_interval='@daily',
)
def spotify_recent_songs():
    data = SimpleHttpOperator(
        task_id='get_op',
        http_conn_id='',
        method='GET',
        endpoint='https://api.spotify.com/v1/me/player/recently-played',
        headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {refresh_token()}'
        },
    )
    
    @task
    def parse_results(api_results):
        import json
        data = json.loads(api_results)
        return data

    parse_results(data.output)

spotify_recent_songs_dag = spotify_recent_songs()