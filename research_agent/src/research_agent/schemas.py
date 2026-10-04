"""모든 노드 간 데이터 계약. plan.md §3.2 의 코드화.

원칙
- 노드는 자유 텍스트가 아니라 이 스키마 타입만 주고받는다 (goals.md O7-L2 구조 불변).
- 각 모델의 `check()` 는 LLM 없이 돌아가는 결정적 자체 검증. Critic 의 1차 게이트.
- Field description 은 그대로 LLM 에게 JSON Schema 로 전달되므로 지시문처럼 쓴다.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

# ---------------------------------------------------------------------------
# ① Understand
# ---------------------------------------------------------------------------


class Variables(BaseModel):
    independent: list[str] = Field(description="독립변수/개입/처치 (X). 예: '생성형 AI 활용'")
    dependent: list[str] = Field(description="종속변수/결과 (Y). 예: '연구 생산성', '연구 품질'")
    population: str = Field(description="연구 대상 모집단. 예: '대학원생'")
    context: str = Field(default="", description="맥락·범위. 예: '고등교육, 2022년 이후'")


class TopicFrame(BaseModel):
    """연구 주제를 분해한 구조. 이후 모든 단계의 기준점."""

    original_topic: str
    topic_en: str = Field(description="주제의 영어 번역 (학술 검색용)")
    domain: str = Field(description="주 학문 분야. 예: 'education', 'computer science', 'accounting'")
    concepts: list[str] = Field(description="핵심 개념 3~8개 (영어)")
    variables: Variables
    synonyms_en: list[str] = Field(description="검색 확장용 영어 동의어·관련어 (최소 3개)")
    research_question: str = Field(description="주제를 한 문장의 연구 질문으로 재진술 (영어)")

    def check(self) -> list[str]:
        issues = []
        if len(self.concepts) < 3:
            issues.append("concepts < 3")
        if len(self.synonyms_en) < 3:
            issues.append("synonyms_en < 3")
        if not self.variables.independent or not self.variables.dependent:
            issues.append("variables.independent/dependent empty")
        return issues


# ---------------------------------------------------------------------------
# ② Plan
# ---------------------------------------------------------------------------


class SubRQ(BaseModel):
    id: str = Field(description="짧은 식별자. 예: 'rq1'")
    question: str = Field(description="하위 연구 질문 (영어). 다른 sub-RQ 와 겹치지 않게")
    rationale: str = Field(description="이 질문이 주제 이해에 왜 필요한지 한 문장")
    queries: list[str] = Field(description="학술 검색 쿼리 2~4개 (영어, 키워드 조합)")
    source_pref: Literal["openalex", "arxiv", "both"] = Field(
        default="both", description="CS/물리 성격이 강하면 arxiv 포함, 아니면 openalex"
    )


class ResearchPlan(BaseModel):
    """조사 계획. sub-RQ 3~6개가 주제를 빠짐없이, 겹치지 않게 덮어야 한다."""

    sub_rqs: list[SubRQ] = Field(min_length=3, max_length=6)
    search_strategy: str = Field(description="전체 검색 전략 요약 (기간, 분야, 제외 기준 등)")

    def check(self) -> list[str]:
        issues = []
        ids = [s.id for s in self.sub_rqs]
        if len(ids) != len(set(ids)):
            issues.append("duplicate sub_rq ids")
        for s in self.sub_rqs:
            if not (2 <= len(s.queries) <= 4):
                issues.append(f"{s.id}: queries count {len(s.queries)} not in 2..4")
        # 쿼리 중복률: 전체 쿼리 중 다른 sub-RQ 와 완전히 같은 것의 비율 < 50%
        all_q = [(s.id, q.strip().lower()) for s in self.sub_rqs for q in s.queries]
        dup = sum(1 for sid, q in all_q if any(q == q2 and sid != sid2 for sid2, q2 in all_q))
        if all_q and dup / len(all_q) >= 0.5:
            issues.append("query overlap >= 50%")
        return issues


# ---------------------------------------------------------------------------
# ③ Search → ④ Evaluate
# ---------------------------------------------------------------------------


class Paper(BaseModel):
    """검색 도구가 반환하는 문헌 메타데이터. LLM 이 만들지 않는다 — 도구 출력 그대로."""

    id: str = Field(description="DOI (소문자, 'https://doi.org/' 제거) 또는 'arxiv:<id>'")
    title: str
    year: int | None = None
    authors: list[str] = Field(default_factory=list)
    venue: str | None = None
    abstract: str | None = None
    doi: str | None = None
    arxiv_id: str | None = None
    url: str | None = None
    cited_by_count: int | None = None
    source: Literal["openalex", "arxiv", "crossref"]
    sub_rq_ids: list[str] = Field(default_factory=list, description="이 문헌을 찾아낸 sub-RQ")
    verified: bool = Field(default=False, description="Crossref/OpenAlex 로 실존 확인됨")

    @model_validator(mode="after")
    def _norm(self):
        if self.doi:
            self.doi = self.doi.lower().replace("https://doi.org/", "").replace("http://doi.org/", "")
        return self


class Evidence(BaseModel):
    """평가된 문헌 한 편. Evaluator(LLM) 가 Paper 를 읽고 채운다."""

    paper_id: str = Field(description="Paper.id 를 그대로")
    relevance: int = Field(ge=0, le=5, description="주제·sub-RQ 관련성 0~5")
    reliability: int = Field(ge=0, le=5, description="방법론·출처 신뢰도 0~5 (동료심사·표본·설계 고려)")
    method: str = Field(description="연구 방법. 예: 'RCT', 'survey n=312', 'systematic review', 'case study'")
    sample: str = Field(default="", description="표본·데이터. 모르면 빈 문자열")
    finding: str = Field(description="핵심 결과 한두 문장 (영어). 초록에 없는 내용은 쓰지 않는다")
    sub_rq_ids: list[str] = Field(description="이 문헌이 답하는 sub-RQ id")
    limitations: str = Field(default="", description="초록에서 드러나는 한계")


class EvidenceTable(BaseModel):
    items: list[Evidence]

    def check(self, papers: dict[str, Paper]) -> list[str]:
        issues = []
        for e in self.items:
            p = papers.get(e.paper_id)
            if p is None:
                issues.append(f"evidence refers unknown paper {e.paper_id}")
            elif not p.verified:
                issues.append(f"unverified paper in evidence: {e.paper_id}")
        return issues


# ---------------------------------------------------------------------------
# ⑤ Synthesize
# ---------------------------------------------------------------------------


class Claim(BaseModel):
    statement: str = Field(description="종합된 주장 한 문장 (영어)")
    evidence_ids: list[str] = Field(min_length=1, description="근거 Paper.id. 반드시 1개 이상")
    sub_rq_ids: list[str] = Field(default_factory=list)


class Conflict(BaseModel):
    claim: str = Field(description="상충하는 쟁점")
    side_a: Claim
    side_b: Claim
    hypothesis_for_conflict: str = Field(description="왜 결과가 갈리는지 가설 (표본, 측정, 맥락 차이 등)")


class Synthesis(BaseModel):
    consensus: list[Claim] = Field(description="다수 문헌이 일치하는 결과")
    conflicts: list[Conflict] = Field(description="문헌 간 상충하는 결과")
    conditional: list[Claim] = Field(description="특정 조건에서만 성립하는 결과")
    coverage_note: str = Field(description="어느 sub-RQ 가 충분/부족한지 한 단락")

    def all_claims(self) -> list[Claim]:
        out = list(self.consensus) + list(self.conditional)
        for c in self.conflicts:
            out += [c.side_a, c.side_b]
        return out

    def check(self, known_ids: set[str]) -> list[str]:
        issues = []
        for c in self.all_claims():
            bad = [i for i in c.evidence_ids if i not in known_ids]
            if bad:
                issues.append(f"claim cites unknown ids {bad}: {c.statement[:60]}")
        for cf in self.conflicts:
            if not cf.hypothesis_for_conflict.strip():
                issues.append(f"conflict without hypothesis: {cf.claim[:60]}")
        return issues


# ---------------------------------------------------------------------------
# ⑥ Gap & Direction
# ---------------------------------------------------------------------------


class Gap(BaseModel):
    description: str = Field(description="무엇이 연구되지 않았는가 (영어)")
    evidence_ids: list[str] = Field(min_length=2, description="이 공백을 드러내는 근거 문헌 2개 이상")
    proposed_rq: str = Field(description="제안 연구 질문")
    method: str = Field(description="제안 방법 (설계, 분석)")
    data: str = Field(description="필요 데이터·표본")


class GapList(BaseModel):
    gaps: list[Gap] = Field(min_length=1)

    def check(self, known_ids: set[str]) -> list[str]:
        return [f"gap cites unknown ids: {g.description[:60]}"
                for g in self.gaps if any(i not in known_ids for i in g.evidence_ids)]


# ---------------------------------------------------------------------------
# 최종 리포트 (goals.md §5 의 7개 섹션)
# ---------------------------------------------------------------------------


class ResearchBrief(BaseModel):
    topic_frame: TopicFrame
    plan: ResearchPlan
    evidence: EvidenceTable
    synthesis: Synthesis
    gaps: GapList
    limitations: list[str] = Field(description="Agent 가 확신하지 못하는 부분, 미달 항목, 검색 범위 한계")
    executive_summary: str = Field(description="연구자가 1분 안에 읽을 요약 (한국어, 5~8문장)")


# ---------------------------------------------------------------------------
# 실행 상태 (노드 간 공유)
# ---------------------------------------------------------------------------


class Critique(BaseModel):
    passed: bool
    deterministic_issues: list[str] = Field(default_factory=list)
    uncovered_sub_rqs: list[str] = Field(default_factory=list)
    weak_claims: list[str] = Field(default_factory=list)
    actions: list[str] = Field(default_factory=list, description="Replan 지시. 예: 'rq2: add query X'")


class RunState(BaseModel):
    topic: str
    topic_frame: TopicFrame | None = None
    plan: ResearchPlan | None = None
    papers: dict[str, Paper] = Field(default_factory=dict)
    evidence: EvidenceTable | None = None
    synthesis: Synthesis | None = None
    critiques: list[Critique] = Field(default_factory=list)
    gaps: GapList | None = None
    brief: ResearchBrief | None = None
    replan_count: int = 0
    notes: list[str] = Field(default_factory=list, description="미달 항목 등 리포트 한계에 자동 기재할 내용")

    def verified_ids(self) -> set[str]:
        return {pid for pid, p in self.papers.items() if p.verified}
