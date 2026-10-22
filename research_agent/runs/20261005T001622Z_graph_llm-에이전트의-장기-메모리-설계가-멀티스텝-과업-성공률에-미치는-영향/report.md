# Research Brief: LLM 에이전트의 장기 메모리 설계가 멀티스텝 과업 성공률에 미치는 영향

> RQ — LLM 에이전트의 장기 기억(long-term memory) 설계는 다단계 과제의 성공률에 어떤 영향을 미치는가?

> 본문은 영어 원문(brief.json)을 한국어로 옮긴 것이다. 논문 제목·저자·DOI·검색 쿼리·§3 표의 결과 요약은 원문 그대로이며, 영어 원문 리포트는 같은 폴더의 `report.en.md`.

## 요약

312편의 후보 중 73편을 평가했으며, 대부분 프리프린트 형태의 실증 연구, 벤치마크 논문, 서베이로 구성됩니다. 합의된 결과는 외부 경험 메모리(반성, 워크플로, 그래프 메모리, 트레이스 보존)가 무메모리·stateless 기준선보다 순차 의사결정 과업의 성공률을 높인다는 것이며, 단독 효과는 크지 않을 수 있습니다. 대화·QA 벤치마크(LoCoMo, LongMemEval 등)에서는 메모리 단위 크기, 그래프 구조, 반복 검색이 검색 정확도를 높이지만, 이는 멀티스텝 과업 성공률이 아니라 QA 정확도에 대한 근거입니다. 구조화 메모리의 일반적 우위는 확정되지 않았습니다. AriGraph와 AWM은 특정 환경에 맞춰 공동 설계되어 선별된 기준선과 비교된 반면, 통제된 harness 연구는 어떤 substrate도 우세하지 않다고 보고하므로, 이득이 구조 자체보다 도메인 맞춤 설계에서 나왔을 가능성이 있습니다. 조건부 결과로, ALFWorld에서 75% 방해 쓰기가 있을 때 TraceRetain만 성공률(97/100)을 유지했지만, 깨끗한 환경에서는 유지 정책 간 차이가 없었고 단일 환경·2개 시드 결과입니다. 광범위한 검색은 장문 QA에는 도움이 되나 순차 의사결정에는 해로울 수 있습니다. 핵심 Gap은 (1) 에피소드·의미·계층 메모리를 에이전트 루프를 고정한 채 직접 비교한 연구의 부재와 (2) 메모리 검색을 계획·분해 루프 안에서 분리해 검증한 연구의 부재입니다. 비용·지연·오류 전파와 통합·망각 효과에 대한 통제된 근거도 거의 없습니다.

## 먼저 읽을 문헌 (10편)

Evaluator 의 관련성(rel)·신뢰도(reli) 점수 순. 전체 평가 표는 §3, 서지 정보는 참고문헌.

| # | 문헌 | 핵심 결과 | sub-RQ | rel · reli |
|---|---|---|---|---|
| [1] | Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents (2026) | 모든 상황에서 우세한 단일 기억 기반(memory substrate)은 없다. 폭넓은 검색(retrieval)은 장문 맥락 사실 질의응답(QA)에 도움이 되지만, 과도한 검색은 순차적 의사결정을 해칠 수 있다. 일부 기억 기반은 더 긴 시계(horizon)에서 비용이 커지거나 취약해진… | rq1, rq2, rq5, rq6 | 5 · 4 |
| [2] | Evaluating Memory in LLM Agents via Incremental Multi-Turn Interactions (2025) | MemoryAgentBench는 점진적 다중 턴 형식을 사용하여 기억 에이전트를 정확한 검색, 테스트 시점 학습(test-time learning), 장거리 이해, 선택적 망각(selective forgetting)의 네 가지 역량에 대해 평가한다. 초록은 결과가 나오기 전에 잘려 있… | rq1, rq3, rq4, rq5 | 5 · 4 |
| [3] | AriGraph: Learning Knowledge Graph World Models with Episodic Memory for LLM Ag… (2024) | AriGraph는 의미 기억(semantic memory)과 일화 기억(episodic memory)을 통합하는 기억 그래프를 구축하고 갱신하며, Ariadne 에이전트는 텍스트 게임 과제에서 다른 기억 방법(전체 이력, 요약, 검색 증강)과 강력한 강화학습(RL) 기준선을 크게 능가… | rq1, rq2, rq3, rq4, rq5 | 5 · 4 |
| [4] | A Survey on the Memory Mechanism of Large Language Model based Agents (2024) | LLM 기반 에이전트의 기억 메커니즘을 개괄하며, 기억이 무엇이고 왜 필요한지, 기억 모듈을 어떻게 설계하고 평가하는지, 그리고 응용 사례를 다룬다. 또한 기존 연구의 한계와 향후 방향을 분석한다. | rq1, rq2, rq3, rq5, rq6 | 5 · 4 |
| [5] | Reflexion: Language Agents with Verbal Reinforcement Learning (2023) | Reflexion 에이전트는 언어로 된 자기 성찰을 일화 기억 버퍼에 저장하여 이후 시행을 개선하며, 여러 과제에서 기준선보다 유의미한 향상을 보인다. HumanEval에서 pass@1 91%를 달성하여 GPT-4의 80%를 넘어선다. | rq1, rq3, rq4, rq5 | 5 · 4 |
| [6] | AdMem: Advanced Memory for Task-solving Agents (2026) | AdMem은 행위자(actor), 기억(memory), 비평자(critic) 에이전트로 구성된 이중 수준의 단기/장기 설계에서 의미 기억, 일화 기억, 절차 기억(procedural memory)을 결합한다. 보상 기반 병합과 가지치기(pruning)가 긴 다중 턴 과제에서 견고성과… | rq1, rq2, rq3 | 5 · 3 |
| [7] | Selective Memory Retention for Long-Horizon LLM Agents (2026) | 외부 기억은 기억이 없는 경우보다 성능을 높인다. 보류(held-out) 과제 50개 중 47-49개를 해결하여 39/50과 대비된다. 제한적 보존 정책(bounded retention policies)은 교란 요소가 없는 ALFWorld에서 통계적으로 구별되지 않는다. 방해 항목 기… | rq1, rq2, rq3, rq5, rq6 | 5 · 3 |
| [8] | MemoryArena: Benchmarking Agent Memory in Interdependent Multi-Session Agentic… (2026) | MemoryArena는 상호 의존적인 하위 과제가 있는 다중 세션 에이전트-환경 루프에서 기억의 획득과 활용을 함께 평가한다. 초록은 중간에 잘려 있지만, 기존 벤치마크에서 성능이 거의 포화에 가까운 에이전트가 여기서는 더 낮은 성능을 보인다고 시사한다. | rq2, rq4, rq5 | 5 · 3 |
| [9] | Cognitive Extensions for Dual-Process Language Agents: Memory and Self-Reflecti… (2026) | 전체 시스템(일화적 적응형 기억 모듈(Adaptive Memory Module)과 자기 성찰 모듈(Self-Reflection Module))이 평균 점수 (64.62), 성공률 (43.17%), 단계 효율 (19.33 steps)에서 최고 성적을 달성했다. 자기 성찰이 단독으로 가장… | rq1, rq3, rq4, rq5 | 5 · 3 |
| [10] | Vector Storage Based Long-term Memory Research on LLM (2024) | VIMBank는 동적 갱신과 에빙하우스 망각 곡선(Ebbinghaus forgetting curve)에 기반한 망각을 갖춘 벡터 저장소(vector-store) 방식의 장기 기억이다. 비교 대상 에이전트보다 과제 의사결정 성공률을 10-20% 높이고 추론 비용을 약 23% 줄인다고 보… | rq1, rq2, rq3, rq6 | 5 · 3 |

## 1. 주제 재정의

- RQ: LLM 에이전트의 장기 기억(long-term memory) 설계는 다단계 과제의 성공률에 어떤 영향을 미치는가?
- 독립변수: Long-term memory design of LLM agents (e.g., memory architecture, storage, retrieval, and update mechanisms)
- 종속변수: Multi-step task success rate
- 대상: LLM-based autonomous agents
- 핵심 개념: LLM agents, long-term memory, memory architecture, multi-step tasks, task success rate, retrieval-augmented memory, agent planning

## 2. 조사 계획

전략: 명시적 기억 설계를 갖춘 LLM 에이전트가 최근에 등장했으므로 2022–2025년 문헌에 초점을 맞추며, OpenAlex 기록과 함께 arXiv 사전 출판물(preprint)과 주요 학회(NeurIPS, ICLR, ACL, EMNLP)를 우선한다. 절제 실험(ablation)이나 벤치마크 비교를 수행한 실증 연구(예: ALFWorld, WebArena, 장기 시계 에이전트 벤치마크)와 분류 체계를 위한 서베이를 선호하며, 순수 장문 맥락 모델링이나 비 LLM 강화학습 기억에 관한 논문은 에이전트를 직접 다루지 않는 한 제외한다. 문헌이 가장 빈약할 것으로 예상되는 곳은 rq6(실패 양상과 비용)과 rq1/rq3에서 기억 설계의 효과를 분리하는 통제 비교이다.

- **rq1** 서로 다른 장기 기억 아키텍처(예: 일화, 의미, 계층, 벡터 저장소, 그래프 기반)는 다단계 과제에서 LLM 에이전트의 과제 성공률에 어떤 영향을 미치는가?

- **rq2** 기억 검색 및 저장 메커니즘(검색 증강 기억, 색인, 관련도 점수화, 요약)은 순차적 과제에서 에이전트의 성공에 어떤 영향을 미치는가?

- **rq3** 기억의 갱신, 통합(consolidation), 성찰(reflection), 망각 메커니즘은 장기간의 상호작용과 반복 과제에서 에이전트 성능에 어떤 영향을 미치는가?

- **rq4** 장기 기억은 에이전트의 계획 및 추론 모듈과 어떻게 상호작용하여 장기 시계 과제의 완수를 뒷받침하는가?

- **rq5** LLM 에이전트에서 기억이 다단계 과제 성공률에 기여하는 정도를 평가하는 데 어떤 벤치마크, 지표, 절제 실험 방법론이 사용되는가?

- **rq6** LLM 에이전트의 장기 기억에서는 어떤 한계, 실패 양상, 비용(예: 기억 잡음, 오류 전파, 맥락 과부하, 지연 시간)이 발생하는가?

<details><summary>검색 쿼리 전체 (27개 — Replan 으로 추가된 쿼리 포함)</summary>

- **rq1** (4개): LLM agent long-term memory architecture task success; memory-augmented language agents long-horizon tasks; episodic memory LLM agents multi-step performance; hierarchical graph memory autonomous language agents

- **rq2** (4개): retrieval-augmented memory LLM agents sequential decision-making; external memory retrieval strategy agent task completion; memory write summarization compression LLM agents; embedding-based memory retrieval agent benchmark

- **rq3** (4개): memory update forgetting mechanism LLM agents; reflection experience learning language agents memory; memory consolidation long-term agent self-improvement; lifelong learning LLM agent experience memory

- **rq4** (7개): agent planning memory integration long-horizon tasks; LLM agent planning with memory-augmented reasoning; autonomous language agents memory and task decomposition; tool-using agents memory planning success rate; memory-conditioned planner ablation long-horizon embodied agents; plan reuse experience retrieval LLM agent planning; ReAct Reflexion with and without memory ablation

- **rq5** (4개): benchmark evaluating LLM agent memory long-horizon; ablation study memory module agent success rate; long-term memory evaluation conversational agents benchmark; agent benchmark task completion rate memory comparison

- **rq6** (4개): memory errors propagation LLM agents failure analysis; irrelevant memory retrieval degrades agent performance; long-term memory latency cost trade-off language agents; hallucination stale memory autonomous agents

</details>

## 3. Evidence Table

### 3.1 Evidence map — sub-RQ × 신뢰도

| sub-RQ | 편수 (rel ≥ 3) | 신뢰도 4~5 | 신뢰도 3 | 신뢰도 ≤ 2 | 평균 신뢰도 | 커버 |
|---|---|---|---|---|---|---|
| rq1 | 27 | 8 | 15 | 4 | 3.1 | ✅ |
| rq2 | 23 | 5 | 15 | 3 | 3.1 | ✅ |
| rq3 | 19 | 5 | 11 | 3 | 3.1 | ✅ |
| rq4 | 19 | 5 | 12 | 2 | 3.2 | ✅ |
| rq5 | 19 | 8 | 10 | 1 | 3.4 | ✅ |
| rq6 | 10 | 3 | 6 | 1 | 3.2 | ✅ |

커버 기준은 Critic 결정적 검사와 같다 (relevance ≥ 3 인 문헌 3편 이상). 신뢰도는 Evaluator 가 설계·표본·출처로 매긴 0~5 점.

### 3.2 sub-RQ 별 문헌

#### rq1 — 서로 다른 장기 기억 아키텍처(예: 일화, 의미, 계층, 벡터 저장소, 그래프 기반)는 다단계 과제에서 LLM 에이전트의 과제 성공률에 어떤 영향을 미치는가?

32편 (rel ≥ 3: 27편) · 신뢰도 평균 3.0 · 상위: [3] AriGraph: Learning Knowledge Graph World Models with Episod… (2024) (reli 4); [5] Reflexion: Language Agents with Verbal Reinforcement Learni… (2023) (reli 4); [2] Evaluating Memory in LLM Agents via Incremental Multi-Turn… (2025) (reli 4)

<details><summary>전체 표 (32편)</summary>

