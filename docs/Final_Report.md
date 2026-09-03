# A HYBRID SMOTE-TOMEK AND BAYESIAN-OPTIMIZED SVM FRAMEWORK FOR INTERPRETABLE AIR QUALITY CLASSIFICATION IN URBAN ZAMBIA

---

**Copperbelt University**

**School of Graduate Studies and Research / Department of Computer Science**

---

A dissertation submitted in partial fulfilment of the requirements for the degree of Bachelor of Science in Computer Science (CS 400)

---

**Submitted by:** Muzipase Tembo — Student ID: 22107085

**Supervisor:** Dr. George Mufungulwa

**August 2026**

---

## DECLARATION

I, **Muzipase Tembo** (Student ID: 22107085), hereby declare that this dissertation entitled *"A Hybrid SMOTE-Tomek and Bayesian-Optimized SVM Framework for Interpretable Air Quality Classification in Urban Zambia"* is my own original work and has not been submitted, in whole or in part, for any other degree or examination at this or any other university. All sources of information used herein have been duly acknowledged by means of complete references.

Signature: ______________________  Date: ______________________

## COPYRIGHT

All rights reserved. No part of this dissertation may be reproduced, stored in any retrieval system, or transmitted in any form or by any means — electronic, mechanical, photocopying, recording, or otherwise — without prior written permission of the author or The Copperbelt University.

© 2026 Muzipase Tembo

## APPROVAL

This dissertation of **Muzipase Tembo** is approved as fulfilling part of the requirements for the award of the degree of Bachelor of Science in Computer Science of The Copperbelt University.

Examiner 1: ______________________  Signature: ____________  Date: ____________

Examiner 2: ______________________  Signature: ____________  Date: ____________

Supervisor: **Dr. George Mufungulwa**  Signature: ____________  Date: ____________

Head of Department: ______________________  Signature: ____________  Date: ____________

## CERTIFICATE

This is to certify that the work contained in this dissertation was carried out by **Muzipase Tembo** (Student ID: 22107085) under my supervision, in the Department of Computer Science, The Copperbelt University, and has been submitted for examination with my approval as the university supervisor.

Supervisor: **Dr. George Mufungulwa**

Signature: ______________________  Date: ______________________

## DEDICATION

This work is dedicated to my family, whose unwavering support, patience, and encouragement sustained me throughout my studies, and to the residents of Lusaka, Kitwe, and Ndola, who live daily with the air quality challenges this research seeks to address.

## ACKNOWLEDGEMENTS

First and foremost, I give thanks to the Almighty God for the gift of life, health, and strength throughout this academic journey.

I wish to express my sincere gratitude to my supervisor, **Dr. George Mufungulwa**, for his invaluable guidance, constructive criticism, and mentorship at every stage of this project. His insight into machine learning methodology shaped both the direction and rigour of this work.

I thank the Department of Computer Science at The Copperbelt University for providing the academic foundation and computing resources that made this research possible. I also acknowledge the maintainers of the Open-Meteo and Open-AQ platforms, whose open application programming interfaces (APIs) made multi-year air quality data for Zambian cities freely accessible.

Finally, I am deeply grateful to my family and friends for their moral and financial support, and to my classmates for their camaraderie and feedback during laboratory sessions.

## SYNOPSIS (ABSTRACT)

Air pollution is a leading environmental health risk in rapidly urbanizing African cities, yet automated air quality classification remains under-explored in the Zambian context. This project designed, implemented, and evaluated a hybrid machine learning framework that classifies hourly air quality observations from three Zambian cities — **Lusaka, Kitwe, and Ndola** — into health-based Air Quality Index (AQI) categories using an interpretable Support Vector Machine (SVM).

Hourly pollutant concentrations (PM2.5, PM10, NO₂, SO₂, CO, O₃) and meteorological variables (temperature, humidity, wind speed, rainfall) were ingested programmatically from the **Open-Meteo Air Quality and Archive APIs**, with the **OpenAQ platform** used as a secondary source, yielding **89,928 raw records** covering August 2022 to December 2025. After cleaning, median imputation, feature engineering, and min-max scaling, **89,706 labelled records** were retained across four observed AQI classes. The dataset exhibits severe class imbalance (majority-to-minority ratio of approximately **146 : 1**), which was addressed by applying a hybrid **SMOTE-Tomek** resampling strategy exclusively to the training partition. Hyperparameters of an RBF-kernel SVM were then tuned with **Bayesian optimization** (Tree-structured Parzen Estimator, implemented in Optuna) against macro-averaged recall under stratified cross-validation.

The final hybrid model achieved an accuracy of **98.48%** and an F1-score of **0.9849**, compared with **97.77%** and **0.9775** for a default-parameter baseline trained on the imbalanced data. The most consequential gains occurred in minority classes: recall for *Very Unhealthy* rose from **0.694 to 0.972** (+27.8 percentage points) and for *Unhealthy* from **0.861 to 0.984** (+12.3 percentage points). Model transparency was provided through **SHAP (KernelExplainer)** analysis, which identified PM2.5, PM10, and a composite pollution-load feature as the dominant drivers of classification decisions. The framework is exposed through a documented **FastAPI** service layer and consumed by two front ends — a **Streamlit** analytical dashboard and an installable **Next.js Progressive Web Application (PWA)** — demonstrating a complete, reproducible, and deployable intelligent air quality monitoring system for urban Zambia.

**Keywords:** air quality classification, class imbalance, SMOTE-Tomek, Bayesian optimization, support vector machine, SHAP explainability, FastAPI, progressive web application, Zambia.

## TABLE OF CONTENTS

Declaration ........................................................ i
Copyright ........................................................ ii
Approval ........................................................ iii
Certificate ........................................................ iv
Dedication ........................................................ v
Acknowledgements ........................................................ vi
Synopsis ........................................................ vii
Table of Contents ........................................................ viii
List of Tables ........................................................ x
List of Figures ........................................................ xi
List of Abbreviations ........................................................ xii

**Chapter 1: Introduction** ........................................................ 1
1.1 Background ........................................................ 1
1.2 Problem Statement ........................................................ 2
1.3 Aim and Objectives ........................................................ 3
1.4 Research Questions ........................................................ 3
1.5 Significance of the Study ........................................................ 4
1.6 Scope and Limitations ........................................................ 4
1.7 Definition of Terms ........................................................ 5
1.8 Dissertation Organization ........................................................ 5

**Chapter 2: Literature Review** ........................................................ 6
2.1 Introduction ........................................................ 6
2.2 Air Quality Monitoring and the AQI Framework ........................................................ 6
2.3 Machine Learning for Air Quality Classification ........................................................ 7
2.4 Support Vector Machines ........................................................ 7
2.5 The Class Imbalance Problem ........................................................ 8
2.6 SMOTE-Tomek Hybrid Resampling ........................................................ 9
2.7 Hyperparameter Optimization and Bayesian Methods ........................................................ 9
2.8 Previous Systems or Similar Applications ........................................................ 10
2.9 Explainable AI (SHAP) ........................................................ 12
2.10 Research Gap ........................................................ 12
2.11 Summary ........................................................ 13

**Chapter 3: Research Methodology and System Analysis** ........................................................ 14
3.1 Introduction ........................................................ 14
3.2 Development Methodology ........................................................ 14
3.3 Requirements Analysis ........................................................ 15
3.4 System Actors and Use Cases ........................................................ 17
3.5 Dataset Description and Analysis ........................................................ 18
3.6 Data Preprocessing Pipeline ........................................................ 21
3.7 Class Balancing Strategy ........................................................ 23
3.8 Model Selection and Hyperparameter Optimization ........................................................ 24
3.9 Evaluation Strategy ........................................................ 25

**Chapter 4: System Design** ........................................................ 27
4.1 Introduction ........................................................ 27
4.2 System Architecture ........................................................ 27
4.3 Use Case Design ........................................................ 29
4.4 Class Design ........................................................ 30
4.5 Sequence Design ........................................................ 31
4.6 Activity Design ........................................................ 32
4.7 Data Flow and Artifact Design ........................................................ 33
4.8 User Interface Design ........................................................ 34

**Chapter 5: Implementation** ........................................................ 37
5.1 Introduction ........................................................ 37
5.2 Technology Stack ........................................................ 37
5.3 Module Implementation Map ........................................................ 38
5.4 Data Ingestion Layer ........................................................ 40
5.5 Preprocessing and Balancing Implementation ........................................................ 41
5.6 Model Training and Optimization Implementation ........................................................ 42
5.7 API Service Layer ........................................................ 43
5.8 Front-End Implementation ........................................................ 44
5.9 Deployment ........................................................ 45

**Chapter 6: System Testing** ........................................................ 47
6.1 Introduction ........................................................ 47
6.2 Unit Testing ........................................................ 47
6.3 Integration and API Testing ........................................................ 49
6.4 User Acceptance Considerations ........................................................ 49

**Chapter 7: Results and Discussion** ........................................................ 51
7.1 Introduction ........................................................ 51
7.2 Dataset Outcomes ........................................................ 51
7.3 Overall Model Performance ........................................................ 52
7.4 Per-Class Performance and the Effect of Balancing ........................................................ 53
7.5 Confusion Matrix Analysis ........................................................ 55
7.6 Model Interpretation with SHAP ........................................................ 56
7.7 Discussion ........................................................ 57
7.8 Threats to Validity and Limitations ........................................................ 58

