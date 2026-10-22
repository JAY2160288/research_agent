# Research Brief: 생성형 AI 활용이 대학원생의 연구 생산성과 연구 품질에 미치는 영향

> RQ — 생성형 AI(generative AI)의 사용은 대학원생의 연구 생산성(research productivity)과 연구 품질(research quality)에 어떤 영향을 미치는가?

> 본문은 영어 원문(brief.json)을 한국어로 옮긴 것이다. 논문 제목·저자·DOI·검색 쿼리·§3 표의 결과 요약은 원문 그대로이며, 영어 원문 리포트는 같은 폴더의 `report.en.md`.

## 요약

524편의 후보 중 98편을 평가했으며, 근거는 설문, 소규모 질적 연구, 리뷰·논평, LLM 출력 검증 연구, 그리고 EFL 환경의 소규모 무작위 대조시험(RCT) 2편으로 이루어져 있다. 합의된 부분은 학생들이 주로 글쓰기·브레인스토밍·정보 검색·paraphrasing에 GenAI를 쓰고, 대학원생도 연구·논문 작성에 유용하다고 인식한다는 점이다. 다만 이 인식은 소규모 자기보고에 기반하며, 작성 속도·소요 시간·출판 성과를 실제로 측정한 연구는 하나도 없어 연구 생산성 주장은 검증되지 않은 상태다. 품질 측면에서는 LLM이 생성한 참고문헌에 허위·부정확 사례가 많고 DOI 정확도가 특히 낮다는 결과가 있으나, 정량 근거는 GPT-3.5와 10개 주제를 다룬 연구 1편에 의존한다. AI 보강 텍스트는 가독성은 높게 평가되지만 연구 세부와 성찰적 통찰은 부족하다는 잠정적 시사점이 있다. 상충 지점으로, AI 산출물에 대한 비판적 평가가 도움이 되는지 해가 되는지는 결과가 서로 대립한다기보다 측정 구성개념(지각된 품질·자기효능감 대 글쓰기 성찰)과 표본(일반 학부생 대 대학원·박사과정)이 달라 직접 비교가 어렵다. 가장 중요한 Gap은 대학원생의 생산성과 전문가 평가 기반 연구 품질을 통제 연구나 로그 기반으로 측정한 근거가 없다는 점과, 코딩·통계·데이터 분석 활용에 대한 근거가 전무하다는 점이다.

## 먼저 읽을 문헌 (10편)

Evaluator 의 관련성(rel)·신뢰도(reli) 점수 순. 전체 평가 표는 §3, 서지 정보는 참고문헌.

| # | 문헌 | 핵심 결과 | sub-RQ | rel · reli |
|---|---|---|---|---|
| [1] | Navigating the Ethical Frontier: Graduate Students’ Experiences with Generative… (2025) | 생성형 AI 연구 도구 COREI를 한 달간 사용한 뒤, 많은 참가자는 이 도구를 책임 있게 사용하면 학문 윤리를 위반하지 않으면서 연구를 향상시킬 수 있는 협업 도구로 인식하게 되었다. 주제는 학문적 진실성(academic integrity), 행위주체성(agency), 저자 자격(… | rq1, rq2, rq4, rq5 | 5 · 3 |
| [2] | Students-Generative AI interaction patterns and its impact on academic writing (2025) | AI 리터러시(AI literacy)가 높은 대학원생은 GenAI 글쓰기 시스템과 상호작용할 때 협업적 패턴을 보였으며, 확인된 상호작용 패턴들은 학술 글쓰기 수행도를 기준으로 비교되었다. AI 리터러시는 학생이 GenAI와 상호작용하는 방식을 형성하였다. | rq2, rq4, rq6 | 5 · 3 |
| [3] | Human-AI collaboration patterns in AI-assisted academic writing (2024) | GAI 글쓰기 도구와 반복적이고 상호작용이 활발한 과정을 거친 박사과정생은 대체로 더 나은 글쓰기 수행도를 보였다. 이 연구는 서로 구별되는 인간-AI 협업 패턴을 확인한다. | rq2, rq3, rq4, rq6 | 5 · 3 |
| [4] | Graduate Students' ChatGPT Experience and Perspectives during Thesis Writing (2024) | 이 연구는 학위논문 작성에서 ChatGPT에 대한 대학원생의 인식을 조사하였으며, 유용성, 사용 용이성, 글쓰기 품질에 미치는 영향, 신뢰성과 진실성 문제를 다루었다. 또한 기술통계(descriptive statistics)로 성별 차이를 검토한다. | rq1, rq2, rq3, rq5 | 5 · 3 |
| [5] | ChatGPT and its impact on research supervision: Insights from Australian postgr… (2023) | 학생들은 연구 진행의 가속, 연구 품질 향상, 학술적·전문적 기술 향상, 비판적 사고 강화, 더 큰 자신감과 자율성을 보고하였으며, 지도교수는 전략적 지도 역할로 전환하였다. | rq1, rq2, rq3, rq4 | 5 · 3 |
| [6] | Generative AI-assisted feedback and EFL writing: a study on proficiency, revisi… (2025) | Grammarly AI 피드백 집단은 사후 글쓰기 검사에서 통제집단보다 유의하게 높은 점수를 받았다. AI 기능의 사용은 더 많은 수정, 그리고 내용·구성·응집성의 향상과 상관이 있었다. | rq2, rq4, rq6 | 4 · 3 |
| [7] | Enhancing disciplinary voice through feedback-seeking in AI-assisted doctoral w… (2025) | AI 도구는 출판을 위한 박사과정 글쓰기의 특정 측면을 향상시킬 수 있으나, 효과적인 사용에는 비판적 참여가 필요하다. 피드백 추구(feedback-seeking)는 AI의 입력이 글쓰기를 강화하는 때와 학문 분야 전문성이 필요한 때를 판단하는 핵심 기술로 나타났다. | rq2, rq4, rq3 | 4 · 3 |
| [8] | A Qualitative Inquiry Into Metacognitive Strategies of Postgraduate Students in… (2024) | 대학원생은 ChatGPT로 글을 쓸 때 계획, 점검, 평가, 정보 관리, 디버깅 전반에 걸쳐 상위인지 전략(metacognitive strategies)을 사용하였다. 디버깅은 GenAI 지원 학술 글쓰기에서만 나타나는 고유한 전략으로 보였다. | rq4, rq2, rq3 | 4 · 3 |
| [9] | Postgraduate Students’ Perceptions on the Benefits Associated with Artificial I… (2024) | 대학원생은 ChatGPT가 학업 및 연구 성공에 유익하다고 인식하였다. 초록이 잘려 있어 구체적인 활용 방식은 상세히 나타나 있지 않다. | rq2, rq1, rq3 | 4 · 3 |
| [10] | The Challenges of Applying ChatGPT in the Academic Writing of Postgraduate Stud… (2025) | 이 연구는 이들 대학원생에게 학술 글쓰기에서 ChatGPT를 사용할 때의 어려움이 이점보다 크다고 보고한다. 이는 과의존(overreliance)과 글쓰기의 어려움에 관한 것이다. | rq2, rq5 | 4 · 2 |

## 1. 주제 재정의

- RQ: 생성형 AI(generative AI)의 사용은 대학원생의 연구 생산성(research productivity)과 연구 품질(research quality)에 어떤 영향을 미치는가?
- 독립변수: Generative AI use
- 종속변수: Research productivity, Research quality
- 대상: Graduate students
- 핵심 개념: generative AI, graduate students, research productivity, research quality, higher education, academic writing, AI-assisted research

## 2. 조사 계획

전략: ChatGPT 시대의 생성형 AI가 관련 개입이므로 2022년부터 현재까지에 초점을 맞추고, 대학원생 또는 박사과정생을 대상으로 한 실증 연구(실험, 준실험, 설문, 면담, 혼합 방법)와 체계적 문헌고찰(systematic review)을 우선한다. 학부생 또는 K-12에 한정된 연구, 인간 사용자가 없는 순수 기술적 LLM 벤치마크, 정책적 맥락을 제공하지 않는 한 자료 없는 의견 글은 제외한다. 대부분의 연구가 객관적 산출물 측정이 아닌 자기보고에 의존하므로 rq6과 rq2의 연구 품질에 관한 인과적 증거가 가장 빈약할 것으로 예상한다.}

- **rq1** 생성형 AI의 사용은 글쓰기 속도, 출판 산출량, 시간 효율성과 같은 대학원생의 연구 생산성에 어떤 영향을 미치는가?

- **rq2** 생성형 AI의 사용은 글쓰기 품질, 논증, 방법론적 엄밀성, 독창성을 포함한 대학원생 연구의 품질에 어떤 영향을 미치는가?

- **rq3** 대학원생은 어떤 연구 과제와 단계(문헌 검토, 데이터 분석, 코딩, 글쓰기, 편집)에서 생성형 AI를 사용하며, 그 사용은 얼마나 널리 퍼져 있고 얼마나 다양한가?

- **rq4** 생성형 AI가 연구 성과에 미치는 영향을 형성하는 기제와 조절 변인(AI 리터러시, 학문 분야, 프롬프트 작성 기술, 지도교수의 지도, 기관 정책, 영어 능력)은 무엇인가?

- **rq5** 대학원 연구에서 생성형 AI를 사용할 때 환각 인용(hallucinated citations), 학문적 진실성 위반, 과의존, 기술 쇠퇴(skill erosion) 등 어떤 위험과 의도치 않은 영향이 발생하는가?

- **rq6** 대학원 교육에서 생성형 AI를 다룬 연구들은 연구 생산성과 연구 품질을 어떻게 측정하며, 연구 설계와 증거의 질은 어떠한가?

<details><summary>검색 쿼리 전체 (33개 — Replan 으로 추가된 쿼리 포함)</summary>

- **rq1** (7개): ChatGPT graduate students research productivity; generative AI doctoral students scholarly output; AI-assisted writing time efficiency graduate researchers; large language models thesis writing productivity; randomized controlled trial LLM assistance time-on-task writing; field experiment ChatGPT task completion time university students; generative AI adoption early-career researchers publication counts bibliometric

- **rq2** (7개): generative AI research quality graduate students; ChatGPT academic writing quality postgraduate; AI tools methodological rigor doctoral research; LLM assistance originality scholarly writing quality; rubric-scored thesis proposal writing ChatGPT master's students; expert-rated argument quality AI-assisted doctoral manuscript; randomized comparison LLM assistance graduate research paper quality

- **rq3** (4개): graduate students use of ChatGPT literature review; AI tools academic research tasks doctoral students survey; generative AI adoption postgraduate researchers patterns; AI-assisted research workflow graduate education

- **rq4** (4개): AI literacy moderator graduate research outcomes; non-native English doctoral students generative AI writing support; supervisor guidance generative AI graduate students; discipline differences generative AI use academic research

- **rq5** (7개): ChatGPT hallucinated references academic integrity graduate students; overreliance generative AI critical thinking doctoral researchers; deskilling generative AI research skills postgraduate; ethical concerns AI-assisted research authorship; audit fabricated citations ChatGPT generated literature reviews; reference accuracy large language model bibliographic hallucination rate; cognitive offloading skill decline doctoral students generative AI longitudinal

- **rq6** (4개): measuring research productivity AI tools higher education; experimental study generative AI academic writing assessment; generative AI graduate education empirical evidence review; systematic review ChatGPT higher education research outcomes

</details>

## 3. Evidence Table

### 3.1 Evidence map — sub-RQ × 신뢰도

| sub-RQ | 편수 (rel ≥ 3) | 신뢰도 4~5 | 신뢰도 3 | 신뢰도 ≤ 2 | 평균 신뢰도 | 커버 |
|---|---|---|---|---|---|---|
| rq1 | 5 | 0 | 4 | 1 | 2.8 | ✅ |
| rq2 | 19 | 2 | 13 | 4 | 2.9 | ✅ |
| rq3 | 16 | 4 | 8 | 4 | 3.0 | ✅ |
| rq4 | 16 | 4 | 11 | 1 | 3.2 | ✅ |
| rq5 | 14 | 4 | 5 | 5 | 2.9 | ✅ |
| rq6 | 4 | 0 | 4 | 0 | 3.0 | ✅ |

커버 기준은 Critic 결정적 검사와 같다 (relevance ≥ 3 인 문헌 3편 이상). 신뢰도는 Evaluator 가 설계·표본·출처로 매긴 0~5 점.

### 3.2 sub-RQ 별 문헌

#### rq1 — 생성형 AI의 사용은 글쓰기 속도, 출판 산출량, 시간 효율성과 같은 대학원생의 연구 생산성에 어떤 영향을 미치는가?

10편 (rel ≥ 3: 5편) · 신뢰도 평균 2.6 · 상위: [4] Graduate Students' ChatGPT Experience and Perspectives duri… (2024) (reli 3); [1] Navigating the Ethical Frontier: Graduate Students’ Experie… (2025) (reli 3); [5] ChatGPT and its impact on research supervision: Insights fr… (2023) (reli 3)

<details><summary>전체 표 (10편)</summary>

