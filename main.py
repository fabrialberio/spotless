import time

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from spotless import SpotlessPlaylist, SpotlessTrackInfo
from src.youtube import SpotlessThreadedDownloader, SpotlessYTDownloader

if __name__ == "__main__":
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=""))

    playlist_url = input("Insert link to the playlist you want to download: ")
    playlist = SpotlessPlaylist.from_url(sp, playlist_url)

    print(f"Downloading songs from «{playlist.name}»...")
    start_time = time.time()

    tracks = list(playlist)

    def track_downloaded(position: int, track: SpotlessTrackInfo):
        print(
            f"({position + 1}/{len(tracks)})\tDownloaded «{', '.join(track.artists)} - {track.name}»"
        )

    downloader = SpotlessYTDownloader(track_downloaded)
    threaded_downloader = SpotlessThreadedDownloader(downloader)
    threaded_downloader.download_tracks(playlist.name, tracks)
