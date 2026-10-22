# Research Brief: 한국어 토크나이징 방법 개선

> RQ — 기존 접근법보다 더 나은 토큰화 품질과 하위 자연어처리(NLP) 성능을 얻으려면 한국어 토큰화 방법을 어떻게 개선할 수 있는가?

> 본문은 영어 원문(brief.json)을 한국어로 옮긴 것이다. 논문 제목·저자·DOI·검색 쿼리·§3 표의 결과 요약은 원문 그대로이며, 영어 원문 리포트는 같은 폴더의 `report.en.md`.

## 요약

397편의 후보 중 93편을 평가했으며, 한국어에 직접 해당하는 근거는 중간 신뢰도의 실증 연구 소수(주로 단일 과제)로 한정되고 효과 크기는 알 수 없다. 합의된 점은 형태소 사전 분절 후 서브워드 학습(morpheme+BPE)이 한국어 NLU·MT 과제 대부분에서 가장 강하고, 서브워드 단위가 단어·형태소 단위보다 OOV에 강건하다는 것이다. 터키어 등 형태소가 풍부한 언어의 연구도 이를 간접적으로 뒷받침한다. 다만 서브워드로도 CJK의 OOV 문제는 사라지지 않으며, 음절 단위 모델링이나 음절 패턴 기반 미등록어 추정이 띄어쓰기 오류와 미등록 형태소에 강건하다는 태깅 연구가 있다. 상충하는 지점은 형태소 분절이 사전 분절기로 쓰일 때와 독립 토크나이저로 쓰일 때의 결과가 다르다는 것이며, 과제·도메인·어휘 조건이 제각각이라 교란되어 있다(KorQuAD에서는 plain BPE가 우세, 리뷰 감성 분석에서는 독립 형태소 토큰이 열세). 핵심 Gap은 첫째, 한국어에서 fertility·형태소 경계 정렬·OOV rate 같은 내재적 지표를 KLUE·KoBEST 등 하위 과제 성능과 연결한 연구를 찾지 못했다는 점이다. 둘째, 어휘 크기와 단일언어/다국어 구성의 영향, 그리고 어휘 확장(EEVE)의 효율 효과가 한국어에서는 검증되지 않았다(리더보드 성능만 보고됨). 노이즈 텍스트 강건성과 자모 단위 토크나이저 비교도 비어 있다.

## 먼저 읽을 문헌 (10편)

Evaluator 의 관련성(rel)·신뢰도(reli) 점수 순. 전체 평가 표는 §3, 서지 정보는 참고문헌.

| # | 문헌 | 핵심 결과 | sub-RQ | rel · reli |
|---|---|---|---|---|
| [1] | An Empirical Study of Tokenization Strategies for Various Korean NLP Tasks (2020) | 형태소 분절(morphological segmentation) 후 BPE를 적용하는 방식이 한영 기계번역(MT)과 자연어 이해(NLU) 과제인 KorNLI, KorSTS, NSMC, PAWS-X에서 가장 좋은 성능을 보인다. 단순 BPE는 KorQuAD에서 가장 좋다. | rq1, rq2, rq4 | 5 · 4 |
| [2] | Efficient and Effective Vocabulary Expansion Towards Multilingual Large Languag… (2024) | 매개변수 동결(parameter freezing)과 하위 단어 초기화(subword initialization)를 적용한 EEVE 어휘 확장은 약 2B 토큰만으로 영어 중심 LLM의 한국어 능력을 향상시킨다. 이 모델은 2024년 1월 기준 Open Ko-LLM Leaderboard에… | rq5, rq3 | 5 · 3 |
| [3] | An Empirical Study of Korean Sentence Representation with Various Tokenizations (2021) | 하위 단어(subword) 단위는 다른 토큰 단위보다 미등록어(OOV) 문제에 더 강건하다. 공백을 특정 기호로 대체하는 것은 감성 분석에서 불리하게 작용했다. | rq1, rq2, rq6 | 5 · 3 |
| [4] | Impact of Tokenization on Language Models: An Analysis for Turkish (2023) | 형태소 수준 토크나이저는 터키어에서 사실상 표준(de facto) 토크나이저와 대등한 성능을 보인다. 어휘 크기가 커지면 사실상 표준 토크나이저보다 형태소 수준 및 단어 수준 토크나이저가 더 큰 이득을 얻는다. | rq1, rq3, rq2 | 4 · 4 |
| [5] | A study on the evaluation of tokenizer performance in natural language processi… (2023) | 감성 분류에서 SentencePiece가 Mecab-Ko보다 뛰어났으며, 특히 ANN과 LSTM-RNN에서 그러했다. SentencePiece는 또한 사전에 정의되지 않은 짧은 단어와 전문 용어에도 의미를 부여할 수 있다. | rq1, rq2, rq6 | 4 · 3 |
| [6] | Language Model Tokenizers Introduce Unfairness Between Languages (2023) | 같은 텍스트를 서로 다른 언어로 번역하면 다국어 토크나이저를 사용하더라도 토큰화 길이가 최대 15배까지 차이날 수 있고, 바이트 및 문자 수준 모델에서는 차이가 4배 넘게 나타난다. 이는 일부 언어 공동체에 비용, 지연 시간, 문맥 수용 능력의 불평등이 존재함을 시사한다. | rq3, rq5, rq2 | 4 · 3 |
| [7] | Korean named entity recognition based on language-specific features (2023) | 조사와 어미 같은 기능 형태소를 분리하여 개체명(NE) 모호성을 줄이는, 한국어 개체명 인식(NER)을 위한 형태소 기반 CoNLL-U 주석 체계를 제안한다. 결과는 이 형식이 실현 가능함을 보여 주며, 모델 성능은 추가된 언어 특화 자질에 따라 달라진다. | rq2, rq4, rq1 | 4 · 3 |
| [8] | Robust Multi-task Learning-based Korean POS Tagging to Overcome Word Spacing Er… (2023) | 음절 수준 다중 과제(multi-task) 품사 태거는 한국어 띄어쓰기 오류에 강건하며 세종 테스트 세트에서 98.30 F1에 도달해 기존 연구보다 우수하다. | rq6, rq4, rq1 | 4 · 3 |
| [9] | Effects and Mitigation of Out-of-vocabulary in Universal Language Models (2021) | 한국어를 포함한 CJK 언어에서는 하위 단어 토큰화를 사용하더라도 OOV가 여전히 문제로 남으며 하위 전이 학습(transfer learning)에 악영향을 미친다. 저자들은 이를 완화하는 접근법을 제안하고 OOV와 과제 성능 사이의 상관관계를 분석한다. | rq3, rq6 | 4 · 3 |
| [10] | Tokenizer Choice For LLM Training: Negligible or Crucial? (2023) | 토크나이저 선택은 하위 성능과 학습 비용에 크게 영향을 미치며, 비옥도(fertility)와 동등성(parity)이 항상 하위 성능을 예측하는 것은 아니다. 다국어 토크나이저는 영어 토크나이저보다 대략 세 배 큰 어휘가 필요하다. | rq3, rq4 | 3 · 4 |

## 1. 주제 재정의

- RQ: 기존 접근법보다 더 나은 토큰화 품질과 하위 자연어처리(NLP) 성능을 얻으려면 한국어 토큰화 방법을 어떻게 개선할 수 있는가?
- 독립변수: improved Korean tokenization method (e.g., morpheme-aware or modified subword segmentation)
- 종속변수: tokenization quality, downstream NLP task performance, vocabulary efficiency (token count, sequence length)
- 대상: Korean-language text corpora and Korean NLP models
- 핵심 개념: Korean tokenization, morphological analysis, subword tokenization, byte-pair encoding, agglutinative language, Korean natural language processing, vocabulary design

## 2. 조사 계획

전략: OpenAlex와 arXiv, 그리고 이를 통해 확인되는 ACL Anthology 계열 학술 발표처를 이용하여 2016년부터 현재까지, 특히 트랜스포머와 LLM 시대를 아우르는 2019년 이후에 중점을 두고 검색한다. 한국어 벤치마크(예: KLUE, NSMC, KorQuAD)에서 비교 기준선(baseline)을 갖춘 실증 연구와 토큰화 분석을 우선하며, 중국어나 일본어 분절만 다루는 논문은 교착어에 전용 가능한 방법을 제시하지 않는 한 제외한다. rq4(한국어 토큰화의 내재적 평가)와 rq6(강건성)가 문헌에서 가장 빈약할 것으로 예상한다.}

- **rq1** 형태소 분석과 하위 단어 방식을 결합한 하이브리드 방식을 포함하여, 형태소 인식(morpheme-aware) 토큰화 방법은 순수 통계적 하위 단어 토크나이저와 비교해 한국어 하위 NLP 과제 성능에서 어떻게 다른가?

- **rq2** 표준 하위 단어 알고리즘(BPE, WordPiece, SentencePiece unigram, 바이트 수준)은 한국어의 교착어 형태론과 한글 문자 체계에서 어떻게 작동하며, 이들에 대해 어떤 수정이 제안되어 왔는가?

- **rq3** 어휘 설계 선택(어휘 크기, 구성, 다국어 대 단일 언어 어휘)은 한국어 토큰 효율, 시퀀스 길이, 모델 성능에 어떤 영향을 미치는가?

- **rq4** 한국어 토큰화 품질을 평가하는 데 어떤 내재적 지표와 평가 절차가 사용되며, 이들은 하위 성능과 얼마나 잘 상관되는가?

- **rq5** 사전학습 모델의 토크나이저 교체나 어휘 확장, 그리고 그것이 비용과 생성 품질에 미치는 영향을 포함하여, 한국어 토큰화 개선은 대규모 언어 모델에 어떻게 적용되는가?

- **rq6** 한국어 토크나이저는 띄어쓰기 오류 처리, 잡음이 섞인 사용자 생성 텍스트, 미등록어, 희귀 형태 변화형 등과 관련하여 어떤 강건성 문제와 의도치 않은 영향을 보이는가?

<details><summary>검색 쿼리 전체 (33개 — Replan 으로 추가된 쿼리 포함)</summary>

- **rq1** (4개): morpheme-aware subword tokenization Korean; Korean morphological analysis BPE hybrid tokenizer; morpheme-based tokenizer Korean downstream tasks; Korean pre-trained language model morphological segmentation

- **rq2** (4개): byte-pair encoding agglutinative language Korean; SentencePiece WordPiece Korean comparison; Hangul jamo-level subword tokenization; byte-level tokenization Korean Unicode

- **rq3** (7개): vocabulary size effect Korean language model; multilingual tokenizer Korean token fertility; tokenizer vocabulary expansion Korean LLM; token count sequence length Korean text efficiency; Korean BERT vocabulary size ablation downstream accuracy; monolingual versus multilingual vocabulary Korean pretrained model; Korean tokens per character tokenizer vocabulary comparison

- **rq4** (7개): intrinsic evaluation tokenization quality morphological alignment; Korean tokenizer evaluation benchmark; tokenization metrics correlation downstream performance; Korean word segmentation spacing evaluation; Korean tokenizer morpheme boundary alignment downstream KLUE; tokenizer fertility compression Korean KoBEST evaluation; Korean subword tokenization ablation intrinsic extrinsic correlation

- **rq5** (7개): Korean large language model tokenizer adaptation; vocabulary extension cross-lingual transfer Korean; tokenizer-free or byte-level models Korean; language model tokenizer inference cost Korean; Korean vocabulary expansion continual pretraining LLaMA; embedding initialization new tokens Korean LLM adaptation; Korean-centric LLM tokenizer extension token efficiency

- **rq6** (4개): Korean noisy text tokenization robustness; spacing errors Korean subword tokenizer; out-of-vocabulary Korean user-generated text; Korean social media morphological analysis

</details>

## 3. Evidence Table

### 3.1 Evidence map — sub-RQ × 신뢰도

| sub-RQ | 편수 (rel ≥ 3) | 신뢰도 4~5 | 신뢰도 3 | 신뢰도 ≤ 2 | 평균 신뢰도 | 커버 |
|---|---|---|---|---|---|---|
| rq1 | 14 | 3 | 11 | 0 | 3.2 | ✅ |
| rq2 | 9 | 3 | 6 | 0 | 3.3 | ✅ |
| rq3 | 10 | 4 | 6 | 0 | 3.4 | ✅ |
| rq4 | 8 | 3 | 5 | 0 | 3.4 | ✅ |
| rq5 | 4 | 1 | 3 | 0 | 3.2 | ✅ |
| rq6 | 9 | 2 | 7 | 0 | 3.2 | ✅ |

커버 기준은 Critic 결정적 검사와 같다 (relevance ≥ 3 인 문헌 3편 이상). 신뢰도는 Evaluator 가 설계·표본·출처로 매긴 0~5 점.

### 3.2 sub-RQ 별 문헌

