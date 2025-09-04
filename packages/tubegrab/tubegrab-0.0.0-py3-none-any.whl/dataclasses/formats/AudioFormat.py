from dataclasses import dataclass
from typing import Optional
from youtube_extractor.dataclasses.formats.MediaFormat import MediaFormat


@dataclass
class AudioFormat(MediaFormat):
    asr: Optional[int] = None  # audio sampling rate
    audio_channels: Optional[int] = None
