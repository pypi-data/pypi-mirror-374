from ..core.document_repository import get_repository


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


def list_docs(category: str | list[str] | None = None) -> dict[str, object]:
    """
    헥토파이낸셜 연동 문서 목록을 조회합니다.

    Args:
        category (str|list[str]|None): 조회할 문서 카테고리
            - 사용 가능한 값: "PG연동개요", "PG신용카드", "PG계좌이체", "PG가상계좌",
              "PG휴대폰", "PG간편결제", "PG관리기능", "내통장결제", "간편현금결제",
              "화이트라벨", "암호화"
            - 단일 카테고리: "PG신용카드" (신용카드 관련 문서만 조회)
            - 다중 카테고리: ["PG신용카드", "내통장결제"] (복수 카테고리 동시 조회)
            - None, "null", "NULL", "undefined", "None", "": 전체 문서 조회 (AI 에이전트 친화적)
            - 각 카테고리 설명:
              * "PG연동개요": PG 연동 개요 문서
              * "PG신용카드": PG 신용카드 결제 문서
              * "PG계좌이체": PG 계좌이체 결제 문서
              * "PG가상계좌": PG 가상계좌 결제 문서
              * "PG휴대폰": PG 휴대폰 결제 문서
              * "PG간편결제": PG 간편결제 문서
              * "PG관리기능": PG 관리 기능 문서
              * "내통장결제": 내통장결제 서비스 관련 문서 (ezauth)
              * "간편현금결제": 간편현금결제 서비스 관련 문서 (ezcp)
              * "화이트라벨": 화이트라벨 서비스 관련 문서 (whitelabel)
              * "암호화": 암호화 가이드 문서

    Returns:
        dict: 조회 성공 시
            {
                "문서목록": list[dict],        # 문서 목록 배열
                "안내": str                    # 사용 안내 메시지
            }

            문서목록 각 항목 구조:
            {
                "문서ID": str,                # 문서 고유 식별자 (get_docs 호출 시 사용)
                "제목": str,                  # 문서 제목 (마크다운 # 제목)
                "카테고리": str,              # 문서 카테고리 (PG, 내통장결제, 간편현금결제, 화이트라벨)
                "파일명": str,                # 원본 파일명 (확장자 포함)
                "태그": list[str]             # 문서 태그 목록
            }

        dict: 조회 실패 시
            {
                "오류": str                   # 오류 메시지
            }
    """
    try:
        # AI 에이전트 친화적인 null 값 정규화
        normalized_category = _normalize_category_input(category)

        repository = get_repository()
        result = repository.list_documents(
            sort_by="id",
            order="asc",
            category=normalized_category,
            page=1,
            page_size=50,
        )
        return {
            "문서목록": result["문서목록"],
            "안내": "문서 ID를 참고해 get_docs로 상세 내용을 확인할 수 있습니다.",
        }
    except Exception as e:
        return {"오류": f"문서 목록 처리 중 문제가 발생했습니다: {e}"}
