import curses
import sys
import os
import vlc

PADDING = 4

# ---- Scan music library ----
def scan_music(path):
    library = {}
    for artist in sorted(os.listdir(path)):
        artist_path = os.path.join(path, artist)
        if os.path.isdir(artist_path):
            albums = {}
            for album in sorted(os.listdir(artist_path)):
                album_path = os.path.join(artist_path, album)
                if os.path.isdir(album_path):
                    songs = [
                        os.path.join(album_path, f)
                        for f in sorted(os.listdir(album_path))
                        if f.lower().endswith(".mp3")
                    ]
                    if songs:
                        albums[album] = songs
            if albums:
                library[artist] = albums
    return library

def songs_for_artist(albums):
    return [song for album in albums.values() for song in album]

# refactor artists and songs to use draw list
def draw_list(win, items, offset, selected, max_rows):
    visible = items[offset:offset + max_rows]
    for i, item in enumerate(visible):
        if i + offset == selected:
            win.addstr(i + 1, 2, item, curses.A_STANDOUT)
        else:
            win.addstr(i + 1, 2, item)

def main_ui(stdscr, path):
    # INITIALIZATION
    curses.curs_set(0)
    selected_artist = 0
    library = scan_music(path)
    artist_offset = 0
    selected_song = 0
    song_offset = 0
    curr_song = None
    curr_artist = None
    playing = False
    repeat = False

    if not library:
        stdscr.addstr(0, 0, "No mp3 files found in the specified path.")
        stdscr.getch()
        return
    
    artists = list(library.keys())

    instance = vlc.Instance()
    player = instance.media_player_new()
    volume = 50
    player.audio_set_volume(volume)

    # Initialize windows once
    height, width = stdscr.getmaxyx()
    max_rows = height - 9
    artist_win_height = height - 7
    
    artist_win = curses.newwin(artist_win_height, int(width/2) - 1, 2, 0)
    songs_win = curses.newwin(artist_win_height, int(width/2) - 1, 2, int(width/2)+1)
    
    # Draw static elements once
    stdscr.clear()
    header = "TMUS - Terminal Music Player"
    stdscr.addstr(1, 1, header, curses.A_BOLD)
    footer = "[q] quit     [p] pause    [+/-] volume     [Enter] play"
    stdscr.addstr(height - 1, int(width/2 - len(footer)/2), footer, curses.A_BOLD)

    while True:
        stdscr.timeout(1500)  # wait max 200ms for key, then return -1 if no input
        
        # Only clear and redraw the content windows
        artist_win.clear()
        songs_win.clear()
        artist_win.box()
        songs_win.box()

        # ---------- ARTISTS SECTION ----------
        # Test an artist with more songs than space permits
        visible_artists = artists[artist_offset:artist_offset + max_rows]
        for i in range(len(visible_artists)):
            if i >= max_rows: break
            if selected_artist == i: artist_win.addstr(i + 1, 2, visible_artists[i], curses.A_STANDOUT)
            else: artist_win.addstr(i + 1, 2, visible_artists[i])

        # ---------- SONGS SECTION ----------
        current_artists_albums = library[visible_artists[selected_artist]]
        all_songs_by_artist = songs_for_artist(current_artists_albums)

        visible_songs = all_songs_by_artist[song_offset : song_offset + max_rows]
        for i, song in enumerate(visible_songs):
            song_split = os.path.basename(song)
            if i == selected_song + song_offset:
                songs_win.addstr(i + 1, 2, song_split, curses.A_STANDOUT)
            else:
                songs_win.addstr(i + 1, 2, song_split)
        
        # Clear and redraw only the now playing area
        if curr_song and curr_artist:
            # Clear the now playing lines
            stdscr.addstr(height - 4, 1, " " * (width - 2))
            stdscr.addstr(height - 3, 1, " " * (width - 2))
            
            pos = player.get_time() / 1000
            duration = player.get_length() / 1000

            if duration <= 0:
                duration = 1

            now_playing = f"Now Playing: {os.path.basename(curr_song)}"
            stdscr.addstr(height - 4, 1, now_playing, curses.A_BOLD)
            bar_width = max(1, width - 2)

            progress = int((pos/duration) * bar_width)
            stdscr.addstr(height - 3, 1, "#" * progress)
            stdscr.addstr(height - 3, 1 + progress, "-" * (bar_width - progress))
            stdscr.addstr(height - 3, 1, "[")
            stdscr.addstr(height - 3,  bar_width, "]")

        stdscr.refresh()
        artist_win.refresh()
        songs_win.refresh()
        key = stdscr.getch()

        # ---------- NAVIGATION ----------
        if key == curses.KEY_UP:
            song_offset = 0; selected_song = 0
            if selected_artist > 0: selected_artist -= 1
            elif selected_artist + artist_offset > 0:
                    artist_offset -= 1
        elif key == curses.KEY_DOWN:
            song_offset = 0; selected_song = 0
            if selected_artist < min(max_rows - 1, len(artists) -  1): selected_artist += 1
            elif selected_artist + artist_offset < len(artists) - 1:
                    artist_offset += 1

        if key == curses.KEY_LEFT:
            if selected_song > 0: selected_song -= 1
            elif selected_song + song_offset > 0:
                    song_offset -= 1
        elif key == curses.KEY_RIGHT:
            if selected_song < min(max_rows - 1, len(all_songs_by_artist) - 1): selected_song += 1
            elif selected_song + song_offset < len(all_songs_by_artist) - 1:
                    song_offset += 1
        
        if key in (curses.KEY_ENTER, 10, 13):
            curr_song = visible_songs[selected_song]
            curr_artist = visible_artists[selected_artist]
            media = instance.media_new(curr_song)
            player.set_media(media)
            player.play()
            playing = True
        elif key == ord("="):
            volume = min(100, volume + 5)
            player.audio_set_volume(volume)
        elif key == ord("-"):
            volume = max(0, volume - 5)
            player.audio_set_volume(volume)
        elif key == ord("p"):
            if playing:
                player.pause()
            else: player.pause()

        if key == ord("q"):
            break
        if key == -1:
            # no key pressed, just continue
            pass

def main():
    if len(sys.argv) < 2:
        print("Usage: python app.py <music_directory>")
        sys.exit(1)
    curses.wrapper(main_ui, sys.argv[1])

if __name__ == "__main__":
    main()
