import re

FMS_BASE_URL = "https://findmestore.thinkr.jp"
BREAK_TIME = 2
RETRY_PERIOD = 30


def fix_json(json_str: str) -> str:
    """Fixes the JSON string by replacing empty 'id' fields with null."""
    return re.sub(r":\s*(,|\})", f": null\\1", json_str)
