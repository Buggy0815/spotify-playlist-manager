# Spotify-Playlist-Manager

this project is about using the spotipy api to add songs from a table format to one of your spotify playlists. It first checks if the songs you want to add already exist in the playlist in order to avoid having the same song multiple times in your playlist. Furthermore you cannot be sure spotify having every track you want to add. Because of that reason this script checks that also in a way by searching for the track on spotify and comparing the 1st result of your search with the track you actually entered in the search

## Usage
1. Get your spotify credentials on https://developer.spotify.com/dashboard
   - Create App
   - Go to settings
   - find your credentials
   - put them into config.py.sample file
   - rename config.py.sample -> config.py

2. install the required packages by
   pip install -r requirements.txt

3. Check the Example.ipynb Notebook
