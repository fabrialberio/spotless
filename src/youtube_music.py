from typing import Self

import ytmusicapi
import ytmusicapi.ytmusic

from src.spotless import SpotlessPlaylist, SpotlessTrackInfo
from src.youtube import YouTubeTrackInfo


class YouTubeMusicPlaylist(SpotlessPlaylist):
    _ytm: ytmusicapi.YTMusic
    _playlist_id: str

    def __init__(self, playlist_id: str) -> None:
        self._ytm = ytmusicapi.YTMusic()
        self._playlist_id = playlist_id

        self.name = self._ytm.get_playlist(playlist_id, limit=0)["title"]

        self._position = 0
        self._current_tracks = []

    @classmethod
    def from_url(cls, playlist_url: str) -> Self:
        return cls(playlist_url.split("/")[-1])

    def _construct_track(self, track: dict) -> SpotlessTrackInfo:
        album_image_url = None
        max_album_image_size = 0
        thumbnails = track["thumbnails"]
        for image in thumbnails:
            if image["height"] > max_album_image_size:
                max_album_image_size = image["height"]
                album_image_url = image["url"]

        return YouTubeTrackInfo(
            video_id=track["videoId"],
            name=track["title"],
            artists=[artist["name"] for artist in track["artists"]],
            album_name=track["album"]["name"],
            album_image_url=album_image_url,
        )

    def fetch_tracks(self) -> list[SpotlessTrackInfo]:
        playlist = self._ytm.get_playlist(
            playlistId=self._playlist_id,
            limit=None,
        )

        return [self._construct_track(t) for t in playlist["tracks"]]
