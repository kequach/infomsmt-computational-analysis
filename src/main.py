import sys
import os
import json
import spotipy
import spotipy.util as sp_util

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scipy.stats import sem

from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOauthError
from spotipy.client import SpotifyException

from display_utils import (
    print_header,
    track_string,
    print_audio_features_for_track,
    print_audio_analysis_for_track,
    choose_tracks
)

from common import (
    authenticate_client,
    authenticate_user,
    fetch_artists,
    fetch_artist_top_tracks
)

# Define the scopes that we need access to
# https://developer.spotify.com/web-api/using-scopes/
scope = 'user-library-read playlist-read-private'


################################################################################
# Main Function
################################################################################

def main():
    """
    Our main function that will get run when the program executes
    """
    print_header('Spotify Web API - Computational Analysis')
    spotify = None
    tracks = []

    username, spotify = authenticate_user()
    # tracks = list_playlists(spotify, username)

    # Get tracks by owner and id instead of listing user's playlists
    tracks = get_tracks_by_owner_and_id(spotify, 'Spotify', '37i9dQZF1DX7qK8ma5wgG1')

    if tracks:
        track_features_map = get_audio_features(spotify, tracks, pretty_print=False)

        # Convert nested dictionary to data frame
        track_features_df = pd.DataFrame.from_dict(track_features_map, orient='index')

        # Generate histogram per feature
        features = ['tempo', 'time_signature', 'key', 'mode', 'loudness', 'energy', 'danceability', 'instrumentalness',
                    'liveness', 'speechiness', 'valence']

        for feature in features:
            plt.figure()
            plt.style.use('seaborn-whitegrid')  # nice and clean grid
            plt.hist(track_features_df[feature], bins=30, facecolor='#2ab0ff', edgecolor='#169acf')
            plt.axvline(track_features_df[feature].mean(), color='k', linestyle='dashed')
            plt.title('Histogram - {0}'.format(feature.capitalize()))
            plt.xlabel(feature.capitalize())
            plt.ylabel('Frequency')
            plt.savefig('../plots/{0}.png'.format(feature))
            plt.close()

            print('{}: M = {:.2f}, SD = {:.2f}, SE = {:.2f}'.format(
                feature.capitalize(),
                track_features_df[feature].mean(),
                track_features_df[feature].std(),
                sem(track_features_df[feature])
            )
            )


################################################################################
# Functions
################################################################################

def list_playlists(spotify, username):
    """
    Get all of a user's playlists and have them select tracks from a playlist
    """
    # Get all the playlists for this user
    playlists = []
    total = 1
    # The API paginates the results, so we need to iterate
    while len(playlists) < total:
        playlists_response = spotify.user_playlists(username, offset=len(playlists))
        playlists.extend(playlists_response.get('items', []))
        total = playlists_response.get('total')

    # Remove any playlists that we don't own
    playlists = [playlist for playlist in playlists if playlist.get('owner', {}).get('id') == username]

    # List out all of the playlists
    print_header('Your Playlists')
    for i, playlist in enumerate(playlists):
        print('  {}) {} - {}'.format(i + 1, playlist.get('name'), playlist.get('uri')))

    # Choose a playlist
    playlist_choice = int(input('\nChoose a playlist: '))
    playlist = playlists[playlist_choice - 1]
    playlist_owner = playlist.get('owner', {}).get('id')

    # Get the playlist tracks
    tracks = []
    total = 1
    # The API paginates the results, so we need to keep fetching until we have all of the items
    while len(tracks) < total:
        tracks_response = spotify.user_playlist_tracks(playlist_owner, playlist.get('id'), offset=len(tracks))
        tracks.extend(tracks_response.get('items', []))
        total = tracks_response.get('total')

    # Pull out the actual track objects since they're nested weird
    tracks = [track.get('track') for track in tracks]

    return tracks


def get_tracks_by_owner_and_id(spotify, playlist_owner, playlist_id):
    """
    Get tracks by playlist owner and id
    """
    print_header('Playlist Owner: {0}\nPlaylist ID: {1}'.format(playlist_owner, playlist_id))

    # Get the playlist tracks
    tracks = []
    total = 1

    # The API paginates the results, so we need to keep fetching until we have all of the items
    while len(tracks) < total:
        tracks_response = spotify.user_playlist_tracks(playlist_owner, playlist_id, offset=len(tracks))
        tracks.extend(tracks_response.get('items', []))
        total = tracks_response.get('total')

    # Pull out the actual track objects since they're nested weird
    tracks = [track.get('track') for track in tracks]

    return tracks


def get_audio_features(spotify, tracks, pretty_print=False):
    """
    Given a list of tracks, get and print the audio features for those tracks!
    :param spotify: An authenticated Spotipy instance
    :param tracks: A list of track dictionaries
    """
    if not tracks:
        print('No tracks provided.')
        return

    # Build a map of id->track so we can get the full track info later
    track_map = {track.get('id'): track for track in tracks}

    # Request the audio features for the chosen tracks (limited to 50)
    print_header('Getting Audio Features')
    tracks_features_response = spotify.audio_features(tracks=track_map.keys())
    track_features_map = {f.get('id'): f for f in tracks_features_response}

    # Iterate through the features and print the track and info
    if pretty_print:
        for track_id, track_features in track_features_map.items():
            # Print out the track info and audio features
            track = track_map.get(track_id)
            print_audio_features_for_track(track, track_features)

    return track_features_map


if __name__ == '__main__':
    main()
