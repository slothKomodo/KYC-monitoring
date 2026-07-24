import random
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "data" / "raw" / "accounts.csv"
OUTPUT_PATH = ROOT / "data" / "processed" / "customer_profile.csv"

random.seed(42)


def assign_source_of_funds(occupation: str) -> str:
    mapping = {
        "Engineer": ["Salary", "Salary", "Savings", "Investment"],
        "Teacher": ["Salary", "Salary", "Savings"],
        "Software Developer": ["Salary", "Salary", "Investment", "Savings"],
        "Business Owner": [
            "Business Income",
            "Business Income",
            "Savings",
            "Investment",
        ],
        "Student": [
            "Family Support",
            "Family Support",
            "Savings",
        ],
        "Consultant": [
            "Salary",
            "Business Income",
            "Savings",
            "Investment",
        ],
    }

    source = random.choice(mapping[occupation])

    # Keep a small proportion unclear for risk-assessment simulation
    if random.random() < 0.08:
        return "Unknown"

    return source


def assign_pep_status(occupation: str) -> str:
    # Synthetic assumption for workflow testing only
    pep_probability = 0.10 if occupation == "Consultant" else 0.03
    return "Yes" if random.random() < pep_probability else "No"


def generate_customer_profiles() -> pd.DataFrame:
    accounts = pd.read_csv(INPUT_PATH)
    profiles = accounts.copy()

    occupations = [
        "Engineer",
        "Business Owner",
        "Teacher",
        "Student",
        "Consultant",
        "Software Developer",
    ]

    profiles["OCCUPATION"] = [
        random.choice(occupations)
        for _ in range(len(profiles))
    ]

    profiles["SOURCE_OF_FUNDS"] = profiles["OCCUPATION"].apply(
        assign_source_of_funds
    )

    profiles["PEP_STATUS"] = profiles["OCCUPATION"].apply(
        assign_pep_status
    )

    profiles["DOCUMENT_STATUS"] = [
        random.choices(
            ["Verified", "Pending", "Rejected"],
            weights=[90, 8, 2],
            k=1,
        )[0]
        for _ in range(len(profiles))
    ]

    profiles["SANCTIONS_STATUS"] = [
        random.choices(
            ["Cleared", "Potential Match"],
            weights=[98, 2],
            k=1,
        )[0]
        for _ in range(len(profiles))
    ]

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    profiles.to_csv(OUTPUT_PATH, index=False)

    return profiles


if __name__ == "__main__":
    customer_profile = generate_customer_profiles()

    print("Customer profile generated successfully!")
    print(customer_profile.head())

    print("\nSource of funds by occupation:")
    print(
        pd.crosstab(
            customer_profile["OCCUPATION"],
            customer_profile["SOURCE_OF_FUNDS"],
        )
    )


# KYC-related attributes were synthetically generated using rule-based conditional distributions because IBM AMLSim does not provide full onboarding information. 
# These fields are used only to demonstrate workflow logic and are not intended to represent real customer risk.