#### rq1 — 형태소 분석과 하위 단어 방식을 결합한 하이브리드 방식을 포함하여, 형태소 인식(morpheme-aware) 토큰화 방법은 순수 통계적 하위 단어 토크나이저와 비교해 한국어 하위 NLP 과제 성능에서 어떻게 다른가?

15편 (rel ≥ 3: 14편) · 신뢰도 평균 3.2 · 상위: [1] An Empirical Study of Tokenization Strategies for Various K… (2020) (reli 4); [3] An Empirical Study of Korean Sentence Representation with V… (2021) (reli 3); [4] Impact of Tokenization on Language Models: An Analysis for… (2023) (reli 4)

<details><summary>전체 표 (15편)</summary>

| # | 문헌 | rel | reli | method | sample | finding |
|---|---|---|---|---|---|---|
| [1] | An Empirical Study of Tokenization Strategies for Various Korean NLP… (2020) | 5 | 4 | empirical comparison of tokenization strategies on Korean-English MT and NLU ta… | KorNLI, KorSTS, NSMC, PAWS-X, KorQuAD, Korean-English MT | 형태소 분절(morphological segmentation) 후 BPE를 적용하는 방식이 한영 기계번역(MT)과 자연어 이해(NLU) 과제인 KorNLI, KorSTS, NSMC, PAWS-X에서 가장 좋은 성능을 보인다. 단순 BPE는 KorQuAD에서 가장 좋다. |
| [3] | An Empirical Study of Korean Sentence Representation with Various Tok… (2021) | 5 | 3 | empirical comparison of word, morpheme, subword, and submorpheme tokenizations… |  | 하위 단어(subword) 단위는 다른 토큰 단위보다 미등록어(OOV) 문제에 더 강건하다. 공백을 특정 기호로 대체하는 것은 감성 분석에서 불리하게 작용했다. |
| [4] | Impact of Tokenization on Language Models: An Analysis for Turkish (2023) | 4 | 4 | empirical comparison of five tokenizers by pretraining RoBERTa-style models and… | Turkish split of OSCAR corpus; six downstream tasks | 형태소 수준 토크나이저는 터키어에서 사실상 표준(de facto) 토크나이저와 대등한 성능을 보인다. 어휘 크기가 커지면 사실상 표준 토크나이저보다 형태소 수준 및 단어 수준 토크나이저가 더 큰 이득을 얻는다. |
| [5] | A study on the evaluation of tokenizer performance in natural languag… (2023) | 4 | 3 | comparative experiment of Mecab-Ko vs SentencePiece with five classifiers (NB,… | Korean online customer reviews | 감성 분류에서 SentencePiece가 Mecab-Ko보다 뛰어났으며, 특히 ANN과 LSTM-RNN에서 그러했다. SentencePiece는 또한 사전에 정의되지 않은 짧은 단어와 전문 용어에도 의미를 부여할 수 있다. |
| [7] | Korean named entity recognition based on language-specific features (2023) | 4 | 3 | corpus annotation scheme and conversion algorithm, with experiments using tradi… |  | 조사와 어미 같은 기능 형태소를 분리하여 개체명(NE) 모호성을 줄이는, 한국어 개체명 인식(NER)을 위한 형태소 기반 CoNLL-U 주석 체계를 제안한다. 결과는 이 형식이 실현 가능함을 보여 주며, 모델 성능은 추가된 언어 특화 자질에 따라 달라진다. |
| [8] | Robust Multi-task Learning-based Korean POS Tagging to Overcome Word… (2023) | 4 | 3 | multi-task learning neural model (ELECTRA + RNN-CRF) with syllable-level I/O, e… | Sejong corpus test set | 음절 수준 다중 과제(multi-task) 품사 태거는 한국어 띄어쓰기 오류에 강건하며 세종 테스트 세트에서 98.30 F1에 도달해 기존 연구보다 우수하다. |
| [11] | KLUE: Korean Language Understanding Evaluation (2021) | 3 | 4 | benchmark construction (8 Korean NLU tasks) with PLM baseline experiments | 8 Korean NLU tasks built from scratch | KLUE offers a Korean NLU benchmark, along with KLUE-BERT and KLUE-RoBERTa models. KLUE-RoBERTa-large outperforms the other baselines, including multilingual PL… |
| [12] | Between words and characters: A Brief History of Open-Vocabulary Mode… (2021) | 3 | 3 | narrative survey of open-vocabulary modeling and tokenization |  | The survey traces word, character, hybrid and subword (BPE-style) approaches to open-vocabulary modeling. It concludes there is no single best solution and tha… |
| [13] | Analysis of Deep Learning Model Combinations and Tokenization Approac… (2023) | 3 | 3 | empirical comparison of eleven tokenization approaches and several deep learnin… | three English and two Turkish datasets | Contextualized BERT/RoBERTa-based embeddings beat the other neural models. Raw or preprocessed words, stemming and WordPiece gave the most promising results, a… |
| [14] | Korean-Vietnamese Neural Machine Translation System With Korean Morph… (2019) | 3 | 3 | NMT system development using UTagger Korean morphological analysis and word sen… | Korean-Vietnamese parallel corpus (size not stated in the a… | A Korean-Vietnamese NMT system uses UTagger for Korean morphological analysis and WSD and RDRsegmenter for Vietnamese. The abstract is truncated before the res… |
| [15] | Syllable-Pattern-Based Unknown-Morpheme Segmentation and Estimation f… (2002) | 3 | 3 | hybrid statistical and rule-based POS tagging with unknown-morpheme estimation;… | three domain corpora; 10% of morphemes in the test corpora… | A syllable-pattern-based unknown-morpheme estimation method in the POSTAG tagger achieved 97% tagging accuracy even with 10% unknown morphemes. It addresses OO… |
| [16] | Phrase-Based Statistical Model for Korean Morpheme Segmentation and P… (2018) | 3 | 3 | phrase-based statistical model (CRF) for Korean morphological analysis, evaluat… | SEJONG corpus | A phrase-based model for Korean morpheme segmentation and POS tagging outperforms morpheme-based baselines, with statistically significant gains over a state-o… |
| [17] | Evaluating Subword Tokenization: Alien Subword Composition and OOV Ge… (2024) | 3 | 3 | intrinsic-extrinsic evaluation framework (UniMorph Labeller plus OOV Generaliza… | ALBERT, BERT, RoBERTa, DeBERTa; three text classification t… | UniMorph Labeller reaches 98% accuracy in classifying subword tokenization as morphological or alien, and alien tokenization leads to poorer OOV generalization… |
| [18] | Korean clinical entity recognition from diagnosis text using BERT (2020) | 3 | 3 | empirical NER experiments comparing BERT with a character-level BiLSTM-CRF base… | New Korean clinical entity dataset from an online medical Q… | A modified BERT labeling strategy that better separates Korean postpositions achieved micro-averaged precision 0.83, recall 0.85 and F1 0.84. BERT significantl… |
| [19] | Morphology-Aware Segmentation and Tokenization for Turkic Languages:… (2026) | 2 | 3 | framework development with intrinsic, extrinsic and external evaluation (Kazakh… | Kazakh corpus of CSE-generated wordforms and segmented sent… | A CSE-guided morphology-aware tokenization framework for Kazakh cut neural model training time by up to about 33%, mainly through shorter tokenized sentences.… |

</details>

#### rq2 — 표준 하위 단어 알고리즘(BPE, WordPiece, SentencePiece unigram, 바이트 수준)은 한국어의 교착어 형태론과 한글 문자 체계에서 어떻게 작동하며, 이들에 대해 어떤 수정이 제안되어 왔는가?

16편 (rel ≥ 3: 9편) · 신뢰도 평균 3.4 · 상위: [1] An Empirical Study of Tokenization Strategies for Various K… (2020) (reli 4); [3] An Empirical Study of Korean Sentence Representation with V… (2021) (reli 3); [4] Impact of Tokenization on Language Models: An Analysis for… (2023) (reli 4)

<details><summary>전체 표 (16편)</summary>

| # | 문헌 | rel | reli | method | sample | finding |
|---|---|---|---|---|---|---|
| [1] | An Empirical Study of Tokenization Strategies for Various Korean NLP… (2020) | 5 | 4 | empirical comparison of tokenization strategies on Korean-English MT and NLU ta… | KorNLI, KorSTS, NSMC, PAWS-X, KorQuAD, Korean-English MT | 형태소 분절(morphological segmentation) 후 BPE를 적용하는 방식이 한영 기계번역(MT)과 자연어 이해(NLU) 과제인 KorNLI, KorSTS, NSMC, PAWS-X에서 가장 좋은 성능을 보인다. 단순 BPE는 KorQuAD에서 가장 좋다. |
| [3] | An Empirical Study of Korean Sentence Representation with Various Tok… (2021) | 5 | 3 | empirical comparison of word, morpheme, subword, and submorpheme tokenizations… |  | 하위 단어(subword) 단위는 다른 토큰 단위보다 미등록어(OOV) 문제에 더 강건하다. 공백을 특정 기호로 대체하는 것은 감성 분석에서 불리하게 작용했다. |
| [4] | Impact of Tokenization on Language Models: An Analysis for Turkish (2023) | 4 | 4 | empirical comparison of five tokenizers by pretraining RoBERTa-style models and… | Turkish split of OSCAR corpus; six downstream tasks | 형태소 수준 토크나이저는 터키어에서 사실상 표준(de facto) 토크나이저와 대등한 성능을 보인다. 어휘 크기가 커지면 사실상 표준 토크나이저보다 형태소 수준 및 단어 수준 토크나이저가 더 큰 이득을 얻는다. |
| [5] | A study on the evaluation of tokenizer performance in natural languag… (2023) | 4 | 3 | comparative experiment of Mecab-Ko vs SentencePiece with five classifiers (NB,… | Korean online customer reviews | 감성 분류에서 SentencePiece가 Mecab-Ko보다 뛰어났으며, 특히 ANN과 LSTM-RNN에서 그러했다. SentencePiece는 또한 사전에 정의되지 않은 짧은 단어와 전문 용어에도 의미를 부여할 수 있다. |
| [6] | Language Model Tokenizers Introduce Unfairness Between Languages (2023) | 4 | 3 | empirical comparison of tokenization lengths across languages |  | 같은 텍스트를 서로 다른 언어로 번역하면 다국어 토크나이저를 사용하더라도 토큰화 길이가 최대 15배까지 차이날 수 있고, 바이트 및 문자 수준 모델에서는 차이가 4배 넘게 나타난다. 이는 일부 언어 공동체에 비용, 지연 시간, 문맥 수용 능력의 불평등이 존재함을 시사한다. |
| [7] | Korean named entity recognition based on language-specific features (2023) | 4 | 3 | corpus annotation scheme and conversion algorithm, with experiments using tradi… |  | 조사와 어미 같은 기능 형태소를 분리하여 개체명(NE) 모호성을 줄이는, 한국어 개체명 인식(NER)을 위한 형태소 기반 CoNLL-U 주석 체계를 제안한다. 결과는 이 형식이 실현 가능함을 보여 주며, 모델 성능은 추가된 언어 특화 자질에 따라 달라진다. |
| [20] | Sub-Character Tokenization for Chinese Pretrained Language Models (2023) | 3 | 4 | proposal of sub-character tokenization with experiments on downstream tasks |  | SubChar tokenizers produce much shorter sequences and, when pronunciation-based, are robust to homophone typos, while performing competitively on downstream ta… |
| [12] | Between words and characters: A Brief History of Open-Vocabulary Mode… (2021) | 3 | 3 | narrative survey of open-vocabulary modeling and tokenization |  | The survey traces word, character, hybrid and subword (BPE-style) approaches to open-vocabulary modeling. It concludes there is no single best solution and tha… |
| [13] | Analysis of Deep Learning Model Combinations and Tokenization Approac… (2023) | 3 | 3 | empirical comparison of eleven tokenization approaches and several deep learnin… | three English and two Turkish datasets | Contextualized BERT/RoBERTa-based embeddings beat the other neural models. Raw or preprocessed words, stemming and WordPiece gave the most promising results, a… |
| [21] | Charformer: Fast Character Transformers via Gradient-based Subword To… (2021) | 2 | 4 | Model proposal (GBST/Charformer) with experiments on English GLUE, multilingual… |  | Charformer learns subword tokenization end-to-end from bytes. It outperforms byte-level baselines, is generally on par with subword models, and is 28%-100% fas… |
| [22] | Canine : Pre-training an Efficient Tokenization-Free Encoder for Lang… (2022) | 2 | 4 | model proposal with pre-training and multilingual benchmark evaluation | multilingual benchmark (TyDi QA) | Canine, a tokenization-free character-level encoder, outperforms a comparable mBERT by 5.7 F1 on TyDi QA with fewer parameters. It shows that fixed subword voc… |
| [23] | MambaByte: Token-free Selective State Space Model (2024) | 2 | 4 | byte-level state space model with language modeling experiments |  | MambaByte, a token-free byte-level SSM, is competitive with or better than subword Transformers on language modeling, is robust to noise, and gains 2.6x infere… |
| [24] | Effect of tokenization on transformers for biological sequences (2024) | 2 | 4 | empirical comparison of tokenization algorithms across eight biological tasks | eight tasks on protein and nucleotide sequences | The study examines how alternative tokenization algorithms affect transformer performance on biological sequences. Its motivation is that such sequences are ex… |
| [25] | Training Multilingual Pre-trained Language Model with Byte-level Subw… (2021) | 2 | 3 | technical report on byte-level BPE vocabulary for multilingual pretraining (NEZ… |  | NEZHA trained with byte-level subwords consistently outperforms Google multilingual BERT and vanilla NEZHA on several multilingual NLU tasks. |
| [26] | A pre-trained BERT for Korean medical natural language processing (2022) | 2 | 3 | domain-specific BERT pre-training with intrinsic and extrinsic evaluation | Korean medical corpus | A Korean medical BERT improved masked LM and NSP accuracy and improved Pearson correlation by 0.046 on medical semantic textual similarity. The abstract notes… |
| [27] | Domain-Specific Language Model Pre-Training for Korean Tax Law Classi… (2022) | 2 | 3 | domain-specific pre-training from scratch (KTL-BERT, DistilRoBERTa-based) for c… | Korean tax law questions | Domain-specific pre-training is proposed to address performance degradation from technical terms in tax law classification. The visible abstract does not discu… |

</details>

#### rq3 — 어휘 설계 선택(어휘 크기, 구성, 다국어 대 단일 언어 어휘)은 한국어 토큰 효율, 시퀀스 길이, 모델 성능에 어떤 영향을 미치는가?

22편 (rel ≥ 3: 10편) · 신뢰도 평균 3.4 · 상위: [2] Efficient and Effective Vocabulary Expansion Towards Multil… (2024) (reli 3); [4] Impact of Tokenization on Language Models: An Analysis for… (2023) (reli 4); [9] Effects and Mitigation of Out-of-vocabulary in Universal La… (2021) (reli 3)

<details><summary>전체 표 (22편)</summary>

| # | 문헌 | rel | reli | method | sample | finding |
|---|---|---|---|---|---|---|
| [2] | Efficient and Effective Vocabulary Expansion Towards Multilingual Lar… (2024) | 5 | 3 | technical report with vocabulary expansion method (parameter freezing, subword… | EEVE-Korean-10.8B built on SOLAR-10.7B; trained with about… | 매개변수 동결(parameter freezing)과 하위 단어 초기화(subword initialization)를 적용한 EEVE 어휘 확장은 약 2B 토큰만으로 영어 중심 LLM의 한국어 능력을 향상시킨다. 이 모델은 2024년 1월 기준 Open Ko-LLM Leaderboard에… |
| [4] | Impact of Tokenization on Language Models: An Analysis for Turkish (2023) | 4 | 4 | empirical comparison of five tokenizers by pretraining RoBERTa-style models and… | Turkish split of OSCAR corpus; six downstream tasks | 형태소 수준 토크나이저는 터키어에서 사실상 표준(de facto) 토크나이저와 대등한 성능을 보인다. 어휘 크기가 커지면 사실상 표준 토크나이저보다 형태소 수준 및 단어 수준 토크나이저가 더 큰 이득을 얻는다. |
| [9] | Effects and Mitigation of Out-of-vocabulary in Universal Language Mod… (2021) | 4 | 3 | empirical study of OOV effects in transfer learning with a proposed mitigation… | pre-trained language models for CJK languages (sizes not st… | 한국어를 포함한 CJK 언어에서는 하위 단어 토큰화를 사용하더라도 OOV가 여전히 문제로 남으며 하위 전이 학습(transfer learning)에 악영향을 미친다. 저자들은 이를 완화하는 접근법을 제안하고 OOV와 과제 성능 사이의 상관관계를 분석한다. |
| [6] | Language Model Tokenizers Introduce Unfairness Between Languages (2023) | 4 | 3 | empirical comparison of tokenization lengths across languages |  | 같은 텍스트를 서로 다른 언어로 번역하면 다국어 토크나이저를 사용하더라도 토큰화 길이가 최대 15배까지 차이날 수 있고, 바이트 및 문자 수준 모델에서는 차이가 4배 넘게 나타난다. 이는 일부 언어 공동체에 비용, 지연 시간, 문맥 수용 능력의 불평등이 존재함을 시사한다. |
| [10] | Tokenizer Choice For LLM Training: Negligible or Crucial? (2023) | 3 | 4 | controlled ablation training 24 mono- and multilingual LLMs at 2.6B parameters | 24 LLMs; European languages | 토크나이저 선택은 하위 성능과 학습 비용에 크게 영향을 미치며, 비옥도(fertility)와 동등성(parity)이 항상 하위 성능을 예측하는 것은 아니다. 다국어 토크나이저는 영어 토크나이저보다 대략 세 배 큰 어휘가 필요하다. |
| [28] | KsponSpeech: Korean Spontaneous Speech Corpus for Automatic Speech Re… (2020) | 3 | 4 | corpus construction with baseline end-to-end ASR experiments | 969 h of spontaneous Korean dialog, about 2000 native speak… | Introduces the KsponSpeech corpus with orthographic and pronunciation transcription and disfluency tags, and gives baseline end-to-end ASR results. It also inv… |
| [29] | Do All Languages Cost the Same? Tokenization in the Era of Commercial… (2023) | 3 | 4 | systematic analysis of OpenAI API cost and utility on multilingual benchmarks | 22 typologically diverse languages | Token counts for the same content vary widely across languages, so speakers of many supported languages are overcharged by the API while getting poorer results… |
| [12] | Between words and characters: A Brief History of Open-Vocabulary Mode… (2021) | 3 | 3 | narrative survey of open-vocabulary modeling and tokenization |  | The survey traces word, character, hybrid and subword (BPE-style) approaches to open-vocabulary modeling. It concludes there is no single best solution and tha… |
| [30] | Tokenization Standards for Linguistic Integrity: Turkish as a Benchma… (2025) | 3 | 3 | tokenizer evaluation framework with five metrics applied to Turkish MMLU | 6,200 Turkish multiple-choice MMLU questions | Proposes metrics including %TR and token purity for evaluating tokenizers on a morphologically rich language. %TR correlates more strongly with downstream MMLU… |
| [31] | Efficient and Effective Text Encoding for Chinese LLaMA and Alpaca (2023) | 3 | 3 | vocabulary extension plus secondary pre-training and instruction fine-tuning of… |  | Extending LLaMA's vocabulary with 20,000 Chinese tokens improves encoding efficiency and Chinese understanding; with secondary pre-training and instruction tun… |
| [32] | BLOOM: A 176B-Parameter Open-Access Multilingual Language Model (2023) | 2 | 4 | model description and benchmark evaluation (176B decoder-only LLM) | ROOTS corpus, 46 natural and 13 programming languages | BLOOM, an open-access 176B multilingual LLM trained on ROOTS, achieves competitive performance on a wide variety of benchmarks, with stronger results after mul… |
| [33] | Language-agnostic BERT Sentence Embedding (2020) | 2 | 4 | empirical model development and benchmark evaluation (LaBSE) | 112 languages; Tatoeba bi-text retrieval | A pre-trained multilingual LM cuts the parallel data needed by 80%. The best combined model reaches 83.7% bi-text retrieval accuracy over 112 languages on Tato… |
| [34] | How multilingual is Multilingual BERT? (2019) | 2 | 4 | probing experiments and zero-shot cross-lingual transfer evaluation of M-BERT | M-BERT pre-trained on monolingual corpora in 104 languages | M-BERT transfers well zero-shot, even across scripts, and works best between typologically similar languages. It also shows systematic deficiencies for certain… |
| [24] | Effect of tokenization on transformers for biological sequences (2024) | 2 | 4 | empirical comparison of tokenization algorithms across eight biological tasks | eight tasks on protein and nucleotide sequences | The study examines how alternative tokenization algorithms affect transformer performance on biological sequences. Its motivation is that such sequences are ex… |
| [25] | Training Multilingual Pre-trained Language Model with Byte-level Subw… (2021) | 2 | 3 | technical report on byte-level BPE vocabulary for multilingual pretraining (NEZ… |  | NEZHA trained with byte-level subwords consistently outperforms Google multilingual BERT and vanilla NEZHA on several multilingual NLU tasks. |
| [35] | Membership Inference Attacks With Token-Level Deduplication on Korean… (2023) | 2 | 3 | empirical attack experiments on a Korean GPT model | Korean GPT model and its training data | Membership inference attacks on a Korean GPT found approximate training data with 20%-90% precision in the top-100 samples, and redundant sentences were hard t… |
| [36] | Tokenization efficiency of current foundational large language models… (2025) | 2 | 3 | comparative tokenizer fertility measurement across LLMs, plus a transliteration… | tokenizers of current pretrained LLMs on Ukrainian text | Ukrainian is underrepresented in LLM tokenizer vocabularies, which raises token counts, cost and latency. The study measures fertility and tests transliteratio… |
| [37] | From Tokens to Words: On the Inner Lexicon of LLMs (2024) | 2 | 3 | interpretability experiments on LLM internal representations |  | LLMs form whole-word representations from sub-word tokens at the last token in early and middle layers, robust to arbitrary splits, typos and OOV words. This e… |
| [38] | A survey of multilingual large language models (2025) | 2 | 3 | survey / literature review of multilingual LLMs |  | The paper presents a unified taxonomy and review of multilingual large language models and multilingual alignment, covering emerging frontiers and open-source… |
| [39] | Zero‐anaphora resolution in Korean based on deep language representat… (2020) | 2 | 3 | empirical model development (fine-tuned BERT for Korean zero-anaphora resolutio… |  | Fine-tuning a pre-trained BERT for Korean zero anaphora resolution without hand-crafted or dependency features significantly improves performance over other mo… |
| [40] | Small and Practical BERT Models for Sequence Labeling (2019) | 2 | 3 | empirical model compression/distillation from multilingual BERT; evaluation on… | 70 treebanks, 48 languages | A model derived from multilingual BERT is 6x smaller and 27x faster with higher accuracy than a multilingual baseline on POS tagging and morphological predicti… |
| [41] | Vietnamese Sentiment Analysis: An Overview and Comparative Study of F… (2023) | 1 | 3 | comparative fine-tuning study of pretrained language models on five Vietnamese… | five benchmark Vietnamese sentiment analysis datasets | Monolingual PhoBERT and ViT5 outperform previous studies and set new state-of-the-art results on five Vietnamese sentiment analysis datasets. |

</details>

#### rq4 — 한국어 토큰화 품질을 평가하는 데 어떤 내재적 지표와 평가 절차가 사용되며, 이들은 하위 성능과 얼마나 잘 상관되는가?

15편 (rel ≥ 3: 8편) · 신뢰도 평균 3.2 · 상위: [1] An Empirical Study of Tokenization Strategies for Various K… (2020) (reli 4); [7] Korean named entity recognition based on language-specific… (2023) (reli 3); [8] Robust Multi-task Learning-based Korean POS Tagging to Over… (2023) (reli 3)

<details><summary>전체 표 (15편)</summary>

| # | 문헌 | rel | reli | method | sample | finding |
|---|---|---|---|---|---|---|
| [1] | An Empirical Study of Tokenization Strategies for Various Korean NLP… (2020) | 5 | 4 | empirical comparison of tokenization strategies on Korean-English MT and NLU ta… | KorNLI, KorSTS, NSMC, PAWS-X, KorQuAD, Korean-English MT | 형태소 분절(morphological segmentation) 후 BPE를 적용하는 방식이 한영 기계번역(MT)과 자연어 이해(NLU) 과제인 KorNLI, KorSTS, NSMC, PAWS-X에서 가장 좋은 성능을 보인다. 단순 BPE는 KorQuAD에서 가장 좋다. |
| [7] | Korean named entity recognition based on language-specific features (2023) | 4 | 3 | corpus annotation scheme and conversion algorithm, with experiments using tradi… |  | 조사와 어미 같은 기능 형태소를 분리하여 개체명(NE) 모호성을 줄이는, 한국어 개체명 인식(NER)을 위한 형태소 기반 CoNLL-U 주석 체계를 제안한다. 결과는 이 형식이 실현 가능함을 보여 주며, 모델 성능은 추가된 언어 특화 자질에 따라 달라진다. |
| [8] | Robust Multi-task Learning-based Korean POS Tagging to Overcome Word… (2023) | 4 | 3 | multi-task learning neural model (ELECTRA + RNN-CRF) with syllable-level I/O, e… | Sejong corpus test set | 음절 수준 다중 과제(multi-task) 품사 태거는 한국어 띄어쓰기 오류에 강건하며 세종 테스트 세트에서 98.30 F1에 도달해 기존 연구보다 우수하다. |
| [11] | KLUE: Korean Language Understanding Evaluation (2021) | 3 | 4 | benchmark construction (8 Korean NLU tasks) with PLM baseline experiments | 8 Korean NLU tasks built from scratch | KLUE offers a Korean NLU benchmark, along with KLUE-BERT and KLUE-RoBERTa models. KLUE-RoBERTa-large outperforms the other baselines, including multilingual PL… |
| [10] | Tokenizer Choice For LLM Training: Negligible or Crucial? (2023) | 3 | 4 | controlled ablation training 24 mono- and multilingual LLMs at 2.6B parameters | 24 LLMs; European languages | 토크나이저 선택은 하위 성능과 학습 비용에 크게 영향을 미치며, 비옥도(fertility)와 동등성(parity)이 항상 하위 성능을 예측하는 것은 아니다. 다국어 토크나이저는 영어 토크나이저보다 대략 세 배 큰 어휘가 필요하다. |
| [16] | Phrase-Based Statistical Model for Korean Morpheme Segmentation and P… (2018) | 3 | 3 | phrase-based statistical model (CRF) for Korean morphological analysis, evaluat… | SEJONG corpus | A phrase-based model for Korean morpheme segmentation and POS tagging outperforms morpheme-based baselines, with statistically significant gains over a state-o… |
| [17] | Evaluating Subword Tokenization: Alien Subword Composition and OOV Ge… (2024) | 3 | 3 | intrinsic-extrinsic evaluation framework (UniMorph Labeller plus OOV Generaliza… | ALBERT, BERT, RoBERTa, DeBERTa; three text classification t… | UniMorph Labeller reaches 98% accuracy in classifying subword tokenization as morphological or alien, and alien tokenization leads to poorer OOV generalization… |
| [30] | Tokenization Standards for Linguistic Integrity: Turkish as a Benchma… (2025) | 3 | 3 | tokenizer evaluation framework with five metrics applied to Turkish MMLU | 6,200 Turkish multiple-choice MMLU questions | Proposes metrics including %TR and token purity for evaluating tokenizers on a morphologically rich language. %TR correlates more strongly with downstream MMLU… |
| [42] | KorNLI and KorSTS: New Benchmark Datasets for Korean Natural Language… (2020) | 2 | 3 | benchmark dataset construction (machine translation of training sets, manual tr… | Korean NLI and STS datasets | Releases KorNLI and KorSTS Korean NLU benchmarks and baseline results. It can serve as a downstream evaluation resource but does not study tokenization in the… |
| [19] | Morphology-Aware Segmentation and Tokenization for Turkic Languages:… (2026) | 2 | 3 | framework development with intrinsic, extrinsic and external evaluation (Kazakh… | Kazakh corpus of CSE-generated wordforms and segmented sent… | A CSE-guided morphology-aware tokenization framework for Kazakh cut neural model training time by up to about 33%, mainly through shorter tokenized sentences.… |
| [43] | Tokenization for Molecular Foundation Models (2026) | 1 | 4 | systematic evaluation of 35 tokenizers with n-gram proxies and 18 pretrained Ro… | 35 tokenizers (20 chemistry-specific); 18 RoBERTa-style mod… | Existing SMILES tokenizers have significant coverage gaps. The authors propose the Smirk and Smirk-GPE tokenizers with full OpenSMILES coverage and use n-gram… |
| [44] | mGPT: Few-Shot Learners Go Multilingual (2024) | 1 | 3 | multilingual GPT-3-style model pretraining with intrinsic and extrinsic evaluat… | 61 languages, 25 language families; downstream evaluation i… | mGPT is pretrained on 61 languages and evaluated on language modeling, cross-lingual NLU benchmarks and knowledge probing, with in-context learning on par with… |
| [45] | Towards Robust Word Embeddings for Noisy Texts (2020) | 1 | 3 | method proposal (skipgram extension with bridge-words) with intrinsic and extri… |  | Bridge-words added to skipgram strengthen similarity between standard words and noisy variants, outperforming baselines on noisy text across intrinsic and extr… |
| [46] | A Word Pair Dataset for Semantic Similarity and Relatedness in Korean… (2021) | 1 | 3 | reference-standard development and validation with physician ratings | 607 medical word pairs from 518 textbooks, 72,844 news item… | The authors built a Korean medical word pair set for evaluating embedding models on semantic similarity and relatedness. The abstract reports 90.8% of word pai… |
| [47] | AMMUS : A Survey of Transformer-based Pretrained Models in Natural La… (2021) | 1 | 2 | narrative survey of transformer-based pretrained language models |  | Provides an overview of pretraining methods, a taxonomy of T-PTLMs, and intrinsic and extrinsic benchmarks. Korean and tokenization are not addressed in the ab… |

</details>

#### rq5 — 사전학습 모델의 토크나이저 교체나 어휘 확장, 그리고 그것이 비용과 생성 품질에 미치는 영향을 포함하여, 한국어 토큰화 개선은 대규모 언어 모델에 어떻게 적용되는가?

15편 (rel ≥ 3: 4편) · 신뢰도 평균 3.0 · 상위: [2] Efficient and Effective Vocabulary Expansion Towards Multil… (2024) (reli 3); [6] Language Model Tokenizers Introduce Unfairness Between Lang… (2023) (reli 3); [29] Do All Languages Cost the Same? Tokenization in the Era of… (2023) (reli 4)

<details><summary>전체 표 (15편)</summary>

| # | 문헌 | rel | reli | method | sample | finding |
|---|---|---|---|---|---|---|
| [2] | Efficient and Effective Vocabulary Expansion Towards Multilingual Lar… (2024) | 5 | 3 | technical report with vocabulary expansion method (parameter freezing, subword… | EEVE-Korean-10.8B built on SOLAR-10.7B; trained with about… | 매개변수 동결(parameter freezing)과 하위 단어 초기화(subword initialization)를 적용한 EEVE 어휘 확장은 약 2B 토큰만으로 영어 중심 LLM의 한국어 능력을 향상시킨다. 이 모델은 2024년 1월 기준 Open Ko-LLM Leaderboard에… |
| [6] | Language Model Tokenizers Introduce Unfairness Between Languages (2023) | 4 | 3 | empirical comparison of tokenization lengths across languages |  | 같은 텍스트를 서로 다른 언어로 번역하면 다국어 토크나이저를 사용하더라도 토큰화 길이가 최대 15배까지 차이날 수 있고, 바이트 및 문자 수준 모델에서는 차이가 4배 넘게 나타난다. 이는 일부 언어 공동체에 비용, 지연 시간, 문맥 수용 능력의 불평등이 존재함을 시사한다. |
| [29] | Do All Languages Cost the Same? Tokenization in the Era of Commercial… (2023) | 3 | 4 | systematic analysis of OpenAI API cost and utility on multilingual benchmarks | 22 typologically diverse languages | Token counts for the same content vary widely across languages, so speakers of many supported languages are overcharged by the API while getting poorer results… |
| [31] | Efficient and Effective Text Encoding for Chinese LLaMA and Alpaca (2023) | 3 | 3 | vocabulary extension plus secondary pre-training and instruction fine-tuning of… |  | Extending LLaMA's vocabulary with 20,000 Chinese tokens improves encoding efficiency and Chinese understanding; with secondary pre-training and instruction tun… |
| [22] | Canine : Pre-training an Efficient Tokenization-Free Encoder for Lang… (2022) | 2 | 4 | model proposal with pre-training and multilingual benchmark evaluation | multilingual benchmark (TyDi QA) | Canine, a tokenization-free character-level encoder, outperforms a comparable mBERT by 5.7 F1 on TyDi QA with fewer parameters. It shows that fixed subword voc… |
| [25] | Training Multilingual Pre-trained Language Model with Byte-level Subw… (2021) | 2 | 3 | technical report on byte-level BPE vocabulary for multilingual pretraining (NEZ… |  | NEZHA trained with byte-level subwords consistently outperforms Google multilingual BERT and vanilla NEZHA on several multilingual NLU tasks. |
| [26] | A pre-trained BERT for Korean medical natural language processing (2022) | 2 | 3 | domain-specific BERT pre-training with intrinsic and extrinsic evaluation | Korean medical corpus | A Korean medical BERT improved masked LM and NSP accuracy and improved Pearson correlation by 0.046 on medical semantic textual similarity. The abstract notes… |
| [27] | Domain-Specific Language Model Pre-Training for Korean Tax Law Classi… (2022) | 2 | 3 | domain-specific pre-training from scratch (KTL-BERT, DistilRoBERTa-based) for c… | Korean tax law questions | Domain-specific pre-training is proposed to address performance degradation from technical terms in tax law classification. The visible abstract does not discu… |
| [35] | Membership Inference Attacks With Token-Level Deduplication on Korean… (2023) | 2 | 3 | empirical attack experiments on a Korean GPT model | Korean GPT model and its training data | Membership inference attacks on a Korean GPT found approximate training data with 20%-90% precision in the top-100 samples, and redundant sentences were hard t… |
| [36] | Tokenization efficiency of current foundational large language models… (2025) | 2 | 3 | comparative tokenizer fertility measurement across LLMs, plus a transliteration… | tokenizers of current pretrained LLMs on Ukrainian text | Ukrainian is underrepresented in LLM tokenizer vocabularies, which raises token counts, cost and latency. The study measures fertility and tests transliteratio… |
| [37] | From Tokens to Words: On the Inner Lexicon of LLMs (2024) | 2 | 3 | interpretability experiments on LLM internal representations |  | LLMs form whole-word representations from sub-word tokens at the last token in early and middle layers, robust to arbitrary splits, typos and OOV words. This e… |
| [48] | Cross-lingual Transferring of Pre-trained Contextualized Language Mod… (2021) | 2 | 3 | proposed method (TreLM cross-lingual transfer framework) with experiments |  | Proposes TreLM, a framework for transferring pre-trained contextualized language models across languages. It uses a TRILayer structure, a new cross-lingual lan… |
| [38] | A survey of multilingual large language models (2025) | 2 | 3 | survey / literature review of multilingual LLMs |  | The paper presents a unified taxonomy and review of multilingual large language models and multilingual alignment, covering emerging frontiers and open-source… |
| [49] | PreparedLLM: effective pre -pretraining framework for domain-specific… (2024) | 2 | 2 | framework proposal for domain-specific LLM pre-pretraining (data recipe, cleani… |  | Presents PreparedLLM, a pre-pretraining framework that includes vocabulary expansion and embedding initialization to improve domain term understanding and toke… |
| [50] | The first step is the hardest: pitfalls of representing and tokenizin… (2024) | 1 | 2 | case study plus brief review (position paper) | sample mobile sensing dataset tokenized with the OpenAI tok… | Argues that LLM tokenizers are poorly suited to numerical and temporal data and that naively passing timeseries to LLMs can be ineffective. |

</details>

#### rq6 — 한국어 토크나이저는 띄어쓰기 오류 처리, 잡음이 섞인 사용자 생성 텍스트, 미등록어, 희귀 형태 변화형 등과 관련하여 어떤 강건성 문제와 의도치 않은 영향을 보이는가?

16편 (rel ≥ 3: 9편) · 신뢰도 평균 3.2 · 상위: [3] An Empirical Study of Korean Sentence Representation with V… (2021) (reli 3); [5] A study on the evaluation of tokenizer performance in natur… (2023) (reli 3); [9] Effects and Mitigation of Out-of-vocabulary in Universal La… (2021) (reli 3)

<details><summary>전체 표 (16편)</summary>

| # | 문헌 | rel | reli | method | sample | finding |
|---|---|---|---|---|---|---|
| [3] | An Empirical Study of Korean Sentence Representation with Various Tok… (2021) | 5 | 3 | empirical comparison of word, morpheme, subword, and submorpheme tokenizations… |  | 하위 단어(subword) 단위는 다른 토큰 단위보다 미등록어(OOV) 문제에 더 강건하다. 공백을 특정 기호로 대체하는 것은 감성 분석에서 불리하게 작용했다. |
| [5] | A study on the evaluation of tokenizer performance in natural languag… (2023) | 4 | 3 | comparative experiment of Mecab-Ko vs SentencePiece with five classifiers (NB,… | Korean online customer reviews | 감성 분류에서 SentencePiece가 Mecab-Ko보다 뛰어났으며, 특히 ANN과 LSTM-RNN에서 그러했다. SentencePiece는 또한 사전에 정의되지 않은 짧은 단어와 전문 용어에도 의미를 부여할 수 있다. |
| [9] | Effects and Mitigation of Out-of-vocabulary in Universal Language Mod… (2021) | 4 | 3 | empirical study of OOV effects in transfer learning with a proposed mitigation… | pre-trained language models for CJK languages (sizes not st… | 한국어를 포함한 CJK 언어에서는 하위 단어 토큰화를 사용하더라도 OOV가 여전히 문제로 남으며 하위 전이 학습(transfer learning)에 악영향을 미친다. 저자들은 이를 완화하는 접근법을 제안하고 OOV와 과제 성능 사이의 상관관계를 분석한다. |
| [8] | Robust Multi-task Learning-based Korean POS Tagging to Overcome Word… (2023) | 4 | 3 | multi-task learning neural model (ELECTRA + RNN-CRF) with syllable-level I/O, e… | Sejong corpus test set | 음절 수준 다중 과제(multi-task) 품사 태거는 한국어 띄어쓰기 오류에 강건하며 세종 테스트 세트에서 98.30 F1에 도달해 기존 연구보다 우수하다. |
| [28] | KsponSpeech: Korean Spontaneous Speech Corpus for Automatic Speech Re… (2020) | 3 | 4 | corpus construction with baseline end-to-end ASR experiments | 969 h of spontaneous Korean dialog, about 2000 native speak… | Introduces the KsponSpeech corpus with orthographic and pronunciation transcription and disfluency tags, and gives baseline end-to-end ASR results. It also inv… |
| [20] | Sub-Character Tokenization for Chinese Pretrained Language Models (2023) | 3 | 4 | proposal of sub-character tokenization with experiments on downstream tasks |  | SubChar tokenizers produce much shorter sequences and, when pronunciation-based, are robust to homophone typos, while performing competitively on downstream ta… |
| [15] | Syllable-Pattern-Based Unknown-Morpheme Segmentation and Estimation f… (2002) | 3 | 3 | hybrid statistical and rule-based POS tagging with unknown-morpheme estimation;… | three domain corpora; 10% of morphemes in the test corpora… | A syllable-pattern-based unknown-morpheme estimation method in the POSTAG tagger achieved 97% tagging accuracy even with 10% unknown morphemes. It addresses OO… |
| [17] | Evaluating Subword Tokenization: Alien Subword Composition and OOV Ge… (2024) | 3 | 3 | intrinsic-extrinsic evaluation framework (UniMorph Labeller plus OOV Generaliza… | ALBERT, BERT, RoBERTa, DeBERTa; three text classification t… | UniMorph Labeller reaches 98% accuracy in classifying subword tokenization as morphological or alien, and alien tokenization leads to poorer OOV generalization… |
| [18] | Korean clinical entity recognition from diagnosis text using BERT (2020) | 3 | 3 | empirical NER experiments comparing BERT with a character-level BiLSTM-CRF base… | New Korean clinical entity dataset from an online medical Q… | A modified BERT labeling strategy that better separates Korean postpositions achieved micro-averaged precision 0.83, recall 0.85 and F1 0.84. BERT significantl… |
| [21] | Charformer: Fast Character Transformers via Gradient-based Subword To… (2021) | 2 | 4 | Model proposal (GBST/Charformer) with experiments on English GLUE, multilingual… |  | Charformer learns subword tokenization end-to-end from bytes. It outperforms byte-level baselines, is generally on par with subword models, and is 28%-100% fas… |
| [23] | MambaByte: Token-free Selective State Space Model (2024) | 2 | 4 | byte-level state space model with language modeling experiments |  | MambaByte, a token-free byte-level SSM, is competitive with or better than subword Transformers on language modeling, is robust to noise, and gains 2.6x infere… |
| [51] | Korean Grammatical Error Correction Based on Transformer with Copying… (2021) | 2 | 3 | empirical comparison of a Transformer with copying mechanism and noise-implanta… |  | Proposes novel noising methods to build Korean GEC datasets and applies a Transformer with copying mechanism. It outperforms two commercial grammar checkers an… |
| [37] | From Tokens to Words: On the Inner Lexicon of LLMs (2024) | 2 | 3 | interpretability experiments on LLM internal representations |  | LLMs form whole-word representations from sub-word tokens at the last token in early and middle layers, robust to arbitrary splits, typos and OOV words. This e… |
| [52] | Modelling the Englishization of vocabulary in contemporary Korean (2018) | 1 | 3 | lexical analysis of vocabulary items with a descriptive model | 2014 New Words list from the National Institute of Korean L… | Finds that English borrowing into Korean is complex, involving at least four source-language combinations and hybridized word formation. It proposes a descript… |
| [45] | Towards Robust Word Embeddings for Noisy Texts (2020) | 1 | 3 | method proposal (skipgram extension with bridge-words) with intrinsic and extri… |  | Bridge-words added to skipgram strengthen similarity between standard words and noisy variants, outperforming baselines on noisy text across intrinsic and extr… |
| [53] | Building a Korean Sentiment Lexicon Using Collective Intelligence (2015) | 1 | 2 | resource construction via crowdsourced voting (collective intelligence) | 35,000+ word votes from university students, drawn from 517… | Builds an open Korean sentiment lexicon and API through crowdsourced voting on words. The abstract notes that Korean's agglutinative nature makes NLP difficult. |

</details>

#### 평가했으나 어느 sub-RQ 에도 배정되지 않은 문헌 (40편, 대부분 관련성 ≤ 1)

Evaluator 가 읽고 관련성이 낮다고 판정한 문헌. 종합·Gap 에 쓰이지 않아 참고문헌 번호를 받지 않으며, 평가 기록으로만 남긴다.

<details><summary>전체 표 (40편)</summary>

| id | 문헌 | rel | reli | method | sample | finding |
|---|---|---|---|---|---|---|
| 10.1162/tacl_a_00467 | Data-driven Model Generalizability in Crosslinguistic Low-resource Mo… (2022) | 1 | 4 | cross-linguistic empirical comparison of three model classes for morphological… | 11 languages across 6 language families | Model generalization depends on the characteristics of the data set, so conclusions about model performance in low-resource morphological segmentation can be c… |
| 10.48550/arxiv.2106.03193 | The FLORES-101 Evaluation Benchmark for Low-Resource and Multilingual… (2021) | 1 | 4 | benchmark dataset construction with professional translation | 3001 English Wikipedia sentences translated into 101 langua… | Introduces FLORES-101, a high-quality multilingually aligned benchmark for low-resource and multilingual machine translation. The abstract does not mention tok… |
| 10.1162/tacl_a_00661 | KoBBQ: Korean Bias Benchmark for Question Answering (2024) | 1 | 4 | benchmark dataset construction with large-scale survey; evaluation of multiling… | 268 templates, 76,048 samples across 12 bias categories | Presents KoBBQ, a Korean bias benchmark with a cultural adaptation framework, and uses it to measure accuracy and bias scores of multilingual LMs. It does not… |
| 10.48550/arxiv.2209.06794 | PaLI: A Jointly-Scaled Multilingual Language-Image Model (2022) | 1 | 4 | model development and benchmark evaluation (vision-language model) | image-text training set of 10B images and texts in over 100… | PaLI jointly scales language and vision components and achieves state-of-the-art results on multiple vision and language tasks using a multilingual pretraining… |
| 10.48550/arxiv.2402.04177 | Scaling Laws for Downstream Task Performance of Large Language Models (2024) | 1 | 4 | empirical scaling-law experiments on LLM pretraining and finetuning for machine… |  | Downstream translation quality (BLEU, COMET) and cross-entropy improve monotonically with more pretraining data when pretraining and downstream distributions a… |
| 10.46298/jdmdh.9152 | Adapting vs. Pre-training Language Models for Historical Languages (2022) | 1 | 3 | empirical comparison of pretraining from scratch vs. adapting BERT-style models… | historical English text | Pretraining from scratch on historical English data gives a generally stronger background model than adapting a present-day language model. |
| 10.48550/arxiv.2206.05224 | A Multi-Task Benchmark for Korean Legal Language Understanding and Ju… (2022) | 1 | 3 | benchmark dataset construction (LBOX OPEN) | 147k Korean precedents (259M tokens); classification, legal… | The paper presents the first large-scale Korean legal AI benchmark with a corpus and several tasks. The abstract does not discuss tokenization. |
| 10.1038/s41598-025-88960-y | Adaptive ensemble techniques leveraging BERT based models for multili… (2025) | 1 | 3 | ensemble of BERT-based models with meta-learners (Parallel Model Fusion) evalua… | English and Korean hate speech datasets | The ensemble reached accuracies of 85% for English and 89% for Korean and outperformed single models and previous studies. The abstract does not address tokeni… |
| 10.1186/s13321-024-00884-3 | PETA: evaluating the impact of protein transfer learning with sub-wor… (2024) | 1 | 3 | empirical pretraining study with BPE and unigram vocabularies plus a benchmark… | protein sequences; vocabularies of various sizes | Subword vocabularies (BPE, unigram) for protein language models outperform single-amino-acid vocabularies on downstream tasks, with vocabularies of 50 and 200… |
| 10.48550/arxiv.2003.14056 | Understanding Cross-Lingual Syntactic Transfer in Multilingual Recurr… (2020) | 1 | 3 | probing experiments on multilingual RNN language models |  | Exposure to a related language does not always increase grammatical knowledge in the target language, and optimal conditions for lexical-semantic transfer may… |
| 10.3390/app132312901 | Contemporary Approaches in Evolving Language Models (2023) | 1 | 2 | narrative survey of language modeling approaches |  | The survey covers language models from n-gram and HMM to BERT, GPT and LLaMA, with attention to agglutinative languages such as Arabic and Turkish. It does not… |
| 10.48550/arxiv.2307.06435 | A Comprehensive Overview of Large Language Models (2023) | 1 | 2 | survey of LLM literature |  | Provides a broad overview of LLM architectures, training, fine-tuning and benchmarking. The abstract does not mention Korean or tokenizer adaptation. |
| 10.48550/arxiv.2307.10169 | Challenges and Applications of Large Language Models (2023) | 1 | 2 | survey/review of open problems in LLMs |  | Aims to set out a systematic list of open problems and application successes for LLMs. The abstract does not mention tokenization or Korean. |
| 10.4040/jkan.2017.47.6.806 | Semantic Network Analysis of Online News and Social Media Text Relate… (2017) | 1 | 2 | semantic network analysis of crawled text with KoNLPy morphological analysis | 536 news pages and 464 tweets | Applies KoNLPy morphological analysis to build semantic networks of text about comprehensive nursing care service. The study uses morphological analysis only a… |
| 10.1017/s014271640808020x | What's in a word? Morphological awareness and vocabulary knowledge in… (2008) | 0 | 4 | longitudinal psycholinguistic study over 9 months to 1 year with controls for p… | over 660 preschool children (Cantonese, Mandarin, Korean sp… | Morphological awareness predicted unique variance in later vocabulary knowledge across the three languages, and vocabulary knowledge predicted later morphologi… |
| 10.1162/tacl_a_00061 | Cross-Lingual Syntactic Transfer with Limited Resources (2017) | 0 | 4 | cross-lingual dependency parser transfer experiments | 38 Universal Dependencies datasets; Bible and Europarl tran… | Presents a cross-lingual syntactic transfer method that improves over the state of the art when only small translation corpora such as the Bible are available. |
| 10.1007/s10462-023-10471-x | A systematic review of the use of topic models for short text social… (2023) | 0 | 4 | systematic literature review of 189 articles | 189 articles on topic modelling for social media | Finds that the development of short-text topic models is not aligned with how they are used in applied social media analysis. |
| 10.1145/3643540 | Mental-LLM (2024) | 0 | 4 | empirical evaluation of multiple LLMs (zero-shot, few-shot, instruction fine-tu… |  | Instruction fine-tuning significantly boosts LLM performance on mental health prediction tasks from online text; fine-tuned Mental-Alpaca and Mental-FLAN-T5 ou… |
| 10.1109/access.2019.2900672 | Ensemble of Instance Segmentation Models for Polyp Segmentation in Co… (2019) | 0 | 3 | Ensemble of Mask R-CNN models, evaluated on three public polyp datasets | CVC-ClinicDB, ETIS-Larib, CVC-ColonDB colonoscopy image dat… | An ensemble of Mask R-CNN models with ResNet50 and ResNet101 backbones is proposed for polyp segmentation in colonoscopy images. The abstract is cut off before… |
| 10.1017/s1366728912000120 | Parental language mixing: Its measurement and the relation of mixed i… (2012) | 0 | 3 | questionnaire-based correlational study (n=181 parents) | 181 bilingual parents and their children | Higher parental language mixing was associated with smaller comprehension vocabularies in 1.5-year-old bilingual infants and marginally smaller production voca… |
| 10.1017/s1366728920000656 | Phonetic categorization ability and vocabulary size contribute to the… (2020) | 0 | 3 | behavioral experiment (lexical decision, categorization, vocabulary test) | two groups of German learners of English (advanced vs. inte… | Phonetic categorization predicted nonword rejection for intermediate L2 learners, while vocabulary size did so for advanced learners. |
| 10.14746/ssllt.2022.12.3.5 | The role of motivation and vocabulary learning strategies in L2 vocab… (2022) | 0 | 3 | questionnaire survey with structural equation modeling, n=185 | 185 Korean secondary-level EFL learners | Motivation directly and indirectly (via vocabulary learning strategies) predicted L2 vocabulary size and depth, with intrinsic motivation having a stronger eff… |
| 10.1111/ijal.12480 | Model‐based feedback for L2 writing revision: The role of vocabulary… (2023) | 0 | 3 | quasi-experimental study, n=60 | 60 Korean EFL learners aged 18-21 | Model-text feedback improved revisions, and learners' receptive and productive vocabulary sizes predicted the effectiveness of the feedback. |
| 10.7820/vli.v02.1.stoeckel.bennett | Sources of differential item functioning between Korean and Japanese… (2013) | 0 | 3 | differential item functioning analysis with Rasch item difficulty, n=330 | 184 Korean and 146 Japanese undergraduate EFL learners | 21 of 90 vocabulary test items showed DIF, and loanword status in the L1 explained some of it. |
| 10.1613/jair.2863 | Cross-lingual Annotation Projection for Semantic Roles (2009) | 0 | 3 | annotation projection framework with experimental evaluation | English-German parallel corpus | Proposes a graph-optimization approach to project FrameNet semantic role annotations across languages and shows feasibility for inducing high-precision German… |
| 10.1613/jair.4786 | Cross-Lingual Bridges with Models of Lexical Borrowing (2016) | 0 | 3 | computational model of lexical borrowing with MT applications |  | Develops an Optimality-Theory-inspired model of morpho-phonological transformations to predict donor forms of borrowed words, and applies it to translating out… |
| 10.1016/s0010-0277(99)00036-0 | Human simulations of vocabulary learning (1999) | 0 | 3 | human simulation experiments |  | Experiments test whether the noun-before-verb pattern in child vocabulary learning stems from the information requirements of verb learning rather than concept… |
| 10.1017/s0958344020000038 | Using image-to-text recognition technology to facilitate vocabulary a… (2020) | 0 | 3 | quasi-experiment, pre-test/post-test/delayed post-test with control group, n=40 | 40 Russian-speaking elementary school EFL learners | An image-to-text recognition system was tested for supporting English vocabulary acquisition against a traditional textbook approach. The abstract does not des… |
| 10.48550/arxiv.2310.07554 | A Multi-Task Embedder For Retrieval Augmented LLMs (2023) | 0 | 3 | method proposal (LLM-Embedder for retrieval augmentation) |  | Proposes LLM-Embedder with rank-aware reward and graded distillation to unify diverse retrieval augmentation scenarios for LLMs. |
| 10.1613/jair.4955 | A Distributed Representation-Based Framework for Cross-Lingual Transf… (2016) | 0 | 3 | cross-lingual transfer parsing framework with distributed representations | English training data transferred to three other languages | Cross-lingual distributed representations reduce labeled attachment error by an average of 10.9% relative to a delexicalized parser. |
| 10.1162/tacl_a_00413 | Compressing Large-Scale Transformer-Based Models: A Case Study on BERT (2021) | 0 | 3 | survey of BERT compression methods |  | The paper surveys the state of the art in compressing Transformer models, focusing on BERT, and clarifies best practices and future directions. |
| 10.1109/access.2021.3092735 | Multimodal Emotion Recognition Fusion Analysis Adapting BERT With Het… (2021) | 0 | 3 | proposed multimodal fusion model, empirical (details unclear from abstract) |  | The paper proposes attention-based fusion modules that combine language, audio and visual features with BERT for multimodal emotion recognition. |
| 10.1162/tacl_a_00395 | Revisiting Negation in Neural Machine Translation (2021) | 0 | 3 | automatic and manual evaluation of negation translation, information-flow analy… | EN–DE and EN–ZH translation directions | NMT negation translation accuracy is 91.7–95.7% in manual evaluation across four directions, with under-translation as the main error type. Unrelated to Korean… |
| 10.48550/arxiv.2308.05696 | A Preliminary Study of the Intrinsic Relationship between Complexity… (2023) | 0 | 3 | experimental study of instruction complexity (Tree-Instruct) for LLM alignment |  | Increasing instruction complexity yields sustained LLM performance gains, and the paper examines whether improvements come from more training tokens. Unrelated… |
| 10.1017/s136672892510076x | Unpacking word segmentation processes by L2 Chinese readers: Evidence… (2025) | 0 | 3 | two eye-movement experiments | 48 L1 and 48 high-proficiency L2 Chinese readers per experi… | Both L1 and L2 Chinese readers process temporary segmentation ambiguities efficiently using similar strategies. Concerns human reading of Chinese, not Korean t… |
| 10.1016/j.artmed.2024.102900 | Transformers and large language models in healthcare: A review (2024) | 0 | 2 | narrative survey of transformers in healthcare |  | Surveys how transformer architectures are applied to healthcare data (clinical NLP, imaging, EHR) and discusses benefits and limitations such as computational… |
| 10.1145/3624725 | The Science of Detecting LLM-Generated Text (2024) | 0 | 2 | commentary/overview |  | Discusses the challenges of detecting LLM-generated text; the abstract does not mention Korean or tokenization. |
| 10.1155/2022/7893775 | A Novel Text Mining Approach for Mental Health Prediction Using Bi-LS… (2022) | 0 | 2 | unclear from abstract (proposed Bi-LSTM and BERT framework) |  | The paper proposes a Bi-LSTM and BERT framework to identify depression- and anxiety-related social media posts. |
| 10.64152/10125/67467 | Word segmentation and reading comprehension among advanced learners o… (2024) | 0 | 2 | error analysis with correlation and survey of learners | college learners of Chinese as a second language (size not… | Learners made five types of word segmentation errors, four of which correlated moderately with reading comprehension. Most learners considered segmentation ski… |
| 10.1044/jshr.0302.166 | Reliability of Language Measures and Size of Language Sample (1960) | 0 | 1 | unclear from abstract |  | The abstract contains only bibliographic metadata and citing-article listings, so no findings can be extracted. |

</details>

## 4. 종합

### 합의

- 형태소 사전 분절(morphological pre-segmentation) 후 하위 단어 학습을 하는 방식은 검증된 대부분의 한국어 NLU 및 MT 과제에서 가장 강력한 선택지이며, 하위 단어 단위는 OOV 강건성에서 단어 또는 형태소 수준 단위를 능가한다. 다만 한국어에 대한 근거는 신뢰도가 중간 수준인 두 건의 실증 연구뿐이어서 효과 크기는 알 수 없다. [1, 3] (근거 2편 · 신뢰도 평균 3.5)

- 한국어 밖에서는 형태소 인식 토큰화가 형태론이 풍부한 언어(터키어)에서 표준 토크나이저와 대등하거나 더 낫고, 미등록 단어(영어 중심 모델)에 더 잘 일반화된다. 이는 한국어에 대한 간접적 근거이다. [4, 17] (근거 2편 · 신뢰도 평균 3.5)

- 하위 단어 토큰화는 한국어와 다른 CJK 언어의 OOV 문제를 없애지 못하며 OOV는 전이 학습에 악영향을 준다. 음절 수준 모델링이나 미지 형태소의 음절 패턴 추정 같은 한국어 특화 처리는 띄어쓰기 오류와 미지 형태소가 있는 상황에서도 태깅 정확도를 높게(97-98점) 유지한다. [8, 9, 15] (근거 3편 · 신뢰도 평균 3.0)

- 같은 내용이라도 다국어 토크나이저를 사용하더라도 일부 언어에서는 다른 언어보다 몇 배나 많은 토큰이 필요할 수 있으며, 이는 API 비용, 지연 시간, 문맥 수용 능력의 불평등을 시사한다. 초록들은 한국어를 따로 언급하지 않는다. [6, 29] (근거 2편 · 신뢰도 평균 3.5)

- 영어 중심 LLM의 어휘 확장은 적당한 수준의 추가 학습만으로 대상 언어 능력을 향상시킨다. 한국어의 경우 근거는 EEVE의 리더보드 상 능력 평가(약 2B 학습 토큰, 효율 수치는 보고되지 않음)이다. 인코딩 효율 향상(중국어 토큰 20,000개 추가)은 Chinese LLaMA에서만 제시된다. [2, 31] (근거 2편 · 신뢰도 평균 3.0)

### 상충

- **한국어에서 형태소 기반 분절을 사전 분절기(pre-segmenter)로 사용할 때와 독립 토크나이저로 사용할 때 도움이 되는지 해가 되는지의 여부.** (A 1편 vs B 2편)
  - A: BPE 이전의 사전 분절기로 사용한 형태소 분절은 한영 MT와 네 가지 NLU 과제에서 최고의 결과를 냈으나, KorQuAD에서는 단순 BPE가 우세했다. [1]
  - B: 독립적인 형태소 기반 토큰화는 학습된 하위 단어에 뒤졌다. 리뷰 감성 분류에서는 SentencePiece가 Mecab-Ko를 앞섰고, 문장 임베딩 감성 분석에서는 하위 단어 단위가 형태소 단위보다 OOV에 더 강건했다. [3, 5]
  - 원인 가설: 대조되는 조건이 서로 다르다. BPE에 입력되는 형태소는 희귀 형태에 대한 하위 단어 포괄 범위를 유지하는 반면, 독립 형태소 토큰은 잡음이 많은 리뷰 텍스트에서 OOV와 전문 용어를 남긴다. 과제도 다르며(MT/NLU 벤치마크 대 리뷰 감성), 감성 연구는 단일 과제·단일 도메인이고 표본 크기가 명시되어 있지 않다.

### 조건부

- 한 연구에서 공백을 특수 기호로 대체하는 것이 한국어 감성 분석에 해가 되었으나, 감성만 평가되었기 때문에 이것이 과제에 따라 달라지는지는 검증되지 않았다. [3] (근거 1편 · 신뢰도 평균 3.0)

- 터키어에서는 어휘가 커지면 사실상 표준 토크나이저보다 형태소 수준 및 단어 수준 토크나이저가 더 큰 도움을 받았으나, 한국어에 대한 적용 가능성은 검증되지 않았으므로 한국어에 대한 확신은 낮다. [4] (근거 1편 · 신뢰도 평균 4.0)

- 통제된 유럽 언어 실험에서 다국어 토크나이저는 영어 토크나이저보다 대략 세 배 큰 어휘가 필요했고, 비옥도(fertility)와 동등성(parity)이 하위 성능을 항상 예측하지는 않았다. 한국어로의 전이는 검증되지 않았다. [10] (근거 1편 · 신뢰도 평균 4.0)

- 발음 기반 하위 문자(sub-character) 토큰화는 시퀀스를 단축하고 동음이의 오타에 강하면서 중국어 PLM에서 경쟁력을 유지하나, 한글이 이점을 얻는지는 제시되지 않았다. [20] (근거 1편 · 신뢰도 평균 4.0)

### 커버리지 메모

한국어 근거는 rq4에서 빈약하다. 비옥도(fertility), 경계 정렬(boundary alignment), OOV 비율 같은 내재적 지표를 하위 점수와 연결한 한국어 연구는 없고, 상관관계 근거는 터키어[30], 유럽어[10], 영어[17] 연구에서 나온다. KLUE[11]와 세종 연구[16]는 토큰화 지표를 하위 결과와 연결하지 않는다. rq3도 한국어에 대해 마찬가지로 답이 없는데, 한국어 항목은 ASR 코퍼스[28], 다중 언어 OOV 논문[9], 효율 수치가 없는 보고서[2]뿐이고 어휘 크기 근거는 터키어나 유럽어의 것이기 때문이다. rq1과 rq2는 가장 직접적인 한국어 근거([1], [3], [5])를 갖고 있으나, 이들은 신뢰도가 중간 수준이고 대부분 단일 과제 연구이며 효과 크기가 없다. rq5는 리더보드 평가를 포함한 한국어 기술 보고서 한 건과 중국어 및 언어 간 비용 연구에 의존한다. rq6은 품사 태깅과 NER에서 나온 띄어쓰기 및 미지 형태소 근거가 있으나 잡음이 섞인 사용자 생성 텍스트에 대한 근거는 거의 없다. 어휘 크기와 단일 언어 대 다국어 어휘를 달리하며 문자당 토큰 수와 하위 점수를 함께 제시하는 한국어 절제 실험(ablation), 내재적 지표를 포함한 KLUE/KoBEST 토크나이저 절제 실험, 한국어 LLM 토크나이저 비용 연구가 빠져 있다.

## 5. Research Gap

### G1. 내재적 토크나이저 지표(비옥도, 형태소 경계 정렬, OOV 비율)를 하위 점수와 나란히 보고한 한국어 연구는 없다.

[10, 17, 30] (근거 3편 · 신뢰도 평균 3.3)

상관관계 근거는 터키어와 유럽 언어에서만 나오며, 거기서도 지표가 하위 결과를 일관되지 않게 예측한다. 어떤 지표가 한국어 하위 성능을 예측하는지는 알려져 있지 않다.

- 제안 RQ: 한국어 토크나이저들 전반에서 어떤 내재적 토크나이저 지표(비옥도, 형태소 경계 F1, OOV 비율, 토큰 순도)가 KLUE와 KoBEST 하위 점수를 예측하는가?
- 방법: 토크나이저(BPE, Unigram, 형태소+BPE, 자모 수준, 바이트 수준)만 다른 동일한 소형 RoBERTa 모델을 약 12개 사전학습하고, 시드 3개로 KLUE/KoBEST에서 미세조정한 뒤, 과제 점수에 대한 각 지표의 순위 상관과 혼합 효과 회귀(mixed-effects regression)를 계산한다. 주요 결과는 각 지표와 하위 점수 간의 상관이며, 터키어 %TR 결과와 비교하여 기준으로 삼는다.
- 데이터: 모두의 말뭉치(Modu)나 나무위키/CC-100 한국어 같은 한국어 코퍼스(최소 10B자)와 공개된 KLUE 및 KoBEST 평가 모음. 연산량은 소규모 사전학습 약 12회 분이다.

### G2. 한국어 어휘 설계(크기, 단일 언어 대 다국어 구성)는 연구되지 않았다.

[4, 10, 28] (근거 3편 · 신뢰도 평균 4.0)

어휘 크기 근거는 터키어 형태소 토크나이저와 유럽 다국어 토크나이저에 관한 것이고, 한국어 하위 단어 크기 분석은 ASR에 있는 것이 유일하다. 한국어 어휘 크기를 문자당 토큰 수 및 하위 정확도와 연결한 연구는 없다.

- 제안 RQ: 어휘 크기와 단일 언어 대 다국어 구성은 한국어 문자당 토큰 수와 KLUE 정확도에 어떤 영향을 미치는가?
- 방법: 어휘 크기 16k, 32k, 64k, 128k 각각에 대해 한국어 전용 토크나이저와 한국어+영어+중국어+일본어 토크나이저를 두고, 고정된 연산량으로 8회의 사전학습을 수행하는 통제된 절제 실험을 실시한다. 문자당 토큰 수와 KLUE 점수를 보고하고, 시드를 두어 크기와 구성의 상호작용을 검정한다.
- 데이터: 균형 잡힌 한국어 및 다국어 웹 코퍼스(예: CC-100 또는 mC4 부분집합)와 KLUE. 8회 실행은 소형 모델의 연산 예산 안에 들어간다.

### G3. 사전 분절기 대 독립 형태소 문제는 연구 간에 교란되어 있다.

[1, 3, 5] (근거 3편 · 신뢰도 평균 3.3)

형태소+BPE는 MT와 NLU에서, 단순 BPE는 KorQuAD에서 우세했지만 독립 형태소 토큰화는 감성 분석에서 뒤졌으며, 각 연구가 서로 다른 과제, 도메인, 어휘를 사용했다. 공백 처리는 감성 분석에서만 검증되었다.

- 제안 RQ: 어휘 크기와 학습 데이터를 고정하면, BPE 이전의 형태소 사전 분절이 독립 형태소 토큰과 단순 BPE를 모두 능가하는가, 그리고 공백 처리는 감성 분석 밖에서도 중요한가?
- 방법: 2x3 모델(공백 표지 유무; BPE, 형태소+BPE, 독립 형태소)을 사전학습하고 NLI, NER, QA, 감성, MT로 구성된 사전 등록 평가 모음에서 미세조정한다. 쌍체 부트스트랩(paired bootstrap)으로 쌍별 비교를 하고, 과제별 효과 크기를 과제와 토크나이저의 상호작용과 함께 보고한다. KLUE 평가 모음은 평가 세트로만 사용한다.
- 데이터: 하나의 공유 한국어 코퍼스, 형태소 분절을 위한 Mecab-Ko 또는 Kiwi, 그리고 KLUE, KorQuAD, NSMC와 잡음이 섞인 리뷰 테스트 세트.

### G4. 한국어 어휘 확장 근거는 리더보드상의 능력 평가뿐이며 효율 수치가 없다.

[2, 6, 31] (근거 3편 · 신뢰도 평균 3.0)

EEVE는 문자당 토큰 수나 지연 시간을 보고하지 않으며, 인코딩 효율 향상은 Chinese LLaMA에서만 제시된다. 추가 어휘 크기, 초기화, 매개변수 동결, 학습 토큰 예산의 역할은 분리되어 있지 않고, 비용 격차는 언어 간에 문서화되어 있으나 한국어 수치는 없다.

- 제안 RQ: 영어 중심 LLM에서 추가 어휘 크기, 임베딩 초기화, 동결 일정, 학습 토큰 예산은 각각 한국어 인코딩 효율과 과제 정확도에 얼마나 기여하는가?
- 방법: 기준선(10k개 추가 토큰, 하위 단어 평균 초기화, 단계적 동결, 2B 토큰)을 중심으로 한 번에 한 요인씩 바꾸는 설계를 사용하여, 어휘 크기(3수준), 초기화(대안 1개), 동결(대안 1개), 예산(2수준)을 달리하며 약 8회 실행한다. 결과 변수는 한국어 문자당 토큰 수, 추론 지연 시간, 확장하지 않은 모델 대비 KoBEST/KMMLU 정확도이다.
- 데이터: 7-10B 규모의 오픈 LLM, 한국어 지속 사전학습 코퍼스(약 0.5-4B 토큰), 그리고 토큰 길이 비율을 측정하기 위한 한영 병렬 텍스트.

### G5. 잡음이 섞인 텍스트와 한글 하위 문자 단위에 대한 한국어 토크나이저의 강건성은 비교된 적이 없다.

[5, 8, 20] (근거 3편 · 신뢰도 평균 3.3)

띄어쓰기와 미지 형태소에 강건한 태거들은 토크나이저 비교가 아니라 내재적 태깅 연구이며, 리뷰 텍스트 근거는 Mecab-Ko와 SentencePiece만 비교한다. 발음 기반 하위 문자 토큰화는 중국어에서만 제시된다.

- 제안 RQ: 한국어 사용자 생성 텍스트의 띄어쓰기 오류, 오타, 속어 상황에서 자모 수준 또는 음절 패턴 인식 토크나이저가 BPE와 형태소+BPE보다 더 잘 버티는가?
- 방법: BPE, 형태소+BPE, 음절 수준, 자모 수준 토크나이저를 사용하는 동등한 PLM을 감성 분석과 NER에서 미세조정하고, 깨끗한 텍스트와 10/20/30% 비율의 인위적 띄어쓰기 및 오타 잡음이 있는 테스트 세트에서 평가한다. 토크나이저 간 정확도 저하 곡선을 비교한다.
- 데이터: NSMC, KLUE-NER, 그리고 새로 수집한 약 3,000건의 커뮤니티 또는 리뷰 게시물 주석 세트에 잡음을 프로그램적으로 주입한 데이터.

## 6. 향후 연구 방향

§5 의 제안을 한 표로 요약했다 (전문은 각 Gap). 근거는 해당 Gap 의 인용을 따른다.

| # | 제안 RQ | 연구 설계 | 데이터 | 근거 Gap |
|---|---|---|---|---|
| 1 | 한국어 토크나이저들 전반에서 어떤 내재적 토크나이저 지표(비옥도, 형태소 경계 F1, OOV 비율, 토큰 순도)가 KLUE와 KoBEST 하위 점수를 예측하는가? | 토크나이저(BPE, Unigram, 형태소+BPE, 자모 수준, 바이트 수준)만 다른 동일한 소형 RoBERTa 모델을 약 12개 사전학습하고, 시드 3개로 KLUE/KoBEST… | 모두의 말뭉치(Modu)나 나무위키/CC-100 한국어 같은 한국어 코퍼스(최소 10B자)와 공개된 KLUE 및 KoBEST 평가 모음. 연산… | G1 [10, 17, 30] |
| 2 | 어휘 크기와 단일 언어 대 다국어 구성은 한국어 문자당 토큰 수와 KLUE 정확도에 어떤 영향을 미치는가? | 어휘 크기 16k, 32k, 64k, 128k 각각에 대해 한국어 전용 토크나이저와 한국어+영어+중국어+일본어 토크나이저를 두고, 고정된 연산량으로 8회의 사전학습을 수행하는 통… | 균형 잡힌 한국어 및 다국어 웹 코퍼스(예: CC-100 또는 mC4 부분집합)와 KLUE. 8회 실행은 소형 모델의 연산 예산 안에 들어간다. | G2 [4, 10, 28] |
| 3 | 어휘 크기와 학습 데이터를 고정하면, BPE 이전의 형태소 사전 분절이 독립 형태소 토큰과 단순 BPE를 모두 능가하는가, 그리고 공백 처리는 감성 분석 밖에서도 중요한가? | 2x3 모델(공백 표지 유무; BPE, 형태소+BPE, 독립 형태소)을 사전학습하고 NLI, NER, QA, 감성, MT로 구성된 사전 등록 평가 모음에서 미세조정한다. 쌍체 부… | 하나의 공유 한국어 코퍼스, 형태소 분절을 위한 Mecab-Ko 또는 Kiwi, 그리고 KLUE, KorQuAD, NSMC와 잡음이 섞인 리뷰… | G3 [1, 3, 5] |
| 4 | 영어 중심 LLM에서 추가 어휘 크기, 임베딩 초기화, 동결 일정, 학습 토큰 예산은 각각 한국어 인코딩 효율과 과제 정확도에 얼마나 기여하는가? | 기준선(10k개 추가 토큰, 하위 단어 평균 초기화, 단계적 동결, 2B 토큰)을 중심으로 한 번에 한 요인씩 바꾸는 설계를 사용하여, 어휘 크기(3수준), 초기화(대안 1개),… | 7-10B 규모의 오픈 LLM, 한국어 지속 사전학습 코퍼스(약 0.5-4B 토큰), 그리고 토큰 길이 비율을 측정하기 위한 한영 병렬 텍스트. | G4 [2, 6, 31] |
| 5 | 한국어 사용자 생성 텍스트의 띄어쓰기 오류, 오타, 속어 상황에서 자모 수준 또는 음절 패턴 인식 토크나이저가 BPE와 형태소+BPE보다 더 잘 버티는가? | BPE, 형태소+BPE, 음절 수준, 자모 수준 토크나이저를 사용하는 동등한 PLM을 감성 분석과 NER에서 미세조정하고, 깨끗한 텍스트와 10/20/30% 비율의 인위적 띄어쓰… | NSMC, KLUE-NER, 그리고 새로 수집한 약 3,000건의 커뮤니티 또는 리뷰 게시물 주석 세트에 잡음을 프로그램적으로 주입한 데이터. | G5 [5, 8, 20] |

## 7. 한계와 신뢰도

- 전문이 아니라 초록과 메타데이터만 읽었기 때문에 효과 크기, 표본 크기, 하이퍼파라미터, 실험 통제를 검증할 수 없었으며, 주장은 저자들이 초록에 보고하기로 선택한 내용에 의존한다.

- 품질 관문(quality gate)은 두 차례 재계획 후에도 rq4(내재적 지표 대 하위 점수)와 rq3(어휘 크기/구성)가 한국어에 대해 사실상 답해지지 않았다고 평가했다. 상관관계와 어휘 크기 근거는 터키어, 유럽 언어, 영어 중심 연구에서 나오므로 한국어로의 전이는 검증되지 않았다.

- rq1/rq2에 대한 직접적인 한국어 근거는 서로 다른 과제, 도메인, 어휘를 사용한 신뢰도 중간 수준의 소수 연구로, 대부분 단일 과제(MT/NLU 벤치마크, 리뷰 감성)이므로 사전 분절기 대 독립 형태소의 충돌은 교란되어 있으며 이 근거로는 해소할 수 없다.

- 강건성 근거(rq6)는 토크나이저 비교보다는 서로 다른 지표를 쓴 품사 태깅과 NER에서 주로 나오며 여기에는 2002년의 신경망 이전 태거도 포함된다. 잡음이 섞인 사용자 생성 텍스트(오타, 속어)는 거의 다뤄지지 않았고, 어휘 확장 주장(rq5)은 비용이나 생성 품질 자료가 없는 한국어 리더보드 보고서 한 건에 한정된다.

- 검색은 고정된 기간 내에서 OpenAlex와 arXiv로 한정되었으며 397건의 후보 중 93건만 평가되었다. 이 집합에 한국어 절제 실험, KLUE/KoBEST 토크나이저 연구, 한국어 LLM 비용 연구가 없다는 사실이 한국어 학술지나 색인되지 않은 기술 보고서 등 다른 곳에도 존재하지 않음을 의미하지는 않는다.

**품질 게이트가 자동으로 기록한 미해결 항목** (사람이 쓴 것이 아니라 파이프라인 검사 결과다):

- Critic 미해결 — major issue(s) persist after re-search, recorded as limitation: rq4: rq4 has no Korean paper linking intrinsic tokenization metrics to downstream scores: 2502.07057 is Turkish, 2310.08754 is European, 2404.13292 is English-centric, and KLUE (2105.09680) and the Sejong study (1587/transinf.2017edp7085) never connect tokenization metrics to downstream results, so the sub-question passes the count check but is effectively unanswered. | rq3: rq3 is answered for Korean only by tangential papers: an ASR corpus (3390/app10196936), a multi-language OOV study (2197/ipsjjip.29.490) and an EEVE report without efficiency numbers (2402.14714), while the vocabulary-size evidence is Turkish (1145/3578707) or European (2310.08754), so the effect of Korean vocabulary size and composition on sequence length and performance is not actually answered.
## 품질 한눈에

| 검색 후보 | 평가 문헌 | 실존 검증 (DOI/arXiv) | sub-RQ 커버리지 (근거 ≥ 3편) | 출처 있는 claim | 근거 ≥ 2편인 Gap | Critic 판정 / Replan | 품질 게이트 미해결 | 비용 · 시간 |
|---|---|---|---|---|---|---|---|---|
| 397 | 93 | 93/93 (100%) | 6/6 | 11/11 | 5/5 | 3회 / 2회 | 1건 → §7 | $0.76 · 6.7분 |

LLM 없이 코드가 계산한 결정적 지표다 (`cost.json` `checks`). 인용 번호 [n] 은 바로 아래 참고문헌을 가리킨다.


## 참고문헌 (53편)

본문·표에 번호로 인용된 문헌. 모두 검색 도구(OpenAlex·arXiv·Crossref)가 반환한 메타데이터 그대로이며 DOI/arXiv id 로 실존이 확인됐다.

1. Kyubyong Park, Joohong Lee, Seongbo Jang et al. (2020). An Empirical Study of Tokenization Strategies for Various Korean NLP Tasks. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2010.02534
2. Seungduk Kim, Seungtaek L. Choi, Myeongho Jeong (2024). Efficient and Effective Vocabulary Expansion Towards Multilingual Large Language Models. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2402.14714
3. Danbi Cho, Hyunyoung Lee, Seung-Shik Kang (2021). An Empirical Study of Korean Sentence Representation with Various Tokenizations. *Electronics*. https://doi.org/10.3390/electronics10070845
4. Çağrı Toraman, Eyüp Halit Yılmaz, Furkan Şahi̇nuç et al. (2023). Impact of Tokenization on Language Models: An Analysis for Turkish. *ACM Transactions on Asian and Low-Resource Language Information Processing*. https://doi.org/10.1145/3578707
5. Sanghyun Choo, Wonjoon Kim (2023). A study on the evaluation of tokenizer performance in natural language processing. *Applied Artificial Intelligence*. https://doi.org/10.1080/08839514.2023.2175112
6. Aleksandar Petrov, Emanuele La Malfa, Philip H. S. Torr et al. (2023). Language Model Tokenizers Introduce Unfairness Between Languages. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2305.15425
7. Yige Chen, KyungTae Lim, Jungyeul Park (2023). Korean named entity recognition based on language-specific features. *Natural Language Engineering*. https://doi.org/10.1017/s1351324923000311
8. Cheoneum Park, Juae Kim (2023). Robust Multi-task Learning-based Korean POS Tagging to Overcome Word Spacing Errors. *ACM Transactions on Asian and Low-Resource Language Information Processing*. https://doi.org/10.1145/3591206
9. Sangwhan Moon, Naoaki Okazaki (2021). Effects and Mitigation of Out-of-vocabulary in Universal Language Models. *Journal of Information Processing*. https://doi.org/10.2197/ipsjjip.29.490
10. Mehdi Ali, Michael Fromm, Klaudia Thellmann et al. (2023). Tokenizer Choice For LLM Training: Negligible or Crucial?. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2310.08754
11. Sungjoon Park, Jihyung Moon, Sungdong Kim et al. (2021). KLUE: Korean Language Understanding Evaluation. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2105.09680
12. Sabrina J. Mielke, Zaid Alyafeai, Elizabeth Salesky et al. (2021). Between words and characters: A Brief History of Open-Vocabulary Modeling and Tokenization in NLP. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2112.10508
13. Ali Erkan, Tunga Güngör (2023). Analysis of Deep Learning Model Combinations and Tokenization Approaches in Sentiment Classification. *IEEE Access*. https://doi.org/10.1109/access.2023.3337354
14. Quang-Phuoc Nguyen, Anh-Dung Vo, Joon-Choul Shin et al. (2019). Korean-Vietnamese Neural Machine Translation System With Korean Morphological Analysis and Word Sense Disambiguation. *IEEE Access*. https://doi.org/10.1109/access.2019.2902270
15. Gary Geunbae Lee, Jeong-Won Cha, Jong-Hyeok Lee (2002). Syllable-Pattern-Based Unknown-Morpheme Segmentation and Estimation for Hybrid Part-of-Speech Tagging of Korean. *Computational Linguistics*. https://doi.org/10.1162/089120102317341774
16. Seung‐Hoon Na, Young-Kil Kim (2018). Phrase-Based Statistical Model for Korean Morpheme Segmentation and POS Tagging. *IEICE Transactions on Information and Systems*. https://doi.org/10.1587/transinf.2017edp7085
17. Khuyagbaatar Batsuren, Ekaterina Vylomova, Verna Dankers et al. (2024). Evaluating Subword Tokenization: Alien Subword Composition and OOV Generalization Challenge. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2404.13292
18. Young-Min Kim, Tae‐Hoon Lee (2020). Korean clinical entity recognition from diagnosis text using BERT. *BMC Medical Informatics and Decision Making*. https://doi.org/10.1186/s12911-020-01241-8
19. Ualsher Tukeyev, Bekarys Rysbek (2026). Morphology-Aware Segmentation and Tokenization for Turkic Languages: A CSE-Guided Framework (The Kazakh Case). *Information*. https://doi.org/10.3390/info17020128
20. Chenglei Si, Zhengyan Zhang, Yingfa Chen et al. (2023). Sub-Character Tokenization for Chinese Pretrained Language Models. *Transactions of the Association for Computational Linguistics*. https://doi.org/10.1162/tacl_a_00560
21. Yi Tay, Vinh Q. Tran, Sebastian Ruder et al. (2021). Charformer: Fast Character Transformers via Gradient-based Subword Tokenization. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2106.12672
22. Jonathan H. Clark, Dan Garrette, Iulia Turc et al. (2022). Canine : Pre-training an Efficient Tokenization-Free Encoder for Language Representation. *Transactions of the Association for Computational Linguistics*. https://doi.org/10.1162/tacl_a_00448
23. Junxiong Wang, Tushaar Gangavarapu, Jing Nathan Yan et al. (2024). MambaByte: Token-free Selective State Space Model. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2401.13660
24. Edo Dotan, Gal Jaschek, Tal Pupko et al. (2024). Effect of tokenization on transformers for biological sequences. *Bioinformatics*. https://doi.org/10.1093/bioinformatics/btae196
25. Wei, Junqiu, Liu, Qun, Yinpeng Guo et al. (2021). Training Multilingual Pre-trained Language Model with Byte-level Subwords. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2101.09469
26. Yoojoong Kim, Jong-Ho Kim, Jeong Moon Lee et al. (2022). A pre-trained BERT for Korean medical natural language processing. *Scientific Reports*. https://doi.org/10.1038/s41598-022-17806-8
27. Yeong Hyeon Gu, Xianghua Piao, Helin Yin et al. (2022). Domain-Specific Language Model Pre-Training for Korean Tax Law Classification. *IEEE Access*. https://doi.org/10.1109/access.2022.3164098
28. Jeong‐Uk Bang, Seung Yun, Seunghi Kim et al. (2020). KsponSpeech: Korean Spontaneous Speech Corpus for Automatic Speech Recognition. *Applied Sciences*. https://doi.org/10.3390/app10196936
29. Orevaoghene Ahia, Sachin Kumar, Hila Gonen et al. (2023). Do All Languages Cost the Same? Tokenization in the Era of Commercial Language Models. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2305.13707
30. Bayram, M. Ali, Ali Arda Fincan, Ahmet Semih Gümüş et al. (2025). Tokenization Standards for Linguistic Integrity: Turkish as a Benchmark. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2502.07057
31. Yiming Cui, Ziqing Yang, Xin Yao (2023). Efficient and Effective Text Encoding for Chinese LLaMA and Alpaca. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2304.08177
32. Scao, Teven Le, Fan, Angela, Akiki, Christopher et al. (2023). BLOOM: A 176B-Parameter Open-Access Multilingual Language Model. *HAL (Le Centre pour la Communication Scientifique Directe)*. https://doi.org/10.4230/oasics.commit2data.3
33. Fangxiaoyu Feng, Yinfei Yang, Daniel M. Cer et al. (2020). Language-agnostic BERT Sentence Embedding. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2007.01852
34. Telmo Pires, Eva Schlinger, Dan Garrette (2019). How multilingual is Multilingual BERT?. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.1906.01502
35. Myung Gyo Oh, Leo Hyun Park, Jaeuk Kim et al. (2023). Membership Inference Attacks With Token-Level Deduplication on Korean Language Models. *IEEE Access*. https://doi.org/10.1109/access.2023.3239668
36. Daniil Maksymenko, Oleksii Turuta (2025). Tokenization efficiency of current foundational large language models for the Ukrainian language. *Frontiers in Artificial Intelligence*. https://doi.org/10.3389/frai.2025.1538165
37. Guy Kaplan, Matanel Oren, Yuval Reif et al. (2024). From Tokens to Words: On the Inner Lexicon of LLMs. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2410.05864
38. Libo Qin, Qiguang Chen, Yuhang Zhou et al. (2025). A survey of multilingual large language models. *Patterns*. https://doi.org/10.1016/j.patter.2024.101118
39. Youngtae Kim, Dong-Yul Ra, Soojong Lim (2020). Zero‐anaphora resolution in Korean based on deep language representation model: BERT. *ETRI Journal*. https://doi.org/10.4218/etrij.2019-0441
40. Tsai, Henry, Jason Riesa, Melvin Johnson et al. (2019). Small and Practical BERT Models for Sequence Labeling. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.1909.00100
41. Dang Van Thin, Duong Ngoc Hao, Ngan Luu-Thuy Nguyen (2023). Vietnamese Sentiment Analysis: An Overview and Comparative Study of Fine-tuning Pretrained Language Models. *ACM Transactions on Asian and Low-Resource Language Information Processing*. https://doi.org/10.1145/3589131
42. Jiyeon Ham, Yo Joong Choe, Kyubyong Park et al. (2020). KorNLI and KorSTS: New Benchmark Datasets for Korean Natural Language Understanding. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2004.03289
43. Alexius Wadell, Anoushka Bhutani, Venkatasubramanian Viswanathan (2026). Tokenization for Molecular Foundation Models. *Journal of Chemical Information and Modeling*. https://doi.org/10.1021/acs.jcim.5c01856
44. Oleh Shliazhko, Alena Fenogenova, Maria Tikhonova et al. (2024). mGPT: Few-Shot Learners Go Multilingual. *Transactions of the Association for Computational Linguistics*. https://doi.org/10.1162/tacl_a_00633
45. Yerai Doval, Jesús Vilares, Carlos Gómez‐Rodríguez (2020). Towards Robust Word Embeddings for Noisy Texts. *Applied Sciences*. https://doi.org/10.3390/app10196893
46. Yunjin Yum, Jeong Moon Lee, Moon Joung Jang et al. (2021). A Word Pair Dataset for Semantic Similarity and Relatedness in Korean Medical Vocabulary: Reference Development and Validation. *JMIR Medical Informatics*. https://doi.org/10.2196/29667
47. Katikapalli Subramanyam Kalyan, Ajit Rajasekharan, S. Sangeetha (2021). AMMUS : A Survey of Transformer-based Pretrained Models in Natural Language Processing. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2108.05542
48. Zuchao Li, Kevin Parnow, Hai  Yan Zhao et al. (2021). Cross-lingual Transferring of Pre-trained Contextualized Language Models. *arXiv (Cornell University)*. https://doi.org/10.48550/arxiv.2107.12627
49. Zhou Chen, Ming Lin, Zimeng Wang et al. (2024). PreparedLLM: effective pre -pretraining framework for domain-specific large language models. *Big Earth Data*. https://doi.org/10.1080/20964471.2024.2396159
50. Dimitris Spathis, Fahim Kawsar (2024). The first step is the hardest: pitfalls of representing and tokenizing temporal data for large language models. *Journal of the American Medical Informatics Association*. https://doi.org/10.1093/jamia/ocae090
51. Myunghoon Lee, Hyeonho Shin, Dabin Lee et al. (2021). Korean Grammatical Error Correction Based on Transformer with Copying Mechanisms and Grammatical Noise Implantation Methods. *Sensors*. https://doi.org/10.3390/s21082658
52. Hyejeong Ahn (2018). Modelling the Englishization of vocabulary in contemporary Korean. *World Englishes*. https://doi.org/10.1111/weng.12345
53. Jungkook An, Hee‐Woong Kim (2015). Building a Korean Sentiment Lexicon Using Collective Intelligence. *Journal of Intelligence and Information Systems*. https://doi.org/10.13088/jiis.2015.21.2.49