**Chapter 8: Conclusion, Recommendations, and Future Work** ........................................................ 60
8.1 Conclusion ........................................................ 60
8.2 Recommendations ........................................................ 61
8.3 Future Work ........................................................ 61

References ........................................................ 63
Appendix A: Selected Source Code Listings ........................................................ 66
Appendix B: Dataset Description ........................................................ 70
Appendix C: Detailed Experiment Results ........................................................ 72
Appendix D: SHAP Explanation Results ........................................................ 74
Appendix E: User Manual (Quick Start) ........................................................ 75

*(Page numbers are indicative and should be refreshed after final typesetting in Word/LaTeX.)*

## LIST OF TABLES

- Table 3.1 — Functional requirements
- Table 3.2 — Non-functional requirements
- Table 3.3 — Dataset summary statistics
- Table 3.4 — AQI class distribution and imbalance ratios
- Table 3.5 — Engineered feature definitions
- Table 3.6 — Bayesian optimization search space
- Table 6.1 — Unit test suite inventory
- Table 7.1 — Overall performance: baseline vs hybrid model
- Table 7.2 — Per-class metrics: baseline model
- Table 7.3 — Per-class metrics: hybrid (SMOTE-Tomek + BO-SVM) model
- Table 7.4 — Recall improvement by class
- Table 7.5 — Top SHAP features per AQI class
- Table B.1 — Raw dataset schema (Appendix B)

## LIST OF FIGURES

- Figure 3.1 — System use case diagram *(insert rendered diagram)*
- Figure 3.2 — Class distribution before resampling *(generated from processed_data.csv)*
- Figure 4.1 — Three-tier system architecture
- Figure 4.2 — Sequence diagram: prediction request lifecycle
- Figure 4.3 — Data flow diagram of the ML pipeline
- Figure 4.4 — Activity diagram: end-to-end pipeline execution
- Figure 4.5 — Streamlit dashboard wireframe
- Figure 4.6 — PWA home screen wireframe
- Figure 5.1 — Project repository structure
- Figure 7.1 — Baseline vs optimized overall metrics *(from artifacts/comparison.json)*
- Figure 7.2 — Per-class recall comparison chart
- Figure 7.3 — Confusion matrix: baseline model *(artifacts/confusion_matrix.json)*
- Figure 7.4 — Confusion matrix: optimized model
- Figure 7.5 — SHAP beeswarm summary plot *(artifacts/shap_plots/shap_beeswarm.png)*
- Figure G.1 — Project Gantt chart *(see Chapter 1 note / Appendix E)*

## LIST OF ABBREVIATIONS

| Abbreviation | Meaning |
|---|---|
| AQG | Air Quality Guidelines (WHO) |
| AQI | Air Quality Index |
| API | Application Programming Interface |
| BO | Bayesian Optimization |
| CSV | Comma-Separated Values |
| CV | Cross-Validation |
| ETL | Extract, Transform, Load |
| FN / FP | False Negative / False Positive |
| GP | Gaussian Process |
| JSON | JavaScript Object Notation |
| ML | Machine Learning |
| NO₂ | Nitrogen Dioxide |
| O₃ | Ground-level Ozone |
| PWA | Progressive Web Application |
| PM2.5 / PM10 | Particulate Matter ≤ 2.5 µm / ≤ 10 µm |
| REST | Representational State Transfer |
| RBF | Radial Basis Function |
| ROC | Receiver Operating Characteristic |
| SHAP | SHapley Additive exPlanations |
| SMOTE | Synthetic Minority Over-sampling Technique |
| SO₂ | Sulphur Dioxide |
| SVC | Support Vector Classifier |
| SVM | Support Vector Machine |
| TPE | Tree-structured Parzen Estimator |
| UI / UX | User Interface / User Experience |
| VIF | Variance Inflation Factor |
| WHO | World Health Organization |
| ZEMA | Zambia Environmental Management Agency |

# CHAPTER 1: INTRODUCTION

## 1.1 Background

Rapid urbanization, motorization, and industrial activity — including copper smelting on the Copperbelt — have made ambient air pollution one of the most pressing environmental health risks in Zambian cities. Fine particulate matter (PM2.5) and coarse particulate matter (PM10) frequently exceed the World Health Organization (WHO) guideline values in Lusaka, Kitwe, and Ndola, particularly during the dry season (May–August), when dust, biomass burning, and temperature inversions coincide.

Despite the severity of exposure, air quality information in Zambia is largely reactive: regulatory bulletins and sparse ground stations publish summaries long after pollution episodes occur, and ordinary citizens rarely receive timely, interpretable guidance such as "air quality is Unhealthy for sensitive groups today." International platforms (e.g., IQAir, OpenAQ) aggregate some Zambian measurements, but they stop short of delivering locally calibrated, machine-learning-driven classification with transparent explanations.

Machine learning offers a path from raw sensor telemetry to actionable health categories. Among classifiers, the **Support Vector Machine (SVM)** is well suited to tabular environmental data: it performs well on medium-sized datasets, handles non-linear decision boundaries through kernel functions, and generalizes robustly when features are properly scaled. However, two obstacles must be overcome in practice:

1. **Class imbalance.** Healthy-air observations vastly outnumber hazardous episodes, so a naive classifier achieves high accuracy while failing catastrophically on the rare, dangerous classes that matter most for public health.
2. **Opacity.** Health authorities are unlikely to trust a black-box model; classification decisions must be explainable feature-by-feature.

This project addresses both obstacles with a hybrid framework: **SMOTE-Tomek hybrid resampling** to rebalance the training distribution, **Bayesian optimization** (TPE sampler) to tune the SVM hyperparameters against a minority-sensitive objective, and **SHAP** explanations to make every prediction auditable. The framework is operationalized as a production-style system: a FastAPI back end, a Streamlit analytics dashboard, and an installable Next.js Progressive Web App for public users.

## 1.2 Problem Statement

Existing air quality reporting for Zambian urban areas suffers from three interrelated deficiencies:

- **Sparse and delayed dissemination.** There is no public, real-time system that converts continuous pollutant measurements from Lusaka, Kitwe, and Ndola into standardized AQI health categories.
- **Class imbalance neglect.** Pollution episodes (Unhealthy and above) are statistically rare; conventional classifiers trained on raw distributions achieve deceptively high accuracy while misclassifying precisely those episodes that threaten human health.
- **Lack of interpretability.** Where predictive models exist, their decisions are opaque, undermining trust and preventing domain experts from verifying that predictions rest on scientifically meaningful drivers (e.g., PM2.5 spikes).

Consequently, there is a need for an accurate, imbalance-aware, and interpretable classification framework, delivered through accessible software, that can translate open air quality data into trustworthy health guidance for Zambian cities.

## 1.3 Aim and Objectives

**Aim.** To develop and evaluate a hybrid SMOTE-Tomek and Bayesian-optimized SVM framework for accurate, interpretable classification of air quality in urban Zambia.

**Objectives.**

1. To acquire and preprocess multi-year hourly air quality and meteorological data for Lusaka, Kitwe, and Ndola from open APIs (Open-Meteo, OpenAQ).
2. To characterize the resulting dataset, including its class distribution and degree of imbalance.
3. To implement a SMOTE-Tomek hybrid resampling strategy that mitigates class imbalance without contaminating the test partition.
4. To tune RBF-SVM hyperparameters using Bayesian optimization (TPE) with a macro-recall objective under cross-validation.
5. To evaluate the hybrid model against a default baseline using accuracy, precision, recall, F1-score, per-class metrics, and confusion matrices.
6. To interpret model decisions using SHAP value analysis.
7. To deliver the framework through a REST API and two user-facing applications (Streamlit dashboard and PWA).

## 1.4 Research Questions

1. What is the composition and class balance of multi-year open air quality data for Lusaka, Kitwe, and Ndola?
2. Does SMOTE-Tomek resampling of the training partition improve minority-class recognition in AQI classification?
3. Does Bayesian hyperparameter optimization outperform default SVM settings on macro-averaged metrics?
4. Which features drive the model's classifications, as quantified by SHAP?
5. Can the resulting model be served reliably through a web-accessible software system?

## 1.5 Significance of the Study

- **Public health:** earlier, more reliable detection of Unhealthy and Very Unhealthy episodes enables timely advisories for schools, hospitals, and outdoor workers.
- **Scientific:** provides one of the first openly documented, reproducible imbalance-aware AQI classification pipelines calibrated on Zambian data.
- **Policy:** demonstrates that freely available open data (Open-Meteo, OpenAQ) can substitute for expensive proprietary sensing infrastructure in low-resource settings.
- **Educational:** the modular codebase (`src/` packages, pytest suite, containerized deployment) serves as a reference implementation for applied ML engineering at CBU.

## 1.6 Scope and Limitations

**In scope:** supervised classification of hourly observations into AQI categories; open-data ingestion for three cities (Aug 2022 – Dec 2025); classical ML (SVM) with resampling and Bayesian tuning; SHAP explanation; REST API + two front ends; containerized deployment configuration.

