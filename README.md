# Spotify Stats
Data pipeline do przetwarzania danych pobranych z API Spotify.

## Uruchamianie
```
git clone git@github.com:m-jachyra/spotify-stats.git
cd spotify-stats
```
Tworzymy zmienne potrzebne do poprawnego działania aplikacji. Zmienna `AIRFLOW_UID` wykorzystywana jest przez Airflow. Pozostałe
potrzebne są do poprawnego łaczenia się z API Spotify.
```
echo -e "AIRFLOW_UID=$(id -u)" > .env
echo "CLIENT_ID=YOUR_CLIENT_ID" > .env
echo -e "CLIENT_SECRET=YOUR_CLIENT_SECRET" > .env
echo -e "REFRESH_TOKEN=YOUR_REFRESH_TOKEN" > .env
```
Aby wykonać migrację bazy danych i utworzyć pierwszego użytkownika korzystamy z polecenia:
```
docker-compose up airflow-init
```
Teraz możemy uruchomić kontener:
```
docker-compose up
```
### Serwisy WWWW

- [pgAdmin](http://localhost:5050)
- [Airflow](http://localhost:8080)
- [Mongo Express](http://localhost:5000)
