# Research Brief: 한국어 토크나이징 방법 개선

> RQ — How can Korean tokenization methods be improved to yield better tokenization quality and downstream NLP performance than existing approaches?

## 요약

397편의 후보 중 93편을 평가했으며, 한국어에 직접 해당하는 근거는 중간 신뢰도의 실증 연구 소수(주로 단일 과제)로 한정되고 효과 크기는 알 수 없다. 합의된 점은 형태소 사전 분절 후 서브워드 학습(morpheme+BPE)이 한국어 NLU·MT 과제 대부분에서 가장 강하고, 서브워드 단위가 단어·형태소 단위보다 OOV에 강건하다는 것이다. 터키어 등 형태소가 풍부한 언어의 연구도 이를 간접적으로 뒷받침한다. 다만 서브워드로도 CJK의 OOV 문제는 사라지지 않으며, 음절 단위 모델링이나 음절 패턴 기반 미등록어 추정이 띄어쓰기 오류와 미등록 형태소에 강건하다는 태깅 연구가 있다. 상충하는 지점은 형태소 분절이 사전 분절기로 쓰일 때와 독립 토크나이저로 쓰일 때의 결과가 다르다는 것이며, 과제·도메인·어휘 조건이 제각각이라 교란되어 있다(KorQuAD에서는 plain BPE가 우세, 리뷰 감성 분석에서는 독립 형태소 토큰이 열세). 핵심 Gap은 첫째, 한국어에서 fertility·형태소 경계 정렬·OOV rate 같은 내재적 지표를 KLUE·KoBEST 등 하위 과제 성능과 연결한 연구를 찾지 못했다는 점이다. 둘째, 어휘 크기와 단일언어/다국어 구성의 영향, 그리고 어휘 확장(EEVE)의 효율 효과가 한국어에서는 검증되지 않았다(리더보드 성능만 보고됨). 노이즈 텍스트 강건성과 자모 단위 토크나이저 비교도 비어 있다.

## 먼저 읽을 문헌 (10편)

Evaluator 의 관련성(rel)·신뢰도(reli) 점수 순. 전체 평가 표는 §3, 서지 정보는 참고문헌.

| # | 문헌 | 핵심 결과 | sub-RQ | rel · reli |
|---|---|---|---|---|
| [1] | An Empirical Study of Tokenization Strategies for Various Korean NLP Tasks (2020) | Morphological segmentation followed by BPE works best for Korean-English MT and for the NLU tasks KorNLI, KorSTS, NSMC and PAWS-X. Plain BPE is best for KorQuA… | rq1, rq2, rq4 | 5 · 4 |
| [2] | Efficient and Effective Vocabulary Expansion Towards Multilingual Large Languag… (2024) | EEVE vocabulary expansion with parameter freezing and subword initialization boosts Korean proficiency of English-centric LLMs with only about 2B tokens. The m… | rq5, rq3 | 5 · 3 |
| [3] | An Empirical Study of Korean Sentence Representation with Various Tokenizations (2021) | Subword units are more robust to OOV problems than other token units. Replacing whitespace with a particular symbol was a disadvantage in sentiment analysis. | rq1, rq2, rq6 | 5 · 3 |
| [4] | Impact of Tokenization on Language Models: An Analysis for Turkish (2023) | A morphological-level tokenizer performs competitively with de facto tokenizers on Turkish. Larger vocabularies help morphological- and word-level tokenizers m… | rq1, rq3, rq2 | 4 · 4 |
| [5] | A study on the evaluation of tokenizer performance in natural language processi… (2023) | SentencePiece outperformed Mecab-Ko for sentiment classification, especially with ANN and LSTM-RNN. SentencePiece can also assign meaning to short words and ja… | rq1, rq2, rq6 | 4 · 3 |
| [6] | Language Model Tokenizers Introduce Unfairness Between Languages (2023) | The same text translated into different languages can have tokenization lengths differing by up to 15 times, even with multilingual tokenizers, and byte- and c… | rq3, rq5, rq2 | 4 · 3 |
| [7] | Korean named entity recognition based on language-specific features (2023) | Proposes a morpheme-based CoNLL-U annotation scheme for Korean NER that separates functional morphemes such as postpositions and particles, reducing NE ambigui… | rq2, rq4, rq1 | 4 · 3 |
| [8] | Robust Multi-task Learning-based Korean POS Tagging to Overcome Word Spacing Er… (2023) | A syllable-level multi-task POS tagger is robust to Korean word spacing errors and reaches 98.30 F1 on the Sejong test set, better than previous studies. | rq6, rq4, rq1 | 4 · 3 |
| [9] | Effects and Mitigation of Out-of-vocabulary in Universal Language Models (2021) | OOV remains a problem under subword tokenization in CJK languages including Korean and hurts downstream transfer learning. The authors propose a mitigation app… | rq3, rq6 | 4 · 3 |
| [10] | Tokenizer Choice For LLM Training: Negligible or Crucial? (2023) | Tokenizer choice significantly affects downstream performance and training cost, and fertility and parity are not always predictive of downstream performance.… | rq3, rq4 | 3 · 4 |

