import time

from spotless import SpotlessTrackInfo
from src.threaded_downloader import ThreadedDownloader
from src.youtube import YouTubeDownloader
from src.youtube_music import YouTubeMusicPlaylist

if __name__ == "__main__":
    playlist_url = (
        "https://music.youtube.com/browse/VLPL5v92TGSjhP0hNmjx4EnkQL0ugblJC81j"
    )
    playlist = YouTubeMusicPlaylist.from_url(playlist_url)

    print(f"Downloading songs from «{playlist.name}»...")
    start_time = time.time()

    tracks = playlist.fetch_tracks()

    print("First track:", tracks[0])

    exit()

    def track_downloaded(position: int, track: SpotlessTrackInfo):
        print(
            f"({position + 1}/{len(tracks)})\tDownloaded «{', '.join(track.artists)} - {track.name}»"
        )

    downloader = YouTubeDownloader(track_downloaded)
    threaded_downloader = ThreadedDownloader(downloader)
    threaded_downloader.download_tracks(playlist.name, tracks)
