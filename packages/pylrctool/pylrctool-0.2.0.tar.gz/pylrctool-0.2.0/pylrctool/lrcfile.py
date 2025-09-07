from __future__ import annotations

from collections.abc import Iterable
from datetime import timedelta
from pathlib import Path
from zlib import crc32

import pendulum
import srt
from sortedcontainers import SortedKeyList

from .lrcevent import LRCEvent


class LRCFile(SortedKeyList):
    def __init__(self, iterable: Iterable[LRCEvent] | None = None):
        super().__init__(key=lambda event: event.time or pendulum.duration())
        for event in iterable or []:
            self.add(event)

    @property
    def id(self) -> str:
        """Compute an ID from the LRC data."""
        checksum = crc32("\n".join([event.id for event in self]).encode("utf8"))

        return hex(checksum)

    def add(self, value: LRCEvent) -> None:
        """
        Add an LRCEvent to the file, ensuring no duplicates.
        :param value: LRCEvent to add.
        :raises TypeError: If the value is not an LRCEvent.
        :return: None
        """
        if not isinstance(value, LRCEvent):
            raise TypeError(f"Can only add LRCEvent objects, not {type(value)}")

        if any((ev == value) for ev in self):
            return

        super().add(value)

    def dump_to_srt(self, path: Path | str) -> int:
        """
        Export LRC Data to SRT file.
        :param path: Path to save the SRT file.
        :return: Number of characters written to the file.
        """
        if isinstance(path, str):
            path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        srt_data = []
        data_len = len(self)
        index = 1
        for event in self:
            if not event.is_lyric:
                index += 1
                continue

            start = timedelta(seconds=event.time.total_seconds())

            repeat_time_end = None
            if event.repeat_time:
                repeat_time_end = timedelta(seconds=event.repeat_time.total_seconds())

            if index < data_len:
                end = timedelta(seconds=self[index].time.total_seconds())
            else:
                end = start + timedelta(seconds=5)

            srt_line = srt.Subtitle(
                index=index + 1,
                content=event.data,
                start=start,
                end=repeat_time_end or end,
            )

            srt_data.append(srt_line)

            if repeat_time_end:
                srt_line.start = repeat_time_end
                srt_line.end = end
                srt_line.end = end
                index += 1
                srt_line.index = index
                srt_data.append(srt_line)

            index += 1

        return path.write_text(srt.compose(srt_data), encoding="utf8")

    def dumps(self, data_only: bool = False) -> str:
        """
        Serialize the LRC data to a string.
        :return: Serialized LRC data as a string.
        """

        if data_only:
            lines = [
                event.data
                for event in self
                if event.is_lyric
                for _ in (1, 2)
                if (_ == 1 or event.repeat_time) and event.data
            ]
            return "\n".join(lines)
        return "\n".join(event.compose for event in self)

    def dump(self, path: Path | str, data_only: bool = False) -> int:
        """
        Save the LRC data to a file.
        :param path: Path to save the LRC file.
        :return: Number of characters written to the file.
        """
        if isinstance(path, str):
            path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        lrc_text = self.dumps(data_only)

        return path.write_text(lrc_text, encoding="utf8")

    def from_string(self, data: str) -> bool:
        """
        Load LRC data from a file.
        :param data: LRC data.
        :return: True if anything was added
        """
        for line in data.splitlines():
            if line:
                if event := LRCEvent.from_string(line.strip()):
                    self.add(event)

        return bool(self)

    def from_file(self, path: Path | str) -> bool:
        """
        Load LRC data from lrc file.
        :param path: Path of the LRC file.
        :return: True if anything was added
        """
        if isinstance(path, str):
            path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"LRC file not found: {path}")

        with path.open("r", encoding="utf8") as file:
            for line in file:
                if event := LRCEvent.from_string(line.strip()):
                    self.add(event)

        return bool(self)

    def from_srt(self, path: Path | str) -> bool:
        """
        Load LRC data from srt file.
        :param path: Path of the SRT file.
        :return: True if anything was added
        """
        if isinstance(path, str):
            path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"SRT file not found: {path}")

        for line in srt.parse(path.read_text()):
            self.add(
                LRCEvent(
                    time=pendulum.duration(
                        seconds=line.start.total_seconds(),
                    ),
                    data=line.content,
                )
            )

        return bool(self)

    def merge_lines(self) -> bool:
        """
        Merge 2 repeating lines leveraging repeat_time.
        :return: True if there was any merge
        """
        merged = False
        i = 1
        for event in self:
            if event.is_lyric:
                if i < len(self) and event.data == self[i].data:
                    event.repeat_time = self[i].time
                    merged = True
                    del self[i]
                i += 1

        return merged

    def shift(self, minutes: int = 0, seconds: int = 0, milliseconds: int = 0) -> None:
        """Shift line by the set time
        :param minutes: Minutes to shift.
        :param seconds: Seconds to shift.
        :param milliseconds: Milliseconds to shift.
        :return: None
        """

        shift_time = pendulum.duration(
            minutes=minutes, seconds=seconds, milliseconds=milliseconds
        )

        for event in self:
            event.time += shift_time

    def __repr__(self) -> str:
        return f"LRCFile({list(self)})"