| # | 문헌 | rel | reli | method | sample | finding |
|---|---|---|---|---|---|---|
| [3] | AriGraph: Learning Knowledge Graph World Models with Episodic Memory… (2024) | 5 | 4 | empirical evaluation of a graph-based memory agent against memory and RL baseli… | interactive text game environments of varying complexity | AriGraph는 의미 기억(semantic memory)과 일화 기억(episodic memory)을 통합하는 기억 그래프를 구축하고 갱신하며, Ariadne 에이전트는 텍스트 게임 과제에서 다른 기억 방법(전체 이력, 요약, 검색 증강)과 강력한 강화학습(RL) 기준선을 크게 능가… |
| [5] | Reflexion: Language Agents with Verbal Reinforcement Learning (2023) | 5 | 4 | empirical evaluation of a framework with ablations across tasks | Sequential decision-making, coding (HumanEval), and languag… | Reflexion 에이전트는 언어로 된 자기 성찰을 일화 기억 버퍼에 저장하여 이후 시행을 개선하며, 여러 과제에서 기준선보다 유의미한 향상을 보인다. HumanEval에서 pass@1 91%를 달성하여 GPT-4의 80%를 넘어선다. |
| [2] | Evaluating Memory in LLM Agents via Incremental Multi-Turn Interactio… (2025) | 5 | 4 | benchmark construction (MemoryAgentBench) and evaluation of memory agents |  | MemoryAgentBench는 점진적 다중 턴 형식을 사용하여 기억 에이전트를 정확한 검색, 테스트 시점 학습(test-time learning), 장거리 이해, 선택적 망각(selective forgetting)의 네 가지 역량에 대해 평가한다. 초록은 결과가 나오기 전에 잘려 있… |
| [1] | Harness the Memory: A Holistic Evaluation of Memory Substrates in Mem… (2026) | 5 | 4 | controlled harness evaluation of memory substrates | three backbone models, four benchmark suites, 26 metrics | 모든 상황에서 우세한 단일 기억 기반(memory substrate)은 없다. 폭넓은 검색(retrieval)은 장문 맥락 사실 질의응답(QA)에 도움이 되지만, 과도한 검색은 순차적 의사결정을 해칠 수 있다. 일부 기억 기반은 더 긴 시계(horizon)에서 비용이 커지거나 취약해진… |
| [4] | A Survey on the Memory Mechanism of Large Language Model based Agents (2024) | 5 | 4 | systematic survey/literature review |  | LLM 기반 에이전트의 기억 메커니즘을 개괄하며, 기억이 무엇이고 왜 필요한지, 기억 모듈을 어떻게 설계하고 평가하는지, 그리고 응용 사례를 다룬다. 또한 기존 연구의 한계와 향후 방향을 분석한다. |
| [6] | AdMem: Advanced Memory for Task-solving Agents (2026) | 5 | 3 | framework proposal with experiments across environments |  | AdMem은 행위자(actor), 기억(memory), 비평자(critic) 에이전트로 구성된 이중 수준의 단기/장기 설계에서 의미 기억, 일화 기억, 절차 기억(procedural memory)을 결합한다. 보상 기반 병합과 가지치기(pruning)가 긴 다중 턴 과제에서 견고성과… |
| [10] | Vector Storage Based Long-term Memory Research on LLM (2024) | 5 | 3 | proposed system (VIMBank) with experimental comparison against other agents |  | VIMBank는 동적 갱신과 에빙하우스 망각 곡선(Ebbinghaus forgetting curve)에 기반한 망각을 갖춘 벡터 저장소(vector-store) 방식의 장기 기억이다. 비교 대상 에이전트보다 과제 의사결정 성공률을 10-20% 높이고 추론 비용을 약 23% 줄인다고 보… |
| [7] | Selective Memory Retention for Long-Horizon LLM Agents (2026) | 5 | 3 | controlled empirical study on ALFWorld with ablated retention policies (two see… | ALFWorld with gpt-5-mini; held-out evaluation of 50 tasks | 외부 기억은 기억이 없는 경우보다 성능을 높인다. 보류(held-out) 과제 50개 중 47-49개를 해결하여 39/50과 대비된다. 제한적 보존 정책(bounded retention policies)은 교란 요소가 없는 ALFWorld에서 통계적으로 구별되지 않는다. 방해 항목 기… |
| [9] | Cognitive Extensions for Dual-Process Language Agents: Memory and Sel… (2026) | 5 | 3 | controlled ablation study on ScienceWorld (4 configurations: baseline, +AMM, +S… | ScienceWorld interactive environment | 전체 시스템(일화적 적응형 기억 모듈(Adaptive Memory Module)과 자기 성찰 모듈(Self-Reflection Module))이 평균 점수 (64.62), 성공률 (43.17%), 단계 효율 (19.33 steps)에서 최고 성적을 달성했다. 자기 성찰이 단독으로 가장… |
| [11] | On the Structural Memory of LLM Agents (2024) | 4 | 4 | empirical comparison of memory structures and retrieval methods across 4 tasks… | four tasks, six datasets | Different memory structures (chunks, triples, atomic facts, summaries, mixed) suit different tasks, and mixed memory is resilient in noisy settings. Iterative… |
| [12] | Agent Workflow Memory (2024) | 4 | 4 | empirical benchmark evaluation (offline and online) on Mind2Web and WebArena | 1000+ tasks across 200+ domains | Agent Workflow Memory induces reusable workflows from past experience and supplies them to guide the agent. It improves relative success rate by 24.6% on Mind2… |
| [13] | Context-Aware Planning and Environment-Aware Memory for Instruction F… (2023) | 4 | 4 | method proposal with benchmark evaluation | interactive instruction-following benchmark, seen and unsee… | CAPEAM combines context-aware planning with environment-aware memory of object states and locations, reaching state-of-the-art results with up to +10.70% gain… |
| [14] | PlugMem: A Task-Agnostic Plugin Memory Module for LLM Agents (2026) | 4 | 3 | method proposal with evaluation on three benchmarks | three heterogeneous benchmarks (conversational QA, multi-ho… | PlugMem structures episodic memory into a knowledge-centric memory graph to reduce context explosion from raw retrieval. It is evaluated unchanged across three… |
| [15] | MemGym: a Long-Horizon Memory Environment for LLM Agents (2026) | 4 | 3 | benchmark/environment construction with five evaluation tracks | Five tracks: tau2-bench, MEMGYM-DR, SWE-Gym, MEMGYM-CODEQA,… | MemGym is a benchmark for agentic memory spanning tool-use dialogue, deep-research search, coding and computer use. It reports memory-isolated scores that deco… |
| [16] | Retrieval-Driven Memory Reconsolidation for Long-Term LLM Agents (2026) | 4 | 3 | method proposal with benchmark evaluation and ablations | LoCoMo and LongMemEval benchmarks | REALM organizes memory as a heterogeneous cognitive graph with adaptive graph-search retrieval and retrieval-driven reconsolidation. It reaches 75.97% accuracy… |
| [17] | A survey on large language model based autonomous agents (2024) | 3 | 3 | narrative survey of LLM-based autonomous agents |  | Proposes a unified framework for constructing LLM-based autonomous agents and reviews applications and evaluation strategies. The abstract does not report memo… |
| [18] | A Survey on Large Language Model based Autonomous Agents (2023) | 3 | 3 | narrative survey of LLM-based autonomous agents (preprint version) |  | Proposes a unified framework for building LLM-based agents and surveys applications and evaluation strategies. The abstract does not report memory-specific eff… |
| [19] | JARVIS -1: Open-World Multi-Task Agents With Memory-Augmented Multimo… (2024) | 3 | 3 | empirical agent system evaluation in Minecraft | over 200 Minecraft tasks | JARVIS-1 uses a multimodal memory to support planning with pre-trained knowledge and game experiences, and completes over 200 different tasks in Minecraft. The… |
| [20] | JARVIS-1: Open-World Multi-task Agents with Memory-Augmented Multimod… (2023) | 3 | 3 | empirical agent system evaluation in Minecraft (preprint) | over 200 Minecraft tasks | JARVIS-1 uses a multimodal memory combining pre-trained knowledge and game experiences to plan, and completes over 200 tasks in Minecraft. The abstract is trun… |
| [21] | Memory is Reconstructed, Not Retrieved: Graph Memory for LLM Agents (2026) | 3 | 3 | method proposal (MRAgent) with benchmark experiments | LoCoMo and LongMemEval benchmarks | A Cue-Tag-Content memory graph with active reconstruction improves over strong baselines by up to 23% while reducing token and runtime cost. Retrieval is adapt… |
| [22] | El Agente: An autonomous agent for quantum chemistry (2025) | 3 | 3 | system description with benchmarking on course exercises and case studies | six university-level course exercises and two case studies | El Agente Q uses a hierarchical memory framework within its cognitive architecture and reaches an average task success above 87%. It also supports longer multi… |
| [23] | From Single to Multi-Granularity: Toward Long-Term Memory Association… (2025) | 3 | 3 | method proposal (MemGAS) with empirical evaluation |  | MemGAS uses multi-granularity memory units, GMM-based clustering and association, and an entropy-based router to pick the retrieval granularity. It aims to bal… |
| [24] | KnowAgent: Knowledge-Augmented Planning for LLM-Based Agents (2024) | 3 | 3 | method proposal with benchmark experiments | HotpotQA and ALFWorld with various backbone LLMs | KnowAgent uses an action knowledge base and self-learning to constrain planning paths, achieving comparable or superior performance to baselines and reducing p… |
| [25] | Rosetta Memory: Adaptive Memory for Cross-LLM Agents (2026) | 3 | 2 | method proposal with jointly trained write/read operators (details unclear from… |  | Proposes memory-centric adaptation so that memory written by one LLM can be consumed by another, via profile-conditioned write and read operators. The abstract… |
| [26] | LeanMem: Simple and Efficient Long-Term Memory for LLM Agents (2026) | 3 | 2 | unclear from abstract (system proposal evaluated on LoCoMo and LongMemEval-S be… |  | LeanMem is a lightweight long-term memory framework that filters low-value content and stores it as profile, event, or record memory. It selectively updates on… |
| [27] | Mind-Tool: Domain Memory Architecture for AI Agents (2026) | 3 | 2 | single-system production deployment case study (90 days), no stated baseline be… | One IT infrastructure management deployment (Proxmox, Kuber… | Mind-Tool, which combines a persistent memory layer, a desired-state goal model and a reasoning engine, reported a 94% task success rate, 68% workflow automati… |
| [28] | Review of Case-Based Reasoning for LLM Agents: Theoretical Foundation… (2025) | 3 | 2 | narrative/systematic review with a mathematical formalization of CBR; no clear… |  | The paper reviews how Case-Based Reasoning (case retrieval, adaptation, learning) can be integrated into LLM agents to supply experience-based memory. It compa… |
| [29] | A Language Agent for Autonomous Driving (2023) | 2 | 3 | empirical evaluation on nuScenes benchmark | nuScenes driving benchmark | Agent-Driver combines a tool library, a cognitive memory of common sense and experiential knowledge, and an LLM reasoning engine, and reportedly outperforms st… |
| [30] | Scene Memory Transformer for Embodied Agents in Long-Horizon Tasks (2019) | 2 | 3 | empirical evaluation of a memory-based RL policy on visual navigation tasks |  | Scene Memory Transformer stores observations in memory and uses attention over them, outperforming reactive and memory-based policies on visual navigation task… |
| [31] | Semantic Memory Modeling and Memory Interaction in Learning Agents (2016) | 2 | 3 | model proposal with experimental studies (fusion ART neural network) | Domains including the Unreal Tournament first-person shooti… | Presents a self-organizing semantic memory model that consolidates knowledge from episodic memory and interacts with procedural memory for more effective decis… |
| [32] | Agents: An Open-source Framework for Autonomous Language Agents (2023) | 2 | 2 | open-source library/framework description |  | The Agents library supports planning, memory, tool use and multi-agent communication in a modular design for building language agents. The abstract reports no… |
| [33] | A Novel Model of Narrative Memory for Conscious Agents (2024) | 2 | 1 | conceptual model proposal |  | Proposes a narrative memory module for conscious agents to create, store and recall narrative representations of past experiences. The abstract claims it would… |

</details>

#### rq2 — 기억 검색 및 저장 메커니즘(검색 증강 기억, 색인, 관련도 점수화, 요약)은 순차적 과제에서 에이전트의 성공에 어떤 영향을 미치는가?

26편 (rel ≥ 3: 23편) · 신뢰도 평균 3.0 · 상위: [3] AriGraph: Learning Knowledge Graph World Models with Episod… (2024) (reli 4); [1] Harness the Memory: A Holistic Evaluation of Memory Substra… (2026) (reli 4); [4] A Survey on the Memory Mechanism of Large Language Model ba… (2024) (reli 4)

<details><summary>전체 표 (26편)</summary>

| # | 문헌 | rel | reli | method | sample | finding |
|---|---|---|---|---|---|---|
| [3] | AriGraph: Learning Knowledge Graph World Models with Episodic Memory… (2024) | 5 | 4 | empirical evaluation of a graph-based memory agent against memory and RL baseli… | interactive text game environments of varying complexity | AriGraph는 의미 기억(semantic memory)과 일화 기억(episodic memory)을 통합하는 기억 그래프를 구축하고 갱신하며, Ariadne 에이전트는 텍스트 게임 과제에서 다른 기억 방법(전체 이력, 요약, 검색 증강)과 강력한 강화학습(RL) 기준선을 크게 능가… |
| [1] | Harness the Memory: A Holistic Evaluation of Memory Substrates in Mem… (2026) | 5 | 4 | controlled harness evaluation of memory substrates | three backbone models, four benchmark suites, 26 metrics | 모든 상황에서 우세한 단일 기억 기반(memory substrate)은 없다. 폭넓은 검색(retrieval)은 장문 맥락 사실 질의응답(QA)에 도움이 되지만, 과도한 검색은 순차적 의사결정을 해칠 수 있다. 일부 기억 기반은 더 긴 시계(horizon)에서 비용이 커지거나 취약해진… |
| [4] | A Survey on the Memory Mechanism of Large Language Model based Agents (2024) | 5 | 4 | systematic survey/literature review |  | LLM 기반 에이전트의 기억 메커니즘을 개괄하며, 기억이 무엇이고 왜 필요한지, 기억 모듈을 어떻게 설계하고 평가하는지, 그리고 응용 사례를 다룬다. 또한 기존 연구의 한계와 향후 방향을 분석한다. |
| [6] | AdMem: Advanced Memory for Task-solving Agents (2026) | 5 | 3 | framework proposal with experiments across environments |  | AdMem은 행위자(actor), 기억(memory), 비평자(critic) 에이전트로 구성된 이중 수준의 단기/장기 설계에서 의미 기억, 일화 기억, 절차 기억(procedural memory)을 결합한다. 보상 기반 병합과 가지치기(pruning)가 긴 다중 턴 과제에서 견고성과… |
| [10] | Vector Storage Based Long-term Memory Research on LLM (2024) | 5 | 3 | proposed system (VIMBank) with experimental comparison against other agents |  | VIMBank는 동적 갱신과 에빙하우스 망각 곡선(Ebbinghaus forgetting curve)에 기반한 망각을 갖춘 벡터 저장소(vector-store) 방식의 장기 기억이다. 비교 대상 에이전트보다 과제 의사결정 성공률을 10-20% 높이고 추론 비용을 약 23% 줄인다고 보… |
| [7] | Selective Memory Retention for Long-Horizon LLM Agents (2026) | 5 | 3 | controlled empirical study on ALFWorld with ablated retention policies (two see… | ALFWorld with gpt-5-mini; held-out evaluation of 50 tasks | 외부 기억은 기억이 없는 경우보다 성능을 높인다. 보류(held-out) 과제 50개 중 47-49개를 해결하여 39/50과 대비된다. 제한적 보존 정책(bounded retention policies)은 교란 요소가 없는 ALFWorld에서 통계적으로 구별되지 않는다. 방해 항목 기… |
| [8] | MemoryArena: Benchmarking Agent Memory in Interdependent Multi-Sessio… (2026) | 5 | 3 | benchmark construction with human-crafted multi-session agentic tasks | tasks across web navigation, preference-constrained plannin… | MemoryArena는 상호 의존적인 하위 과제가 있는 다중 세션 에이전트-환경 루프에서 기억의 획득과 활용을 함께 평가한다. 초록은 중간에 잘려 있지만, 기존 벤치마크에서 성능이 거의 포화에 가까운 에이전트가 여기서는 더 낮은 성능을 보인다고 시사한다. |
| [11] | On the Structural Memory of LLM Agents (2024) | 4 | 4 | empirical comparison of memory structures and retrieval methods across 4 tasks… | four tasks, six datasets | Different memory structures (chunks, triples, atomic facts, summaries, mixed) suit different tasks, and mixed memory is resilient in noisy settings. Iterative… |
| [34] | RAP: Retrieval-Augmented Planning with Contextual Memory for Multimod… (2024) | 4 | 3 | method proposal with empirical evaluation (details unclear from abstract) |  | RAP retrieves past experiences relevant to the current context to enhance planning, reporting SOTA in textual scenarios and improved multimodal agent performan… |
| [35] | TRAD: Enhancing LLM Agents with Step-Wise Thought Retrieval and Align… (2024) | 4 | 3 | method proposal (TRAD) with empirical evaluation (details unclear from abstract) |  | Step-level thought retrieval and aligned decision select more helpful demonstrations with less irrelevant context than trajectory-level retrieval. It targets s… |
| [14] | PlugMem: A Task-Agnostic Plugin Memory Module for LLM Agents (2026) | 4 | 3 | method proposal with evaluation on three benchmarks | three heterogeneous benchmarks (conversational QA, multi-ho… | PlugMem structures episodic memory into a knowledge-centric memory graph to reduce context explosion from raw retrieval. It is evaluated unchanged across three… |
| [15] | MemGym: a Long-Horizon Memory Environment for LLM Agents (2026) | 4 | 3 | benchmark/environment construction with five evaluation tracks | Five tracks: tau2-bench, MEMGYM-DR, SWE-Gym, MEMGYM-CODEQA,… | MemGym is a benchmark for agentic memory spanning tool-use dialogue, deep-research search, coding and computer use. It reports memory-isolated scores that deco… |
| [16] | Retrieval-Driven Memory Reconsolidation for Long-Term LLM Agents (2026) | 4 | 3 | method proposal with benchmark evaluation and ablations | LoCoMo and LongMemEval benchmarks | REALM organizes memory as a heterogeneous cognitive graph with adaptive graph-search retrieval and retrieval-driven reconsolidation. It reaches 75.97% accuracy… |
| [36] | IFCMemoryBench: Evaluating Long-Term Memory of LLM-Based Agents in BI… (2026) | 4 | 3 | benchmark construction and evaluation | 143 multi-session tasks across 19 BIM projects and 4,016 pr… | Introduces IFCMemoryBench to evaluate long-term memory when agents must combine remembered context from earlier sessions with live IFC queries. The framework d… |
| [37] | On Memory Construction and Retrieval for Personalized Conversational… (2025) | 3 | 4 | empirical analysis plus method proposal (SeCom) evaluated on benchmarks | LOCOMO and Long-MT-Bench+ benchmarks | Memory unit granularity matters, and prompt compression (LLMLingua-2) works as a denoiser to improve retrieval accuracy. Segment-level memory (SeCom) significa… |
| [21] | Memory is Reconstructed, Not Retrieved: Graph Memory for LLM Agents (2026) | 3 | 3 | method proposal (MRAgent) with benchmark experiments | LoCoMo and LongMemEval benchmarks | A Cue-Tag-Content memory graph with active reconstruction improves over strong baselines by up to 23% while reducing token and runtime cost. Retrieval is adapt… |
| [38] | Towards Improving Sequential Decision-Making in LLM Agents via Experi… (2026) | 3 | 3 | empirical evaluation on two-player zero-sum games with experience-memory agent… | Tic-tac-toe, Connect Four; multiple model tiers; MCTS oppon… | LLMs play suboptimally in simple games and lose to MCTS opponents, and obfuscating the surface form leaves performance largely unchanged. An experience memory… |
| [39] | Think-in-Memory: Recalling and Post-thinking Enable LLMs with Long-Te… (2023) | 3 | 3 | method proposal (TiM memory mechanism), evaluation details not in abstract |  | TiM stores historical thoughts in an evolving memory, recalls them before responding and post-thinks to update memory after responding. This is meant to avoid… |
| [23] | From Single to Multi-Granularity: Toward Long-Term Memory Association… (2025) | 3 | 3 | method proposal (MemGAS) with empirical evaluation |  | MemGAS uses multi-granularity memory units, GMM-based clustering and association, and an entropy-based router to pick the retrieval granularity. It aims to bal… |
| [40] | State Contamination in Memory-Augmented LLM Agents (2026) | 3 | 3 | paired counterfactual multi-agent rollouts |  | Toxic content compressed into memory summaries can fall below toxicity detection thresholds yet still raise downstream toxicity. Raw transcript reuse drives ov… |
| [25] | Rosetta Memory: Adaptive Memory for Cross-LLM Agents (2026) | 3 | 2 | method proposal with jointly trained write/read operators (details unclear from… |  | Proposes memory-centric adaptation so that memory written by one LLM can be consumed by another, via profile-conditioned write and read operators. The abstract… |
| [26] | LeanMem: Simple and Efficient Long-Term Memory for LLM Agents (2026) | 3 | 2 | unclear from abstract (system proposal evaluated on LoCoMo and LongMemEval-S be… |  | LeanMem is a lightweight long-term memory framework that filters low-value content and stores it as profile, event, or record memory. It selectively updates on… |
| [28] | Review of Case-Based Reasoning for LLM Agents: Theoretical Foundation… (2025) | 3 | 2 | narrative/systematic review with a mathematical formalization of CBR; no clear… |  | The paper reviews how Case-Based Reasoning (case retrieval, adaptation, learning) can be integrated into LLM agents to supply experience-based memory. It compa… |
| [41] | Toward Conversational Agents with Context and Time Sensitive Long-ter… (2024) | 2 | 3 | new dataset construction and retrieval model evaluation | new dataset of ambiguous and time-based questions built on… | Standard RAG handles time/event-based and ambiguous queries over long conversations poorly. A new retrieval model combining chain-of-table search and vector-da… |
| [42] | Enhancing Group Recommendation with Memory-Augmented Reasoning in LLM… (2026) | 2 | 2 | unclear from abstract (method proposal, LLM agent with memory and reasoning mod… |  | Proposes AGR, an LLM agent for group recommendation with a hash-table memory module supporting insertion, updating, retrieval, forgetting and summarization, pl… |
| [43] | Agentic MailBot: Autonomous Multi-Agent Email Response System with Co… (2026) | 1 | 2 | system implementation with reported metrics |  | A multi-agent email response system combining RAG over vector databases and ReAct agents with SQL toolkit reached 91.2% classification accuracy and an 88.4% en… |

</details>

#### rq3 — 기억의 갱신, 통합(consolidation), 성찰(reflection), 망각 메커니즘은 장기간의 상호작용과 반복 과제에서 에이전트 성능에 어떤 영향을 미치는가?

21편 (rel ≥ 3: 19편) · 신뢰도 평균 3.0 · 상위: [3] AriGraph: Learning Knowledge Graph World Models with Episod… (2024) (reli 4); [5] Reflexion: Language Agents with Verbal Reinforcement Learni… (2023) (reli 4); [2] Evaluating Memory in LLM Agents via Incremental Multi-Turn… (2025) (reli 4)

<details><summary>전체 표 (21편)</summary>

| # | 문헌 | rel | reli | method | sample | finding |
|---|---|---|---|---|---|---|
| [3] | AriGraph: Learning Knowledge Graph World Models with Episodic Memory… (2024) | 5 | 4 | empirical evaluation of a graph-based memory agent against memory and RL baseli… | interactive text game environments of varying complexity | AriGraph는 의미 기억(semantic memory)과 일화 기억(episodic memory)을 통합하는 기억 그래프를 구축하고 갱신하며, Ariadne 에이전트는 텍스트 게임 과제에서 다른 기억 방법(전체 이력, 요약, 검색 증강)과 강력한 강화학습(RL) 기준선을 크게 능가… |
| [5] | Reflexion: Language Agents with Verbal Reinforcement Learning (2023) | 5 | 4 | empirical evaluation of a framework with ablations across tasks | Sequential decision-making, coding (HumanEval), and languag… | Reflexion 에이전트는 언어로 된 자기 성찰을 일화 기억 버퍼에 저장하여 이후 시행을 개선하며, 여러 과제에서 기준선보다 유의미한 향상을 보인다. HumanEval에서 pass@1 91%를 달성하여 GPT-4의 80%를 넘어선다. |
| [2] | Evaluating Memory in LLM Agents via Incremental Multi-Turn Interactio… (2025) | 5 | 4 | benchmark construction (MemoryAgentBench) and evaluation of memory agents |  | MemoryAgentBench는 점진적 다중 턴 형식을 사용하여 기억 에이전트를 정확한 검색, 테스트 시점 학습(test-time learning), 장거리 이해, 선택적 망각(selective forgetting)의 네 가지 역량에 대해 평가한다. 초록은 결과가 나오기 전에 잘려 있… |
| [4] | A Survey on the Memory Mechanism of Large Language Model based Agents (2024) | 5 | 4 | systematic survey/literature review |  | LLM 기반 에이전트의 기억 메커니즘을 개괄하며, 기억이 무엇이고 왜 필요한지, 기억 모듈을 어떻게 설계하고 평가하는지, 그리고 응용 사례를 다룬다. 또한 기존 연구의 한계와 향후 방향을 분석한다. |
| [6] | AdMem: Advanced Memory for Task-solving Agents (2026) | 5 | 3 | framework proposal with experiments across environments |  | AdMem은 행위자(actor), 기억(memory), 비평자(critic) 에이전트로 구성된 이중 수준의 단기/장기 설계에서 의미 기억, 일화 기억, 절차 기억(procedural memory)을 결합한다. 보상 기반 병합과 가지치기(pruning)가 긴 다중 턴 과제에서 견고성과… |
| [10] | Vector Storage Based Long-term Memory Research on LLM (2024) | 5 | 3 | proposed system (VIMBank) with experimental comparison against other agents |  | VIMBank는 동적 갱신과 에빙하우스 망각 곡선(Ebbinghaus forgetting curve)에 기반한 망각을 갖춘 벡터 저장소(vector-store) 방식의 장기 기억이다. 비교 대상 에이전트보다 과제 의사결정 성공률을 10-20% 높이고 추론 비용을 약 23% 줄인다고 보… |
| [7] | Selective Memory Retention for Long-Horizon LLM Agents (2026) | 5 | 3 | controlled empirical study on ALFWorld with ablated retention policies (two see… | ALFWorld with gpt-5-mini; held-out evaluation of 50 tasks | 외부 기억은 기억이 없는 경우보다 성능을 높인다. 보류(held-out) 과제 50개 중 47-49개를 해결하여 39/50과 대비된다. 제한적 보존 정책(bounded retention policies)은 교란 요소가 없는 ALFWorld에서 통계적으로 구별되지 않는다. 방해 항목 기… |
| [9] | Cognitive Extensions for Dual-Process Language Agents: Memory and Sel… (2026) | 5 | 3 | controlled ablation study on ScienceWorld (4 configurations: baseline, +AMM, +S… | ScienceWorld interactive environment | 전체 시스템(일화적 적응형 기억 모듈(Adaptive Memory Module)과 자기 성찰 모듈(Self-Reflection Module))이 평균 점수 (64.62), 성공률 (43.17%), 단계 효율 (19.33 steps)에서 최고 성적을 달성했다. 자기 성찰이 단독으로 가장… |
| [12] | Agent Workflow Memory (2024) | 4 | 4 | empirical benchmark evaluation (offline and online) on Mind2Web and WebArena | 1000+ tasks across 200+ domains | Agent Workflow Memory induces reusable workflows from past experience and supplies them to guide the agent. It improves relative success rate by 24.6% on Mind2… |
| [16] | Retrieval-Driven Memory Reconsolidation for Long-Term LLM Agents (2026) | 4 | 3 | method proposal with benchmark evaluation and ablations | LoCoMo and LongMemEval benchmarks | REALM organizes memory as a heterogeneous cognitive graph with adaptive graph-search retrieval and retrieval-driven reconsolidation. It reaches 75.97% accuracy… |
| [19] | JARVIS -1: Open-World Multi-Task Agents With Memory-Augmented Multimo… (2024) | 3 | 3 | empirical agent system evaluation in Minecraft | over 200 Minecraft tasks | JARVIS-1 uses a multimodal memory to support planning with pre-trained knowledge and game experiences, and completes over 200 different tasks in Minecraft. The… |
| [20] | JARVIS-1: Open-World Multi-task Agents with Memory-Augmented Multimod… (2023) | 3 | 3 | empirical agent system evaluation in Minecraft (preprint) | over 200 Minecraft tasks | JARVIS-1 uses a multimodal memory combining pre-trained knowledge and game experiences to plan, and completes over 200 tasks in Minecraft. The abstract is trun… |
| [38] | Towards Improving Sequential Decision-Making in LLM Agents via Experi… (2026) | 3 | 3 | empirical evaluation on two-player zero-sum games with experience-memory agent… | Tic-tac-toe, Connect Four; multiple model tiers; MCTS oppon… | LLMs play suboptimally in simple games and lose to MCTS opponents, and obfuscating the surface form leaves performance largely unchanged. An experience memory… |
| [39] | Think-in-Memory: Recalling and Post-thinking Enable LLMs with Long-Te… (2023) | 3 | 3 | method proposal (TiM memory mechanism), evaluation details not in abstract |  | TiM stores historical thoughts in an evolving memory, recalls them before responding and post-thinks to update memory after responding. This is meant to avoid… |
| [44] | Understanding the planning of LLM agents: A survey (2024) | 3 | 3 | survey with taxonomy |  | The survey gives a taxonomy of LLM-agent planning (task decomposition, plan selection, external module, reflection and memory) and discusses open challenges. M… |
| [23] | From Single to Multi-Granularity: Toward Long-Term Memory Association… (2025) | 3 | 3 | method proposal (MemGAS) with empirical evaluation |  | MemGAS uses multi-granularity memory units, GMM-based clustering and association, and an entropy-based router to pick the retrieval granularity. It aims to bal… |
| [45] | Long Term Memory: The Foundation of AI Self-Evolution (2024) | 3 | 2 | position/conceptual report |  | The report argues that long-term memory is needed for AI self-evolution, letting models evolve at inference time from accumulated interactions and supporting l… |
| [26] | LeanMem: Simple and Efficient Long-Term Memory for LLM Agents (2026) | 3 | 2 | unclear from abstract (system proposal evaluated on LoCoMo and LongMemEval-S be… |  | LeanMem is a lightweight long-term memory framework that filters low-value content and stores it as profile, event, or record memory. It selectively updates on… |
| [28] | Review of Case-Based Reasoning for LLM Agents: Theoretical Foundation… (2025) | 3 | 2 | narrative/systematic review with a mathematical formalization of CBR; no clear… |  | The paper reviews how Case-Based Reasoning (case retrieval, adaptation, learning) can be integrated into LLM agents to supply experience-based memory. It compa… |
| [31] | Semantic Memory Modeling and Memory Interaction in Learning Agents (2016) | 2 | 3 | model proposal with experimental studies (fusion ART neural network) | Domains including the Unreal Tournament first-person shooti… | Presents a self-organizing semantic memory model that consolidates knowledge from episodic memory and interacts with procedural memory for more effective decis… |
| [42] | Enhancing Group Recommendation with Memory-Augmented Reasoning in LLM… (2026) | 2 | 2 | unclear from abstract (method proposal, LLM agent with memory and reasoning mod… |  | Proposes AGR, an LLM agent for group recommendation with a hash-table memory module supporting insertion, updating, retrieval, forgetting and summarization, pl… |

</details>

#### rq4 — 장기 기억은 에이전트의 계획 및 추론 모듈과 어떻게 상호작용하여 장기 시계 과제의 완수를 뒷받침하는가?

24편 (rel ≥ 3: 19편) · 신뢰도 평균 3.0 · 상위: [3] AriGraph: Learning Knowledge Graph World Models with Episod… (2024) (reli 4); [5] Reflexion: Language Agents with Verbal Reinforcement Learni… (2023) (reli 4); [2] Evaluating Memory in LLM Agents via Incremental Multi-Turn… (2025) (reli 4)

<details><summary>전체 표 (24편)</summary>

| # | 문헌 | rel | reli | method | sample | finding |
|---|---|---|---|---|---|---|
| [3] | AriGraph: Learning Knowledge Graph World Models with Episodic Memory… (2024) | 5 | 4 | empirical evaluation of a graph-based memory agent against memory and RL baseli… | interactive text game environments of varying complexity | AriGraph는 의미 기억(semantic memory)과 일화 기억(episodic memory)을 통합하는 기억 그래프를 구축하고 갱신하며, Ariadne 에이전트는 텍스트 게임 과제에서 다른 기억 방법(전체 이력, 요약, 검색 증강)과 강력한 강화학습(RL) 기준선을 크게 능가… |
| [5] | Reflexion: Language Agents with Verbal Reinforcement Learning (2023) | 5 | 4 | empirical evaluation of a framework with ablations across tasks | Sequential decision-making, coding (HumanEval), and languag… | Reflexion 에이전트는 언어로 된 자기 성찰을 일화 기억 버퍼에 저장하여 이후 시행을 개선하며, 여러 과제에서 기준선보다 유의미한 향상을 보인다. HumanEval에서 pass@1 91%를 달성하여 GPT-4의 80%를 넘어선다. |
| [2] | Evaluating Memory in LLM Agents via Incremental Multi-Turn Interactio… (2025) | 5 | 4 | benchmark construction (MemoryAgentBench) and evaluation of memory agents |  | MemoryAgentBench는 점진적 다중 턴 형식을 사용하여 기억 에이전트를 정확한 검색, 테스트 시점 학습(test-time learning), 장거리 이해, 선택적 망각(selective forgetting)의 네 가지 역량에 대해 평가한다. 초록은 결과가 나오기 전에 잘려 있… |
| [8] | MemoryArena: Benchmarking Agent Memory in Interdependent Multi-Sessio… (2026) | 5 | 3 | benchmark construction with human-crafted multi-session agentic tasks | tasks across web navigation, preference-constrained plannin… | MemoryArena는 상호 의존적인 하위 과제가 있는 다중 세션 에이전트-환경 루프에서 기억의 획득과 활용을 함께 평가한다. 초록은 중간에 잘려 있지만, 기존 벤치마크에서 성능이 거의 포화에 가까운 에이전트가 여기서는 더 낮은 성능을 보인다고 시사한다. |
| [9] | Cognitive Extensions for Dual-Process Language Agents: Memory and Sel… (2026) | 5 | 3 | controlled ablation study on ScienceWorld (4 configurations: baseline, +AMM, +S… | ScienceWorld interactive environment | 전체 시스템(일화적 적응형 기억 모듈(Adaptive Memory Module)과 자기 성찰 모듈(Self-Reflection Module))이 평균 점수 (64.62), 성공률 (43.17%), 단계 효율 (19.33 steps)에서 최고 성적을 달성했다. 자기 성찰이 단독으로 가장… |
| [12] | Agent Workflow Memory (2024) | 4 | 4 | empirical benchmark evaluation (offline and online) on Mind2Web and WebArena | 1000+ tasks across 200+ domains | Agent Workflow Memory induces reusable workflows from past experience and supplies them to guide the agent. It improves relative success rate by 24.6% on Mind2… |
| [13] | Context-Aware Planning and Environment-Aware Memory for Instruction F… (2023) | 4 | 4 | method proposal with benchmark evaluation | interactive instruction-following benchmark, seen and unsee… | CAPEAM combines context-aware planning with environment-aware memory of object states and locations, reaching state-of-the-art results with up to +10.70% gain… |
| [34] | RAP: Retrieval-Augmented Planning with Contextual Memory for Multimod… (2024) | 4 | 3 | method proposal with empirical evaluation (details unclear from abstract) |  | RAP retrieves past experiences relevant to the current context to enhance planning, reporting SOTA in textual scenarios and improved multimodal agent performan… |
| [17] | A survey on large language model based autonomous agents (2024) | 3 | 3 | narrative survey of LLM-based autonomous agents |  | Proposes a unified framework for constructing LLM-based autonomous agents and reviews applications and evaluation strategies. The abstract does not report memo… |
| [18] | A Survey on Large Language Model based Autonomous Agents (2023) | 3 | 3 | narrative survey of LLM-based autonomous agents (preprint version) |  | Proposes a unified framework for building LLM-based agents and surveys applications and evaluation strategies. The abstract does not report memory-specific eff… |
| [19] | JARVIS -1: Open-World Multi-Task Agents With Memory-Augmented Multimo… (2024) | 3 | 3 | empirical agent system evaluation in Minecraft | over 200 Minecraft tasks | JARVIS-1 uses a multimodal memory to support planning with pre-trained knowledge and game experiences, and completes over 200 different tasks in Minecraft. The… |
| [20] | JARVIS-1: Open-World Multi-task Agents with Memory-Augmented Multimod… (2023) | 3 | 3 | empirical agent system evaluation in Minecraft (preprint) | over 200 Minecraft tasks | JARVIS-1 uses a multimodal memory combining pre-trained knowledge and game experiences to plan, and completes over 200 tasks in Minecraft. The abstract is trun… |
| [21] | Memory is Reconstructed, Not Retrieved: Graph Memory for LLM Agents (2026) | 3 | 3 | method proposal (MRAgent) with benchmark experiments | LoCoMo and LongMemEval benchmarks | A Cue-Tag-Content memory graph with active reconstruction improves over strong baselines by up to 23% while reducing token and runtime cost. Retrieval is adapt… |
| [39] | Think-in-Memory: Recalling and Post-thinking Enable LLMs with Long-Te… (2023) | 3 | 3 | method proposal (TiM memory mechanism), evaluation details not in abstract |  | TiM stores historical thoughts in an evolving memory, recalls them before responding and post-thinks to update memory after responding. This is meant to avoid… |
| [22] | El Agente: An autonomous agent for quantum chemistry (2025) | 3 | 3 | system description with benchmarking on course exercises and case studies | six university-level course exercises and two case studies | El Agente Q uses a hierarchical memory framework within its cognitive architecture and reaches an average task success above 87%. It also supports longer multi… |
| [44] | Understanding the planning of LLM agents: A survey (2024) | 3 | 3 | survey with taxonomy |  | The survey gives a taxonomy of LLM-agent planning (task decomposition, plan selection, external module, reflection and memory) and discusses open challenges. M… |
| [24] | KnowAgent: Knowledge-Augmented Planning for LLM-Based Agents (2024) | 3 | 3 | method proposal with benchmark experiments | HotpotQA and ALFWorld with various backbone LLMs | KnowAgent uses an action knowledge base and self-learning to constrain planning paths, achieving comparable or superior performance to baselines and reducing p… |
| [27] | Mind-Tool: Domain Memory Architecture for AI Agents (2026) | 3 | 2 | single-system production deployment case study (90 days), no stated baseline be… | One IT infrastructure management deployment (Proxmox, Kuber… | Mind-Tool, which combines a persistent memory layer, a desired-state goal model and a reasoning engine, reported a 94% task success rate, 68% workflow automati… |
| [28] | Review of Case-Based Reasoning for LLM Agents: Theoretical Foundation… (2025) | 3 | 2 | narrative/systematic review with a mathematical formalization of CBR; no clear… |  | The paper reviews how Case-Based Reasoning (case retrieval, adaptation, learning) can be integrated into LLM agents to supply experience-based memory. It compa… |
| [29] | A Language Agent for Autonomous Driving (2023) | 2 | 3 | empirical evaluation on nuScenes benchmark | nuScenes driving benchmark | Agent-Driver combines a tool library, a cognitive memory of common sense and experiential knowledge, and an LLM reasoning engine, and reportedly outperforms st… |
| [42] | Enhancing Group Recommendation with Memory-Augmented Reasoning in LLM… (2026) | 2 | 2 | unclear from abstract (method proposal, LLM agent with memory and reasoning mod… |  | Proposes AGR, an LLM agent for group recommendation with a hash-table memory module supporting insertion, updating, retrieval, forgetting and summarization, pl… |
| [46] | The Landscape of Emerging AI Agent Architectures for Reasoning, Plann… (2024) | 2 | 2 | survey of agent architectures |  | The survey compares single- and multi-agent architectures and highlights planning, execution and reflection phases that support robust agents. Memory is not ex… |
| [32] | Agents: An Open-source Framework for Autonomous Language Agents (2023) | 2 | 2 | open-source library/framework description |  | The Agents library supports planning, memory, tool use and multi-agent communication in a modular design for building language agents. The abstract reports no… |
| [47] | ChatEDA: A Large Language Model Powered Autonomous Agent for EDA (2024) | 1 | 3 | system description with experimental evaluation |  | ChatEDA is an LLM-based EDA agent that handles task decomposition, script generation and execution, and its fine-tuned AutoMage model outperforms GPT-4. The ab… |

</details>

#### rq5 — LLM 에이전트에서 기억이 다단계 과제 성공률에 기여하는 정도를 평가하는 데 어떤 벤치마크, 지표, 절제 실험 방법론이 사용되는가?

22편 (rel ≥ 3: 19편) · 신뢰도 평균 3.2 · 상위: [3] AriGraph: Learning Knowledge Graph World Models with Episod… (2024) (reli 4); [5] Reflexion: Language Agents with Verbal Reinforcement Learni… (2023) (reli 4); [2] Evaluating Memory in LLM Agents via Incremental Multi-Turn… (2025) (reli 4)

<details><summary>전체 표 (22편)</summary>

| # | 문헌 | rel | reli | method | sample | finding |
|---|---|---|---|---|---|---|
| [3] | AriGraph: Learning Knowledge Graph World Models with Episodic Memory… (2024) | 5 | 4 | empirical evaluation of a graph-based memory agent against memory and RL baseli… | interactive text game environments of varying complexity | AriGraph는 의미 기억(semantic memory)과 일화 기억(episodic memory)을 통합하는 기억 그래프를 구축하고 갱신하며, Ariadne 에이전트는 텍스트 게임 과제에서 다른 기억 방법(전체 이력, 요약, 검색 증강)과 강력한 강화학습(RL) 기준선을 크게 능가… |
| [5] | Reflexion: Language Agents with Verbal Reinforcement Learning (2023) | 5 | 4 | empirical evaluation of a framework with ablations across tasks | Sequential decision-making, coding (HumanEval), and languag… | Reflexion 에이전트는 언어로 된 자기 성찰을 일화 기억 버퍼에 저장하여 이후 시행을 개선하며, 여러 과제에서 기준선보다 유의미한 향상을 보인다. HumanEval에서 pass@1 91%를 달성하여 GPT-4의 80%를 넘어선다. |
| [2] | Evaluating Memory in LLM Agents via Incremental Multi-Turn Interactio… (2025) | 5 | 4 | benchmark construction (MemoryAgentBench) and evaluation of memory agents |  | MemoryAgentBench는 점진적 다중 턴 형식을 사용하여 기억 에이전트를 정확한 검색, 테스트 시점 학습(test-time learning), 장거리 이해, 선택적 망각(selective forgetting)의 네 가지 역량에 대해 평가한다. 초록은 결과가 나오기 전에 잘려 있… |
| [1] | Harness the Memory: A Holistic Evaluation of Memory Substrates in Mem… (2026) | 5 | 4 | controlled harness evaluation of memory substrates | three backbone models, four benchmark suites, 26 metrics | 모든 상황에서 우세한 단일 기억 기반(memory substrate)은 없다. 폭넓은 검색(retrieval)은 장문 맥락 사실 질의응답(QA)에 도움이 되지만, 과도한 검색은 순차적 의사결정을 해칠 수 있다. 일부 기억 기반은 더 긴 시계(horizon)에서 비용이 커지거나 취약해진… |
| [4] | A Survey on the Memory Mechanism of Large Language Model based Agents (2024) | 5 | 4 | systematic survey/literature review |  | LLM 기반 에이전트의 기억 메커니즘을 개괄하며, 기억이 무엇이고 왜 필요한지, 기억 모듈을 어떻게 설계하고 평가하는지, 그리고 응용 사례를 다룬다. 또한 기존 연구의 한계와 향후 방향을 분석한다. |
| [7] | Selective Memory Retention for Long-Horizon LLM Agents (2026) | 5 | 3 | controlled empirical study on ALFWorld with ablated retention policies (two see… | ALFWorld with gpt-5-mini; held-out evaluation of 50 tasks | 외부 기억은 기억이 없는 경우보다 성능을 높인다. 보류(held-out) 과제 50개 중 47-49개를 해결하여 39/50과 대비된다. 제한적 보존 정책(bounded retention policies)은 교란 요소가 없는 ALFWorld에서 통계적으로 구별되지 않는다. 방해 항목 기… |
| [8] | MemoryArena: Benchmarking Agent Memory in Interdependent Multi-Sessio… (2026) | 5 | 3 | benchmark construction with human-crafted multi-session agentic tasks | tasks across web navigation, preference-constrained plannin… | MemoryArena는 상호 의존적인 하위 과제가 있는 다중 세션 에이전트-환경 루프에서 기억의 획득과 활용을 함께 평가한다. 초록은 중간에 잘려 있지만, 기존 벤치마크에서 성능이 거의 포화에 가까운 에이전트가 여기서는 더 낮은 성능을 보인다고 시사한다. |
| [9] | Cognitive Extensions for Dual-Process Language Agents: Memory and Sel… (2026) | 5 | 3 | controlled ablation study on ScienceWorld (4 configurations: baseline, +AMM, +S… | ScienceWorld interactive environment | 전체 시스템(일화적 적응형 기억 모듈(Adaptive Memory Module)과 자기 성찰 모듈(Self-Reflection Module))이 평균 점수 (64.62), 성공률 (43.17%), 단계 효율 (19.33 steps)에서 최고 성적을 달성했다. 자기 성찰이 단독으로 가장… |
| [12] | Agent Workflow Memory (2024) | 4 | 4 | empirical benchmark evaluation (offline and online) on Mind2Web and WebArena | 1000+ tasks across 200+ domains | Agent Workflow Memory induces reusable workflows from past experience and supplies them to guide the agent. It improves relative success rate by 24.6% on Mind2… |
| [13] | Context-Aware Planning and Environment-Aware Memory for Instruction F… (2023) | 4 | 4 | method proposal with benchmark evaluation | interactive instruction-following benchmark, seen and unsee… | CAPEAM combines context-aware planning with environment-aware memory of object states and locations, reaching state-of-the-art results with up to +10.70% gain… |
| [14] | PlugMem: A Task-Agnostic Plugin Memory Module for LLM Agents (2026) | 4 | 3 | method proposal with evaluation on three benchmarks | three heterogeneous benchmarks (conversational QA, multi-ho… | PlugMem structures episodic memory into a knowledge-centric memory graph to reduce context explosion from raw retrieval. It is evaluated unchanged across three… |
| [15] | MemGym: a Long-Horizon Memory Environment for LLM Agents (2026) | 4 | 3 | benchmark/environment construction with five evaluation tracks | Five tracks: tau2-bench, MEMGYM-DR, SWE-Gym, MEMGYM-CODEQA,… | MemGym is a benchmark for agentic memory spanning tool-use dialogue, deep-research search, coding and computer use. It reports memory-isolated scores that deco… |
| [16] | Retrieval-Driven Memory Reconsolidation for Long-Term LLM Agents (2026) | 4 | 3 | method proposal with benchmark evaluation and ablations | LoCoMo and LongMemEval benchmarks | REALM organizes memory as a heterogeneous cognitive graph with adaptive graph-search retrieval and retrieval-driven reconsolidation. It reaches 75.97% accuracy… |
| [36] | IFCMemoryBench: Evaluating Long-Term Memory of LLM-Based Agents in BI… (2026) | 4 | 3 | benchmark construction and evaluation | 143 multi-session tasks across 19 BIM projects and 4,016 pr… | Introduces IFCMemoryBench to evaluate long-term memory when agents must combine remembered context from earlier sessions with live IFC queries. The framework d… |
| [37] | On Memory Construction and Retrieval for Personalized Conversational… (2025) | 3 | 4 | empirical analysis plus method proposal (SeCom) evaluated on benchmarks | LOCOMO and Long-MT-Bench+ benchmarks | Memory unit granularity matters, and prompt compression (LLMLingua-2) works as a denoiser to improve retrieval accuracy. Segment-level memory (SeCom) significa… |
| [17] | A survey on large language model based autonomous agents (2024) | 3 | 3 | narrative survey of LLM-based autonomous agents |  | Proposes a unified framework for constructing LLM-based autonomous agents and reviews applications and evaluation strategies. The abstract does not report memo… |
| [18] | A Survey on Large Language Model based Autonomous Agents (2023) | 3 | 3 | narrative survey of LLM-based autonomous agents (preprint version) |  | Proposes a unified framework for building LLM-based agents and surveys applications and evaluation strategies. The abstract does not report memory-specific eff… |
| [38] | Towards Improving Sequential Decision-Making in LLM Agents via Experi… (2026) | 3 | 3 | empirical evaluation on two-player zero-sum games with experience-memory agent… | Tic-tac-toe, Connect Four; multiple model tiers; MCTS oppon… | LLMs play suboptimally in simple games and lose to MCTS opponents, and obfuscating the surface form leaves performance largely unchanged. An experience memory… |
| [26] | LeanMem: Simple and Efficient Long-Term Memory for LLM Agents (2026) | 3 | 2 | unclear from abstract (system proposal evaluated on LoCoMo and LongMemEval-S be… |  | LeanMem is a lightweight long-term memory framework that filters low-value content and stores it as profile, event, or record memory. It selectively updates on… |
| [41] | Toward Conversational Agents with Context and Time Sensitive Long-ter… (2024) | 2 | 3 | new dataset construction and retrieval model evaluation | new dataset of ambiguous and time-based questions built on… | Standard RAG handles time/event-based and ambiguous queries over long conversations poorly. A new retrieval model combining chain-of-table search and vector-da… |
| [48] | From Language Models to Agentic AI: A Survey of Autonomous, Action-En… (2026) | 2 | 2 | taxonomy-driven survey |  | Presents a modular reference architecture and four-dimensional taxonomy of agentic AI systems, noting design trade-offs, recurring failure modes and evaluation… |
| [49] | A review of large language models and autonomous agents in chemistry (2024) | 1 | 2 | narrative review of LLMs and agents in chemistry |  | Reviews LLM capabilities in chemistry and LLM-based agents with tool use, noting challenges such as data quality and the need for standard benchmarks. Memory d… |

</details>

#### rq6 — LLM 에이전트의 장기 기억에서는 어떤 한계, 실패 양상, 비용(예: 기억 잡음, 오류 전파, 맥락 과부하, 지연 시간)이 발생하는가?

15편 (rel ≥ 3: 10편) · 신뢰도 평균 2.9 · 상위: [1] Harness the Memory: A Holistic Evaluation of Memory Substra… (2026) (reli 4); [4] A Survey on the Memory Mechanism of Large Language Model ba… (2024) (reli 4); [10] Vector Storage Based Long-term Memory Research on LLM (2024) (reli 3)

<details><summary>전체 표 (15편)</summary>

| # | 문헌 | rel | reli | method | sample | finding |
|---|---|---|---|---|---|---|
| [1] | Harness the Memory: A Holistic Evaluation of Memory Substrates in Mem… (2026) | 5 | 4 | controlled harness evaluation of memory substrates | three backbone models, four benchmark suites, 26 metrics | 모든 상황에서 우세한 단일 기억 기반(memory substrate)은 없다. 폭넓은 검색(retrieval)은 장문 맥락 사실 질의응답(QA)에 도움이 되지만, 과도한 검색은 순차적 의사결정을 해칠 수 있다. 일부 기억 기반은 더 긴 시계(horizon)에서 비용이 커지거나 취약해진… |
| [4] | A Survey on the Memory Mechanism of Large Language Model based Agents (2024) | 5 | 4 | systematic survey/literature review |  | LLM 기반 에이전트의 기억 메커니즘을 개괄하며, 기억이 무엇이고 왜 필요한지, 기억 모듈을 어떻게 설계하고 평가하는지, 그리고 응용 사례를 다룬다. 또한 기존 연구의 한계와 향후 방향을 분석한다. |
| [10] | Vector Storage Based Long-term Memory Research on LLM (2024) | 5 | 3 | proposed system (VIMBank) with experimental comparison against other agents |  | VIMBank는 동적 갱신과 에빙하우스 망각 곡선(Ebbinghaus forgetting curve)에 기반한 망각을 갖춘 벡터 저장소(vector-store) 방식의 장기 기억이다. 비교 대상 에이전트보다 과제 의사결정 성공률을 10-20% 높이고 추론 비용을 약 23% 줄인다고 보… |
| [7] | Selective Memory Retention for Long-Horizon LLM Agents (2026) | 5 | 3 | controlled empirical study on ALFWorld with ablated retention policies (two see… | ALFWorld with gpt-5-mini; held-out evaluation of 50 tasks | 외부 기억은 기억이 없는 경우보다 성능을 높인다. 보류(held-out) 과제 50개 중 47-49개를 해결하여 39/50과 대비된다. 제한적 보존 정책(bounded retention policies)은 교란 요소가 없는 ALFWorld에서 통계적으로 구별되지 않는다. 방해 항목 기… |
| [11] | On the Structural Memory of LLM Agents (2024) | 4 | 4 | empirical comparison of memory structures and retrieval methods across 4 tasks… | four tasks, six datasets | Different memory structures (chunks, triples, atomic facts, summaries, mixed) suit different tasks, and mixed memory is resilient in noisy settings. Iterative… |
| [35] | TRAD: Enhancing LLM Agents with Step-Wise Thought Retrieval and Align… (2024) | 4 | 3 | method proposal (TRAD) with empirical evaluation (details unclear from abstract) |  | Step-level thought retrieval and aligned decision select more helpful demonstrations with less irrelevant context than trajectory-level retrieval. It targets s… |
| [36] | IFCMemoryBench: Evaluating Long-Term Memory of LLM-Based Agents in BI… (2026) | 4 | 3 | benchmark construction and evaluation | 143 multi-session tasks across 19 BIM projects and 4,016 pr… | Introduces IFCMemoryBench to evaluate long-term memory when agents must combine remembered context from earlier sessions with live IFC queries. The framework d… |
| [23] | From Single to Multi-Granularity: Toward Long-Term Memory Association… (2025) | 3 | 3 | method proposal (MemGAS) with empirical evaluation |  | MemGAS uses multi-granularity memory units, GMM-based clustering and association, and an entropy-based router to pick the retrieval granularity. It aims to bal… |
| [40] | State Contamination in Memory-Augmented LLM Agents (2026) | 3 | 3 | paired counterfactual multi-agent rollouts |  | Toxic content compressed into memory summaries can fall below toxicity detection thresholds yet still raise downstream toxicity. Raw transcript reuse drives ov… |
| [26] | LeanMem: Simple and Efficient Long-Term Memory for LLM Agents (2026) | 3 | 2 | unclear from abstract (system proposal evaluated on LoCoMo and LongMemEval-S be… |  | LeanMem is a lightweight long-term memory framework that filters low-value content and stores it as profile, event, or record memory. It selectively updates on… |
| [41] | Toward Conversational Agents with Context and Time Sensitive Long-ter… (2024) | 2 | 3 | new dataset construction and retrieval model evaluation | new dataset of ambiguous and time-based questions built on… | Standard RAG handles time/event-based and ambiguous queries over long conversations poorly. A new retrieval model combining chain-of-table search and vector-da… |
| [50] | SAUP: Situation Awareness Uncertainty Propagation on LLM Agent (2024) | 2 | 3 | method proposal with experiments on benchmark datasets |  | SAUP propagates step-level uncertainty with situational weights through multistep LLM agent reasoning, improving AUROC by up to 20% over existing uncertainty e… |
| [51] | From Dialogue Systems to Autonomous Agents: A Modeling Framework for… (2026) | 2 | 2 | conceptual review and modeling framework |  | Proposes a framework for ethical clinical AI agents, identifying state persistence among the core architectural dimensions. It examines how these features affe… |
| [48] | From Language Models to Agentic AI: A Survey of Autonomous, Action-En… (2026) | 2 | 2 | taxonomy-driven survey |  | Presents a modular reference architecture and four-dimensional taxonomy of agentic AI systems, noting design trade-offs, recurring failure modes and evaluation… |
| [52] | Trustworthy Agentic AI: A Survey and Taxonomy of Secure Coordination… (2026) | 2 | 2 | literature survey and taxonomy |  | Proposes a seven-layer trust taxonomy (including memory and retrieval layers) and six secure-coordination design patterns for multi-agent LLM systems. Hallucin… |

</details>

#### 평가했으나 어느 sub-RQ 에도 배정되지 않은 문헌 (21편, 대부분 관련성 ≤ 1)

Evaluator 가 읽고 관련성이 낮다고 판정한 문헌. 종합·Gap 에 쓰이지 않아 참고문헌 번호를 받지 않으며, 평가 기록으로만 남긴다.

<details><summary>전체 표 (21편)</summary>

| id | 문헌 | rel | reli | method | sample | finding |
|---|---|---|---|---|---|---|
| 10.48550/arxiv.2512.23128 | It's a TRAP! Task-Redirecting Agent Persuasion Benchmark for Web Agen… (2025) | 1 | 4 | benchmark evaluation of prompt-injection susceptibility | six frontier models on realistic web tasks | Agents were susceptible to prompt injection in 25% of tasks on average (13% for GPT-5 to 43% for DeepSeek-R1). Small interface or context changes often doubled… |
| 10.1038/s41524-026-02139-1 | Hierarchical Multi-agent Large Language Model Reasoning for Autonomou… (2026) | 1 | 3 | empirical comparison of single-agent, multi-agent and stochastic baselines | two chemical applications (CO adsorption on Cu adatoms and… | Hierarchical multi-agent LLM reasoning reduced the required atomistic simulations by up to 90% relative to heuristic or random selection. The abstract does not… |
| 10.48550/arxiv.2402.16823 | Language Agents as Optimizable Graphs (2024) | 1 | 3 | framework proposal with experiments (details unclear from abstract) |  | Describes LLM agents as computational graphs with automatic node (prompt) and edge (orchestration) optimizers. The abstract does not address long-term memory. |
| 10.48550/arxiv.2312.11671 | Evaluating Language-Model Agents on Realistic Autonomous Tasks (2023) | 1 | 3 | benchmark evaluation of 4 agents on 12 tasks | 4 LLM agents, 12 ARA-relevant tasks | LM agents could complete only the easiest of the 12 autonomous replication and adaptation tasks, making some progress on harder ones. The abstract says nothing… |
| 10.1109/tpami.2020.3008558 | Multiple Trajectory Prediction of Moving Agents With Memory Augmented… (2020) | 1 | 3 | model proposal with empirical evaluation on four datasets | four trajectory prediction datasets | MANTRA uses memory-augmented networks to predict multiple trajectories of other agents, with state-of-the-art results on four datasets. Because the memory is n… |
| 10.1146/annurev-psych-040723-012736 | The Relation Between Attention and Memory (2023) | 1 | 3 | narrative review |  | Reviews evidence on the relation between attention and memory across working memory, long-term memory, development and neuropsychology, organized by an embedde… |
| 10.48550/arxiv.2604.15367 | SoK: Security of Autonomous LLM Agents in Agentic Commerce (2026) | 1 | 2 | systematization of knowledge (SoK) from a curated corpus |  | Develops a security framework for autonomous LLM agents in commerce, with 12 cross-layer attack vectors across five threat dimensions. Failures propagate from… |
| 10.48550/arxiv.2409.10553 | "Flipped" University: LLM-Assisted Lifelong Learning Environment (2024) | 1 | 1 | conceptual framework |  | The paper proposes a conceptual LLM-supported lifelong learning environment for education, stressing personal world models and reflective practice. It is not a… |
| 10.1523/jneurosci.3162-15.2016 | Sleep Spindle Density Predicts the Effect of Prior Knowledge on Memor… (2016) | 0 | 3 | human behavioral and fMRI study with polysomnography | Human participants (n not stated in abstract) | Sleep spindle density predicted a larger schema benefit to memory over 24 h and reduced decay of schema-related memories. It concerns human memory consolidatio… |
| 10.1371/journal.pcbi.1003307 | Synaptic Scaling Enables Dynamically Distinct Short- and Long-Term Me… (2013) | 0 | 3 | computational neuroscience modeling |  | Shows that synaptic scaling combined with plasticity can separate short- from long-term memory storage in a neural model. It is not about LLM agents. |
| 10.1101/lm.63604 | Associative Mechanosensory Conditioning of the Proboscis Extension Re… (2004) | 0 | 3 | laboratory conditioning experiments | harnessed honeybees (n not stated in abstract) | Honeybees learn side-specific associative mechanosensory conditioning of the proboscis extension reflex, with memory still present 24 h later and an optimal in… |
| 10.1242/jeb.062026 | Visual conditioning of the sting extension reflex in harnessed honeyb… (2011) | 0 | 3 | laboratory conditioning experiments | harnessed honeybees (n not stated in abstract) | Intact harnessed bees can learn visual discrimination via sting extension reflex conditioning with shock punishment, and antennae ablation impaired rather than… |
| 10.1523/jneurosci.4302-11.2011 | Visual Pathway for the Optokinetic Reflex in Infant Macaque Monkeys (2011) | 0 | 3 | neurophysiological recordings in anesthetized animals | 4 infant macaques | NOT-DTN neurons in infant macaques are direction selective shortly after birth but have lower selectivity, truncated velocity tuning and weaker V1 input than a… |
| 10.1080/088395100117106 | Autonomous agents for business process management (2000) | 0 | 2 | system design and implementation description |  | Describes an agent-based business process management system with autonomous problem-solving agents that negotiate and coordinate. It is unrelated to LLM agents… |
| 10.1101/lm.241006 | Retrieval failure versus memory loss in experimental amnesia: Definit… (2006) | 0 | 2 | narrative review/theoretical discussion |  | Argues that experimental amnesia in animals reflects, at least in part, retrieval deficits rather than storage failure. It is about biological memory, not LLM… |
| 10.1146/annurev-clinpsy-050718-095754 | Abnormal Sleep Spindles, Memory Consolidation, and Schizophrenia (2019) | 0 | 2 | narrative review |  | Reviews evidence that sleep spindle deficits in schizophrenia relate to impaired sleep-dependent memory consolidation and thalamocortical dysfunction. It conce… |
| 10.1002/smj.964 | Psychological foundations of dynamic capabilities: reflexion and refl… (2011) | 0 | 2 | conceptual/theoretical article |  | The paper argues that dynamic capabilities in firms require blending analytic and intuitive cognitive and emotional processes, drawing on social cognitive neur… |
| 10.3389/fpsyg.2022.841207 | Wired to Connect: The Autonomic Socioemotional Reflex Arc (2022) | 0 | 2 | narrative historical review and theory proposal |  | Proposes a theory of autonomic socioemotional reflexes in mother-infant co-regulation after a narrative history of nervous system theories. |
| 10.1515/phys-2019-0047 | Modeling Human Pupil Dilation to Decouple the Pupillary Light Reflex (2019) | 0 | 2 | modeling/methods comparison of pupil size equations |  | Presents and compares models to calculate pupil size from luminance, age and other parameters so the pupillary light reflex can be decoupled from other influen… |
| 10.1590/0101-3173.2021.v44dossier2.10.p151 | Memory and reflection (2021) | 0 | 1 | philosophical essay |  | The paper discusses memory, forgetting and reflection in Confucian and virtue epistemology. It does not address LLM agents. |
| 10.1515/phw-2016-5370 | A History/Memory Matrix for History Education (2016) | 0 | 1 | unclear from abstract |  | The abstract contains only a licensing statement and no substantive content. The title suggests a history/memory framework for history education, unrelated to… |

</details>

## 4. 종합

### 합의

- 외부 경험 기억(언어적 성찰, 유도된 워크플로, 그래프 기억, 보존된 궤적)을 추가하면 순차적 의사결정 과제에서 기억이 없거나 상태를 유지하지 않는 기준선보다 성공률이 높아지지만, 단독 이득은 크지 않을 수 있다. [3, 5, 7, 9, 12] (근거 5편 · 신뢰도 평균 3.6)

- 의사결정 과제의 증거만 보면, 과제 구조화 기억이 비구조적 대안보다 우수했다. AriGraph 기억 그래프는 텍스트 게임에서 전체 이력, 요약, 검색 증강을 능가했고, Agent Workflow Memory는 Mind2Web과 WebArena에서 성공률을 높이면서 WebArena에서는 단계 수도 줄였다. 맥락 축소 메커니즘은 분리되어 검증된 것이 아니라 주장된 것이며, 아래의 하네스(harness) 연구는 일반적인 우위를 반박한다. [3, 12] (근거 2편 · 신뢰도 평균 4.0)

- 대화 및 QA 기억 벤치마크(LoCoMo, LongMemEval, Long-MT-Bench+이며 다단계 과제 성공률은 아님)에서는 기억 단위의 세분도(granularity), 그래프로 조직된 기억, 반복적 검색이 검색 정확도를 높인다. 최적의 구조는 과제에 따라 다르며, 혼합 기억이 잡음 아래에서 가장 탄력적이다. [11, 16, 21, 37] (근거 4편 · 신뢰도 평균 3.5)

- 교훈을 기억에 다시 기록하는 성찰 또는 에피소드 이후 규칙 추출은 가중치 갱신 없이 이후 성능을 향상시킨다. 이는 단일 벤치마크 절제 실험과 소규모 도메인 결과에 근거하므로 확신도는 중간 수준이다. [5, 9, 38] (근거 3편 · 신뢰도 평균 3.3)

- 비선택적 기억(과도한 검색 또는 무제한 기록)은 정밀도나 순차적 의사결정 성공률을 떨어뜨린다. 과제 성공에 대한 비용, 지연 시간, 오류 전파의 직접 측정은 여전히 드물며 대부분 저자 자체 보고에 의존한다. [1, 7, 11] (근거 3편 · 신뢰도 평균 3.7)

- 기억 특화 벤치마크(MemoryAgentBench, MemoryArena, MemGym, IFCMemoryBench)는 기존 벤치마크가 기억을 분리해 측정하지 못하기 때문에 만들어졌다. 이들은 다중 세션 또는 점진적 형식을 추가하고 수용(ingestion), 검색, 활용을 구분하지만, 초록에는 결과가 보고되어 있지 않다. [2, 8, 15, 36] (근거 4편 · 신뢰도 평균 3.2)

### 상충

- **순차적 의사결정 과제에서 구조화된 기억이 더 단순한 기억보다 일반적인 우위를 갖는지 여부** (A 2편 vs B 1편)
  - A: 구조화되고 과제에 맞게 구축된 기억(AriGraph의 기억 그래프, AWM의 유도된 워크플로)은 이력, 요약, 검색 기준선을 능가했거나 성공률과 단계 효율을 향상시켰다. [3, 12]
  - B: 세 개의 백본(backbone)과 네 개의 스위트(suite)를 사용한 통제된 하네스에서는 우세한 단일 기억 기반이 없었고 과도한 검색이 순차적 의사결정을 해쳤으며, 이는 구조화 기억의 일반적 우위와 모순된다. [1]
  - 원인 가설: AriGraph와 AWM은 기억의 구축, 갱신, 활용이 하나의 환경군에 맞춰 함께 설계된 맞춤형 에이전트이며 선별된 기준선과 비교되었다. 하네스는 모델과 스위트에 걸쳐 기억 기반을 고정하므로, 이득은 구조 자체보다 도메인에 맞게 조정된 설계에서 비롯되었을 수 있다. 연구마다 검색의 폭과 강도도 다를 수 있으며, 양쪽 모두 초록이 잘려 있거나 절제 실험이 없는 사전 출판물이다.

### 조건부

- ALFWorld에서 방해 항목 기록이 75%인 조건에서는 궤적을 인식하는 TraceRetain 정책만이 성공률(97/100)을 유지했고, 단순 제한적 보존(FIFO)과 무제한 기억은 정밀도가 저하되었다. 교란 요소가 없는 ALFWorld에서는 제한적 정책들이 통계적으로 구별되지 않았으며, 이는 단일 환경, 두 시드(seed)의 결과이다. [7] (근거 1편 · 신뢰도 평균 3.0)

- 낮은 확신도: 망각과 가지치기가 도움이 된다고 보고되지만(VIMBank의 에빙하우스식 망각은 자체 보고된 10-20% 향상과 ~23%의 추론 비용 감소, AdMem의 보상 기반 가지치기는 수치 없음), 이는 자체 보고이며 교란 요소가 없는 ALFWorld에서의 보존 효과 부재와 상충한다. [6, 7, 10] (근거 3편 · 신뢰도 평균 3.0)

- 한 ScienceWorld 절제 실험(SwiftSage)에서 자기 성찰이 단독으로 가장 큰 기여를 했고 일화 기억은 런타임 루프가 안정화된 뒤에 가장 큰 도움이 되었다. 이는 해당 단일 벤치마크와 에이전트를 넘어 일반화해서는 안 된다. [9] (근거 1편 · 신뢰도 평균 3.0)

- 폭넓은 검색은 장문 맥락 사실 QA에는 도움이 되지만 순차적 의사결정에는 해가 될 수 있다. 기억에 조건화된 계획(RAP, TRAD)은 검색된 내용이 각 단계와 관련될 때 효과가 있다고 보고되지만, 절제 실험 수치나 분리된 기억 효과는 제시되지 않는다. [1, 34, 35] (근거 3편 · 신뢰도 평균 3.3)

### 커버리지 메모

rq5(벤치마크)는 가장 잘 다뤄졌으나 대부분의 벤치마크 초록에 결과가 없으며, rq1과 rq2는 증거가 중간 수준이고 그 상당수가 다단계 과제가 아닌 대화형 QA에서 나온다. rq4(기억-계획 상호작용)는 빈약하다. RAP(수치 없음), TRAD(결과 없음), 계획 서베이, JARVIS-1, CAPEAM(분리된 절제 실험 없음)만이 이를 다루며, 계획이나 분해 루프 내부에서 기억 검색을 절제한 연구는 없다. rq3은 통제된 절제 실험이 적고 ALFWorld와 ScienceWorld의 단일 환경 연구뿐이다. rq6은 빈약하다. 비용과 지연 시간 주장은 자체 보고이고(VIMBank, MRAgent), 오류 전파는 과제 성공에 대해 측정되지 않았으며, 독성(toxicity) 논문은 주제와 간접적으로만 관련된다. rq1의 경우 일화, 의미, 계층 기억을 직접 비교한 논문이 없고, 중복된 JARVIS-1과 에이전트 서베이 항목은 두 번 세어서는 안 된다. 하네스 연구 [1]은 이미 여러 모델과 스위트를 다루므로, 남은 공백은 다중 시드, 에이전트 루프의 변화, 설계별 전체 결과이다. 또 다른 공백은 더 넓은 검색이 해로워지는 용량-반응(dose-response) 임계값으로, 해당 연구는 이를 정성적으로만 보고한다. 여기서는 새로운 검색이 불가능했으므로, 비평자가 지적한 rq1, rq3, rq4, rq6의 공백은 그대로 남아 있다.

## 5. Research Gap

### G1. 에이전트 루프를 고정한 채 다단계 과제 성공률에 대해 일화, 의미, 계층적 장기 기억을 직접 비교한 연구는 없다.

[1, 3, 12] (근거 3편 · 신뢰도 평균 4.0)

통제된 하네스는 우세한 기반이 없다고 보고하지만, 그 초록에는 다중 시드, 에이전트 루프의 변화, 설계별 전체 결과가 나타나 있지 않다. AriGraph와 AWM은 각각 선별된 기준선에 맞서 맞춤형으로 함께 설계된 기억을 사용하므로, 구조를 도메인 조정과 분리할 수 없다.

- 제안 RQ: 백본과 환경을 고정했을 때 일화, 의미, 계층, 그래프 기억은 다단계 성공률에서 차이가 나는가, 그리고 그 순위는 에이전트 루프(ReAct, Reflexion 방식, 계획 후 실행)에 따라 달라지는가?
- 방법: 사전 등록된 요인 설계(factorial) 실험: 기억 설계 4개 x 에이전트 루프 3개 x 백본 3개로, 셀당 최소 5개 시드를 사용하고 성공률을 주요 결과로 하여 혼합 효과 모형(mixed-effects model)으로 분석한다. 공통 하네스 안에서 AriGraph 방식과 AWM 방식의 기억을 재구현하여, 도메인 특화 공동 설계 없이도 이들의 이득이 유지되는지 검증한다.
- 데이터: 보류 평가 과제를 포함한 ALFWorld, ScienceWorld, WebArena, Mind2Web 과제 분할을 사용하며, 오픈소스 하네스 코드와 공개 벤치마크를 이용한다. 스위트당 보류 과제는 대략 50-100개이다.

### G2. 하네스 연구는 폭넓은 검색이 장문 맥락 QA에는 도움이 되는 반면 과도한 검색이 순차적 의사결정을 해친다고 정성적으로만 보고한다.

[1, 11, 35] (근거 3편 · 신뢰도 평균 3.7)

검색이 해로워지는 임계값과 관련도 품질이 이를 이동시키는지는 측정된 바 없다. QA 연구는 반복적 검색이 단일 단계 검색보다 낫다고 보고하고 단계 수준 검색이 무관한 맥락을 줄인다고 주장되지만, 어느 쪽도 과제 성공에 대한 용량-반응 효과로 검증되지 않았다.

- 제안 RQ: 검색된 기억 항목의 수나 토큰 예산이 늘어남에 따라 과제 성공률은 어떻게 변하며, 단계 수준 검색과 궤적 수준 검색 중 무엇을 택하느냐가 성공률이 떨어지기 시작하는 지점을 이동시키는가?
- 방법: top-k(0, 1, 3, 5, 10, 20)를 검색 세분도(단계 대 궤적), 그리고 오라클 대 잡음 있는 관련도와 교차시켜 변화시키는 에이전트 내(within-agent) 용량-반응 실험. 검색된 토큰에 대한 성공률의 조건별 곡선을 적합하고 부트스트랩 신뢰구간(CI)으로 변곡점을 추정한다.
- 데이터: 이전 에피소드로 채워진 하나의 기억 저장소를 사용하는 ALFWorld와 WebArena이며, 2-3개의 백본과 최소 3개 시드를 사용한다. 대응되는 QA 과제(LongMemEval)를 대조 조건으로 사용한다.

### G3. 장기 시계 과제에서 계획 또는 과제 분해 루프 내부의 기억 검색을 절제한 연구는 없다.

[13, 34, 35, 44] (근거 4편 · 신뢰도 평균 3.2)

RAP, TRAD, CAPEAM은 검색된 경험을 계획에 연결하지만, 이들의 초록에는 수치가 없거나 분리된 절제 실험이 없다. 계획 서베이는 기억을 계획 강화의 한 범주로만 다루므로, 기억이 계획 시점에 도움이 되는지, 실행 시점에 도움이 되는지, 아니면 둘 다인지는 알려져 있지 않다.

- 제안 RQ: 계획자(planner)에게 검색된 기억에 대한 접근을 주는 것이 실행자(executor)에게만 주는 것보다 장기 시계 성공률을 더 높이는가, 그리고 기억으로부터의 계획 재사용은 단계 수준 힌트 이상의 이득을 더하는가?
- 방법: 하나의 계획-실행(plan-and-execute) 에이전트에 대해 기억 접근을 계획 시에만, 실행 시에만, 둘 다, 또는 둘 다 없음으로 설정하고 계획 재사용 조건을 추가한 통제 절제 실험. 주요 결과는 의존적인 단계가 10개 이상 필요한 과제의 성공률이며, 실패는 계획이 깨졌는지 실행이 깨졌는지에 따라 코딩한다.
- 데이터: MemoryArena 방식의 상호 의존적 다중 세션 과제와 WebArena 또는 ALFWorld의 장기 시계 부분집합. 약 200개 과제, 3개 시드, 그리고 실패 코딩을 위한 추적 로그.

### G4. 통합, 망각, 가지치기에 대한 통제된 증거는 거의 없다.

[2, 6, 7, 10] (근거 4편 · 신뢰도 평균 3.2)

망각과 보상 기반 가지치기의 이득은 자체 보고되었거나 수치가 없는 사전 출판물에서 나오며, 통제된 유일한 ALFWorld 연구는 교란 요소가 없는 과제에서는 제한적 보존이 구별되지 않고 TraceRetain으로 인한 이득은 합성된 방해 잡음 아래에서만 나타난다고 보고한다. 이러한 메커니즘이 여러 세션에 걸쳐 자연스럽게 누적되는 현실적인 잡음 아래에서도 도움이 되는지는 검증되지 않았다.

- 제안 RQ: 자연스럽게 누적되고 일부는 오래된 항목을 포함하는 많은 순차 세션에 걸쳐, 에빙하우스식 망각, 보상 기반 가지치기, 궤적 인식 보존이 FIFO와 무제한 기억보다 성공률을 향상시키는가?
- 방법: 무제한, FIFO, 망각 곡선, 보상 가지치기, TraceRetain 정책을 비교하는 20+개의 연속 세션에 걸친 종단적 절제 실험으로, 정해진 세션 시점마다 성공률을 측정한다. 이전 사실이 무효화되는 선택적 망각 탐침(probe)을 포함한다.
- 데이터: MemoryAgentBench의 점진적 형식과 다중 세션 에이전트 과제(MemoryArena, IFCMemoryBench)이며, 최소 3개 시드를 사용하고 합성 잡음 주입은 하지 않는다.

### G5. 장기 기억의 비용, 지연 시간, 오류 전파는 과제 성공률과 대비하여 측정되지 않았다.

[1, 7, 10, 40] (근거 4편 · 신뢰도 평균 3.2)

비용과 지연 시간 절감은 자체 보고이고, 하네스 연구는 설계별 수치가 보이지 않은 채 비용이 크거나 취약한 기반이 있다고 언급하며, 잘못 저장된 기억이 이후 과제에 어떤 영향을 미치는지 측정한 연구는 없다. 유일한 전파 증거는 시뮬레이션된 다중 에이전트 환경의 독성 연구이며, 이는 과제 성공을 다루지 않는다.

- 제안 RQ: 잘못되었거나 오염된(poisoned) 기억 항목은 기억 설계별로 이후의 다단계 성공률에 어떤 영향을 미치며, 기억 비용을 포함하면 토큰당, 초당 성공률은 얼마인가?
- 방법: 각 기억 설계에 잘못된 교훈이나 워크플로를 0%, 10%, 30% 삽입하고 성공률의 하락과 영향을 받는 이후 에피소드의 수를 측정하는 결함 주입(fault-injection) 실험. 기억이 있을 때와 없을 때의 비용 조정 성공률(1k 토큰당 및 분당 성공률)을 보고한다.
- 데이터: 토큰 수와 지연 시간이 기록된 ALFWorld와 WebArena 에피소드. 결함은 저장된 성찰이나 워크플로를 손상시켜 생성하며, 2개의 백본과 최소 3개 시드를 사용한다.

## 6. 향후 연구 방향

§5 의 제안을 한 표로 요약했다 (전문은 각 Gap). 근거는 해당 Gap 의 인용을 따른다.

| # | 제안 RQ | 연구 설계 | 데이터 | 근거 Gap |
|---|---|---|---|---|
| 1 | 백본과 환경을 고정했을 때 일화, 의미, 계층, 그래프 기억은 다단계 성공률에서 차이가 나는가, 그리고 그 순위는 에이전트 루프(ReAct, Reflexion 방식, 계획 후 실행)에 따라 달라지는가? | 사전 등록된 요인 설계(factorial) 실험: 기억 설계 4개 x 에이전트 루프 3개 x 백본 3개로, 셀당 최소 5개 시드를 사용하고 성공률을 주요 결과로 하여 혼합 효과… | 보류 평가 과제를 포함한 ALFWorld, ScienceWorld, WebArena, Mind2Web 과제 분할을 사용하며, 오픈소스 하네스… | G1 [1, 3, 12] |
| 2 | 검색된 기억 항목의 수나 토큰 예산이 늘어남에 따라 과제 성공률은 어떻게 변하며, 단계 수준 검색과 궤적 수준 검색 중 무엇을 택하느냐가 성공률이 떨어지기 시작하는 지점을 이동시키는가? | top-k(0, 1, 3, 5, 10, 20)를 검색 세분도(단계 대 궤적), 그리고 오라클 대 잡음 있는 관련도와 교차시켜 변화시키는 에이전트 내(within-agent) 용량… | 이전 에피소드로 채워진 하나의 기억 저장소를 사용하는 ALFWorld와 WebArena이며, 2-3개의 백본과 최소 3개 시드를 사용한다. 대… | G2 [1, 11, 35] |
| 3 | 계획자(planner)에게 검색된 기억에 대한 접근을 주는 것이 실행자(executor)에게만 주는 것보다 장기 시계 성공률을 더 높이는가, 그리고 기억으로부터의 계획 재사용은 단계 수준 힌트 이상의 이득을 더하는가? | 하나의 계획-실행(plan-and-execute) 에이전트에 대해 기억 접근을 계획 시에만, 실행 시에만, 둘 다, 또는 둘 다 없음으로 설정하고 계획 재사용 조건을 추가한 통제… | MemoryArena 방식의 상호 의존적 다중 세션 과제와 WebArena 또는 ALFWorld의 장기 시계 부분집합. 약 200개 과제, 3… | G3 [13, 34, 35, 44] |
| 4 | 자연스럽게 누적되고 일부는 오래된 항목을 포함하는 많은 순차 세션에 걸쳐, 에빙하우스식 망각, 보상 기반 가지치기, 궤적 인식 보존이 FIFO와 무제한 기억보다 성공률을 향상시키는가? | 무제한, FIFO, 망각 곡선, 보상 가지치기, TraceRetain 정책을 비교하는 20+개의 연속 세션에 걸친 종단적 절제 실험으로, 정해진 세션 시점마다 성공률을 측정한다.… | MemoryAgentBench의 점진적 형식과 다중 세션 에이전트 과제(MemoryArena, IFCMemoryBench)이며, 최소 3개 시… | G4 [2, 6, 7, 10] |
| 5 | 잘못되었거나 오염된(poisoned) 기억 항목은 기억 설계별로 이후의 다단계 성공률에 어떤 영향을 미치며, 기억 비용을 포함하면 토큰당, 초당 성공률은 얼마인가? | 각 기억 설계에 잘못된 교훈이나 워크플로를 0%, 10%, 30% 삽입하고 성공률의 하락과 영향을 받는 이후 에피소드의 수를 측정하는 결함 주입(fault-injection) 실… | 토큰 수와 지연 시간이 기록된 ALFWorld와 WebArena 에피소드. 결함은 저장된 성찰이나 워크플로를 손상시켜 생성하며, 2개의 백본과… | G5 [1, 7, 10, 40] |

## 7. 한계와 신뢰도

- 전문이 아니라 초록과 메타데이터만 읽었기 때문에 수치, 절제 실험의 세부 사항, 실험 통제가 누락되거나 잘못 해석되었을 수 있으며, 여러 벤치마크 및 방법 초록에는 결과가 전혀 보고되어 있지 않다.

- 검색은 제한된 기간 내에서 OpenAlex와 arXiv만 대상으로 했으며 후보 312편 중 73편이 평가되었다. 증거의 상당수는 동료 심사를 거치지 않은 사전 출판물이고, 일부 항목은 중복(JARVIS-1, 에이전트 서베이)이어서 두 번 세어서는 안 된다.

- 기억-계획 상호작용에 관한 하위 질문(rq4)은 사실상 답이 나오지 않았다. RAP, TRAD, CAPEAM, JARVIS-1, 계획 서베이는 분리된 기억 절제 실험이나 성공률 수치를 제공하지 않는다. 비평자가 요청한 rq1, rq2, rq3, rq4, rq6에 대한 후속 검색은 수행할 수 없었으므로 이 공백들은 그대로 남아 있다.

- 검색 및 저장 메커니즘(rq2)에 관한 증거는 대부분 다단계 과제 성공률이 아닌 대화형 및 QA 벤치마크에서 나오므로, 과제 성공에 관한 결론의 근거는 약하다. 보존과 방해 잡음에 대한 통제된 증거는 시드 두 개를 사용한 단일 ALFWorld 환경이며, SwiftSage 절제 실험은 하나의 벤치마크와 하나의 에이전트에 해당한다.

- 비용, 지연 시간, 망각 또는 가지치기의 이득(VIMBank, MRAgent, AdMem)은 자체 보고이거나 수치가 없으며, 과제 성공에 영향을 미치는 오류 전파는 측정되지 않았다. 유일한 전파 증거는 시뮬레이션된 다중 에이전트 환경에서의 주제와 간접적으로만 관련된 독성 연구이다.

- 'unselective memory degrades success' 주장은 하네스 연구 하나로만 직접 뒷받침되며, 인용된 다른 연구들은 정밀도 저하나 QA 잡음 내성을 보여 줄 뿐이므로 확신도는 낮다. 구조화 기억 대 단순 기억의 'conflict'는 진정한 모순이 아니라 범위의 차이(맞춤형으로 함께 설계된 에이전트 대 기반을 고정한 비교)일 가능성이 크다.

**품질 게이트가 자동으로 기록한 미해결 항목** (사람이 쓴 것이 아니라 파이프라인 검사 결과다):

- 검색 부족 — arXiv unavailable (disabled after 2 failures, 10 queries skipped); OpenAlex only

- 검색 부족 — arXiv unavailable (disabled after 2 failures, 0 queries skipped); OpenAlex only

- Critic 미해결 — major issue(s) persist after re-search, recorded as limitation: rq4: rq4 passes on count but is effectively unanswered: RAP (2402.03610, no numbers), TRAD (2403.06221, in-context demonstrations, no results), CAPEAM (2308.07241, e
## 품질 한눈에

| 검색 후보 | 평가 문헌 | 실존 검증 (DOI/arXiv) | sub-RQ 커버리지 (근거 ≥ 3편) | 출처 있는 claim | 근거 ≥ 2편인 Gap | Critic 판정 / Replan | 품질 게이트 미해결 | 비용 · 시간 |
|---|---|---|---|---|---|---|---|---|
| 312 | 73 | 73/73 (100%) | 6/6 | 12/12 | 5/5 | 2회 / 1회 | 3건 → §7 | $0.66 · 7.1분 |

LLM 없이 코드가 계산한 결정적 지표다 (`cost.json` `checks`). 인용 번호 [n] 은 바로 아래 참고문헌을 가리킨다.


## 참고문헌 (52편)

본문·표에 번호로 인용된 문헌. 모두 검색 도구(OpenAlex·arXiv·Crossref)가 반환한 메타데이터 그대로이며 DOI/arXiv id 로 실존이 확인됐다.

1. Wei-Chieh Huang, Weizhi Zhang, Yuchen Wu et al. (2026). Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2608.15008
2. Hu, Yuanzhe, Yu Wang, Julian McAuley (2025). Evaluating Memory in LLM Agents via Incremental Multi-Turn Interactions. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2507.05257
3. Petr Anokhin, Semenov, Nikita, Artyom Sorokin et al. (2024). AriGraph: Learning Knowledge Graph World Models with Episodic Memory for LLM Agents. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2407.04363
4. Zeyu Zhang, Xiaohe Bo, Chen Ma et al. (2024). A Survey on the Memory Mechanism of Large Language Model based Agents. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2404.13501
5. Noah Shinn, Cassano, Federico, Berman, Edward et al. (2023). Reflexion: Language Agents with Verbal Reinforcement Learning. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2303.11366
6. Runzhe Wang, Huilin Lu, Shengjie Liu et al. (2026). AdMem: Advanced Memory for Task-solving Agents. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2606.06787
7. Pranath Reddy (2026). Selective Memory Retention for Long-Horizon LLM Agents. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2606.29178
8. Zexue He, Yu Wang, Churan Zhi et al. (2026). MemoryArena: Benchmarking Agent Memory in Interdependent Multi-Session Agentic Tasks. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2602.16313
9. João Meneses dos Santos, Arlindo L. Oliveira (2026). Cognitive Extensions for Dual-Process Language Agents: Memory and Self-Reflection in Interactive Environments. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2609.19128
10. Kun Li, Jing Lei Xin, Chengang Jing (2024). Vector Storage Based Long-term Memory Research on LLM. *International Journal of Advanced Network Monitoring and Controls*. https://doi.org/10.2478/ijanmc-2024-0029
11. Ruihong Zeng, Jinyuan Fang, Siwei Liu et al. (2024). On the Structural Memory of LLM Agents. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2412.15266
12. Zora Zhiruo Wang, Mao, Jiayuan, Daniel Fried et al. (2024). Agent Workflow Memory. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2409.07429
13. Byeonghwi Kim, Jinyeon Kim, Yuyeong Kim et al. (2023). Context-Aware Planning and Environment-Aware Memory for Instruction Following Embodied Agents. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2308.07241
14. Ke Yang, Zixi Chen, Xuan He et al. (2026). PlugMem: A Task-Agnostic Plugin Memory Module for LLM Agents. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2603.03296
15. Wujiang Xu, Wang, Yu, 1964-, Kai Mei et al. (2026). MemGym: a Long-Horizon Memory Environment for LLM Agents. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2605.20833
16. Yuanyi Song, Yukai Wang, Xinbei Ma et al. (2026). Retrieval-Driven Memory Reconsolidation for Long-Term LLM Agents. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2609.16053
17. Lei Wang, Chen Ma, Xueyang Feng et al. (2024). A survey on large language model based autonomous agents. *Frontiers of Computer Science*. https://doi.org/10.1007/s11704-024-40231-1
18. Wang, Lei, Chen Ma, Xueyang Feng et al. (2023). A Survey on Large Language Model based Autonomous Agents. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2308.11432
19. Zihao Wang, Shaofei Cai, Anji Liu et al. (2024). JARVIS -1: Open-World Multi-Task Agents With Memory-Augmented Multimodal Language Models. *IEEE Transactions on Pattern Analysis and Machine Intelligence*. https://doi.org/10.1109/tpami.2024.3511593
20. Zihao Wang, Shaofei Cai, Anji Liu et al. (2023). JARVIS-1: Open-World Multi-task Agents with Memory-Augmented Multimodal Language Models. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2311.05997
21. Shuo Ji, Yibo Li, Bryan Hooi (2026). Memory is Reconstructed, Not Retrieved: Graph Memory for LLM Agents. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2606.06036
22. Yushi Zou, Austin Cheng, Abdulrahman Aldossary et al. (2025). El Agente: An autonomous agent for quantum chemistry. *Matter*. https://doi.org/10.1016/j.matt.2025.102263
23. Derong Xu, Yi Wen, Pengyue Jia et al. (2025). From Single to Multi-Granularity: Toward Long-Term Memory Association and Selection of Conversational Agents. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2505.19549
24. Yuqi Zhu, Shuofei Qiao, Yixin Ou et al. (2024). KnowAgent: Knowledge-Augmented Planning for LLM-Based Agents. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2403.03101
25. Hao Yang, Shiqi Shen, Haoxuan Li et al. (2026). Rosetta Memory: Adaptive Memory for Cross-LLM Agents. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2606.07711
26. Yuxin Liao, Le Wu, Min Hou et al. (2026). LeanMem: Simple and Efficient Long-Term Memory for LLM Agents. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2608.03463
27. Ioannis Chrysochos (2026). Mind-Tool: Domain Memory Architecture for AI Agents. *Journal of Engineering and Artificial Intelligence*. https://doi.org/10.64142/jeai.2.1.43
28. Kostas Hatalis, Despina Christou, Vyshnavi Kondapalli (2025). Review of Case-Based Reasoning for LLM Agents: Theoretical Foundations, Architectural Components, and Cognitive Integration. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2504.06943
29. Jiageng Mao, Junjie Ye, Yuxi Qian et al. (2023). A Language Agent for Autonomous Driving. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2311.10813
30. Kuan Fang, Alexander Toshev, Li Fei-Fei et al. (2019). Scene Memory Transformer for Embodied Agents in Long-Horizon Tasks. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.1903.03878
31. Wenwen Wang, Ah‐Hwee Tan, Loo-Nin Teow (2016). Semantic Memory Modeling and Memory Interaction in Learning Agents. *IEEE Transactions on Systems Man and Cybernetics Systems*. https://doi.org/10.1109/tsmc.2016.2531683
32. Wangchunshu Zhou, Yuchen Eleanor Jiang, Long Li et al. (2023). Agents: An Open-source Framework for Autonomous Language Agents. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2309.07870
33. Muhammad Azam, Tanveer Rafiq, Falak Gul Naz et al. (2024). A Novel Model of Narrative Memory for Conscious Agents. *International Journal of Information Systems and Computer Technologies*. https://doi.org/10.58325/ijisct.003.01.0080
34. Tomoyuki Kagaya, Thong Jing Yuan, Yuxuan Lou et al. (2024). RAP: Retrieval-Augmented Planning with Contextual Memory for Multimodal LLM Agents. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2402.03610
35. Ruiwen Zhou, Yingxuan Yang, Muning Wen et al. (2024). TRAD: Enhancing LLM Agents with Step-Wise Thought Retrieval and Aligned Decision. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2403.06221
36. Changyu Du, Alexander Vosseler, Filippo Mazza et al. (2026). IFCMemoryBench: Evaluating Long-Term Memory of LLM-Based Agents in BIM Information Retrieval. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2607.26072
37. Zhuoshi Pan, Qianhui Wu, Huiqiang Jiang et al. (2025). On Memory Construction and Retrieval for Personalized Conversational Agents. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2502.05589
38. Jakub Rada, Viliam Lisý (2026). Towards Improving Sequential Decision-Making in LLM Agents via Experience Memory. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2608.03420
39. Lei Liu, Xiaoyan Yang, Yue Shen et al. (2023). Think-in-Memory: Recalling and Post-thinking Enable LLMs with Long-Term Memory. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2311.08719
40. Yian Wang, Agam Goyal, Yuen Chen et al. (2026). State Contamination in Memory-Augmented LLM Agents. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2605.16746
41. Nick Alonso, Tomas Figliolia, Anthony Ndirango et al. (2024). Toward Conversational Agents with Context and Time Sensitive Long-term Memory. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2406.00057
42. Qimeng Niu, Bowen Hao, Zixuan Zhang et al. (2026). Enhancing Group Recommendation with Memory-Augmented Reasoning in LLM Agent. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2608.21939
43. Swapnil Bharamu Patil (2026). Agentic MailBot: Autonomous Multi-Agent Email Response System with Contextual Intelligence. *INTERANTIONAL JOURNAL OF SCIENTIFIC RESEARCH IN ENGINEERING AND MANAGEMENT*. https://doi.org/10.55041/ijsrem63558
44. Xu Huang, Weiwen Liu, Xiaolong Chen et al. (2024). Understanding the planning of LLM agents: A survey. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2402.02716
45. Xun Jiang, Feng Li, Han Zhao et al. (2024). Long Term Memory: The Foundation of AI Self-Evolution. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2410.15665
46. Tula Masterman, Sandi Besen, Mason Sawtell et al. (2024). The Landscape of Emerging AI Agent Architectures for Reasoning, Planning, and Tool Calling: A Survey. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2404.11584
47. Haoyuan Wu, Zhuolun He, Xinyun Zhang et al. (2024). ChatEDA: A Large Language Model Powered Autonomous Agent for EDA. *IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems*. https://doi.org/10.1109/tcad.2024.3383347
48. Sparsh Bajoria -, Sumit Ranjan, Adhitya M et al. (2026). From Language Models to Agentic AI: A Survey of Autonomous, Action-Enabled, and Collaborative LLM Agents. *Cognitive Computation*. https://doi.org/10.1007/s12559-026-10619-1
49. Mayk Caldas Ramos, Christopher J. Collison, Andrew Dickson White (2024). A review of large language models and autonomous agents in chemistry. *Chemical Science*. https://doi.org/10.1039/d4sc03921a
50. Q. C. Zhao, Xujiang Zhao, Yanchi Liu et al. (2024). SAUP: Situation Awareness Uncertainty Propagation on LLM Agent. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2412.01033
51. James C. L. Chow, Kay Li (2026). From Dialogue Systems to Autonomous Agents: A Modeling Framework for Ethical Generative AI in Healthcare. *Information*. https://doi.org/10.3390/info17040361
52. Tharakesvulu Vangalapat, Samreen Iftekhar Shaikh (2026). Trustworthy Agentic AI: A Survey and Taxonomy of Secure Coordination and Hallucination Mitigation in Multi-Agent Large Language Model Systems. *International Journal of Innovative Science and Research Technology (IJISRT)*. https://doi.org/10.38124/ijisrt/26feb1090
