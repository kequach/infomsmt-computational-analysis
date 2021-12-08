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
    desired_features = ['tempo', 'time_signature', 'key', 'mode', 'loudness', 'energy', 'danceability', 'instrumentalness',
                'liveness', 'speechiness', 'valence']

    username, spotify = authenticate_user()

    # Get tracks by playlist owner and id
    # Sad Songs by Spotify, 1,3 million likes -> 37i9dQZF1DX7qK8ma5wgG1
    # SMT Special Songs by Jakub, 15 likes -> 5XnTgCWRtlcKweUSvEWJAE
    tracks = get_tracks_by_owner_and_id(spotify, 'Spotify', '37i9dQZF1DX7qK8ma5wgG1')

    if tracks:
        # Get high level audio feature information
        track_features_map = get_audio_features(spotify, tracks, pretty_print=False)

        # Create plots
        create_plots(track_features_map, desired_features)

        # Calculate statistics
        calculate_statistics(track_features_map, desired_features)


################################################################################
# Functions
################################################################################
def get_tracks_by_owner_and_id(spotify, playlist_owner, playlist_id):
    """
    Get tracks by playlist owner and id
    """
    print_header('Get tracks by playlist owner and id\nplaylist_owner: {0}\nplaylist_id: {1}'.format(playlist_owner, playlist_id))

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
    print_header('Get Audio Features')
    tracks_features_response = spotify.audio_features(tracks=track_map.keys())
    track_features_map = {f.get('id'): f for f in tracks_features_response}

    # Iterate through the features and print the track and info
    if pretty_print:
        for track_id, track_features in track_features_map.items():
            # Print out the track info and audio features
            track = track_map.get(track_id)
            print_audio_features_for_track(track, track_features)

    return track_features_map


def create_plots(track_features_map, desired_features):
    """
    Create plots
    """
    print_header('Create plots')

    # Convert nested dictionary to data frame
    track_features_df = pd.DataFrame.from_dict(track_features_map, orient='index')

    for desired_feature in desired_features:
        plt.figure()
        plt.style.use('seaborn-whitegrid')  # nice and clean grid
        plt.hist(track_features_df[desired_feature], bins=30, facecolor='#2ab0ff', edgecolor='#169acf')
        plt.axvline(track_features_df[desired_feature].mean(), color='k', linestyle='dashed')
        plt.title('Histogram - {0}'.format(desired_feature.capitalize()))
        plt.xlabel(desired_feature.capitalize())
        plt.ylabel('Frequency')
        plt.savefig('../plots/{0}.png'.format(desired_feature))
        plt.close()


def calculate_statistics(track_features_map, desired_features):
    """
    Calculate statistics
    """
    print_header('Calculate statistics')

    # Convert nested dictionary to data frame
    track_features_df = pd.DataFrame.from_dict(track_features_map, orient='index')
    for desired_feature in desired_features:
        print('{}: M = {:.2f}, SD = {:.2f}, SE = {:.2f}'.format(
            desired_feature.capitalize(),
            track_features_df[desired_feature].mean(),
            track_features_df[desired_feature].std(),
            sem(track_features_df[desired_feature])
        )
        )


if __name__ == '__main__':
    main()