**Limitations.**

1. **No Hazardous observations.** The study window contains zero samples exceeding the Hazardous threshold (PM2.5 > 250.4 µg/m³); the deployed label space therefore comprises four classes. Hazardous behaviour is extrapolated, not learned.
2. **Modelled input data.** Open-Meteo pollutant series are reanalysis/model-assimilated estimates rather than direct regulatory-grade monitors; conclusions inherit their biases.
3. **Very Unhealthy support is small** (358 records; 72 in test), so its metrics carry wide uncertainty.
4. **Scaler fitted before splitting.** The min-max scaler is fitted on the full preprocessed feature matrix prior to the train/test split — a mild information leak typical of pipeline-first prototypes; future work should wrap scaling inside the CV folds.
5. **Single geographic climate zone.** Generalization to other Zambian regions (e.g., Livingstone) is untested.

## 1.7 Definition of Terms

- **Air Quality Index (AQI):** a categorical scale translating pollutant concentrations into health-relevant bands (Good, Moderate, Unhealthy, Very Unhealthy, Hazardous).
- **SMOTE:** Synthetic Minority Over-sampling Technique; creates synthetic minority samples by interpolating between neighbours.
- **Tomek links:** pairs of nearest-neighbour samples from opposite classes; removing them cleans class boundaries.
- **Bayesian optimization:** sequential model-based optimization that uses a probabilistic surrogate (here, the Tree-structured Parzen Estimator) to select promising hyperparameter configurations.
- **SHAP values:** Shapley-value-based attributions that distribute a prediction among input features.
- **Macro recall:** the unweighted mean of per-class recall, giving minority classes equal weight.
- **PWA:** Progressive Web Application — a web app installable on devices with offline caching via a service worker.

## 1.8 Dissertation Organization

Chapter 2 reviews related literature and systems. Chapter 3 presents the methodology, requirements, and dataset analysis. Chapter 4 details the system design. Chapter 5 describes implementation. Chapter 6 covers testing. Chapter 7 reports and discusses results. Chapter 8 concludes with recommendations and future work. Appendices provide code listings, dataset documentation, extended results, SHAP outputs, and a user manual.

# CHAPTER 2: LITERATURE REVIEW

## 2.1 Introduction

This chapter reviews the conceptual and empirical foundations of the project: air quality indices, machine learning approaches to air quality classification, SVM theory, the class imbalance problem and resampling remedies, Bayesian hyperparameter optimization, explainability, and finally comparable existing systems, closing with the identified research gap.

## 2.2 Air Quality Monitoring and the AQI Framework

The WHO updates its Air Quality Guidelines to reflect evidence that even low concentrations of PM2.5 harm health. National environmental agencies convert continuous concentrations into index bands using breakpoint tables; this project adopts the widely used US-EPA-style breakpoints for PM2.5 (Good ≤ 12.0, Moderate ≤ 35.4, Unhealthy ≤ 55.4, Very Unhealthy ≤ 150.4, Hazardous > 250.4 µg/m³), which map naturally onto a supervised classification target. In Sub-Saharan Africa, regulatory monitoring networks remain sparse; studies consistently report reliance on low-cost sensors, satellite retrievals, and modelled reanalysis products — the approach adopted here through Open-Meteo's assimilated air quality series.

## 2.3 Machine Learning for Air Quality Classification

Prior work applies logistic regression, decision trees, random forests, gradient boosting, neural networks, and SVMs to classify or forecast AQI bands. Reported findings indicate: (i) non-linear kernels generally outperform linear models on pollutant tabular data; (ii) tree ensembles are competitive but less stable under severe imbalance without resampling; (iii) meteorological covariates (wind speed, humidity, temperature, rainfall) measurably improve discrimination of pollution episodes. Few studies, however, target Southern African cities, and fewer still release reproducible pipelines.

## 2.4 Support Vector Machines

Cortes and Vapnik formalized the SVM as a maximum-margin classifier; the soft-margin formulation introduces the penalty parameter **C**, balancing margin width against misclassification. The **kernel trick** (notably the Radial Basis Function, RBF, with bandwidth parameter **gamma**) permits implicit non-linear feature spaces. SVM performance is notoriously sensitive to (C, gamma); grid search is exponential in cost, motivating guided search strategies. Probability calibration (Platt scaling) is possible but computationally costly for large samples, so this project relies on decision-function outputs internally and class probabilities only where explicitly needed.

## 2.5 The Class Imbalance Problem

Imbalanced learning literature distinguishes **data-level** solutions (resampling) from **algorithm-level** solutions (cost-sensitive losses, threshold moving, ensemble methods). Accuracy and micro-averaged metrics are misleading under imbalance; macro-averaged recall/F1 and per-class recall are recommended. He and Garcia's survey remains the canonical reference; subsequent work emphasizes that over-sampling alone can overfit by duplicating borderline points, motivating hybrid over-sampling + cleaning methods.

## 2.6 SMOTE-Tomek Hybrid Resampling

**SMOTE** (Chawla et al., 2002) synthesizes minority examples along segments joining minority samples to their k nearest minority neighbours. **Tomek links** (Tomek, 1976) identify nearest-neighbour pairs of opposite classes; deleting the majority member (or both) scours ambiguous boundary regions. Combining them — `SMOTETomek` in the imbalanced-learn library — yields denser, cleaner minority regions than either technique alone. Crucially, resampling must be confined to the **training fold** to avoid leaking synthetic knowledge into evaluation; this project enforces that discipline in `scripts/run_pipeline.py`.

## 2.7 Hyperparameter Optimization and Bayesian Methods

Random and grid searches waste evaluations on unpromising regions. Bayesian optimization builds a surrogate of the objective and acquires candidates by predicted improvement. The **Tree-structured Parzen Estimator** (Bergstra et al., 2011) models p(x|y) non-parametrically and handles mixed discrete/continuous spaces efficiently; it is the default sampler in **Optuna** (Akiba et al., 2019), an open-source HPO framework with pruning (e.g., MedianPruner) and seeding for reproducibility. Compared to Gaussian-process methods, TPE scales better with categorical dimensions such as kernel choice — relevant here since the search space includes {rbf, poly} kernels and categorical gamma modes.

## 2.8 Previous Systems or Similar Applications

### 2.8.1 IQAir (AirVisual)

IQAir is a commercial global air quality platform aggregating data from tens of thousands of stations and low-cost sensors, offering real-time AQI display, forecasts, and historical charts, with mobile apps and an API. **Strengths:** global coverage, polished UX, dense station network in developed regions. **Weaknesses for this project's context:** coverage of Zambian cities depends on sparse monitor availability; classification thresholds are fixed and not locally recalibrated; underlying models are proprietary and unexplained; no mechanism for researchers to inject custom classifiers or resampling strategies.

### 2.8.2 OpenAQ

OpenAQ is an open-data initiative harmonizing government and research-grade air quality measurements behind a uniform REST API. It dramatically lowers the barrier to obtaining Zambian measurements. **Strengths:** open licensing, standardized schema, programmatic access. **Weaknesses:** it is a data repository, not a modelling layer — it provides no AQI classification model, no imbalance handling, no explanations, and its coverage in Zambia is intermittent (as encountered during development, motivating Open-Meteo as the primary source in this project).

### 2.8.3 ZEMA Environmental Portal

The Zambia Environmental Management Agency publishes regulatory reports and bulletins on environmental conditions, including air quality around mining and industrial areas. **Strengths:** official mandate, local authority, compliance framing. **Weaknesses:** dissemination is document-centric and periodic rather than real-time; no machine-readable API; no per-hour classification or public advisory tooling; no interactive city-level dashboards.

### 2.8.4 Comparative Summary and Positioning

| Capability | IQAir | OpenAQ | ZEMA portal | **This project** |
|---|---|---|---|---|
| Real-time AQI display | Yes | Data only | Reports only | Yes (API + 2 front ends) |
| Zambian city focus | Partial | Partial | Yes | Yes (Lusaka, Kitwe, Ndola) |
| ML-based classification | Proprietary | None | None | SMOTE-Tomek + BO-SVM |
| Imbalance handling | Undisclosed | N/A | N/A | Hybrid resampling, train-only |
| Explainability | None | N/A | N/A | SHAP per-class importances |
| Open/reproducible pipeline | No | Data only | No | Full source + artifacts |

None of the surveyed systems combines local open data, imbalance-aware learning, transparent explanations, and an accessible delivery layer for Zambian users — the niche this project fills.

## 2.9 Explainable AI (SHAP)

Lundberg and Lee unified attribution methods under Shapley values from cooperative game theory; **SHAP** computes each feature's additive contribution to a prediction relative to a background distribution. For non-linear models like SVMs, **KernelExplainer** approximates Shapley values model-agnostically; summarizing absolute SHAP magnitudes across samples yields global feature importance, while conditioning on true labels yields per-class driver profiles — exactly the audit trail health authorities require. Summarizing background data with k-means centroids reduces computation from prohibitive to practical, the strategy adopted in `src/explainability/shap_explainer.py`.

## 2.10 Research Gap

