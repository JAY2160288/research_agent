"""CLI.  uv run agent --help"""

from __future__ import annotations

import typer

from .config import load_settings

app = typer.Typer(add_completion=False, help="AI Research Agent (DAS6035 hackathon)")


@app.command()
def run(
    topic: str = typer.Option(..., "--topic", "-t", help="연구 주제 (한국어/영어)"),
    mode: str = typer.Option("graph", "--mode", "-m", help="graph (최종 구조: 역할 분리 그래프 + Critic/Replan, 기본) | baseline (단일 ReAct, ablation 기준점)"),
    model: str | None = typer.Option(None, "--model", help="config/models.yaml 의 model 을 이번 실행만 덮어씀"),
    no_cache: bool = typer.Option(False, "--no-cache", help="도구 캐시 끄기 (live 재현)"),
    until: str | None = typer.Option(None, "--until", help="graph 모드: 이 노드까지만 실행 (예: plan)"),
    critic: str | None = typer.Option(None, "--critic", help="graph 모드 품질 게이트: none | deterministic | full (ablation B/C/D)"),
    max_replans: int | None = typer.Option(None, "--max-replans", help="graph 모드 Replan 상한 (기본 config graph.max_replans)"),
    plan_from: str | None = typer.Option(None, "--plan-from", help="graph 모드: 이 실행 폴더의 topic_frame.json·plan.json 을 재사용 (understand·plan 생략, ablation 공정성·OpenAlex 예산 절약)"),
):
    """연구 주제 하나로 파이프라인 실행. 결과는 runs/<timestamp>_<mode>_<topic>/ 에 저장."""
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

    if mode == "baseline":
        from .baseline import run_baseline
        brief, log = run_baseline(topic, s, use_cache=not no_cache)
        done = brief is not None
    elif mode == "graph":
        from .graph import run_graph
        from pathlib import Path
        state, log = run_graph(topic, s, use_cache=not no_cache, until=until,
                               plan_from=Path(plan_from) if plan_from else None)
        done = state.brief is not None
        if state.plan:
            typer.echo(f"sub-RQ {len(state.plan.sub_rqs)}개: " + "; ".join(sq.question[:60] for sq in state.plan.sub_rqs))
        if state.critiques:
            rounds = ", ".join(f"r{c.round}={'pass' if c.passed else 'fail'}" for c in state.critiques)
            typer.echo(f"Critic {len(state.critiques)}회 ({rounds}) · Replan {state.replan_count}회")
        if state.notes:
            typer.echo("미해결 검사: " + " | ".join(state.notes))
    else:
        raise typer.BadParameter(f"unknown mode {mode}")

    typer.echo(f"\n결과 폴더: {log.dir}")
    typer.echo(f"비용 ${log.cost_usd:.3f} · LLM 호출 {log.llm_calls}회 · {log.elapsed_min:.1f}분")
    if done:
        typer.echo(f"리포트: {log.dir / 'report.md'}")
    elif mode == "graph":
        typer.echo("(리포트 없음 — 구현된 노드까지만 실행됨. 중간 산출물은 결과 폴더의 *.json)")
    else:
        typer.echo("리포트 생성 실패 (events.jsonl 확인)")


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
