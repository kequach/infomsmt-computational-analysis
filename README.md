- [SMT project: Music recommendation and analysis](#smt-project-music-recommendation-and-analysis)
      - [The Spotify Web API](#the-spotify-web-api)
      - [Spotipy](#spotipy)
  - [Setup](#setup)
      - [Register Your Application With Spotify](#register-your-application-with-spotify)
      - [Install Dependencies](#install-dependencies)
  - [Running](#running)
      - [Example Run](#example-run)

# SMT project: Music recommendation and analysis
This repo contains the code for the Sound and Music Technology Project in 2021 for group 2.
TODO: Add more info


#### The Spotify Web API
The Spotify Web API allows applications to fetch lots of awesome data from the Spotify catalog, as well as manage
a user's playlists and saved music.  Some examples of of info you get are:
  - Track, artist, album, and playlist metadata and search
  - High-level audio features for tracks
  - In-depth audio analysis for tracks
  - Featured playlists and new releases
  - Music recommendations based on seed data

#### Spotipy
Spotipy is an awesome lightweight Python wrapper library for the Spotify Web API.  Using Spotipy, you can get any information
that you can get through the raw Web API.  The library does a bunch of the heavy lifting for things like authenticating
against the API, serializing request data, and deserialzing response data.


## Setup
#### Register Your Application With Spotify
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

#### Install Dependencies
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

You need to provide a .csv file. See following example:
```
playlist_name,link,category
Mood Booster,https://open.spotify.com/playlist/37i9dQZF1DX3rxVfibe1L0,happy
Songs to Sing in the Shower,https://open.spotify.com/playlist/37i9dQZF1DWSqmBTGDYngZ,happy
Happy Hits!,https://open.spotify.com/playlist/37i9dQZF1DXdPec7aLTmlC,happy
Beast Mode, https://open.spotify.com/playlist/37i9dQZF1DX76Wlfdnj7AP,neutral
```
Only link and category are needed. You can leave the playlist_name empty.

#### Example Run
TODO: Update example run when complete
```
```
