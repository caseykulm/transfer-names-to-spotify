import spotipy
import json
from sys import argv

def get_id_for_artist(sp, artist_name) :
    result = sp.search(q="artist:{0}".format(artist_name), type='artist')
    return result['artists']

def get_albums_for_artist(sp, artist_id) :
    # results = sp.search(q="artist:{0}".format(artist_name), type='album')
    results = sp.artist_albums("spotify:artist:{0}".format(artist_id), album_type='album')
    albums = results['items']
    while results['next']:
        results = sp.next(results)
        albums.extend(results['items'])
    for album in albums:
        print(album['name'])
    return albums

def pretty_print_json(json_str) :
    print json.dumps(json_str, sort_keys=False, indent=2, separators=(',', ': '))

def handle_no_artists_found(artist_name) :
    print "No artists found for {0}".format(artist_name)

def handle_one_artist_found(artist_name, artists) :
    print "1 artists found for {0}".format(artist_name)
    artist = artists['items'][0]
    genres = artist['genres']
    resolved_name = artist['name']
    spotify_uri = artist['uri']
    print "resolved name to {0} with genres {1} and uri {2}".format(resolved_name, genres, spotify_uri)

def handle_multiple_artists_found(artist_name, artists_count, artists) :
    print "{0} artists found for {1}".format(artists_count, artist_name)
    # for artist in artists['items'] :
    #     an = artist['name']
    #     ap = artist['popularity']
    #     aft = artist['followers']['total']
    #     auri = artist['uri']
    #     print u'{0} with {1} popularity and {2} followers and uri {3}'.format(an, ap, aft, auri)

def transfer_artist(sp, artist_name) :
    artists = get_id_for_artist(sp, artist_name)
    artists_count = artists['total']
    if artists_count == 0 :
        handle_no_artists_found(artist_name)
        return False
    elif artists_count == 1:
        handle_one_artist_found(artist_name, artists)
        return True
    else :
        handle_multiple_artists_found(artist_name, artists_count, artists)
        return True

def transfer_artists(sp, artist_names) :
    found_artist_names = []
    not_found_artist_names = []
    for artist_name in artist_names :
        print "### Transfer for {0} ###".format(artist_name)
        found = transfer_artist(sp, artist_name)
        if found :
            found_artist_names.append(artist_name)
        else :
            not_found_artist_names.append(artist_name)
        print ""
    return found_artist_names, not_found_artist_names

def get_artist_names_from_file(file_name) :
    return [line.rstrip('\n') for line in open(file_name)]

script, filename = argv

sp = spotipy.Spotify()
artist_names = get_artist_names_from_file(filename)
found_artist_names, not_found_artist_names = transfer_artists(sp, artist_names)

print "### Failed to find artists for ###"
for artist_name in not_found_artist_names:
    print artist_name
