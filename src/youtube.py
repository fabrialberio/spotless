import threading
from dataclasses import dataclass

import yt_dlp

from spotless import SpotlessDownloader, SpotlessTrackInfo
from src.id3 import add_track_info_to_file


class _YouTubeLogger:
    def debug(self, msg: str):
        if msg.startswith("[debug] "):
            return
        else:
            self.info(msg)

    def info(self, msg: str): ...

    def warning(self, msg: str): ...

    def error(self, msg: str):
        print(msg)


@dataclass(frozen=True)
class YouTubeTrackInfo(SpotlessTrackInfo):
    video_id: str = ""


class YouTubeDownloader(SpotlessDownloader):
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

    def download_tracks(
        self,
        dirname: str,
        tracks: list[SpotlessTrackInfo],
    ):
        self._position = 0
        self._tracks = tracks

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
        }

        ydl = yt_dlp.YoutubeDL(ydl_opts)
        ydl.add_post_hook(self._track_downloaded)

        search_list = []

        if isinstance(tracks[0], YouTubeTrackInfo):
            for t in tracks:
                assert isinstance(t, YouTubeTrackInfo)
                search_list.append(t.video_id)
        else:
            search_list = [
                f"ytsearch:{' '.join(t.artists)} {t.name}" for t in tracks
            ]

        ydl.download(search_list)