## 1. 주제 재정의

- RQ: How can Korean tokenization methods be improved to yield better tokenization quality and downstream NLP performance than existing approaches?
- 독립변수: improved Korean tokenization method (e.g., morpheme-aware or modified subword segmentation)
- 종속변수: tokenization quality, downstream NLP task performance, vocabulary efficiency (token count, sequence length)
- 대상: Korean-language text corpora and Korean NLP models
- 핵심 개념: Korean tokenization, morphological analysis, subword tokenization, byte-pair encoding, agglutinative language, Korean natural language processing, vocabulary design

## 2. 조사 계획

전략: Search 2016–present, with emphasis on 2019 onward, covering the transformer and LLM era, using OpenAlex and arXiv, and ACL Anthology-type venues surfaced through them. Prefer empirical studies with comparative baselines on Korean benchmarks (e.g., KLUE, NSMC, KorQuAD) and tokenization analyses; exclude papers that are only about Chinese or Japanese segmentation unless they offer transferable methods for agglutinative languages. I expect rq4 (intrinsic evaluation of Korean tokenization) and rq6 (robustness) to be the thinnest in the literature.}

- **rq1** How do morpheme-aware tokenization methods, including hybrid morphological analysis plus subword approaches, compare with purely statistical subword tokenizers on Korean downstream NLP task performance?

- **rq2** How do standard subword algorithms (BPE, WordPiece, SentencePiece unigram, byte-level) behave on Korean agglutinative morphology and Hangul script, and what modifications to them have been proposed?

- **rq3** How do vocabulary design choices (vocabulary size, composition, multilingual vs. monolingual vocabularies) affect Korean token efficiency, sequence length and model performance?

- **rq4** What intrinsic metrics and evaluation protocols are used to assess Korean tokenization quality, and how well do they correlate with downstream performance?

- **rq5** How are tokenization improvements for Korean adapted in large language models, including tokenizer replacement or vocabulary extension in pre-trained models and the effects on cost and generation quality?

- **rq6** What robustness issues and unintended effects do Korean tokenizers exhibit, such as handling of spacing errors, noisy user-generated text, out-of-vocabulary words, and rare morphological forms?

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

#### rq1 — How do morpheme-aware tokenization methods, including hybrid morphological analysis plus subword approaches, compare with purely statistical subword tokenizers on Korean downstream NLP task performance?

15편 (rel ≥ 3: 14편) · 신뢰도 평균 3.2 · 상위: [1] An Empirical Study of Tokenization Strategies for Various K… (2020) (reli 4); [3] An Empirical Study of Korean Sentence Representation with V… (2021) (reli 3); [4] Impact of Tokenization on Language Models: An Analysis for… (2023) (reli 4)

<details><summary>전체 표 (15편)</summary>

