import itertools
import re
from dataclasses import dataclass

from .utils.bm25_utils import BM25Params, bm25_score
from .utils.dynamic_keyword_processor import DynamicKeywordProcessor


@dataclass
class DocumentChunk:
    id: int
    text: str
    word_count: int
    origin_title: str
    filename: str
    category: str


@dataclass
class SearchResult:
    id: int
    score: float
    total_tf: int


def build_context(ctx_stack, last_level2):
    if len(ctx_stack) == 2 and ctx_stack[0] == ctx_stack[1]:
        return [ctx_stack[0]]
    if len(ctx_stack) == 2 and ctx_stack[0] in ctx_stack[1]:
        return [ctx_stack[1]]
    if len(ctx_stack) == 1 and last_level2:
        if last_level2 == ctx_stack[0]:
            return [ctx_stack[0]]
        if last_level2 in ctx_stack[0]:
            return [ctx_stack[0]]
        return [last_level2, ctx_stack[0]]
    return ctx_stack.copy()


class HectoSearchEngine:
    def __init__(self, chunks: list[DocumentChunk], k1=1.2, b=0.75, window_size=5):
        self.k1 = k1
        self.b = b
        self.window_size = window_size
        self.all_chunks = chunks
        self.total_count = sum(chunk.word_count for chunk in self.all_chunks)
        self.average_doc_length = (
            self.total_count / len(self.all_chunks) if self.all_chunks else 0
        )
        self.N = len(self.all_chunks)

        # 동적 키워드 처리기 초기화
        self.keyword_processor = DynamicKeywordProcessor(chunks)

    def calculate(self, query: str, top_n: int = 20) -> list[SearchResult]:
        if not self.all_chunks:
            return []

        # 기본 키워드 추출
        raw_keywords = [k for k in re.split(r"[ ,|]+", query) if k]

        # 동적 키워드 분해 적용
        expanded_keywords = set()
        for keyword in raw_keywords:
            # 기존 방식 유지
            expanded_keywords.add(keyword)
            if re.match(r"[가-힣 ]+", keyword):
                expanded_keywords.add(keyword.replace(" ", ""))
                expanded_keywords.update(keyword.split())

            # 새로운 동적 분해 방식 추가
            decomposed = self.keyword_processor.decompose_keyword(keyword)
            expanded_keywords.update(decomposed)

        # 기존 조합 방식도 유지
        max_comb_length = 3
        for r in range(2, min(len(raw_keywords), max_comb_length) + 1):
            for comb in itertools.combinations(raw_keywords, r):
                expanded_keywords.add("".join(comb))

        keywords = list(expanded_keywords)
        term_frequencies, doc_frequencies = self._calculate_frequencies(keywords)
        scores = self._calculate_score(term_frequencies, doc_frequencies, keywords)
        filtered_scores = [s for s in scores if s.total_tf > 0]
        filtered_scores.sort(key=lambda x: (-x.score, -x.total_tf))
        return filtered_scores[:top_n]

    def _calculate_frequencies(
        self, keywords: list[str]
    ) -> tuple[dict[int, dict[str, int]], dict[str, int]]:
        term_frequencies = {}
        doc_frequencies = {}
        for chunk in self.all_chunks:
            term_counts = {}
            for keyword in keywords:
                if re.match(r"[가-힣]+", keyword):
                    text = chunk.text.replace(" ", "").lower()
                    k = keyword.replace(" ", "").lower()
                else:
                    text = chunk.text.lower()
                    k = keyword.lower()
                count = text.count(k)
                if count > 0:
                    term_counts[keyword] = count
            if term_counts:
                term_frequencies[chunk.id] = term_counts
                for term in term_counts:
                    doc_frequencies[term] = doc_frequencies.get(term, 0) + 1
        return term_frequencies, doc_frequencies

    def _calculate_score(
        self,
        term_frequencies: dict[int, dict[str, int]],
        doc_frequencies: dict[str, int],
        keywords: list[str] | None = None,
    ) -> list[SearchResult]:
        params = BM25Params(
            k1=self.k1, b=self.b, average_doc_length=self.average_doc_length, n=self.N
        )
        if keywords is None:
            keywords = []
        bm25_results = bm25_score(
            term_frequencies, doc_frequencies, self.all_chunks, params, keywords
        )
        return [
            SearchResult(id=r.id, score=r.score, total_tf=r.total_tf)
            for r in bm25_results
        ]

    def get_chunk_by_id(self, chunk_id: int) -> DocumentChunk | None:
        if 0 <= chunk_id < len(self.all_chunks):
            return self.all_chunks[chunk_id]
        return None

    def highlight_terms(self, chunk_text: str, keywords: list[str]) -> str:
        def replacer(match):
            word = match.group(0)
            return (
                word if word.startswith("**") and word.endswith("**") else f"**{word}**"
            )

        for keyword in sorted(keywords, key=len, reverse=True):
            if re.match(r"[가-힣]+", keyword):
                pattern = re.compile(
                    rf"(?<!\*){re.escape(keyword)}(?!\*)", re.IGNORECASE
                )
            else:
                pattern = re.compile(
                    rf"(?<!\*)\b{re.escape(keyword)}\b(?!\*)", re.IGNORECASE
                )
            chunk_text = pattern.sub(replacer, chunk_text)
        return chunk_text
