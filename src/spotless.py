import datetime
from dataclasses import dataclass
from typing import Callable, Optional, Protocol


@dataclass(frozen=True)
class SpotlessTrackInfo:
    """
    Structure containing information about a track.
    """

    name: str
    artists: list[str]
    album_name: str
    track_number: Optional[int] = None
    release_date: Optional[datetime.date] = None
    album_image_url: Optional[str] = None


class SpotlessPlaylist:
    """
    Base class for allowing to get a list of tracks from a playlist.
    """

    name: str

    def fetch_tracks(self) -> list[SpotlessTrackInfo]: ...


type _TrackDownloadedCb = Callable[[int, SpotlessTrackInfo], None]


class SpotlessDownloader(Protocol):
    """
    Base class for allowing to download tracks.
    """

    track_downloaded_cb: Optional[_TrackDownloadedCb]

    def __init__(
        self,
        track_downloaded_cb: Optional[_TrackDownloadedCb] = None,
    ):
        self.track_downloaded_cb = track_downloaded_cb

    def download_tracks(
        self,
        dirname: str,
        tracks: list[SpotlessTrackInfo],
    ): ...
