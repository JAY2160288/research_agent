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
    pinned: bool = Field(default=False, description="사용자가 --include 로 고정한 문헌. evaluate 후보 상한과 무관하게 평가한다")

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


class BriefText(BaseModel):
    """Writer 노드가 LLM 으로 만드는 유일한 자유 텍스트. 나머지 섹션은 상태에서 결정적으로 조립한다."""

    executive_summary: str = Field(description="연구자가 1분 안에 읽을 요약 (한국어, 5~8문장). 합의·상충·핵심 Gap 을 포함")
    limitations: list[str] = Field(min_length=1, description="Agent 가 확신하지 못하는 부분, 검색 범위 한계, 근거가 얇은 sub-RQ (영어, 3~6개)")

    def check(self) -> list[str]:
        issues = []
        if not any("가" <= ch <= "힣" for ch in self.executive_summary):
            issues.append("executive_summary must be written in Korean")
        if len(self.executive_summary) < 150:
            issues.append("executive_summary too short (< 150 chars)")
        return issues


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


class CritiqueIssue(BaseModel):
    """Critic LLM 비판의 지적 하나. 결정적 검사가 못 보는 깊이·논리 문제."""

    severity: Literal["major", "minor"] = Field(
        description="major = 이 브리프를 믿은 연구자가 오도되거나 sub-RQ 가 사실상 미답. 그 외는 minor")
    where: Literal["synthesis", "gaps", "evidence"]
    sub_rq_id: str | None = Field(default=None, description="관련 sub-RQ id. 특정 sub-RQ 문제가 아니면 null")
    problem: str = Field(description="무엇이 문제인지 한 문장. 관련 paper id 나 claim 을 지목")
    action: str = Field(description="파이프라인이 할 일. 'search rq3: <찾을 문헌 종류>' 또는 'synthesize: ...' / 'gap: ...'")


class LLMCritique(BaseModel):
    """Critic 의 LLM 비판 결과. 결정적 검사를 통과한 뒤에만 호출된다 (plan.md §3.3 마지막 행)."""

    issues: list[CritiqueIssue] = Field(default_factory=list, description="문제 없으면 빈 목록")

    @property
    def major(self) -> list[CritiqueIssue]:
        return [i for i in self.issues if i.severity == "major"]

    def check(self, rq_ids: set[str]) -> list[str]:
        return [f"issue refers unknown sub_rq_id {i.sub_rq_id}" for i in self.issues
                if i.sub_rq_id is not None and i.sub_rq_id not in rq_ids]


class Critique(BaseModel):
    round: int = 1
    passed: bool
    deterministic_issues: list[str] = Field(default_factory=list)
    uncovered_sub_rqs: list[str] = Field(default_factory=list)
    weak_claims: list[str] = Field(default_factory=list)
    actions: list[str] = Field(default_factory=list, description="Replan 지시. 예: 'rq2: add query X'")
    llm_ran: bool = Field(default=False, description="LLM 비판이 실행됐는가 (결정적 검사 통과 + critic=full 일 때만)")
    llm_issues: list[CritiqueIssue] = Field(default_factory=list)

    def feedback_lines(self) -> list[str]:
        """synthesize·gap 재실행 시 프롬프트에 붙일 비판 요약."""
        return list(self.deterministic_issues) + [f"[{i.severity}] {i.problem} → {i.action}" for i in self.llm_issues]


class ReplanItem(BaseModel):
    sub_rq_id: str = Field(description="재검색할 sub-RQ id (계획에 있는 것만)")
    reason: str = Field(description="왜 이 sub-RQ 를 다시 찾는가 (Critic 지적 요약)")
    queries: list[str] = Field(min_length=1, description="기존 쿼리와 표현이 다른 새 검색 쿼리 1~3개 (영어). 3개를 넘으면 앞의 3개만 쓴다")


class ReplanPlan(BaseModel):
    """Replan 노드 출력. items 가 비어 있으면 재검색 없이 종합·Gap 만 비판을 반영해 다시 쓴다."""

    items: list[ReplanItem] = Field(default_factory=list)
    rationale: str = Field(description="무엇을 왜 바꿨는지 1~3문장")

    def check(self, plan: ResearchPlan, required: set[str] | None = None) -> list[str]:
        """required = Critic 이 재검색을 지시한 sub-RQ. 그 각각에 쿼리가 있어야 한다 — rationale 에 글로만 쓰고
        items 를 비워 보내는 응답(Haiku 에서 관찰)은 한 라운드를 통째로 낭비하므로 되먹인다."""
        issues = []
        by_id = {s.id: s for s in plan.sub_rqs}
        missing = sorted((required or set()) - {it.sub_rq_id for it in self.items})
        if missing:
            issues.append(f"items is missing the sub-RQs the critic asked to re-search: {missing}. "
                          "Give 1-3 NEW queries for each of them in `items` (rationale text is not a substitute)")
        for it in self.items:
            sq = by_id.get(it.sub_rq_id)
            if sq is None:
                issues.append(f"unknown sub_rq_id {it.sub_rq_id}")
                continue
            old = {q.strip().lower() for q in sq.queries}
            dup = [q for q in it.queries if q.strip().lower() in old]
            if dup:
                issues.append(f"{it.sub_rq_id}: queries already used {dup}")
        return issues

    def as_extra_queries(self) -> dict[str, list[str]]:
        out: dict[str, list[str]] = {}
        for it in self.items:
            out.setdefault(it.sub_rq_id, []).extend(it.queries)
        return out


