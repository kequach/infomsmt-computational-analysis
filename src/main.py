import json
import argparse
from collections import Counter

import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import (
    sem,
    ttest_ind
)
from statsmodels.sandbox.stats.multicomp import multipletests

from display_utils import (
    print_header,
    print_audio_features_for_track
)

from common import (
    authenticate_client,
    fetch_artists
)

# Define the scopes that we need access to
# https://developer.spotify.com/web-api/using-scopes/
scope = 'user-library-read playlist-read-private'

# Uncomment line below to remove scientific notation and round after 7 decimals
# pd.options.display.float_format = '{:.7f}'.format

################################################################################
# Main Function
################################################################################

def main():
    print_header('Spotify Web API - Computational Analysis')

    desired_features = ['tempo', 'loudness', 'energy', 'danceability', 'speechiness', 'valence']

    spotify = authenticate_client()
    df = parse_input_file()
    playlist_ids_mood_boosting = get_playlist_ids(df, 'mood boosting')
    playlist_ids_running = get_playlist_ids(df, 'running')
    playlist_ids_studying = get_playlist_ids(df, 'studying')

    # Get tracks from a list of playlists
    tracks_mood_boosting = get_tracks_from_list_of_playlists(spotify, playlist_ids_mood_boosting)
    tracks_running = get_tracks_from_list_of_playlists(spotify, playlist_ids_running)
    tracks_studying = get_tracks_from_list_of_playlists(spotify, playlist_ids_studying)

    # Get high level audio feature information
    track_features_map_mood_boosting = get_audio_features_in_chunks(spotify, tracks_mood_boosting)
    track_features_map_running = get_audio_features_in_chunks(spotify, tracks_running)
    track_features_map_studying = get_audio_features_in_chunks(spotify, tracks_studying)

    descriptive_statistics_list = []
    t_test_list = []
    for desired_feature in desired_features:
        # Calculate descriptive statistics
        descriptive_statistics_list.append(calculate_descriptive_statistics(track_features_map_mood_boosting, desired_feature, "mood boosting"))
        descriptive_statistics_list.append(calculate_descriptive_statistics(track_features_map_running, desired_feature, "running"))
        descriptive_statistics_list.append(calculate_descriptive_statistics(track_features_map_studying, desired_feature, "studying"))

        # Perform t-test
        t_test_list.append(t_test(track_features_map_mood_boosting, track_features_map_running, desired_feature, "running"))
        t_test_list.append(t_test(track_features_map_mood_boosting, track_features_map_studying, desired_feature, "studying"))

        # Create plots per desired feature
        create_histogram(track_features_map_mood_boosting, track_features_map_running, track_features_map_studying,
                         desired_feature)

    # Bonferroni correction of t-tests
    p_values = [entry[0] for entry in t_test_list]
    # Create a list of the adjusted p-values
    p_adjusted = multipletests(p_values, alpha=.05, method='bonferroni')
    p_values_adjusted = [round(value, 7) for value in p_adjusted[1]]
    print("P-values uncorrected")
    print(p_values)
    print("P-values with bonferroni-correction")
    print(p_values_adjusted)
    t_test_list_adjusted = []

    # create new list with added adjusted values
    for (p_value, t_value, feature, group), p_value_adjusted in zip(t_test_list, p_values_adjusted):
        t_test_list_adjusted.append([p_value_adjusted, p_value, t_value, feature, group])

    # Export statistics and t-test to .tex tables
    descriptive_statistics_df = pd.DataFrame(descriptive_statistics_list, columns=["group", "feature", "mean", "standard deviation", "standard error"])
    descriptive_statistics_df.to_latex(("../tables/descriptive_statistics.tex"),index=False)

    t_test_adjusted_df = pd.DataFrame(t_test_list_adjusted, columns=["p-value corrected", "p-value uncorrected", "t-value", "feature", "group"])
    t_test_adjusted_df.to_latex(("../tables/t_tests.tex"),index=False)

    # get genres from artists 
    genres = get_top5_genres(spotify, tracks_mood_boosting)

    recommendations = get_recommendations(spotify, descriptive_statistics_df, genres)
    pd.DataFrame(recommendations, columns = ["Artists", "Name", "Preview-URL", "Spotify-URL"]).to_csv("recommendations.csv", index=False)

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


def create_histogram(track_features_map_mood_boosting, track_features_map_running, track_features_map_studying,
                     desired_feature):
    # Convert nested dictionary to data frame
    track_features_df_mood_boosting = pd.DataFrame.from_dict(track_features_map_mood_boosting, orient='index')
    track_features_df_running = pd.DataFrame.from_dict(track_features_map_running, orient='index')
    track_features_df_studying = pd.DataFrame.from_dict(track_features_map_studying, orient='index')

    # Create figure with nice clean grid
    plt.figure()
    plt.style.use('seaborn-whitegrid')

    # Plot histograms per category
    plt.hist(track_features_df_mood_boosting[desired_feature], bins=30, alpha=0.5, label="Mood boosting", facecolor='#1DB954',
             edgecolor='#191414')
    plt.hist(track_features_df_running[desired_feature], bins=30, alpha=0.5, label="Running", facecolor='#FC7E00',
             edgecolor='#191414')
    plt.hist(track_features_df_studying[desired_feature], bins=30, alpha=0.5, label="Studying", facecolor='#009FFF',
             edgecolor='#191414')

    # Plot dashed line for average
    plt.axvline(track_features_df_mood_boosting[desired_feature].mean(), color='#1DB954', linestyle='dashed')
    plt.axvline(track_features_df_running[desired_feature].mean(), color='#FC7E00', linestyle='dashed')
    plt.axvline(track_features_df_studying[desired_feature].mean(), color='#009FFF', linestyle='dashed')

    # Plot descriptions
    plt.title(f'Histogram - {desired_feature.capitalize()}')
    plt.xlabel(desired_feature.capitalize()
               .replace('Tempo', 'Tempo (BPM)')
               .replace('Loudness', 'Loudness (dB)'))
    plt.ylabel('Frequency')

    # Add legend at best fit
    plt.legend()

    # Save figure
    plt.savefig(f'../plots/histogram_{desired_feature}.png', bbox_inches='tight')
    plt.close()


