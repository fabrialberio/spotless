from src.spotify import SpotifyPlaylist
from src.spotless import SpotlessTrackInfo
from src.threaded_downloader import ThreadedDownloader
from src.youtube_music import YouTubeMusicDownloader, YouTubeMusicPlaylist

if __name__ == "__main__":
    playlist_url = input(
        "Inserire il link della playlist che si vuole scaricare: "
    )

    if "music.youtube.com" in playlist_url:
        playlist = YouTubeMusicPlaylist.from_url(playlist_url)
    elif "open.spotify.com" in playlist_url:
        playlist = SpotifyPlaylist.from_url(playlist_url)
    else:
        raise ValueError("Link non supportato.")

    print(f"Elencando le canzoni di «{playlist.name}»...")
    tracks = playlist.fetch_tracks()

    def track_downloaded(position: int, track: SpotlessTrackInfo):
        print(
            f"({position + 1}/{len(tracks)})\tScaricato «{', '.join(track.artists)} - {track.name}»"
        )

    print(f"Scaricando {len(tracks)} canzoni...")
    downloader = YouTubeMusicDownloader(track_downloaded)

    threaded_downloader = ThreadedDownloader(downloader)
    threaded_downloader.download_tracks(playlist.name, tracks)
