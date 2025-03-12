import time

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from downloaders import UnspotifyThreadedDownloader
from unspotify import UnspotifyPlaylist

if __name__ == "__main__":
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=""))

    playlist_url = input("Insert link to the playlist you want to download: ")
    playlist = UnspotifyPlaylist.from_url(sp, playlist_url)

    print(f"Downloading songs from «{playlist.name}»...")
    start_time = time.time()

    downloader = UnspotifyThreadedDownloader()
    downloader.download_tracks(
        playlist.name,
        list(playlist),
        lambda: print(
            f"Download completed in {time.time() - start_time:.2f} seconds."
        ),
    )
