"""CLI.  uv run agent --help"""

from __future__ import annotations

import typer

from .config import load_settings

app = typer.Typer(add_completion=False, help="AI Research Agent (DAS6035 hackathon)")


def _has_korean(text: str) -> bool:
    return any("가" <= ch <= "힣" for ch in text)


def _split_ids(raw: list[str] | None) -> list[str]:
    """--exclude a,b --exclude c → [a, b, c]"""
    out: list[str] = []
    for chunk in raw or []:
        out += [x.strip() for x in chunk.split(",") if x.strip()]
    return out


@app.command()
def run(
    topic: str = typer.Option("", "--topic", "-t", help="연구 주제 (한국어/영어). --resume 때는 생략 가능"),
    mode: str = typer.Option("graph", "--mode", "-m", help="graph (최종 구조: 역할 분리 그래프 + Critic/Replan, 기본) | baseline (단일 ReAct, ablation 기준점)"),
    model: str | None = typer.Option(None, "--model", help="config/models.yaml 의 model 을 이번 실행만 덮어씀"),
    no_cache: bool = typer.Option(False, "--no-cache", help="도구 캐시 끄기 (live 재현)"),
    until: str | None = typer.Option(None, "--until", help="graph 모드: 이 노드까지만 실행 (예: plan)"),
    critic: str | None = typer.Option(None, "--critic", help="graph 모드 품질 게이트: none | deterministic | full (ablation B/C/D)"),
    max_replans: int | None = typer.Option(None, "--max-replans", help="graph 모드 Replan 상한 (기본 config graph.max_replans)"),
    plan_from: str | None = typer.Option(None, "--plan-from", help="graph 모드: 이 실행 폴더의 topic_frame.json·plan.json 을 재사용 (understand·plan 생략, ablation 공정성·OpenAlex 예산 절약)"),
    resume: str | None = typer.Option(None, "--resume", help="graph 모드: 중단된 실행 폴더를 이어서 실행 (끝난 노드는 건너뜀, 같은 폴더에 기록)"),
    exclude: list[str] | None = typer.Option(None, "--exclude", help="제외할 문헌 (DOI 또는 arxiv:<id>, 쉼표 구분·반복 가능). 레지스트리에 들어오지 않아 인용될 수 없다"),
    include: list[str] | None = typer.Option(None, "--include", help="꼭 평가할 문헌 DOI (쉼표 구분·반복 가능). OpenAlex 에서 가져와 모든 sub-RQ 후보에 고정"),
    lang: str | None = typer.Option(None, "--lang", help="ko: 끝난 뒤 리포트 산문을 한국어로 번역(agent translate, +≈$0.12) · en: 번역 안 함. 기본: 주제가 한국어면 ko"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="진행 표시 끄기"),
):
    """연구 주제 하나로 파이프라인 실행. 결과는 runs/<timestamp>_<mode>_<topic>/ 에 저장."""
    from pathlib import Path
    s = load_settings()
    if model:
        s.llm.model = model
    if critic is not None or max_replans is not None:
        from .config import GraphConfig
        s.graph = GraphConfig(  # pydantic 이 잘못된 critic 값을 거른다
            critic=critic or s.graph.critic,  # type: ignore[arg-type]
            max_replans=s.graph.max_replans if max_replans is None else max_replans,
        )
    if not s.anthropic_api_key:
        typer.echo("ANTHROPIC_API_KEY 가 없습니다 (.env 확인)", err=True)
        raise typer.Exit(1)
    if not topic and not resume:
        typer.echo("--topic 을 주거나 --resume <실행 폴더> 를 주세요", err=True)
        raise typer.Exit(1)
    if lang not in (None, "ko", "en"):
        raise typer.BadParameter("--lang 은 ko | en")

    from .progress import Progress
    listeners = [] if quiet else [Progress(typer.echo)]

    if mode == "baseline":
        from .baseline import run_baseline
        if resume or exclude or include:
            typer.echo("--resume / --exclude / --include 는 graph 모드 전용입니다", err=True)
            raise typer.Exit(1)
        brief, log = run_baseline(topic, s, use_cache=not no_cache)
        done = brief is not None
    elif mode == "graph":
        from .graph import run_graph
        try:
            state, log = run_graph(topic, s, use_cache=not no_cache, until=until,
                                   plan_from=Path(plan_from) if plan_from else None,
                                   resume_from=Path(resume) if resume else None,
                                   exclude=_split_ids(exclude), include=_split_ids(include), listeners=listeners)
        except ValueError as e:        # --resume / --plan-from 인자 오류
            typer.echo(str(e), err=True)
            raise typer.Exit(1)
        topic = state.topic
        done = state.brief is not None
        if state.plan:
            typer.echo(f"\nsub-RQ {len(state.plan.sub_rqs)}개: " + "; ".join(sq.question[:60] for sq in state.plan.sub_rqs))
        if state.critiques:
            rounds = ", ".join(f"r{c.round}={'pass' if c.passed else 'fail'}" for c in state.critiques)
            typer.echo(f"Critic {len(state.critiques)}회 ({rounds}) · Replan {state.replan_count}회")
        if state.notes:
            typer.echo("미해결 검사: " + " | ".join(state.notes))
    else:
        raise typer.BadParameter(f"unknown mode {mode}")

    typer.echo(f"\n결과 폴더: {log.dir}")
    typer.echo(f"비용 ${log.cost_usd:.3f} · LLM 호출 {log.llm_calls}회 · {log.elapsed_min:.1f}분")
    if not done:
        if mode == "graph":
            typer.echo("(리포트 없음 — 구현된 노드까지만 실행됨. 중간 산출물은 결과 폴더의 *.json. "
                       "중단된 실행은 `agent run --resume <결과 폴더>` 로 이어갈 수 있습니다)")
        else:
            typer.echo("리포트 생성 실패 (events.jsonl 확인)")
        return

    want_ko = lang == "ko" or (lang is None and _has_korean(topic))
    if want_ko:   # 사후 번역 단계 (ADR-11): brief.json·지표 불변, report.md 만 한국어본 + report.en.md
        from .translate import translate_run
        typer.echo("한국어 번역 중 … (LLM 1회, ≈ $0.12)")
        try:
            r = translate_run(log.dir, s)
            typer.echo(f"번역 {len(r['items'])}/{r['source_items']} 항목 · ${r['cost_usd']:.3f}" +
                       (f" · ⚠ {r['notes'][0]}" if r["notes"] else "") + " · 영어 원문은 report.en.md")
        except Exception as e:  # noqa: BLE001 — 번역 실패는 리포트 완주를 막지 않는다
            typer.echo(f"⚠ 번역 실패, 영어 리포트를 그대로 둡니다: {str(e)[:200]}  (`agent translate {log.dir}` 로 재시도)")
    typer.echo(f"리포트: {log.dir / 'report.md'}")


