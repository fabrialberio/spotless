import time

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from downloaders import SpotlessThreadedDownloader
from spotless import SpotlessPlaylist, SpotlessTrackInfo

if __name__ == "__main__":
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=""))

    playlist_url = input("Insert link to the playlist you want to download: ")
    playlist = SpotlessPlaylist.from_url(sp, playlist_url)

    print(f"Downloading songs from «{playlist.name}»...")
    start_time = time.time()

    tracks = list(playlist)

    def track_downloaded(position: int, track: SpotlessTrackInfo):
        print(
            f"({position + 1}/{len(tracks)})\tDownloaded «{track.artist} - {track.name}»"
        )

    downloader = SpotlessThreadedDownloader()
    downloader.download_tracks(playlist.name, tracks, track_downloaded)
