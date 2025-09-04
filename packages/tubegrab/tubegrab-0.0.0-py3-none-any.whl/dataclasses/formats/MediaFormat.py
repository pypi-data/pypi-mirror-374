from dataclasses import dataclass
from typing import Optional, Dict, Any, Literal, Union

from youtube_extractor.mixins import SerializableMixin


@dataclass
class MediaFormat(SerializableMixin.SerializableMixin):
    # Always present
    url: str
    format_id: str
    ext: Optional[
        Union[
            Literal[
                "mp4",
                "webm",
                "m4a",
                "mp3",
                "ogg",
                "mkv",
                "flv",
                "3gp",
                "wav",
                "aac",
                "ts",
            ],
            str,
        ]
    ]
    protocol: Union[
        Literal[
            "http",
            "https",
            "m3u8",
            "m3u8_native",
            "dash",
            "mss",
            "hls",
            "http_dash_segments",
            "rtmp",
            "ftp",
            "rtsp",
            "data",
            "mms",
        ],
        str,
    ]
    format: str

    # Common optional
    format_note: Optional[str] = None
    source_preference: Optional[int] = None
    quality: Optional[Union[int, float]] = None
    has_drm: Optional[bool] = None
    filesize: Optional[int] = None
    filesize_approx: Optional[int] = None
    container: Optional[str] = None
    available_at: Optional[int] = None  # Unix Timestamp
    downloader_options: Optional[Dict[str, Any]] = None
    http_headers: Optional[Dict[str, str]] = None
    language: Optional[str] = None
    language_preference: Optional[int] = None
    preference: Optional[int] = None

    acodec: Union[Literal["none"], str] = "none"  # usually "none" in video-only
    vcodec: Union[Literal["none"], str] = "none"  # usually "none" in audio-only
    audio_ext: Optional[str] = None
    video_ext: Optional[str] = None

    tbr: Optional[Union[int, float]] = None
    vbr: Optional[Union[int, float]] = None  # sometimes 0 in audio-only
    abr: Optional[Union[int, float]] = None  # audio bitrate, sometimes 0 in video
    resolution: Optional[Union[str, Literal["audio only"]]] = (
        None  # usually "audio only" in audio-only
    )