@app.command()
def export(
    run_dirs: list[str] = typer.Argument(..., help="실행 폴더 (runs/<timestamp>_<mode>_<slug>)"),
    fmt: str = typer.Option("bibtex", "--format", "-f", help="bibtex | ris  (Zotero·EndNote 는 ris, LaTeX 는 bibtex)"),
):
    """리포트 참고문헌을 BibTeX / RIS 로 내보낸다 (LLM·네트워크 없음). 순서·번호는 report.md 의 번호 인용과 같다."""
    from pathlib import Path
    from .export import export_run
    for d in run_dirs:
        try:
            r = export_run(Path(d), fmt)
        except ValueError as e:
            typer.echo(f"skip: {e}", err=True)
            continue
        typer.echo(f"{r['path']}  ({r['refs']}편, {r['bytes'] // 1024}KB)")


@app.command()
def judge(
    run_dirs: list[str] = typer.Argument(None, help="채점할 실행 폴더 (runs/<timestamp>_<mode>_<slug>). 생략하면 --all"),
    all_runs: bool = typer.Option(False, "--all", help="runs/ 의 완주 실행 중 judge.json 이 없는 것 전부"),
    mode: str | None = typer.Option(None, "--mode", help="--all 일 때 baseline | graph 만"),
    since: str = typer.Option("", "--since", help="--all 일 때 이 타임스탬프(폴더명 접두) 이후만. 예: 20261005T000000Z"),
    force: bool = typer.Option(False, "--force", help="이미 judge.json 이 있어도 다시 채점"),
    model: str | None = typer.Option(None, "--model", help="config llm.judge_model 을 이번만 덮어씀"),
):
    """LLM-judge: 완주한 실행의 report.md 를 루브릭 J1~J7 로 채점해 그 폴더에 judge.json 을 남긴다 (eval/rubric.md §B)."""
    from pathlib import Path
    from .config import RUNS_DIR
    from .judge import judge_run, judgeable_runs
    s = load_settings()
    if not s.anthropic_api_key:
        typer.echo("ANTHROPIC_API_KEY 가 없습니다 (.env 확인)", err=True)
        raise typer.Exit(1)
    if run_dirs:
        targets = [Path(d) for d in run_dirs]
    elif all_runs:
        targets = judgeable_runs(RUNS_DIR, mode=mode, since=since, force=force)
    else:
        typer.echo("실행 폴더를 주거나 --all 을 붙이세요", err=True)
        raise typer.Exit(1)
    if not targets:
        typer.echo("채점할 실행이 없습니다 (이미 judge.json 이 있으면 --force)")
        return
    total = 0.0
    for d in targets:
        if (d / "judge.json").exists() and not force and run_dirs:
            typer.echo(f"skip (judge.json 있음, --force 로 재채점): {d.name}")
            continue
        try:
            r = judge_run(d, s, model=model)
        except ValueError as e:
            typer.echo(f"skip: {e}")
            continue
        total += r["cost_usd"]
        scores = " ".join(f"{k}={v}" for k, v in r["scores"].items())
        flag = f"  ⚠ {len(r['flags'])} flag(s)" if r["flags"] else ""
        typer.echo(f"{d.name[:60]}  mean {r['mean']:.2f}  [{scores}]  ${r['cost_usd']:.3f}{flag}")
    typer.echo(f"\n{len(targets)}개 채점, judge 비용 합계 ${total:.3f} (원 실행 cost.json 에는 포함되지 않음)")


