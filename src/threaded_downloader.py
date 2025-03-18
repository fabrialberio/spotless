import threading

from src.spotless import SpotlessDownloader, SpotlessTrackInfo


class ThreadedDownloader(SpotlessDownloader):
    _position: int
    _downloader_class: type[SpotlessDownloader]
    _max_threads: int

    def __init__(self, downloader: SpotlessDownloader, max_threads=6):
        self._downloader_class = downloader.__class__
        self.track_downloaded_cb = downloader.track_downloaded_cb
        self._max_threads = max_threads

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
        total_threads = min(self._max_threads, len(tracks) // 5)

        slice_lenght = (len(tracks) // total_threads) + 1

        for i in range(total_threads):
            current_slice = tracks[
                i * slice_lenght : min((i + 1) * slice_lenght, len(tracks))
            ]

            downloader = self._downloader_class(self._track_downloaded)

            thread = threading.Thread(
                target=downloader.download_tracks,
                args=(dirname, current_slice),
            )
            thread.start()
