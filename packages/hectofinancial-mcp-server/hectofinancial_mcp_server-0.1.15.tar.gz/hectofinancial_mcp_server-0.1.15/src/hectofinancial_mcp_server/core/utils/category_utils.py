import json
from pathlib import Path

CATEGORY_MAP_PATH = Path(__file__).parent / "category_map.json"


def load_category_map():
    with open(CATEGORY_MAP_PATH, encoding="utf-8") as f:
        return json.load(f)


CATEGORY_MAP = load_category_map()


def extract_category(path: str) -> str:
    path_lower = path.lower()
    # 더 구체적인 매칭을 위해 키를 길이 순으로 정렬 (긴 키부터)
    sorted_keys = sorted(CATEGORY_MAP.keys(), key=len, reverse=True)
    for key in sorted_keys:
        if key != "etc" and key in path_lower:
            return CATEGORY_MAP[key]
    return CATEGORY_MAP.get("etc", "기타")
