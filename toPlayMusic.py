#!/usr/local/bin/python3
import os

from gmusicapi import Mobileclient
import getpass
import argparse

parser = argparse.ArgumentParser(description='Create a Google Play Music playlist from a list of track names.')
parser.add_argument('--account', required=True,
                   help='Google Play account (email address)')
parser.add_argument('--playlist', required=True,
                   help='Google Play Music playlist to add tracks to. If a playlist by the given name does not exist, '
                        'a new playlist is created')
parser.add_argument('--tracklist', required=True,
                   help='Path for a file listing the tracks to be added to the playlist')

args = parser.parse_args()

with open(args.tracklist) as f:
    trackNamesToBeAdded = f.readlines()

password = ''
if 'GOOGLE_PLAY_PASSWORD' in os.environ:
    password = os.environ['GOOGLE_PLAY_PASSWORD']
if not password:
    password = getpass.getpass('Google Play account password: ')

api = Mobileclient()
api.login(args.account, password, Mobileclient.FROM_MAC_ADDRESS)

print("Login successful")

api = Mobileclient()
api.login(args.account, password, Mobileclient.FROM_MAC_ADDRESS)

playlists = api.get_all_playlists()

playlistIds = [playlist['id'] for playlist in playlists
            if playlist['name'] == args.playlist]

playlistId = ''

if not playlistIds:
    print("Playlist with name '{} was not found from Google Play music. Creating a new playlist".format(args.playlist))
    playlistId = api.create_playlist(args.playlist)
else:
    playlistId = playlistIds[0]

print("Searching for track list tracks from library")
def matchesSearch(title):
    for s in trackNamesToBeAdded:
        titleToMatch = s.rstrip()
        if title.strip('!?,.').lower().find(titleToMatch.lower()) != -1:
            print("Found a match for: {}: {}".format(titleToMatch, title))
            return True
    return False

library = api.get_all_songs()
tracks = [track['id'] for track in library
          if matchesSearch(track['title'])]

print("Adding tracks")
api.add_songs_to_playlist(playlistId, tracks)
print("Done")