import re

from ..core.document_repository import get_repository
from ..core.utils.markdown_utils import format_search_result_entry


def _normalize_category_input(category: str | list[str] | None) -> str | list[str] | None:
    """
    AI 에이전트가 전달할 수 있는 null 관련 값들을 None으로 정규화합니다.

    Args:
        category: 원본 카테고리 값

    Returns:
        정규화된 카테고리 값
    """
    if category is None:
        return None

    # 문자열인 경우 null 관련 값들을 None으로 변환
    if isinstance(category, str):
        null_values = {'null', 'NULL', 'Null', 'undefined', 'None', ''}
        if category in null_values:
            return None
        return category

    # 리스트인 경우 각 요소를 정규화
    if isinstance(category, list):
        normalized_list = []
        for item in category:
            if isinstance(item, str) and item in {'null', 'NULL', 'Null', 'undefined', 'None', ''}:
                continue  # null 값들은 리스트에서 제외
            normalized_list.append(item)
        return normalized_list if normalized_list else None

    return category


class SearchValidator:
    MAX_QUERY_LENGTH = 200
    MAX_KEYWORDS = 10
    MIN_KEYWORD_LENGTH = 1
    MAX_KEYWORD_LENGTH = 50

    @staticmethod
    def validate_and_clean_query(query: str) -> tuple[bool, str, list[str]]:
        if not query:
            return False, "검색어를 입력해 주세요.", []

        if len(query) > SearchValidator.MAX_QUERY_LENGTH:
            return (
                False,
                f"검색어가 너무 깁니다. (최대 {SearchValidator.MAX_QUERY_LENGTH}자)",
                [],
            )

        safe_query = re.sub(r"[^\w\s가-힣,.-]", "", query)

        try:
            keywords = [
                kw.strip() for kw in re.split(r"[,\s]+", safe_query) if kw.strip()
            ]
        except re.error:
            return False, "검색어 형식이 올바르지 않습니다.", []

        valid_keywords = []
        for kw in keywords:
            if (
                SearchValidator.MIN_KEYWORD_LENGTH
                <= len(kw)
                <= SearchValidator.MAX_KEYWORD_LENGTH
            ):
                valid_keywords.append(kw)

        if not valid_keywords:
            return False, "유효한 검색어가 없습니다.", []

        if len(valid_keywords) > SearchValidator.MAX_KEYWORDS:
            valid_keywords = valid_keywords[: SearchValidator.MAX_KEYWORDS]

        return True, "검증 성공", valid_keywords


def search_docs(
    query: str, category: str | list[str] | None = None
) -> dict[str, object]:
    """
    헥토파이낸셜 연동 문서에서 키워드 기반 검색을 수행합니다.

    Args:
        query (str): 검색할 키워드 문자열
            - 형식: 쉼표(,) 또는 공백으로 구분된 키워드
            - 제약: 1-200자, 최대 10개 키워드, 각 키워드 1-50자
            - 예시: "신용카드 결제", "API 연동 방법", "ezauth,내통장결제"
            - 한국어 키워드 자동 조합 지원 (예: "내통장 결제" → "내통장결제")

        category (str|list[str]|None): 검색 범위를 제한할 카테고리
            - 사용 가능한 값: "PG연동개요", "PG신용카드", "PG계좌이체", "PG가상계좌",
              "PG휴대폰", "PG간편결제", "PG관리기능", "내통장결제", "간편현금결제",
              "화이트라벨", "암호화"
            - 단일 카테고리: "PG신용카드" (신용카드 관련 문서만 검색)
            - 다중 카테고리: ["PG신용카드", "내통장결제"] (복수 카테고리 동시 검색)
            - None, "null", "NULL", "undefined", "None", "": 전체 문서에서 검색 (AI 에이전트 친화적)
            - 각 카테고리 설명:
              * "PG연동개요": PG 연동 개요 문서
              * "PG신용카드": PG 신용카드 결제 문서
              * "PG계좌이체": PG 계좌이체 결제 문서
              * "PG가상계좌": PG 가상계좌 결제 문서
              * "PG휴대폰": PG 휴대폰 결제 문서
              * "PG간편결제": PG 간편결제 문서
              * "PG관리기능": PG 관리 기능 문서
              * "내통장결제": 내통장결제 서비스 관련 문서
              * "간편현금결제": 간편현금결제 서비스 관련 문서
              * "화이트라벨": 화이트라벨 서비스 관련 문서
              * "암호화": 암호화 가이드 문서

    Returns:
        dict: 검색 성공 시
            {
                "검색어": list[str],           # 실제 검색에 사용된 키워드 목록
                "검색결과": list[dict],        # BM25 점수 기반 정렬된 문서 섹션
                "안내": str                    # 검색 결과 설명
            }

            검색결과 각 항목 구조:
            {
                "문서제목": str,              # 문서의 제목
                "문서ID": str,                # 문서 고유 식별자
                "카테고리": str,              # 문서 카테고리 (PG, 내통장결제, 간편현금결제, 화이트라벨)
                "본문": str                   # 매칭된 문서 섹션 내용
            }

        dict: 검색 실패 시
            {
                "오류": str,                  # 오류 메시지
                "안내": str                   # 해결 방법 안내 (선택적)
            }
    """
    is_valid, message, keywords = SearchValidator.validate_and_clean_query(query)
    if not is_valid:
        return {"오류": message}

    try:
        # AI 에이전트 친화적인 null 값 정규화
        normalized_category = _normalize_category_input(category)

        repository = get_repository()
        results = repository.search_documents(keywords, category=normalized_category, top_n=20)

        if "오류" in results:
            return results

        result_entries = []
        for entry in results.get("검색결과", []):
            meta = entry.get("meta", {})
            content = entry.get("content", "")
            result_entries.append(format_search_result_entry(meta, content))

        return {
            "검색어": keywords,
            "검색결과": result_entries,
            "안내": results.get(
                "안내", "관련성이 높은 문서 섹션을 정렬하여 제공합니다."
            ),
        }

    except Exception as e:
        return {
            "오류": f"검색 중 문제가 발생했습니다: {e}",
            "안내": "다시 시도해 주세요. 문제가 지속되면 관리자에게 문의하세요.",
        }
