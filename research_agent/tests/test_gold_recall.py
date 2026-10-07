"""scripts/gold_recall.py — 정답 서베이 참고문헌 회수율. 네트워크 없이 캐시·id 정규화·집합 계산만 검증."""

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("gold_recall", ROOT / "scripts" / "gold_recall.py")
gr = importlib.util.module_from_spec(spec)
sys.modules["gold_recall"] = gr
spec.loader.exec_module(gr)


def test_canon_unifies_arxiv_doi_and_arxiv_id():
    assert gr.canon("10.48550/arxiv.2112.10508") == "arxiv:2112.10508"
    assert gr.canon("arxiv:2112.10508v2") == "arxiv:2112.10508"
    assert gr.canon("https://doi.org/10.1145/3748302") == "10.1145/3748302"
    assert gr.canon("10.1007/S44163-025-00495-3") == "10.1007/s44163-025-00495-3"


def test_run_ids_three_stages(tmp_path):
    d = tmp_path / "r"
    d.mkdir()
    brief = {"evidence": {"items": [{"paper_id": "10.1/a"}, {"paper_id": "arxiv:1"}]},
             "synthesis": {"consensus": [{"evidence_ids": ["10.1/a"]}], "conditional": [],
                           "conflicts": [{"side_a": {"evidence_ids": ["arxiv:1"]}, "side_b": {"evidence_ids": ["10.1/a"]}}]},
             "gaps": {"gaps": [{"evidence_ids": ["10.1/a", "10.1/zz"]}]}}
    (d / "brief.json").write_text(json.dumps(brief))
    (d / "papers.json").write_text(json.dumps({"10.1/a": {}, "10.48550/arxiv.1": {}, "10.1/b": {}}))
    ids = gr.run_ids(d)
    assert ids["retrieved"] == {"10.1/a", "arxiv:1", "10.1/b"}
    assert ids["evaluated"] == {"10.1/a", "arxiv:1"}
    assert ids["cited"] == {"10.1/a", "arxiv:1", "10.1/zz"}
    assert gr.run_ids(tmp_path) is None


def test_gold_sets_uses_cache_without_network(tmp_path, monkeypatch):
    monkeypatch.setattr(gr, "GOLD_F", tmp_path / "gold.yaml")
    monkeypatch.setattr(gr, "CACHE_F", tmp_path / "gold_refs.json")
    (tmp_path / "gold.yaml").write_text("gold:\n  T1:\n    - doi: 10.1/s1\n    - doi: 10.1/s2\n", encoding="utf-8")
    (tmp_path / "gold_refs.json").write_text(json.dumps({"10.1/s1": {"refs": ["10.1/x", "10.1/y"]}, "10.1/s2": {"refs": ["10.1/y", "10.1/z"]}}))
    monkeypatch.setattr(gr, "fetch_refs", lambda doi, mailto: (_ for _ in ()).throw(AssertionError("network used")))
    monkeypatch.setattr(gr, "load_settings", lambda: type("S", (), {"contact_email": None})())
    assert gr.gold_sets(refresh=False) == {"T1": {"10.1/x", "10.1/y", "10.1/z"}}


def test_shipped_gold_cache_covers_every_gold_survey():
    """제출 패키지의 캐시가 gold.yaml 의 서베이를 전부 담고 있어야 평가자가 네트워크 없이 재계산한다."""
    import yaml
    gold = yaml.safe_load((ROOT / "eval" / "gold.yaml").read_text(encoding="utf-8"))["gold"]
    cache = json.loads((ROOT / "eval" / "gold_refs.json").read_text(encoding="utf-8"))
    for tid, surveys in gold.items():
        for sv in surveys:
            assert sv["doi"] in cache and len(cache[sv["doi"]]["refs"]) >= 20, (tid, sv["doi"])
