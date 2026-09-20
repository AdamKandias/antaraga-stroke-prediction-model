# Artikel JAEE — Draf Lengkap (English) + Panduan Penyisip

====================================================================================================
# NASKAH ARTIKEL (English) — mulai dari sini disalin ke template Word JAEE
====================================================================================================

# A Pre-Hospital Early Warning System for Ischemic Stroke Risk Based on Multi-Wavelength PPG and an XGBoost Algorithm

Adam Kandias¹, Kadek Savita Dyutianaya², Kalyana Daeva Ali³, Ni Komang Diah Pratiwi⁴, Jonzeven La Royba⁵, and Agrippina Waya Rahmaning Gusti³*
*(afiliasi dan email: sama seperti template yang sudah dibuat)*

**Abstract**—Ischemic stroke outcomes depend on how quickly families recognize warning signs, yet risk-stratification tools are applied only after hospital arrival. This study presents a pre-hospital early-warning system that couples a three-channel photoplethysmography (PPG) wristband (green 525 nm, red 660 nm, infrared 880 nm) with cloud-side signal processing, five physiological estimators, and a class-weighted XGBoost stroke-risk classifier. In 11 volunteers, streamed heart rate agreed with a finger oximeter (mean absolute error 1.2 bpm), and the leave-one-subject-out accuracy of the five estimators ranged from 76.2% to 91.4% against reference devices. On a public dataset (n = 5,110; 4.9% positive), the classifier reached an AUC of 0.823 and a recall of 0.973 at a screening threshold. Propagating the estimation errors into the classifier changed at most 3.8% of the risk tiers, showing that the alert output is stable against them.

**Keywords**—class imbalance, ischemic stroke, multi-wavelength photoplethysmography, pre-hospital monitoring, XGBoost

## I. INTRODUCTION

*(Paragraf 1–3 tetap sesuai naskah Anda, kecuali kalimat penutup paragraf 3 diganti berikut.)*

**Ganti kalimat terakhir paragraf ke-3** ("The primary benefit expected from this study is ... which is integrated") **dengan:**

> The primary benefit expected from this study is a wearable screening device with high sensitivity that is integrated with a mobile application, so that a family caregiver is alerted before the patient reaches a healthcare facility. The contributions of this work are threefold: (i) a distributed architecture that connects three-wavelength PPG acquisition, server-side signal processing, and stroke-risk classification; (ii) a leave-one-subject-out evaluation of the estimation of five physiological parameters in an initial cohort of 11 volunteers, with an independent laboratory comparison in one volunteer; and (iii) a class-weighted XGBoost classifier with two decision thresholds, together with a sensitivity analysis that propagates the observed estimation errors into the final risk tier.

## II. METHOD

*(Paragraf pembuka dan II.A tetap sesuai naskah Anda. Sisipkan Fig. 1 di akhir II.A.)*

> **[SISIPKAN Fig. 1 di sini — lebar halaman]** `figures-jaee/fig1_arsitektur.png` dari `jaee_0_arsitektur_sistem.ipynb`
> **Caption (di bawah gambar):** Fig. 1. Architecture of the proposed system: (a) three-wavelength wearable prototype, (b) cloud server for signal processing, physiological estimation, and stroke-risk classification, and (c) mobile application delivering vital-sign cards and risk alerts to the family caregiver.
>
> **Paragraf pembahasan (wajib setelah gambar):** Fig. 1 summarizes the data flow. The wristband streams one-second batches of raw samples over Wi-Fi to the server, which returns vital-sign estimates and a three-level risk tier to the mobile application. Keeping the computation on the server keeps the microcontroller light and allows the models to be retrained as calibration data accumulate, without reflashing the firmware.

### B. Signal Preprocessing and Physiological Estimation

*(Ganti seluruh sub-bagian B di naskah Anda dengan versi berikut — mengoreksi dua pernyataan pada 0.2 butir 2 dan 3. Ada 10 persamaan bernomor di II.B–II.D; tiap persamaan ditulis sebagai blok "**(n)** `format linear Word` → tampilan yang diharapkan". Salin isi di antara tanda `…` ke kotak persamaan Word, lalu tekan Tab dan ketik nomornya; lihat 0.1c.)*