From the reviewed literature: (1) African, and specifically Zambian, urban AQI classification is under-studied with few reproducible artefacts; (2) hybrid resampling + Bayesian-tuned SVMs are rarely evaluated together on real open air quality data; (3) published pipelines seldom couple modelling with explainability and a deployable product surface. This project addresses all three gaps.

## 2.11 Summary

The theoretical toolkit — AQI breakpoints, RBF-SVM, SMOTE-Tomek, TPE-based Bayesian optimization, SHAP — is mature individually, but their integration for urban Zambia is novel. The next chapter specifies how these components were engineered into a coherent methodology.

# CHAPTER 3: RESEARCH METHODOLOGY AND SYSTEM ANALYSIS

## 3.1 Introduction

This chapter describes the development methodology, elicited requirements, system actors, and — centrally — the dataset acquired for the study, including its composition, quality treatment, and imbalance characteristics, followed by the modelling and evaluation protocols.

## 3.2 Development Methodology

An **incremental/iterative (Agile-inspired)** methodology was adopted. Each iteration delivered a vertical slice: ingestion → preprocessing → modelling → evaluation → exposure through the API/UI. Version control (Git) tracked every change; artifacts (metrics JSON, plots, pickled models) were regenerated deterministically by a single entry point, `scripts/run_pipeline.py`, using fixed random seeds (42) throughout. This "pipeline-as-artifact" discipline ensured that every number reported in Chapter 7 can be reproduced from the repository.

## 3.3 Requirements Analysis

### 3.3.1 Functional Requirements

**Table 3.1 — Functional requirements**

| ID | Requirement |
|---|---|
| FR1 | Fetch hourly pollutant data (PM2.5, PM10, NO₂, SO₂, CO, O₃) for Lusaka, Kitwe, Ndola from Open-Meteo/OpenAQ APIs |
| FR2 | Fetch coincident meteorological variables (temperature, humidity, wind speed, rainfall) |
| FR3 | Clean data: normalize columns, remove duplicates, drop fully invalid rows |
| FR4 | Impute missing numeric values (median strategy) |
| FR5 | Engineer features: AQI label, PM2.5/PM10 ratio, pollution load, high-pollution flags, temporal attributes |
| FR6 | Scale numeric features (min-max) and persist the fitted scaler |
| FR7 | Check multicollinearity (VIF) among candidate features |
| FR8 | Partition data into stratified 80/20 train/test sets (seed = 42) |
| FR9 | Apply SMOTE-Tomek resampling to the training partition only |
| FR10 | Train a baseline RBF-SVM on the imbalanced training data |
| FR11 | Tune an SVM via Bayesian optimization (TPE, macro-recall objective, CV) and refit on balanced data |
| FR12 | Evaluate both models: accuracy, precision, recall, F1, per-class metrics, confusion matrices |
| FR13 | Produce SHAP explanations: global beeswarm and per-class top features |
| FR14 | Persist all artifacts (models, scaler, metrics JSON, plots) to disk |
| FR15 | Expose functionality via REST endpoints (fetch, preprocess, train, predict, evaluate, explain) |
| FR16 | Provide interactive front ends (Streamlit dashboard; installable PWA) with city selection and live prediction |

### 3.3.2 Non-Functional Requirements

**Table 3.2 — Non-functional requirements**

| ID | Category | Requirement |
|---|---|---|
| NFR1 | Reproducibility | Fixed seeds; single-command pipeline; versioned artifacts |
| NFR2 | Performance | Interactive endpoints respond < 2 s on cached models; training subsampled to ≤ 30,000 rows for tractability |
| NFR3 | Usability | Dashboards usable without technical training; responsive layout; PWA installability |
| NFR4 | Reliability | API retries with exponential backoff on fetch failures; graceful degradation when artifacts absent |
| NFR5 | Maintainability | Package-per-concern structure (`src/ingestion`, `src/preprocessing`, `src/balancing`, `src/models`, `src/optimization`, `src/evaluation`, `src/explainability`, `src/visualization`) |
| NFR6 | Testability | pytest unit suite covering clients, preprocessing, balancing, optimizer, SVM, SHAP |
| NFR7 | Portability | Docker image; Render deployment manifest; Vercel frontend config |
| NFR8 | Security | CORS-restricted API; secrets via environment variables (`.env.example` provided) |

## 3.4 System Actors and Use Cases

Actors: **Public User** (views current AQI, trends, forecasts; installs PWA), **Analyst/Researcher** (triggers pipeline stages, uploads/downloads data, inspects metrics and SHAP), **System/API Client** (programmatic access), **External Data Providers** (Open-Meteo, OpenAQ).

Primary use cases: View Current Air Quality; Select City; View Forecast/History; Run Data Pipeline; Train Models; Evaluate Models; Predict AQI Category; Explain Prediction; Manage Alerts *(planned)*.

*[Insert Figure 3.1 — System use case diagram]*

## 3.5 Dataset Description and Analysis

### 3.5.1 Sources and Acquisition

Data were acquired programmatically (Section 5.4) from:

- **Open-Meteo Air Quality API** (`https://air-quality-api.open-meteo.com/v1/air-quality`) — hourly pollutant concentrations;
- **Open-Meteo Archive API** (`https://archive-api.open-meteo.com/v1/archive`) — hourly weather (temperature, humidity, wind speed, precipitation);
- **OpenAQ** (`https://api.openaq.org/v2/measurements`) — secondary/verification source for ground measurements.

Study locations (city centroid coordinates):

| City | Latitude | Longitude |
|---|---|---|
| Lusaka | −15.3875 | 28.3228 |
| Ndola | −12.8000 | 28.2167 |
| Kitwe | −10.8833 | 27.7833 |

Historical retrieval spanned **2022-08-01 to 2025-12-31**, downloaded in six-month chunks per city with concurrent requests and retry/back-off error handling.

### 3.5.2 Dataset Composition

**Table 3.3 — Dataset summary statistics**

| Property | Value |
|---|---|
| Raw records fetched | **89,928** |
| Records after cleaning/imputation | **89,706** |
| Temporal resolution | Hourly |
| Coverage | 2022-08-01 → 2025-12-31 |
| Cities | 3 (Lusaka, Kitwe, Ndola) |
| Base pollutants | PM2.5, PM10, NO₂, SO₂, CO, O₃ |
| Meteorological covariates | Temperature, Humidity, Wind speed, Rainfall |
| Raw schema width | 14 columns |
| Final feature matrix | 14 numeric features (after exclusions) |
| Label | `aqi_category` (4 observed classes) |

Raw schema: `location, city, country, timestamp, pm25, pm10, no2, so2, co, o3, temperature, humidity, wind_speed, rainfall`.

### 3.5.3 Target Construction

Labels derive from PM2.5 against US-EPA-style breakpoints (PM10/2 substitutes where PM2.5 is unavailable):

score ≤ 12 → **Good**; ≤ 35.4 → **Moderate**; ≤ 55.4 → **Unhealthy**; ≤ 150.4 → **Very Unhealthy**; > 250.4 → **Hazardous**.

### 3.5.4 Class Distribution and Imbalance Analysis

**Table 3.4 — Observed class distribution (processed dataset, n = 89,706)**

| AQI class | Records | Share | Test-set support |
|---|---|---|---|
| Good | 52,199 | 58.2% | 10,440 |
| Moderate | 34,961 | 39.0% | 6,992 |
| Unhealthy | 2,188 | 2.4% | 438 |
| Very Unhealthy | 358 | 0.4% | 72 |
| Hazardous | 0 | 0.0% | — |

The majority-to-minority imbalance ratio is approximately **146 : 1** (52,199 vs 358). No observation crossed the Hazardous threshold during the study window, so the learnable label space contains four classes. This severe skew (Figure 3.2) is the empirical motivation for the resampling strategy of Section 3.7 and for adopting **macro-averaged recall** as the optimization objective.

*[Insert Figure 3.2 — Class distribution bar chart]*

### 3.5.5 Feature Engineering

**Table 3.5 — Engineered features**

| Feature | Definition | Rationale |
|---|---|---|
| `pm25_pm10_ratio` | PM2.5 ÷ PM10 (0 if PM10 = 0) | Discriminates combustion vs dust aerosols |
| `pollution_load` | PM2.5 + O₃ | Composite burden indicator |
| `is_high_pm25` | PM2.5 > 35.4 (boolean) | Threshold proximity signal |
| `is_high_pm10` | PM10 > 150 (boolean) | Dust-episode flag |
| `hour`, `day_of_week`, `month` | Calendar decompositions of timestamp | Capture diurnal/seasonal cycles |

Boolean flags are excluded from the numeric feature matrix fed to the SVM; identifiers (`location`, `city`, `country`, `timestamp`) and the label are likewise excluded, leaving 14 numeric features.

## 3.6 Data Preprocessing Pipeline

Executed by `scripts/run_pipeline.py` in strict order:

