from typing import Dict
from youtube_extractor.utils.format_classifier import (
    classify_audio_formats,
    classify_video_formats,
)


class ClassifyFormat(object):
    @staticmethod
    def get_video_formats(formats: Dict):
        return classify_video_formats(formats)

    @staticmethod
    def get_audio_formats(formats: Dict):
        return classify_audio_formats(formats)


ClassifyFormat.get_audio_formats.__doc__ = classify_audio_formats.__doc__
ClassifyFormat.get_video_formats.__doc__ = classify_video_formats.__doc__