To minimize the computational load on the microcontroller, the system employs a distributed processing architecture between the prototype and the server. The ESP32-S3 computes a Signal Quality Index (SQI) for every one-second batch and transmits it as metadata together with the raw samples; the decision to accept or discard a batch is made on the server, where all sub-metrics are available and the thresholds can be changed without reflashing the device.

On the server, each channel is filtered with a fourth-order Butterworth band-pass filter (0.5–5 Hz) applied forward and backward to obtain zero phase distortion [15]. The lower edge removes the direct-current baseline and respiratory modulation (about 0.15–0.3 Hz), and the upper edge retains the first four harmonics of a 75 bpm pulse. The pulsatile component of each channel is characterized by its mean level D (DC) and the peak-to-peak amplitude A (AC) of the last second.

Heart rate is obtained from the autocorrelation of the band-passed infrared signal y[n], computed through the fast Fourier transform,

> **(1)** `R[k]=ℱ^(−1) (|ℱ(y)|^2)∕N,`  → R[k] = ℱ⁻¹(|ℱ(y)|²)/N,

where ℱ denotes the discrete Fourier transform and N the number of samples. The dominant lag k̂ is the highest local maximum of R[k] inside the physiological range of 40–180 bpm, refined by parabolic interpolation, and the heart rate is

> **(2)** `HR=60 f_s∕k̂,`  → HR = 60 f_s / k̂,

where f_s is the sampling rate (400 Hz for the MAX30102 channels). The periodicity confidence c = R[k̂]/R[0] lies in [0, 1], and readings with c < 0.30 are rejected. Because a window that contains alternating pulse amplitudes can lock onto twice the beat period (an octave error that halves the rate), the raw estimate is passed through a temporal stabilizer. A reading that deviates by more than 20% from the last accepted value is corrected by a factor of two when it matches half or double the previous value, otherwise it is held; the output is the median of the last five accepted values,

> **(3)** `HR_t="median"{HR′_(t−4),…,HR′_t},`  → HR_t = median{HR′_(t−4), …, HR′_t},

where HR′ denotes the accepted (octave-corrected) readings. The estimator is evaluated on a window that grows every second up to 10 s (minimum 4 s), which reproduces the streaming behavior of the deployed system.

The cleaned optical signals are then used to estimate five physiological parameters (systolic blood pressure, diastolic blood pressure, blood glucose, cholesterol, and uric acid). For each parameter, the input is a seven-element vector: the DC level and AC amplitude of the infrared and red channels, the heart rate, age, and sex, standardized with the mean and standard deviation of the training subjects only. A separate regression model is selected automatically for each parameter from 12 candidates (three model configurations × 4 feature subsets: all seven features, heart rate with age and sex, the two DC levels with age, and age only). The model configurations are support vector regression (SVR) with a linear kernel and with an RBF kernel [16], and XGBoost [17]; a multilayer perceptron was compared in preliminary experiments and gave lower accuracy than SVR and XGBoost, so it was not retained. Hyperparameters are fixed in advance rather than tuned after seeing the scores. The winning candidate m* is the one with the highest leave-one-subject-out validation score S on the training subjects,

> **(4)** `m^*=arg max_m S_"LOSO" (m).`  → m* = arg max_m S_LOSO(m).

To ensure that the trained regression models do not experience data leakage between users, model performance is evaluated with leave-one-subject-out (LOSO) cross-validation [21]: each volunteer is held out in turn, the model is selected and fitted on the other N − 1 volunteers, and it then estimates the held-out volunteer. Because every volunteer contributes one recording, LOSO coincides with leave-one-out. The accuracies reported in Section III are those of the selected model for each parameter. The results of these physiological estimates are then integrated with user profiles to generate nine risk factors that serve as inputs for the final stroke risk classification model.

### C. Risk Level Classification Modeling Using XGBoost Algorithm

**Input.** The classifier takes nine risk factors: age, sex, body-mass index (BMI), hypertension, heart disease, average glucose level, smoking status, residence type, and working status. In deployment, the average glucose level comes from the glucose estimator, and the hypertension flag is derived from the estimated blood pressure,

> **(5)** `"HTN"=I("SBP"≥140 ∨ "DBP"≥90),`  → HTN = I(SBP ≥ 140 ∨ DBP ≥ 90),

where I(·) is 1 when the condition holds and 0 otherwise.

**Training data.** The model is trained on a public stroke dataset [18] with 5,110 records (249 positive, 4.87%), from which a stratified 70/30 split gives 3,577 training and 1,533 test records (75 test positives). BMI is missing in 201 records and is handled natively by XGBoost. The dataset contains no blood pressure, so hypertension is a diagnosis flag at training time.

