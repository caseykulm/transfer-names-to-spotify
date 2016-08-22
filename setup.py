import spotipy
import json
from sys import argv

# helper to make the json readable
def pretty_print_json(json_str) :
    print json.dumps(json_str, sort_keys=False, indent=2, separators=(',', ': '))

def get_id_for_artist(sp, artist_name) :
    result = sp.search(q="artist:{0}".format(artist_name), type='artist')
    return result['artists']

def get_songs_for_album(sp, album_uri) :
    return ['abc123']

def get_albums_for_artist(sp, artist_uri) :
    # results = sp.search(q="artist:{0}".format(artist_name), type='album')
    results = sp.artist_albums(artist_uri, album_type='album')
    albums = results['items']
    while results['next']:
        results = sp.next(results)
        albums.extend(results['items'])
    for album in albums:
        pretty_print_json(album)
    return albums

def get_songs_for_artist(sp, artist_uri) :
    albums = get_albums_for_artist(sp, artist_uri)
    songs_for_artist = []
    for album in albums :
        songs_for_album = get_songs_for_album(sp, album['uri'])
        for song in songs_for_album :
            songs_for_artist.append(song)
    return songs_for_artist

# :( No artist found on spotify for the search query
def handle_no_artists_found(artist_name) :
    print "No artists found for {0}".format(artist_name)
    return False, None

# Ideal state where there is only one artist listed for the query text
def handle_one_artist_found(artist_name, artists) :
    print "1 artists found for {0}".format(artist_name)
    artist = artists['items'][0]
    genres = artist['genres']
    resolved_name = artist['name']
    spotify_uri = artist['uri']
    print "resolved name to {0} with genres {1} and uri {2}".format(resolved_name, genres, spotify_uri)
    return True, artist

# Chooses the first spotify artist listed since it seems to alway be the most
# relevant one
def handle_multiple_artists_found(artist_name, artists_count, artists) :
    print "{0} artists found for {1}".format(artists_count, artist_name)
    # for artist in artists['items'] :
    #     an = artist['name']
    #     ap = artist['popularity']
    #     aft = artist['followers']['total']
    #     auri = artist['uri']
    #     print u'{0} with {1} popularity and {2} followers and uri {3}'.format(an, ap, aft, auri)
    artist = artists['items'][0]
    return True, artist

def get_resolved_artist(sp, artist_name) :
    artists = get_id_for_artist(sp, artist_name)
    artists_count = artists['total']
    if artists_count == 0 :
        return handle_no_artists_found(artist_name)
    elif artists_count == 1:
        return handle_one_artist_found(artist_name, artists)
    else :
        return handle_multiple_artists_found(artist_name, artists_count, artists)

# Given the list of artist names, it resolves artists to spotify models
# and creates found/not found lists
def get_resolved_artists(sp, artist_names) :
    resolved_artists = []
    found_artist_names = []
    not_found_artist_names = []
    for artist_name in artist_names :
        print "### Transfer for {0} ###".format(artist_name)
        found, artist = get_resolved_artist(sp, artist_name)
        if found :
            found_artist_names.append(artist_name)
            resolved_artists.append(artist)
        else :
            not_found_artist_names.append(artist_name)
        print ""
    return found_artist_names, not_found_artist_names, resolved_artists

# Wrapper around get_resolved_artists that helps find missing artists
# returns the resolved artists
def resolve_artists_helper(sp, artist_names) :
    found_artist_names, not_found_artist_names, resolved_artists = get_resolved_artists(sp, artist_names)

    if len(not_found_artist_names) > 0:
        print "### Failed to find artists for ###"
        for artist_name in not_found_artist_names:
            print artist_name
        raise ValueError('Missing artists')

    return resolved_artists

def get_artist_names_from_file(file_name) :
    return [line.rstrip('\n') for line in open(file_name)]

script, filename = argv

sp = spotipy.Spotify()
artist_names = get_artist_names_from_file(filename)
resolved_artists = resolve_artists_helper(sp, artist_names)

for resolved_artist in resolved_artists:
    artist_uri = resolved_artist['uri']
    get_albums_for_artist(sp, artist_uri)
