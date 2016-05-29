#!/usr/local/bin/python3

from gmusicapi import Mobileclient
import taglib
import fnmatch
import os
import getpass
import argparse

parser = argparse.ArgumentParser(description='Create a m3u playlist from Google Play Music playlist.')
parser.add_argument('--account', required=True,
                   help='Google Play account (email address)')
parser.add_argument('--playlist', required=True,
                   help='Google Play Music playlist to convert')
parser.add_argument('--path', required=True,
                   help='Path on local file system where music files are located')

args = parser.parse_args()

password = ''
if 'GOOGLE_PLAY_PASSWORD' in os.environ:
    password = os.environ['GOOGLE_PLAY_PASSWORD']
if not password:
    password = getpass.getpass('Google Play account password: ')

api = Mobileclient()
api.login(args.account, password, Mobileclient.FROM_MAC_ADDRESS)

print("Login successful")

print("Fetching all playlists")
googlePlayPlaylists = api.get_all_user_playlist_contents()

print("Fetching list of tracks for the playlist")
googlePlayPlaylistTrackList = [playlist['tracks'] for playlist in googlePlayPlaylists
                               if playlist['name'] == args.playlist][0]

googlePlayTrackIds = list(map(lambda x: x['trackId'], googlePlayPlaylistTrackList))

print("Fetching list of files in Google Play library")
allTracksInGooglePlayLibrary = api.get_all_songs()

print("Fetching track info for tracks in playlist")
tracksInGooglePlayPlaylist = [track for track in allTracksInGooglePlayLibrary
                              if track['id'] in googlePlayTrackIds]

googlePlayTrackInfos = \
    list(map(lambda x: {'artist': x['artist'], 'title': x['title'], 'comment': x['comment'], 'album': x['album']},
             tracksInGooglePlayPlaylist))

def googlePlayPlaylistContainsTrack(tags):
    for info in googlePlayTrackInfos:
        if 'ARTIST' in tags and 'TITLE' in tags and info['artist'] == tags['ARTIST'][0] and info['title'] == tags['TITLE'][0]:
                # TODO: remove track from infos
                googlePlayTrackInfos.remove(info)
                print("Found a match for: {} - {}".format(tags['ARTIST'][0], tags['TITLE'][0]))
                return True
    return False

print("Searching for matching tracks in {}".format(args.path))
tags = []
for root, dirnames, filenames in os.walk(args.path):
    for filename in fnmatch.filter(filenames, '*.mp3'):
        fullPath = os.path.join(root, filename)
        tagInfo = taglib.File(fullPath)
        if (googlePlayPlaylistContainsTrack(tagInfo.tags)):
            tags.append(tagInfo)

playlistFile = '{}.m3u'.format(args.playlist)
print("Writing playlist to {}", playlistFile)
of = open(playlistFile, 'w')
of.write("#EXTM3U\n")

for tagInfo in tags:
    of.write("#EXTINF:%s,%s\n" % (tagInfo.length, tagInfo.path))
    of.write(tagInfo.path + "\n")

of.close()

print("Done")