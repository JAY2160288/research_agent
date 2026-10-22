# Research Brief: AI 기반 이상거래 탐지가 외부감사 품질과 감사 비용에 미치는 영향

> RQ — How does the adoption of AI-based anomaly (fraudulent transaction) detection in external audits affect audit quality and audit costs?

## 요약

후보 403편 중 80편을 평가했으며, 실증 아카이벌 연구 2편, 설문·인터뷰, 문헌 리뷰, 개념 연구, 도구 설명이 섞여 있다. 합의된 점은 감사법인의 AI 투자가 늘수록 고객사 재무제표 재작성(restatement) 가능성이 낮아진다는 것인데(한 연구에서 AI 투자 1 SD당 약 5.0% 감소), 이는 오류 감소와 탐지력 약화를 구분하지 못하는 간접 지표다. 감사 비용 측면에서는 감사보수가 AI 투자 1 SD당 0.9% 낮아졌다는 결과가 있으나, 보수는 가격일 뿐 외부감사 시간·노력은 어떤 연구도 측정하지 않았다. 효율성 증거는 설문, 내부감사 연구, 보고 지연(report lag)에 한정된다. 조건부 결과로는 중국 연구에서 감사인과 고객사가 AI를 함께 쓸 때만 보고 지연이 줄고 따로 쓰면 오히려 늘어난다. 사기 예측 모델은 오탐 대 진탐 비율이 100:1을 넘으면 감사인에게는 비용이 과도하지만 투자자나 규제기관에는 순편익이 있을 수 있다. 다만 이는 전통적 모델 대상이다. 가장 큰 공백은 실제 감사의 분개·거래 수준에서 정밀도·재현율·오탐률을 보고한 연구가 없다는 점과, 외부감사 시간 및 감사인이 AI 경고에 대응하는 방식에 대한 증거가 없다는 점이다. 직업적 회의주의 약화와 윤리·인력·설명가능성 위험은 주로 일반 감사 데이터 분석에 대한 개념·기술(descriptive) 연구에 근거한다.

## 먼저 읽을 문헌 (10편)

Evaluator 의 관련성(rel)·신뢰도(reli) 점수 순. 전체 평가 표는 §3, 서지 정보는 참고문헌.

| # | 문헌 | 핵심 결과 | sub-RQ | rel · reli |
|---|---|---|---|---|
| [1] | Does the adoption of artificial intelligence by audit firms and their clients a… (2024) | When audit firms and clients use AI separately, audit report lag increases. When they use AI together, report lag falls, improving efficiency. AI use is also a… | rq1, rq2, rq4 | 5 · 4 |
| [2] | Is artificial intelligence improving the audit process? (2022) | Greater AI investment by audit firms is associated with improved audit quality, lower fees, and displacement of human auditors. A one-SD increase in AI investm… | rq1, rq2, rq5 | 5 · 4 |
| [3] | The Cost of Fraud Prediction Errors (2021) | Even the best models trade off false to true positives at rates above 100:1. The resulting false positives make all seven models too costly for auditors to imp… | rq3, rq5, rq2 | 5 · 4 |
| [4] | An Analysis on Financial Statement Fraud Detection for Chinese Listed Companies… (2022) | Develops a deep learning fraud detection system using financial and non-financial indices plus text features from MD&A to address class imbalance in financial… | rq3 | 4 · 4 |
| [5] | Application of Artificial Intelligence and Audit Quality in Nigeria (2023) | Expert systems, machine learning and intelligent agents showed significant positive relationships with audit quality in Nigeria. | rq1, rq4 | 4 · 3 |
| [6] | Detecting Anomalies in Financial Data Using Machine Learning Algorithms (2022) | The best supervised and unsupervised models show high potential for detecting predefined anomalies in general ledger journal entries, addressing sampling risk… | rq3, rq2 | 4 · 3 |
| [7] | Auditors' Perception on the Impact of Artificial Intelligence on Professional S… (2021) | Examines auditors' perceptions of how AI/ML affect professional skepticism and judgment and thereby audit efficiency, including influencing factors and challen… | rq4, rq5, rq2 | 4 · 3 |
| [8] | Big Data and changes in audit technology: contemplating a research agenda (2018) | Provides an overview of how big data and analytics change audit practice, covering auditor-client relationships, engagement conduct and challenges in embedding… | rq2, rq4, rq5 | 4 · 3 |
| [9] | Cluster Analysis for Anomaly Detection in Accounting Data: An Audit Approach (2011) | Cluster analysis grouped similar claims and flagged small-population clusters for further investigation, helping auditors focus effort. Flagged clusters were c… | rq3 | 4 · 3 |
| [10] | The application of Artificial Intelligence in external auditing and its implica… (2023) | Explores the role of AI in external auditing and assesses debates, with proponents citing better sampling, efficiency and audit quality and opponents citing et… | rq1, rq2, rq4, rq5 | 4 · 2 |

## 1. 주제 재정의

- RQ: How does the adoption of AI-based anomaly (fraudulent transaction) detection in external audits affect audit quality and audit costs?
- 독립변수: AI-based anomaly detection adoption in external audits
- 종속변수: external audit quality, audit costs (audit fees)
- 대상: External auditors and audit firms (and their audit engagements/clients)
- 핵심 개념: AI-based anomaly detection, fraudulent transaction detection, external audit quality, audit fees, audit efficiency, machine learning in auditing, continuous auditing, audit analytics

## 2. 조사 계획

전략: Cover roughly 2010 to the present, with emphasis on 2016 onward when audit analytics and machine learning adoption accelerated. Prefer archival and empirical studies, experiments, field studies, and systematic reviews in accounting, auditing, and information systems, plus technical fraud detection papers from arXiv for rq3. Exclude papers on internal fraud detection in banking or payments with no audit link, and purely opinion or vendor pieces. The thinnest literature is expected for rq2 (causal evidence on audit fees and costs from AI specifically) and for direct archival evidence on AI and audit quality in rq1.

- **rq1** How does the adoption of AI and machine learning anomaly detection by auditors affect external audit quality, such as misstatement and fraud detection, restatements, and discretionary accruals?

- **rq2** How does the use of AI and audit analytics affect audit fees, audit hours and effort, and audit efficiency?

- **rq3** How accurate and effective are machine learning and anomaly detection techniques at identifying fraudulent transactions and anomalous journal entries in audit settings?

- **rq4** Through which mechanisms and under which conditions (auditor judgment, skepticism, client complexity, firm size, regulation) does AI-based detection change audit outcomes?

- **rq5** What are the adoption drivers, implementation barriers, and risks (false positives, explainability, data quality, liability, regulatory concerns) of AI in external auditing?

<details><summary>검색 쿼리 전체 (26개 — Replan 으로 추가된 쿼리 포함)</summary>

- **rq1** (4개): artificial intelligence adoption audit quality; audit data analytics audit quality restatements; machine learning auditing misstatement detection; technology-enabled auditing fraud detection effectiveness

- **rq2** (4개): audit analytics audit fees effect; artificial intelligence audit efficiency audit hours; big data analytics audit cost reduction; audit fee audit effort technology investment

- **rq3** (7개): journal entry testing machine learning anomaly detection; financial statement fraud detection machine learning; unsupervised anomaly detection accounting transactions audit; deep learning fraudulent journal entries autoencoder; journal entry fraud detection precision recall real ledger data; AAER labelled misstatement prediction ensemble learning out-of-sample; isolation forest outlier detection general ledger audit false positive rate

- **rq4** (7개): auditor judgment reliance on AI tools; professional skepticism audit data analytics; audit firm size technology adoption audit outcomes; algorithm aversion auditors decision support; experimental auditors data analytics professional skepticism evidence evaluation; Big 4 versus non-Big 4 artificial intelligence audit quality; client complexity moderates audit analytics effect on audit outcomes

- **rq5** (4개): barriers to artificial intelligence adoption in auditing; explainable AI audit risks false positives; continuous auditing machine learning implementation challenges; regulatory standards AI audit evidence PCAOB

</details>

## 3. Evidence Table

### 3.1 Evidence map — sub-RQ × 신뢰도

| sub-RQ | 편수 (rel ≥ 3) | 신뢰도 4~5 | 신뢰도 3 | 신뢰도 ≤ 2 | 평균 신뢰도 | 커버 |
|---|---|---|---|---|---|---|
| rq1 | 10 | 4 | 2 | 4 | 3.0 | ✅ |
| rq2 | 10 | 4 | 5 | 1 | 3.3 | ✅ |
| rq3 | 13 | 6 | 6 | 1 | 3.4 | ✅ |
| rq4 | 14 | 3 | 8 | 3 | 3.0 | ✅ |
| rq5 | 19 | 4 | 9 | 6 | 2.9 | ✅ |

커버 기준은 Critic 결정적 검사와 같다 (relevance ≥ 3 인 문헌 3편 이상). 신뢰도는 Evaluator 가 설계·표본·출처로 매긴 0~5 점.

### 3.2 sub-RQ 별 문헌

#### rq1 — How does the adoption of AI and machine learning anomaly detection by auditors affect external audit quality, such as misstatement and fraud detection, restatements, and discretionary accruals?

11편 (rel ≥ 3: 10편) · 신뢰도 평균 3.1 · 상위: [2] Is artificial intelligence improving the audit process? (2022) (reli 4); [1] Does the adoption of artificial intelligence by audit firms… (2024) (reli 4); [5] Application of Artificial Intelligence and Audit Quality in… (2023) (reli 3)

<details><summary>전체 표 (11편)</summary>

