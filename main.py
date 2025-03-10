import spotipy
from spotipy.oauth2 import SpotifyOAuth

from unspotify import UnspotifyPlaylist, UnspotifyYTDownloader

if __name__ == "__main__":
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=""))

    playlist_url = input("Insert link to the playlist you want to download: ")
    playlist = UnspotifyPlaylist.from_url(sp, playlist_url)

    downloader = UnspotifyYTDownloader()
    downloader.download_playlist(playlist)
