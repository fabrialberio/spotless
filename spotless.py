import datetime
import pathlib
import urllib.request
from dataclasses import dataclass
from typing import Iterator, Optional, Self

import mutagen.id3
import spotipy
from mutagen.id3._frames import APIC, TALB, TIT2, TOFN, TORY, TPE1, TPE2, TRCK


@dataclass(frozen=True)
class SpotlessTrackInfo:
    name: str
    artist: str
    track_number: int
    disc_number: int
    album_name: str
    album_image_url: Optional[str]
    release_date: Optional[datetime.date]

    @classmethod
    def from_spotify_track(cls, track: dict) -> Self:
        album_image_url = None
        max_album_image_size = 0
        album_images = track["album"]["images"]
        for image in album_images:
            if image["height"] > max_album_image_size:
                max_album_image_size = image["height"]
                album_image_url = image["url"]

        release_date = None
        match track["album"]["release_date_precision"]:
            case "day":
                release_date = datetime.date.fromisoformat(
                    track["album"]["release_date"]
                )
            case "month":
                release_date_parts = track["album"]["release_date"].split("-")

                release_date = datetime.date(
                    int(release_date_parts[0]),
                    int(release_date_parts[1]) + 1,
                    1,
                )
            case "year":
                release_date = datetime.date(
                    int(track["album"]["release_date"]), 1, 1
                )
            case None:
                release_date = None
            case _ as p:
                raise ValueError(f"Unsupported precision «{p}»")

        return cls(
            name=track["name"],
            artist=track["artists"][0]["name"],  # TODO: Multiple artists?
            track_number=track["track_number"],
            disc_number=track["disc_number"],
            album_name=track["album"]["name"],
            album_image_url=album_image_url,
            release_date=release_date,
        )

    def add_to_file(self, path: str):
        file = mutagen.id3.ID3(path)

        file.add(TOFN(encoding=3, text=pathlib.Path(path).stem))
        file.add(TIT2(encoding=3, text=self.name))
        file.add(TPE1(encoding=3, text=self.artist))
        file.add(TPE2(encoding=3, text=self.artist))
        file.add(TRCK(encoding=3, text=str(self.track_number)))
        file.add(TALB(encoding=3, text=self.album_name))

        if self.release_date is not None:
            file.add(TORY(encoding=3, text=str(self.release_date.year)))

        if self.album_image_url is not None:
            with urllib.request.urlopen(self.album_image_url) as response:
                file.add(
                    APIC(
                        mime="image/jpeg",
                        type=3,
                        desc="Cover",
                        data=response.read(),
                    )
                )

        file.save()

        # rename(
        #    path, pathlib.Path(path).with_stem((f"{self.artist} - {self.name}"))
        # )


class SpotlessPlaylist(Iterator):
    name: str
    _sp: spotipy.Spotify
    _playlist_id: str
    _position: int
    _current_tracks: list[dict]

    def __init__(self, sp: spotipy.Spotify, playlist_id: str):
        self._sp = sp
        self._playlist_id = playlist_id

        self.name = sp.playlist(playlist_id, fields=["name"])["name"]  # type: ignore

        self._position = 0
        self._current_tracks = []

    @classmethod
    def from_url(cls, sp: spotipy.Spotify, playlist_url: str) -> Self:
        return cls(sp, playlist_url.split("/")[-1].split("&")[0])

    def __iter__(self) -> Iterator[SpotlessTrackInfo]:
        return self

    def __next__(self) -> SpotlessTrackInfo:
        if self._position % 100 == 0:
            tracks = self._sp.playlist_tracks(
                playlist_id=self._playlist_id,
                limit=100,
                offset=100 * (self._position // 100),
            )
            assert tracks is not None

            self._current_tracks = tracks["items"]

        self._position += 1

        if self._position % 100 >= len(self._current_tracks):
            raise StopIteration

        return SpotlessTrackInfo.from_spotify_track(
            self._current_tracks[self._position % 100]["track"]
        )
