"""한국어 번역 — 끝난 실행의 brief.json 산문을 한국어로 옮겨 report.md 를 한국어본으로 다시 그린다 (ADR-11, 2026-10-08).

왜 사후 단계인가
- 독자는 한국어로 주제를 넣는 한국 연구자다. 요약만 한국어고 본문 400줄이 영어면 "1분 요약" 다음에 영어 벽이 선다.
- 그런데 노드 프롬프트를 한국어로 바꾸면 (1) ablation 20회·judge 점수가 영어 출력 기준이라 비교 가능성이 깨지고,
  (2) 한국어는 토큰이 1.5~2배라 evaluate 배치가 `node_max_tokens` 에 걸려 잘린 JSON 재시도(2026-10-04 장애)가 재발하며,
  (3) 결정적 검사가 영어 길이 전제다. 그래서 파이프라인은 그대로 두고 **렌더러처럼 표현 계층에서** 번역한다.
- `agent support` 의 초록 verbatim 대조(ADR-10)는 영어 원문 brief 에 대고 하므로 영향 없음.

무엇을 옮기나 (`source_items`): 연구 질문, 검색 전략, sub-RQ 질문, §4 합의·상충·조건부·커버리지 메모, §5 Gap 설명·제안 RQ·방법·데이터,
§7 한계(LLM 서술만 — `[auto]` 파이프라인 노트는 기계 메모라 영어 유지), "먼저 읽을 문헌" Top N 의 핵심 결과.
영어로 남기는 것: 논문 제목·저자·DOI·검색 쿼리·초록 인용문·§3 전체 표의 finding/method/sample(95행, 비용 대비 가치 낮음)·§1 변수명(검색어 겸용).

보장 장치 (O7): `KoreanBrief.item_issues` — 한글 포함, 원문 숫자·DOI 토큰 전부 보존, 길이 비율 0.35~1.6. 걸린 항목은 되먹여 재호출하고,
끝까지 안 풀리면 **그 항목은 영어 원문을 그대로 쓴다** (내용 변조보다 영어가 낫다). 결과 `brief.ko.json` 은 id → 한국어 사전이고
`report.rerender_run` 이 이를 brief 에 덧씌워 report.md(한국어)·report.en.md(영어 원문)를 그린다. brief.json 은 건드리지 않는다.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config import Settings, load_prompt
from .llm import LLM
from .report import AUTO_PREFIX, top_read
from .runlog import RunLogger
from .schemas import KoreanBrief, Paper, ResearchBrief

KO_BANNER = ("본문은 영어 원문(brief.json)을 한국어로 옮긴 것이다. 논문 제목·저자·DOI·검색 쿼리·§3 표의 결과 요약은 원문 그대로이며, "
             "영어 원문 리포트는 같은 폴더의 `report.en.md`.")


# ---------------------------------------------------------------- 산문 필드 ↔ id

def source_items(brief: ResearchBrief, papers: dict[str, Paper] | None = None) -> dict[str, str]:
    """번역할 산문 필드를 id → 영어 로. 순서는 리포트에 나오는 순서."""
    src: dict[str, str] = {"rq": brief.topic_frame.research_question}
    for e in top_read(brief, papers):
        src[f"finding:{e.paper_id}"] = e.finding
    src["strategy"] = brief.plan.search_strategy
    for s in brief.plan.sub_rqs:
        src[f"subrq:{s.id}"] = s.question
    syn = brief.synthesis
    for i, c in enumerate(syn.consensus):
        src[f"consensus:{i}"] = c.statement
    for i, c in enumerate(syn.conflicts):
        src[f"conflict:{i}:claim"] = c.claim
        src[f"conflict:{i}:a"] = c.side_a.statement
        src[f"conflict:{i}:b"] = c.side_b.statement
        src[f"conflict:{i}:hyp"] = c.hypothesis_for_conflict
    for i, c in enumerate(syn.conditional):
        src[f"conditional:{i}"] = c.statement
    src["coverage"] = syn.coverage_note
    for i, g in enumerate(brief.gaps.gaps):
        src[f"gap:{i}:desc"] = g.description
        src[f"gap:{i}:rq"] = g.proposed_rq
        src[f"gap:{i}:method"] = g.method
        src[f"gap:{i}:data"] = g.data
    for i, x in enumerate(brief.limitations):
        if not x.startswith(AUTO_PREFIX):
            src[f"limit:{i}"] = x
    return {k: v for k, v in src.items() if v and v.strip()}


def apply_translation(brief: ResearchBrief, ko: dict[str, str]) -> ResearchBrief:
    """id → 한국어 사전을 brief 의 복사본에 덧씌운다. 사전에 없는 id 는 영어 그대로 (검사 실패 항목의 fallback)."""
    b = brief.model_copy(deep=True)

    def pick(key: str, default: str) -> str:
        return ko.get(key) or default

    b.topic_frame.research_question = pick("rq", b.topic_frame.research_question)
    b.plan.search_strategy = pick("strategy", b.plan.search_strategy)
    for s in b.plan.sub_rqs:
        s.question = pick(f"subrq:{s.id}", s.question)
    for e in b.evidence.items:
        e.finding = pick(f"finding:{e.paper_id}", e.finding)
    syn = b.synthesis
    for i, c in enumerate(syn.consensus):
        c.statement = pick(f"consensus:{i}", c.statement)
    for i, c in enumerate(syn.conflicts):
        c.claim = pick(f"conflict:{i}:claim", c.claim)
        c.side_a.statement = pick(f"conflict:{i}:a", c.side_a.statement)
        c.side_b.statement = pick(f"conflict:{i}:b", c.side_b.statement)
        c.hypothesis_for_conflict = pick(f"conflict:{i}:hyp", c.hypothesis_for_conflict)
    for i, c in enumerate(syn.conditional):
        c.statement = pick(f"conditional:{i}", c.statement)
    syn.coverage_note = pick("coverage", syn.coverage_note)
    for i, g in enumerate(b.gaps.gaps):
        g.description = pick(f"gap:{i}:desc", g.description)
        g.proposed_rq = pick(f"gap:{i}:rq", g.proposed_rq)
        g.method = pick(f"gap:{i}:method", g.method)
        g.data = pick(f"gap:{i}:data", g.data)
    b.limitations = [pick(f"limit:{i}", x) for i, x in enumerate(b.limitations)]
    return b


# ---------------------------------------------------------------- 실행

def translate_run(run_dir: Path, settings: Settings, *, model: str | None = None,
                  client: Any | None = None) -> dict[str, Any]:
    """한 실행의 산문을 번역해 brief.ko.json 을 쓰고 report.md 를 한국어본으로 다시 그린다. 미완주면 ValueError.
    client 는 테스트용 가짜 Anthropic 클라이언트 (tests/test_translate.py)."""
    from .report import rerender_run

    brief_f, papers_f = run_dir / "brief.json", run_dir / "papers.json"
    if not brief_f.exists() or not papers_f.exists():
        raise ValueError(f"{run_dir.name}: brief.json / papers.json 없음 (완주한 실행만 번역한다)")
    brief = ResearchBrief.model_validate_json(brief_f.read_text(encoding="utf-8"))
    papers = {k: Paper.model_validate(v) for k, v in json.loads(papers_f.read_text(encoding="utf-8")).items()}
    src = source_items(brief, papers)

    model = model or settings.llm.translate_model
    log = RunLogger(run_dir.name, "translate", into=run_dir, prefix="translate_")
    llm = LLM(settings, log, client=client)
    system = load_prompt("translate")
    user = "Items to translate (JSON):\n\n" + json.dumps([{"id": k, "en": v} for k, v in src.items()], ensure_ascii=False, indent=1)

    issues: list[str] = []
    result: KoreanBrief | None = None
    for attempt in range(settings.llm.max_retries + 1):          # 검사 실패 → 되먹여 재호출 (nodes.checked_call 과 같은 규약)
        prompt = user if not issues else (user + "\n\nYour previous answer failed these checks (fix ONLY these, keep the rest identical):\n- "
                                          + "\n- ".join(issues[:30]) + "\nReturn the complete list again.")
        result = llm.call(role="translate", system=system, user=prompt, schema=KoreanBrief, model=model,
                          max_tokens=settings.llm.max_tokens)
        issues = result.check(src)
        log.event("translate_check", attempt=attempt + 1, issues=issues)
        if not issues:
            break
    assert result is not None
    accepted = result.accepted(src)
    fallback = [k for k in src if k not in accepted]
    notes = [f"{len(fallback)} item(s) kept in English after checks failed: {fallback[:8]}"] if fallback else []

    out = {
        "model": model,
        "items": accepted,
        "fallback_en": fallback,
        "source_items": len(src),
        "source_chars": sum(len(v) for v in src.values()),
        "ko_chars": sum(len(v) for v in accepted.values()),
        "notes": notes,
        "cost_usd": round(log.cost_usd, 4),
        "llm_calls": log.llm_calls,
        "elapsed_sec": round(log.elapsed_min * 60, 1),
    }
    (run_dir / "brief.ko.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    r = rerender_run(run_dir)                                     # report.md ← 한국어, report.en.md ← 영어 원문
    log.event("translate_end", items=len(accepted), fallback=len(fallback), cost_usd=out["cost_usd"], bytes=r["bytes"])
    return out
