from typing import Dict

from youtube_extractor.dataclasses.formats.VideoFormat import VideoFormat
from youtube_extractor.dataclasses.format_classification import VideoFormatClassification


def classify_video_formats(formats: Dict) -> VideoFormatClassification:
    """
    Classifies video formats into best, lowest, ranked list, and non-video formats.

    Returns:
    {
        "best_video": {},
        "lowest_video": {},
        "videos": [{}],
    }
    """

    def is_valid_video_file(fmt):
        # Must have actual video content and not be a streaming manifest
        has_video = fmt.get("video_ext") not in [None, "none"]
        is_streaming = fmt.get("protocol") == "m3u8_native" or fmt.get(
            "url", ""
        ).endswith(".m3u8")
        return has_video and not is_streaming

    def get_video_quality_key(fmt):
        # Prioritize resolution, fallback to bitrate
        resolution = fmt.get("height") or 0
        bitrate = fmt.get("tbr") or 0
        fps = fmt.get("fps") or 0
        return (resolution, bitrate, fps)

    video_formats = [f for f in formats if is_valid_video_file(f)]
    # non_video_formats = [f for f in formats if not is_valid_video_file(f)]

    video_formats_sorted = sorted(
        video_formats,
        key=get_video_quality_key,
        reverse=True,
    )

    best_video = video_formats_sorted[0] if video_formats_sorted else None
    lowest_video = (
        video_formats_sorted[-1] if len(video_formats_sorted) > 1 else best_video
    )

    data_classes = VideoFormatClassification(
        highest=VideoFormat.from_json(best_video) if best_video else None,
        lowest=VideoFormat.from_json(lowest_video) if lowest_video else None,
        items=[VideoFormat.from_json(f) for f in video_formats_sorted],
    )
    return data_classes