**Model.** XGBoost builds an additive ensemble of regression trees and minimizes a regularized logistic loss [17]. To address the extreme class imbalance, the positive class is up-weighted in that loss,

> **(6)** `ℓ_ρ (y,p)=−ρ y log p−(1−y) log(1−p),`  → ℓ_ρ(y, p) = −ρ y log p − (1 − y) log(1 − p),

where y ∈ {0, 1} is the label, p the predicted probability, and ρ = N₋/N₊ the ratio of negative to positive training records, which gives ρ = 19.56 on the training split. Hyperparameters were searched by randomized search (40 candidates, stratified five-fold cross-validation, average precision as the score); the selected configuration is 100 trees, maximum depth 4, learning rate 0.03, minimum child weight 5, subsample 1.0, and L2 regularization λ = 1.0. HistGradientBoosting was evaluated as a challenger under the same protocol, and XGBoost was retained on cross-validated average precision.

**Two decision thresholds.** The proposed device is a screening tool, so missing a person at risk is costlier than a false alert. Two thresholds with different roles are derived from out-of-fold (OOF) predictions on the training set only (never from the test set) [19]. With precision P = TP/(TP + FP), recall R = TP/(TP + FN), and F₁ = 2PR/(P + R), the detection threshold is the highest threshold that still reaches a target recall,

> **(7)** `τ_"det"="max" {τ:R_"OOF" (τ)≥0.98},`  → τ_det = max{τ : R_OOF(τ) ≥ 0.98},

and the high-risk threshold is the F₁-optimal point,

> **(8)** `τ_"high"=arg max_τ F_(1,"OOF") (τ).`  → τ_high = arg max_τ F_1,OOF(τ).

The risk tier shown to the user is low when the predicted probability p is below τ_det, medium when p lies from τ_det up to τ_high, and high when p is at least τ_high. A target recall of 0.98 rather than 1.0 is used because perfect recall is reached only when nearly the whole population is flagged, at which point the output carries no discriminative information. The two thresholds are kept separate; deriving the medium tier as a fraction of τ_det would collapse the low tier once τ_det is lowered for recall. Because average precision is more informative than ROC analysis for imbalanced data [20], it is used for model selection, and the area under the ROC curve is reported alongside it.

### D. Participants, Reference Measurements, and Evaluation Metrics

*(Sub-bagian baru; sisipkan setelah C.)*

**Participants and protocol.** Eleven volunteers (5 men, 6 women; age 20–80 years; two with a personal history of stroke) were recorded once each between 3 August and 7 September 2026. The protocol was approved by the Health Research Ethics Committee, Faculty of Public Health, Universitas Airlangga (No. 235/EA/KEPK/2026, 23 July 2026), and all volunteers gave written informed consent. After 5–10 minutes of seated rest, the wristband was worn on the wrist with the arm supported at heart level, and the server stored the last 10 s of the PPG buffer. Reference values were taken within about two minutes of the recording: blood pressure with a digital sphygmomanometer on the contralateral arm, capillary glucose, total cholesterol, and uric acid with an Elvasense 3-in-1 EMS10 meter, and heart rate with a finger pulse oximeter [*sphygmomanometer and oximeter brand/model to be completed*]. All samples were non-fasting (random). For one volunteer (S010), venous blood was additionally analyzed at a commercial clinical laboratory (Klinik Parahita, Surabaya) on the same day, providing an independent laboratory comparison.

**Metrics.** For each parameter, with reference y_i and estimate ŷ_i over N volunteers, we report the mean absolute error, MAE = (1/N) Σ|y_i − ŷ_i|, and the mean absolute percentage error,

> **(9)** `"MAPE"=100/N ∑_(i=1)^N e_i,`  → MAPE = (100/N) Σ_{i=1..N} e_i,

where e_i = |y_i − ŷ_i| / |y_i| is the relative error of volunteer i. The percentage accuracy commonly quoted in non-invasive sensing studies is Acc = 100 − MAPE. Heart-rate agreement is summarized by the bias and the 95% limits of agreement (bias ± 1.96 SD) of the Bland–Altman analysis. Classifier discrimination is reported as AUC and average precision with 95% bootstrap confidence intervals (1,000 resamples of the test set).