@app.command()
def support(
    run_dirs: list[str] = typer.Argument(None, help="검증할 실행 폴더 (runs/<timestamp>_<mode>_<slug>). 생략하면 --all"),
    all_runs: bool = typer.Option(False, "--all", help="runs/ 의 완주 실행 중 support.json 이 없는 것 전부"),
    mode: str | None = typer.Option(None, "--mode", help="--all 일 때 baseline | graph 만"),
    since: str = typer.Option("", "--since", help="--all 일 때 이 타임스탬프(폴더명 접두) 이후만"),
    force: bool = typer.Option(False, "--force", help="이미 support.json 이 있어도 다시 검증"),
    model: str | None = typer.Option(None, "--model", help="config llm.judge_model 을 이번만 덮어씀"),
):
    """주장-근거 지지 검증: §4 종합의 claim 마다 인용 초록이 실제로 뒷받침하는지 (claim, paper) 쌍 단위로 판정해 support.json 을 남긴다 (ADR-10)."""
    from pathlib import Path
    from .config import RUNS_DIR
    from .judge import judgeable_runs, support_run
    s = load_settings()
    if not s.anthropic_api_key:
        typer.echo("ANTHROPIC_API_KEY 가 없습니다 (.env 확인)", err=True)
        raise typer.Exit(1)
    if run_dirs:
        targets = [Path(d) for d in run_dirs]
    elif all_runs:
        targets = judgeable_runs(RUNS_DIR, mode=mode, since=since, force=force, marker="support.json")
    else:
        typer.echo("실행 폴더를 주거나 --all 을 붙이세요", err=True)
        raise typer.Exit(1)
    if not targets:
        typer.echo("검증할 실행이 없습니다 (이미 support.json 이 있으면 --force)")
        return
    total = 0.0
    for d in targets:
        if (d / "support.json").exists() and not force and run_dirs:
            typer.echo(f"skip (support.json 있음, --force 로 재검증): {d.name}")
            continue
        try:
            r = support_run(d, s, model=model)
        except ValueError as e:
            typer.echo(f"skip: {e}")
            continue
        total += r["cost_usd"]
        rate = lambda x: "-" if x is None else f"{x:.0%}"
        typer.echo(f"{d.name[:60]}  citation {rate(r['citation_support_rate'])} (lenient {rate(r['citation_support_rate_lenient'])})"
                   f"  claim {rate(r['claim_support_rate'])}  pairs {r['pairs_supported']}/{r['pairs_partial']}/{r['pairs_unsupported']} sup/par/unsup"
                   f"  no_abstract {r['pairs_no_abstract']}  ${r['cost_usd']:.3f}" + (f"  ⚠ {r['notes']}" if r["notes"] else ""))
    typer.echo(f"\n{len(targets)}개 검증, 비용 합계 ${total:.3f} (원 실행 cost.json 에는 포함되지 않음)")


