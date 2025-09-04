from dataclasses import dataclass, field
from typing import List, Optional

from youtube_extractor.dataclasses.formats.AudioFormat import AudioFormat
from youtube_extractor.dataclasses.formats.VideoFormat import VideoFormat
from youtube_extractor.mixins import SerializableMixin


@dataclass
class AudioFormatClassification(SerializableMixin.SerializableMixin):
    highest: Optional[AudioFormat]
    lowest: Optional[AudioFormat]
    items: List[AudioFormat] = field(default_factory=list)


@dataclass
class VideoFormatClassification(SerializableMixin.SerializableMixin):
    highest: Optional[VideoFormat]
    lowest: Optional[VideoFormat]
    items: List[VideoFormat] = field(default_factory=list)
