import time

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from spotless import SpotlessTrackInfo
from src.spotify import SpotifyPlaylist
from src.threaded_downloader import ThreadedDownloader
from src.youtube import YouTubeDownloader

if __name__ == "__main__":
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=""))

    playlist_url = input("Insert link to the playlist you want to download: ")
    playlist = SpotifyPlaylist.from_url(sp, playlist_url)

    print(f"Downloading songs from «{playlist.name}»...")
    start_time = time.time()

    tracks = list(playlist)

    def track_downloaded(position: int, track: SpotlessTrackInfo):
        print(
            f"({position + 1}/{len(tracks)})\tDownloaded «{', '.join(track.artists)} - {track.name}»"
        )

    downloader = YouTubeDownloader(track_downloaded)
    threaded_downloader = ThreadedDownloader(downloader)
    threaded_downloader.download_tracks(playlist.name, tracks)