@app.command()
def translate(
    run_dirs: list[str] = typer.Argument(None, help="번역할 실행 폴더 (runs/<timestamp>_<mode>_<slug>). 생략하면 --all"),
    all_runs: bool = typer.Option(False, "--all", help="runs/ 의 완주 실행 중 brief.ko.json 이 없는 것 전부"),
    mode: str | None = typer.Option(None, "--mode", help="--all 일 때 baseline | graph 만"),
    since: str = typer.Option("", "--since", help="--all 일 때 이 타임스탬프(폴더명 접두) 이후만"),
    force: bool = typer.Option(False, "--force", help="이미 brief.ko.json 이 있어도 다시 번역"),
    model: str | None = typer.Option(None, "--model", help="config llm.translate_model 을 이번만 덮어씀"),
):
    """brief.json 의 산문을 한국어로 옮겨 report.md 를 한국어본으로 다시 그린다 (ADR-11). 영어 원문은 report.en.md 로, brief.json 은 불변.
    LLM 1회 호출(실행당 ≈ $0.05~0.1), 네트워크 검색 없음. 번역 검사(숫자·DOI 보존, 한글, 길이 비율)에 걸린 항목은 영어로 남고 brief.ko.json 의 fallback_en 에 기록."""
    from pathlib import Path
    from .config import RUNS_DIR
    from .judge import judgeable_runs
    from .translate import translate_run
    s = load_settings()
    if not s.anthropic_api_key:
        typer.echo("ANTHROPIC_API_KEY 가 없습니다 (.env 확인)", err=True)
        raise typer.Exit(1)
    if run_dirs:
        targets = [Path(d) for d in run_dirs]
    elif all_runs:
        targets = judgeable_runs(RUNS_DIR, mode=mode, since=since, force=force, marker="brief.ko.json")
    else:
        typer.echo("실행 폴더를 주거나 --all 을 붙이세요", err=True)
        raise typer.Exit(1)
    if not targets:
        typer.echo("번역할 실행이 없습니다 (이미 brief.ko.json 이 있으면 --force)")
        return
    total = 0.0
    for d in targets:
        if (d / "brief.ko.json").exists() and not force and run_dirs:
            typer.echo(f"skip (brief.ko.json 있음, --force 로 재번역): {d.name}")
            continue
        try:
            r = translate_run(d, s, model=model)
        except ValueError as e:
            typer.echo(f"skip: {e}")
            continue
        total += r["cost_usd"]
        typer.echo(f"{d.name[:60]}  {len(r['items'])}/{r['source_items']} 항목  {r['source_chars'] // 1000}k→{r['ko_chars'] // 1000}k자"
                   f"  ${r['cost_usd']:.3f}  {r['llm_calls']}회" + (f"  ⚠ {r['notes'][0]}" if r["notes"] else ""))
    typer.echo(f"\n{len(targets)}개 번역, 비용 합계 ${total:.3f} (원 실행 cost.json 에는 포함되지 않음)")


@app.command()
def render(
    run_dirs: list[str] = typer.Argument(None, help="다시 그릴 실행 폴더 (runs/<timestamp>_<mode>_<slug>). 생략하면 --all"),
    all_runs: bool = typer.Option(False, "--all", help="runs/ 의 완주 실행(brief.json 있는 것) 전부"),
    no_keep: bool = typer.Option(False, "--no-keep", help="기존 report.md 를 report_v1.md 로 보관하지 않음"),
):
    """끝난 실행의 brief.json·papers.json·cost.json 으로 report.md 를 다시 그린다. LLM·네트워크·API 키 불필요.
    렌더러(report.py)를 고친 뒤 기존 실행 전부를 새 형식으로 맞출 때 쓴다 — 지표(cost.json checks)는 바뀌지 않는다."""
    from pathlib import Path
    from .config import RUNS_DIR
    from .report import rerender_run
    if run_dirs:
        targets = [Path(d) for d in run_dirs]
    elif all_runs:
        targets = sorted(d for d in RUNS_DIR.iterdir() if d.is_dir() and (d / "brief.json").exists())
    else:
        typer.echo("실행 폴더를 주거나 --all 을 붙이세요", err=True)
        raise typer.Exit(1)
    n = 0
    for d in targets:
        try:
            r = rerender_run(d, keep_old=not no_keep)
        except ValueError as e:
            typer.echo(f"skip: {e}")
            continue
        n += 1
        typer.echo(f"{d.name[:60]}  참고문헌 {r['refs']}편  {r['bytes'] // 1024}KB")
    typer.echo(f"\n{n}개 다시 그림")


@app.command()
def models():
    """계정에서 사용 가능한 Claude 모델명 출력 (config/models.yaml 설정용)."""
    import anthropic
    s = load_settings()
    c = anthropic.Anthropic(api_key=s.anthropic_api_key)
    for m in c.models.list(limit=50):
        typer.echo(m.id)


@app.command()
def schema(out: str = typer.Option("schemas/brief.json", help="출력 경로")):
    """ResearchBrief JSON Schema 를 내보낸다 (설계 문서용)."""
    import json
    from pathlib import Path
    from .schemas import ResearchBrief
    p = Path(out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ResearchBrief.model_json_schema(), indent=2, ensure_ascii=False), encoding="utf-8")
    typer.echo(f"wrote {p}")


if __name__ == "__main__":
    app()