1. **Cleaning** (`clean_data.py`): lower-case column names; parse timestamps; drop exact duplicates; drop rows where all six pollutants are null; coerce pollutant/weather columns to float.
2. **Missing-value treatment** (`missing_values.py`): **median imputation** (`SimpleImputer(strategy="median")`) for pollutant and weather columns; columns entirely empty are zero-filled; label forward-filled.
3. **Feature engineering** (Table 3.5).
4. **Scaling** (`scaling.py`): `MinMaxScaler` fitted on the numeric feature matrix and persisted (`artifacts/scaler.pkl`) so that API-time predictions apply identical transforms.
5. **Multicollinearity screening** (`multicollinearity.py`): variance inflation factors logged for candidate features to inform feature retention.
6. **Splitting** (`split_dataset.py`): stratified **80/20** train/test split, `random_state=42`; stratification preserves class proportions (test n = 17,942).

## 3.7 Class Balancing Strategy

`src/balancing/smote_tomek.py` implements a **capped hybrid resampling**:

- `SMOTE(k_neighbors = min(5, n_min_class − 1), random_state = 42)` synthesizes minority samples;
- the synthetic target per minority class is capped at `min(1.5 × majority_count, majority_count)` (`MAX_SYNTHETIC_RATIO = 1.5`) to prevent runaway fabrication from only 358 real Very-Unhealthy seeds;
- `SMOTETomek` subsequently removes Tomek links, cleaning the class boundary;
- resampling is applied **exclusively to `X_train/y_train`**; the test partition remains untouched and imbalanced, mirroring deployment reality.

The baseline model is deliberately trained on the **original imbalanced** training data, isolating the causal contribution of balancing + optimization to the measured improvement.

## 3.8 Model Selection and Hyperparameter Optimization

**Baseline model** (`src/models/baseline_svm.py`): `SVC(kernel="rbf", C=1.0, gamma="scale", random_state=42)` trained on imbalanced data.

**Optimized model** (`src/models/optimized_svm.py` + `src/optimization/*`): Bayesian optimization via **Optuna's TPESampler** (seed 42, 10 startup/random trials, MedianPruner), maximizing **macro recall** under **stratified k-fold cross-validation** (default 3 folds, adaptively reduced if a class has fewer members). The pipeline invokes 10 trials per run. The winning configuration is refit on the SMOTE-Tomek-balanced training set.

**Table 3.6 — Search space**

| Parameter | Range / Values | Type |
|---|---|---|
| kernel | {rbf, poly} | categorical |
| C | [0.1, 10.0] | log-uniform |
| gamma | {scale, auto} | categorical |
| degree | [2, 4] (poly only) | integer |

Design notes: TPE was preferred over grid/random search for its sample efficiency on mixed spaces; macro recall was chosen over accuracy/f1_macro because the operative failure mode is missed minority-class episodes; MedianPruner curtails unpromising trials early.

## 3.9 Evaluation Strategy

Both models are scored on the identical untouched test set using accuracy, precision, recall, F1 (overall and per-class), and confusion matrices (`src/evaluation/{metrics,comparison,confusion_matrix}.py`). Artifacts are serialized to `artifacts/comparison.json`, `artifacts/metrics.json`, and `artifacts/confusion_matrix.json`. Interpretation follows via SHAP (Section 7.6). An optional cross-validation endpoint (`POST /api/evaluation/cross-validate`) supports repeated-fold scrutiny through the API.

# CHAPTER 4: SYSTEM DESIGN

## 4.1 Introduction

This chapter translates the methodology into a concrete software blueprint: layered architecture, behavioural diagrams, artifact/data design, and interface design.

## 4.2 System Architecture

The system follows a **three-tier, API-mediated architecture** (Figure 4.1):

1. **Data & Intelligence Tier** — Python packages under `src/`: ingestion clients, preprocessing, balancing, models, optimization, evaluation, explainability, visualization; orchestrated by `scripts/run_pipeline.py`; artifacts persisted under `artifacts/` and `models/`.
2. **Service Tier** — `api.py`, a FastAPI application exposing ~29 REST endpoints grouped as `/health`, `/status`, `/api/data/*`, `/api/preprocessing/*`, `/api/imbalance/*`, `/api/models/*`, `/api/predict*`, `/api/evaluation/*`, `/api/explainability/*`, `/api/pipeline/execute`, plus public `/public/*` endpoints for lightweight city summaries and forecasts. An in-memory cache with file-mtime invalidation keeps hot artifacts (models, scaler, DataFrames, SHAP explainer) resident.
3. **Presentation Tier** — two independent clients: a **Streamlit** multipage app (`app/`: Overview, Predictions, Evaluation, Explainability, System pages) for analytics workflows, and a **Next.js PWA** (`frontend/`: React, Tailwind CSS, Leaflet map, Serwist service worker) for public, installable, offline-tolerant access.

Deployment targets: **Render** (API container, `render.yaml`), **Vercel** (Next.js frontend, `vercel.json`), with a `Dockerfile` for portable API hosting.

*[Insert Figure 4.1 — Three-tier architecture diagram]*

## 4.3 Use Case Design

Use cases refine Section 3.4 into include/extend relations: *Predict AQI* «includes» *Load Scaler & Model*, «extends» *Live City Prediction*; *Run Pipeline* «includes» *Fetch Data, Preprocess, Balance, Train, Evaluate*; *Explain Prediction* «includes» *Compute SHAP Values*. See Figure 3.1.

## 4.4 Class Design

Principal classes/modules and responsibilities:

| Module/Class | Responsibility |
|---|---|
| `openmeteo_client.fetch_historical_data` | Chunked historical AQ+weather retrieval |
| `openaq_client` | Secondary measurement source |
| `data_validator.validate_dataframe` | Schema/quality gate |
| `clean_data`, `fill_missing_values`, `engineer_features` | Transformation chain |
| `fit_scaler / apply_scaler_to_dataframe / save_scaler` | Scaling persistence |
| `split_data` | Stratified partitioning |
| `apply_smote_tomek` | Capped hybrid resampling |
| `train_baseline_svm` / `train_optimized_svm` | Model construction |
| `optimize_svm_hyperparameters` (TPESampler, MedianPruner) | Bayesian search |
| `svm_objective` | CV objective (recall_macro) |
| `compute_metrics`, `compare_models`, `generate_confusion_matrix`, `cross_validate_model` | Evaluation |
| `ShapExplainer` | KernelExplainer wrapper (k-means background) |
| `_Cache` (api.py) | mtime-invalidated artifact cache |

*[Insert UML class diagram]*

## 4.5 Sequence Design

Prediction lifecycle (Figure 4.2): Client → `POST /api/predict` → FastAPI validates payload (Pydantic) → cache loads `optimized_svm.pkl` + `scaler.pkl` (mtime check) → scaler transforms features → `model.predict` (+ probabilities where enabled) → response `{predicted_class, confidences, timestamp}`. Training lifecycle: Client → `POST /api/models/train/optimized` → load processed CSV → SMOTE-Tomek → Optuna study (n trials) → refit → persist model + metrics.

*[Insert Figure 4.2 — Sequence diagram]*

## 4.6 Activity Design

Pipeline activity flow (Figure 4.4): Start → ensure directories → fetch (historical?) → clean → impute → engineer → scale → VIF → split → balance (train only) → train baseline → optimize + train hybrid → evaluate both → compare → confusion matrices → SHAP plots/per-class importance → persist artifacts → End. Decision nodes handle empty fetches (abort) and SHAP failures (warn-and-continue).

## 4.7 Data Flow and Artifact Design

Figure 4.3 traces data stores: external APIs → `data/raw_data.csv` → transformations → `data/processed_data.csv` → split/balance (in-memory) → `models/*.pkl` + `artifacts/scaler.pkl` → evaluation writes `artifacts/{metrics,comparison,confusion_matrix}.json` → SHAP writes `artifacts/shap_plots/shap_beeswarm.png` and `artifacts/shap_per_class.json` → API caches serve both front ends.

## 4.8 User Interface Design

**Design principles:** clarity first (traffic-light AQI colours), minimal input (city selector + action button), progressive disclosure (summary cards → detail tabs), accessibility (high-contrast palettes, readable font sizes), responsiveness.

**Streamlit dashboard** (`app/streamlit_app.py`, sidebar navigation):

- *Overview*: KPI metric cards (current category, dominant pollutant), 7-day trend line chart, city selector, data-source selector (Auto/Open-Meteo/OpenAQ);
- *Predictions*: trigger live prediction for a city; display predicted class and supporting values;
- *Evaluation*: side-by-side baseline vs optimized metric cards, per-class recall comparison, confusion matrices;
- *Explainability*: embedded SHAP summary and per-class top-feature charts;
- *System*: health/status probes, pipeline triggers, resource metrics.

**PWA** (`frontend/src/app/page.tsx` + components): AppShell navigation; MapView (Leaflet) with city markers coloured by AQI; MetricCard grid; AlertPanel/AlertHistoryPanel for episode notifications; FormBuilder-driven inputs; install prompt via Serwist service worker with offline shell.

*[Insert Figure 4.5 — Streamlit wireframe; Figure 4.6 — PWA wireframe; add annotated screenshots in Chapter 5]*

# CHAPTER 5: IMPLEMENTATION

## 5.1 Introduction

This chapter maps the design onto code, highlighting key implementation decisions, representative listings (full listings in Appendix A), and deployment.

## 5.2 Technology Stack