class RunState(BaseModel):
    topic: str
    topic_frame: TopicFrame | None = None
    plan: ResearchPlan | None = None
    papers: dict[str, Paper] = Field(default_factory=dict)
    evidence: EvidenceTable | None = None
    synthesis: Synthesis | None = None
    critiques: list[Critique] = Field(default_factory=list)
    replans: list[ReplanPlan] = Field(default_factory=list)
    gaps: GapList | None = None
    brief: ResearchBrief | None = None
    replan_count: int = 0
    notes: list[str] = Field(default_factory=list, description="미달 항목 등 리포트 한계에 자동 기재할 내용")

    def verified_ids(self) -> set[str]:
        return {pid for pid, p in self.papers.items() if p.verified}


# ---------------------------------------------------------------------------
# LLM-judge (eval/rubric.md §B) — 실행 결과 채점. 파이프라인 밖(사후) 에서만 쓴다
# ---------------------------------------------------------------------------

JUDGE_ITEMS: dict[str, str] = {
    "J1": "주제 이해의 정확성",
    "J2": "조사 계획의 완결성",
    "J3": "근거 평가의 충실성",
    "J4": "종합의 깊이",
    "J5": "Research Gap 의 타당성",
    "J6": "향후 연구 제안의 구체성",
    "J7": "한계 서술의 정직성",
}


class JudgeItem(BaseModel):
    id: Literal["J1", "J2", "J3", "J4", "J5", "J6", "J7"]
    score: int = Field(description="1~5 정수. 5 = 루브릭의 5점 기준 충족, 1 = 1점 기준")
    quote: str = Field(description="점수의 근거가 되는 리포트 문장을 **그대로** 인용 (의역 금지, 1~3문장)")
    reason: str = Field(description="왜 그 점수인지 한국어 1~2문장. 루브릭 기준을 지목")


class JudgeResult(BaseModel):
    """J1~J7 각 1개. 총점은 코드에서 단순 평균으로 계산한다 (rubric §B)."""

    items: list[JudgeItem]
    overall_comment: str = Field(description="브리프 전체에 대한 총평 (한국어, 2~4문장)")

    def check(self) -> list[str]:
        """결정적 검증: 7항목이 정확히 한 번씩, 점수 1~5, 인용 비어있지 않음.
        점수 범위는 스키마 제약(ge/le)이 아니라 여기서 본다 — SDK parse 단계 실패는 호출을 통째로 버리기 때문 (CLAUDE.md)."""
        issues = []
        ids = [it.id for it in self.items]
        missing = sorted(set(JUDGE_ITEMS) - set(ids))
        dup = sorted({i for i in ids if ids.count(i) > 1})
        if missing:
            issues.append(f"missing items {missing}")
        if dup:
            issues.append(f"duplicated items {dup}")
        for it in self.items:
            if not 1 <= it.score <= 5:
                issues.append(f"{it.id}: score {it.score} not in 1..5")
            if not it.quote.strip():
                issues.append(f"{it.id}: quote is empty — cite the report verbatim")
        return issues

    @property
    def mean(self) -> float:
        return round(sum(it.score for it in self.items) / len(self.items), 2) if self.items else 0.0


# ---------------------------------------------------------------------------
# 주장-근거 지지 검증 (claim support) — judge 와 같은 사후 작업. plan.md §6.2, ADR-10
# "인용이 실존한다"(citation_verified_rate) 와 "인용이 주장을 뒷받침한다" 는 다른 지표다.
# ---------------------------------------------------------------------------

SUPPORT_VERDICTS = ("supported", "partial", "unsupported")


class SupportVerdict(BaseModel):
    claim_id: str = Field(description="입력에 적힌 claim id 를 그대로 (예: c3)")
    paper_id: str = Field(description="입력에 적힌 paper id 를 그대로")
    verdict: Literal["supported", "partial", "unsupported"] = Field(
        description="supported = 초록이 주장을 직접 뒷받침 · partial = 방향은 같지만 범위·조건·강도가 다름 · unsupported = 초록에 근거 없음 또는 반대")
    quote: str = Field(default="", description="supported/partial 이면 근거가 되는 초록 문장을 **그대로** 복사 (의역 금지, 1~2문장). unsupported 면 빈 문자열")
    reason: str = Field(description="판정 이유 한국어 1문장")


