import os

def scan_music(path):
    library = {}
    for artist in sorted(os.listdir(path)):
        artist_path = os.path.join(path, artist)
        if os.path.isdir(artist_path):
            albums = {}
            for album in sorted(os.listdir(artist_path)):
                album_path = os.path.join(artist_path, album)
                if os.path.isdir(album_path):
                    allowed_extensions = {".mp3", ".flac", ".wav", ".aac", ".ogg", ".webm"}
                    songs = [
                        os.path.join(album_path, f)
                        for f in sorted(os.listdir(album_path))
                        if os.path.splitext(f)[1].lower() in allowed_extensions
                    ]
                    if songs:
                        albums[album] = songs
            if albums:
                library[artist] = albums
    return library

def flatten_album(albums):
    return [song for album in albums.values() for song in album]