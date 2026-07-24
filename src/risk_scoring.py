from pathlib import Path

import pandas as pd

###risk score standard

# PEP	+40
# Unknown source of funds	+20
# Pending documents	+15
# Rejected documents	+40
# Potential sanctions match	+50


# 0–29   Low
# 30–59  Medium
# 60 up    High



# Project paths
ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "data" / "processed" / "customer_profile.csv"
OUTPUT_PATH = ROOT / "data" / "processed" / "customer_risk_results.csv"

#  Calculate a customer's risk score based on synthetic KYC attributes."

def calculate_risk(row: pd.Series) -> pd.Series:
   

    risk_score = 0
    risk_reasons = []

    # PEP screening
    if row["PEP_STATUS"] == "Yes":
        risk_score += 40
        risk_reasons.append("PEP status")

    # Source of funds assessment
    if row["SOURCE_OF_FUNDS"] == "Unknown":
        risk_score += 20
        risk_reasons.append("Unknown source of funds")

    # Document verification
    if row["DOCUMENT_STATUS"] == "Pending":
        risk_score += 15
        risk_reasons.append("Pending documents")

    elif row["DOCUMENT_STATUS"] == "Rejected":
        risk_score += 40
        risk_reasons.append("Rejected documents")

    # Sanctions screening
    if row["SANCTIONS_STATUS"] == "Potential Match":
        risk_score += 50
        risk_reasons.append("Potential sanctions match")

    # Assign risk level
    if risk_score >= 60:
        risk_level = "High"
    elif risk_score >= 30:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    # Determine KYC status
    if row["DOCUMENT_STATUS"] == "Rejected":
        kyc_status = "Rejected"
    elif row["SANCTIONS_STATUS"] == "Potential Match":
        kyc_status = "Manual Review"
    elif row["DOCUMENT_STATUS"] == "Pending":
        kyc_status = "Pending"
    else:
        kyc_status = "Verified"

    # Trigger EDD for high-risk customers, PEPs, or sanctions matches
    edd_required = (
        risk_level == "High"
        or row["PEP_STATUS"] == "Yes"
        or row["SANCTIONS_STATUS"] == "Potential Match"
    )

    return pd.Series(
        {
            "KYC_STATUS": kyc_status,
            "RISK_SCORE": risk_score,
            "RISK_LEVEL": risk_level,
            "RISK_REASONS": (
                "; ".join(risk_reasons)
                if risk_reasons
                else "No major risk indicators"
            ),
            "EDD_REQUIRED": "Yes" if edd_required else "No",
            "EDD_STATUS": (
                "Pending Review"
                if edd_required
                else "Not Required"
            ),
        }
    )


# Read customer profiles, calculate risk, and save the results.

def score_customers() -> pd.DataFrame:
    """Read customer profiles, calculate risk, and save the results."""

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_PATH}\n"
            "Run customer_profile_generator.py first."
        )

    customer_profiles = pd.read_csv(INPUT_PATH)

    required_columns = {
        "PEP_STATUS",
        "SOURCE_OF_FUNDS",
        "DOCUMENT_STATUS",
        "SANCTIONS_STATUS",
    }

    missing_columns = required_columns - set(customer_profiles.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    risk_results = customer_profiles.apply(
        calculate_risk,
        axis=1,
    )

    final_results = pd.concat(
        [customer_profiles, risk_results],
        axis=1,
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    final_results.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    return final_results


if __name__ == "__main__":
    results = score_customers()

    print("Customer risk scoring completed successfully!")
    print(f"Output file: {OUTPUT_PATH}")

    print("\nRisk level distribution:")
    print(results["RISK_LEVEL"].value_counts())

    print("\nKYC status distribution:")
    print(results["KYC_STATUS"].value_counts())

    print("\nEDD requirement distribution:")
    print(results["EDD_REQUIRED"].value_counts())

    print("\nSample results:")
    print(
        results[
            [
                "ACCOUNT_ID",
                "PEP_STATUS",
                "SOURCE_OF_FUNDS",
                "DOCUMENT_STATUS",
                "SANCTIONS_STATUS",
                "KYC_STATUS",
                "RISK_SCORE",
                "RISK_LEVEL",
            ]
        ].head()
    )