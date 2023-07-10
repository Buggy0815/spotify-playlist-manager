import pandas as pd
import numpy as np
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from fuzzywuzzy import process, fuzz
import sys
sys.path.append('..')
import config

# function that reads a two column pandas dataframe (artist, title)
# checking if the song exists on spotify
# checking if the song is already in playlist
# adding song to the playlist

# 1. dropping duplicates in dataframe
# 2. dropping unknown and untitled tracks
# 3.

token = SpotifyOAuth(scope = config.scope,
                    username = config.username,
                    client_id = config.client_id,
                    client_secret = config.client_secret,
                    redirect_uri = config.redirect_uri)
spotifyObject = spotipy.Spotify(auth_manager = token)



def add_df_to_playlist(df, playlist_name):
	df = clean_tracks(df)
	df = add_uris(df)
	df = check_tracks(df)
	add_to_playlist(df, playlist_name)

def clean_tracks(df):
    df = df.drop_duplicates(subset = ['title', 'artist'])
    df = df.replace('', np.nan)
    df = df.replace('Untitled', np.nan)
    df = df.replace('Unknown', np.nan)
    df = df.drop(df.loc[df.isna().any(axis = 1)].index)
    return df

# adding a uri column to the whole dataframe
def add_uris(df):
    df['search'] = df.apply(lambda row: row['title'] + ', ' + row['artist'], axis = 1)
    df['item'] = df['search'].apply(lambda x : add_item(x))
    df['artist2'] = df['item'].apply(lambda x: add_artist(x))
    df['title2'] = df['item'].apply(lambda x: add_title(x))
    df['uri'] = df['item'].apply(lambda x: add_uri(x))
    df['id'] = df['item'].apply(lambda x: add_id(x))
    #df = df.drop('item', axis = 1)
    df = df.loc[df.notna().all(axis = 1)]
    return df

# functions to apply within dataframe to every row

def add_item(search):
    try:
        ret = spotifyObject.search(q = search)['tracks']['items']
    except:
        ret = np.nan
    return ret


def add_artist(item):
    try:
        ret = item[0]['artists'][0]['name']
    except:
        ret = np.nan
    return ret

def add_title(item):
    try:
        ret = item[0]['name']
    except:
        ret = np.nan
    return ret

def add_uri(item):
    try:
        ret = item[0]['uri']
    except:
        ret = np.nan
    return ret

def add_id(item):
    try:
        ret = item[0]['id']
    except:
        ret = np.nan
    return ret

def get_uri_list(items):
    uris = []
    for i in range(len(items)):
        uris.append(items[i]['track']['uri'])
    return uris

def get_tracks(playlist_id):
    playlist = spotifyObject.playlist_tracks(playlist_id)
    tracks = []
    tracks.extend(get_uri_list(playlist['items']))
    while playlist['next']:
        playlist = spotifyObject.next(playlist)
        tracks.extend(get_uri_list(playlist['items']))
    return tracks


# check retrieved title and artist names to input and deleting tracks that are too different from input
def check_tracks(df):
    df['PTSR_artist'] = df.apply(lambda row: fuzz.partial_token_set_ratio(row['artist'].lower(), row['artist2'].lower()), axis = 1)
    df['PR_title'] = df.apply(lambda row: fuzz.partial_ratio(row['title'].lower(), row['title2'].lower()), axis = 1)
    df = df.drop(df.loc[(df['PTSR_artist'] < 100)].index)
    df = df.drop(df.loc[(df['PR_title'] < 50)].index)
    return df

def add_to_playlist(df, playlist_name):
    uri_list = df['uri'].tolist()
    #get all the playlist by user
    playlists = spotifyObject.user_playlists(user = config.username)
    #search for playlist index (ix) by name
    playlists_list = [playlist['name'] for playlist in playlists['items']]
    ix = playlists_list.index(playlist_name)
    playlist_id = playlists['items'][ix]['id']
    added_uris = get_tracks(playlist_id)
    uris_toadd = uri_list = list(set(uri_list) - set(added_uris))
    chunks = [uris_toadd[x:x+100] for x in range(0, len(uris_toadd), 100)]
    for chunk in chunks:
        spotifyObject.user_playlist_add_tracks(user = config.username, playlist_id = playlist_id, tracks = chunk)
