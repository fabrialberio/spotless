import threading
from dataclasses import dataclass

import yt_dlp

from src.id3 import add_track_info_to_file
from src.spotless import SpotlessDownloader, SpotlessTrackInfo


class _YouTubeLogger:
    def debug(self, msg: str): ...
    def info(self, msg: str): ...
    def warning(self, msg: str): ...
    def error(self, msg: str):
        print(msg)


@dataclass(frozen=True)
class YouTubeTrackInfo(SpotlessTrackInfo):
    video_id: str = ""


class YouTubeDownloader(SpotlessDownloader):
    """
    Allows to download tracks from YouTube.

    Uses `yt-dlp` to search for the track's name on YouTube and then downloads
    the corresponding video.
    """

    _position: int
    _tracks: list[SpotlessTrackInfo]

    def _track_downloaded(self, path: str):
        track = self._tracks[self._position]

        thread = threading.Thread(
            target=add_track_info_to_file,
            args=(track, path),
        )
        thread.start()

        self._position += 1

        if self.track_downloaded_cb is not None:
            self.track_downloaded_cb(self._position, track)

    def download_search_list(self, dirname: str, search_list: list[str]):
        ydl_opts = {
            "format": "mp3/bestaudio/best",
            "outtmpl": f"./{dirname}/%(title)s.%(ext)s",
            "logger": _YouTubeLogger(),
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                }
            ],
            "force-ipv4": True,
            # TODO: Age-restricted videos?
        }

        ydl = yt_dlp.YoutubeDL(ydl_opts)
        ydl.add_post_hook(self._track_downloaded)
        ydl.download(search_list)

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
            search_list = [
                f"ytsearch:{' '.join(t.artists)} {t.name}" for t in tracks
            ]

        self.download_search_list(dirname, search_list)
