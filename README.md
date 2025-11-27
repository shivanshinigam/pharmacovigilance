
# BCPNN – Drug Side Effect Signal Detection using FDA FAERS

## 📌 Project Overview

This project implements a pharmacovigilance system using the **Bayesian Confidence Propagation Neural Network (BCPNN)** approach to detect potentially unsafe drug–side effect relationships.

The system answers one core question:

“Does this drug appear unusually often with this side effect compared to random chance?”

It does not diagnose disease — it identifies statistically suspicious drug–ADR combinations.

---

## 📂 Data Source

The dataset comes from the **FDA FAERS (Adverse Event Reporting System)** database which contains real-world adverse event reports.

Official source:
https://fis.fda.gov/extensions/FPD-QDE-FAERS/FPD-QDE-FAERS.html

Files used:
- DRUG file → drug names per report
- REAC file → adverse reactions per report

For fast execution, trimmed samples were used:

data/drug_small.txt  
data/adr_small.txt  

Each file contains the first 5000 records.

---

## 📁 Project Structure

pharma/
  ├── code.py
  ├── README.md
  └── data/
       ├── drug_small.txt
       └── adr_small.txt


---

## 🧩 How the System Works

### 1. Data Parsing

Each report lists:
- Drugs taken
- Reactions reported

Reports are linked using a unique report ID.

---

### 2. Association Table Construction

For each drug–reaction pair, a 2×2 frequency table is built:

|                 | ADR Present | ADR Absent |
|-----------------|-------------|------------|
| Drug Present    | a           | b          |
| Drug Absent     | c           | d          |

---

### 3. Bayesian Scoring

The model computes:

- Expectation (IC) → Strength of association
- Variance / Standard Deviation → Uncertainty
- Adjusted Score = IC − 2 × Std Dev

This ensures unreliable signals are penalized.

---

### 4. Signal Categories

| Category | Meaning |
|----------|--------|
| none | No association |
| weak | Slight association |
| moderate | Likely association |
| strong | Potential safety risk |

---

## 📊 Program Output
- The screenshot below shows how many drug–ADR pairs were classified into each signal category.

<img width="508" height="164" alt="Screenshot 2025-11-27 at 7 02 32 PM" src="https://github.com/user-attachments/assets/8ca76e27-2d7e-4731-8dff-148e075ee826" />

### Interpretation

- Most drug–ADR pairs show no relationship (expected).
- Only **14 pairs** showed strong suspicious patterns.
- This mirrors real pharmacovigilance where strong safety signals are rare.
- These are statistical signals, not confirmed medical side effects.

---

## 🔝 Top 20 Strongest Drug–ADR Pairs
- The following screenshot shows the drug–ADR combinations with the highest adjusted signal scores:
  
<img width="890" height="313" alt="Screenshot 2025-11-27 at 7 02 44 PM" src="https://github.com/user-attachments/assets/e347c984-f10e-49f3-ba91-ed3329f21545" />


### Meaning:

These combinations appeared unusually often.

They indicate potential safety risks needing further investigation.

---

## 🔎 Query Result Example
The system allows checking any specific drug–ADR pair.

User input:

<img width="593" height="321" alt="Screenshot 2025-11-27 at 7 02 55 PM" src="https://github.com/user-attachments/assets/09ef14d9-fdb0-48b6-a374-bfe8b00d7fe2" />


### Interpretation

Only **1 report** showed both the drug and reaction.

This is not enough evidence to conclude a real relationship.

Hence → **NO SIGNAL**.

## Understanding the query numbers

For each checked (drug, ADR) pair, the system prints:

| Value | Meaning |
|-------|---------|
| a | drug & ADR occurred together |
| b | drug appeared without ADR |
| c | ADR appeared without drug |
| d | neither occurred |

When **a** is very small compared to **b**, **c**, and **d**, the signal is weak or rejected.

## Bayesian Priors (Important Detail)

BCPNN is a Bayesian model and can optionally use prior knowledge.

The program supports an optional file:

adr-drug.csv

If present, this file provides historical probabilities for each drug–ADR pair.

If missing (as in this project), neutral default values are used:

alp = 2  
alp1 = 1  
bet = 2  
bet1 = 1  
g11 = 1  

### Meaning

All drugs and ADRs start with equal assumptions.

Results are driven purely by data.

Using fake or guessed priors can distort results, so neutral priors were intentionally chosen.








