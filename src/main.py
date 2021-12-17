import sys
import os
import json
import argparse
import spotipy
import spotipy.util as sp_util

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import ttest_ind

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
    desired_features = ['tempo', 'time_signature', 'key', 'mode', 'loudness', 'energy', 'danceability', 'instrumentalness',
                'liveness', 'speechiness', 'valence']

    spotify = authenticate_client()

    df = parse_input_file()
    happy_ids = get_playlist_ids(df, "happy")
    neutral_ids = get_playlist_ids(df, "neutral")

    # Get tracks by playlist owner and id
    # Beast Mode by Spotify, 8,5 million likes -> 37i9dQZF1DX76Wlfdnj7AP
    # Mode Booster by Spotify, 5,9 million likes -> 37i9dQZF1DX3rxVfibe1L0
    # Happy Hits by Spotify, 5,7 million likes -> 37i9dQZF1DXdPec7aLTmlC
    # Sad Songs by Spotify, 1,3 million likes -> 37i9dQZF1DX7qK8ma5wgG1
    # SMT Special Songs by Jakub, 15 likes -> 5XnTgCWRtlcKweUSvEWJAE
    # tracks = get_tracks_by_owner_and_id(spotify, None, '37i9dQZF1DX76Wlfdnj7AP')

    tracks_happy = get_tracks_from_list_of_playlists(spotify, happy_ids)
    tracks_neutral = get_tracks_from_list_of_playlists(spotify, neutral_ids)

    # Get high level audio feature information
    track_happy_features_map = get_audio_features_large(spotify, tracks_happy)
    track_neutral_features_map = get_audio_features_large(spotify, tracks_neutral)
    # track_features_map = get_audio_features(spotify, tracks_happy, pretty_print=False)

    # Create plots
    create_plots(track_happy_features_map, desired_features)

    # Calculate statistics
    calculate_statistics(track_happy_features_map, desired_features)
    calculate_statistics(track_neutral_features_map, desired_features)


    happy_df = pd.DataFrame.from_dict(track_happy_features_map, orient='index')
    neutral_df = pd.DataFrame.from_dict(track_neutral_features_map, orient='index')
    t_test(happy_df, neutral_df, "valence")


################################################################################
# Functions
################################################################################
def parse_input_file():
    # Initiate the parser
    parser = argparse.ArgumentParser()

    # Add arguments to be parsed
    parser.add_argument("--input",
                        "-i",
                        help="The path to the file with playlists",
                        default="../playlists.csv")
    # Read arguments from the command line
    args = parser.parse_args()
    df = read_input_file(args.input)
    return df

def get_playlist_ids(df, category):
    df_filtered = df.loc[df['category'] == category] 
    ids = set([url.split("/")[-1] for url in df_filtered["link"]])
    return ids

def get_tracks_from_list_of_playlists(spotify, playlist_ids):
    tracks = []
    for id in playlist_ids:
        tracks.extend(get_tracks_by_owner_and_id(spotify, None, id))

    # filter out duplicates
    set_of_jsons = {json.dumps(d, sort_keys=True) for d in tracks}
    tracks = [json.loads(t) for t in set_of_jsons]
    print(f"Total number of tracks retrieved: {len(tracks)}")
    return tracks

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

def get_audio_features_large(spotify, tracks, chunk_size = 100):
    track_features_map = {}
    for i in range(0, len(tracks), chunk_size):
        chunk = tracks[i:i+chunk_size]
        # process chunk of size <= chunk_size
        track_features_map.update(get_audio_features(spotify, chunk, pretty_print=False))
    return track_features_map

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

def t_test(df_one, df_two, col_name):
    print_header('Calculate t-test')
    t, p = ttest_ind(df_one[col_name], df_two[col_name], equal_var=False)
    print(f"ttest for {col_name}: t = {t}  p = {p}")
    return(t,p)

def read_input_file(file_path):
    """reads in the input file through Pandas

    Args:
        file_path (string): path to the file

    Returns:
        DataFrame
    """
    if "xlsx" in file_path:
        file = pd.read_excel(file_path, engine='openpyxl')
    else:
        file = pd.read_csv(file_path)
    return file


if __name__ == '__main__':
    main()