## III. RESULT AND DISCUSSION

### A. Signal Acquisition and Heart-Rate Estimation

> **[SISIPKAN Fig. 2 di sini — lebar halaman]** `figures-jaee/fig2_sinyal_3kanal.png` dari `jaee_1_sinyal_dan_bpm.ipynb`
> **Caption:** Fig. 2. Three-channel PPG example (subject S011, 6-s window). (a) Raw signals. (b) Signals after the 0.5–5 Hz zero-phase Butterworth band-pass filter; the red and infrared channels are inverted for display because systole appears as a trough in reflective mode. Triangles mark detected pulse peaks.

Fig. 2 shows that all three channels carry a clear pulsatile component. The raw traces sit on very different direct-current levels (about 1.2×10³ counts for green, 9.8×10⁴ for red, and 1.6×10⁵ for infrared) with slow baseline drift. The peak-to-peak swing over the 10-s recording, which includes that drift, is 23% of the mean for green but only 0.17% for red and 0.26% for infrared, so the green channel has a far larger relative pulsatile amplitude. The band-pass filter removes the drift and high-frequency noise; a secondary (diastolic) shoulder is visible in several green beats. This agrees with the report that green light gives a higher AC/DC ratio and better motion resilience than red or infrared light [22], which supports using green as the primary pulse-waveform channel and infrared as the deeper reference. Note that the deployed heart-rate estimator in (2) uses the infrared channel (with red as fallback) because it is sampled at 400 Hz, whereas the green channel is sampled at 200 Hz.

> **[SISIPKAN Fig. 3 di sini — lebar halaman]** `figures-jaee/fig3_validasi_bpm.png` dari `jaee_1_sinyal_dan_bpm.ipynb`
> **Caption:** Fig. 3. Heart-rate agreement with a finger pulse oximeter (n = 8 recordings with an output). (a) Scatter plot; filled circles are the system output, open squares are the raw 10-s autocorrelation estimates that suffered octave errors. (b) Bland–Altman plot of the system output.

The heart-rate estimator of (2) and (3) was evaluated on the recordings as a growing window, as in the deployed system. The raw ten-second autocorrelation alone occasionally locked onto twice the beat period: three of the eight recordings with a valid confidence (S003, S006, and S010) returned almost exactly half of the oximeter rate (42.9 vs 84, 41.3 vs 82, and 42.7 vs 83 bpm), which is the octave error that the temporal stabilizer of (3) is designed to remove. With the stabilizer, the estimates agreed with the oximeter with a bias of +0.7 bpm, limits of agreement of −1.95 to +3.40 bpm, a mean absolute error of 1.2 bpm (1.5%), and a correlation of 0.996 (Fig. 3). The stabilizer works because the octave error appears only in some windows, so the accepted history steers the correction of the halved readings. Eight of the eleven recordings produced a heart-rate output. The other three were too short or too weakly periodic for the acceptance criteria (S007: 7 s long, confidence 0.18; S008: 2 s long, below the 4 s minimum; S009: confidence just below the 0.30 gate), which shows that the recording should last at least about ten seconds.

### B. Cohort and Physiological Estimation

**TABLE I** — CHARACTERISTICS OF THE STUDY COHORT (N = 11)

| Characteristic | Value, mean ± SD (range) |
|---|---|
| Age (years) | 65.0 ± 16.7 (20.0–80.0) |
| Sex, male / female | 5 / 6 |
| Sampling condition | Random (non-fasting) |
| Heart rate, oximeter (bpm) | 80.3 ± 13.0 (54.0–102.0) |
| SBP, reference device (mmHg) | 147 ± 16 (121–173) |
| DBP, reference device (mmHg) | 83 ± 12 (56–102) |
| Glucose, reference device (mg/dL) | 141 ± 35 (94–183) |
| Cholesterol, reference device (mg/dL) | 232 ± 37 (151–269) |
| Uric acid, reference device (mg/dL) | 5.3 ± 1.0 (3.7–7.2) |

*(Angka dari `jaee_2_estimasi_vital_loso.ipynb`, sel "TABLE I".)*

The cohort consists of 11 volunteers, mostly elderly (mean age 65 years, range 20–80), which matches the intended user group of the system; two volunteers had a personal history of stroke. Each reference value spans a clinically relevant range, from normal to elevated levels: SBP 121–173 mmHg, DBP 56–102 mmHg, random glucose 94–183 mg/dL, total cholesterol 151–269 mg/dL, and uric acid 3.7–7.2 mg/dL. Nine of the eleven volunteers met the hypertension criterion in (5) by their reference readings, so both hypertensive and non-hypertensive profiles are represented.