class SupportResult(BaseModel):
    verdicts: list[SupportVerdict]

    def check(self, expected: set[tuple[str, str]], abstracts: dict[str, str]) -> list[str]:
        """결정적 검증: (claim, paper) 쌍이 빠짐·중복 없이 한 번씩, quote 가 그 초록에 실제로 있는 문자열인지."""
        issues = []
        seen = [(v.claim_id, v.paper_id) for v in self.verdicts]
        missing = sorted(expected - set(seen))
        extra = sorted(set(seen) - expected)
        dup = sorted({p for p in seen if seen.count(p) > 1})
        if missing:
            issues.append(f"missing pairs {missing[:5]}{'...' if len(missing) > 5 else ''}")
        if extra:
            issues.append(f"unknown pairs {extra[:5]}")
        if dup:
            issues.append(f"duplicated pairs {dup[:5]}")
        for v in self.verdicts:
            if v.verdict == "unsupported":
                continue
            q = _squash(v.quote)
            if not q:
                issues.append(f"{v.claim_id}/{v.paper_id}: {v.verdict} needs a verbatim quote from the abstract")
            elif q not in _squash(abstracts.get(v.paper_id, "")):
                issues.append(f"{v.claim_id}/{v.paper_id}: quote is not verbatim from that abstract — copy exact text")
        return issues


def _squash(text: str) -> str:
    """인용 대조용 정규화: 공백 압축 + 소문자. 따옴표·대시 같은 기호 차이는 그대로 둔다 (LLM 이 베껴 쓰게 강제)."""
    return " ".join(text.split()).lower()


# ---------------------------------------------------------------------------
# 한국어 번역 (translate.py, ADR-11) — 표현 계층. 영어 brief.json 이 진실 원천이고 이것은 그 산문 필드의 번역본
# ---------------------------------------------------------------------------


class KoText(BaseModel):
    id: str = Field(description="입력에서 받은 id 그대로 (바꾸거나 빠뜨리지 않는다)")
    ko: str = Field(description="한국어 번역. 숫자·DOI·논문 제목·고유명사·따옴표 인용은 원문 그대로 두고, 전문용어는 '과적합(overfitting)' 처럼 영어를 병기한다")


def _nums(text: str) -> set[str]:
    """숫자 토큰 집합 (천 단위 콤마 제거). 번역이 수치를 빠뜨리거나 바꾸지 않았는지 대조용."""
    import re
    return set(re.findall(r"\d+(?:\.\d+)?", text.replace(",", "")))


class KoreanBrief(BaseModel):
    """brief 의 독자용 산문 필드(id → 영어)를 받아 같은 id 로 한국어를 돌려준 결과.

    결정적 검사(`item_issues`/`check`)는 번역이 **내용을 바꾸지 않았음** 을 코드가 확인하는 장치다 — 한글 포함, 원문 숫자 토큰 전부 보존,
    길이 비율 0.35~1.6 (한국어는 보통 영어의 0.5~0.9배 글자 수 — 그 밖이면 누락·장황). 검사에 걸린 항목은 영어 원문을 그대로 쓴다 (translate.py)."""
    items: list[KoText]

    def item_issues(self, source: dict[str, str]) -> dict[str, list[str]]:
        """항목별 문제. 문제 없는 id 는 키가 없다."""
        out: dict[str, list[str]] = {}
        for it in self.items:
            en = source.get(it.id)
            if en is None:
                continue
            iss: list[str] = []
            ko = it.ko.strip()
            if not any("가" <= ch <= "힣" for ch in ko):
                iss.append("no Korean text")
            lost = _nums(en) - _nums(ko)
            if lost:
                iss.append(f"numbers missing from translation: {sorted(lost)[:6]} — copy every number, DOI and id verbatim")
            if len(en) >= 40:
                ratio = len(ko) / len(en)
                if ratio < 0.35:
                    iss.append(f"too short (ratio {ratio:.2f}) — translate the whole text, do not summarize")
                elif ratio > 1.6:
                    iss.append(f"too long (ratio {ratio:.2f}) — translate, do not add explanations")
            if iss:
                out[it.id] = iss
        return out

    def check(self, source: dict[str, str]) -> list[str]:
        got = [it.id for it in self.items]
        missing = [k for k in source if k not in got]
        extra = sorted(set(got) - set(source))
        dup = sorted({k for k in got if got.count(k) > 1})
        issues: list[str] = []
        if missing:
            issues.append(f"missing ids {missing[:8]}{'...' if len(missing) > 8 else ''}")
        if extra:
            issues.append(f"unknown ids {extra[:5]}")
        if dup:
            issues.append(f"duplicated ids {dup[:5]}")
        issues += [f"{k}: {'; '.join(v)}" for k, v in self.item_issues(source).items()]
        return issues

    def accepted(self, source: dict[str, str]) -> dict[str, str]:
        """검사를 통과한 항목만 id → 한국어. 중복 id 는 첫 것."""
        bad = self.item_issues(source)
        out: dict[str, str] = {}
        for it in self.items:
            if it.id in source and it.id not in bad and it.id not in out:
                out[it.id] = it.ko.strip()
        return out
