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