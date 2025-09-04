from dataclasses import dataclass
from typing import Optional, Literal, Union
from .MediaFormat import MediaFormat


@dataclass
class VideoFormat(MediaFormat):
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[float] = None
    dynamic_range: Optional[
        Union[Literal["SDR", "HDR10", "HLG", "DV", "Dolby Vision", "HDR"], str]
    ] = None
    aspect_ratio: Optional[float] = None
