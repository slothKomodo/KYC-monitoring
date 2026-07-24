# KYC Onboarding & AML Transaction Monitoring Prototype

This project implements a rule-based KYC onboarding and AML transaction monitoring workflow using Python and the IBM AMLSim synthetic dataset.

The goal of this project is to learn how customer onboarding, risk assessment, Enhanced Due Diligence (EDD), and transaction monitoring work together in a compliance workflow.

## Why this project?

I built this project to better understand how KYC onboarding and AML transaction monitoring work in financial institutions.

Since IBM AMLSim focuses on transaction data rather than customer onboarding, I generated synthetic KYC information to simulate a complete compliance workflow.

## Project Overview

This project demonstrates a rule-based compliance workflow commonly used by financial institutions and fintech companies.

The workflow includes:

- Customer profile generation
- KYC onboarding
- Customer risk assessment
- Enhanced Due Diligence (EDD)
- AML transaction monitoring
- Alert generation

Because IBM AMLSim does not provide customer onboarding information, synthetic KYC attributes are generated to simulate a realistic onboarding process.

---

## Workflow

```text
┌──────────────────┐
│ Accounts Dataset │
└──────────────────┘
          │
          ▼
┌───────────────────────┐
│ KYC Profile Generator │
└───────────────────────┘
          │
          ▼
┌──────────────────┐
│   Risk Scoring   │
└──────────────────┘
          │
          ▼
┌──────────────────┐
│   EDD Decision   │
└──────────────────┘
          │
          ▼
┌──────────────────────────┐
│ Transaction Monitoring   │
└──────────────────────────┘
          │
          ▼
┌──────────────────┐
│    AML Alerts    │
└──────────────────┘
```

## Features

- Generate synthetic customer KYC profiles
- Calculate customer risk scores using rule-based logic
- Flag customers for Enhanced Due Diligence (EDD)
- Monitor transactions using several AML rules
- Generate AML alerts

## Project Structure


```text
kyc-aml-monitoring/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── notebooks/
│   └── exploratory_analysis.ipynb
│
├── src/
│   ├── customer_profile_generator.py
│   ├── risk_scoring.py
│   └── transaction_monitoring.py
│
├── README.md
└── requirements.txt
```

## Technologies

- Python
- Pandas
- NumPy
- IBM AMLSim
- Rule-based Risk Engine

## How to Run

```bash
python src/customer_profile_generator.py
python src/risk_scoring.py
python src/transaction_monitoring.py
```

---

## Example Outputs

The project generates:

- customer_profile.csv
- customer_risk_results.csv
- aml_alerts.csv

---

## Future Improvements

Possible future enhancements include:

- Graph-based AML Detection
- Machine Learning Risk Models
- Suspicious Network Visualization

---

## Disclaimer

This project is intended for educational and portfolio purposes only.

Risk scoring rules, monitoring thresholds, and generated customer attributes are simplified assumptions designed to demonstrate AML compliance workflows and do not represent production compliance policies.