import json
import argparse

import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import (
    sem,
    ttest_ind
)

from display_utils import (
    print_header,
    print_audio_features_for_track
)

from common import (
    authenticate_client
)

# Define the scopes that we need access to
# https://developer.spotify.com/web-api/using-scopes/
scope = 'user-library-read playlist-read-private'


################################################################################
# Main Function
################################################################################

def main():
    print_header('Spotify Web API - Computational Analysis')

    desired_features = ['tempo', 'loudness', 'energy', 'danceability', 'speechiness', 'valence']

    spotify = authenticate_client()

    df = parse_input_file()
    playlist_ids_happy = get_playlist_ids(df, 'happy')
    playlist_ids_running = get_playlist_ids(df, 'running')
    playlist_ids_studying = get_playlist_ids(df, 'studying')

    # Get tracks from a list of playlists
    tracks_happy = get_tracks_from_list_of_playlists(spotify, playlist_ids_happy)
    tracks_running = get_tracks_from_list_of_playlists(spotify, playlist_ids_running)
    tracks_studying = get_tracks_from_list_of_playlists(spotify, playlist_ids_studying)

    # Get high level audio feature information
    track_features_map_happy = get_audio_features_in_chunks(spotify, tracks_happy)
    track_features_map_running = get_audio_features_in_chunks(spotify, tracks_running)
    track_features_map_studying = get_audio_features_in_chunks(spotify, tracks_studying)

    for desired_feature in desired_features:
        # Calculate descriptive statistics
        calculate_descriptive_statistics(track_features_map_happy, desired_feature)
        calculate_descriptive_statistics(track_features_map_running, desired_feature)
        calculate_descriptive_statistics(track_features_map_studying, desired_feature)

        # Perform t-test
        t_test(track_features_map_happy, track_features_map_running, desired_feature)
        t_test(track_features_map_happy, track_features_map_studying, desired_feature)

        # Create plots per desired feature
        create_histogram(track_features_map_happy, track_features_map_running, track_features_map_studying,
                         desired_feature)


################################################################################
# Functions
################################################################################
def get_playlist_ids(df, category):
    df_filtered = df.loc[df['category'] == category]
    ids = set([url.split('/')[-1] for url in df_filtered['link']])
    return ids


def get_tracks_from_list_of_playlists(spotify, playlist_ids):
    tracks = []
    for playlist_id in playlist_ids:
        tracks.extend(get_tracks_by_playlist_id(spotify, None, playlist_id))

    # filter out duplicates
    set_of_jsons = {json.dumps(d, sort_keys=True) for d in tracks}
    tracks = [json.loads(t) for t in set_of_jsons]
    print(f'Total number of tracks retrieved: {len(tracks)}')
    return tracks


def get_tracks_by_playlist_id(spotify, playlist_owner, playlist_id):
    # Get tracks of playlist by id
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


def get_audio_features_in_chunks(spotify, tracks, chunk_size=100):
    track_features_map = {}
    for i in range(0, len(tracks), chunk_size):
        chunk = tracks[i:i + chunk_size]
        # process chunk of size <= chunk_size
        track_features_map.update(get_audio_features(spotify, chunk, pretty_print=False))
    return track_features_map


def get_audio_features(spotify, tracks, pretty_print=False):
    if not tracks:
        print('No tracks provided.')
        return

    # Build a map of id->track so we can get the full track info later
    track_map = {track.get('id'): track for track in tracks}

    # Request the audio features for the chosen tracks (limited to 50)
    tracks_features_response = spotify.audio_features(tracks=track_map.keys())
    track_features_map = {f.get('id'): f for f in tracks_features_response}

    # Iterate through the features and print the track and info
    if pretty_print:
        for track_id, track_features in track_features_map.items():
            # Print out the track info and audio features
            track = track_map.get(track_id)
            print_audio_features_for_track(track, track_features)

    return track_features_map


def create_histogram(track_features_map_happy, track_features_map_running, track_features_map_studying,
                     desired_feature):
    print_header(f'Create histogram: {desired_feature.capitalize()}')

    # Convert nested dictionary to data frame
    track_features_df_happy = pd.DataFrame.from_dict(track_features_map_happy, orient='index')
    track_features_df_running = pd.DataFrame.from_dict(track_features_map_running, orient='index')
    track_features_df_studying = pd.DataFrame.from_dict(track_features_map_studying, orient='index')

    plt.figure()
    plt.style.use('seaborn-whitegrid')  # nice and clean grid

    # Plot histograms per category
    plt.hist(track_features_df_happy[desired_feature], bins=30, alpha=0.5, label="Happiness", facecolor='#1DB954',
             edgecolor='#191414')
    plt.hist(track_features_df_running[desired_feature], bins=30, alpha=0.5, label="Running", facecolor='#FC7E00',
             edgecolor='#191414')
    plt.hist(track_features_df_studying[desired_feature], bins=30, alpha=0.5, label="Studying", facecolor='#009FFF',
             edgecolor='#191414')

    # Plot dashed line for average
    plt.axvline(track_features_df_happy[desired_feature].mean(), color='#1DB954', linestyle='dashed')
    plt.axvline(track_features_df_running[desired_feature].mean(), color='#FC7E00', linestyle='dashed')
    plt.axvline(track_features_df_studying[desired_feature].mean(), color='#009FFF', linestyle='dashed')

    # Plot descriptions
    plt.title(f'Histogram - {desired_feature.capitalize()}')
    plt.xlabel(desired_feature.capitalize())
    plt.ylabel('Frequency')
    plt.legend(loc='best')

    # Save figure
    plt.savefig(f'../plots/{desired_feature}.png', bbox_inches='tight')
    plt.close()


def calculate_descriptive_statistics(track_features_map, desired_feature):
    print_header(f'Descriptive statistics: {desired_feature.capitalize()}')

    # Convert nested dictionary to data frame
    track_features_df = pd.DataFrame.from_dict(track_features_map, orient='index')
    print(f'M = {track_features_df[desired_feature].mean():.2f}, '
          f'SD = {track_features_df[desired_feature].std():.2f}, '
          f'SE = {sem(track_features_df[desired_feature]):.2f}')


def t_test(track_features_map_one, track_features_map_two, desired_feature):
    print_header(f't-test: {desired_feature.capitalize()}')

    track_features_df_one = pd.DataFrame.from_dict(track_features_map_one, orient='index')
    track_features_df_two = pd.DataFrame.from_dict(track_features_map_two, orient='index')

    t, p = ttest_ind(track_features_df_one[desired_feature], track_features_df_two[desired_feature], equal_var=False)
    print(f't = {t:.2f}  p = {p:.3f}')
    return t, p


def read_input_file(file_path):
    if 'xlsx' in file_path:
        file = pd.read_excel(file_path, engine='openpyxl')
    else:
        file = pd.read_csv(file_path)
    return file


def parse_input_file():
    # Initiate the parser
    parser = argparse.ArgumentParser()

    # Add arguments to be parsed
    parser.add_argument('--input',
                        '-i',
                        help='The path to the file with playlists',
                        default='../playlists.csv')
    # Read arguments from the command line
    args = parser.parse_args()
    df = read_input_file(args.input)
    return df


if __name__ == '__main__':
    main()
