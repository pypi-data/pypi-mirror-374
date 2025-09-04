from dataclasses import dataclass, field
from typing import List, Literal, Optional, TypedDict, Union

from youtube_extractor.mixins import SerializableMixin


class Subtitle(TypedDict):
    ext: Union[
        Literal[
            "vtt",
            "srt",
            "ttml",
            "srv3",
            "srv2",
            "srv1",
            "json3",
            "json2",
            "json1",
            "dfxp",
            "lrc",
            "sami",
        ],
        str,
    ]
    url: str
    name: Optional[str]
    lang: Optional[str]
    is_auto_generated: bool
    impersonated: bool


@dataclass
class Channel(SerializableMixin.SerializableMixin):
    id: str
    name: str
    link: str = field(init=False)
    follower_count: Optional[int]
    is_verified: bool

    def __post_init__(self):
        self.link = f"https://www.youtube.com/channel/{self.id}"


@dataclass
class Uploader(SerializableMixin.SerializableMixin):
    id: Optional[str]
    name: str
    link: Optional[str]
    date: Optional[str]


@dataclass
class YouTubeResponse(SerializableMixin.SerializableMixin):
    id: str
    title: str
    link: str = field(init=False)
    description: str
    channel: Channel
    upload: Uploader
    duration: int
    duration_string: str
    view_count: int
    age_limit: int
    video_link: str
    thumbnail: str
    categories: List[str]
    tags: List[str]
    is_live: bool
    was_live: bool
    media_type: str
    release_timestamp: Optional[int]
    timestamp: int
    subtitles: Optional[dict[str, List[Subtitle]]]
    comment_count: Optional[int]
    like_count: Optional[int]
    availability: Optional[str]

    def __post_init__(self):
        self.link = f"https://www.youtube.com/watch?v={self.id}"