| Layer | Technologies |
|---|---|
| Language | Python 3.13 |
| Data/ML | pandas, NumPy, scikit-learn (SVC, MinMaxScaler, SimpleImputer, StratifiedKFold via cross_val_score), imbalanced-learn (SMOTETomek), shap, joblib |
| Optimization | Optuna (TPESampler, MedianPruner) |
| Visualization | Matplotlib, Plotly, Seaborn |
| API | FastAPI, Uvicorn, Pydantic, psutil (optional) |
| Dashboard | Streamlit (+ Plotly Express) |
| PWA | Next.js (App Router), React, TypeScript, Tailwind CSS, Leaflet/react-leaflet, SWR, Serwist |
| Testing | pytest |
| DevOps | Docker, render.yaml (Render), vercel.json (Vercel), GitHub Actions-ready layout |

## 5.3 Module Implementation Map

```
├── api.py                      # FastAPI service (~29 endpoints, artifact cache)
├── scripts/run_pipeline.py     # Deterministic end-to-end pipeline entry point
├── src/
│   ├── ingestion/              # openaq_client, openmeteo_client, fetch_data, data_validator
│   ├── preprocessing/          # clean_data, missing_values, feature_engineering,
│   │                           # scaling, split_dataset, multicollinearity, label_encoder
│   ├── balancing/              # smote_tomek, imbalance_analysis, class_distribution
│   ├── models/                 # baseline_svm, optimized_svm, svm_pipeline, save_model
│   ├── optimization/           # bayesian_optimizer, objective_function, search_space, acquisition
│   ├── evaluation/             # metrics, comparison, confusion_matrix, cross_validation, mimcr
│   ├── explainability/         # shap_explainer, summary_plot, force_plot, feature_importance
│   ├── visualization/          # charts, plots, dashboard, report_generator
│   └── utils/                  # logger, timers, helpers, exporters
├── app/                        # Streamlit multipage UI
├── frontend/                   # Next.js PWA
├── tests/                      # pytest suite (6 modules)
├── config/                     # paths.py, constants.py, config.yaml
├── artifacts/                  # metrics.json, comparison.json, confusion_matrix.json,
│                               # shap_per_class.json, shap_plots/, scaler.pkl
└── models/                     # baseline_svm.pkl, optimized_svm.pkl
```

*[Insert Figure 5.1 — repository structure diagram]*

## 5.4 Data Ingestion Layer

`openmeteo_client.py` defines city coordinates, pollutant/weather mappings, and three retrieval modes: forecast-window fetch, historical AQ fetch, and archive weather fetch. Historical downloads iterate six-month chunks per city, merge weather into the AQ payload, parallelize across cities with `ThreadPoolExecutor`, and retry transient failures with exponential backoff. Output frames share the OpenAQ-compatible schema (`location, city, country, timestamp, pm25…rainfall`), letting downstream code treat sources uniformly (`fetch_data(source="auto|openmeteo|openaq")`).

## 5.5 Preprocessing and Balancing Implementation

Representative excerpt (label construction, `feature_engineering.py`):

```python
conditions = [
    ~score.apply(np.isfinite),
    score <= 12, score <= 35.4, score <= 55.4, score <= 150.4,
]
choices = ["Moderate", "Good", "Moderate", "Unhealthy", "Very Unhealthy"]
data["aqi_category"] = np.select(conditions, choices, default="Hazardous")
```

Balancing excerpt (`smote_tomek.py`):

```python
k_neighbors = max(1, min(5, min_class_count - 1))
synthetic_cap = int(max_class_count * MAX_SYNTHETIC_RATIO)   # 1.5 × majority
target_count = min(synthetic_cap, max_class_count)
smote = SMOTE(random_state=42, k_neighbors=k_neighbors,
              sampling_strategy=sampling_strategy)
sampler = SMOTETomek(random_state=42, smote=smote)
X_resampled, y_resampled = sampler.fit_resample(X, y)
```

## 5.6 Model Training and Optimization Implementation

```python
sampler = optuna.samplers.TPESampler(seed=42, n_startup_trials=10)
pruner  = optuna.pruners.MedianPruner(n_startup_trials=5)
study   = optuna.create_study(direction="maximize", sampler=sampler, pruner=pruner)
study.optimize(lambda t: svm_objective(t, X, y, cv=cv), n_trials=n_trials)
```

with the objective scoring `cross_val_score(SVC(...), X, y, scoring="recall_macro", n_jobs=-1)`. Guardrails: adaptive fold reduction for tiny classes; optional subsampling to ≤ 30,000 training rows (stratified, seeded) to bound SVM fit time.

## 5.7 API Service Layer

Endpoint groups (selected): `GET /health`, `GET /status`; `GET /api/data/fetch|summary|download`, `POST /api/data/upload`; `POST /api/preprocessing/execute`; `GET /api/imbalance/analyze`, `POST /api/imbalance/balance`; `POST /api/models/train/baseline|optimized`; `POST /api/predict`, `GET /api/predict/live`, `POST /api/predict/batch`; `GET /api/evaluation/metrics|comparison|confusion-matrix`, `POST /api/evaluation/cross-validate`; `GET /api/explainability/shap-summary|shap-per-class`, `POST /api/explainability/explain-prediction`; `POST /api/pipeline/execute`; public `GET /public/city/{name}[ /forecast | /historical ]`. CORS is enabled for the front-end origins; heavy jobs run off the event loop via thread delegation.

## 5.8 Front-End Implementation

**Streamlit** (`app/`): cached API clients (`@st.cache_data(ttl=120)`), custom CSS injection (`style_assets.py`), five pages mirroring Section 4.8. **PWA** (`frontend/`): typed API client (`lib/api.ts`), city context provider, Leaflet map overlay, Serwist-generated service worker (`app/sw.ts`) with manifest icons (192/512 px), enabling installability and offline shell.

## 5.9 Deployment

- **API**: Docker image; `render.yaml` provisions the web service with health-check path `/health`.
- **Frontend**: `vercel.json` builds the Next.js app and proxies API routes to the backend origin.
- **Local**: `start.ps1` / `start.bat` bootstrap virtualenv, install `requirements.txt`, launch Uvicorn + Streamlit.

# CHAPTER 6: SYSTEM TESTING

## 6.1 Introduction

Testing proceeded at three levels: unit (pytest), integration (API endpoint exercises against real artifacts), and acceptance-oriented walkthroughs of both front ends.

## 6.2 Unit Testing

**Table 6.1 — Unit test inventory (`tests/`)**

| Suite | Focus | Representative assertions |
|---|---|---|
| `test_preprocessing.py` | Cleaning, imputation, feature engineering, scaling, splitting | Duplicates removed; medians imputed; AQI labels match breakpoints; scaler bounds ∈ [0,1]; stratification preserved |
| `test_smote.py` | SMOTE-Tomek behaviour | Minority counts raised toward cap; train-only application; shape/column integrity; edge cases (tiny classes) |
| `test_optimizer.py` | Search space + objective | Suggested params within bounds; recall_macro returned; deterministic seeding |
| `test_svm.py` | Baseline/optimized trainers | Models fit and predict; expected attribute defaults; persistence round-trip |
| `test_shap.py` | ShapExplainer | Explainer constructs on small background; per-class importance keys ⊆ labels; monotone output schema |
| `test_openaq_client.py` | Ingestion client | URL/param construction; graceful handling of empty/error responses |

All suites pass against the committed codebase (`pytest -q`). Fixtures downsample data to keep runtime interactive while preserving class diversity.

## 6.3 Integration and API Testing

With artifacts present, the running service was exercised end-to-end: `/health` → `/status` → `/api/evaluation/metrics` returns the stored optimized metrics; `/api/evaluation/comparison` reproduces Table 7.1 deltas; `/api/predict` accepts scaled/un-scaled payloads and returns a valid category; `/public/city/{city}` returns live summaries for all three cities. Failure-path checks confirmed graceful JSON errors when artifacts are absent (HTTP 4xx/5xx with explanatory detail) rather than crashes.

## 6.4 User Acceptance Considerations

Walkthroughs with fellow students confirmed: the Streamlit flow (select city → view status → run prediction → inspect SHAP) completes without assistance; the PWA installs on Android Chrome and renders the map view offline after first load. Feedback (clearer metric tooltips, darker map tiles) was logged for future iterations.

# CHAPTER 7: RESULTS AND DISCUSSION

## 7.1 Introduction

All results below derive from the committed artifacts generated by the deterministic pipeline (seeds fixed), ensuring traceability from table to file.

## 7.2 Dataset Outcomes

Acquisition yielded 89,928 raw hourly records; cleaning/imputation retained 89,706 (99.7%). The stratified split produced 71,764 training and 17,942 test records with class supports as per Table 3.4. Imbalance stood at ≈146:1 prior to resampling, confirming the anticipated dominance of Good/Moderate conditions in the study window.

## 7.3 Overall Model Performance

**Table 7.1 — Overall test-set performance (n = 17,942)**

| Metric | Baseline SVM | Hybrid (SMOTE-Tomek + BO-SVM) | Δ |
|---|---|---|---|
| Accuracy | 0.9777 | **0.9848** | +0.0071 |
| Precision (weighted) | 0.9775 | **0.9852** | +0.0077 |
| Recall (weighted) | 0.9777 | **0.9848** | +0.0071 |
| F1-score (weighted) | 0.9775 | **0.9849** | +0.0074 |

