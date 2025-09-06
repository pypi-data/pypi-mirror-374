import json
from pathlib import Path
from typing import Dict


class Version:
    """Utility class for managing MONAI Deploy versions"""

    @staticmethod
    def get_version() -> str:
        """Get the current MONAI Deploy version"""
        try:
            version_file = Path(__file__).parent.parent / "_version.py"
            version_info = Version.parse_version_file(version_file)
            return version_info.get("version", "unknown")
        except Exception:
            return "unknown"

    @staticmethod
    def parse_version_file(version_file: Path) -> Dict:
        """Parse version info from _version.py file"""
        if not version_file.exists():
            return {}

        version_text = version_file.read_text()
        version_json = version_text.split("version_json = '")[1].split("'\n")[0]
        return json.loads(version_json)

    @staticmethod
    def get_version_info() -> Dict:
        """Get full version information including git details"""
        try:
            version_file = Path(__file__).parent.parent / "_version.py"
            return Version.parse_version_file(version_file)
        except Exception:
            return {"version": "unknown"}