**TABLE II** — LOSO ESTIMATION PERFORMANCE OF THE FIVE PHYSIOLOGICAL ESTIMATORS (N = 11)

| Parameter | Selected model | Feature subset | MAE | RMSE | Accuracy (%) |
|---|---|---|---|---|---|
| SBP (mmHg) | SVR (linear) | All seven features | 13.18 | 16.06 | 91.0 |
| DBP (mmHg) | SVR (linear) | All seven features | 6.09 | 9.61 | 91.4 |
| Glucose (mg/dL) | XGBoost | Age only | 29.36 | 35.57 | 76.2 |
| Cholesterol (mg/dL) | SVR (linear) | Age only | 30.44 | 37.39 | 85.1 |
| Uric acid (mg/dL) | SVR (RBF) | Age only | 0.75 | 0.96 | 86.2 |

*MAE and RMSE are in the unit of each parameter; Accuracy = 100 − MAPE, from (9). Each volunteer is estimated by a model that was not fitted on that volunteer.*

> **[SISIPKAN Fig. 4 di sini — lebar halaman]** `figures-jaee/fig4_estimasi_vital.png` dari `jaee_2_estimasi_vital_loso.ipynb`
> **Caption:** Fig. 4. Leave-one-subject-out estimates against reference-device values for (a) SBP, (b) DBP, (c) glucose, (d) cholesterol, and (e) uric acid; the dashed line is identity and labels are volunteer codes. (f) LOSO accuracy per parameter.

Table II and Fig. 4 summarize the estimates. With only ten training volunteers per fold, accuracy reached 91.0% for SBP and 91.4% for DBP, and it was above 85% for cholesterol (85.1%) and uric acid (86.2%); glucose, which has the widest relative range in the cohort (coefficient of variation 25%), reached 76.2%. The median absolute percentage error was 3.0% for DBP, 9.0–11.7% for SBP, uric acid, and cholesterol, and 14.6% for glucose, and ten of the eleven SBP estimates were within 20% of the reference. In physical units, the mean absolute errors were 13.2 mmHg (SBP), 6.1 mmHg (DBP), 29.4 mg/dL (glucose), 30.4 mg/dL (cholesterol), and 0.75 mg/dL (uric acid). The DBP estimates follow the identity line closely across the 56–102 mmHg range (Fig. 4b), and nine of eleven volunteers were estimated within 15% of the reference for SBP and, separately, for DBP. These results show that the complete pipeline, from the wristband signal to the vital-sign card in the mobile application, delivers an estimate of all five parameters for volunteers who were not used to train the model.

The automatic selection chose SVR for four parameters and XGBoost for glucose, with a different feature subset for each, which is expected when the relationship between the optical signal and each analyte differs. Because the candidates were compared on the same 11 volunteers and the reference ranges are still narrow, the accuracies in Table II are preliminary. They are meant to show that the approach is feasible, and the planned enlargement of the cohort to at least 30 volunteers, with a separate test set, will provide the independent evidence needed to confirm them.

### C. Comparison With a Clinical Laboratory Reference

**TABLE III** — CASE S010: ESTIMATES AGAINST A CLINICAL LABORATORY (SAMPLE TAKEN 7 SEPTEMBER 2026, NON-FASTING)

| Parameter | Laboratory | Reference device | Proposed device (LOSO) | \|Proposed − lab\| | Acc. vs lab (%) | \|Reference − lab\| | Reference acc. (%) |
|---|---|---|---|---|---|---|---|
| SBP (mmHg) | 150 | 155 | 141.0 | 9.0 | 94.0 | 5.0 | 96.7 |
| DBP (mmHg) | 80 | 85 | 85.4 | 5.4 | 93.2 | 5.0 | 93.8 |
| Glucose (mg/dL) | 178 | 175 | 149.4 | 28.6 | 84.0 | 3.0 | 98.3 |
| Cholesterol (mg/dL) | 154 | 151 | 240.5 | 86.5 | 43.9 | 3.0 | 98.1 |
| Uric acid (mg/dL) | 4.6 | 4.8 | 4.7 | 0.1 | 97.8 | 0.2 | 95.7 |