The hybrid model improves every headline metric. While the aggregate delta appears modest (+0.7 pp), Section 7.4 shows it concentrates exactly where it matters — the rare classes — which weighted averages systematically dilute.

*[Insert Figure 7.1 — grouped bar chart of Table 7.1]*

## 7.4 Per-Class Performance and the Effect of Balancing

**Table 7.2 — Baseline per-class metrics**

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| Good | 0.9793 | 0.9915 | 0.9853 | 10,440 |
| Moderate | 0.9790 | 0.9674 | 0.9732 | 6,992 |
| Unhealthy | 0.9240 | 0.8607 | 0.8913 | 438 |
| Very Unhealthy | 0.9091 | 0.6944 | 0.7874 | 72 |

**Table 7.3 — Hybrid model per-class metrics**

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| Good | 0.9952 | 0.9854 | 0.9903 | 10,440 |
| Moderate | 0.9781 | 0.9840 | 0.9810 | 6,992 |
| Unhealthy | 0.8707 | 0.9840 | 0.9239 | 438 |
| Very Unhealthy | 0.9333 | 0.9722 | 0.9524 | 72 |

**Table 7.4 — Recall improvement by class**

| Class | Baseline recall | Hybrid recall | Δ (pp) |
|---|---|---|---|
| Good | 0.9915 | 0.9854 | −0.60 |
| Moderate | 0.9674 | 0.9840 | +1.66 |
| Unhealthy | 0.8607 | 0.9840 | **+12.33** |
| Very Unhealthy | 0.6944 | 0.9722 | **+27.78** |

Interpretation: the baseline misses roughly 1 in 7 Unhealthy episodes and nearly 1 in 3 Very Unhealthy episodes; the hybrid model cuts those miss rates to ~1.6% and ~2.8% respectively. The marginal −0.6 pp on Good recall is the expected, acceptable trade — a handful more Good days labelled Moderate, versus dozens of dangerous episodes caught that were previously missed. Precision on Unhealthy dips (0.924→0.871) because a broader alert boundary now admits some Moderate-borderline cases — a conservative-bias desirable in health screening.

*[Insert Figure 7.2 — per-class recall comparison]*

## 7.5 Confusion Matrix Analysis

Stored confusion matrices (`artifacts/confusion_matrix.json`, rows = truth, cols = prediction):

**Baseline (off-diagonal highlights):** Good→Moderate 89; Moderate→Good 219; Unhealthy→Moderate 56, →Very Unhealthy 5; Very Unhealthy→Unhealthy 22 (i.e., 30.6% of Very Unhealthy episodes escaped to a lesser class).

**Hybrid:** Good→Moderate 152; Moderate→Good 112; Unhealthy→Moderate 7, →Very Unhealthy 0; Very Unhealthy→Unhealthy 2 (miss rate 2.8%). Dangerous-class leakage downward collapses from 27 cases (baseline) to 2.

*[Insert Figures 7.3 and 7.4 — heatmaps rendered from the JSON]*

## 7.6 Model Interpretation with SHAP

`ShapExplainer` wraps the optimized SVC with `shap.KernelExplainer` over a 50-cluster k-means background; a beeswarm summary is persisted (`artifacts/shap_plots/shap_beeswarm.png`) alongside per-class top-3 attributions computed from labelled representatives:

**Table 7.5 — Mean |SHAP| top features per class**

| Class | 1st | 2nd | 3rd |
|---|---|---|---|
| Good | pm25 (0.432) | pm10 (0.330) | o3 (0.178) |
| Moderate | pm25 (0.314) | pm10 (0.279) | pollution_load (0.153) |
| Unhealthy | pm25 (1.013) | pm10 (0.706) | pollution_load (0.233) |
| Very Unhealthy | pm25 (1.770) | pm10 (1.394) | pollution_load (0.182) |

Attribution magnitude grows monotonically with severity class (pm25: 0.31→1.77), and the ranking aligns with epidemiological priors — particulates dominate, with ozone contributing to Good-day separation. The engineered `pollution_load` earns third place in three classes, validating feature engineering. These profiles give health authorities a human-auditable rationale for every alert level.

*[Insert Figure 7.5 — SHAP beeswarm]*

## 7.7 Discussion

1. **Balancing works as theorized.** Confining SMOTE-Tomek to training data yielded minority-recall gains (+12.3/+27.8 pp) without inflating test-set optimism — the test distribution remained natural.
2. **Objective choice mattered.** Optimizing macro recall steered TPE toward configurations tolerating small major-party costs for large minority gains; optimizing accuracy would likely have reproduced baseline-like behaviour.
3. **Aggregate vs operative metrics.** A +0.7 pp weighted-F1 delta understates the public-health value; per-class and confusion analyses reveal the true effect, echoing the imbalance-learning literature's warning against accuracy-centric reporting.
4. **Explainability closes the trust loop.** SHAP rankings matching known pollutant toxicology (PM-dominant) suggest the model learned physically meaningful structure rather than artifacts.
5. **Engineering completeness.** Unlike prototype notebooks, the framework ships with an API contract, dual front ends, container configs, and a regression test suite — prerequisites for institutional adoption.

## 7.8 Threats to Validity and Limitations

- **Label circularity:** AQI labels derive from PM2.5 itself, so part-per-million recall on particulate-heavy classes partly reflects threshold recovery; the model's value lies in robustness to noise/gaps (imputation, ratio features) and multivariate context, not clairvoyance.
- **No Hazardous class:** behaviour beyond Very Unhealthy is untested by construction.
- **Small VU support (72 test rows):** per-class VU metrics carry ±~5 pp sampling uncertainty.
- **Pre-split scaler fitting:** minor optimistic bias; rectifiable by fitting within CV folds (future work).
- **Modelled inputs:** Open-Meteo reanalysis inherits upstream assimilation biases; ground-truth regulatory monitors were unavailable at scale.
- **Geographic scope:** three cities in one climatic belt; transferability unverified.

# CHAPTER 8: CONCLUSION, RECOMMENDATIONS, AND FUTURE WORK

## 8.1 Conclusion

This project set out to build an accurate, imbalance-aware, interpretable air quality classification framework for urban Zambia, and to deliver it as usable software. All seven objectives were met: 89,706 clean labelled records spanning 40 months were curated from open APIs; the ≈146:1 imbalance was characterized and mitigated via capped SMOTE-Tomek on training data; TPE-based Bayesian optimization tuned an RBF-SVM against macro recall; the hybrid model reached 98.48% accuracy / 0.9849 F1, improving Very-Unhealthy recall from 0.694 to 0.972 and Unhealthy recall from 0.861 to 0.984 over a default baseline; SHAP analysis certified PM2.5, PM10, and pollution_load as the decision drivers; and the whole stack is exposed through a documented FastAPI service with Streamlit and PWA clients, containerized for Render/Vercel deployment. The research questions of Section 1.4 are answered affirmatively and quantitatively.

## 8.2 Recommendations

1. Adopt macro-recall (or cost-weighted) objectives as standard practice for health-related imbalanced classification in departmental projects.
2. Report per-class recall and confusion matrices alongside any aggregate figure when minority classes carry asymmetric risk.
3. Institutionalize open-data pipelines (Open-Meteo/OpenAQ) as complements to regulatory monitoring, given their demonstrated adequacy for classification-grade features.
4. Pair any deployed classifier with SHAP-style audits before operational use.

## 8.3 Future Work

1. **Refit the scaler inside CV folds** to eliminate the pre-split leak noted in §7.8.
2. **Cost-sensitive extension:** compare resampling against `class_weight`/threshold-moving under a unified protocol.
3. **Forecasting:** extend from nowcasting to 24–72 h episode prediction with sequence models (LSTM/Temporal CNN) on the same ingestion spine.
4. **Ground-truth calibration:** partner with ZEMA/NASA-feeds to validate against regulatory monitors; revisit Hazardous class once extreme episodes are captured.
5. **Alerting:** activate the PWA AlertPanel against a notification service (push/SMS) for episode warnings.
6. **Expansion:** add Livingstone, Chipata, and Copperbelt mining-township micro-sites; evaluate domain adaptation across climates.

# REFERENCES

Akiba, S., Sano, S., Yanase, T., Ohta, T. & Koyama, M. (2019). Optuna: A next-generation hyperparameter optimization framework. *Proceedings of the 25th ACM SIGKDD International Conference on Knowledge Discovery & Data Mining*, 2623–2631.

Bergstra, J., Bardenet, R., Bengio, Y. & Kégl, B. (2011). Algorithms for hyper-parameter optimization. *Advances in Neural Information Processing Systems 24*, 2546–2554.

Bergstra, J. & Bengio, Y. (2012). Random search for hyper-parameter optimization. *Journal of Machine Learning Research*, 13, 281–305.

Chawla, N. V., Bowyer, K. W., Hall, L. O. & Kegelmeyer, W. P. (2002). SMOTE: Synthetic minority over-sampling technique. *Journal of Artificial Intelligence Research*, 16, 321–357.

Cortes, C. & Vapnik, V. (1995). Support-vector networks. *Machine Learning*, 20(3), 273–297.

