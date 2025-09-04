import re
from urllib.parse import urlparse, parse_qs


def extract_youtube_id(url: str) -> str | None:
    """
    Extracts the YouTube video ID from different types of YouTube URLs.

    Supported formats:
    - https://www.youtube.com/watch?v=VIDEOID
    - https://youtu.be/VIDEOID
    - https://www.youtube.com/embed/VIDEOID
    - https://www.youtube.com/shorts/VIDEOID
    - https://youtube.com/v/VIDEOID
    """

    parsed_url = urlparse(url)

    if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
        if parsed_url.path == "/watch":
            return parse_qs(parsed_url.query).get("v", [None])[0]

        regex_match = re.match(r"^/(embed|v|shorts)/([^/?]+)", parsed_url.path)
        if regex_match:
            return regex_match.group(2)

    if parsed_url.hostname == "youtu.be":
        return parsed_url.path.lstrip("/")

    return None


if __name__ == "__main__":
    urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://www.youtube.com/embed/dQw4w9WgXcQ",
        "https://youtube.com/v/dQw4w9WgXcQ",
        "https://www.youtube.com/shorts/dQw4w9WgXcQ",
    ]

    for u in urls:
        print(u, "->", extract_youtube_id(u))