*S010 was excluded from training for its own estimate (LOSO). Blood pressure was measured at the clinic and is not a laboratory assay.*

The point-of-care reference devices agree closely with the laboratory (95.7–98.3% for glucose, cholesterol, and uric acid), which supports using them as reference values for the cohort. For the same volunteer, the proposed device estimated SBP, DBP, and uric acid within 9.0 mmHg, 5.4 mmHg, and 0.1 mg/dL of the laboratory values (accuracy 93.2–97.8%), and glucose within 28.6 mg/dL (84.0%). Cholesterol was the least accurate estimate for this volunteer (43.9%): the laboratory value (154 mg/dL) is the lowest in the cohort and lies outside the range covered by the other ten volunteers (200–269 mg/dL by reference device), so an estimate obtained without this volunteer in training moves toward the rest of the cohort. A single volunteer cannot support conclusions on accuracy, but this case shows that the reference devices used for training are consistent with an independent laboratory, and it identifies the coverage of low cholesterol values as a target for the next recruitment.

### D. Stroke-Risk Classification

**TABLE IV** — DISCRIMINATION AND PERFORMANCE AT THE DEFAULT THRESHOLD OF 0.5 (TEST SET, n = 1,533; 75 STROKE CASES)

| Model | AUC | AP | Recall at 0.5 | Precision at 0.5 |
|---|---|---|---|---|
| Unweighted XGBoost | 0.838 | 0.271 | 0.013 | 1.000 |
| **Class-weighted XGBoost (proposed)** | 0.823 | 0.250 | 0.760 | 0.123 |
| Balanced logistic regression | 0.838 | 0.218 | 0.773 | 0.128 |

*Bootstrap 95% CI of the proposed model: AUC 0.823 (0.780–0.865), AP 0.256 (0.177–0.349). Prevalence in the test set is 0.049.*

**TABLE V** — PERFORMANCE AT THE RECALL-TARGETED THRESHOLD (τ FROM OUT-OF-FOLD RECALL ≥ 0.98)

| Model | Threshold | Recall | Precision | FN | Alert rate |
|---|---|---|---|---|---|
| Unweighted XGBoost | 0.010 | 0.933 | 0.082 | 5 | 55.8% |
| **Class-weighted XGBoost (proposed)** | 0.042 | 0.973 | 0.075 | 2 | 63.8% |
| Balanced logistic regression | 0.164 | 0.933 | 0.082 | 5 | 55.8% |

*FN = missed stroke cases out of 75; alert rate = share of the 1,533 test records flagged (false alerts: 786, 905, and 785, respectively). Bootstrap 95% CI of the proposed model: recall 0.973 (0.930–1.000), precision 0.075 (0.058–0.091).*

> **[SISIPKAN Fig. 5 di sini — lebar halaman]** `figures-jaee/fig5_klasifikasi_stroke.png` dari `jaee_3_klasifikasi_stroke.ipynb`
> **Caption:** Fig. 5. Stroke-risk classifier. (a) Feature importance (gain) of the deployed XGBoost model. (b) Precision–recall curves on the test set with the two operating points τ_det and τ_high. (c) Recall, precision, and F1 against the decision threshold.

Age dominates the model with a gain of 0.502, followed by BMI (0.086), hypertension (0.079), sex (0.078), average glucose (0.076), and heart disease (0.076); working status receives exactly zero (Fig. 5a). The dominance of age is consistent with the clinical epidemiology of stroke, where incidence roughly doubles every decade after 55 years [25], and hypertension is the strongest modifiable risk factor, with an odds ratio near 3 and about half of the population-attributable risk in a 32-country case–control study [24]. On the test set the classifier reaches an AUC of 0.823 and an average precision of 0.250 against a prevalence of 0.049, that is, about five times better than chance (Table IV and Fig. 5b). At the detection threshold τ_det = 0.042 it finds 73 of 75 stroke cases (recall 0.973, Table V), which fulfils the screening goal of minimizing missed cases; this comes with 905 false alerts (precision 0.075), a trade-off that is intentional for a tool whose alerts lead to a low-cost follow-up (the ABCD2 self-assessment) rather than to treatment. At τ_high = 0.705 the precision rises to 0.206 with recall 0.493, and at the default threshold of 0.5 the recall is 0.760 (Fig. 5c). The three tiers are ordered as intended: the observed stroke rate is 0.4% in the low tier (555 people, 2 events), 4.5% in the medium tier (798 people, 36 events), and 20.6% in the high tier (180 people, 37 events).

