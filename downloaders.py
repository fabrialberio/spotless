import threading
from typing import Callable, Protocol

import yt_dlp

from unspotify import UnspotifyTrackInfo


class UnspotifyDownloader(Protocol):
    def download_tracks(
        self,
        dirname: str,
        tracks: list[UnspotifyTrackInfo],
        download_completed_cb: Callable[[], None],
    ): ...


class _UnspotifyYTLogger:
    def debug(self, msg: str):
        if msg.startswith("[debug] "):
            return
        else:
            self.info(msg)

    def info(self, msg: str): ...

    def warning(self, msg: str): ...

    def error(self, msg: str):
        print(msg)


class UnspotifyYTDownloader(UnspotifyDownloader):
    _current_pos: int
    _current_tracks: list[UnspotifyTrackInfo]
    _download_completed_cb: Callable[[], None]

    def _track_downloaded(self, path: str):
        print(f"Downloaded «{self._current_tracks[self._current_pos].name}»...")

        thread = threading.Thread(
            target=self._current_tracks[self._current_pos].add_to_file,
            args=(path,),
        )
        thread.start()

        self._current_pos += 1

        if self._current_pos == len(self._current_tracks):
            self._download_completed_cb()

    def download_tracks(
        self,
        dirname: str,
        tracks: list[UnspotifyTrackInfo],
        download_completed_cb: Callable[[], None],
    ):
        self._current_pos = 0
        self._current_tracks = tracks
        self._download_completed_cb = download_completed_cb

        ydl_opts = {
            "format": "mp3/bestaudio/best",
            "outtmpl": f"./{dirname}/%(title)s.%(ext)s",
            "logger": _UnspotifyYTLogger(),
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


class UnspotifyThreadedDownloader(UnspotifyDownloader):
    _total_threads: int
    _completed_threads: int
    _download_completed_cb: Callable[[], None]

    def _thread_completed_cb(self):
        self._completed_threads += 1

        if self._completed_threads == self._total_threads:
            self._download_completed_cb()

    def download_tracks(
        self,
        dirname: str,
        tracks: list[UnspotifyTrackInfo],
        download_completed_cb: Callable[[], None],
    ):
        self._total_threads = min(6, len(tracks) // 5)
        self._completed_threads = 0
        self._download_completed_cb = download_completed_cb

        slice_lenght = (len(tracks) // self._total_threads) + 1

        for i in range(self._total_threads):
            current_slice = tracks[
                i * slice_lenght : min((i + 1) * slice_lenght, len(tracks))
            ]

            print(f"Starting thread {i + 1}/{self._total_threads}...")
            downloader = UnspotifyYTDownloader()

            thread = threading.Thread(
                target=downloader.download_tracks,
                args=(dirname, current_slice, self._thread_completed_cb),
            )
            thread.start()
