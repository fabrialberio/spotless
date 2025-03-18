import pathlib
import urllib.request

import mutagen.id3
from mutagen.id3._frames import APIC, TALB, TIT2, TOFN, TORY, TPE1, TPE2, TRCK

from spotless import SpotlessTrackInfo

ID3_SEPARATOR = "\u0000"


def add_track_info_to_file(info: SpotlessTrackInfo, path: str):
    file = mutagen.id3.ID3(path)

    file.add(TOFN(encoding=3, text=pathlib.Path(path).stem))
    file.add(TIT2(encoding=3, text=info.name))
    file.add(TPE1(encoding=3, text=ID3_SEPARATOR.join(info.artists)))
    file.add(TPE2(encoding=3, text=ID3_SEPARATOR.join(info.artists)))
    file.add(TALB(encoding=3, text=info.album_name))

    if info.track_number is not None:
        file.add(TRCK(encoding=3, text=str(info.track_number)))

    if info.release_date is not None:
        file.add(TORY(encoding=3, text=str(info.release_date.year)))

    if info.album_image_url is not None:
        with urllib.request.urlopen(info.album_image_url) as response:
            file.add(
                APIC(
                    mime="image/jpeg",
                    type=3,
                    desc="Cover",
                    data=response.read(),
                )
            )

    file.save()
