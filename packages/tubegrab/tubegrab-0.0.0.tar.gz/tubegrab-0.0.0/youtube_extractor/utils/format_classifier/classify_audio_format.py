from typing import Dict
from youtube_extractor.dataclasses.formats.AudioFormat import AudioFormat
from youtube_extractor.dataclasses.format_classification import (
    AudioFormatClassification,
)


def classify_audio_formats(formats: Dict) -> AudioFormatClassification:
    """
    Classifies audio formats into best, lowest, sorted list of audios, and those without audio.

    Returns a dictionary:
    {
        'best_audio': {...},
        'lowest_audio': {...},
        'audios': [{}, {}, ...],
    }
    """

    def is_audio_format(fmt):
        has_audio = fmt.get("audio_ext") not in [None, "none"]
        is_streaming = fmt.get("protocol") == "m3u8_native" or fmt.get(
            "url", ""
        ).endswith(".m3u8")
        return has_audio and not is_streaming

    def get_audio_quality_key(fmt):
        # Use available audio bitrate or fallback to filesize if bitrate is unavailable
        return fmt.get("abr") or fmt.get("tbr") or fmt.get("filesize") or 0

    audio_formats = [f for f in formats if is_audio_format(f)]
    # non_audio_formats = [f for f in formats if not is_audio_format(f)]

    # Sort audio formats by quality descending
    audio_formats_sorted = sorted(
        audio_formats,
        key=get_audio_quality_key,
        reverse=True,
    )

    best_audio = audio_formats_sorted[0] if audio_formats_sorted else None
    lowest_audio = (
        audio_formats_sorted[-1] if len(audio_formats_sorted) > 1 else best_audio
    )

    data_classes = AudioFormatClassification(
        highest=AudioFormat.from_json(best_audio) if best_audio else None,
        lowest=AudioFormat.from_json(lowest_audio) if lowest_audio else None,
        items=[AudioFormat.from_json(f) for f in audio_formats_sorted],
    )
    return data_classes
