import threading
from typing import Callable, Protocol

import yt_dlp
from spotless import SpotlessTrackInfo


class SpotlessDownloader(Protocol):
    def download_tracks(
        self,
        dirname: str,
        tracks: list[SpotlessTrackInfo],
        track_downloaded_cb: Callable[[int, SpotlessTrackInfo], None],
    ): ...


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
    _track_downloaded_cb: Callable[[int, SpotlessTrackInfo], None]

    def _track_downloaded(self, path: str):
        track = self._tracks[self._position]

        thread = threading.Thread(
            target=track.add_to_file,
            args=(path,),
        )
        thread.start()

        self._position += 1
        self._track_downloaded_cb(self._position, track)

    def download_tracks(
        self,
        dirname: str,
        tracks: list[SpotlessTrackInfo],
        track_downloaded_cb: Callable[[int, SpotlessTrackInfo], None],
    ):
        self._position = 0
        self._tracks = tracks
        self._track_downloaded_cb = track_downloaded_cb

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
        ydl.download([f"ytsearch:{t.artist} {t.name}" for t in tracks])


class SpotlessThreadedDownloader(SpotlessDownloader):
    _position: int
    _track_downloaded_cb: Callable[[int, SpotlessTrackInfo], None]

    def track_downloaded(self, _: int, track: SpotlessTrackInfo):
        self._track_downloaded_cb(self._position, track)
        self._position += 1

    def download_tracks(
        self,
        dirname: str,
        tracks: list[SpotlessTrackInfo],
        track_downloaded_cb: Callable[[int, SpotlessTrackInfo], None],
    ):
        self._position = 0
        self._track_downloaded_cb = track_downloaded_cb

        total_threads = min(6, len(tracks) // 5)

        slice_lenght = (len(tracks) // total_threads) + 1

        for i in range(total_threads):
            current_slice = tracks[
                i * slice_lenght : min((i + 1) * slice_lenght, len(tracks))
            ]

            print(f"Starting thread {i + 1}/{total_threads}...")
            downloader = SpotlessYTDownloader()

            thread = threading.Thread(
                target=downloader.download_tracks,
                args=(dirname, current_slice, self.track_downloaded),
            )
            thread.start()