| # | 문헌 | rel | reli | method | sample | finding |
|---|---|---|---|---|---|---|
| [2] | Is artificial intelligence improving the audit process? (2022) | 5 | 4 | archival analysis of resume data on AI workers plus interviews with 17 audit pa… | 310,000+ resumes for 36 largest audit firms; 17 audit partn… | Greater AI investment by audit firms is associated with improved audit quality, lower fees, and displacement of human auditors. A one-SD increase in AI investm… |
| [1] | Does the adoption of artificial intelligence by audit firms and their… (2024) | 5 | 4 | archival study with propensity score matching and two-stage OLS | Chinese firms, 2011-2020 | When audit firms and clients use AI separately, audit report lag increases. When they use AI together, report lag falls, improving efficiency. AI use is also a… |
| [5] | Application of Artificial Intelligence and Audit Quality in Nigeria (2023) | 4 | 3 | cross-sectional survey with OLS regression, n=125 | 125 accounting firms in Nigeria applying AI (purposive samp… | Expert systems, machine learning and intelligent agents showed significant positive relationships with audit quality in Nigeria. |
| [10] | The application of Artificial Intelligence in external auditing and i… (2023) | 4 | 2 | qualitative critical review of ongoing debates |  | Explores the role of AI in external auditing and assesses debates, with proponents citing better sampling, efficiency and audit quality and opponents citing et… |
| [11] | Auditing with data and analytics: External reviewers' judgments of au… (2023) | 3 | 4 | two experiments with experienced external reviewers | Experienced external reviewers (size not stated in abstract) | Reviewers rate data and analytics audit procedures as lower quality than traditional ones because they perceive them as less effortful, even at equal assurance… |
| [12] | Financial Statement Fraud Detection: An Analysis of Statistical and M… (2011) | 3 | 4 | empirical comparison of six statistical and ML models for financial statement f… | fraud and nonfraud firms; 42 predictors examined (sample si… | Logistic regression and support vector machines perform well relative to ANN, bagging, C4.5, and stacking at detecting financial statement fraud. Only six of 4… |
| [13] | Artificial intelligence adoption, audit quality and integrated financ… (2024) | 3 | 3 | panel regression (OLS) with propensity score robustness checks | 2,912 non-financial firm-year observations, GCC listed firm… | The study examines whether firm AI adoption improves integrated financial reporting, with audit quality (fees, industry specialization, restatement) as a moder… |
| [14] | Audit data analytics, machine learning, and full population testing (2022) | 3 | 2 | conceptual paper proposing an approach |  | The paper presents an approach for applying audit data analytics and machine learning to full population testing instead of sampling, and discusses related cha… |
| [15] | Current machine learning applications in accounting and auditing (2020) | 3 | 2 | content analysis of Big Four machine learning tools | Machine learning tools and platforms of the Big Four firms | Big Four firms have developed ML tools for audit coordination, automated audits in limited areas such as cash, data analysis, risk assessment and document extr… |
| [16] | AUDITING WITH AI: A THEORETICAL FRAMEWORK FOR APPLYING MACHINE LEARNI… (2024) | 3 | 2 | theoretical framework / conceptual paper drawing on extant literature |  | Proposes a framework for applying ML and data analytics across the internal audit lifecycle, from planning to reporting. It argues auditors need a continuous i… |
| [17] | Abnormal Audit Fees and Audit Quality: Evidence from the Korean Audit… (2020) | 2 | 4 | archival empirical study (regression analysis of audit fees, audit hours and au… | public firms in the Korean audit market | Abnormally low audit fees are associated with larger discretionary accruals and a higher likelihood of meeting or beating analyst forecasts. No significant ass… |

</details>

#### rq2 — How does the use of AI and audit analytics affect audit fees, audit hours and effort, and audit efficiency?

14편 (rel ≥ 3: 10편) · 신뢰도 평균 3.3 · 상위: [2] Is artificial intelligence improving the audit process? (2022) (reli 4); [1] Does the adoption of artificial intelligence by audit firms… (2024) (reli 4); [3] The Cost of Fraud Prediction Errors (2021) (reli 4)

<details><summary>전체 표 (14편)</summary>

| # | 문헌 | rel | reli | method | sample | finding |
|---|---|---|---|---|---|---|
| [2] | Is artificial intelligence improving the audit process? (2022) | 5 | 4 | archival analysis of resume data on AI workers plus interviews with 17 audit pa… | 310,000+ resumes for 36 largest audit firms; 17 audit partn… | Greater AI investment by audit firms is associated with improved audit quality, lower fees, and displacement of human auditors. A one-SD increase in AI investm… |
| [1] | Does the adoption of artificial intelligence by audit firms and their… (2024) | 5 | 4 | archival study with propensity score matching and two-stage OLS | Chinese firms, 2011-2020 | When audit firms and clients use AI separately, audit report lag increases. When they use AI together, report lag falls, improving efficiency. AI use is also a… |
| [3] | The Cost of Fraud Prediction Errors (2021) | 5 | 4 | empirical comparison of seven fraud prediction models using a cost-based measure | firm-level fraud and restatement samples (size not stated i… | Even the best models trade off false to true positives at rates above 100:1. The resulting false positives make all seven models too costly for auditors to imp… |
| [8] | Big Data and changes in audit technology: contemplating a research ag… (2018) | 4 | 3 | semi-structured interviews n=22 plus document analysis | 22 individuals experienced in developing, implementing or a… | Provides an overview of how big data and analytics change audit practice, covering auditor-client relationships, engagement conduct and challenges in embedding… |
| [6] | Detecting Anomalies in Financial Data Using Machine Learning Algorith… (2022) | 4 | 3 | empirical ML experiment: 7 supervised and 2 unsupervised models (isolation fore… | one real-life general ledger dataset (size not stated in ab… | The best supervised and unsupervised models show high potential for detecting predefined anomalies in general ledger journal entries, addressing sampling risk… |
| [7] | Auditors' Perception on the Impact of Artificial Intelligence on Prof… (2021) | 4 | 3 | structured questionnaire survey with correlation analysis | 169 respondents across sectors in Oman | Examines auditors' perceptions of how AI/ML affect professional skepticism and judgment and thereby audit efficiency, including influencing factors and challen… |
| [10] | The application of Artificial Intelligence in external auditing and i… (2023) | 4 | 2 | qualitative critical review of ongoing debates |  | Explores the role of AI in external auditing and assesses debates, with proponents citing better sampling, efficiency and audit quality and opponents citing et… |
| [18] | The Effect of Audit Partner Digitalization Expertise on Audit Fees (2024) | 3 | 4 | archival regression analysis of audit fees | listed U.S. companies, 2016-2021 | Documents a statistically and economically significant audit fee premium for audit partners with digitalization expertise, strongest in highly digitalized indu… |
| [19] | The Impact of Audit Technology on Audit Task Outcomes: Evidence for T… (2022) | 3 | 3 | two surveys plus interviews with auditors and chief audit executives | internal auditors and CAEs (sizes not stated in abstract) | Greater use of technology-based audit techniques is associated with more audits completed, more risk factors found, more recommendations and fewer audit days,… |
| [20] | Artificial Intelligence in audit (2022) | 3 | 3 | online questionnaire survey with principal axis factor analysis, n=206 | 206 auditing and accounting practitioners and students in P… | Respondents perceive that AI adoption increases audit efficiency, enhances client communication and service, and automates routine tasks. Three factors explain… |
| [17] | Abnormal Audit Fees and Audit Quality: Evidence from the Korean Audit… (2020) | 2 | 4 | archival empirical study (regression analysis of audit fees, audit hours and au… | public firms in the Korean audit market | Abnormally low audit fees are associated with larger discretionary accruals and a higher likelihood of meeting or beating analyst forecasts. No significant ass… |
| [21] | Audit Fees and Book-Tax Differences (2012) | 2 | 4 | archival regression study of audit fees and book-tax differences |  | Book-tax differences are positively associated with audit fees, and the association is larger for firms that appear to have managed earnings. This is consisten… |
| [22] | Auditing in times of social distancing: the effect of COVID-19 on aud… (2020) | 2 | 2 | desk study / theoretical discussion |  | Argues that COVID-19 social distancing could affect audit fees, effort, procedures and audit quality. It recommends that audit firms invest in digital programs… |
| [23] | Female audit committee members and their influence on audit fees (2016) | 1 | 3 | archival cross-sectional regression | 624 Australian companies, 2011 | Female audit committee representation is positively associated with audit fees, and it moderates the effects of firm size, risk and complexity on fees. It does… |

</details>

#### rq3 — How accurate and effective are machine learning and anomaly detection techniques at identifying fraudulent transactions and anomalous journal entries in audit settings?

21편 (rel ≥ 3: 13편) · 신뢰도 평균 3.2 · 상위: [3] The Cost of Fraud Prediction Errors (2021) (reli 4); [4] An Analysis on Financial Statement Fraud Detection for Chin… (2022) (reli 4); [6] Detecting Anomalies in Financial Data Using Machine Learnin… (2022) (reli 3)

<details><summary>전체 표 (21편)</summary>

| # | 문헌 | rel | reli | method | sample | finding |
|---|---|---|---|---|---|---|
| [3] | The Cost of Fraud Prediction Errors (2021) | 5 | 4 | empirical comparison of seven fraud prediction models using a cost-based measure | firm-level fraud and restatement samples (size not stated i… | Even the best models trade off false to true positives at rates above 100:1. The resulting false positives make all seven models too costly for auditors to imp… |
| [4] | An Analysis on Financial Statement Fraud Detection for Chinese Listed… (2022) | 4 | 4 | deep learning model development combining numerical and textual (MD&A) features | 5130 Chinese listed companies' annual reports | Develops a deep learning fraud detection system using financial and non-financial indices plus text features from MD&A to address class imbalance in financial… |
| [6] | Detecting Anomalies in Financial Data Using Machine Learning Algorith… (2022) | 4 | 3 | empirical ML experiment: 7 supervised and 2 unsupervised models (isolation fore… | one real-life general ledger dataset (size not stated in ab… | The best supervised and unsupervised models show high potential for detecting predefined anomalies in general ledger journal entries, addressing sampling risk… |
| [9] | Cluster Analysis for Anomaly Detection in Accounting Data: An Audit A… (2011) | 4 | 3 | applied case study using cluster analysis on insurance claims data | group life insurance claims (size not stated in abstract) | Cluster analysis grouped similar claims and flagged small-population clusters for further investigation, helping auditors focus effort. Flagged clusters were c… |
| [24] | Financial Fraud Detection Based on Machine Learning: A Systematic Lit… (2022) | 3 | 4 | systematic literature review (Kitchenham) of 93 articles | 93 articles | Synthesizes ML techniques, fraud types, and evaluation metrics in ML-based financial fraud detection, noting that conventional manual methods are imprecise, co… |
| [12] | Financial Statement Fraud Detection: An Analysis of Statistical and M… (2011) | 3 | 4 | empirical comparison of six statistical and ML models for financial statement f… | fraud and nonfraud firms; 42 predictors examined (sample si… | Logistic regression and support vector machines perform well relative to ANN, bagging, C4.5, and stacking at detecting financial statement fraud. Only six of 4… |
| [25] | Intelligent Fraud Detection in Financial Statements Using Machine Lea… (2021) | 3 | 4 | systematic literature review (Kitchenham) of 47 articles | 47 articles | Reviews ML and data mining methods and datasets for detecting fraudulent financial statements, noting that supervised algorithms are used more than unsupervise… |
| [26] | Financial fraud detection through the application of machine learning… (2024) | 3 | 4 | systematic literature review (PRISMA and Kitchenham) of 104 articles, 2012-2023 | 104 articles | Reviews ML techniques for financial fraud detection and notes a trend toward real datasets. Credit card fraud models are the most common application. |
| [27] | Big data techniques in auditing research and practice: Current trends… (2018) | 3 | 3 | literature review of big data techniques in auditing, accounting and finance re… |  | Finds that big data techniques are less widespread in auditing than in related fields such as financial fraud modelling. The authors refute the argument that a… |
| [28] | Detecting Financial Fraud Using Data Mining Techniques: A Decade Revi… (2021) | 3 | 3 | literature review of 65 articles on data mining for financial fraud, 2004-2015 | 65 articles (58 journal, 7 conference) | Identifies 41 data mining techniques used across financial fraud applications such as health insurance and credit card. Logistic regression appeared to be the… |
| [29] | Comparing performances and effectiveness of machine learning classifi… (2021) | 3 | 3 | empirical comparison of seven ML classifiers with SMOTE and undersampling | 341 Turkish SMEs, 2013-2017; 1384 non-fraud and 321 fraud c… | Evaluates seven ML classifiers for detecting financial accounting fraud in SME financial statements, using sampling methods to handle class imbalance. |
| [30] | Bagging or boosting? Empirical evidence from financial statement frau… (2023) | 3 | 3 | comparative empirical study of five bagging- and boosting-based ensemble learni… | Chinese A-share listed companies, 2012-2022 | Bagging outperforms boosting across various evaluation indicators in detecting financial statement fraud. Profitability and asset quality are positively associ… |
| [14] | Audit data analytics, machine learning, and full population testing (2022) | 3 | 2 | conceptual paper proposing an approach |  | The paper presents an approach for applying audit data analytics and machine learning to full population testing instead of sampling, and discusses related cha… |
| [31] | A Comparative Evaluation of Unsupervised Anomaly Detection Algorithms… (2016) | 2 | 4 | comparative empirical evaluation of 19 unsupervised anomaly detection algorithm… | 10 datasets from multiple application domains | Evaluates strengths and weaknesses of 19 unsupervised anomaly detection algorithms across datasets, including performance and computational effort. Fraud detec… |
| [32] | Statistical Fraud Detection: A Review (2002) | 2 | 3 | narrative review of statistical and machine learning fraud detection tools |  | Statistics and machine learning provide effective technologies for fraud detection, applied to money laundering, credit card fraud, telecommunications fraud an… |
| [33] | Explainable AI in Fintech Risk Management (2020) | 2 | 3 | empirical modelling with Shapley-value explainable AI | 15,000 SMEs seeking peer-to-peer lending credit | A Shapley-value explainable AI model groups risky and non-risky borrowers by similar financial characteristics, which helps explain credit scores and predict f… |
| [34] | A Secure AI-Driven Architecture for Automated Insurance Systems: Frau… (2020) | 2 | 3 | framework development with ML model comparison (XGBoost vs other algorithms) |  | Proposes a blockchain-based automated insurance framework that uses XGBoost to detect fraudulent claims and assess risk, and compares it with other state-of-th… |
| [35] | Advanced Fraud Detection in Blockchain Transactions: An Ensemble Lear… (2024) | 2 | 3 | ML ensemble modeling with explainable AI on cryptocurrency transactions | Ethereum transaction data (size not stated) | A hard voting ensemble reached 99% accuracy in detecting fraudulent Ethereum transactions. The authors stress XAI for transparency and trust. |
| [36] | Big Data Analytics for Business Intelligence in Accounting and Audit (2021) | 2 | 2 | narrative review/commentary (method unclear from abstract) |  | Reports that audit firms are keen to use machine learning tools to read contracts, analyze journal entries and assist in fraud detection, and anticipates accel… |
| [37] | Detection of Anomaly using Machine Learning: A Comprehensive Survey (2022) | 1 | 3 | literature survey of 101 articles on ML anomaly detection, 2015-2022 | 101 articles | Surveys ML anomaly detection across system log, network, cloud and medical domains. Most researchers use real-life datasets and unsupervised learning. |
| [38] | Machine Learning-Based Network Anomaly Detection: Design, Implementat… (2024) | 1 | 3 | ML system development and evaluation for network anomaly detection (unsupervise… | network traffic data (size not stated) | Random Forest reached 94.3% accuracy in classifying network anomalies. SHAP was used for interpretability. |

</details>

#### rq4 — Through which mechanisms and under which conditions (auditor judgment, skepticism, client complexity, firm size, regulation) does AI-based detection change audit outcomes?

23편 (rel ≥ 3: 14편) · 신뢰도 평균 3.1 · 상위: [1] Does the adoption of artificial intelligence by audit firms… (2024) (reli 4); [8] Big Data and changes in audit technology: contemplating a r… (2018) (reli 3); [7] Auditors' Perception on the Impact of Artificial Intelligen… (2021) (reli 3)

<details><summary>전체 표 (23편)</summary>

| # | 문헌 | rel | reli | method | sample | finding |
|---|---|---|---|---|---|---|
| [1] | Does the adoption of artificial intelligence by audit firms and their… (2024) | 5 | 4 | archival study with propensity score matching and two-stage OLS | Chinese firms, 2011-2020 | When audit firms and clients use AI separately, audit report lag increases. When they use AI together, report lag falls, improving efficiency. AI use is also a… |
| [8] | Big Data and changes in audit technology: contemplating a research ag… (2018) | 4 | 3 | semi-structured interviews n=22 plus document analysis | 22 individuals experienced in developing, implementing or a… | Provides an overview of how big data and analytics change audit practice, covering auditor-client relationships, engagement conduct and challenges in embedding… |
| [7] | Auditors' Perception on the Impact of Artificial Intelligence on Prof… (2021) | 4 | 3 | structured questionnaire survey with correlation analysis | 169 respondents across sectors in Oman | Examines auditors' perceptions of how AI/ML affect professional skepticism and judgment and thereby audit efficiency, including influencing factors and challen… |
| [5] | Application of Artificial Intelligence and Audit Quality in Nigeria (2023) | 4 | 3 | cross-sectional survey with OLS regression, n=125 | 125 accounting firms in Nigeria applying AI (purposive samp… | Expert systems, machine learning and intelligent agents showed significant positive relationships with audit quality in Nigeria. |
| [10] | The application of Artificial Intelligence in external auditing and i… (2023) | 4 | 2 | qualitative critical review of ongoing debates |  | Explores the role of AI in external auditing and assesses debates, with proponents citing better sampling, efficiency and audit quality and opponents citing et… |
| [11] | Auditing with data and analytics: External reviewers' judgments of au… (2023) | 3 | 4 | two experiments with experienced external reviewers | Experienced external reviewers (size not stated in abstract) | Reviewers rate data and analytics audit procedures as lower quality than traditional ones because they perceive them as less effortful, even at equal assurance… |
| [18] | The Effect of Audit Partner Digitalization Expertise on Audit Fees (2024) | 3 | 4 | archival regression analysis of audit fees | listed U.S. companies, 2016-2021 | Documents a statistically and economically significant audit fee premium for audit partners with digitalization expertise, strongest in highly digitalized indu… |
| [13] | Artificial intelligence adoption, audit quality and integrated financ… (2024) | 3 | 3 | panel regression (OLS) with propensity score robustness checks | 2,912 non-financial firm-year observations, GCC listed firm… | The study examines whether firm AI adoption improves integrated financial reporting, with audit quality (fees, industry specialization, restatement) as a moder… |
| [19] | The Impact of Audit Technology on Audit Task Outcomes: Evidence for T… (2022) | 3 | 3 | two surveys plus interviews with auditors and chief audit executives | internal auditors and CAEs (sizes not stated in abstract) | Greater use of technology-based audit techniques is associated with more audits completed, more risk factors found, more recommendations and fewer audit days,… |
| [39] | Auditor judgment in the fourth industrial revolution (2023) | 3 | 3 | qualitative study, 44 in-depth interviews | 44 auditors, regulators and AI software providers | Automating seemingly low-level audit tasks may erode deliberation, sensemaking and reflexivity important for socializing junior auditors, while higher-level au… |
| [40] | Artificial intelligence based decision-making in accounting and audit… (2022) | 3 | 3 | narrative (semi-systematic) literature review, 2015-2020, interpretive/hermeneu… |  | Identifies five major ethical challenges of AI-based decision-making in accounting: objectivity, privacy, transparency, accountability and trustworthiness, str… |
| [41] | Anticipatory innovation of professional services: The case of auditin… (2023) | 3 | 3 | in-depth qualitative case study | Big Four audit firms in Japan, 2010s | Shows how newly created service R&D organizations advanced AI adoption in external audit services and builds a three-phase model of the process. Addresses orga… |
| [16] | AUDITING WITH AI: A THEORETICAL FRAMEWORK FOR APPLYING MACHINE LEARNI… (2024) | 3 | 2 | theoretical framework / conceptual paper drawing on extant literature |  | Proposes a framework for applying ML and data analytics across the internal audit lifecycle, from planning to reporting. It argues auditors need a continuous i… |
| [42] | Behavioral challenges to professional skepticism in auditors’ data an… (2022) | 3 | 2 | narrative literature review / discussion paper |  | Reviews audit research to identify behavioral challenges to professional skepticism when using audit data analytics, from five perspectives: attitudes toward A… |
| [43] | A Model and Literature Review of Professional Skepticism in Auditing (2009) | 2 | 4 | literature review with conceptual model |  | Defines professional skepticism as judgments reflecting heightened assessment of the risk that an assertion is incorrect, and presents a model of how audit evi… |
| [44] | Towards a better understanding on mitigating algorithm aversion in fo… (2021) | 2 | 4 | online experiment (forecasting task) | 1,840 participants | Time pressure mitigates algorithm aversion, apparently because forecasters lose confidence in their own forecasts. No support was found for the 'do your best'… |
| [45] | Professional Skepticism and Auditors’ Assessment of Misstatement Risk… (2017) | 2 | 4 | field experiment with multiple regression, n=248 | 248 auditors from Big4 and non-Big4 firms in Malaysia | Professional skepticism and experience positively affect risk-of-misstatement assessment while time budget pressure negatively affects it. Experience strengthe… |
| [46] | The extent of algorithm aversion in decision-making situations with v… (2023) | 2 | 3 | framing experiment |  | Algorithm aversion becomes more frequent as the consequences of a decision become more serious, which lowers the probability of success in important decisions. |
| [47] | Auditors’ professional skepticism and fraud detection (2021) | 2 | 3 | cross-sectional survey with PLS, n=173 | 173 internal auditors at Indonesia's Inspectorate General o… | Auditor experience and professional skepticism positively affect fraud detection, while competence, independence and time pressure have no direct effect. Skept… |
| [48] | PROFESSIONAL SKEPTICISM IN AUDITING AND ITS CHARACTERISTICS (2017) | 2 | 2 | narrative literature synthesis |  | Synthesizes research on auditor professional skepticism into six attributes (questioning mind, suspension of judgment, search for knowledge, interpersonal unde… |
| [49] | Does Audit Committee Accounting Expertise Help to Promote Audit Quali… (2019) | 1 | 4 | archival empirical study | Clients with internal control audits; restatements used as… | Greater audit committee accounting expertise is associated with more adverse internal control opinions among clients with likely weaknesses. It is also associa… |
| [50] | Algorithm appreciation or aversion? Comparing in-service and pre-serv… (2021) | 1 | 3 | behavioral and questionnaire study | in-service and pre-service teachers (size not stated in abs… | Both in-service and pre-service teachers prefer advice from a human counselor over an expert model, and acceptance depends on task difficulty. |
| [51] | Time budget pressure on audit quality with audit structure, independe… (2020) | 1 | 3 | survey with moderated regression analysis | auditors at public accounting firms in Bali Province, Indon… | Time budget pressure has a negative but statistically non-significant effect on audit quality; audit structure, independence and supervision were examined as m… |

</details>

#### rq5 — What are the adoption drivers, implementation barriers, and risks (false positives, explainability, data quality, liability, regulatory concerns) of AI in external auditing?

30편 (rel ≥ 3: 19편) · 신뢰도 평균 2.8 · 상위: [2] Is artificial intelligence improving the audit process? (2022) (reli 4); [3] The Cost of Fraud Prediction Errors (2021) (reli 4); [8] Big Data and changes in audit technology: contemplating a r… (2018) (reli 3)

<details><summary>전체 표 (30편)</summary>

| # | 문헌 | rel | reli | method | sample | finding |
|---|---|---|---|---|---|---|
| [2] | Is artificial intelligence improving the audit process? (2022) | 5 | 4 | archival analysis of resume data on AI workers plus interviews with 17 audit pa… | 310,000+ resumes for 36 largest audit firms; 17 audit partn… | Greater AI investment by audit firms is associated with improved audit quality, lower fees, and displacement of human auditors. A one-SD increase in AI investm… |
| [3] | The Cost of Fraud Prediction Errors (2021) | 5 | 4 | empirical comparison of seven fraud prediction models using a cost-based measure | firm-level fraud and restatement samples (size not stated i… | Even the best models trade off false to true positives at rates above 100:1. The resulting false positives make all seven models too costly for auditors to imp… |
| [8] | Big Data and changes in audit technology: contemplating a research ag… (2018) | 4 | 3 | semi-structured interviews n=22 plus document analysis | 22 individuals experienced in developing, implementing or a… | Provides an overview of how big data and analytics change audit practice, covering auditor-client relationships, engagement conduct and challenges in embedding… |
| [7] | Auditors' Perception on the Impact of Artificial Intelligence on Prof… (2021) | 4 | 3 | structured questionnaire survey with correlation analysis | 169 respondents across sectors in Oman | Examines auditors' perceptions of how AI/ML affect professional skepticism and judgment and thereby audit efficiency, including influencing factors and challen… |
| [10] | The application of Artificial Intelligence in external auditing and i… (2023) | 4 | 2 | qualitative critical review of ongoing debates |  | Explores the role of AI in external auditing and assesses debates, with proponents citing better sampling, efficiency and audit quality and opponents citing et… |
| [11] | Auditing with data and analytics: External reviewers' judgments of au… (2023) | 3 | 4 | two experiments with experienced external reviewers | Experienced external reviewers (size not stated in abstract) | Reviewers rate data and analytics audit procedures as lower quality than traditional ones because they perceive them as less effortful, even at equal assurance… |
| [25] | Intelligent Fraud Detection in Financial Statements Using Machine Lea… (2021) | 3 | 4 | systematic literature review (Kitchenham) of 47 articles | 47 articles | Reviews ML and data mining methods and datasets for detecting fraudulent financial statements, noting that supervised algorithms are used more than unsupervise… |
| [27] | Big data techniques in auditing research and practice: Current trends… (2018) | 3 | 3 | literature review of big data techniques in auditing, accounting and finance re… |  | Finds that big data techniques are less widespread in auditing than in related fields such as financial fraud modelling. The authors refute the argument that a… |
| [19] | The Impact of Audit Technology on Audit Task Outcomes: Evidence for T… (2022) | 3 | 3 | two surveys plus interviews with auditors and chief audit executives | internal auditors and CAEs (sizes not stated in abstract) | Greater use of technology-based audit techniques is associated with more audits completed, more risk factors found, more recommendations and fewer audit days,… |
| [39] | Auditor judgment in the fourth industrial revolution (2023) | 3 | 3 | qualitative study, 44 in-depth interviews | 44 auditors, regulators and AI software providers | Automating seemingly low-level audit tasks may erode deliberation, sensemaking and reflexivity important for socializing junior auditors, while higher-level au… |
| [52] | The Effect of Technology Readiness on Adopting Artificial Intelligenc… (2024) | 3 | 3 | cross-sectional survey n=143 (technology acceptance model-based) | 143 accountants and auditors in companies in Vietnam | Technology readiness positively relates to AI adoption among accounting and auditing professionals, with perceived usefulness and perceived ease of use mediati… |
| [40] | Artificial intelligence based decision-making in accounting and audit… (2022) | 3 | 3 | narrative (semi-systematic) literature review, 2015-2020, interpretive/hermeneu… |  | Identifies five major ethical challenges of AI-based decision-making in accounting: objectivity, privacy, transparency, accountability and trustworthiness, str… |
| [41] | Anticipatory innovation of professional services: The case of auditin… (2023) | 3 | 3 | in-depth qualitative case study | Big Four audit firms in Japan, 2010s | Shows how newly created service R&D organizations advanced AI adoption in external audit services and builds a three-phase model of the process. Addresses orga… |
| [20] | Artificial Intelligence in audit (2022) | 3 | 3 | online questionnaire survey with principal axis factor analysis, n=206 | 206 auditing and accounting practitioners and students in P… | Respondents perceive that AI adoption increases audit efficiency, enhances client communication and service, and automates routine tasks. Three factors explain… |
| [14] | Audit data analytics, machine learning, and full population testing (2022) | 3 | 2 | conceptual paper proposing an approach |  | The paper presents an approach for applying audit data analytics and machine learning to full population testing instead of sampling, and discusses related cha… |
| [15] | Current machine learning applications in accounting and auditing (2020) | 3 | 2 | content analysis of Big Four machine learning tools | Machine learning tools and platforms of the Big Four firms | Big Four firms have developed ML tools for audit coordination, automated audits in limited areas such as cash, data analysis, risk assessment and document extr… |
| [16] | AUDITING WITH AI: A THEORETICAL FRAMEWORK FOR APPLYING MACHINE LEARNI… (2024) | 3 | 2 | theoretical framework / conceptual paper drawing on extant literature |  | Proposes a framework for applying ML and data analytics across the internal audit lifecycle, from planning to reporting. It argues auditors need a continuous i… |
| [53] | Current State and Challenges in the Implementation of Smart Robotic P… (2020) | 3 | 2 | conceptual overview of RPA ecosystem and challenges (unclear from abstract) |  | The study summarizes the evolving RPA ecosystem and identifies challenges critical for successfully implementing smart (AI-augmented) RPA in accounting and aud… |
| [42] | Behavioral challenges to professional skepticism in auditors’ data an… (2022) | 3 | 2 | narrative literature review / discussion paper |  | Reviews audit research to identify behavioral challenges to professional skepticism when using audit data analytics, from five perspectives: attitudes toward A… |
| [33] | Explainable AI in Fintech Risk Management (2020) | 2 | 3 | empirical modelling with Shapley-value explainable AI | 15,000 SMEs seeking peer-to-peer lending credit | A Shapley-value explainable AI model groups risky and non-risky borrowers by similar financial characteristics, which helps explain credit scores and predict f… |
| [54] | Transparency, Auditability and eXplainability of Machine Learning Mod… (2020) | 2 | 3 | framework development with real-world case study |  | The paper proposes a framework and overview of techniques to make black-box ML credit scoring models transparent, auditable and explainable. A real-world case… |
| [35] | Advanced Fraud Detection in Blockchain Transactions: An Ensemble Lear… (2024) | 2 | 3 | ML ensemble modeling with explainable AI on cryptocurrency transactions | Ethereum transaction data (size not stated) | A hard voting ensemble reached 99% accuracy in detecting fraudulent Ethereum transactions. The authors stress XAI for transparency and trust. |
| [22] | Auditing in times of social distancing: the effect of COVID-19 on aud… (2020) | 2 | 2 | desk study / theoretical discussion |  | Argues that COVID-19 social distancing could affect audit fees, effort, procedures and audit quality. It recommends that audit firms invest in digital programs… |
| [55] | Factors Influencing Audit Technology Acceptance by Audit Firms: A New… (2012) | 2 | 2 | conceptual framework development (I-TOE) combining UTAUT2 and TOE |  | Proposes an Individual-Technology-Organization-Environment framework to explain adoption of computer-assisted audit techniques by audit firms. The abstract doe… |
| [56] | “Computer says no”: Algorithmic decision support and organisational r… (2021) | 2 | 2 | conceptual overview with guidelines and a digital tool |  | Gives an overview of issues around algorithmic decision support, responsibility and organisational decision-making. It identifies research gaps and proposes gu… |
| [57] | Financial Risk Management and Explainable, Trustworthy, Responsible AI (2022) | 2 | 2 | perspective paper based on round-table sessions |  | The paper discusses model risk management for AI/ML models in banks and financial institutions and expects more complex models in anti-money laundering, fraud… |
| [36] | Big Data Analytics for Business Intelligence in Accounting and Audit (2021) | 2 | 2 | narrative review/commentary (method unclear from abstract) |  | Reports that audit firms are keen to use machine learning tools to read contracts, analyze journal entries and assist in fraud detection, and anticipates accel… |
| [58] | Explaining Why the Computer Says No: Algorithmic Transparency Affects… (2022) | 1 | 4 | survey experiment with two scenarios | citizens (sample size not stated in abstract) | Explainability affects trust in algorithmic decisions more than accessibility, and the effect partly extends to trust in the human decision-maker. Effects are… |
| [59] | Explainable AI (XAI): Core Ideas, Techniques, and Solutions (2022) | 1 | 3 | survey/taxonomy of XAI techniques |  | Surveys and classifies XAI techniques and programming frameworks across the machine learning development process. |
| [60] | The perils and pitfalls of explainable AI: Strategies for explaining… (2021) | 1 | 3 | illustrative multiple case studies (3 cases) | three government algorithmic decision-making cases | Explainable, data-driven decisions are often not perceived as objective by the public and can provoke distrust and resistance. The paper proposes decision-spec… |

</details>

#### 평가했으나 어느 sub-RQ 에도 배정되지 않은 문헌 (20편, 대부분 관련성 ≤ 1)

Evaluator 가 읽고 관련성이 낮다고 판정한 문헌. 종합·Gap 에 쓰이지 않아 참고문헌 번호를 받지 않으며, 평가 기록으로만 남긴다.

<details><summary>전체 표 (20편)</summary>

| id | 문헌 | rel | reli | method | sample | finding |
|---|---|---|---|---|---|---|
| 10.1017/s0022109011000457 | Corporate Lobbying and Fraud Detection (2011) | 1 | 4 | archival empirical study of lobbying expenses and fraud detection (hazard model) | Large frauds detected 1998-2004; corporate lobbying data | Lobbying firms have a significantly lower hazard of fraud detection, evade detection 117 days longer, and are 38% less likely to be detected by regulators. Fra… |
| 10.2308/tar-2022-0249 | Audit-Employee Turnover, Audit Delivery, and Auditor-Client Realignme… (2025) | 1 | 4 | archival empirical study using novel office-level audit-employee turnover data |  | Audit-employee turnover within accounting firm offices is associated with costlier, less timely, less thorough and lower-quality audits, and leads to greater a… |
| 10.1506/f024-686l-7233-n62j | Audit Firm Appointments, Audit Firm Alumni, and Audit Committee Indep… (2007) | 1 | 3 | archival empirical study of auditor appointments |  | Companies appoint officers' former audit firms more often than alternatives, but less often when audit committees are more independent. This suggests independe… |
| 10.1016/j.jbusres.2016.08.001 | Critical analysis of Big Data challenges and analytical methods (2016) | 1 | 3 | state-of-the-art literature review of big data challenges and analytics methods |  | Reviews big data challenges and analytics methods that organizations use to support investment decisions. It is general to business and not specific to auditin… |
| 10.1111/j.1467-629x.2012.00490.x | Independent audit committee members’ board tenure and audit fees (2012) | 1 | 3 | archival regression study (details unclear from abstract) |  | Audit fees are negatively associated with the proportion of long-tenure directors on independent audit committees, consistent with lower audit effort. The stud… |
| 10.1016/j.compind.2020.103368 | Big data analytics: Implementation challenges in Indian manufacturing… (2020) | 1 | 3 | ISM-DEMATEL-Fuzzy MICMAC barrier modeling | Indian manufacturing supply chains; twelve barriers | Lack of top management support, financial support, skills, and techniques/procedures are the most significant barriers to big data analytics implementation in… |
| 10.1109/access.2021.3056614 | Benchmarking of Machine Learning for Anomaly Based Intrusion Detectio… (2021) | 1 | 3 | benchmarking of 10 supervised and unsupervised ML algorithms on the CICIDS2017… | CICIDS2017 network intrusion dataset | Benchmarks ML algorithms for anomaly-based intrusion detection to identify suitable algorithms, parameters, and testing criteria. |
| 10.1109/access.2023.3321800 | A Comprehensive Survey of Machine Learning Methods for Surveillance V… (2023) | 1 | 3 | survey of machine learning methods for video anomaly detection |  | Provides a critical review of recent learning algorithms for anomaly detection in surveillance video, including strengths, weaknesses and anomaly type classifi… |
| 10.1109/access.2023.3325929 | IoT Network Anomaly Detection in Smart Homes Using Machine Learning (2023) | 1 | 3 | machine learning classifier comparison on benchmark dataset | UNSW BoT-IoT dataset | Proposes a machine learning-based anomaly detection approach for IoT smart home traffic using four classifiers. Not related to auditing or financial fraud. |
| 10.5296/wjbm.v3i1.11321 | The Structure of Emotional Intelligence, Spiritual Intelligence and I… (2017) | 1 | 3 | cross-sectional questionnaire survey with SEM-PLS (WarpPLS) | 91 analyzable questionnaires from auditors in Public Accoun… | Emotional intelligence raises work enthusiasm, spiritual intelligence directly improves auditor performance, and work enthusiasm positively affects auditor per… |
| 10.12691/acis-3-1-3 | Heterogeneous Data and Big Data Analytics (2017) | 1 | 2 | narrative review of heterogeneous data and big data analytics methods |  | Introduces data processing methods, tools and ML/deep learning approaches for heterogeneous big data. It does not address auditing. |
| 10.1007/s44206-023-00074-y | Auditing of AI: Legal, Ethical and Technical Approaches (2023) | 1 | 2 | narrative review/editorial |  | The review argues that AI auditing can learn from historical audit practices in financial accounting, safety engineering and the social sciences. It distinguis… |
| 10.1007/s11229-022-03485-5 | Conceptual challenges for interpretable machine learning (2022) | 1 | 2 | philosophical/conceptual analysis |  | The article identifies three conceptual challenges for interpretable ML: ambiguity of target, disregard for error rates and severe testing, and emphasis on pro… |
| 10.3390/app12073234 | Detecting Cryptojacking Web Threats: An Approach with Autoencoders an… (2022) | 1 | 2 | unclear from abstract (autoencoder and deep dense neural network detection mode… |  | The paper proposes an approach using autoencoders and deep dense neural networks to detect cryptojacking web threats. The abstract is truncated and gives no re… |
| 10.1109/access.2021.3071269 | Deep Learning in Smart Grid Technology: A Review of Recent Advancemen… (2021) | 0 | 3 | review of deep learning in smart grids with bibliometric analysis |  | Reviews deep learning advances and enabling technologies in smart grid systems. |
| 10.18280/ria.350102 | Attack and Anomaly Detection in IoT Networks Using Supervised Machine… (2021) | 0 | 3 | supervised ML experiments on the BoT-IoT dataset | BoT-IoT dataset | Develops an IoT intrusion detection system using a seven-feature set that detects DDoS, DoS, reconnaissance and information theft attacks with supervised ML. |
| 10.1109/access.2020.3041178 | Smart Grid Big Data Analytics: Survey of Technologies, Techniques, an… (2020) | 0 | 2 | survey / literature review of smart grid big data technologies |  | Surveys big data analytics technologies and challenges in smart grids. It is unrelated to auditing. |
| 10.1007/s13347-017-0278-y | Big Data Analytics, Infectious Diseases and Associated Ethical Impacts (2017) | 0 | 2 | conceptual/ethical discussion paper |  | Discusses ethical impacts of big data analytics in infectious disease contexts, including algorithmic reliance, informed consent complexity, and profiling. |
| 10.1109/access.2019.2905101 | Towards Deep Learning Prospects: Insights for Social Media Analytics (2019) | 0 | 2 | narrative survey / taxonomy of deep learning for social media analytics |  | Summarizes deep learning architectures for social media analytics and highlights challenges such as scalability, heterogeneity and multimodality. Not related t… |
| 10.47760/ijcsmc.2020.v09i10.012 | Attack and Anomaly Detection in IoT Networks using Machine Learning (2020) | 0 | 2 | comparison of ML algorithms (RF, NB, SVM, decision tree) for IoT anomaly detect… |  | Random Forest performed best, with 99.5% accuracy in detecting anomalies in IoT network data. |

</details>

## 4. 종합

### 합의

- Greater AI use by audit firms is associated with a lower likelihood of client restatements in two archival studies (about 5.0% lower per SD of AI investment in one). This is only an indirect quality proxy, since fewer restatements could reflect fewer errors or weaker detection, and the Nigerian perception survey adds only self-reported quality. [1, 2, 5] (근거 3편 · 신뢰도 평균 3.7)

- Evidence on efficiency gains from AI or audit technology is perception-based or comes from internal audit, with self-reported efficiency gains and fewer audit days. No study measures external-audit hours or effort, so efficiency gains are unmeasured in external audit. [1, 19, 20] (근거 3편 · 신뢰도 평균 3.3)

- The ML fraud-detection literature is dominated by firm-level financial-statement and other non-audit fraud applications, with supervised methods more common than unsupervised ones. The reviews give no audit-specific, transaction-level accuracy benchmark, so no cross-paper consensus on journal-entry accuracy exists. [24, 25, 26, 28] (근거 4편 · 신뢰도 평균 3.8)

- Conceptual and qualitative work, largely about audit data analytics generally and not AI anomaly detection specifically, raises concerns that analytics could weaken professional skepticism and erode junior auditors' sensemaking. [39, 42] (근거 2편 · 신뢰도 평균 2.5)

- Reviews, interviews and tool descriptions identify ethical concerns, difficulty hiring skilled staff, and the difficulty of quantifying benefits as barriers and risks. Technology readiness and perceived usefulness drive adoption in one small survey. This evidence is mostly descriptive and low to moderate reliability. [10, 15, 19, 40, 41, 52] (근거 6편 · 신뢰도 평균 2.7)

### 상충

- (없음)

### 조건부

- In one Chinese archival study, audit report lag falls only when audit firms and clients use AI together; separate use increases lag. This is a within-study moderation by joint versus separate use, not a conflict, and report lag is not audit hours. [1] (근거 1편 · 신뢰도 평균 4.0)

- Experienced reviewers rate data-and-analytics procedures as lower quality because of an effort heuristic, even at equal assurance, and a theory-based intervention reduces this bias. This is reviewer perception, not evidence of eroded auditor judgment, and it concerns D&A generally. [11] (근거 1편 · 신뢰도 평균 4.0)

- The practical value of fraud-prediction models depends on whose costs are counted. At false-to-true-positive ratios above 100:1, all seven tested models were too costly for auditors, while some gave net benefits to investors or regulators. This tests traditional models, not modern AI. [3] (근거 1편 · 신뢰도 평균 4.0)

- Model rankings are dataset-specific single-study results at firm level: logistic regression and SVM did well against ANN, bagging and stacking in a 2011 study, and bagging beat boosting among ensembles in Chinese A-share data. Neither addresses transaction-level or journal-entry detection. [12, 30] (근거 2편 · 신뢰도 평균 3.5)

### 커버리지 메모

No new papers were added to the table, so the critic's requested searches are still outstanding. rq3 is effectively unanswered for transaction-level accuracy: the only journal-entry study [6] uses predefined anomalies on a single ledger, the insurance-claims study [9] has no validation, and [4] shows no results. The rest is firm-level or non-audit work. Studies on AAER-labelled or confirmed-misstatement data reporting precision, recall or false-positive rates are missing. rq1 rests on restatement likelihood in two archival studies; no study covers discretionary accruals, detection of misstatement or fraud, AAERs or going-concern outcomes. rq2 separates fees (a price: 0.9% lower per SD in [2]; a partner digital-expertise premium in [18], a different construct from firm AI investment) from hours and effort, which are unmeasured in external audit. Efficiency evidence is limited to report lag, perception surveys and internal audit. rq4 moderators (client complexity, firm size, regulation) are untested; evidence is generic D&A experiments, interviews and one effort-lag mechanism, and no study examines auditors' use of AI flags. rq5 risks are covered descriptively; false positives, explainability, data quality, liability and PCAOB/IAASB guidance are not directly covered. The most useful missing studies are archival or experimental work on auditor AI use with objective outcomes, and audit-hours data.}</br>Correction: the JSON above must be a single object; see below.</br>{

## 5. Research Gap

### G1. No study reports precision, recall or false-positive rates for AI anomaly detection on labelled journal-entry or transaction data from real audits.

[3, 6, 9] (근거 3편 · 신뢰도 평균 3.3)

The only journal-entry study tests predefined anomalies on one ledger, and the insurance-claims study has no validation. The cost-based evidence covers only traditional firm-level models, where false positives above 100:1 made all seven too costly for auditors.

- 제안 RQ: How accurate are supervised and unsupervised anomaly detectors on journal entries with confirmed misstatements, and what is the audit-cost burden of their false positives?
- 방법: Benchmark isolation forest, autoencoders and supervised classifiers on labelled entries using time-split validation. Report precision, recall and false positives per 1,000 entries, and convert follow-up effort into hours using a cost model like the one in [3].
- 데이터: Journal-entry populations with confirmed misstatements or AAER-linked cases, obtained through a partnership with one or more audit firms or from forensic-case archives. Synthetic injected-fraud data would serve only as a secondary check.

### G2. External-audit hours and effort have not been measured in relation to AI adoption.

[1, 2, 19] (근거 3편 · 신뢰도 평균 3.7)

Fees are a price, report lag is a timing proxy, and the efficiency evidence otherwise comes from internal audit or perception surveys. Whether cost savings exist, and who captures them, is therefore unknown.

- 제안 RQ: Does staged adoption of AI anomaly detection reduce external-audit hours per engagement, and how much of the saving reaches clients as lower fees?
- 방법: Difference-in-differences with staggered adoption, comparing engagements before and after tool rollout against not-yet-adopting offices. The main outcomes are total and staff-level hours, fees and realization rates.
- 데이터: Engagement-level time-and-billing records from one or more firms, covering about three years before and after rollout. Where access fails, use audit-hours disclosures in jurisdictions that publish them.

### G3. Audit quality is measured only by restatement likelihood and by perceived quality in a Nigerian survey.

[1, 2, 5] (근거 3편 · 신뢰도 평균 3.7)

Fewer restatements could mean fewer errors or weaker detection. No study links auditor AI use to discretionary accruals, detected misstatements, AAERs or going-concern outcomes.

- 제안 RQ: Is auditor AI investment associated with lower abnormal accruals and a higher rate of audit-adjusted misstatements and going-concern modifications, once restatements are controlled for?
- 방법: Panel regressions with client and auditor fixed effects, instrumenting AI investment with the firm's pre-period digital hiring. Outcomes are absolute discretionary accruals, audit adjustments, AAER incidence and going-concern opinion accuracy for distressed clients.
- 데이터: AI-hiring measures built from resume data like those in [2], merged with Audit Analytics and Compustat for U.S. listed clients.

### G4. No study examines how auditors act on AI anomaly flags, or whether the effect varies with client complexity, auditor firm size or regulatory regime.

[11, 39, 42] (근거 3편 · 신뢰도 평균 3.0)

The skepticism and sensemaking concerns come from conceptual work, interviews and a reviewer-perception experiment, all about audit data analytics in general. The reviewer finding concerns perceived procedure quality, not auditor judgment.

- 제안 RQ: Do auditors investigate AI-generated flags less thoroughly when the flags are numerous or the tool is opaque, and does this differ by client complexity and auditor experience?
- 방법: Pre-registered 2×2×2 experiment manipulating flag volume, explanation availability and client complexity, with experienced auditors. The outcomes are the proportion of true anomalies investigated and the time spent on each flag.
- 데이터: About 150 senior auditors recruited through firms or professional bodies. Add a Big 4 versus non-Big 4 comparison in the sample.

### G5. Risks of AI anomaly detection in external audit rest on descriptive ethics reviews and public Big Four tool descriptions.

[15, 40, 41] (근거 3편 · 신뢰도 평균 2.7)

Explainability, data quality, auditor liability and the PCAOB/IAASB guidance have not been studied empirically. Without these, cost and quality gains cannot be set against implementation risk.

- 제안 RQ: How do explainability limits, data-quality problems and liability and standard-setter expectations constrain the use of AI anomaly detection as audit evidence?
- 방법: Mixed methods: document analysis of PCAOB and IAASB guidance and inspection findings, plus a survey (n≈200) and 20 interviews with auditors, regulators and tool vendors. The comparison is across firm tiers and jurisdictions, and the outcome is the share of AI output accepted as sufficient evidence.
- 데이터: Public regulatory documents and inspection reports, plus survey and interview participants from Big Four, mid-tier firms and regulators in at least two jurisdictions.

## 6. 향후 연구 방향

§5 의 제안을 한 표로 요약했다 (전문은 각 Gap). 근거는 해당 Gap 의 인용을 따른다.

| # | 제안 RQ | 연구 설계 | 데이터 | 근거 Gap |
|---|---|---|---|---|
| 1 | How accurate are supervised and unsupervised anomaly detectors on journal entries with confirmed misstatements, and what is the audit-cost… | Benchmark isolation forest, autoencoders and supervised classifiers on labelled entries using time-… | Journal-entry populations with confirmed misstatements or AAER-linked cases, ob… | G1 [3, 6, 9] |
| 2 | Does staged adoption of AI anomaly detection reduce external-audit hours per engagement, and how much of the saving reaches clients as lowe… | Difference-in-differences with staggered adoption, comparing engagements before and after tool roll… | Engagement-level time-and-billing records from one or more firms, covering abou… | G2 [1, 2, 19] |
| 3 | Is auditor AI investment associated with lower abnormal accruals and a higher rate of audit-adjusted misstatements and going-concern modifi… | Panel regressions with client and auditor fixed effects, instrumenting AI investment with the firm'… | AI-hiring measures built from resume data like those in [2], merged with Audit… | G3 [1, 2, 5] |
| 4 | Do auditors investigate AI-generated flags less thoroughly when the flags are numerous or the tool is opaque, and does this differ by clien… | Pre-registered 2×2×2 experiment manipulating flag volume, explanation availability and client compl… | About 150 senior auditors recruited through firms or professional bodies. Add a… | G4 [11, 39, 42] |
| 5 | How do explainability limits, data-quality problems and liability and standard-setter expectations constrain the use of AI anomaly detectio… | Mixed methods: document analysis of PCAOB and IAASB guidance and inspection findings, plus a survey… | Public regulatory documents and inspection reports, plus survey and interview p… | G5 [15, 40, 41] |

## 7. 한계와 신뢰도

- Sub-question 3 (accuracy on audit journal entries and transactions) is effectively unanswered: the only journal-entry study uses predefined anomalies on a single ledger, the insurance-claims study has no validation, and one paper shows no results; the rest are firm-level or non-audit fraud models.

- Audit-quality evidence rests on restatement likelihood in two archival studies plus a Nigerian perception survey; no study covers discretionary accruals, detected misstatements, AAERs or going-concern outcomes, and fewer restatements could reflect weaker detection.

- Cost evidence is thin and mixed in construct: fees (a firm-level AI discount versus a partner digital-expertise premium) and report lag are proxies, external-audit hours are unmeasured, and the efficiency evidence comes mainly from perception surveys and internal audit.

- Much of the skepticism, sensemaking, ethics and adoption-barrier evidence comes from reviews, interviews, conceptual work, small surveys and vendor tool descriptions about audit data analytics generally, so reliability is low to moderate and it does not isolate AI anomaly detection; moderators (client complexity, firm size, regulation) and risks such as explainability, liability and PCAOB/IAASB guidance are untested.

- Only abstracts and metadata were read, with no full texts, and the search covered OpenAlex and arXiv only (80 of 403 candidates evaluated), so relevant work in other databases or practitioner and regulator sources may be missed.

- The final quality gate flagged rq3 as a major unresolved gap, and the requested follow-up searches for labelled-misstatement accuracy studies and for auditor-response or moderation studies were not completed.

**품질 게이트가 자동으로 기록한 미해결 항목** (사람이 쓴 것이 아니라 파이프라인 검사 결과다):

- Critic 미해결 — major issue(s) persist after re-search, recorded as limitation: rq3: rq3 asks about accuracy at identifying fraudulent transactions and journal entries in audit settings. The only audit-relevant papers are [6]
## 품질 한눈에

| 검색 후보 | 평가 문헌 | 실존 검증 (DOI/arXiv) | sub-RQ 커버리지 (근거 ≥ 3편) | 출처 있는 claim | 근거 ≥ 2편인 Gap | Critic 판정 / Replan | 품질 게이트 미해결 | 비용 · 시간 |
|---|---|---|---|---|---|---|---|---|
| 403 | 80 | 80/80 (100%) | 5/5 | 9/9 | 5/5 | 3회 / 2회 | 1건 → §7 | $0.81 · 6.8분 |

LLM 없이 코드가 계산한 결정적 지표다 (`cost.json` `checks`). 인용 번호 [n] 은 바로 아래 참고문헌을 가리킨다.


## 참고문헌 (60편)

본문·표에 번호로 인용된 문헌. 모두 검색 도구(OpenAlex·arXiv·Crossref)가 반환한 메타데이터 그대로이며 DOI/arXiv id 로 실존이 확인됐다.

1. Md Jahidur Rahman, Hongtao Zhu, Yue Li (2024). Does the adoption of artificial intelligence by audit firms and their clients affect audit quality and efficiency? Evidence from China. *Managerial Auditing Journal*. https://doi.org/10.1108/maj-03-2023-3846
2. Anastassia Fedyk, James Hodson, Natalya V. Khimich et al. (2022). Is artificial intelligence improving the audit process?. *Review of Accounting Studies*. https://doi.org/10.1007/s11142-022-09697-x
3. Messod Daniel Beneish, Patrick Vorst (2021). The Cost of Fraud Prediction Errors. *The Accounting Review*. https://doi.org/10.2308/tar-2020-0068
4. Wu Xiuguo, Sheng-Yong Du (2022). An Analysis on Financial Statement Fraud Detection for Chinese Listed Companies Using Deep Learning. *IEEE Access*. https://doi.org/10.1109/access.2022.3153478
5. E-mails: dagundurome@pg.abuad.edu.ng1, falanaga@pg.abuad.edu.ng2, olayinkaadewara@pg.abuad.edu.ng3 busayoto@pg.abuad.edu.ng4   ORCID 0000-0002-1177-71011, ORCID 0000-0001-8512-67693, ORCID 0000-0003-0507-43944, Muyiwa Emmanuel Dagunduro et al. (2023). Application of Artificial Intelligence and Audit Quality in Nigeria. *Advances in Multidisciplinary & Scientific Research Journal Publication*. https://doi.org/10.22624/aims/humanities/v11n1p4
6. Alexander Bakumenko, Ahmed A. Elragal (2022). Detecting Anomalies in Financial Data Using Machine Learning Algorithms. *Systems*. https://doi.org/10.3390/systems10050130
7. Gopalan Puthukulam, Anitha Ravikumar, Ravi Vinod Kumar Sharma et al. (2021). Auditors' Perception on the Impact of Artificial Intelligence on Professional Skepticism and Judgment in Oman. *Universal Journal of Accounting and Finance*. https://doi.org/10.13189/ujaf.2021.090527
8. George Salijeni, Anna Samsonova‐Taddei, Stuart Turley (2018). Big Data and changes in audit technology: contemplating a research agenda. *Accounting and Business Research*. https://doi.org/10.1080/00014788.2018.1459458
9. Sutapat Thiprungsri, Miklos Antal Vasarhelyi (2011). Cluster Analysis for Anomaly Detection in Accounting Data: An Audit Approach. *The International Journal of Digital Accounting Research*. https://doi.org/10.4192/1577-8517-v11_4
10. Favourate Yelesedzani Mpofu (2023). The application of Artificial Intelligence in external auditing and its implications on audit quality? A review of the ongoing debates. *International Journal of Research in Business and Social Science (2147-4478)*. https://doi.org/10.20525/ijrbs.v12i9.2737
11. Scott A. Emett, Steven E. Kaplan, Elaine G. Mauldin et al. (2023). Auditing with data and analytics: External reviewers' judgments of audit quality and effort. *Contemporary Accounting Research*. https://doi.org/10.1111/1911-3846.12894
12. Johan L. Perols (2011). Financial Statement Fraud Detection: An Analysis of Statistical and Machine Learning Algorithms. *Auditing A Journal of Practice & Theory*. https://doi.org/10.2308/ajpt-50009
13. Faisal Khan, Sharif Ullah Jan, Hafiz Muhammad Zia‐ul‐haq (2024). Artificial intelligence adoption, audit quality and integrated financial reporting in GCC markets. *Asian Review of Accounting*. https://doi.org/10.1108/ara-03-2024-0085
14. Feiqi Huang, Won Gyun No, Miklos Antal Vasarhelyi et al. (2022). Audit data analytics, machine learning, and full population testing. *The Journal of Finance and Data Science*. https://doi.org/10.1016/j.jfds.2022.05.002
15. Derya Üçoğlu (2020). Current machine learning applications in accounting and auditing. *Pressacademia*. https://doi.org/10.17261/pressacademia.2020.1337
16. Vivek Shivram (2024). AUDITING WITH AI: A THEORETICAL FRAMEWORK FOR APPLYING MACHINE LEARNING ACROSS THE INTERNAL AUDIT LIFECYCLE. *EDPACS*. https://doi.org/10.1080/07366981.2024.2312025
17. Matthew J. Behrend, Sarfraz A. Khan, Young Woo Ko et al. (2020). Abnormal Audit Fees and Audit Quality: Evidence from the Korean Audit Market. *Journal of International Accounting Research*. https://doi.org/10.2308/jiar-18-053
18. Arpine Maghakyan, Henry Jarva, Lasse Niemi et al. (2024). The Effect of Audit Partner Digitalization Expertise on Audit Fees. *European Accounting Review*. https://doi.org/10.1080/09638180.2023.2298433
19. Marc Eulerich, Adi Masli, Jeffrey S. Pickerd et al. (2022). The Impact of Audit Technology on Audit Task Outcomes: Evidence for Technology‐Based Audit Techniques*. *Contemporary Accounting Research*. https://doi.org/10.1111/1911-3846.12847
20. Anna Maria Karmańska (2022). Artificial Intelligence in audit. *Prace Naukowe Uniwersytetu Ekonomicznego we Wrocławiu*. https://doi.org/10.15611/pn.2022.4.06
21. Michelle Hanlon, Gopal V. Krishnan, Lillian F. Mills (2012). Audit Fees and Book-Tax Differences. *Journal of the American Taxation Association*. https://doi.org/10.2308/atax-10184
22. Khaldoon Albitar, Ali Meftah Gerged, Hassan Yahia Kikhia et al. (2020). Auditing in times of social distancing: the effect of COVID-19 on auditing quality. *International Journal of Accounting and Information Management*. https://doi.org/10.1108/ijaim-08-2020-0128
23. Husam Aldamen, Janice Hollindale, Jennifer L. Ziegelmayer (2016). Female audit committee members and their influence on audit fees. *Accounting and Finance*. https://doi.org/10.1111/acfi.12248
24. Abdulalem Ali, Shukor Bin Abd Razak, Siti Hajar Othman et al. (2022). Financial Fraud Detection Based on Machine Learning: A Systematic Literature Review. *Applied Sciences*. https://doi.org/10.3390/app12199637
25. Matin N. Ashtiani, Bijan Raahemi (2021). Intelligent Fraud Detection in Financial Statements Using Machine Learning and Data Mining: A Systematic Literature Review. *IEEE Access*. https://doi.org/10.1109/access.2021.3096799
26. Ludivia Hernández Aros, Luisa Ximena Bustamante Molano, Fernando Gutiérrez-Portela et al. (2024). Financial fraud detection through the application of machine learning techniques: a literature review. *Humanities and Social Sciences Communications*. https://doi.org/10.1057/s41599-024-03606-0
27. Adrian Gepp, Martina K. Linnenluecke, Terrence J. O’Neill et al. (2018). Big data techniques in auditing research and practice: Current trends and future opportunities. *Journal of Accounting Literature*. https://doi.org/10.1016/j.acclit.2017.05.003
28. Albashrawi Mousa (2021). Detecting Financial Fraud Using Data Mining Techniques: A Decade Review from 2004 to 2015. *Journal of Data Science*. https://doi.org/10.6339/jds.201607_14(3).0010
29. Serhan Hamal, Özlem Şenvar (2021). Comparing performances and effectiveness of machine learning classifiers in detecting financial accounting fraud for Turkish SMEs. *International Journal of Computational Intelligence Systems*. https://doi.org/10.2991/ijcis.d.210203.007
30. Xiaowei Chen, C. Xiaoyu Zhai (2023). Bagging or boosting? Empirical evidence from financial statement fraud detection. *Accounting and Finance*. https://doi.org/10.1111/acfi.13159
31. Markus Goldstein, Seiichi Uchida (2016). A Comparative Evaluation of Unsupervised Anomaly Detection Algorithms for Multivariate Data. *PLoS ONE*. https://doi.org/10.1371/journal.pone.0152173
32. Richard J. Bolton, David J. Hand (2002). Statistical Fraud Detection: A Review. *Statistical Science*. https://doi.org/10.1214/ss/1042727940
33. Niklas Bussmann, Paolo Giudici, Dimitri Marinelli et al. (2020). Explainable AI in Fintech Risk Management. *Frontiers in Artificial Intelligence*. https://doi.org/10.3389/frai.2020.00026
34. Najmeddine Dhieb, Hakim Ghazzai, Hichem Besbes et al. (2020). A Secure AI-Driven Architecture for Automated Insurance Systems: Fraud Detection and Risk Measurement. *IEEE Access*. https://doi.org/10.1109/access.2020.2983300
35. Shimal Sh. Taher, Siddeeq Y. Ameen, Jihan A. Ahmed (2024). Advanced Fraud Detection in Blockchain Transactions: An Ensemble Learning and Explainable AI Approach. *Engineering Technology & Applied Science Research*. https://doi.org/10.48084/etasr.6641
36. Mui Kim Chu, Kevin Ow Yong (2021). Big Data Analytics for Business Intelligence in Accounting and Audit. *Open Journal of Social Sciences*. https://doi.org/10.4236/jss.2021.99004
37. Deepak Mane, Sunil Mahadev Sangve, Gopal Dadarao Upadhye et al. (2022). Detection of Anomaly using Machine Learning: A Comprehensive Survey. *International Journal of Emerging Technology and Advanced Engineering*. https://doi.org/10.46338/ijetae1122_15
38. Pilar Schummer, Alberto del Rio Ponce, Javier Serrano et al. (2024). Machine Learning-Based Network Anomaly Detection: Design, Implementation, and Evaluation. *AI*. https://doi.org/10.3390/ai5040143
39. Rita Samiolo, Crawford Spence, Dorothy Toh (2023). Auditor judgment in the fourth industrial revolution. *Contemporary Accounting Research*. https://doi.org/10.1111/1911-3846.12901
40. Othmar Manfred Lehner, Kim Ittonen, Hanna Silvola et al. (2022). Artificial intelligence based decision-making in accounting and auditing: ethical challenges and normative thinking. *Accounting Auditing & Accountability Journal*. https://doi.org/10.1108/aaaj-09-2020-4934
41. Masashi Goto (2023). Anticipatory innovation of professional services: The case of auditing and artificial intelligence. *Research Policy*. https://doi.org/10.1016/j.respol.2023.104828
42. Xiaoxing Li (2022). Behavioral challenges to professional skepticism in auditors’ data analytics journey. *Maandblad Voor Accountancy en Bedrijfseconomie*. https://doi.org/10.5117/mab.96.78525
43. Mark W. Nelson (2009). A Model and Literature Review of Professional Skepticism in Auditing. *Auditing A Journal of Practice & Theory*. https://doi.org/10.2308/aud.2009.28.2.1
44. Markus Jung, Mischa Seiter (2021). Towards a better understanding on mitigating algorithm aversion in forecasting: an experimental study. *Journal of Management Control*. https://doi.org/10.1007/s00187-021-00326-3
45. Sayed Alwee Hussnie Sayed Hussin, Takiah Mohd Iskandar, Norman Mohd Saleh et al. (2017). Professional Skepticism and Auditors’ Assessment of Misstatement Risks: The Moderating Effect of Experience and Time Budget Pressure. *Economics & Sociology*. https://doi.org/10.14254/2071-789x.2017/10-4/17
46. Ibrahim Filiz, Jan René Judek, Marco Lorenz et al. (2023). The extent of algorithm aversion in decision-making situations with varying gravity. *PLoS ONE*. https://doi.org/10.1371/journal.pone.0278751
47. Fauzia Agustina, Nurkholis Nurkholis, Mohamad Khoiru Rusydi (2021). Auditors’ professional skepticism and fraud detection. *International Journal of Research in Business and Social Science (2147-4478)*. https://doi.org/10.20525/ijrbs.v10i4.1214
48. Maciej Ciołek (2017). PROFESSIONAL SKEPTICISM IN AUDITING AND ITS CHARACTERISTICS. *Prace Naukowe Uniwersytetu Ekonomicznego we Wrocławiu*. https://doi.org/10.15611/pn.2017.474.03
49. Ling Lei Lisic, Linda A. Myers, Timothy A. Seidel et al. (2019). Does Audit Committee Accounting Expertise Help to Promote Audit Quality? Evidence from Auditor Reporting of Internal Control Weaknesses. *Contemporary Accounting Research*. https://doi.org/10.1111/1911-3846.12517
50. Esther Kaufmann (2021). Algorithm appreciation or aversion? Comparing in-service and pre-service teachers’ acceptance of computerized expert models. *Computers and Education Artificial Intelligence*. https://doi.org/10.1016/j.caeai.2021.100028
51. I Ketut Jati, Herkulanus Bambang Suprasto (2020). Time budget pressure on audit quality with audit structure, independence, and audit supervision as moderating variable. *International Research Journal of Management IT and Social Sciences*. https://doi.org/10.21744/irjmis.v7n6.997
52. Nguyen Thi Mai Anh, Le Thi Khanh Hoa, Lai Phuong Thao et al. (2024). The Effect of Technology Readiness on Adopting Artificial Intelligence in Accounting and Auditing in Vietnam. *Journal of risk and financial management*. https://doi.org/10.3390/jrfm17010027
53. Max Gotthardt, Dan Koivulaakso, Okyanus Paksoy et al. (2020). Current State and Challenges in the Implementation of Smart Robotic Process Automation in Accounting and Auditing. *ACRN Journal of Finance and Risk Perspectives*. https://doi.org/10.35944/jofrp.2020.9.1.007
54. Michael Bücker, Gero Szepannek, Alicja Gosiewska et al. (2020). Transparency, Auditability and eXplainability of Machine Learning Models in Credit Scoring. *arXiv (Cornell University)*. https://doi.org/10.1080/01605682.2021.1922098
55. Khairina Rosli, Paul H.P. Yeow, Eu-Gene Siew (2012). Factors Influencing Audit Technology Acceptance by Audit Firms: A New I-TOE Adoption Framework. *Journal of Accounting and Auditing Research & Practice*. https://doi.org/10.5171/2012.876814
56. Angelika Adensamer, Rita Gsenger, Lukas Daniel Klausner (2021). “Computer says no”: Algorithmic decision support and organisational responsibility. *Journal of Responsible Technology*. https://doi.org/10.1016/j.jrt.2021.100014
57. Sebastian G. Fritz-Morgenthal, Bernhard Hein, Jochen Papenbrock (2022). Financial Risk Management and Explainable, Trustworthy, Responsible AI. *Frontiers in Artificial Intelligence*. https://doi.org/10.3389/frai.2022.779799
58. Stephan Grimmelikhuijsen (2022). Explaining Why the Computer Says No: Algorithmic Transparency Affects the Perceived Trustworthiness of Automated Decision‐Making. *Public Administration Review*. https://doi.org/10.1111/puar.13483
59. Rudresh Dwivedi, Devam Dave, Het Naik et al. (2022). Explainable AI (XAI): Core Ideas, Techniques, and Solutions. *ACM Computing Surveys*. https://doi.org/10.1145/3561048
60. Hans de Bruijn, Martijn Warnier, Marijn Janssen (2021). The perils and pitfalls of explainable AI: Strategies for explaining algorithmic decision-making. *Government Information Quarterly*. https://doi.org/10.1016/j.giq.2021.101666