Class weighting mainly makes the default operating point usable. Without weighting, the model predicts almost no positives at the threshold of 0.5 (recall 0.013), whereas the class-weighted model detects 57 of the 75 cases (recall 0.760; Table IV). The ranking metrics are comparable across the three models: the AUC of the weighted model (0.823) is within 0.015 of that of the unweighted and balanced logistic-regression models (0.838 for both), and the paired bootstrap 95% confidence intervals of these differences include zero (−0.032 to +0.001 and −0.040 to +0.010). For average precision, the weighted model is 0.032 higher than balanced logistic regression (95% CI −0.048 to +0.107). With a threshold tuned for the target recall (Table V), the weighted model detects 73 of the 75 cases against 70 for the other two models. Class weighting therefore delivers high sensitivity without resampling of medical records, in line with the benefit reported for other imbalanced medical data [10]–[14].

### E. End-to-End Sensitivity to Estimation Error

**TABLE VI** — EFFECT OF PPG ESTIMATION ERROR ON THE RISK OUTPUT (100 SIMULATIONS; MEAN ± SD; τ = τ_det)

| Scenario | AUC | AP | Recall | Precision | Tier changed (%) |
|---|---|---|---|---|---|
| Clean inputs | 0.823 | 0.250 | 0.973 | 0.075 | 0.0 |
| Glucose error only (σ = 35.6 mg/dL) | 0.820 ± 0.005 | 0.241 ± 0.010 | 0.973 | 0.074 | 2.9 ± 0.3 |
| Hypertension-flag error only (27.3% flips) | 0.821 ± 0.002 | 0.242 ± 0.010 | 0.973 | 0.075 | 1.2 ± 0.2 |
| Both errors | 0.818 ± 0.005 | 0.235 ± 0.012 | 0.973 | 0.074 | 3.8 ± 0.4 |

*Glucose noise ~ N(0, σ²) with σ equal to the LOSO glucose RMSE in Table II; hypertension flags flipped independently at the observed disagreement rate (3 of 11 volunteers). Values clipped to 40–400 mg/dL.*

Two of the classifier's nine inputs come from PPG estimates in deployment, the average glucose level and the hypertension flag, so the observed estimation errors were propagated into the classifier. The public dataset has no blood pressure, so blood-pressure error is represented through the hypertension flag: the flag derived from the estimated blood pressure agreed with the flag from the reference readings in 8 of 11 volunteers (7 of the 9 hypertensive volunteers were flagged), and this disagreement rate was applied as a symmetric flip probability, which is an approximation. With the full LOSO glucose error (σ = 35.6 mg/dL) and the flag error together, the AUC changed from 0.823 to 0.818, the recall at τ_det remained 0.973, and only 3.8% of the risk tiers changed (Table VI). The alert output is therefore stable against the estimation errors observed in this study. This stability also reflects the structure of the model: age, which comes from the user profile, carries half of the importance, so the tier is anchored by profile data, while the PPG-derived inputs act as complementary modifiers that can be refreshed at every measurement. A classifier trained on data that include PPG-derived measurements from the target population is a natural next step.

## IV. CONCLUSION

*(Satu paragraf, sesuai aturan JAEE: temuan, keterbatasan, dan saran.)*

This study presented a pre-hospital early-warning system that links a three-wavelength PPG wristband, server-side signal processing, five physiological estimators, and a class-weighted XGBoost stroke-risk classifier, and that delivers the results to a family caregiver through a mobile application. Streamed heart-rate estimation agreed with a finger oximeter with a mean absolute error of 1.2 bpm, and the leave-one-subject-out accuracy of the five estimators against reference devices was 91.0% for systolic and 91.4% for diastolic blood pressure, 76.2% for glucose, 85.1% for cholesterol, and 86.2% for uric acid in the 11 volunteers. The stroke-risk classifier reached an AUC of 0.823 (95% CI 0.780–0.865) with a recall of 0.973 at its screening threshold, its three risk tiers separated observed stroke rates of 0.4%, 4.5%, and 20.6%, and the tier changed for only 3.8% of the people when the observed estimation errors were propagated into it. The proposed system is intended as pre-hospital screening support that prompts a medical evaluation, not as a diagnostic device. The main limitations are the small cohort (n = 11, one ten-second recording each, two volunteers with a history of stroke), the use of the same volunteers to select and evaluate the estimation models, a classifier trained on a public dataset without PPG-derived inputs, and an alert rate of 63.8% at the screening threshold. Future work should recruit at least 30 volunteers with repeated sessions and a separate test set, add a second measurement site for pulse-transit-time features, recalibrate the thresholds for a lower alert burden, and train and validate the classifier prospectively on data collected with the device.