| # | 문헌 | rel | reli | method | sample | finding |
|---|---|---|---|---|---|---|
| [4] | Graduate Students' ChatGPT Experience and Perspectives during Thesis… (2024) | 5 | 3 | questionnaire survey with descriptive statistics, n=80 | 80 male and female postgraduate students across fields at J… | 이 연구는 학위논문 작성에서 ChatGPT에 대한 대학원생의 인식을 조사하였으며, 유용성, 사용 용이성, 글쓰기 품질에 미치는 영향, 신뢰성과 진실성 문제를 다루었다. 또한 기술통계(descriptive statistics)로 성별 차이를 검토한다. |
| [1] | Navigating the Ethical Frontier: Graduate Students’ Experiences with… (2025) | 5 | 3 | semi-structured interviews with thematic analysis, n=10 | 10 graduate students (4 doctoral, 6 master's) at one large… | 생성형 AI 연구 도구 COREI를 한 달간 사용한 뒤, 많은 참가자는 이 도구를 책임 있게 사용하면 학문 윤리를 위반하지 않으면서 연구를 향상시킬 수 있는 협업 도구로 인식하게 되었다. 주제는 학문적 진실성(academic integrity), 행위주체성(agency), 저자 자격(… |
| [5] | ChatGPT and its impact on research supervision: Insights from Austral… (2023) | 5 | 3 | qualitative study (practices and perspectives of students) | 20 postgraduate research students in Australia with at leas… | 학생들은 연구 진행의 가속, 연구 품질 향상, 학술적·전문적 기술 향상, 비판적 사고 강화, 더 큰 자신감과 자율성을 보고하였으며, 지도교수는 전략적 지도 역할로 전환하였다. |
| [9] | Postgraduate Students’ Perceptions on the Benefits Associated with Ar… (2024) | 4 | 3 | qualitative study with semi-structured interviews n=10 and thematic analysis | 10 master's students at two historically disadvantaged Sout… | 대학원생은 ChatGPT가 학업 및 연구 성공에 유익하다고 인식하였다. 초록이 잘려 있어 구체적인 활용 방식은 상세히 나타나 있지 않다. |
| [11] | Potentials and Challenges of Chatbot-Supported Thesis Writing: An Aut… (2023) | 3 | 2 | autoethnography (single-author case; logs and ChatGPT chat histories) | one student writing a bachelor's thesis | Using ChatGPT while writing a bachelor's thesis was documented through logs and chat histories, and recommendations for student use were derived from a framewo… |
| [12] | Generative AI and the Automating of Academia (2023) | 2 | 3 | survey n=284 with critical analysis | 284 UK academics | Based on a survey of UK academics' GAI use, the paper argues that GAI is framed as relief from overwork in academia. The abstract is truncated before the findi… |
| [13] | Teacher Education Students’ Practices, Benefits, and Challenges in th… (2026) | 2 | 3 | mixed-methods study (survey plus qualitative data) | 314 undergraduate teacher education students (Early Childho… | Most students use GenAI mainly for academic purposes such as information searching, data analysis, study advice and exam preparation. They reported benefits su… |
| [14] | Exploring the Usage of ChatGPT in Higher Education: Frequency and Imp… (2023) | 2 | 2 | qualitative interviews with lecturers | lecturers (number not stated in abstract) | Lecturers reported that ChatGPT helps with finding information, generating ideas, translating and creating alternative questions, and they perceived improved p… |
| [15] | ChatGPT is a Remarkable Tool—For Experts (2023) | 2 | 2 | narrative review / experimental exploration of ChatGPT capabilities (design unc… |  | ChatGPT can enhance productivity and improve writing style across domains including scientific writing, but it risks incorrect and fictitious responses, code i… |
| [16] | Benefits, limits, and risks of ChatGPT in medicine (2025) | 2 | 2 | narrative review |  | ChatGPT is reported to yield efficiency gains in healthcare (e.g., 70% reduction in administrative time for discharge summaries) and to accelerate research wor… |

</details>

#### rq2 — 생성형 AI의 사용은 글쓰기 품질, 논증, 방법론적 엄밀성, 독창성을 포함한 대학원생 연구의 품질에 어떤 영향을 미치는가?

31편 (rel ≥ 3: 19편) · 신뢰도 평균 3.0 · 상위: [3] Human-AI collaboration patterns in AI-assisted academic wri… (2024) (reli 3); [4] Graduate Students' ChatGPT Experience and Perspectives duri… (2024) (reli 3); [1] Navigating the Ethical Frontier: Graduate Students’ Experie… (2025) (reli 3)

<details><summary>전체 표 (31편)</summary>

| # | 문헌 | rel | reli | method | sample | finding |
|---|---|---|---|---|---|---|
| [3] | Human-AI collaboration patterns in AI-assisted academic writing (2024) | 5 | 3 | learning-analytics study of recorded interactions (HMM sequence analysis, clust… | 10 doctoral students, 626 recorded activities | GAI 글쓰기 도구와 반복적이고 상호작용이 활발한 과정을 거친 박사과정생은 대체로 더 나은 글쓰기 수행도를 보였다. 이 연구는 서로 구별되는 인간-AI 협업 패턴을 확인한다. |
| [4] | Graduate Students' ChatGPT Experience and Perspectives during Thesis… (2024) | 5 | 3 | questionnaire survey with descriptive statistics, n=80 | 80 male and female postgraduate students across fields at J… | 이 연구는 학위논문 작성에서 ChatGPT에 대한 대학원생의 인식을 조사하였으며, 유용성, 사용 용이성, 글쓰기 품질에 미치는 영향, 신뢰성과 진실성 문제를 다루었다. 또한 기술통계(descriptive statistics)로 성별 차이를 검토한다. |
| [1] | Navigating the Ethical Frontier: Graduate Students’ Experiences with… (2025) | 5 | 3 | semi-structured interviews with thematic analysis, n=10 | 10 graduate students (4 doctoral, 6 master's) at one large… | 생성형 AI 연구 도구 COREI를 한 달간 사용한 뒤, 많은 참가자는 이 도구를 책임 있게 사용하면 학문 윤리를 위반하지 않으면서 연구를 향상시킬 수 있는 협업 도구로 인식하게 되었다. 주제는 학문적 진실성(academic integrity), 행위주체성(agency), 저자 자격(… |
| [2] | Students-Generative AI interaction patterns and its impact on academi… (2025) | 5 | 3 | mixed-methods behavioral study using think-aloud protocols, screen recordings,… | 36 Chinese graduate students | AI 리터러시(AI literacy)가 높은 대학원생은 GenAI 글쓰기 시스템과 상호작용할 때 협업적 패턴을 보였으며, 확인된 상호작용 패턴들은 학술 글쓰기 수행도를 기준으로 비교되었다. AI 리터러시는 학생이 GenAI와 상호작용하는 방식을 형성하였다. |
| [5] | ChatGPT and its impact on research supervision: Insights from Austral… (2023) | 5 | 3 | qualitative study (practices and perspectives of students) | 20 postgraduate research students in Australia with at leas… | 학생들은 연구 진행의 가속, 연구 품질 향상, 학술적·전문적 기술 향상, 비판적 사고 강화, 더 큰 자신감과 자율성을 보고하였으며, 지도교수는 전략적 지도 역할로 전환하였다. |
| [8] | A Qualitative Inquiry Into Metacognitive Strategies of Postgraduate S… (2024) | 4 | 3 | qualitative study using audio recordings, semi-structured interviews, and human… | 13 postgraduate students in Hong Kong | 대학원생은 ChatGPT로 글을 쓸 때 계획, 점검, 평가, 정보 관리, 디버깅 전반에 걸쳐 상위인지 전략(metacognitive strategies)을 사용하였다. 디버깅은 GenAI 지원 학술 글쓰기에서만 나타나는 고유한 전략으로 보였다. |
| [9] | Postgraduate Students’ Perceptions on the Benefits Associated with Ar… (2024) | 4 | 3 | qualitative study with semi-structured interviews n=10 and thematic analysis | 10 master's students at two historically disadvantaged Sout… | 대학원생은 ChatGPT가 학업 및 연구 성공에 유익하다고 인식하였다. 초록이 잘려 있어 구체적인 활용 방식은 상세히 나타나 있지 않다. |
| [6] | Generative AI-assisted feedback and EFL writing: a study on proficien… (2025) | 4 | 3 | randomized controlled study with pre/post tests plus semi-structured interviews… | 60 postgraduate EFL students, randomly assigned to experime… | Grammarly AI 피드백 집단은 사후 글쓰기 검사에서 통제집단보다 유의하게 높은 점수를 받았다. AI 기능의 사용은 더 많은 수정, 그리고 내용·구성·응집성의 향상과 상관이 있었다. |
| [7] | Enhancing disciplinary voice through feedback-seeking in AI-assisted… (2025) | 4 | 3 | qualitative textual analysis of student reflections and AI interactions within… | 55 doctoral students, linguistically and disciplinarily div… | AI 도구는 출판을 위한 박사과정 글쓰기의 특정 측면을 향상시킬 수 있으나, 효과적인 사용에는 비판적 참여가 필요하다. 피드백 추구(feedback-seeking)는 AI의 입력이 글쓰기를 강화하는 때와 학문 분야 전문성이 필요한 때를 판단하는 핵심 기술로 나타났다. |
| [10] | The Challenges of Applying ChatGPT in the Academic Writing of Postgra… (2025) | 4 | 2 | qualitative survey questionnaire plus short interviews | 25 postgraduate English-major students at IUH, Ho Chi Minh… | 이 연구는 이들 대학원생에게 학술 글쓰기에서 ChatGPT를 사용할 때의 어려움이 이점보다 크다고 보고한다. 이는 과의존(overreliance)과 글쓰기의 어려움에 관한 것이다. |
| [17] | Exploring students’ AI literacy and its effects on their AI output qu… (2025) | 3 | 4 | online survey with structural equation modeling, n=286 | 286 Austrian university students | AI technical understanding and practical application positively influenced AI self-efficacy, and practical application also raised AI output quality. AI critic… |
| [18] | Hallucination Rates and Reference Accuracy of ChatGPT and Bard for Sy… (2024) | 3 | 4 | comparative analysis of LLM outputs against gold-standard systematic reviews | 11 systematic reviews across 4 fields, 33 prompts to LLMs | ChatGPT and Bard were tested on reproducing references from published systematic reviews using recall, precision, F1 and hallucination rate, to assess reliabil… |
| [19] | Enhancing academic writing skills and motivation: assessing the effic… (2023) | 3 | 3 | mixed-methods study with randomized pre-test/post-test design and semi-structur… | 50 Chinese EFL students randomized to ChatGPT-assisted or t… | Students receiving ChatGPT-assisted instruction showed significant improvements in writing skills and motivation compared with the control group. |
| [20] | The Future of Feedback: Integrating Peer and Generative AI Reviews to… (2024) | 3 | 3 | exploratory post-course survey (quantitative and qualitative) with thematic ana… | graduate students at a US university, 2023 term (size not s… | Peer reviews were perceived as slightly higher than AI reviews on quality, usefulness and actionability. Thematic analysis showed distinct strengths and limita… |
| [21] | The great AI witch hunt: Reviewers’ perception and (Mis)conception of… (2024) | 3 | 3 | snippet-based online survey | 17 peer reviewers from top-tier HCI conferences | AI-augmented writing improved readability, language diversity and informativeness but often lacked research details and reflective insights. Reviewers could no… |
| [22] | Impact of ChatGPT on Academic Writing at Moroccan Universities (2024) | 3 | 3 | questionnaire survey n=180 | 180 volunteers (university students and educators) at Moroc… | Respondents affirmed ChatGPT's value as a tool for academic writing but acknowledged it can be both beneficial and harmful. Students use it without guidance or… |
| [23] | ChatGPT in academic writing: Maximizing its benefits and minimizing t… (2023) | 3 | 2 | narrative review |  | The review lists potential uses of ChatGPT for novice researchers in research proposal preparation and manuscript writing. It stresses reliability concerns and… |
| [11] | Potentials and Challenges of Chatbot-Supported Thesis Writing: An Aut… (2023) | 3 | 2 | autoethnography (single-author case; logs and ChatGPT chat histories) | one student writing a bachelor's thesis | Using ChatGPT while writing a bachelor's thesis was documented through logs and chat histories, and recommendations for student use were derived from a framewo… |
| [24] | Navigating the AI frontier: Should we fear ChatGPT use in higher educ… (2024) | 3 | 2 | narrative review with ChatGPT trials (transcripts), guideline development |  | The authors examine how ChatGPT is used by academia, young researchers and students, and distinguish positive use cases, areas requiring caution, limitations a… |
| [25] | Writing without borders: AI and cross-cultural convergence in academi… (2025) | 2 | 4 | large-scale bibliometric/readability analysis with mixed GLM and lexical tracki… | over one million English-language social science abstracts… | Writing complexity (readability) improved globally, with non-native English-speaking countries showing notable advances, and China surpassing traditional leade… |
| [26] | From Offloading to Engagement: An Experimental Study on Structured Pr… (2025) | 2 | 4 | cross-country randomized experiment with conditions (human-only, unguided AI, g… | n=150 participants (Germany, Switzerland, UK); 450 evaluate… | Unguided AI use fostered cognitive offloading without improving reasoning quality, whereas structured prompting reduced offloading and improved critical reason… |
| [27] | Can ChatGPT support prospective teachers in physics task development? (2023) | 2 | 4 | RCT n=26 | 26 prospective physics teacher students | Students using ChatGPT showed no difference in task correctness compared with a textbook group, but the textbook group achieved higher clarity and more often e… |
| [28] | Mastering knowledge: the impact of generative AI on student learning… (2025) | 2 | 3 | quasi-experimental qualitative analysis with quantitative content analysis of s… | 192 student reflections in higher education | Students who used GenAI to construct and augment knowledge (mastery approach) achieved higher-level learning than those who used it procedurally. The authors s… |
| [29] | Student Perceptions of ChatGPT Use in a College Essay Assignment: Imp… (2024) | 2 | 3 | pre-post study with quantitative and thematic analysis | 24 undergraduate engineering students | ChatGPT did not simplify the writing process, and students raised concerns about accuracy and limited feedback on output confidence. Students came to see it as… |
| [30] | The model student: GPT-4 performance on graduate biomedical science e… (2024) | 2 | 3 | benchmark evaluation of GPT-4 on graduate exams (seven blinded) | nine graduate-level biomedical science examinations | GPT-4 scored above the student average in seven of nine exams and above all students on four. It performed poorly on questions with simulated-data figures or h… |
| [31] | ChatGPT versus human essayists: an exploration of the impact of artif… (2024) | 2 | 3 | blinded marking comparison of AI-written vs human essays | AI essays vs first-year undergraduate English essays at Oxf… | AI-written essays averaged 60.46 versus 63.57 for human essays, a non-significant difference (p = 0.10). AI essays tended to describe rather than analyse and l… |
| [32] | Detection of GPT-4 Generated Text in Higher Education: Combining Acad… (2023) | 2 | 3 | experimental detection study with marking by academic staff | 22 ChatGPT-generated submissions marked by 15 academic staf… | Turnitin flagged 91% of the AI-generated submissions as containing AI content, but only 54.8% of the content was identified as AI-generated. Staff reported onl… |
| [33] | Impact of Generative AI on Critical Thinking Skills in Undergraduates… (2024) | 2 | 3 | systematic literature review of 30 papers | 30 selected papers on generative AI and undergraduate criti… | About half of the 30 reviewed papers suggest generative AI benefits undergraduate critical thinking, while others are inconclusive. Study design limitations pr… |
| [34] | Mathematical Capabilities of ChatGPT (2023) | 2 | 3 | benchmark evaluation of LLMs on new datasets (GHOSTS, miniGHOSTS) curated by ma… | Graduate-level mathematics datasets; ChatGPT (two versions)… | Benchmarks ChatGPT and GPT-4 on graduate-level natural-language mathematics with fine-grained metrics and tests whether they can serve as helpful assistants to… |
| [35] | On the assessment of generative AI in modeling tasks: an experience r… (2023) | 2 | 3 | experience report / exploratory evaluation of ChatGPT on UML modeling tasks |  | ChatGPT's performance on software modeling is limited, with syntactic and semantic deficiencies, inconsistent responses and scalability issues, in contrast to… |
| [36] | From Struggle to Mastery: AI-Powered Writing Skills in ESL Education (2025) | 1 | 3 | design-based research with iterative implementation | 10th grade bilingual ESL secondary students in Colombia | Combining the Writing Workshop Instructional Model with Grammarly and ChatGPT feedback significantly improved academic writing performance, and learners report… |

</details>

#### rq3 — 대학원생은 어떤 연구 과제와 단계(문헌 검토, 데이터 분석, 코딩, 글쓰기, 편집)에서 생성형 AI를 사용하며, 그 사용은 얼마나 널리 퍼져 있고 얼마나 다양한가?

30편 (rel ≥ 3: 16편) · 신뢰도 평균 2.8 · 상위: [3] Human-AI collaboration patterns in AI-assisted academic wri… (2024) (reli 3); [4] Graduate Students' ChatGPT Experience and Perspectives duri… (2024) (reli 3); [5] ChatGPT and its impact on research supervision: Insights fr… (2023) (reli 3)

<details><summary>전체 표 (30편)</summary>

| # | 문헌 | rel | reli | method | sample | finding |
|---|---|---|---|---|---|---|
| [3] | Human-AI collaboration patterns in AI-assisted academic writing (2024) | 5 | 3 | learning-analytics study of recorded interactions (HMM sequence analysis, clust… | 10 doctoral students, 626 recorded activities | GAI 글쓰기 도구와 반복적이고 상호작용이 활발한 과정을 거친 박사과정생은 대체로 더 나은 글쓰기 수행도를 보였다. 이 연구는 서로 구별되는 인간-AI 협업 패턴을 확인한다. |
| [4] | Graduate Students' ChatGPT Experience and Perspectives during Thesis… (2024) | 5 | 3 | questionnaire survey with descriptive statistics, n=80 | 80 male and female postgraduate students across fields at J… | 이 연구는 학위논문 작성에서 ChatGPT에 대한 대학원생의 인식을 조사하였으며, 유용성, 사용 용이성, 글쓰기 품질에 미치는 영향, 신뢰성과 진실성 문제를 다루었다. 또한 기술통계(descriptive statistics)로 성별 차이를 검토한다. |
| [5] | ChatGPT and its impact on research supervision: Insights from Austral… (2023) | 5 | 3 | qualitative study (practices and perspectives of students) | 20 postgraduate research students in Australia with at leas… | 학생들은 연구 진행의 가속, 연구 품질 향상, 학술적·전문적 기술 향상, 비판적 사고 강화, 더 큰 자신감과 자율성을 보고하였으며, 지도교수는 전략적 지도 역할로 전환하였다. |
| [8] | A Qualitative Inquiry Into Metacognitive Strategies of Postgraduate S… (2024) | 4 | 3 | qualitative study using audio recordings, semi-structured interviews, and human… | 13 postgraduate students in Hong Kong | 대학원생은 ChatGPT로 글을 쓸 때 계획, 점검, 평가, 정보 관리, 디버깅 전반에 걸쳐 상위인지 전략(metacognitive strategies)을 사용하였다. 디버깅은 GenAI 지원 학술 글쓰기에서만 나타나는 고유한 전략으로 보였다. |
| [9] | Postgraduate Students’ Perceptions on the Benefits Associated with Ar… (2024) | 4 | 3 | qualitative study with semi-structured interviews n=10 and thematic analysis | 10 master's students at two historically disadvantaged Sout… | 대학원생은 ChatGPT가 학업 및 연구 성공에 유익하다고 인식하였다. 초록이 잘려 있어 구체적인 활용 방식은 상세히 나타나 있지 않다. |
| [7] | Enhancing disciplinary voice through feedback-seeking in AI-assisted… (2025) | 4 | 3 | qualitative textual analysis of student reflections and AI interactions within… | 55 doctoral students, linguistically and disciplinarily div… | AI 도구는 출판을 위한 박사과정 글쓰기의 특정 측면을 향상시킬 수 있으나, 효과적인 사용에는 비판적 참여가 필요하다. 피드백 추구(feedback-seeking)는 AI의 입력이 글쓰기를 강화하는 때와 학문 분야 전문성이 필요한 때를 판단하는 핵심 기술로 나타났다. |
| [37] | Students’ voices on generative AI: perceptions, benefits, and challen… (2023) | 3 | 4 | cross-sectional survey n=399 | 399 undergraduate and postgraduate students from various di… | Students were generally positive about GenAI and saw value in writing and brainstorming assistance and research and analysis support. They also raised concerns… |
| [38] | Artificial Intelligence in studies—use of ChatGPT and AI-based tools… (2023) | 3 | 4 | nationwide cross-sectional online survey, n>6300 | More than 6300 university students across Germany | Almost two-thirds of students use or have used AI tools in their studies, and almost half name ChatGPT or GPT-4. Use is highest in engineering, mathematics and… |
| [39] | Generative AI and the future of higher education: a threat to academi… (2024) | 3 | 4 | cross-national online survey, n=1217 | 1217 participants (higher education students and staff) fro… | Respondents showed high awareness of GenAI tools and intended to continue using them, mainly for information retrieval and text paraphrasing. The study discuss… |
| [40] | Influence of Topic Familiarity and Prompt Specificity on Citation Fab… (2025) | 3 | 4 | experimental study of GPT-4o generated literature reviews (6 reviews, ≥20 citat… | 6 GPT-4o-generated literature reviews on 3 mental health di… | The study examines how often GPT-4o fabricates or mis-cites bibliographic references in literature reviews, and whether this varies with topic familiarity/scie… |
| [41] | Combining human and artificial intelligence for enhanced AI literacy… (2024) | 3 | 3 | convergent mixed-methods case study, n=37 | 37 graduate students in three 8-week courses in a College o… | Participants appeared to feel more comfortable using GenAI tools after the course experience. The study examines how a GenAI reviewer tool and image generators… |
| [22] | Impact of ChatGPT on Academic Writing at Moroccan Universities (2024) | 3 | 3 | questionnaire survey n=180 | 180 volunteers (university students and educators) at Moroc… | Respondents affirmed ChatGPT's value as a tool for academic writing but acknowledged it can be both beneficial and harmful. Students use it without guidance or… |
| [23] | ChatGPT in academic writing: Maximizing its benefits and minimizing t… (2023) | 3 | 2 | narrative review |  | The review lists potential uses of ChatGPT for novice researchers in research proposal preparation and manuscript writing. It stresses reliability concerns and… |
| [42] | Is ChatGPT a “Fire of Prometheus” for Non-Native English-Speaking Res… (2023) | 3 | 2 | narrative review / commentary |  | LLMs can lower the barrier to English academic writing for non-native researchers, especially for Introduction and Discussion sections. Risks include hallucina… |
| [11] | Potentials and Challenges of Chatbot-Supported Thesis Writing: An Aut… (2023) | 3 | 2 | autoethnography (single-author case; logs and ChatGPT chat histories) | one student writing a bachelor's thesis | Using ChatGPT while writing a bachelor's thesis was documented through logs and chat histories, and recommendations for student use were derived from a framewo… |
| [24] | Navigating the AI frontier: Should we fear ChatGPT use in higher educ… (2024) | 3 | 2 | narrative review with ChatGPT trials (transcripts), guideline development |  | The authors examine how ChatGPT is used by academia, young researchers and students, and distinguish positive use cases, areas requiring caution, limitations a… |
| [43] | Students’ Acceptance of ChatGPT in Higher Education: An Extended Unif… (2023) | 2 | 4 | cross-sectional survey with PLS-SEM (UTAUT2 extended) | 503 Polish state university students | Habit was the strongest predictor of behavioral intention to use ChatGPT, followed by performance expectancy and hedonic motivation. Behavioral intention had t… |
| [44] | ChatGPT in medicine: A cross-disciplinary systematic review of ChatGP… (2024) | 2 | 4 | systematic review of 83 studies | 83 studies (PubMed, Medline, Scopus) | ChatGPT is useful for scientific research and academic writing, aiding grammar, clarity and coherence and helping non-English speakers, but has limitations inc… |
| [45] | What Is the Impact of ChatGPT on Education? A Rapid Review of the Lit… (2023) | 2 | 3 | rapid review of 50 articles with content analysis | 50 articles published Dec 2022 to Feb 2023 | ChatGPT performance varied across subject domains, from outstanding in economics to unsatisfactory in mathematics. It could assist instructors and students but… |
| [46] | Drivers of generative AI adoption in higher education through the len… (2024) | 2 | 3 | cross-sectional online questionnaire with PLS-SEM (Theory of Planned Behaviour) | 130 lecturers and 168 students in higher education institut… | Perceived strengths of GenAI positively affected attitudes, subjective norms and perceived behavioural control, which positively influenced intention to use an… |
| [47] | Medical Student Experiences and Perceptions of ChatGPT and Artificial… (2023) | 2 | 3 | cross-sectional web-based survey | 265 of 325 graduating medical students (81.5% response rate) | The vast majority of respondents denied using ChatGPT in medical school. The study gauges graduating students' experiences and perspectives on ChatGPT and AI i… |
| [13] | Teacher Education Students’ Practices, Benefits, and Challenges in th… (2026) | 2 | 3 | mixed-methods study (survey plus qualitative data) | 314 undergraduate teacher education students (Early Childho… | Most students use GenAI mainly for academic purposes such as information searching, data analysis, study advice and exam preparation. They reported benefits su… |
| [48] | Students’ Experiences of Using ChatGPT in an Undergraduate Programmin… (2024) | 2 | 3 | anonymous post-exercise surveys | part-time undergraduate students in a five-week Java course | Most students viewed ChatGPT positively for learning programming, mainly using it for background knowledge, syntax, concepts and algorithm suggestions. Some ab… |
| [14] | Exploring the Usage of ChatGPT in Higher Education: Frequency and Imp… (2023) | 2 | 2 | qualitative interviews with lecturers | lecturers (number not stated in abstract) | Lecturers reported that ChatGPT helps with finding information, generating ideas, translating and creating alternative questions, and they perceived improved p… |
| [49] | An overview of the capabilities of ChatGPT for medical writing and it… (2023) | 2 | 2 | brief overview/commentary |  | The article summarizes ChatGPT capabilities for medical writing, lists generative tools and AI text detectors, and offers recommendations on academic integrity… |
| [50] | The role of ChatGPT in higher education: Benefits, challenges, and fu… (2023) | 2 | 2 | perspective paper |  | The paper identifies five benefits, including support for research and data analysis, and five challenges, including academic integrity and reliability. It pro… |
| [16] | Benefits, limits, and risks of ChatGPT in medicine (2025) | 2 | 2 | narrative review |  | ChatGPT is reported to yield efficiency gains in healthcare (e.g., 70% reduction in administrative time for discharge summaries) and to accelerate research wor… |
| [51] | ChatGPT for Education and Research: Opportunities, Threats, and Strat… (2023) | 2 | 2 | narrative discussion with ChatGPT coding demonstrations (no formal design state… |  | Discusses opportunities (personalized feedback, accessibility) and threats (cheating, reduced critical thinking, difficulty evaluating output) of ChatGPT in ed… |
| [52] | The Role of ChatGPT in Data Science: How AI-Assisted Conversational I… (2023) | 2 | 1 | perspective article |  | Argues ChatGPT can assist data scientists with data cleaning, preprocessing, model training and result interpretation, while noting bias and plagiarism concern… |
| [53] | A Bibliometric Exposition and Review on Leveraging LLMs for Programmi… (2025) | 1 | 2 | bibliometric analysis and review |  | LLMs, especially ChatGPT, could play a significant role in programming education, though benefits must be weighed against risks. The paper also evaluates ChatG… |

</details>

#### rq4 — 생성형 AI가 연구 성과에 미치는 영향을 형성하는 기제와 조절 변인(AI 리터러시, 학문 분야, 프롬프트 작성 기술, 지도교수의 지도, 기관 정책, 영어 능력)은 무엇인가?

31편 (rel ≥ 3: 16편) · 신뢰도 평균 3.1 · 상위: [3] Human-AI collaboration patterns in AI-assisted academic wri… (2024) (reli 3); [1] Navigating the Ethical Frontier: Graduate Students’ Experie… (2025) (reli 3); [2] Students-Generative AI interaction patterns and its impact… (2025) (reli 3)

<details><summary>전체 표 (31편)</summary>

| # | 문헌 | rel | reli | method | sample | finding |
|---|---|---|---|---|---|---|
| [3] | Human-AI collaboration patterns in AI-assisted academic writing (2024) | 5 | 3 | learning-analytics study of recorded interactions (HMM sequence analysis, clust… | 10 doctoral students, 626 recorded activities | GAI 글쓰기 도구와 반복적이고 상호작용이 활발한 과정을 거친 박사과정생은 대체로 더 나은 글쓰기 수행도를 보였다. 이 연구는 서로 구별되는 인간-AI 협업 패턴을 확인한다. |
| [1] | Navigating the Ethical Frontier: Graduate Students’ Experiences with… (2025) | 5 | 3 | semi-structured interviews with thematic analysis, n=10 | 10 graduate students (4 doctoral, 6 master's) at one large… | 생성형 AI 연구 도구 COREI를 한 달간 사용한 뒤, 많은 참가자는 이 도구를 책임 있게 사용하면 학문 윤리를 위반하지 않으면서 연구를 향상시킬 수 있는 협업 도구로 인식하게 되었다. 주제는 학문적 진실성(academic integrity), 행위주체성(agency), 저자 자격(… |
| [2] | Students-Generative AI interaction patterns and its impact on academi… (2025) | 5 | 3 | mixed-methods behavioral study using think-aloud protocols, screen recordings,… | 36 Chinese graduate students | AI 리터러시(AI literacy)가 높은 대학원생은 GenAI 글쓰기 시스템과 상호작용할 때 협업적 패턴을 보였으며, 확인된 상호작용 패턴들은 학술 글쓰기 수행도를 기준으로 비교되었다. AI 리터러시는 학생이 GenAI와 상호작용하는 방식을 형성하였다. |
| [5] | ChatGPT and its impact on research supervision: Insights from Austral… (2023) | 5 | 3 | qualitative study (practices and perspectives of students) | 20 postgraduate research students in Australia with at leas… | 학생들은 연구 진행의 가속, 연구 품질 향상, 학술적·전문적 기술 향상, 비판적 사고 강화, 더 큰 자신감과 자율성을 보고하였으며, 지도교수는 전략적 지도 역할로 전환하였다. |
| [8] | A Qualitative Inquiry Into Metacognitive Strategies of Postgraduate S… (2024) | 4 | 3 | qualitative study using audio recordings, semi-structured interviews, and human… | 13 postgraduate students in Hong Kong | 대학원생은 ChatGPT로 글을 쓸 때 계획, 점검, 평가, 정보 관리, 디버깅 전반에 걸쳐 상위인지 전략(metacognitive strategies)을 사용하였다. 디버깅은 GenAI 지원 학술 글쓰기에서만 나타나는 고유한 전략으로 보였다. |
| [6] | Generative AI-assisted feedback and EFL writing: a study on proficien… (2025) | 4 | 3 | randomized controlled study with pre/post tests plus semi-structured interviews… | 60 postgraduate EFL students, randomly assigned to experime… | Grammarly AI 피드백 집단은 사후 글쓰기 검사에서 통제집단보다 유의하게 높은 점수를 받았다. AI 기능의 사용은 더 많은 수정, 그리고 내용·구성·응집성의 향상과 상관이 있었다. |
| [7] | Enhancing disciplinary voice through feedback-seeking in AI-assisted… (2025) | 4 | 3 | qualitative textual analysis of student reflections and AI interactions within… | 55 doctoral students, linguistically and disciplinarily div… | AI 도구는 출판을 위한 박사과정 글쓰기의 특정 측면을 향상시킬 수 있으나, 효과적인 사용에는 비판적 참여가 필요하다. 피드백 추구(feedback-seeking)는 AI의 입력이 글쓰기를 강화하는 때와 학문 분야 전문성이 필요한 때를 판단하는 핵심 기술로 나타났다. |
| [37] | Students’ voices on generative AI: perceptions, benefits, and challen… (2023) | 3 | 4 | cross-sectional survey n=399 | 399 undergraduate and postgraduate students from various di… | Students were generally positive about GenAI and saw value in writing and brainstorming assistance and research and analysis support. They also raised concerns… |
| [38] | Artificial Intelligence in studies—use of ChatGPT and AI-based tools… (2023) | 3 | 4 | nationwide cross-sectional online survey, n>6300 | More than 6300 university students across Germany | Almost two-thirds of students use or have used AI tools in their studies, and almost half name ChatGPT or GPT-4. Use is highest in engineering, mathematics and… |
| [39] | Generative AI and the future of higher education: a threat to academi… (2024) | 3 | 4 | cross-national online survey, n=1217 | 1217 participants (higher education students and staff) fro… | Respondents showed high awareness of GenAI tools and intended to continue using them, mainly for information retrieval and text paraphrasing. The study discuss… |
| [17] | Exploring students’ AI literacy and its effects on their AI output qu… (2025) | 3 | 4 | online survey with structural equation modeling, n=286 | 286 Austrian university students | AI technical understanding and practical application positively influenced AI self-efficacy, and practical application also raised AI output quality. AI critic… |
| [19] | Enhancing academic writing skills and motivation: assessing the effic… (2023) | 3 | 3 | mixed-methods study with randomized pre-test/post-test design and semi-structur… | 50 Chinese EFL students randomized to ChatGPT-assisted or t… | Students receiving ChatGPT-assisted instruction showed significant improvements in writing skills and motivation compared with the control group. |
| [41] | Combining human and artificial intelligence for enhanced AI literacy… (2024) | 3 | 3 | convergent mixed-methods case study, n=37 | 37 graduate students in three 8-week courses in a College o… | Participants appeared to feel more comfortable using GenAI tools after the course experience. The study examines how a GenAI reviewer tool and image generators… |
| [22] | Impact of ChatGPT on Academic Writing at Moroccan Universities (2024) | 3 | 3 | questionnaire survey n=180 | 180 volunteers (university students and educators) at Moroc… | Respondents affirmed ChatGPT's value as a tool for academic writing but acknowledged it can be both beneficial and harmful. Students use it without guidance or… |
| [54] | Evaluation of Large Language Model Performance and Reliability for Ci… (2024) | 3 | 3 | cross-disciplinary evaluation of citation accuracy | 10 topics, 102 citations generated by ChatGPT (GPT-3.5) | About 73-77% of ChatGPT-generated citations were confirmed to exist across natural sciences and humanities, but DOI presence and accuracy were low, especially… |
| [42] | Is ChatGPT a “Fire of Prometheus” for Non-Native English-Speaking Res… (2023) | 3 | 2 | narrative review / commentary |  | LLMs can lower the barrier to English academic writing for non-native researchers, especially for Introduction and Discussion sections. Risks include hallucina… |
| [25] | Writing without borders: AI and cross-cultural convergence in academi… (2025) | 2 | 4 | large-scale bibliometric/readability analysis with mixed GLM and lexical tracki… | over one million English-language social science abstracts… | Writing complexity (readability) improved globally, with non-native English-speaking countries showing notable advances, and China surpassing traditional leade… |
| [43] | Students’ Acceptance of ChatGPT in Higher Education: An Extended Unif… (2023) | 2 | 4 | cross-sectional survey with PLS-SEM (UTAUT2 extended) | 503 Polish state university students | Habit was the strongest predictor of behavioral intention to use ChatGPT, followed by performance expectancy and hedonic motivation. Behavioral intention had t… |
| [55] | How Generative AI Influences Students’ Self-Regulated Learning and Cr… (2025) | 2 | 4 | systematic review (PRISMA) of 38 studies | 38 studies selected from 3,214 documents identified (2022–2… | 71.4% of studies reported a positive role of generative AI in self-regulated learning and 62.5% in critical thinking. Researchers cautioned that overreliance m… |
| [44] | ChatGPT in medicine: A cross-disciplinary systematic review of ChatGP… (2024) | 2 | 4 | systematic review of 83 studies | 83 studies (PubMed, Medline, Scopus) | ChatGPT is useful for scientific research and academic writing, aiding grammar, clarity and coherence and helping non-English speakers, but has limitations inc… |
| [26] | From Offloading to Engagement: An Experimental Study on Structured Pr… (2025) | 2 | 4 | cross-country randomized experiment with conditions (human-only, unguided AI, g… | n=150 participants (Germany, Switzerland, UK); 450 evaluate… | Unguided AI use fostered cognitive offloading without improving reasoning quality, whereas structured prompting reduced offloading and improved critical reason… |
| [56] | Investigating influencing factors of learning satisfaction in AI Chat… (2024) | 2 | 3 | cross-sectional questionnaire survey with SEM (TAM-based) | 262 students at King Faisal University, Saudi Arabia | Interaction learning, collaborative learning and information quality influenced ChatGPT adoption and continued use, with perceived ease of use and usefulness a… |
| [28] | Mastering knowledge: the impact of generative AI on student learning… (2025) | 2 | 3 | quasi-experimental qualitative analysis with quantitative content analysis of s… | 192 student reflections in higher education | Students who used GenAI to construct and augment knowledge (mastery approach) achieved higher-level learning than those who used it procedurally. The authors s… |
| [57] | Reimagining Higher Education: Navigating the Challenges of Generative… (2025) | 2 | 3 | mixed methods study |  | The study identifies key challenges and interdependencies affecting GenAI adoption in higher education, including academic integrity, critical thinking and rel… |
| [58] | ChatGPT and the rise of generative AI: Threat to academic integrity? (2023) | 2 | 2 | overview/commentary on arguments (no systematic method stated) |  | The paper concludes that ChatGPT and other GenAI could revolutionise academia but, depending on how they are used, could undermine academic integrity. It calls… |
| [59] | Exploring the Potential Impact of Artificial Intelligence (AI) on Int… (2023) | 2 | 2 | research essay (non-systematic conceptual analysis) |  | The essay discusses AI applications (chatbots for learning and research, personalized learning, analytics) for international students, and states these could i… |
| [60] | The promise and challenges of generative AI in education (2024) | 2 | 2 | expert commentary (nine contributors) |  | The commentary says GenAI can enhance learning design, feedback and assessment, while noting limitations, ethical consequences and potential misuses. It calls… |
| [15] | ChatGPT is a Remarkable Tool—For Experts (2023) | 2 | 2 | narrative review / experimental exploration of ChatGPT capabilities (design unc… |  | ChatGPT can enhance productivity and improve writing style across domains including scientific writing, but it risks incorrect and fictitious responses, code i… |
| [50] | The role of ChatGPT in higher education: Benefits, challenges, and fu… (2023) | 2 | 2 | perspective paper |  | The paper identifies five benefits, including support for research and data analysis, and five challenges, including academic integrity and reliability. It pro… |
| [61] | Generative AI in Higher Education: Balancing Innovation and Integrity (2025) | 2 | 2 | narrative literature review |  | GenAI offers automation and efficiency benefits but poses challenges to academic integrity, equity, bias and the authenticity of student work. The paper argues… |
| [62] | The Impact of Adaptive Learning Technologies, Personalized Feedback,… (2025) | 1 | 3 | quantitative survey study (design not fully clear from abstract), n=500 | 500 students from science, engineering, humanities and soci… | Adaptive learning technologies, personalized feedback and interactive AI tools improved student engagement, and students with higher digital literacy were more… |

</details>

#### rq5 — 대학원 연구에서 생성형 AI를 사용할 때 환각 인용(hallucinated citations), 학문적 진실성 위반, 과의존, 기술 쇠퇴(skill erosion) 등 어떤 위험과 의도치 않은 영향이 발생하는가?

50편 (rel ≥ 3: 14편) · 신뢰도 평균 2.7 · 상위: [4] Graduate Students' ChatGPT Experience and Perspectives duri… (2024) (reli 3); [1] Navigating the Ethical Frontier: Graduate Students’ Experie… (2025) (reli 3); [10] The Challenges of Applying ChatGPT in the Academic Writing… (2025) (reli 2)

<details><summary>전체 표 (50편)</summary>

| # | 문헌 | rel | reli | method | sample | finding |
|---|---|---|---|---|---|---|
| [4] | Graduate Students' ChatGPT Experience and Perspectives during Thesis… (2024) | 5 | 3 | questionnaire survey with descriptive statistics, n=80 | 80 male and female postgraduate students across fields at J… | 이 연구는 학위논문 작성에서 ChatGPT에 대한 대학원생의 인식을 조사하였으며, 유용성, 사용 용이성, 글쓰기 품질에 미치는 영향, 신뢰성과 진실성 문제를 다루었다. 또한 기술통계(descriptive statistics)로 성별 차이를 검토한다. |
| [1] | Navigating the Ethical Frontier: Graduate Students’ Experiences with… (2025) | 5 | 3 | semi-structured interviews with thematic analysis, n=10 | 10 graduate students (4 doctoral, 6 master's) at one large… | 생성형 AI 연구 도구 COREI를 한 달간 사용한 뒤, 많은 참가자는 이 도구를 책임 있게 사용하면 학문 윤리를 위반하지 않으면서 연구를 향상시킬 수 있는 협업 도구로 인식하게 되었다. 주제는 학문적 진실성(academic integrity), 행위주체성(agency), 저자 자격(… |
| [10] | The Challenges of Applying ChatGPT in the Academic Writing of Postgra… (2025) | 4 | 2 | qualitative survey questionnaire plus short interviews | 25 postgraduate English-major students at IUH, Ho Chi Minh… | 이 연구는 이들 대학원생에게 학술 글쓰기에서 ChatGPT를 사용할 때의 어려움이 이점보다 크다고 보고한다. 이는 과의존(overreliance)과 글쓰기의 어려움에 관한 것이다. |
| [37] | Students’ voices on generative AI: perceptions, benefits, and challen… (2023) | 3 | 4 | cross-sectional survey n=399 | 399 undergraduate and postgraduate students from various di… | Students were generally positive about GenAI and saw value in writing and brainstorming assistance and research and analysis support. They also raised concerns… |
| [39] | Generative AI and the future of higher education: a threat to academi… (2024) | 3 | 4 | cross-national online survey, n=1217 | 1217 participants (higher education students and staff) fro… | Respondents showed high awareness of GenAI tools and intended to continue using them, mainly for information retrieval and text paraphrasing. The study discuss… |
| [18] | Hallucination Rates and Reference Accuracy of ChatGPT and Bard for Sy… (2024) | 3 | 4 | comparative analysis of LLM outputs against gold-standard systematic reviews | 11 systematic reviews across 4 fields, 33 prompts to LLMs | ChatGPT and Bard were tested on reproducing references from published systematic reviews using recall, precision, F1 and hallucination rate, to assess reliabil… |
| [40] | Influence of Topic Familiarity and Prompt Specificity on Citation Fab… (2025) | 3 | 4 | experimental study of GPT-4o generated literature reviews (6 reviews, ≥20 citat… | 6 GPT-4o-generated literature reviews on 3 mental health di… | The study examines how often GPT-4o fabricates or mis-cites bibliographic references in literature reviews, and whether this varies with topic familiarity/scie… |
| [21] | The great AI witch hunt: Reviewers’ perception and (Mis)conception of… (2024) | 3 | 3 | snippet-based online survey | 17 peer reviewers from top-tier HCI conferences | AI-augmented writing improved readability, language diversity and informativeness but often lacked research details and reflective insights. Reviewers could no… |
| [22] | Impact of ChatGPT on Academic Writing at Moroccan Universities (2024) | 3 | 3 | questionnaire survey n=180 | 180 volunteers (university students and educators) at Moroc… | Respondents affirmed ChatGPT's value as a tool for academic writing but acknowledged it can be both beneficial and harmful. Students use it without guidance or… |
| [54] | Evaluation of Large Language Model Performance and Reliability for Ci… (2024) | 3 | 3 | cross-disciplinary evaluation of citation accuracy | 10 topics, 102 citations generated by ChatGPT (GPT-3.5) | About 73-77% of ChatGPT-generated citations were confirmed to exist across natural sciences and humanities, but DOI presence and accuracy were low, especially… |
| [23] | ChatGPT in academic writing: Maximizing its benefits and minimizing t… (2023) | 3 | 2 | narrative review |  | The review lists potential uses of ChatGPT for novice researchers in research proposal preparation and manuscript writing. It stresses reliability concerns and… |
| [42] | Is ChatGPT a “Fire of Prometheus” for Non-Native English-Speaking Res… (2023) | 3 | 2 | narrative review / commentary |  | LLMs can lower the barrier to English academic writing for non-native researchers, especially for Introduction and Discussion sections. Risks include hallucina… |
| [11] | Potentials and Challenges of Chatbot-Supported Thesis Writing: An Aut… (2023) | 3 | 2 | autoethnography (single-author case; logs and ChatGPT chat histories) | one student writing a bachelor's thesis | Using ChatGPT while writing a bachelor's thesis was documented through logs and chat histories, and recommendations for student use were derived from a framewo… |
| [24] | Navigating the AI frontier: Should we fear ChatGPT use in higher educ… (2024) | 3 | 2 | narrative review with ChatGPT trials (transcripts), guideline development |  | The authors examine how ChatGPT is used by academia, young researchers and students, and distinguish positive use cases, areas requiring caution, limitations a… |
| [55] | How Generative AI Influences Students’ Self-Regulated Learning and Cr… (2025) | 2 | 4 | systematic review (PRISMA) of 38 studies | 38 studies selected from 3,214 documents identified (2022–2… | 71.4% of studies reported a positive role of generative AI in self-regulated learning and 62.5% in critical thinking. Researchers cautioned that overreliance m… |
| [44] | ChatGPT in medicine: A cross-disciplinary systematic review of ChatGP… (2024) | 2 | 4 | systematic review of 83 studies | 83 studies (PubMed, Medline, Scopus) | ChatGPT is useful for scientific research and academic writing, aiding grammar, clarity and coherence and helping non-English speakers, but has limitations inc… |
| [26] | From Offloading to Engagement: An Experimental Study on Structured Pr… (2025) | 2 | 4 | cross-country randomized experiment with conditions (human-only, unguided AI, g… | n=150 participants (Germany, Switzerland, UK); 450 evaluate… | Unguided AI use fostered cognitive offloading without improving reasoning quality, whereas structured prompting reduced offloading and improved critical reason… |
| [45] | What Is the Impact of ChatGPT on Education? A Rapid Review of the Lit… (2023) | 2 | 3 | rapid review of 50 articles with content analysis | 50 articles published Dec 2022 to Feb 2023 | ChatGPT performance varied across subject domains, from outstanding in economics to unsatisfactory in mathematics. It could assist instructors and students but… |
| [46] | Drivers of generative AI adoption in higher education through the len… (2024) | 2 | 3 | cross-sectional online questionnaire with PLS-SEM (Theory of Planned Behaviour) | 130 lecturers and 168 students in higher education institut… | Perceived strengths of GenAI positively affected attitudes, subjective norms and perceived behavioural control, which positively influenced intention to use an… |
| [29] | Student Perceptions of ChatGPT Use in a College Essay Assignment: Imp… (2024) | 2 | 3 | pre-post study with quantitative and thematic analysis | 24 undergraduate engineering students | ChatGPT did not simplify the writing process, and students raised concerns about accuracy and limited feedback on output confidence. Students came to see it as… |
| [47] | Medical Student Experiences and Perceptions of ChatGPT and Artificial… (2023) | 2 | 3 | cross-sectional web-based survey | 265 of 325 graduating medical students (81.5% response rate) | The vast majority of respondents denied using ChatGPT in medical school. The study gauges graduating students' experiences and perspectives on ChatGPT and AI i… |
| [63] | AI-induced Deskilling in Medicine: A Mixed-Method Review and Research… (2025) | 2 | 3 | mixed-method review combining systematic review and narrative synthesis |  | The review identifies vulnerabilities in physical examination, differential diagnosis, clinical judgment and communication from AI-driven deskilling in medicin… |
| [30] | The model student: GPT-4 performance on graduate biomedical science e… (2024) | 2 | 3 | benchmark evaluation of GPT-4 on graduate exams (seven blinded) | nine graduate-level biomedical science examinations | GPT-4 scored above the student average in seven of nine exams and above all students on four. It performed poorly on questions with simulated-data figures or h… |
| [31] | ChatGPT versus human essayists: an exploration of the impact of artif… (2024) | 2 | 3 | blinded marking comparison of AI-written vs human essays | AI essays vs first-year undergraduate English essays at Oxf… | AI-written essays averaged 60.46 versus 63.57 for human essays, a non-significant difference (p = 0.10). AI essays tended to describe rather than analyse and l… |
| [64] | Educational Applications of the ChatGPT AI System: A Systematic Revie… (2023) | 2 | 3 | systematic review (number of studies not stated in abstract) |  | The review organizes the literature on ChatGPT in education into positive and negative themes, covering potential implications, possibilities and concerns. The… |
| [32] | Detection of GPT-4 Generated Text in Higher Education: Combining Acad… (2023) | 2 | 3 | experimental detection study with marking by academic staff | 22 ChatGPT-generated submissions marked by 15 academic staf… | Turnitin flagged 91% of the AI-generated submissions as containing AI content, but only 54.8% of the content was identified as AI-generated. Staff reported onl… |
| [57] | Reimagining Higher Education: Navigating the Challenges of Generative… (2025) | 2 | 3 | mixed methods study |  | The study identifies key challenges and interdependencies affecting GenAI adoption in higher education, including academic integrity, critical thinking and rel… |
| [33] | Impact of Generative AI on Critical Thinking Skills in Undergraduates… (2024) | 2 | 3 | systematic literature review of 30 papers | 30 selected papers on generative AI and undergraduate criti… | About half of the 30 reviewed papers suggest generative AI benefits undergraduate critical thinking, while others are inconclusive. Study design limitations pr… |
| [13] | Teacher Education Students’ Practices, Benefits, and Challenges in th… (2026) | 2 | 3 | mixed-methods study (survey plus qualitative data) | 314 undergraduate teacher education students (Early Childho… | Most students use GenAI mainly for academic purposes such as information searching, data analysis, study advice and exam preparation. They reported benefits su… |
| [35] | On the assessment of generative AI in modeling tasks: an experience r… (2023) | 2 | 3 | experience report / exploratory evaluation of ChatGPT on UML modeling tasks |  | ChatGPT's performance on software modeling is limited, with syntactic and semantic deficiencies, inconsistent responses and scalability issues, in contrast to… |
| [48] | Students’ Experiences of Using ChatGPT in an Undergraduate Programmin… (2024) | 2 | 3 | anonymous post-exercise surveys | part-time undergraduate students in a five-week Java course | Most students viewed ChatGPT positively for learning programming, mainly using it for background knowledge, syntax, concepts and algorithm suggestions. Some ab… |
| [65] | ChatGPT and a new academic reality: Artificial Intelligence‐written r… (2023) | 2 | 2 | commentary / conceptual discussion |  | Discusses ChatGPT's potential for automated preparation of scholarly manuscripts and the ethical issues LLMs raise for academics and scholarly publishing. The… |
| [14] | Exploring the Usage of ChatGPT in Higher Education: Frequency and Imp… (2023) | 2 | 2 | qualitative interviews with lecturers | lecturers (number not stated in abstract) | Lecturers reported that ChatGPT helps with finding information, generating ideas, translating and creating alternative questions, and they perceived improved p… |
| [58] | ChatGPT and the rise of generative AI: Threat to academic integrity? (2023) | 2 | 2 | overview/commentary on arguments (no systematic method stated) |  | The paper concludes that ChatGPT and other GenAI could revolutionise academia but, depending on how they are used, could undermine academic integrity. It calls… |
| [59] | Exploring the Potential Impact of Artificial Intelligence (AI) on Int… (2023) | 2 | 2 | research essay (non-systematic conceptual analysis) |  | The essay discusses AI applications (chatbots for learning and research, personalized learning, analytics) for international students, and states these could i… |
| [49] | An overview of the capabilities of ChatGPT for medical writing and it… (2023) | 2 | 2 | brief overview/commentary |  | The article summarizes ChatGPT capabilities for medical writing, lists generative tools and AI text detectors, and offers recommendations on academic integrity… |
| [66] | ChatGPT in higher education: Considerations for academic integrity an… (2023) | 2 | 2 | content analysis of news articles, N=100 | 100 news articles from Australia, New Zealand, the US and t… | Public discussion and university responses to ChatGPT were mixed, focusing mainly on academic integrity concerns and opportunities for innovative assessment de… |
| [60] | The promise and challenges of generative AI in education (2024) | 2 | 2 | expert commentary (nine contributors) |  | The commentary says GenAI can enhance learning design, feedback and assessment, while noting limitations, ethical consequences and potential misuses. It calls… |
| [67] | ChatGPT: Bullshit spewer or the end of traditional assessments in hig… (2023) | 2 | 2 | narrative literature review with experimentation with ChatGPT |  | The article describes ChatGPT's functionality, strengths and limitations, and discusses its implications for assessment in higher education. |
| [68] | Generative AI in Education: Pedagogical, Theoretical, and Methodologi… (2024) | 2 | 2 | special issue editorial summarizing 17 studies |  | The editorial reports that GenAI tools can improve educational outcomes through personalized feedback and support for research methods. It also notes concerns… |
| [69] | ChatGPT: ethical concerns and challenges in academics and research (2023) | 2 | 2 | informal experiments testing ChatGPT accuracy plus ethical discussion |  | ChatGPT's information was inaccurate in tests on research and academic writing, raising concerns about bias, misinformation and plagiarism. The authors call fo… |
| [15] | ChatGPT is a Remarkable Tool—For Experts (2023) | 2 | 2 | narrative review / experimental exploration of ChatGPT capabilities (design unc… |  | ChatGPT can enhance productivity and improve writing style across domains including scientific writing, but it risks incorrect and fictitious responses, code i… |
| [50] | The role of ChatGPT in higher education: Benefits, challenges, and fu… (2023) | 2 | 2 | perspective paper |  | The paper identifies five benefits, including support for research and data analysis, and five challenges, including academic integrity and reliability. It pro… |
| [61] | Generative AI in Higher Education: Balancing Innovation and Integrity (2025) | 2 | 2 | narrative literature review |  | GenAI offers automation and efficiency benefits but poses challenges to academic integrity, equity, bias and the authenticity of student work. The paper argues… |
| [16] | Benefits, limits, and risks of ChatGPT in medicine (2025) | 2 | 2 | narrative review |  | ChatGPT is reported to yield efficiency gains in healthcare (e.g., 70% reduction in administrative time for discharge summaries) and to accelerate research wor… |
| [70] | Fabricated citations: an audit across 2·5 million biomedical papers (2026) | 2 | 2 | audit of references (unclear from abstract) | 2.5 million biomedical papers (per title) | The abstract only states the importance of reference integrity and that non-existent references prevent evaluation of evidence; no results are given. |
| [51] | ChatGPT for Education and Research: Opportunities, Threats, and Strat… (2023) | 2 | 2 | narrative discussion with ChatGPT coding demonstrations (no formal design state… |  | Discusses opportunities (personalized feedback, accessibility) and threats (cheating, reduced critical thinking, difficulty evaluating output) of ChatGPT in ed… |
| [71] | Deskilling dilemma: brain over automation (2026) | 2 | 1 | opinion piece |  | The opinion argues that overreliance on AI may erode independent clinical reasoning and competence in early-career clinicians and residents. It frames deskilli… |
| [52] | The Role of ChatGPT in Data Science: How AI-Assisted Conversational I… (2023) | 2 | 1 | perspective article |  | Argues ChatGPT can assist data scientists with data cleaning, preprocessing, model training and result interpretation, while noting bias and plagiarism concern… |
| [72] | Detecting LLM-generated peer reviews (2025) | 1 | 4 | methodological development of watermarking and statistical detection framework |  | The paper proposes a prompt-injection watermarking scheme with hypothesis tests controlling family-wise error rate to detect LLM-generated peer reviews. It bea… |

</details>

#### rq6 — 대학원 교육에서 생성형 AI를 다룬 연구들은 연구 생산성과 연구 품질을 어떻게 측정하며, 연구 설계와 증거의 질은 어떠한가?

18편 (rel ≥ 3: 4편) · 신뢰도 평균 3.0 · 상위: [3] Human-AI collaboration patterns in AI-assisted academic wri… (2024) (reli 3); [2] Students-Generative AI interaction patterns and its impact… (2025) (reli 3); [6] Generative AI-assisted feedback and EFL writing: a study on… (2025) (reli 3)

<details><summary>전체 표 (18편)</summary>

| # | 문헌 | rel | reli | method | sample | finding |
|---|---|---|---|---|---|---|
| [3] | Human-AI collaboration patterns in AI-assisted academic writing (2024) | 5 | 3 | learning-analytics study of recorded interactions (HMM sequence analysis, clust… | 10 doctoral students, 626 recorded activities | GAI 글쓰기 도구와 반복적이고 상호작용이 활발한 과정을 거친 박사과정생은 대체로 더 나은 글쓰기 수행도를 보였다. 이 연구는 서로 구별되는 인간-AI 협업 패턴을 확인한다. |
| [2] | Students-Generative AI interaction patterns and its impact on academi… (2025) | 5 | 3 | mixed-methods behavioral study using think-aloud protocols, screen recordings,… | 36 Chinese graduate students | AI 리터러시(AI literacy)가 높은 대학원생은 GenAI 글쓰기 시스템과 상호작용할 때 협업적 패턴을 보였으며, 확인된 상호작용 패턴들은 학술 글쓰기 수행도를 기준으로 비교되었다. AI 리터러시는 학생이 GenAI와 상호작용하는 방식을 형성하였다. |
| [6] | Generative AI-assisted feedback and EFL writing: a study on proficien… (2025) | 4 | 3 | randomized controlled study with pre/post tests plus semi-structured interviews… | 60 postgraduate EFL students, randomly assigned to experime… | Grammarly AI 피드백 집단은 사후 글쓰기 검사에서 통제집단보다 유의하게 높은 점수를 받았다. AI 기능의 사용은 더 많은 수정, 그리고 내용·구성·응집성의 향상과 상관이 있었다. |
| [41] | Combining human and artificial intelligence for enhanced AI literacy… (2024) | 3 | 3 | convergent mixed-methods case study, n=37 | 37 graduate students in three 8-week courses in a College o… | Participants appeared to feel more comfortable using GenAI tools after the course experience. The study examines how a GenAI reviewer tool and image generators… |
| [25] | Writing without borders: AI and cross-cultural convergence in academi… (2025) | 2 | 4 | large-scale bibliometric/readability analysis with mixed GLM and lexical tracki… | over one million English-language social science abstracts… | Writing complexity (readability) improved globally, with non-native English-speaking countries showing notable advances, and China surpassing traditional leade… |
| [27] | Can ChatGPT support prospective teachers in physics task development? (2023) | 2 | 4 | RCT n=26 | 26 prospective physics teacher students | Students using ChatGPT showed no difference in task correctness compared with a textbook group, but the textbook group achieved higher clarity and more often e… |
| [73] | Integrating ChatGPT in Orthopedic Education for Medical Undergraduate… (2024) | 2 | 4 | RCT n=129 plus ChatGPT accuracy evaluation on MCQs | 129 undergraduate medical students | Evaluated ChatGPT's accuracy on orthopedics MCQs and tested its effect as a learning aid over a 2-week intervention, with follow-up on end-of-semester performa… |
| [12] | Generative AI and the Automating of Academia (2023) | 2 | 3 | survey n=284 with critical analysis | 284 UK academics | Based on a survey of UK academics' GAI use, the paper argues that GAI is framed as relief from overwork in academia. The abstract is truncated before the findi… |
| [28] | Mastering knowledge: the impact of generative AI on student learning… (2025) | 2 | 3 | quasi-experimental qualitative analysis with quantitative content analysis of s… | 192 student reflections in higher education | Students who used GenAI to construct and augment knowledge (mastery approach) achieved higher-level learning than those who used it procedurally. The authors s… |
| [45] | What Is the Impact of ChatGPT on Education? A Rapid Review of the Lit… (2023) | 2 | 3 | rapid review of 50 articles with content analysis | 50 articles published Dec 2022 to Feb 2023 | ChatGPT performance varied across subject domains, from outstanding in economics to unsatisfactory in mathematics. It could assist instructors and students but… |
| [46] | Drivers of generative AI adoption in higher education through the len… (2024) | 2 | 3 | cross-sectional online questionnaire with PLS-SEM (Theory of Planned Behaviour) | 130 lecturers and 168 students in higher education institut… | Perceived strengths of GenAI positively affected attitudes, subjective norms and perceived behavioural control, which positively influenced intention to use an… |
| [74] | A Systematic Review of Generative AI for Teaching and Learning Practi… (2024) | 2 | 3 | systematic bibliometric-style review (PRISMA) of Scopus-indexed studies | 625 papers retrieved, 355 included | The review maps the state of GenAI research in higher education teaching and learning, covering document trends, sources and keywords. It identifies gaps in AI… |
| [64] | Educational Applications of the ChatGPT AI System: A Systematic Revie… (2023) | 2 | 3 | systematic review (number of studies not stated in abstract) |  | The review organizes the literature on ChatGPT in education into positive and negative themes, covering potential implications, possibilities and concerns. The… |
| [34] | Mathematical Capabilities of ChatGPT (2023) | 2 | 3 | benchmark evaluation of LLMs on new datasets (GHOSTS, miniGHOSTS) curated by ma… | Graduate-level mathematics datasets; ChatGPT (two versions)… | Benchmarks ChatGPT and GPT-4 on graduate-level natural-language mathematics with fine-grained metrics and tests whether they can serve as helpful assistants to… |
| [75] | A Bibliometric Analysis of the Rise of ChatGPT in Medical Research (2023) | 2 | 3 | bibliometric analysis of 267 articles (PubMed, Embase, Scopus, Web of Science) | 267 ChatGPT articles in the medical field | Most ChatGPT articles in medicine were editorials or correspondence, averaging 7.5 +/- 18.4 citations, and came mainly from the US, India, and China. Topics in… |
| [60] | The promise and challenges of generative AI in education (2024) | 2 | 2 | expert commentary (nine contributors) |  | The commentary says GenAI can enhance learning design, feedback and assessment, while noting limitations, ethical consequences and potential misuses. It calls… |
| [76] | A systematic review of ChatGPT use in K‐12 education (2023) | 1 | 3 | systematic review (PRISMA) of 13 papers with SWOT analysis | 13 papers on K-12 education | ChatGPT could support lesson planning, material generation and personalised learning in K-12 settings, but academic integrity and output quality concerns need… |
| [77] | Challenges and Opportunities of Generative AI for Higher Education as… (2023) | 1 | 1 | thing ethnography using ChatGPT's own output (qualitative) |  | ChatGPT's self-generated account lists challenges and opportunities for higher education, including academic integrity, plagiarism detection and critical think… |

</details>

#### 평가했으나 어느 sub-RQ 에도 배정되지 않은 문헌 (21편, 대부분 관련성 ≤ 1)

Evaluator 가 읽고 관련성이 낮다고 판정한 문헌. 종합·Gap 에 쓰이지 않아 참고문헌 번호를 받지 않으며, 평가 기록으로만 남긴다.

<details><summary>전체 표 (21편)</summary>

| id | 문헌 | rel | reli | method | sample | finding |
|---|---|---|---|---|---|---|
| 10.1038/s42256-024-00832-8 | Augmenting large language models with chemistry tools (2024) | 1 | 4 | tool development and evaluation (LLM agent with LLM and expert assessment) |  | ChemCrow, a GPT-4 agent with 18 expert-designed tools, performed chemistry tasks such as planning and executing syntheses. It is a technical system paper and d… |
| 10.48550/arxiv.2308.10620 | Large Language Models for Software Engineering: A Systematic Literatu… (2023) | 1 | 4 | systematic literature review of 395 papers | 395 research papers (2017-2024) | Categorizes LLMs, data methods, optimization and evaluation strategies, and successful tasks in software engineering. It does not address graduate student rese… |
| 10.1007/s12525-024-00707-1 | AI Literacy for the top management: An upper echelons perspective on… (2024) | 1 | 4 | observational study with firm-level and LinkedIn data | 6986 executives | Top management team AI literacy positively affects firm AI orientation and AI implementation ability, with AI orientation mediating the effect. The effect on i… |
| 10.3390/bioengineering12060631 | Large Language Models in Healthcare and Medical Applications: A Review (2025) | 1 | 3 | review of LLMs in healthcare (described as systematic, details unclear) |  | Reviews LLM applications and challenges in healthcare, including privacy, ethics and factual accuracy. It is off-topic for graduate research productivity. |
| 10.1101/2022.12.19.22283643 | Performance of ChatGPT on USMLE: Potential for AI-Assisted Medical Ed… (2022) | 1 | 3 | benchmark evaluation of ChatGPT on USMLE exams (preprint) |  | ChatGPT performed at or near the passing threshold on all three USMLE exams without specialized training. It showed high concordance and insight in its explana… |
| 10.1186/s40359-025-02757-2 | Mediating effect of AI attitudes and AI literacy on the relationship… (2025) | 1 | 3 | cross-sectional survey with structural equation modeling | 455 Chinese college students | Career self-efficacy reduces job-seeking anxiety, with AI attitudes and AI literacy mediating this relationship. |
| 10.1109/access.2025.3533217 | Exploring LLMs Applications in Law: A Literature Review on Current Le… (2025) | 1 | 3 | systematic literature review of 61 publications (database search and snowballin… | 61 publications on LLMs in legal NLP, 2017-2023 | Literature on LLMs in the legal domain grew and diversified across tasks such as document analysis, case prediction and contract review. Methodological sophist… |
| 10.1016/j.ssci.2023.106244 | The risks of using ChatGPT to obtain common safety-related informatio… (2023) | 1 | 3 | expert panel case analysis of 9 safety cases | 9 cases across safety domains, multidisciplinary expert con… | Experts concluded ChatGPT (3.5) posed potentially significant risks as a source of safety-related advice, providing incorrect or potentially harmful informatio… |
| 10.3390/su151814025 | Generative AI and ChatGPT in School Children’s Education: Evidence fr… (2023) | 1 | 3 | classroom intervention study with test lessons | 110 pupils aged 8–14 in 4 classes at two schools | ChatGPT-3.5 could personalize learning material to pupils' levels, and a clear majority of pupils enjoyed the AI-modified material. |
| 10.36227/techrxiv.23589741.v1 | A Survey on Large Language Models: Applications, Challenges, Limitati… (2023) | 1 | 2 | narrative survey of LLMs (no stated method) |  | Gives a general overview of LLM history, architecture, applications and challenges. It does not address graduate research productivity or quality. |
| 10.1007/s43621-025-00815-8 | A comprehensive review of large language models: issues and solutions… (2025) | 1 | 2 | narrative review with proposed theoretical framework and case studies (method u… |  | The paper reviews LLM types, history, training, and educational applications, and proposes a framework for integrating LLMs into education addressing personali… |
| 10.3390/fi15060192 | ChatGPT and Open-AI Models: A Preliminary Review (2023) | 1 | 2 | preliminary narrative literature review |  | The article gives an overview of ChatGPT's training and functionality and a preliminary review of the literature, discussing its implications and challenges. I… |
| 10.3390/su16073034 | Generative AI for Customizable Learning Experiences (2024) | 1 | 2 | tool development / design description (unclear evaluation design from abstract) |  | The authors built an LLM-based tool inside a learning management system at a software engineering college that generates personalized learning materials in thr… |
| 10.7759/cureus.38317 | ChatGPT in Dentistry: A Comprehensive Review (2023) | 1 | 2 | comprehensive narrative review of 66 articles | 66 articles from PubMed and Google Scholar | The review discusses ChatGPT applications in dentistry, including a role in scientific research, and notes risks and limitations of the chatbot. |
| 10.1007/s12599-023-00834-7 | Generative AI (2023) | 1 | 2 | commentary / conceptual editorial |  | The abstract introduces generative AI as capable of producing creative content indistinguishable from human work. It reports no empirical findings on graduate… |
| 10.3389/fpsyg.2024.1269319 | Exploring the potential of ChatGPT for foreign language education at… (2024) | 1 | 2 | qualitative questionnaire survey | university students (size not stated in abstract) | Students were fascinated and satisfied with ChatGPT for foreign language learning despite reservations; teachers and students need to upskill to handle AI. |
| 10.1017/dsj.2024.8 | Challenges in applying large language models to requirements engineer… (2024) | 1 | 2 | narrative literature review of LLM applications to requirements engineering tas… |  | The review surveys how LLMs have been applied to engineering requirements tasks and identifies shared challenges across them. It suggests drawing on how other… |
| 10.1371/journal.pone.0291229 | Determinants and outcomes of eHealth literacy in healthy adults: A sy… (2023) | 0 | 4 | systematic review (JBI critical appraisal, six databases) |  | The review examines determinants and outcomes of eHealth literacy in healthy adults. It is unrelated to generative AI or graduate research. |
| 10.1109/access.2026.3698694 | From LLM Reasoning to Autonomous AI Agents: A Comprehensive Review (2026) | 0 | 3 | comprehensive review and taxonomy of about 60 benchmarks and agent frameworks |  | The paper consolidates LLM and AI-agent benchmarks (2019-2025) into a taxonomy and reviews agent frameworks and applications. It does not address graduate stud… |
| 10.1007/s43681-024-00425-6 | Formalizing ethical principles within AI systems: experts’ opinions o… (2024) | 0 | 3 | expert interviews n=12 | 12 experts from philosophy, AI and cognitive sciences | Experts' arguments for and against computational ethics cluster into pragmatic, societal and epistemic reasons. The study is unrelated to graduate student use… |
| 10.48550/arxiv.2407.00215 | LLM Critics Help Catch LLM Bugs (2024) | 0 | 3 | LLM critic model training with human evaluation (RLHF) |  | LLM critics trained with RLHF catch more bugs in model-written code than paid human contractors, though they can hallucinate bugs; human-machine teams hallucin… |

</details>

## 4. 종합

### 합의

- 학생들은 GenAI를 주로 글쓰기 및 아이디어 구상 지원, 정보 검색, 바꿔쓰기와 개념 설명에 사용한다고 보고하지만, 이러한 사용 비율 수치는 대학원생 특정 표본이 아니라 일반 또는 혼합 학생 집단에서 나온 것이다. [37, 38, 39] (근거 3편 · 신뢰도 평균 4.0)

- 대학원생과 석·박사과정생은 GenAI가 더 빠른 진행을 포함하여 연구와 학위논문 작성에 유용하다고 인식하지만, 이는 소규모 표본의 자기보고 인식이며 이들 연구 중 어느 것도 절감된 시간, 글쓰기 속도 또는 출판 산출량을 측정하지 않는다. [1, 4, 5, 9] (근거 4편 · 신뢰도 평균 3.0)

- LLM이 생성한 참고문헌은 신뢰할 수 없다. 상당수가 조작되었거나 부정확하며, 특히 DOI 정확도가 매우 낮다. 이 검사들은 대학원생 표본이 아니라 LLM 출력물을 사용하였고, 대부분 구형 모델이었다. [18, 40, 54] (근거 3편 · 신뢰도 평균 3.7)

- 설문, 문헌고찰, 논평은 정확성, 환각(hallucination), 진실성, 과의존에 대한 우려를 제기하고 인간의 판단을 중심에 둘 것을 권고하지만, 이는 대체로 신뢰도가 낮은 서술적 문헌고찰(narrative review)과 인식 자료에 근거한다. [10, 23, 24, 37, 42] (근거 5편 · 신뢰도 평균 2.4)

- 조심스럽게 말하면, AI로 보강된 글은 더 잘 읽히지만 연구의 깊이가 부족할 수 있다. 검토자들은 가독성과 정보성에서는 더 높게 평가했으나 연구 세부 내용과 성찰적 통찰이 부족하다고 보았으며, AI 리뷰는 동료 심사보다 약간 낮게 평가되었다. 표본은 작고(HCI 검토자 17명, 상세 미상의 대학원 과정) 대학원 연구 글쓰기에 특화된 것도 아니다. [20, 21] (근거 2편 · 신뢰도 평균 3.0)

### 상충

- **AI 출력물에 대한 비판적 평가가 성과에 도움이 되는지 해가 되는지 여부** (A 1편 vs B 3편)
  - A: AI에 대한 비판적 평가는 대학생의 AI 자기효능감(self-efficacy)과 AI 출력 품질에 유의한 부정적 영향을 미쳤다. [17]
  - B: 대학원생에 대한 질적 연구는 비판적 평가와 피드백 추구를 책임 있고 유익한 사용과 더 나은 글쓰기의 핵심으로 서술한다. [1, 5, 7]
  - 원인 가설: 설문은 인식된 출력 품질과 자기효능감을 측정하므로 학생이 출력물을 면밀히 검토할 때 이 값이 떨어질 수 있는 반면, 질적 연구는 평가되거나 성찰된 글쓰기 품질과 책임 있는 사용을 다룬다. 표본도 다르다. 횡단 구조방정식모형(SEM)의 일반 오스트리아 대학생 대 연구 글쓰기를 성찰하는 대학원생 또는 박사과정생이다.

- **학술 글쓰기에서 ChatGPT의 이점이 어려움보다 큰지 여부** (A 1편 vs B 1편)
  - A: ChatGPT를 지속적으로 사용한 연구 학생들은 진행 가속, 더 높은 품질, 더 큰 자신감을 보고하였다. [5]
  - B: 영어 전공 대학원생은 과의존과 글쓰기의 어려움을 포함한 어려움이 이점보다 크다고 보고하였다. [10]
  - 원인 가설: 첫 번째 집단은 최소 4개월의 연구 사용 경험이 있었고 숙련 사용자로 자기선택되었던 반면, 두 번째 집단은 자신의 전공 분야로 글을 쓰는 영어 전공자여서 언어 품질 향상의 중요성이 더 낮다. 둘 다 소규모 자기보고 표본에 의존하며, 두 번째는 신뢰도가 더 낮다.

### 조건부

- GenAI를 활용한 더 나은 글쓰기 수행은 반복적이고 상호작용이 활발한 협업적 사용, 그리고 높은 AI 리터러시와 비판적 참여와 관련이 있다. 다만 이는 소규모 단일 과제 연구이며 인과가 아닌 연관이다. [2, 3, 7, 8] (근거 4편 · 신뢰도 평균 3.0)

- 무작위 시험(randomized trial)에서 AI 피드백이나 ChatGPT 지원 수업에 따른 글쓰기 향상은 구조화된 수업을 받은 EFL 학습자에게서만 나타났으며, 그중 하나는 Grammarly 기반 도구를 사용하였다. 결과 변수는 연구 산출물이 아니라 글쓰기 숙련도이다. [6, 19] (근거 2편 · 신뢰도 평균 3.0)

- LLM은 비영어권 연구자가 공개를 전제로 편집과 다듬기에 사용하고 많은 분량의 텍스트를 생성하는 데 쓰지 않는다면 영어 학술 글쓰기의 장벽을 낮춘다고 하나, 이는 실증 자료가 없는 논평이다. [42] (근거 1편 · 신뢰도 평균 2.0)

- ChatGPT의 인용 정확도는 학문 분야에 따라 달라진다. DOI 정확도는 인문학(8.5%)이 자연과학(32.7%)보다 훨씬 낮았으나, 10개 주제에서 GPT-3.5만 검사되었다. [54] (근거 1편 · 신뢰도 평균 3.0)

### 커버리지 메모

rq1(생산성)은 사실상 답이 없다. 표에 있는 어떤 논문도 글쓰기 속도, 과제 수행 시간 또는 출판 산출량을 측정하지 않으며, 증거는 자기보고 인식과 n=1의 학부생 자문화기술지(autoethnography) 하나뿐이므로 생산성 주장은 검증되지 않은 것으로 다뤄야 한다. rq3의 사용 비율은 규모는 크지만 일반 학생 대상의 설문에 근거하며, 대학원생 특정 증거는 소규모 질적 연구에 한정되고, 코딩, 통계 분석 또는 데이터 분석 사용을 다룬 논문이 없으므로 이 공백은 미사용의 증거가 아니라 표에 없음을 반영한다. rq2와 rq4는 중간 정도이나 소규모 표본의 증거이며 대부분 질적 연구 또는 단일 과제 행동 연구이고, EFL 환경의 소규모 RCT가 두 건 있다. rq5는 학생이 관여하지 않은 LLM 출력 검사를 통한 인용 환각에서 가장 강하고, 진실성 위반과 기술 쇠퇴에서는 더 빈약하다. rq6에서 측정은 대부분 인식 또는 단일 과제 평가 글쓰기이다. 시간, 산출량, 출판, 전문가 평가 품질을 장기간 측정하는 대학원생 대상의 통제 연구 또는 로그 기반 연구, 그리고 코딩과 데이터 분석에 관한 설문이나 실험이 빠져 있다.

## 5. Research Gap

### G1. 표에 있는 어떤 연구도 과제 수행 시간, 글쓰기 속도, 산출량 또는 출판 건수와 같은 대학원생의 연구 생산성을 측정하지 않는다.

[4, 5, 9, 11] (근거 4편 · 신뢰도 평균 2.8)

생산성 주장은 소규모 질적 또는 설문 표본의 자기보고 인식에 근거한다. 문서화된 유일한 사용 흔적은 n=1의 학부생 자문화기술지이며, 이는 대학원 수준의 주장을 뒷받침할 수 없다.

- 제안 RQ: 범용 생성형 AI 어시스턴트를 이용할 수 있는 것이 이용할 수 없는 경우에 비해 대학원생의 과제 수행 시간과 원고 또는 학위논문 장(章)의 산출량을 바꾸는가?
- 방법: 한 학기 동안 2개 집단(GenAI 이용 대 비이용)으로 사전등록한 RCT로, 기록된 글쓰기 시간과 주당 초고 단어 수를 1차 결과로, 장 또는 원고 제출을 2차 결과로 한다. 생산적 사용과 유휴 사용을 구분하기 위해 키 입력 및 채팅 기록을 추가한다.
- 데이터: 2-3개 대학 대학원을 통해 모집한 석사 및 박사과정생 약 120명으로, 글쓰기 도구 로그와 지도교수가 확인한 단계별 이력 기록을 사용한다. 학문 분야와 영어 사용 여부에 따라 층화한다.

### G2. 연구 품질은 인식 또는 단일 과제 평가 글쓰기를 통해서만 측정되었고, 연구 자체(독창성, 엄밀성, 논증의 깊이)에 대한 전문가 판단으로는 측정된 적이 없다.

[2, 5, 20, 21] (근거 4편 · 신뢰도 평균 3.0)

증거에 따르면 AI로 보강된 글은 더 잘 읽히지만 연구 세부 내용과 성찰적 통찰이 부족한 반면, 대학원생은 더 높은 품질을 인식한다. 이 두 신호는 대학원생 작업에 대한 눈가림 전문가 평가로 서로 검증된 적이 없다.

- 제안 RQ: 눈가림 전문가 평가자는 GenAI로 작성한 대학원 연구 초고를 AI 없이 작성한 초고보다 엄밀성, 독창성, 논증의 깊이에서 더 높게 판단하는가, 그리고 이것이 학생 자신의 품질 평가와 일치하는가?
- 방법: 각 학생이 비슷한 두 개의 문헌 검토 또는 방법 부분을 쓰되 하나는 GenAI를 사용하고 하나는 사용하지 않는 무작위 교차 설계(crossover design)로, 눈가림한 평가자가 타당화된 평가 기준표로 채점한다. 전문가 점수와 학생 자기평가를 비교하여 인식과 실제 사이의 격차를 추정한다.
- 데이터: 연구방법론 과정 또는 글쓰기 프로그램의 대학원생 약 60명과 교수 평가자 6-10명으로, 평가 기준표 점수와 채팅 기록을 사용한다.

### G3. AI 출력물에 대한 비판적 평가가 도움이 되는지 해가 되는지에 대해 증거가 상충한다.

[1, 2, 7, 17] (근거 4편 · 신뢰도 평균 3.2)

일반 학생 설문은 이것이 자기효능감과 인식된 출력 품질을 낮춘다고 밝히는 반면, 대학원생과 박사과정생의 질적 연구는 비판적 평가를 좋은 글쓰기의 핵심으로 제시한다. 설문은 인식된 결과를 다룬 횡단 연구이고 질적 연구는 객관적 품질 비교가 없으므로 이 상충은 해소되지 않았다.

- 제안 RQ: 대학원생에게 AI 출력물의 비판적 평가를 교육하면 AI 자기효능감을 낮추거나 유지하면서 전문가가 평가한 글쓰기 품질이 향상되는가?
- 방법: 연구 글쓰기 과제에 앞서 비판적 평가 및 검증 교육 모듈과 기본 도구 사용 모듈을 비교하는 2개 집단 무작위 실험이다. 1차 결과는 눈가림 전문가 평가 품질이며, 자기효능감과 인식된 출력 품질은 둘이 괴리되는지 검증하기 위한 2차 결과이다.
- 데이터: 대학원을 통해 모집한 여러 학문 분야의 대학원생 약 100명으로, 사전/사후 자기효능감 척도와 평가된 글쓰기 표본을 사용한다.

### G4. 인용 조작은 구형 모델(GPT-3.5, Bard) 또는 좁은 주제를 사용한 LLM 출력 검사에서만 입증되었고, 대학원생이 실제로 제출하는 결과물에서는 입증된 적이 없다.

[4, 18, 40, 54] (근거 4편 · 신뢰도 평균 3.5)

학생이 조작된 참고문헌을 걸러내는지, 학문 분야에 따른 오류율이 현재 모델에도 이어지는지, 조작이 학위논문이나 원고의 품질에 영향을 미치는지는 알려져 있지 않다.

- 제안 RQ: 대학원생의 GenAI 지원 문헌 검토에서 조작되었거나 부정확한 참고문헌 중 학생의 검증을 통과해 남는 비율은 얼마이며, 이는 학문 분야와 모델 버전에 따라 어떻게 다른가?
- 방법: 학생들이 최신 LLM으로 문헌 검토를 작성하고, 학생의 확인 전후에 모든 인용을 데이터베이스와 대조해 검증하는 감사 연구(audit study)이다. 학문 분야 간, 그리고 검증 교육을 받은 학생과 받지 않은 학생 간에 오류 잔존율을 비교한다.
- 데이터: 인문학, 사회과학, 자연과학 프로그램의 대학원생 약 80명으로, 초고, 채팅 기록, Crossref와 Scopus 같은 서지 데이터베이스를 사용한다.

### G5. 대규모 설문이 일반 또는 혼합 학생 집단을 표본으로 하므로 대학원생 특정 사용 비율과 과제 양상은 알려져 있지 않다.

[37, 38, 39] (근거 3편 · 신뢰도 평균 4.0)

표에 있는 어떤 연구도 대학원생의 코딩, 통계 분석 또는 데이터 분석을 위한 LLM 사용을 다루지 않아, 연구 생산성과 품질의 데이터 분석 측면은 검토되지 않은 상태이다.

- 제안 RQ: 석사 및 박사과정생 중 코딩, 통계 분석, 데이터 해석에 GenAI를 사용하는 비율은 얼마이며, 그 사용은 분석 오류와 인식된 의존도와 어떤 관련이 있는가?
- 방법: 대학원생 대상의 층화 횡단 설문과, 하위 표본이 표준 분석을 GenAI를 사용하거나 사용하지 않고 수행하여 오류를 기준 해답과 대조해 채점하는 후속 과제로 구성한다. 학문 분야와 경력 단계에 따라 사용 양상을 비교한다.
- 데이터: 여러 대학 또는 국가 박사과정 네트워크의 대학원생 약 1,000명에 대한 설문과, 분석 과제를 위한 학생 약 60명.

## 6. 향후 연구 방향

§5 의 제안을 한 표로 요약했다 (전문은 각 Gap). 근거는 해당 Gap 의 인용을 따른다.

| # | 제안 RQ | 연구 설계 | 데이터 | 근거 Gap |
|---|---|---|---|---|
| 1 | 범용 생성형 AI 어시스턴트를 이용할 수 있는 것이 이용할 수 없는 경우에 비해 대학원생의 과제 수행 시간과 원고 또는 학위논문 장(章)의 산출량을 바꾸는가? | 한 학기 동안 2개 집단(GenAI 이용 대 비이용)으로 사전등록한 RCT로, 기록된 글쓰기 시간과 주당 초고 단어 수를 1차 결과로, 장 또는 원고 제출을 2차 결과로 한다.… | 2-3개 대학 대학원을 통해 모집한 석사 및 박사과정생 약 120명으로, 글쓰기 도구 로그와 지도교수가 확인한 단계별 이력 기록을 사용한다.… | G1 [4, 5, 9, 11] |
| 2 | 눈가림 전문가 평가자는 GenAI로 작성한 대학원 연구 초고를 AI 없이 작성한 초고보다 엄밀성, 독창성, 논증의 깊이에서 더 높게 판단하는가, 그리고 이것이 학생 자신의 품질 평가와 일치하는가? | 각 학생이 비슷한 두 개의 문헌 검토 또는 방법 부분을 쓰되 하나는 GenAI를 사용하고 하나는 사용하지 않는 무작위 교차 설계(crossover design)로, 눈가림한 평가… | 연구방법론 과정 또는 글쓰기 프로그램의 대학원생 약 60명과 교수 평가자 6-10명으로, 평가 기준표 점수와 채팅 기록을 사용한다. | G2 [2, 5, 20, 21] |
| 3 | 대학원생에게 AI 출력물의 비판적 평가를 교육하면 AI 자기효능감을 낮추거나 유지하면서 전문가가 평가한 글쓰기 품질이 향상되는가? | 연구 글쓰기 과제에 앞서 비판적 평가 및 검증 교육 모듈과 기본 도구 사용 모듈을 비교하는 2개 집단 무작위 실험이다. 1차 결과는 눈가림 전문가 평가 품질이며, 자기효능감과 인… | 대학원을 통해 모집한 여러 학문 분야의 대학원생 약 100명으로, 사전/사후 자기효능감 척도와 평가된 글쓰기 표본을 사용한다. | G3 [1, 2, 7, 17] |
| 4 | 대학원생의 GenAI 지원 문헌 검토에서 조작되었거나 부정확한 참고문헌 중 학생의 검증을 통과해 남는 비율은 얼마이며, 이는 학문 분야와 모델 버전에 따라 어떻게 다른가? | 학생들이 최신 LLM으로 문헌 검토를 작성하고, 학생의 확인 전후에 모든 인용을 데이터베이스와 대조해 검증하는 감사 연구(audit study)이다. 학문 분야 간, 그리고 검증… | 인문학, 사회과학, 자연과학 프로그램의 대학원생 약 80명으로, 초고, 채팅 기록, Crossref와 Scopus 같은 서지 데이터베이스를 사… | G4 [4, 18, 40, 54] |
| 5 | 석사 및 박사과정생 중 코딩, 통계 분석, 데이터 해석에 GenAI를 사용하는 비율은 얼마이며, 그 사용은 분석 오류와 인식된 의존도와 어떤 관련이 있는가? | 대학원생 대상의 층화 횡단 설문과, 하위 표본이 표준 분석을 GenAI를 사용하거나 사용하지 않고 수행하여 오류를 기준 해답과 대조해 채점하는 후속 과제로 구성한다. 학문 분야와… | 여러 대학 또는 국가 박사과정 네트워크의 대학원생 약 1,000명에 대한 설문과, 분석 과제를 위한 학생 약 60명. | G5 [37, 38, 39] |

## 7. 한계와 신뢰도

- 초록과 메타데이터만 읽었고 전문은 읽지 않았으므로 효과 크기, 상호작용 패턴 결과, 조작률 수치 같은 세부 사항은 검증할 수 없었으며, 일부 초록(예: [18], [40])은 추출할 수 있는 수치를 제공하지 않는다.

- 검색은 제한된 기간 내에서 OpenAlex와 arXiv만 대상으로 했고 후보 524건 중 98건이 평가되었으므로, 다른 데이터베이스나 색인되지 않은 학술지의 관련 연구가 누락되었을 수 있다.

- rq1(생산성)은 사실상 답이 없다. 어떤 논문도 과제 수행 시간, 글쓰기 속도 또는 출판 산출량을 측정하지 않으며, 유일한 신호는 자기보고와 n=1의 학부생 자문화기술지뿐이다. 이는 두 차례의 재계획 후에도 주요 품질 관문(quality-gate) 결과로 지적되었으며 해결되지 않은 채 남았다.

- 증거의 상당 부분은 신뢰도가 낮고(서술적 문헌고찰, 논평, 인식 설문) 대학원생 특정 연구 표본이 아니라 일반 또는 혼합 학생 집단이나 EFL 환경에서 나온 것이며, 두 RCT는 연구 산출물이 아니라 글쓰기 숙련도를 측정한다.

- 진실성 위반, 과의존, 기술 쇠퇴(rq5)에 관한 증거는 빈약하고 대학원생 특정 자료는 없으며, 코딩, 통계 분석 또는 문헌 검색 작업 흐름을 다룬 논문이 없으므로 이 공백은 미사용의 증거가 아니라 표에 없음을 반영한다.

- 일부 종합 주장은 근거가 약하다. AI 리터러시와 수행도의 연결 및 비판적 평가의 상충은 비교할 수 없는 구성개념을 비교하고, 인용 조작률은 GPT-3.5 연구 하나에 근거하며, AI 대 동료 심사 결과는 대학원생 자신의 연구 품질과는 거리가 있다.

**품질 게이트가 자동으로 기록한 미해결 항목** (사람이 쓴 것이 아니라 파이프라인 검사 결과다):

- Critic 미해결 — major issue(s) persist after re-search, recorded as limitation: rq1: rq1 is effectively unanswered: no paper in the table measures writing speed, time-on-task or publication output. The only productivity signals are self-reports ([5], [4], [9]) and an n=1 undergraduate autoethnography [11].
## 품질 한눈에

| 검색 후보 | 평가 문헌 | 실존 검증 (DOI/arXiv) | sub-RQ 커버리지 (근거 ≥ 3편) | 출처 있는 claim | 근거 ≥ 2편인 Gap | Critic 판정 / Replan | 품질 게이트 미해결 | 비용 · 시간 |
|---|---|---|---|---|---|---|---|---|
| 524 | 98 | 98/98 (100%) | 6/6 | 13/13 | 5/5 | 3회 / 2회 | 1건 → §7 | $0.81 · 7.3분 |

LLM 없이 코드가 계산한 결정적 지표다 (`cost.json` `checks`). 인용 번호 [n] 은 바로 아래 참고문헌을 가리킨다.


## 참고문헌 (77편)

본문·표에 번호로 인용된 문헌. 모두 검색 도구(OpenAlex·arXiv·Crossref)가 반환한 메타데이터 그대로이며 DOI/arXiv id 로 실존이 확인됐다.

1. Soroush Sabbaghan, Sarah Elaine Eaton (2025). Navigating the Ethical Frontier: Graduate Students’ Experiences with Generative AI-Mediated Scholarship. *International Journal of Artificial Intelligence in Education*. https://doi.org/10.1007/s40593-024-00454-6
2. Jinhee Kim, Sang-Soog Lee, Rita Detrick et al. (2025). Students-Generative AI interaction patterns and its impact on academic writing. *Journal of Computing in Higher Education*. https://doi.org/10.1007/s12528-025-09444-6
3. Andy Nguyen, Yvonne Hong, Belle Dang et al. (2024). Human-AI collaboration patterns in AI-assisted academic writing. *Studies in Higher Education*. https://doi.org/10.1080/03075079.2024.2323593
4. Luqman Mahmoud Rababah, Mahmoud Ali Rababah, Nisreen Al-Khawaldeh (2024). Graduate Students' ChatGPT Experience and Perspectives during Thesis Writing. *International Journal of Engineering Pedagogy (iJEP)*. https://doi.org/10.3991/ijep.v14i3.48395
5. Yun Dai, Sichen Lai, Cher Ping Lim et al. (2023). ChatGPT and its impact on research supervision: Insights from Australian postgraduate research students. *Australasian Journal of Educational Technology*. https://doi.org/10.14742/ajet.8843
6. Mohamed Amin Abdel Gawad Mekheimer (2025). Generative AI-assisted feedback and EFL writing: a study on proficiency, revision frequency and writing quality. *Discover Education*. https://doi.org/10.1007/s44217-025-00602-7
7. Baraa Khuder (2025). Enhancing disciplinary voice through feedback-seeking in AI-assisted doctoral writing for publication. *Applied Linguistics*. https://doi.org/10.1093/applin/amaf022
8. Yuan Yao, Yiwen Sun, Siyu Zhu et al. (2024). A Qualitative Inquiry Into Metacognitive Strategies of Postgraduate Students in Employing ChatGPT for English Academic Writing. *European Journal of Education*. https://doi.org/10.1111/ejed.12824
9. Thulani Andrew Chauke, Themba Ralph Mkhize, Lina Mmakgabo Methi et al. (2024). Postgraduate Students’ Perceptions on the Benefits Associated with Artificial Intelligence Tools on Academic Success: In Case of ChatGPT AI tool. *Journal of Curriculum Studies Research*. https://doi.org/10.46303/jcsr.2024.4
10. Thi Yen Phuong Nguyen, Ngoc T.M. Nguyen, Nguyen Khanh Hoa Phan (2025). The Challenges of Applying ChatGPT in the Academic Writing of Postgraduate Students in English Major at IUH. *International journal of AI in language education.*. https://doi.org/10.54855/ijaile.25212
11. Nicolas Schwenke, Heinrich Söbke, Eckhard Kraft (2023). Potentials and Challenges of Chatbot-Supported Thesis Writing: An Autoethnography. *Trends in Higher Education*. https://doi.org/10.3390/higheredu2040037
12. Richard Watermeyer, Lawrie Phipps, Donna Lanclos et al. (2023). Generative AI and the Automating of Academia. *Postdigital Science and Education*. https://doi.org/10.1007/s42438-023-00440-6
13. Stavros Athanassopoulos, Aggeliki Tzavara, Spyridon Aravantinos et al. (2026). Teacher Education Students’ Practices, Benefits, and Challenges in the Use of Generative AI Tools in Higher Education. *Education Sciences*. https://doi.org/10.3390/educsci16020228
14. Radha Firaina, Dwi Sulisworo (2023). Exploring the Usage of ChatGPT in Higher Education: Frequency and Impact on Productivity. *Buletin Edukasi Indonesia*. https://doi.org/10.56741/bei.v2i01.310
15. Amos Azaria, Rina Azoulay, Shulamit Reches (2023). ChatGPT is a Remarkable Tool—For Experts. *Data Intelligence*. https://doi.org/10.1162/dint_a_00235
16. Jonathan Alan Tangsrivimol, Erfan Darzidehkalani, Hafeez Ul Hassan Virk et al. (2025). Benefits, limits, and risks of ChatGPT in medicine. *Frontiers in Artificial Intelligence*. https://doi.org/10.3389/frai.2025.1518049
17. Senad Bećirović, Edda Polz, Isabella Tinkel (2025). Exploring students’ AI literacy and its effects on their AI output quality, self-efficacy, and academic performance. *Smart Learning Environments*. https://doi.org/10.1186/s40561-025-00384-3
18. Mikaël Chelli, Jules Descamps, Vincent Lavoué et al. (2024). Hallucination Rates and Reference Accuracy of ChatGPT and Bard for Systematic Reviews: Comparative Analysis. *Journal of Medical Internet Research*. https://doi.org/10.2196/53164
19. Cuiping Song, Yanping Song (2023). Enhancing academic writing skills and motivation: assessing the efficacy of ChatGPT in AI-assisted language learning for EFL students. *Frontiers in Psychology*. https://doi.org/10.3389/fpsyg.2023.1260843
20. Akash Kumar Saini, Bill Cope, Mary Kalantzis et al. (2024). The Future of Feedback: Integrating Peer and Generative AI Reviews to Support Student Work. https://doi.org/10.35542/osf.io/x3dct
21. Hilda Hadan, D. Wang, Reza Hadi Mogavi et al. (2024). The great AI witch hunt: Reviewers’ perception and (Mis)conception of generative AI in research writing. *Computers in Human Behavior Artificial Humans*. https://doi.org/10.1016/j.chbah.2024.100095
22. Khairi Obaid Al-Zubaidi, Mohamed Jaafari, Fatima Zahra Touzani (2024). Impact of ChatGPT on Academic Writing at Moroccan Universities. *Arab World English Journal*. https://doi.org/10.24093/awej/chatgpt.1
23. Himel Mondal, Shaikat Mondal (2023). ChatGPT in academic writing: Maximizing its benefits and minimizing the risks. *Indian Journal of Ophthalmology*. https://doi.org/10.4103/ijo.ijo_718_23
24. Daniele Saccenti, Matilde Buattini, Silvia Grazioli et al. (2024). Navigating the AI frontier: Should we fear ChatGPT use in higher education and scientific research? Finding a middle ground through guiding principles and practical applications. *Possibility Studies & Society*. https://doi.org/10.1177/27538699241231862
25. Arjun Prakash, Shruti Aggarwal, Jeevan John Varghese et al. (2025). Writing without borders: AI and cross-cultural convergence in academic writing quality. *Humanities and Social Sciences Communications*. https://doi.org/10.1057/s41599-025-05484-6
26. Michael Gerlich (2025). From Offloading to Engagement: An Experimental Study on Structured Prompting and Critical Reasoning with Generative AI. *Data*. https://doi.org/10.3390/data10110172
27. Stefan Küchemann, Steffen Steinert, Natalia Revenga et al. (2023). Can ChatGPT support prospective teachers in physics task development?. *Physical Review Physics Education Research*. https://doi.org/10.1103/physrevphyseducres.19.020128
28. Jessica Leigh Pallant, Janneke Blijlevens, Alexander D. Campbell et al. (2025). Mastering knowledge: the impact of generative AI on student learning outcomes. *Studies in Higher Education*. https://doi.org/10.1080/03075079.2025.2487570
29. Chad C. Tossell, Nathan L. Tenhundfeld, Ali Momen et al. (2024). Student Perceptions of ChatGPT Use in a College Essay Assignment: Implications for Learning, Grading, and Trust in Artificial Intelligence. *IEEE Transactions on Learning Technologies*. https://doi.org/10.1109/tlt.2024.3355015
30. Daniel Stribling, Yuxing Xia, Maha K Amer et al. (2024). The model student: GPT-4 performance on graduate biomedical science exams. *Scientific Reports*. https://doi.org/10.1038/s41598-024-55568-7
31. T. Revell, Will Yeadon, Glenn Cahilly-Bretzin et al. (2024). ChatGPT versus human essayists: an exploration of the impact of artificial intelligence for authorship and academic integrity in the humanities. *International Journal for Educational Integrity*. https://doi.org/10.1007/s40979-024-00161-8
32. Mike Perkins, Jasper Roe, Darius Postma et al. (2023). Detection of GPT-4 Generated Text in Higher Education: Combining Academic Judgement and Software to Identify Generative AI Tool Misuse. *Journal of Academic Ethics*. https://doi.org/10.1007/s10805-023-09492-6
33. P. P. Premkumar, M. R. K. N. Yatigammana, S. Kannangara (2024). Impact of Generative AI on Critical Thinking Skills in Undergraduates: A Systematic Review. *The journal of desk research review and analysis.*. https://doi.org/10.4038/jdrra.v2i1.55
34. Simon Frieder, Luca Pinchetti, Chevalier, Alexis et al. (2023). Mathematical Capabilities of ChatGPT. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2301.13867
35. Javier Cámara, Javier Troya, Loli Burgueño et al. (2023). On the assessment of generative AI in modeling tasks: an experience report with ChatGPT and UML. *Software & Systems Modeling*. https://doi.org/10.1007/s10270-023-01105-5
36. John Jairo Jaramillo, Andrés Chiappe, Fabiola Sáez-Delgado (2025). From Struggle to Mastery: AI-Powered Writing Skills in ESL Education. *Applied Sciences*. https://doi.org/10.3390/app15148079
37. Cecilia Ka Yuk Chan, Wenjie Hu (2023). Students’ voices on generative AI: perceptions, benefits, and challenges in higher education. *International Journal of Educational Technology in Higher Education*. https://doi.org/10.1186/s41239-023-00411-8
38. Jörg von Garrel, Jana Mayer (2023). Artificial Intelligence in studies—use of ChatGPT and AI-based tools among students in Germany. *Humanities and Social Sciences Communications*. https://doi.org/10.1057/s41599-023-02304-7
39. Abdullahi Yusuf, Nasrin Pervin, ‪Marcos Román-González‬ (2024). Generative AI and the future of higher education: a threat to academic integrity or reformation? Evidence from multicultural perspectives. *International Journal of Educational Technology in Higher Education*. https://doi.org/10.1186/s41239-024-00453-6
40. Jake Linardon, Hannah K. Jarman, Zoe McClure et al. (2025). Influence of Topic Familiarity and Prompt Specificity on Citation Fabrication in Mental Health Research Using Large Language Models: Experimental Study. *JMIR Mental Health*. https://doi.org/10.2196/80371
41. Anastasia Olga Tzirides, Gabriela Cecilia Zapata, Nikoleta Polyxeni Kastania et al. (2024). Combining human and artificial intelligence for enhanced AI literacy in higher education. *Computers and Education Open*. https://doi.org/10.1016/j.caeo.2024.100184
42. Sung Il Hwang, Joon Seo Lim, Ro Woon Lee et al. (2023). Is ChatGPT a “Fire of Prometheus” for Non-Native English-Speaking Researchers in Academic Writing?. *Korean Journal of Radiology*. https://doi.org/10.3348/kjr.2023.0773
43. Artur Strzelecki (2023). Students’ Acceptance of ChatGPT in Higher Education: An Extended Unified Theory of Acceptance and Use of Technology. *Innovative Higher Education*. https://doi.org/10.1007/s10755-023-09686-1
44. Afia Fatima, Muhammad Ashir Shafique, Khadija Alam et al. (2024). ChatGPT in medicine: A cross-disciplinary systematic review of ChatGPT’s (artificial intelligence) role in research, clinical practice, education, and patient interaction. *Medicine*. https://doi.org/10.1097/md.0000000000039250
45. Chung Kwan Lo (2023). What Is the Impact of ChatGPT on Education? A Rapid Review of the Literature. *Education Sciences*. https://doi.org/10.3390/educsci13040410
46. Stanislav Hristov Ivanov, Mohammad S.A. Soliman, Aarni Tuomi et al. (2024). Drivers of generative AI adoption in higher education through the lens of the Theory of Planned Behaviour. *Technology in Society*. https://doi.org/10.1016/j.techsoc.2024.102521
47. Saif M I Alkhaaldi, Carl H Kassab, Zakia Dimassi et al. (2023). Medical Student Experiences and Perceptions of ChatGPT and Artificial Intelligence: Cross-Sectional Study. *JMIR Medical Education*. https://doi.org/10.2196/51302
48. Philipp Haindl, Gerald Weinberger (2024). Students’ Experiences of Using ChatGPT in an Undergraduate Programming Course. *IEEE Access*. https://doi.org/10.1109/access.2024.3380909
49. Huihui Liu, Mehreen Azam, Salman Bin Naeem et al. (2023). An overview of the capabilities of ChatGPT for medical writing and its implications for academic integrity. *Health Information & Libraries Journal*. https://doi.org/10.1111/hir.12509
50. Tareq Rasul, Sumesh Nair, Diane Robyn Kalendra et al. (2023). The role of ChatGPT in higher education: Benefits, challenges, and future research directions. *Journal of Applied Learning & Teaching*. https://doi.org/10.37074/jalt.2023.6.1.29
51. Md. Mostafizer Rahman, Yutaka Watanobe (2023). ChatGPT for Education and Research: Opportunities, Threats, and Strategies. *Applied Sciences*. https://doi.org/10.3390/app13095783
52. Hossein Hassani, Emmanuel Sirimal Silva (2023). The Role of ChatGPT in Data Science: How AI-Assisted Conversational Interfaces Are Revolutionizing the Field. *Big Data and Cognitive Computing*. https://doi.org/10.3390/bdcc7020062
53. Joanah Pwanedo Amos, Oluwatosin Ahmed Amodu, Raja Azlina Raja Mahmood et al. (2025). A Bibliometric Exposition and Review on Leveraging LLMs for Programming Education. *IEEE Access*. https://doi.org/10.1109/access.2025.3554627
54. Joseph Mugaanyi, Liuying Cai, Sumei Cheng et al. (2024). Evaluation of Large Language Model Performance and Reliability for Citations and References in Scholarly Writing: Cross-Disciplinary Study. *Journal of Medical Internet Research*. https://doi.org/10.2196/52935
55. Juli Sardi, Darmansyah Darmansyah, Oriza Candra et al. (2025). How Generative AI Influences Students’ Self-Regulated Learning and Critical Thinking Skills? A Systematic Review. *International Journal of Engineering Pedagogy (iJEP)*. https://doi.org/10.3991/ijep.v15i1.53379
56. Mohammed Abdullatif Almulla (2024). Investigating influencing factors of learning satisfaction in AI ChatGPT for research: University students perspective. *Heliyon*. https://doi.org/10.1016/j.heliyon.2024.e32220
57. Laurie Hughes, Tegwen Malik, Sandra Dettmer et al. (2025). Reimagining Higher Education: Navigating the Challenges of Generative AI Adoption. *Information Systems Frontiers*. https://doi.org/10.1007/s10796-025-10582-6
58. Damian Eke (2023). ChatGPT and the rise of generative AI: Threat to academic integrity?. *Journal of Responsible Technology*. https://doi.org/10.1016/j.jrt.2023.100060
59. Ting Wang, Brady Daniel Lund, Agostino Marengo et al. (2023). Exploring the Potential Impact of Artificial Intelligence (AI) on International Students in Higher Education: Generative AI, Chatbots, Analytics, and International Student Success. *Applied Sciences*. https://doi.org/10.3390/app13116716
60. Michail N. Giannakos, Roger Azevedo, Peter L. Brusilovsky et al. (2024). The promise and challenges of generative AI in education. *Behaviour and Information Technology*. https://doi.org/10.1080/0144929x.2024.2394886
61. Nigel Francis, Sue Jones, David P. Smith (2025). Generative AI in Higher Education: Balancing Innovation and Integrity. *British Journal of Biomedical Science*. https://doi.org/10.3389/bjbs.2024.14048
62. Husam Yaseen, Abdelaziz Saleh Mohammad, Najwa Mohammad Ashal et al. (2025). The Impact of Adaptive Learning Technologies, Personalized Feedback, and Interactive AI Tools on Student Engagement: The Moderating Role of Digital Literacy. *Sustainability*. https://doi.org/10.3390/su17031133
63. Chiara Natali, Luca Marconi, Leslye Denisse Dias Duran et al. (2025). AI-induced Deskilling in Medicine: A Mixed-Method Review and Research Agenda for Healthcare and Beyond. *Artificial Intelligence Review*. https://doi.org/10.1007/s10462-025-11352-1
64. Ziyaeddin Halid İPEK, Ali İbrahim Can Gözüm, Stamatios Papadakis et al. (2023). Educational Applications of the ChatGPT AI System: A Systematic Review Research. *Educational Process International Journal*. https://doi.org/10.22521/edupij.2023.123.2
65. Brady Daniel Lund, Ting Wang, Nishith Reddy Mannuru et al. (2023). ChatGPT and a new academic reality: Artificial Intelligence‐written research papers and the ethics of the large language models in scholarly publishing. *Journal of the Association for Information Science and Technology*. https://doi.org/10.1002/asi.24750
66. Miriam Sullivan, Andrew Kelly, Paul McLaughlan (2023). ChatGPT in higher education: Considerations for academic integrity and student learning. *Journal of Applied Learning & Teaching*. https://doi.org/10.37074/jalt.2023.6.1.17
67. Jürgen Rudolph, Samson Tan, Shannon Tan (2023). ChatGPT: Bullshit spewer or the end of traditional assessments in higher education?. *Journal of Applied Learning & Teaching*. https://doi.org/10.37074/jalt.2023.6.1.9
68. Omid Noroozi, Saba Soleimani, Mohammadreza Farrokhnia et al. (2024). Generative AI in Education: Pedagogical, Theoretical, and Methodological Perspectives. *International Journal of Technology in Education*. https://doi.org/10.46328/ijte.845
69. Ankita Guleria, Kewal Krishan, Vishal Sharma et al. (2023). ChatGPT: ethical concerns and challenges in academics and research. *The Journal of Infection in Developing Countries*. https://doi.org/10.3855/jidc.18738
70. Maxim Topaz, Nir Roguin, Pallavi Gupta et al. (2026). Fabricated citations: an audit across 2·5 million biomedical papers. *The Lancet*. https://doi.org/10.1016/s0140-6736(26)00603-3
71. Shereen El Tarhouny, Amira Farghaly (2026). Deskilling dilemma: brain over automation. *Frontiers in Medicine*. https://doi.org/10.3389/fmed.2026.1765692
72. Vishisht Srihari Rao, Aounon Kumar, Himabindu Lakkaraju et al. (2025). Detecting LLM-generated peer reviews. *PLoS ONE*. https://doi.org/10.1371/journal.pone.0331871
73. Wenyi Gan, Jianfeng Ouyang, Hua Li et al. (2024). Integrating ChatGPT in Orthopedic Education for Medical Undergraduates: Randomized Controlled Trial. *Journal of Medical Internet Research*. https://doi.org/10.2196/57037
74. Bayode Ogunleye, Kudirat Ibilola Zakariyyah, Oluwaseun Ajao et al. (2024). A Systematic Review of Generative AI for Teaching and Learning Practice. *Education Sciences*. https://doi.org/10.3390/educsci14060636
75. Nikki M. Barrington, Nithin K. Gupta, Basel Musmar et al. (2023). A Bibliometric Analysis of the Rise of ChatGPT in Medical Research. *Medical Sciences*. https://doi.org/10.3390/medsci11030061
76. Peng Zhang, Gemma Tur (2023). A systematic review of ChatGPT use in K‐12 education. *European Journal of Education*. https://doi.org/10.1111/ejed.12599
77. Rosario Michel‐Villarreal, Eliseo Luis Vilalta-perdomo, David Ernesto Salinas-Navarro et al. (2023). Challenges and Opportunities of Generative AI for Higher Education as Explained by ChatGPT. *Education Sciences*. https://doi.org/10.3390/educsci13090856