def calculate_descriptive_statistics(track_features_map, desired_feature, group):
    print_header(f'Descriptive statistics for {group}: {desired_feature.capitalize()}')

    # Convert nested dictionary to data frame
    track_features_df = pd.DataFrame.from_dict(track_features_map, orient='index')

    # Calculate mean, standard deviation, and standard error
    mean = round(track_features_df[desired_feature].mean(), 3)
    standard_deviation = round(track_features_df[desired_feature].std(), 3)
    standard_error = round(sem(track_features_df[desired_feature]), 3)

    # Print and return mean, standard deviation, and standard error
    print(f'M = {mean}, SD = {standard_deviation}, SE = {standard_error}')
    return group, desired_feature, mean, standard_deviation, standard_error


def t_test(track_features_map_one, track_features_map_two, desired_feature, group):
    print_header(f't-test: {desired_feature.capitalize()}, comparison to {group}')

    track_features_df_one = pd.DataFrame.from_dict(track_features_map_one, orient='index')
    track_features_df_two = pd.DataFrame.from_dict(track_features_map_two, orient='index')

    t, p = ttest_ind(track_features_df_one[desired_feature], track_features_df_two[desired_feature], equal_var=False)
    t_rounded = round(t, 3)
    p_rounded = round(p, 7)
    print(f't = {t_rounded}  p = {p_rounded}')
    return p_rounded, t_rounded, desired_feature, group


def get_top5_genres(spotify, tracks):
    artists = []
    for track in tracks:
        for artist in track["artists"]:
            artists.append(artist["id"])
    print(f"Total number of artists retrieved: {len(artists)}")
    print(f"Number of unique artists retrieved: {len(set(artists))}")
    artists_retrieved = fetch_artists(spotify, artists)
    artist_genres = []
    for artist in artists_retrieved:
        artist_genres.extend(artist["genres"])
    genre_counts = Counter(artist_genres)
    available_genres = spotify.recommendation_genre_seeds()["genres"]
    counter = 0
    genres = []
    for (genre, _) in genre_counts.most_common():
        if counter >= 5:
            break
        if genre in available_genres:
            genres.append(genre)
            counter += 1
    print(f"Found {counter} genres: {genres}")
    return genres


def get_recommendations(spotify, descriptive_statistics_df, seed_genres):
    print_header('Get recommendations')

    descriptive_statistics_df = descriptive_statistics_df.query('group == "mood boosting"')

    results = spotify.recommendations(seed_artists=None, seed_genres=seed_genres, seed_tracks=None,
                                      country=None, limit=10,
                                      min_tempo=descriptive_statistics_df.query('feature == "tempo"')["mean"] - descriptive_statistics_df.query('feature == "tempo"')["standard deviation"],
                                      max_tempo=descriptive_statistics_df.query('feature == "tempo"')["mean"] + descriptive_statistics_df.query('feature == "tempo"')["standard deviation"],
                                      min_loudness=descriptive_statistics_df.query('feature == "loudness"')["mean"] - descriptive_statistics_df.query('feature == "loudness"')["standard deviation"],
                                      max_loudness=descriptive_statistics_df.query('feature == "loudness"')["mean"] + descriptive_statistics_df.query('feature == "loudness"')["standard deviation"],
                                      min_energy=descriptive_statistics_df.query('feature == "energy"')["mean"] - descriptive_statistics_df.query('feature == "energy"')["standard deviation"],
                                      max_energy=descriptive_statistics_df.query('feature == "energy"')["mean"] + descriptive_statistics_df.query('feature == "energy"')["standard deviation"],
                                      min_danceability=descriptive_statistics_df.query('feature == "danceability"')["mean"] - descriptive_statistics_df.query('feature == "danceability"')["standard deviation"],
                                      max_danceability=descriptive_statistics_df.query('feature == "danceability"')["mean"] + descriptive_statistics_df.query('feature == "danceability"')["standard deviation"],
                                      min_speechiness=descriptive_statistics_df.query('feature == "speechiness"')["mean"] - descriptive_statistics_df.query('feature == "speechiness"')["standard deviation"],
                                      max_speechiness=descriptive_statistics_df.query('feature == "speechiness"')["mean"] + descriptive_statistics_df.query('feature == "speechiness"')["standard deviation"],
                                      min_valence=descriptive_statistics_df.query('feature == "valence"')["mean"] - descriptive_statistics_df.query('feature == "valence"')["standard deviation"],
                                      max_valence=descriptive_statistics_df.query('feature == "valence"')["mean"] + descriptive_statistics_df.query('feature == "valence"')["standard deviation"]
                                      )
    recommendations = []
    for track in results['tracks']:
        artists = "; ".join([artist["name"] for artist in track["artists"]])
        print(f'Artists: {artists}\n'
              f'Name: {track["name"]}\n'
              f'Preview-URL: {track["preview_url"]}\n'
              f'Spotify-URL: {track["external_urls"]["spotify"]}\n')
        recommendations.append([artists, track["name"], track["preview_url"], track["external_urls"]["spotify"]])
    return recommendations


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
