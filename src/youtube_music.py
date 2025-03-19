from typing import Callable, Optional, Self

import ytmusicapi.ytmusic

from src.spotless import SpotlessPlaylist, SpotlessTrackInfo
from src.youtube import YouTubeDownloader, YouTubeTrackInfo


class YouTubeMusicPlaylist(SpotlessPlaylist):
    """
    Allows to get a list of tracks from a YouTube Music playlist using
    `ytmusicapi`.
    """

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
        return cls(playlist_url.split("/")[-1].split("&")[0].split("=")[-1])

    def _construct_track(self, track: dict) -> SpotlessTrackInfo:
        album_image_url = None
        max_album_image_size = 0
        thumbnails = self._ytm.get_album(track["album"]["id"])["thumbnails"]
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


class YouTubeMusicDownloader(YouTubeDownloader):
    """
    Allows to download tracks from YouTube Music using `ytmusicapi` and `yt-dlp`.

    Uses `ytmusicapi` to search for the track's name on YouTube Music and then
    uses `yt-dlp` to download the corresponding video.

    This downloader has more accurate results compared to `YouTubeDownloader`,
    but it takes more time to search the tracks.
    """

    _ytm: ytmusicapi.YTMusic

    def __init__(
        self,
        track_downloaded_cb: Optional[
            Callable[[int, SpotlessTrackInfo], None]
        ] = None,
    ):
        super().__init__(track_downloaded_cb)
        self._ytm = ytmusicapi.YTMusic()

    def download_tracks(
        self,
        dirname: str,
        tracks: list[SpotlessTrackInfo],
    ):
        self._position = 0
        self._tracks = tracks

        search_list = []
        if isinstance(tracks[0], YouTubeTrackInfo):
            for t in tracks:
                assert isinstance(t, YouTubeTrackInfo)
                search_list.append(t.video_id)
        else:
            for t in tracks:
                results = self._ytm.search(
                    f"{' '.join(t.artists)} {t.name}",
                    filter="songs",
                    limit=1,
                    ignore_spelling=True,
                )

                if len(results) == 0:
                    results = self._ytm.search(
                        f"{' '.join(t.artists)} {t.name}",
                        filter="songs",
                        limit=1,
                    )

                if len(results) == 0:
                    print(
                        f"Ricerca di «{', '.join(t.artists)} - {t.name}» fallita."
                    )
                    break

                search_list.append(results[0]["videoId"])

        self.download_search_list(dirname, search_list)
