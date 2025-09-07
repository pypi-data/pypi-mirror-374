import os
import re
from typing import Optional

import requests

from tikorgzo.constants import DOWNLOAD_PATH
from tikorgzo.exceptions import InvalidVideoLink, VideoFileAlreadyExistsError, VideoIDExtractionError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tikorgzo.core.video.model import Video
    # If doing this directly, this causes circular import so the alternative is
    # to forward reference the VideoInfo of the _process_output_paths() for
    # type hinting so that we don't need direct import of this class

USERNAME_REGEX = r"\/@([\w\.\-]+)\/video\/\d+"
NORMAL_TIKTOK_VIDEO_LINK_REGEX = r"(https?://)?(www\.)?tiktok\.com/@[\w\.\-]+/video/\d+(\?.*)?$"
VT_TIKTOK_VIDEO_LINK_REGEX = r"(https?://)?vt\.tiktok\.com/"


class VideoInfoProcessor:
    def validate_video_link(self, video_link: str):
        """Checks if the video link is a valid TikTok video link or a valid video ID."""

        if re.search(NORMAL_TIKTOK_VIDEO_LINK_REGEX, video_link):
            return video_link

        elif re.search(VT_TIKTOK_VIDEO_LINK_REGEX, video_link):
            video_link = self._get_normalized_url(video_link)
            return video_link

        elif len(video_link) == 19 and video_link.isdigit():
            return video_link

        raise InvalidVideoLink(video_link)

    def extract_video_id(self, video_link: str) -> int:
        """Extracts the video ID which is a 19-digit long that uniquely identifies a TikTok video."""
        match = re.search(r'/video/(\d+)', video_link)
        if match:
            return int(match.group(1))

        elif len(video_link) == 19 and video_link.isdigit():
            return int(video_link)

        match = re.search(r'/(\d+)_original\.mp4', video_link)
        if match:
            return int(match.group(1))

        raise VideoIDExtractionError()

    def check_if_already_downloaded(self, filename: str):
        """Recursively checks the output folder, which is the default DOWNLOAD_PATH,
        to see if a file (where the filename is a video ID) already exists. If true,
        this will raise an error."""

        filename += ".mp4"

        for root, _, filenames in os.walk(DOWNLOAD_PATH):
            for f in filenames:
                if f == filename:
                    username = os.path.basename(root)
                    raise VideoFileAlreadyExistsError(filename, username)

    def process_output_paths(self, video: "Video") -> None:
        """Determines and creates the output directory and file path for the video.
        If the video has been downloaded already, this will raise an error."""

        username = video._username
        video_id = video._video_id

        assert isinstance(video_id, int)

        video_filename = str(video_id) + ".mp4"

        if username is not None:
            output_path = os.path.join(DOWNLOAD_PATH, username)
            os.makedirs(output_path, exist_ok=True)
            video_file = os.path.join(output_path, video_filename)

            if os.path.exists(video_file):
                raise VideoFileAlreadyExistsError(video_filename, username)

            video._output_file_dir = output_path
            video._output_file_path = video_file

    def _get_normalized_url(self, video_link):
        """Returns a normalized URL whenever the inputted video link doesn't contain the username and the video ID
        (e.g., https://vt.tiktok.com/AbCdEfGhI).

        This is needed so that we can extract the username and the video ID when the normalized URL is extracted, which
        are both needed so that when we have downloaded the video, they will be saved in the Downloads folder in which they
        are grouped by username and the filename will be the video ID."""

        if not video_link.startswith(r"https://") and not video_link.startswith(r"http://"):
            video_link = "https://" + video_link

        response = requests.get(video_link, allow_redirects=True)
        return response.url

    def _process_username(self, video_link: str) -> Optional[str]:
        """Some video links include username so this method processes those links
        and extracts the username from it.

        If nothing can be extracted, this returns None
        """
        match = re.search(USERNAME_REGEX, video_link)

        if match:
            return match.group(1)
        else:
            return None
