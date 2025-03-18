import datetime
from dataclasses import dataclass
from typing import Callable, Iterator, Optional, Protocol, Self


@dataclass(frozen=True)
class SpotlessTrackInfo:
    name: str
    artists: list[str]
    track_number: int
    disc_number: int
    album_name: str
    album_image_url: Optional[str]
    release_date: Optional[datetime.date]


class SpotlessPlaylist(Iterator):
    name: str

    def __iter__(self) -> Iterator[SpotlessTrackInfo]:
        return self

    def __next__(self) -> SpotlessTrackInfo: ...


type _TrackDownloadedCb = Callable[[int, SpotlessTrackInfo], None]


class SpotlessDownloader(Protocol):
    track_downloaded_cb: Optional[_TrackDownloadedCb]

    def __init__(
        self,
        track_downloaded_cb: Optional[_TrackDownloadedCb] = None,
    ):
        self.track_downloaded_cb = track_downloaded_cb

    def dup(self) -> Self:
        return self.__class__(self.track_downloaded_cb)

    def download_tracks(
        self,
        dirname: str,
        tracks: list[SpotlessTrackInfo],
    ): ...