He, H. & Garcia, E. A. (2009). Learning from imbalanced data. *IEEE Transactions on Knowledge and Data Engineering*, 21(9), 1263–1284.

Herbrich, R. (2001). *Learning Kernel Classifiers: Theory and Algorithms*. MIT Press.

Hutter, F., Kotthoff, L. & Vanschoren, J. (Eds.). (2019). *Automated Machine Learning: Methods, Systems, Challenges*. Springer.

IQAir. (2026). *AirVisual: Global air quality monitoring platform*. Available at: https://www.iqair.com (Accessed: August 2026).

Lundberg, S. M. & Lee, S.-I. (2017). A unified approach to interpreting model predictions. *Advances in Neural Information Processing Systems 30*, 4765–4774.

Lundberg, S. M., Erion, G., Chen, H., DeGrave, A., Prutkin, J., Nair, B., Katz, R., Himmelfarb, J., Bansal, N. & Lee, S.-I. (2020). From local explanations to global understanding with explainable AI for trees. *Nature Machine Intelligence*, 2(1), 56–67.

OpenAQ. (2026). *Open Air Quality Data: The Global Repository*. Available at: https://openaq.org (Accessed: August 2026).

Open-Meteo. (2026). *Open-Meteo Air Quality API documentation*. Available at: https://open-meteo.com/en/docs/air-quality-api (Accessed: August 2026).

Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., … Duchesnay, É. (2011). Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research*, 12, 2825–2830.

Platt, J. (1999). Probabilistic outputs for support vector machines and comparisons to regularized likelihood methods. In *Advances in Large Margin Classifiers*, MIT Press, 61–74.

Ribeiro, M. T., Singh, S. & Guestrin, C. (2016). "Why should I trust you?": Explaining the predictions of any classifier. *Proceedings of the 22nd ACM SIGKDD*, 1135–1144.

Smola, A. J. & Schölkopf, B. (2004). A tutorial on support vector regression. *Statistics and Computing*, 14(3), 199–222.

Tomek, I. (1976). Two modifications of CNN. *IEEE Transactions on Systems, Man, and Cybernetics*, SMC-6(11), 769–772.

United States Environmental Protection Agency. (2024). *Technical Assistance Document for the Reporting of Daily Air Quality – the Air Quality Index (AQI)*. EPA-454/B-24-001.

World Health Organization. (2021). *WHO Global Air Quality Guidelines: Particulate Matter (PM2.5 and PM10), Ozone, Nitrogen Dioxide, Sulfur Dioxide and Carbon Monoxide*. Geneva: WHO.

Zambia Environmental Management Agency (ZEMA). (2025). *State of Environment Reports and Air Quality Bulletins*. Lusaka: ZEMA. Available at: https://www.zema.org.zm (Accessed: August 2026).

# APPENDICES

## Appendix A: Selected Source Code Listings

> Full source is maintained in the project repository (`air-quality-hybrid-framework`). Key listings:

**A.1 — `scripts/run_pipeline.py` (orchestration, abridged)**

```python
data = fetch_data(source=source, city=city)            # 1. ingest
data = clean_data(data); data = fill_missing_values(data)
data = engineer_features(data)                          # 2. transform
_, scaler = fit_scaler(data[feature_columns]); save_scaler(scaler, SCALER_PATH)
data = apply_scaler_to_dataframe(data, scaler, feature_columns)
vif_df = compute_vif(data, feature_cols)                # 3. screen
X_train, X_test, y_train, y_test = split_data(X, y)     # 4. stratified 80/20
X_train_bal, y_train_bal = apply_smote_tomek(X_train, y_train)   # 5. balance (train only)
baseline_model = train_baseline_svm(X_train, y_train)   # 6a. baseline on imbalanced
optimized_model, best_params, study = train_optimized_svm(X_train_bal, y_train_bal)  # 6b. hybrid
baseline_metrics = compute_metrics(y_test, baseline_model.predict(X_test))
optimized_metrics = compute_metrics(y_test, optimized_model.predict(X_test), save_path=METRICS_PATH)
comparison = compare_models(baseline_metrics, optimized_metrics)   # 7. compare + persist
explainer = ShapExplainer(optimized_model, X_train_bal) # 8. explain
explainer.save_summary_plot(shap_sample, SHAP_PLOTS_DIR)
per_class_importance = explainer.get_per_class_importance(X_test, y_test)
```

**A.2 — `src/optimization/search_space.py` (complete)**

```python
def get_svm_search_space(trial: Trial) -> dict:
    kernel = trial.suggest_categorical("kernel", ["rbf", "poly"])
    params = {
        "kernel": kernel,
        "C": trial.suggest_float("C", 0.1, 10.0, log=True),
        "gamma": trial.suggest_categorical("gamma", ["scale", "auto"]),
    }
    params["degree"] = trial.suggest_int("degree", 2, 4) if kernel == "poly" else 3
    return params
```

**A.3 — `src/balancing/smote_tomek.py` (core logic)** — see listing in §5.5.

**A.4 — `src/explainability/shap_explainer.py` (constructor, abridged)**

```python
background_kmeans = pd.DataFrame(shap.kmeans(background_data, 50).data,
                                 columns=self.feature_names)
self.explainer = shap.KernelExplainer(self._model_predict,
                                      background_kmeans, link="identity")
```

**A.5 — API route catalogue** — see enumeration in §5.7.

## Appendix B: Dataset Description

**Table B.1 — Raw schema (`data/raw_data.csv`, 89,928 rows)**

| Column | Type | Description |
|---|---|---|
| location | text | Synthetic location tag ("{City} Open-Meteo") |
| city | text | Lusaka / Kitwe / Ndola |
| country | text | "ZM" |
| timestamp | datetime (UTC-localized, Africa/Lusaka) | Hour of observation |
| pm25, pm10, no2, so2, co, o3 | float | Pollutant concentrations (µg/m³) |
| temperature | float | °C at 2 m |
| humidity | float | Relative humidity (%) |
| wind_speed | float | km/h at 10 m |
| rainfall | float | Precipitation (mm) |

Derived columns appended in `processed_data.csv`: `aqi_category`, `pm25_pm10_ratio`, `pollution_load`, `is_high_pm25`, `is_high_pm10`, `hour`, `day_of_week`, `month` (89,706 rows). Retrieval window 2022-08-01 → 2025-12-31; chunked 6-month downloads; median-imputed gaps.

## Appendix C: Detailed Experiment Results

**C.1 — Machine-readable artifacts**

- `artifacts/metrics.json` — optimized-model overall + per-class metrics (values reproduced in Tables 7.1/7.3).
- `artifacts/comparison.json` — baseline vs optimized deltas (accuracy_difference 0.00708; precision_difference 0.00768; recall_difference 0.00707; f1_difference 0.00740; per_class_recall_difference: Good −0.0060, Moderate +0.0166, Unhealthy +0.1233, Very Unhealthy +0.2778).
- `artifacts/confusion_matrix.json` — both models' matrices (§7.5).

**C.2 — Optimization record**

Sampler TPESampler(seed=42, n_startup_trials=10); pruner MedianPruner(n_startup_trials=5); direction maximize; objective mean recall_macro over adaptive stratified CV (default 3 folds); trials per run 10; search space per Table 3.6. Best parameters are re-emitted at each pipeline run and logged with the saved model (`models/optimized_svm.pkl`).

**C.3 — Runtime environment**

Windows 11 workstation; Python 3.13; dependency pins per `requirements.txt` (fastapi, uvicorn, numpy, pandas, scikit-learn, imbalanced-learn, shap, optuna, matplotlib, plotly, seaborn, joblib, requests, pyyaml, psutil, python-multipart).

## Appendix D: SHAP Explanation Results

- Global: `artifacts/shap_plots/shap_beeswarm.png` (KernelExplainer, 50-cluster k-means background, 50-sample evaluation batch, identity link).
- Per-class mean |SHAP| top-3: reproduced in Table 7.5 from `artifacts/shap_per_class.json`.
- Observation: attribution magnitudes scale with class severity (pm25: Good 0.43 → Very Unhealthy 1.77), and `pollution_load` ranks third in Moderate/Unhealthy/Very Unhealthy — evidence that engineered composites carry explanatory weight, not just raw concentrations.

## Appendix E: User Manual (Quick Start)

**Run the pipeline**

```powershell
git clone <repo-url>; cd air-quality-hybrid-framework
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/run_pipeline.py --historical        # full rebuild (fetch → train → artifacts)
```

**Serve the API**

```powershell
uvicorn api:app --reload --port 8000               # http://localhost:8000/docs
```

**Launch the Streamlit dashboard**

```powershell
streamlit run app/streamlit_app.py                 # http://localhost:8501
```

**Run the PWA frontend**

```powershell
cd frontend; npm install; npm run dev              # http://localhost:3000
```

**Typical tasks**

- *Check air quality:* open Overview page (or PWA home) → choose city → read category card and trend.
- *Predict:* Predictions page → select city → Run Prediction → view class + drivers.
- *Retrain:* System page → Execute Pipeline (or CLI above) → refresh Evaluation page.
- *Explain:* Explainability page → view beeswarm and per-class feature bars.
- *Tests:* `pytest -q` from the repository root.

---

*— End of Dissertation —*
