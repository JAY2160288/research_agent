"""CLI.  uv run agent --help"""

from __future__ import annotations

import typer

from .config import load_settings

app = typer.Typer(add_completion=False, help="AI Research Agent (DAS6035 hackathon)")


@app.command()
def run(
    topic: str = typer.Option(..., "--topic", "-t", help="연구 주제 (한국어/영어)"),
    mode: str = typer.Option("baseline", "--mode", "-m", help="baseline (단일 ReAct) | graph (역할 분리 노드)"),
    model: str | None = typer.Option(None, "--model", help="config/models.yaml 의 model 을 이번 실행만 덮어씀"),
    no_cache: bool = typer.Option(False, "--no-cache", help="도구 캐시 끄기 (live 재현)"),
    until: str | None = typer.Option(None, "--until", help="graph 모드: 이 노드까지만 실행 (예: plan)"),
):
    """연구 주제 하나로 파이프라인 실행. 결과는 runs/<timestamp>_<mode>_<topic>/ 에 저장."""
    s = load_settings()
    if model:
        s.llm.model = model
    if not s.anthropic_api_key:
        typer.echo("ANTHROPIC_API_KEY 가 없습니다 (.env 확인)", err=True)
        raise typer.Exit(1)

    if mode == "baseline":
        from .baseline import run_baseline
        brief, log = run_baseline(topic, s, use_cache=not no_cache)
        done = brief is not None
    elif mode == "graph":
        from .graph import run_graph
        state, log = run_graph(topic, s, use_cache=not no_cache, until=until)
        done = state.brief is not None
        if state.plan:
            typer.echo(f"sub-RQ {len(state.plan.sub_rqs)}개: " + "; ".join(sq.question[:60] for sq in state.plan.sub_rqs))
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
