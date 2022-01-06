# -*- coding: utf-8 -*-
import sys
import os
import spotipy
import spotipy.util as sp_util
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOauthError
from spotipy.client import SpotifyException
from dotenv import load_dotenv

# Define the scopes that we need access to
# https://developer.spotify.com/web-api/using-scopes/
scope = 'user-library-read playlist-read-private'

################################################################################
# Authentication Functions
################################################################################
def authenticate_client():
    """
    Using credentials from the environment variables, attempt to authenticate with the spotify web API.  If successful,
    create a spotipy instance and return it.
    :return: An authenticated Spotipy instance
    """
    try:
        load_dotenv()
        
        client_id = os.environ.get("SPOTIPY_CLIENT_ID")
        client_secret = os.environ.get("SPOTIPY_CLIENT_SECRET")
        # Get an auth token for this user
        client_credentials = SpotifyClientCredentials(client_id=client_id,
                                                           client_secret=client_secret)

        spotify = spotipy.Spotify(client_credentials_manager=client_credentials)
        return spotify
    except SpotifyOauthError as e:
        print('API credentials not set.  Please see README for instructions on setting credentials.')
        sys.exit(1)


################################################################################
# Fetcher Functions
################################################################################
def fetch_artists(spotify, artists):
    """
    Get a large number of artists by chunking the requests
    """
    batch_size = 50
    batches = range(0, len(artists), batch_size)
    result = []
    for i in batches:
        end = i+batch_size
        # print('Fetching artists {} - {}'.format(i, end))
        chunk = spotify.artists(artists[i:end])
        result = result + chunk.get('artists', [])

    return result

def fetch_artist_top_tracks(spotify, artists):
    """
    Get a large number of artists by chunking the requests
    """
    batch_size = 50
    batches = range(0, len(artists), batch_size)
    result = []
    for i in batches:
        end = i+batch_size
        print('Fetching artists {} - {}'.format(i, end))
        chunk = spotify.artists(artists[i:end])
        result = result + chunk.get('artists', [])

    return result