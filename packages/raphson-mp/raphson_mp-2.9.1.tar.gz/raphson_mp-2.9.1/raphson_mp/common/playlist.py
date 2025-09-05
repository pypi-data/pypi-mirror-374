from dataclasses import dataclass
from typing import TypedDict


@dataclass(kw_only=True)
class PlaylistBase:
    name: str
    track_count: int


class PlaylistDict(TypedDict):
    name: str
    track_count: int
    favorite: bool
    write: bool
