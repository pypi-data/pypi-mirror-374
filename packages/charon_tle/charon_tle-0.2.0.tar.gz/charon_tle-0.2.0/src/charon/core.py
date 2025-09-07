"""Core functionality for Charon TLE processor."""

import re
from typing import List, Optional, Set, Tuple
from urllib.parse import urljoin

import requests


class CharonTLE:
    """Main class for handling TLE data from CelesTrak."""

    BASE_URL = "https://celestrak.org/NORAD/elements/gp.php"

    # 预定义的常用星座
    CONSTELLATIONS = {
        "starlink": "starlink",
        "oneweb": "oneweb",
        "iridium": "iridium",
        "globalstar": "globalstar",
    }

    def __init__(self, timeout: int = 30):
        """Initialize CharonTLE.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
            }
        )

    def download_tle(self, group: str, custom_url: Optional[str] = None) -> str:
        """Download TLE data from CelesTrak.

        Args:
            group: Constellation group name (e.g., 'starlink', 'oneweb')
            custom_url: Custom URL to download from (overrides group)

        Returns:
            Raw TLE text content

        Raises:
            requests.RequestException: If download fails
            ValueError: If group is not supported and no custom_url provided
        """
        if custom_url:
            url = custom_url
        else:
            if group.lower() not in self.CONSTELLATIONS:
                raise ValueError(
                    f"Unsupported group: {group}. "
                    f"Supported groups: {list(self.CONSTELLATIONS.keys())} "
                    f"or provide custom_url"
                )

            url = f"{self.BASE_URL}?GROUP={group}&FORMAT=tle"

        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.text.strip()
        except requests.RequestException as e:
            raise requests.RequestException(
                f"Failed to download TLE data from {url}: {e}"
            )

    def save_tle(self, tle_content: str, filepath: str) -> None:
        """Save TLE content to file.

        Args:
            tle_content: TLE text content
            filepath: Output file path
        """
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(tle_content)
            
    def extract_catid(self, tle_content: str, keyword: Optional[str] = None) -> List[str]:
        """Extract catalog IDs from TLE content, optionally filtered by keyword.

        Args:
            tle_content: TLE text content
            keyword: Optional keyword to filter satellites (e.g., 'DTC', 'STARLINK', etc.)
                    If None, extracts all catalog IDs

        Returns:
            List of catalog IDs, optionally filtered by keyword
        """
        cat_ids = []
        lines = tle_content.strip().split("\n")

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # 如果指定了关键词，检查标题行是否包含该关键词
            if keyword:
                keyword_pattern = f"[{keyword}]"
                if keyword_pattern in line and i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    # 检查下一行是否是TLE第一行
                    if next_line.startswith("1 "):
                        match = re.match(r"1 (\d+)", next_line)
                        if match:
                            cat_ids.append(match.group(1))
            else:
                # 没有指定关键词，提取所有catalog ID
                if line.startswith("1 "):
                    match = re.match(r"1 (\d+)", line)
                    if match:
                        cat_ids.append(match.group(1))
            
            i += 1

        return cat_ids


    def filter_tle_by_catid(self, tle_content: str, catid_list: List[str]) -> str:
        """Filter TLE content by catalog IDs.

        Args:
            tle_content: TLE text content
            cat_ids: List of catalog IDs to keep

        Returns:
            Filtered TLE content
        """
        if not catid_list:
            return ""

        cat_id_set = set(catid_list)
        filtered_lines = []
        lines = tle_content.strip().split("\n")

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # 如果是标题行，检查后续的TLE行
            if not line.startswith(("1 ", "2 ")) and i + 2 < len(lines):
                line1 = lines[i + 1].strip()
                line2 = lines[i + 2].strip()

                # 检查是否是完整的TLE条目
                if line1.startswith("1 ") and line2.startswith("2 "):
                    match = re.match(r"1 (\d+)", line1)
                    if match and match.group(1) in cat_id_set:
                        # 添加标题行和两行TLE数据
                        filtered_lines.extend([line, line1, line2])
                    i += 3
                    continue

            i += 1

        return "\n".join(filtered_lines)

    def parse_tle_entries(self, tle_content: str) -> List[Tuple[str, str, str, str]]:
        """Parse TLE content into structured entries.

        Args:
            tle_content: TLE text content

        Returns:
            List of tuples (title, cat_id, line1, line2)
        """
        entries = []
        lines = tle_content.strip().split("\n")

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # 如果不是TLE数据行，可能是标题行
            if not line.startswith(("1 ", "2 ")) and i + 2 < len(lines):
                line1 = lines[i + 1].strip()
                line2 = lines[i + 2].strip()

                # 检查是否是完整的TLE条目
                if line1.startswith("1 ") and line2.startswith("2 "):
                    match = re.match(r"1 (\d+)", line1)
                    if match:
                        cat_id = match.group(1)
                        entries.append((line, cat_id, line1, line2))
                    i += 3
                    continue

            i += 1

        return entries

    def get_constellation_url(self, group: str) -> str:
        """Get the full URL for a constellation group.

        Args:
            group: Constellation group name

        Returns:
            Full URL for the constellation

        Raises:
            ValueError: If group is not supported
        """
        if group.lower() not in self.CONSTELLATIONS:
            raise ValueError(
                f"Unsupported group: {group}. "
                f"Supported groups: {list(self.CONSTELLATIONS.keys())}"
            )

        return f"{self.BASE_URL}?GROUP={group}&FORMAT=tle"