## ACKNOWLEDGMENT

The authors thank the volunteers who took part in the data collection, Klinik Parahita for the laboratory analysis, the Health Research Ethics Committee of the Faculty of Public Health, Universitas Airlangga, for the ethical review, the neurologist who reviewed the clinical risk parameters used in this study, and their academic supervisor for guidance throughout the work.

## REFERENCES

*(Nomor [1]–[14] tetap sesuai naskah Anda. Tambahkan [15]–[25] berikut, urut menurut kemunculan di teks.)*

[15] J. Park, H. S. Seok, S.-S. Kim, and H. Shin, "Photoplethysmogram analysis and applications: An integrative review," *Front. Physiol.*, vol. 12, Art. no. 808451, Mar. 2022, doi: 10.3389/fphys.2021.808451.

[16] A. J. Smola and B. Schölkopf, "A tutorial on support vector regression," *Stat. Comput.*, vol. 14, no. 3, pp. 199–222, Aug. 2004, doi: 10.1023/B:STCO.0000035301.49549.88.

[17] T. Chen and C. Guestrin, "XGBoost: A scalable tree boosting system," in *Proc. 22nd ACM SIGKDD Int. Conf. Knowl. Discov. Data Min.*, San Francisco, CA, USA, 2016, pp. 785–794, doi: 10.1145/2939672.2939785.

[18] fedesoriano, "Stroke prediction dataset," Kaggle, 2021. [Online]. Available: https://www.kaggle.com/datasets/fedesoriano/stroke-prediction-dataset *(cek nama pengunggah/tahun; lihat 0.4)*

[19] Q. Zou, S. Xie, Z. Lin, M. Wu, and Y. Ju, "Finding the best classification threshold in imbalanced classification," *Big Data Res.*, vol. 5, pp. 2–8, Sep. 2016. *(tambahkan DOI setelah dicek)*

[20] T. Saito and M. Rehmsmeier, "The precision-recall plot is more informative than the ROC plot when evaluating binary classifiers on imbalanced datasets," *PLoS One*, vol. 10, no. 3, Art. no. e0118432, Mar. 2015, doi: 10.1371/journal.pone.0118432.

[21] S. Mehta, N. Kwatra, M. Jain, and D. McDuff, "Examining the challenges of blood pressure estimation via photoplethysmogram," *Sci. Rep.*, vol. 14, Aug. 2024, doi: 10.1038/s41598-024-68862-1.

[22] J. Lee, M. Kim, H.-K. Park, and I. Y. Kim, "Motion artifact reduction in wearable photoplethysmography based on multi-channel sensors with multiple wavelengths," *Sensors*, vol. 20, no. 5, p. 1493, Mar. 2020, doi: 10.3390/s20051493.

[23] M. Zeynali, K. Alipour, B. Tarvirdizadeh, and M. Ghamari, "Non-invasive blood glucose monitoring using PPG signals with various deep learning models and implementation using TinyML," *Sci. Rep.*, vol. 15, Art. no. 581, 2025, doi: 10.1038/s41598-024-84265-8.

[24] M. J. O'Donnell *et al.*, "Global and regional effects of potentially modifiable risk factors associated with acute stroke in 32 countries (INTERSTROKE): A case-control study," *Lancet*, vol. 388, no. 10046, pp. 761–775, Aug. 2016, doi: 10.1016/S0140-6736(16)30506-2.

[25] M. Yousufuddin and N. Young, "Aging and ischemic stroke," *Aging (Albany NY)*, vol. 11, no. 9, pp. 2542–2544, May 2019, doi: 10.18632/aging.101931.

*(Semua entri [15]–[25] judul, penulis, dan DOI-nya dicocokkan lewat pencarian web di sesi ini; PDF lengkapnya belum dibaca — unduh dan cek sebelum submit, sama seperti catatan di `list-tanya-jawab.md`.)*
