# SMT project: Music recommendation and analysis <!-- omit in toc -->
- [General information](#general-information)
  - [The Spotify Web API](#the-spotify-web-api)
  - [Spotipy](#spotipy)
- [Setup](#setup)
  - [Register Your Application With Spotify](#register-your-application-with-spotify)
  - [Install Dependencies](#install-dependencies)
- [Running](#running)
  - [Example Run](#example-run)

This repo contains the code for the Sound and Music Technology Project in 2021 for group 2.
TODO: Add more info

## General information

### The Spotify Web API
The Spotify Web API allows applications to fetch lots of awesome data from the Spotify catalog, as well as manage
a user's playlists and saved music.  Some examples of of info you get are:

  - Track, artist, album, and playlist metadata and search
  - High-level audio features for tracks
  - In-depth audio analysis for tracks
  - Featured playlists and new releases
  - Music recommendations based on seed data

### Spotipy

Spotipy is an awesome lightweight Python wrapper library for the Spotify Web API.  Using Spotipy, you can get any information
that you can get through the raw Web API.  The library does a bunch of the heavy lifting for things like authenticating
against the API, serializing request data, and deserialzing response data.

## Setup

### Register Your Application With Spotify

In order to access certain features of the Web API, we need to tell spotify that we're a legitimate app.
To do this, go to https://developer.spotify.com/my-applications and create a new Application.

For the Redirect URI, add `http://localhost/` - It should look like this:
![spotify application page](https://raw.githubusercontent.com/markkohdev/spotify-api-starter/master/assets/spotify_api.png)

From that page, copy your ClientId and your ClientSecret and put them into a file called
`.env` in the root of this repo that looks like this:
```
SPOTIPY_CLIENT_ID='YOUR_CLIENT_ID'
SPOTIPY_CLIENT_SECRET='YOUR_CLIENT_SECRET'
```
For details about how the API authenticates your account with this, see
https://developer.spotify.com/web-api/authorization-guide/#authorization_code_flow

### Install Dependencies

In order to run this program, we need to make sure python3 and pip are installed on your system.
To install this stuff, run
```
pip install -r requirements.txt
```

## Running

To run the project, navigate to the src folder and execute the following from the command line:
```
python main.py
```

You need to provide a playlists.csv file. See following example:
```
playlist_name,link,category
Mood Booster,https://open.spotify.com/playlist/37i9dQZF1DX3rxVfibe1L0,happy
Songs to Sing in the Shower,https://open.spotify.com/playlist/37i9dQZF1DWSqmBTGDYngZ,happy
Happy Hits!,https://open.spotify.com/playlist/37i9dQZF1DXdPec7aLTmlC,happy
Beast Mode, https://open.spotify.com/playlist/37i9dQZF1DX76Wlfdnj7AP,neutral
```
Only link and category are needed. You can leave the playlist_name empty.

It is also possible to use other .csv or .xlsx files. Here is an example. You need to specify the file name on the command line:
```
python main.py --input ../other_file_name.csv
```

### Example Run

TODO: Update example run when complete
```
**************************************************
Spotify Web API - Computational Analysis
**************************************************

**************************************************
Parsing playlists
**************************************************
Get tracks from list of playlists for mood boosting
Total number of tracks retrieved: 495
Get tracks from list of playlists for running
Total number of tracks retrieved: 502
Get tracks from list of playlists for studying
Total number of tracks retrieved: 505

**************************************************
Calculating statistics
**************************************************
Successfully calculated statistics and exported to tables subfolder.

**************************************************
Get top 5 genres
**************************************************
Total number of artists retrieved: 662
Unique number of artists retrieved: 363
Found 5 genres: pop, soul, edm, funk, disco

**************************************************
Get recommendations
**************************************************
Artists: Duke Dumont; Jax Jones
Name: I Got U
Preview-URL: None
Spotify-URL: https://open.spotify.com/track/4r8hRPbidDIoDPphxi78aY

Artists: Jess Glynne
Name: All I Am
Preview-URL: None
Spotify-URL: https://open.spotify.com/track/5GNjiM8jZCgbqjHklAcT9e

Artists: Thelma Houston
Name: Don't Leave Me This Way - Single Version
Preview-URL: None
Spotify-URL: https://open.spotify.com/track/4IMArXimMttK8tB0UBa0Ue

Artists: Britney Spears
Name: Till the World Ends
Preview-URL: https://p.scdn.co/mp3-preview/fd017ae5c0a60cff3d5f5b4d37c4e8617c93b11f?cid=33046789d13d49dda7597ce0554f1919
Spotify-URL: https://open.spotify.com/track/38iU2jg98IZZEIJPrP7aWD

Artists: Pitbull; Ne-Yo
Name: Time of Our Lives
Preview-URL: https://p.scdn.co/mp3-preview/c7ee72511ef4733508b42f92de3e62ed4753e223?cid=33046789d13d49dda7597ce0554f1919
Spotify-URL: https://open.spotify.com/track/2bJvI42r8EF3wxjOuDav4r

Artists: Flo Rida
Name: I Cry
Preview-URL: https://p.scdn.co/mp3-preview/83ecc26ad34e94df4a61ed9e44cdd3bacda81d6a?cid=33046789d13d49dda7597ce0554f1919
Spotify-URL: https://open.spotify.com/track/3zrYNl1aMdFrQkcOjKVr5u

Artists: Echosmith
Name: Cool Kids
Preview-URL: https://p.scdn.co/mp3-preview/27df0a89036135748fd03fb67114abeb00c529a4?cid=33046789d13d49dda7597ce0554f1919
Spotify-URL: https://open.spotify.com/track/13P5rwmk2EsoFRIz9UCeh9

Artists: Melanie Martinez
Name: Dollhouse
Preview-URL: https://p.scdn.co/mp3-preview/d98a9f944430689505c2ee20aa6180b6949830f0?cid=33046789d13d49dda7597ce0554f1919
Spotify-URL: https://open.spotify.com/track/6wNeKPXF0RDKyvfKfri5hf

Artists: Little Mix
Name: Touch
Preview-URL: None
Spotify-URL: https://open.spotify.com/track/6B7op3kK1kFQp4Ck1UZtK5

Artists: Martha Reeves & The Vandellas
Name: Dancing In The Street
Preview-URL: None
Spotify-URL: https://open.spotify.com/track/6TPl5DQrkBY2XIqIaFmxqi
```