| # | 문헌 | rel | reli | method | sample | finding |
|---|---|---|---|---|---|---|
| [1] | An Empirical Study of Tokenization Strategies for Various Korean NLP… (2020) | 5 | 4 | empirical comparison of tokenization strategies on Korean-English MT and NLU ta… | KorNLI, KorSTS, NSMC, PAWS-X, KorQuAD, Korean-English MT | Morphological segmentation followed by BPE works best for Korean-English MT and for the NLU tasks KorNLI, KorSTS, NSMC and PAWS-X. Plain BPE is best for KorQuA… |
| [3] | An Empirical Study of Korean Sentence Representation with Various Tok… (2021) | 5 | 3 | empirical comparison of word, morpheme, subword, and submorpheme tokenizations… |  | Subword units are more robust to OOV problems than other token units. Replacing whitespace with a particular symbol was a disadvantage in sentiment analysis. |
| [4] | Impact of Tokenization on Language Models: An Analysis for Turkish (2023) | 4 | 4 | empirical comparison of five tokenizers by pretraining RoBERTa-style models and… | Turkish split of OSCAR corpus; six downstream tasks | A morphological-level tokenizer performs competitively with de facto tokenizers on Turkish. Larger vocabularies help morphological- and word-level tokenizers m… |
| [5] | A study on the evaluation of tokenizer performance in natural languag… (2023) | 4 | 3 | comparative experiment of Mecab-Ko vs SentencePiece with five classifiers (NB,… | Korean online customer reviews | SentencePiece outperformed Mecab-Ko for sentiment classification, especially with ANN and LSTM-RNN. SentencePiece can also assign meaning to short words and ja… |
| [7] | Korean named entity recognition based on language-specific features (2023) | 4 | 3 | corpus annotation scheme and conversion algorithm, with experiments using tradi… |  | Proposes a morpheme-based CoNLL-U annotation scheme for Korean NER that separates functional morphemes such as postpositions and particles, reducing NE ambigui… |
| [8] | Robust Multi-task Learning-based Korean POS Tagging to Overcome Word… (2023) | 4 | 3 | multi-task learning neural model (ELECTRA + RNN-CRF) with syllable-level I/O, e… | Sejong corpus test set | A syllable-level multi-task POS tagger is robust to Korean word spacing errors and reaches 98.30 F1 on the Sejong test set, better than previous studies. |
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

#### rq2 — How do standard subword algorithms (BPE, WordPiece, SentencePiece unigram, byte-level) behave on Korean agglutinative morphology and Hangul script, and what modifications to them have been proposed?

16편 (rel ≥ 3: 9편) · 신뢰도 평균 3.4 · 상위: [1] An Empirical Study of Tokenization Strategies for Various K… (2020) (reli 4); [3] An Empirical Study of Korean Sentence Representation with V… (2021) (reli 3); [4] Impact of Tokenization on Language Models: An Analysis for… (2023) (reli 4)

<details><summary>전체 표 (16편)</summary>

| # | 문헌 | rel | reli | method | sample | finding |
|---|---|---|---|---|---|---|
| [1] | An Empirical Study of Tokenization Strategies for Various Korean NLP… (2020) | 5 | 4 | empirical comparison of tokenization strategies on Korean-English MT and NLU ta… | KorNLI, KorSTS, NSMC, PAWS-X, KorQuAD, Korean-English MT | Morphological segmentation followed by BPE works best for Korean-English MT and for the NLU tasks KorNLI, KorSTS, NSMC and PAWS-X. Plain BPE is best for KorQuA… |
| [3] | An Empirical Study of Korean Sentence Representation with Various Tok… (2021) | 5 | 3 | empirical comparison of word, morpheme, subword, and submorpheme tokenizations… |  | Subword units are more robust to OOV problems than other token units. Replacing whitespace with a particular symbol was a disadvantage in sentiment analysis. |
| [4] | Impact of Tokenization on Language Models: An Analysis for Turkish (2023) | 4 | 4 | empirical comparison of five tokenizers by pretraining RoBERTa-style models and… | Turkish split of OSCAR corpus; six downstream tasks | A morphological-level tokenizer performs competitively with de facto tokenizers on Turkish. Larger vocabularies help morphological- and word-level tokenizers m… |
| [5] | A study on the evaluation of tokenizer performance in natural languag… (2023) | 4 | 3 | comparative experiment of Mecab-Ko vs SentencePiece with five classifiers (NB,… | Korean online customer reviews | SentencePiece outperformed Mecab-Ko for sentiment classification, especially with ANN and LSTM-RNN. SentencePiece can also assign meaning to short words and ja… |
| [6] | Language Model Tokenizers Introduce Unfairness Between Languages (2023) | 4 | 3 | empirical comparison of tokenization lengths across languages |  | The same text translated into different languages can have tokenization lengths differing by up to 15 times, even with multilingual tokenizers, and byte- and c… |
| [7] | Korean named entity recognition based on language-specific features (2023) | 4 | 3 | corpus annotation scheme and conversion algorithm, with experiments using tradi… |  | Proposes a morpheme-based CoNLL-U annotation scheme for Korean NER that separates functional morphemes such as postpositions and particles, reducing NE ambigui… |
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

#### rq3 — How do vocabulary design choices (vocabulary size, composition, multilingual vs. monolingual vocabularies) affect Korean token efficiency, sequence length and model performance?

22편 (rel ≥ 3: 10편) · 신뢰도 평균 3.4 · 상위: [2] Efficient and Effective Vocabulary Expansion Towards Multil… (2024) (reli 3); [4] Impact of Tokenization on Language Models: An Analysis for… (2023) (reli 4); [9] Effects and Mitigation of Out-of-vocabulary in Universal La… (2021) (reli 3)

<details><summary>전체 표 (22편)</summary>

| # | 문헌 | rel | reli | method | sample | finding |
|---|---|---|---|---|---|---|
| [2] | Efficient and Effective Vocabulary Expansion Towards Multilingual Lar… (2024) | 5 | 3 | technical report with vocabulary expansion method (parameter freezing, subword… | EEVE-Korean-10.8B built on SOLAR-10.7B; trained with about… | EEVE vocabulary expansion with parameter freezing and subword initialization boosts Korean proficiency of English-centric LLMs with only about 2B tokens. The m… |
| [4] | Impact of Tokenization on Language Models: An Analysis for Turkish (2023) | 4 | 4 | empirical comparison of five tokenizers by pretraining RoBERTa-style models and… | Turkish split of OSCAR corpus; six downstream tasks | A morphological-level tokenizer performs competitively with de facto tokenizers on Turkish. Larger vocabularies help morphological- and word-level tokenizers m… |
| [9] | Effects and Mitigation of Out-of-vocabulary in Universal Language Mod… (2021) | 4 | 3 | empirical study of OOV effects in transfer learning with a proposed mitigation… | pre-trained language models for CJK languages (sizes not st… | OOV remains a problem under subword tokenization in CJK languages including Korean and hurts downstream transfer learning. The authors propose a mitigation app… |
| [6] | Language Model Tokenizers Introduce Unfairness Between Languages (2023) | 4 | 3 | empirical comparison of tokenization lengths across languages |  | The same text translated into different languages can have tokenization lengths differing by up to 15 times, even with multilingual tokenizers, and byte- and c… |
| [10] | Tokenizer Choice For LLM Training: Negligible or Crucial? (2023) | 3 | 4 | controlled ablation training 24 mono- and multilingual LLMs at 2.6B parameters | 24 LLMs; European languages | Tokenizer choice significantly affects downstream performance and training cost, and fertility and parity are not always predictive of downstream performance.… |
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

#### rq4 — What intrinsic metrics and evaluation protocols are used to assess Korean tokenization quality, and how well do they correlate with downstream performance?

15편 (rel ≥ 3: 8편) · 신뢰도 평균 3.2 · 상위: [1] An Empirical Study of Tokenization Strategies for Various K… (2020) (reli 4); [7] Korean named entity recognition based on language-specific… (2023) (reli 3); [8] Robust Multi-task Learning-based Korean POS Tagging to Over… (2023) (reli 3)

<details><summary>전체 표 (15편)</summary>

| # | 문헌 | rel | reli | method | sample | finding |
|---|---|---|---|---|---|---|
| [1] | An Empirical Study of Tokenization Strategies for Various Korean NLP… (2020) | 5 | 4 | empirical comparison of tokenization strategies on Korean-English MT and NLU ta… | KorNLI, KorSTS, NSMC, PAWS-X, KorQuAD, Korean-English MT | Morphological segmentation followed by BPE works best for Korean-English MT and for the NLU tasks KorNLI, KorSTS, NSMC and PAWS-X. Plain BPE is best for KorQuA… |
| [7] | Korean named entity recognition based on language-specific features (2023) | 4 | 3 | corpus annotation scheme and conversion algorithm, with experiments using tradi… |  | Proposes a morpheme-based CoNLL-U annotation scheme for Korean NER that separates functional morphemes such as postpositions and particles, reducing NE ambigui… |
| [8] | Robust Multi-task Learning-based Korean POS Tagging to Overcome Word… (2023) | 4 | 3 | multi-task learning neural model (ELECTRA + RNN-CRF) with syllable-level I/O, e… | Sejong corpus test set | A syllable-level multi-task POS tagger is robust to Korean word spacing errors and reaches 98.30 F1 on the Sejong test set, better than previous studies. |
| [11] | KLUE: Korean Language Understanding Evaluation (2021) | 3 | 4 | benchmark construction (8 Korean NLU tasks) with PLM baseline experiments | 8 Korean NLU tasks built from scratch | KLUE offers a Korean NLU benchmark, along with KLUE-BERT and KLUE-RoBERTa models. KLUE-RoBERTa-large outperforms the other baselines, including multilingual PL… |
| [10] | Tokenizer Choice For LLM Training: Negligible or Crucial? (2023) | 3 | 4 | controlled ablation training 24 mono- and multilingual LLMs at 2.6B parameters | 24 LLMs; European languages | Tokenizer choice significantly affects downstream performance and training cost, and fertility and parity are not always predictive of downstream performance.… |
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

#### rq5 — How are tokenization improvements for Korean adapted in large language models, including tokenizer replacement or vocabulary extension in pre-trained models and the effects on cost and generation quality?

15편 (rel ≥ 3: 4편) · 신뢰도 평균 3.0 · 상위: [2] Efficient and Effective Vocabulary Expansion Towards Multil… (2024) (reli 3); [6] Language Model Tokenizers Introduce Unfairness Between Lang… (2023) (reli 3); [29] Do All Languages Cost the Same? Tokenization in the Era of… (2023) (reli 4)

<details><summary>전체 표 (15편)</summary>

| # | 문헌 | rel | reli | method | sample | finding |
|---|---|---|---|---|---|---|
| [2] | Efficient and Effective Vocabulary Expansion Towards Multilingual Lar… (2024) | 5 | 3 | technical report with vocabulary expansion method (parameter freezing, subword… | EEVE-Korean-10.8B built on SOLAR-10.7B; trained with about… | EEVE vocabulary expansion with parameter freezing and subword initialization boosts Korean proficiency of English-centric LLMs with only about 2B tokens. The m… |
| [6] | Language Model Tokenizers Introduce Unfairness Between Languages (2023) | 4 | 3 | empirical comparison of tokenization lengths across languages |  | The same text translated into different languages can have tokenization lengths differing by up to 15 times, even with multilingual tokenizers, and byte- and c… |
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

#### rq6 — What robustness issues and unintended effects do Korean tokenizers exhibit, such as handling of spacing errors, noisy user-generated text, out-of-vocabulary words, and rare morphological forms?

16편 (rel ≥ 3: 9편) · 신뢰도 평균 3.2 · 상위: [3] An Empirical Study of Korean Sentence Representation with V… (2021) (reli 3); [5] A study on the evaluation of tokenizer performance in natur… (2023) (reli 3); [9] Effects and Mitigation of Out-of-vocabulary in Universal La… (2021) (reli 3)

<details><summary>전체 표 (16편)</summary>

| # | 문헌 | rel | reli | method | sample | finding |
|---|---|---|---|---|---|---|
| [3] | An Empirical Study of Korean Sentence Representation with Various Tok… (2021) | 5 | 3 | empirical comparison of word, morpheme, subword, and submorpheme tokenizations… |  | Subword units are more robust to OOV problems than other token units. Replacing whitespace with a particular symbol was a disadvantage in sentiment analysis. |
| [5] | A study on the evaluation of tokenizer performance in natural languag… (2023) | 4 | 3 | comparative experiment of Mecab-Ko vs SentencePiece with five classifiers (NB,… | Korean online customer reviews | SentencePiece outperformed Mecab-Ko for sentiment classification, especially with ANN and LSTM-RNN. SentencePiece can also assign meaning to short words and ja… |
| [9] | Effects and Mitigation of Out-of-vocabulary in Universal Language Mod… (2021) | 4 | 3 | empirical study of OOV effects in transfer learning with a proposed mitigation… | pre-trained language models for CJK languages (sizes not st… | OOV remains a problem under subword tokenization in CJK languages including Korean and hurts downstream transfer learning. The authors propose a mitigation app… |
| [8] | Robust Multi-task Learning-based Korean POS Tagging to Overcome Word… (2023) | 4 | 3 | multi-task learning neural model (ELECTRA + RNN-CRF) with syllable-level I/O, e… | Sejong corpus test set | A syllable-level multi-task POS tagger is robust to Korean word spacing errors and reaches 98.30 F1 on the Sejong test set, better than previous studies. |
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

- Morphological pre-segmentation followed by subword learning is the strongest option on most Korean NLU and MT tasks tested, and subword units beat word- or morpheme-level units on OOV robustness; the Korean evidence is two moderate-reliability empirical studies, so the effect sizes are unknown. [1, 3] (근거 2편 · 신뢰도 평균 3.5)

- Outside Korean, morphology-aware tokenization is competitive with or better than standard tokenizers on morphologically rich languages (Turkish) and generalizes better to OOV words (English-centric models); this is indirect support for Korean. [4, 17] (근거 2편 · 신뢰도 평균 3.5)

- Subword tokenization does not eliminate OOV problems for Korean and other CJK languages, and OOV hurts transfer learning; Korean-specific handling such as syllable-level modeling or syllable-pattern estimation of unknown morphemes keeps tagging accuracy high under spacing errors and unknown morphemes (97-98 points). [8, 9, 15] (근거 3편 · 신뢰도 평균 3.0)

- The same content can need many times more tokens in some languages than in others, even with multilingual tokenizers, implying unequal API cost, latency and context capacity; the abstracts do not single out Korean. [6, 29] (근거 2편 · 신뢰도 평균 3.5)

- Vocabulary extension of an English-centric LLM improves target-language proficiency with modest continued training. For Korean, the evidence is leaderboard proficiency from EEVE (about 2B training tokens, no efficiency numbers reported). The encoding-efficiency gain (20,000 added Chinese tokens) is shown only for Chinese LLaMA. [2, 31] (근거 2편 · 신뢰도 평균 3.0)

### 상충

- **Whether morpheme-based segmentation helps or hurts when used as a pre-segmenter versus as a standalone tokenizer for Korean.** (A 1편 vs B 2편)
  - A: Morphological segmentation used as a pre-segmenter before BPE gave the best results on Korean-English MT and four NLU tasks, though plain BPE won on KorQuAD. [1]
  - B: Standalone morpheme-based tokenization lost to learned subwords: SentencePiece beat Mecab-Ko for review sentiment classification, and subword units were more OOV-robust than morpheme units in sentence-embedding sentiment analysis. [3, 5]
  - 원인 가설: The contrasts differ: morphemes feeding BPE keep subword coverage for rare forms, whereas standalone morpheme tokens leave OOVs and jargon in noisy review text. The tasks also differ (MT/NLU benchmarks vs. sentiment on reviews), and the sentiment studies are single-task and single-domain with unstated sample sizes.

### 조건부

- Replacing whitespace with a special symbol hurt Korean sentiment analysis in one study; whether this is task-dependent is untested because only sentiment was evaluated. [3] (근거 1편 · 신뢰도 평균 3.0)

- In Turkish, larger vocabularies helped morphological- and word-level tokenizers more than de facto tokenizers; Korean applicability is untested, so confidence for Korean is low. [4] (근거 1편 · 신뢰도 평균 4.0)

- In controlled European-language experiments, multilingual tokenizers needed roughly three times larger vocabularies than English ones, and fertility and parity did not always predict downstream performance; transfer to Korean is untested. [10] (근거 1편 · 신뢰도 평균 4.0)

- Pronunciation-based sub-character tokenization shortens sequences and resists homophone typos while staying competitive on Chinese PLMs; whether Hangul benefits is not shown. [20] (근거 1편 · 신뢰도 평균 4.0)

### 커버리지 메모

The Korean evidence is thin on rq4: no Korean study links intrinsic metrics such as fertility, boundary alignment or OOV rate to downstream scores, and the correlation evidence is Turkish [30], European [10] and English [17]; KLUE [11] and the Sejong study [16] never connect tokenization metrics to downstream results. rq3 is similarly unanswered for Korean, since the Korean items are an ASR corpus [28], a multi-language OOV paper [9] and a report without efficiency numbers [2]; vocabulary-size evidence is Turkish or European. rq1 and rq2 have the most direct Korean evidence ([1], [3], [5]), but these are moderate-reliability, mostly single-task studies with no effect sizes. rq5 rests on one Korean technical report with leaderboard evaluation plus Chinese and cross-language cost studies. rq6 has spacing and unknown-morpheme evidence from POS tagging and NER but little on noisy user-generated text. Missing are Korean ablations varying vocabulary size and monolingual vs. multilingual vocabularies with tokens-per-character and downstream scores, KLUE/KoBEST tokenizer ablations with intrinsic metrics, and Korean LLM tokenizer cost studies.

## 5. Research Gap

### G1. No Korean study reports intrinsic tokenizer metrics (fertility, morpheme-boundary alignment, OOV rate) next to downstream scores.

[10, 17, 30] (근거 3편 · 신뢰도 평균 3.3)

The correlation evidence comes only from Turkish and European languages, where the metrics predict downstream results inconsistently. Whether any metric predicts Korean downstream performance is unknown.

- 제안 RQ: Which intrinsic tokenizer metrics (fertility, morpheme-boundary F1, OOV rate, token purity) predict KLUE and KoBEST downstream scores across Korean tokenizers?
- 방법: Pretrain about 12 identical small RoBERTa models that differ only in tokenizer (BPE, Unigram, morpheme+BPE, jamo-level, byte-level), fine-tune on KLUE/KoBEST with 3 seeds, and compute rank correlations and mixed-effects regressions of task score on each metric. The main outcome is the correlation between each metric and downstream score, benchmarked against the Turkish %TR result.
- 데이터: Korean corpora such as Modu or Namuwiki/CC-100 Korean (at least 10B characters) and the public KLUE and KoBEST suites. Compute is about 12 pretraining runs at small scale.

### G2. Korean vocabulary design (size, monolingual vs multilingual composition) is unstudied.

[4, 10, 28] (근거 3편 · 신뢰도 평균 4.0)

The vocabulary-size evidence concerns Turkish morphological tokenizers and European multilingual tokenizers, and the only Korean sub-word size analysis is in ASR. Nothing links Korean vocabulary size to tokens per character and downstream accuracy.

- 제안 RQ: How do vocabulary size and monolingual vs multilingual composition affect tokens per Korean character and KLUE accuracy?
- 방법: Run a controlled ablation with vocabulary sizes of 16k, 32k, 64k and 128k, each as a Korean-only and a Korean+English+Chinese+Japanese tokenizer, in 8 pretraining runs at fixed compute. Report tokens per character and KLUE scores, and test a size-by-composition interaction with seeds.
- 데이터: Balanced Korean and multilingual web corpora (e.g., CC-100 or mC4 subsets) plus KLUE. The 8 runs fit a small-model compute budget.

### G3. The pre-segmenter vs standalone morpheme question is confounded across studies.

[1, 3, 5] (근거 3편 · 신뢰도 평균 3.3)

Morpheme+BPE won on MT and NLU while plain BPE won on KorQuAD, but standalone morpheme tokenization lost on sentiment, where each study used different tasks, domains and vocabularies. Whitespace handling was tested only on sentiment.

- 제안 RQ: With vocabulary size and training data fixed, does morpheme pre-segmentation before BPE outperform both standalone morpheme tokens and plain BPE, and does whitespace handling matter outside sentiment?
- 방법: Pretrain 2x3 models (whitespace marker vs none; BPE, morpheme+BPE, standalone morpheme) and fine-tune on a pre-registered suite of NLI, NER, QA, sentiment and MT. Compare pairwise with paired bootstrap, and report per-task effect sizes with a task-by-tokenizer interaction. The KLUE suite serves as the evaluation set only.
- 데이터: One shared Korean corpus, Mecab-Ko or Kiwi for morpheme segmentation, and KLUE, KorQuAD and NSMC, plus a noisy-review test set.

### G4. Korean vocabulary-extension evidence is leaderboard proficiency only, with no efficiency numbers.

[2, 6, 31] (근거 3편 · 신뢰도 평균 3.0)

EEVE reports no tokens-per-character or latency, and the encoding-efficiency gain is shown only for Chinese LLaMA. The roles of added-vocabulary size, initialization, parameter freezing and training-token budget are not separated, and cost disparity is documented across languages without Korean figures.

- 제안 RQ: How much does each of added-vocabulary size, embedding initialization, freezing schedule and training-token budget contribute to Korean encoding efficiency and task accuracy in an English-centric LLM?
- 방법: Use a one-factor-at-a-time design around a baseline (10k added tokens, subword-mean initialization, staged freezing, 2B tokens), varying vocabulary size (3 levels), initialization (1 alternative), freezing (1 alternative) and budget (2 levels) for about 8 runs. Outcomes are tokens per Korean character, inference latency and KoBEST/KMMLU accuracy against the unextended model.
- 데이터: A 7-10B open LLM, Korean continued-pretraining corpora (about 0.5-4B tokens), and parallel Korean-English text to measure token-length ratios.

### G5. Robustness of Korean tokenizers to noisy text and Hangul sub-character units has not been compared.

[5, 8, 20] (근거 3편 · 신뢰도 평균 3.3)

The spacing- and unknown-morpheme-robust taggers are intrinsic tagging studies, not tokenizer comparisons, and the review-text evidence compares only Mecab-Ko with SentencePiece. Pronunciation-based sub-character tokenization is shown only for Chinese.

- 제안 RQ: Do jamo-level or syllable-pattern-aware tokenizers hold up better than BPE and morpheme+BPE under spacing errors, typos and slang in Korean user-generated text?
- 방법: Fine-tune matched PLMs with BPE, morpheme+BPE, syllable-level and jamo-level tokenizers on sentiment and NER, and evaluate on clean text and on test sets with synthetic spacing and typo noise at 10/20/30% rates. Compare accuracy degradation curves between tokenizers.
- 데이터: NSMC, KLUE-NER and a newly collected annotated set of about 3,000 community or review posts, with noise injected programmatically.

## 6. 향후 연구 방향

§5 의 제안을 한 표로 요약했다 (전문은 각 Gap). 근거는 해당 Gap 의 인용을 따른다.

| # | 제안 RQ | 연구 설계 | 데이터 | 근거 Gap |
|---|---|---|---|---|
| 1 | Which intrinsic tokenizer metrics (fertility, morpheme-boundary F1, OOV rate, token purity) predict KLUE and KoBEST downstream scores acros… | Pretrain about 12 identical small RoBERTa models that differ only in tokenizer (BPE, Unigram, morph… | Korean corpora such as Modu or Namuwiki/CC-100 Korean (at least 10B characters)… | G1 [10, 17, 30] |
| 2 | How do vocabulary size and monolingual vs multilingual composition affect tokens per Korean character and KLUE accuracy? | Run a controlled ablation with vocabulary sizes of 16k, 32k, 64k and 128k, each as a Korean-only an… | Balanced Korean and multilingual web corpora (e.g., CC-100 or mC4 subsets) plus… | G2 [4, 10, 28] |
| 3 | With vocabulary size and training data fixed, does morpheme pre-segmentation before BPE outperform both standalone morpheme tokens and plai… | Pretrain 2x3 models (whitespace marker vs none; BPE, morpheme+BPE, standalone morpheme) and fine-tu… | One shared Korean corpus, Mecab-Ko or Kiwi for morpheme segmentation, and KLUE,… | G3 [1, 3, 5] |
| 4 | How much does each of added-vocabulary size, embedding initialization, freezing schedule and training-token budget contribute to Korean enc… | Use a one-factor-at-a-time design around a baseline (10k added tokens, subword-mean initialization,… | A 7-10B open LLM, Korean continued-pretraining corpora (about 0.5-4B tokens), a… | G4 [2, 6, 31] |
| 5 | Do jamo-level or syllable-pattern-aware tokenizers hold up better than BPE and morpheme+BPE under spacing errors, typos and slang in Korean… | Fine-tune matched PLMs with BPE, morpheme+BPE, syllable-level and jamo-level tokenizers on sentimen… | NSMC, KLUE-NER and a newly collected annotated set of about 3,000 community or… | G5 [5, 8, 20] |

## 7. 한계와 신뢰도

- Only abstracts and metadata were read, not full texts, so effect sizes, sample sizes, hyperparameters and experimental controls could not be verified; claims rest on what authors chose to report in abstracts.

- The quality gate rated rq4 (intrinsic metrics vs. downstream scores) and rq3 (vocabulary size/composition) as effectively unanswered for Korean after two replans; the correlation and vocabulary-size evidence comes from Turkish, European-language and English-centric studies, so transfer to Korean is untested.

- The direct Korean evidence for rq1/rq2 is a handful of moderate-reliability, mostly single-task studies (MT/NLU benchmarks, review sentiment) using different tasks, domains and vocabularies, so the pre-segmenter vs. standalone morpheme conflict is confounded and cannot be resolved from this evidence.

- Robustness evidence (rq6) comes mostly from POS tagging and NER with different metrics, including a 2002 pre-neural tagger, rather than tokenizer comparisons; noisy user-generated text (typos, slang) is barely covered, and the vocabulary-extension claim (rq5) is limited to one Korean leaderboard report with no cost or generation-quality data.

- Search was limited to OpenAlex and arXiv within a fixed time window, with 93 of 397 candidates evaluated; absence of Korean ablations, KLUE/KoBEST tokenizer studies or Korean LLM cost studies in this set does not show that they do not exist elsewhere, e.g. in Korean-language venues or non-indexed technical reports.

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
