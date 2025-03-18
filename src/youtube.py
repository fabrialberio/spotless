import threading
from typing import Optional, Self

import yt_dlp

from spotless import SpotlessDownloader, SpotlessTrackInfo
from src.id3 import add_track_info_to_file


class _SpotlessYTLogger:
    def debug(self, msg: str):
        if msg.startswith("[debug] "):
            return
        else:
            self.info(msg)

    def info(self, msg: str): ...

    def warning(self, msg: str): ...

    def error(self, msg: str):
        print(msg)


class SpotlessYTDownloader(SpotlessDownloader):
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
            "logger": _SpotlessYTLogger(),
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                }
            ],
        }

        ydl = yt_dlp.YoutubeDL(ydl_opts)
        ydl.add_post_hook(self._track_downloaded)
        ydl.download(
            [f"ytsearch:{' '.join(t.artists)} {t.name}" for t in tracks]
        )


class SpotlessThreadedDownloader(SpotlessDownloader):
    _position: int
    _downloader: SpotlessDownloader

    def __init__(self, downloader: SpotlessDownloader):
        self._downloader = downloader
        self.track_downloaded_cb = downloader.track_downloaded_cb

    def dup(self) -> Self:
        return self.__class__(self._downloader)

    def _track_downloaded(self, _: int, track: SpotlessTrackInfo):
        if self.track_downloaded_cb is not None:
            self.track_downloaded_cb(self._position, track)

        self._position += 1

    def download_tracks(
        self,
        dirname: str,
        tracks: list[SpotlessTrackInfo],
    ):
        self._position = 0
        total_threads = min(6, len(tracks) // 5)

        slice_lenght = (len(tracks) // total_threads) + 1

        for i in range(total_threads):
            current_slice = tracks[
                i * slice_lenght : min((i + 1) * slice_lenght, len(tracks))
            ]

            print(f"Starting thread {i + 1}/{total_threads}...")
            downloader = self._downloader.dup()

            thread = threading.Thread(
                target=downloader.download_tracks,
                args=(dirname, current_slice),
            )
            thread.start()
