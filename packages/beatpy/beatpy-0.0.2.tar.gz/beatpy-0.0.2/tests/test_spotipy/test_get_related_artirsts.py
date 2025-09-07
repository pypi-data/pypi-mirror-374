import requests
import pytest
import os

from spotipy.oauth2 import SpotifyClientCredentials


BASE_URL = "https://api.spotify.com/v1"

auth_manager = SpotifyClientCredentials(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
)

# acá obtenés el token válido
token = auth_manager.get_access_token(as_dict=False)


@pytest.fixture
def artist_id_swans() -> str:
    return "79S80ZWgVhIPMCHuvl6SkA"


@pytest.fixture
def artist_id_milo_j() -> str:
    return "19HM5j0ULGSmEoRcrSe5x3"


def test_get_related_artists(artist_id_swans: str):
    url = f"{BASE_URL}/artists/{artist_id_milo_j}/related-artists"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)

    print(response.json())
    assert response.status_code == 200


