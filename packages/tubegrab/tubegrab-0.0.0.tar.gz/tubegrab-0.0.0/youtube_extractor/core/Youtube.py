from typing import Dict, Optional
from yt_dlp import YoutubeDL

from youtube_extractor.utils.ClassifyFormat import ClassifyFormat
from youtube_extractor.utils.transform_ytdlp_response import transform_yt_dlp


class YouTube(YoutubeDL):
    def __init__(self, url: Optional[str] = None, params=None, auto_init=True):
        super().__init__(params, auto_init)
        self.extracted_info: Dict | None = None
        self.__url = url

    def extract_info(
        self,
        url: Optional[str] = None,
        download=False,
        ie_key=None,
        extra_info=None,
        process=True,
        force_generic_extractor=False,
    ):
        _url = url if url else self.__url

        if not _url:
            raise Exception("Please provide valid url.")

        info = super().extract_info(
            _url,
            download,
            ie_key,
            extra_info,
            process,
            force_generic_extractor,
        )
        self.extracted_info = info
        return info

    def audio_formats(self):
        if not self.extracted_info or "formats" not in self.extracted_info:
            raise Exception("Please call 'extract_info' method first.")

        return ClassifyFormat.get_audio_formats(self.extracted_info["formats"])

    def video_formats(self):
        if not self.extracted_info or "formats" not in self.extracted_info:
            raise Exception("Please call 'extract_info' method first.")

        return ClassifyFormat.get_video_formats(self.extracted_info["formats"])

    def video_data(self):
        if not self.extracted_info:
            raise Exception("Please call 'extract_info' method first.")

        return transform_yt_dlp(self.extracted_info)
