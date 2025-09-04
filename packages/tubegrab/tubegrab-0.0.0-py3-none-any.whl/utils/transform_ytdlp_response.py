from youtube_extractor.dataclasses.YoutubeResponse import (
    Channel,
    Subtitle,
    Uploader,
    YouTubeResponse,
)


def transform_yt_dlp(response: dict) -> YouTubeResponse:
    """
    Transforms a yt-dlp response dictionary into a YouTubeResponse dataclass instance.
    """

    channel = Channel(
        id=response.get("channel_id", ""),
        name=response.get("channel", ""),
        follower_count=response.get("channel_follower_count"),
        is_verified=response.get("channel_is_verified", False),
    )

    uploader = Uploader(
        id=response.get("uploader_id"),
        name=response.get("uploader", ""),
        link=response.get("uploader_url"),
        date=response.get("upload_date"),
    )

    _subtitles = response.get("subtitles")

    return YouTubeResponse(
        id=response["id"],
        title=response["title"],
        description=response.get("description", ""),
        channel=channel,
        upload=uploader,
        duration=response.get("duration", 0),
        age_limit=response.get("age_limit", 0),
        view_count=response.get("view_count", 0),
        video_link=response.get("webpage_url", ""),
        thumbnail=response.get("thumbnail", ""),
        categories=response.get("categories", []),
        tags=response.get("tags", []),
        is_live=response.get("is_live", False),
        was_live=response.get("was_live", False),
        media_type=response.get("media_type", "video"),
        release_timestamp=response.get("release_timestamp"),
        timestamp=response.get("timestamp", 0),
        duration_string=response.get("duration_string", ""),
        comment_count=response.get("comment_count"),
        like_count=response.get("like_count"),
        availability=response.get("availability"),
        subtitles=(
            {k: [Subtitle(**vi) for vi in v] for k, v in _subtitles.items()}
            if _subtitles and isinstance(_subtitles, dict)
            else None
        ),
    )
