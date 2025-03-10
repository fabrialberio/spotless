import spotipy

from typing import Iterator, Optional, Self
import datetime


class UnspotifyTrackInfo:
    name: str
    artist: str
    track_number: int
    disc_number: int
    album_name: str
    album_image_url: str
    release_date: Optional[datetime.date]

    def __init__(self, track: dict):
        self.name = track["name"]
        self.artist = track["artists"][0]["name"]  # TODO: Multiple artists?
        self.track_number = track["track_number"]
        self.disc_number = track["disc_number"]

        self.album_name = track["album"]["name"]

        max_album_image_size = 0
        album_images = track["album"]["images"]
        for image in album_images:
            if image["height"] > max_album_image_size:
                max_album_image_size = image["height"]
                self.album_image_url = image["url"]

        match track["album"]["release_date_precision"]:
            case "day":
                self.release_date = datetime.date.fromisoformat(
                    track["album"]["release_date"]
                )
            case "month":
                release_date_parts = track["album"]["release_date"].split("-")

                self.release_date = datetime.date(
                    int(release_date_parts[0]),
                    int(release_date_parts[1]) + 1,
                    1,
                )
            case "year":
                self.release_date = datetime.date(
                    int(track["album"]["release_date"]), 1, 1
                )
            case None:
                self.release_date = None
            case _ as p:
                raise ValueError(f"Unsupported precision «{p}»")


class UnspotifyPlaylist(Iterator):
    name: str
    _sp: spotipy.Spotify
    _playlist_id: str
    _current_pos: int
    _current_tracks: list[dict]

    def __init__(self, sp: spotipy.Spotify, playlist_id: str):
        self._sp = sp
        self._playlist_id = playlist_id

        self.name = sp.playlist(playlist_id, fields=["name"])["name"]  # type: ignore

        self._current_pos = 0
        self._current_tracks = []

    @classmethod
    def from_url(cls, sp: spotipy.Spotify, playlist_url: str) -> Self:
        return cls(sp, playlist_url.split("/")[-1].split("&")[0])

    def __iter__(self) -> Iterator[UnspotifyTrackInfo]:
        return self

    def __next__(self) -> UnspotifyTrackInfo:
        if self._current_pos % 100 == 0:
            tracks = self._sp.playlist_tracks(
                playlist_id=self._playlist_id,
                limit=100,
                offset=100 * (self._current_pos // 100),
            )
            assert tracks is not None

            self._current_tracks = tracks["items"]

        self._current_pos += 1

        if self._current_pos % 100 >= len(self._current_tracks):
            raise StopIteration

        return UnspotifyTrackInfo(
            self._current_tracks[self._current_pos % 100]["track"]
        )
