import threading
from typing import Self

from spotless import SpotlessDownloader, SpotlessTrackInfo


class ThreadedDownloader(SpotlessDownloader):
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
