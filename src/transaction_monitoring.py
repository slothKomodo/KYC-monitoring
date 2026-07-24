from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

TRANSACTIONS_PATH = ROOT / "data" / "raw" / "transactions.csv"
CUSTOMER_RISK_PATH = (
    ROOT / "data" / "processed" / "customer_risk_results.csv"
)
OUTPUT_PATH = ROOT / "data" / "processed" / "alerts.csv"


def build_alert_reason(row: pd.Series) -> str:
    reasons = []

    if row["RULE_LARGE_TRANSACTION"]:
        reasons.append("Large transaction")

    if row["RULE_HIGH_RISK_CUSTOMER"]:
        reasons.append("High-risk customer activity")

    if row["RULE_HIGH_FREQUENCY"]:
        reasons.append("High transaction frequency")

    if row["RULE_FAN_OUT"]:
        reasons.append("Fan-out activity")

    return "; ".join(reasons)


def assign_alert_severity(row: pd.Series) -> str:
    if (
        row["RISK_LEVEL"] == "High"
        or row["RULE_LARGE_TRANSACTION"]
    ):
        return "High"

    return "Medium"


def monitor_transactions() -> pd.DataFrame:
    if not TRANSACTIONS_PATH.exists():
        raise FileNotFoundError(
            f"Transaction file not found: {TRANSACTIONS_PATH}"
        )

    if not CUSTOMER_RISK_PATH.exists():
        raise FileNotFoundError(
            f"Customer risk file not found: {CUSTOMER_RISK_PATH}\n"
            "Run risk_scoring.py first."
        )

    transactions = pd.read_csv(TRANSACTIONS_PATH)
    customer_risk = pd.read_csv(CUSTOMER_RISK_PATH)

    transactions["TIMESTAMP"] = pd.to_datetime(
        transactions["TIMESTAMP"],
        errors="coerce",
    )

    customer_columns = [
        "ACCOUNT_ID",
        "CUSTOMER_ID",
        "PEP_STATUS",          # 新增
        "KYC_STATUS",
        "RISK_SCORE",
        "RISK_LEVEL",
        "EDD_REQUIRED",
]

    monitored = transactions.merge(
        customer_risk[customer_columns],
        left_on="SENDER_ACCOUNT_ID",
        right_on="ACCOUNT_ID",
        how="left",
    )

    # Dataset-relative thresholds
    large_transaction_threshold = transactions[
        "TX_AMOUNT"
    ].quantile(0.99)

    high_risk_transaction_threshold = transactions[
        "TX_AMOUNT"
    ].quantile(0.95)

    # Rule 1: top 1% transaction amounts
    monitored["RULE_LARGE_TRANSACTION"] = (
        monitored["TX_AMOUNT"] >= large_transaction_threshold
    )

    # Rule 2: transactions from high-risk customers above the 95th percentile
    monitored["RULE_HIGH_RISK_CUSTOMER"] = (
        (monitored["RISK_LEVEL"] == "High")
        & (
            monitored["TX_AMOUNT"]
            >= high_risk_transaction_threshold
        )
    )

    # Rule 3: 10 or more transactions in the same 30-minute window
    monitored["TIME_WINDOW_30_MIN"] = monitored[
        "TIMESTAMP"
    ].dt.floor("30min")

    monitored["TX_COUNT_30_MIN"] = (
        monitored.groupby(
            ["SENDER_ACCOUNT_ID", "TIME_WINDOW_30_MIN"]
        )["TX_ID"]
        .transform("count")
    )

    frequency_threshold = monitored["TX_COUNT_30_MIN"].quantile(0.99)

    monitored["RULE_HIGH_FREQUENCY"] = (
        monitored["TX_COUNT_30_MIN"] >= frequency_threshold
    )

    # Count unique receivers per sender in each time window
    monitored["UNIQUE_RECEIVER_COUNT_30_MIN"] = (
        monitored.groupby(
            ["SENDER_ACCOUNT_ID", "TIME_WINDOW_30_MIN"]
        )["RECEIVER_ACCOUNT_ID"]
        .transform("nunique")
    )

    fan_out_threshold = monitored[
        "UNIQUE_RECEIVER_COUNT_30_MIN"
    ].quantile(0.99)

    monitored["RULE_FAN_OUT"] = (
        monitored["UNIQUE_RECEIVER_COUNT_30_MIN"]
        >= fan_out_threshold
    )

    # Rule 4: High-value transaction by a PEP
    monitored["RULE_PEP"] = (
        (monitored["PEP_STATUS"] == "Yes")
        & (monitored["TX_AMOUNT"] >= high_risk_transaction_threshold)
    )

    monitored["ALERT_REASON"] = monitored.apply(
        build_alert_reason,
        axis=1,
    )

    
    alerts = monitored[
        monitored["ALERT_REASON"] != ""
    ].copy()

    alerts = alerts.reset_index(drop=True)

    alerts["GENERATED_ALERT_ID"] = [
        f"AML-{index + 1:06d}"
        for index in range(len(alerts))
    ]

    alerts["ALERT_SEVERITY"] = alerts.apply(
        assign_alert_severity,
        axis=1,
    )

    alerts["CASE_STATUS"] = "Open"

    output_columns = [
        "GENERATED_ALERT_ID",
        "TX_ID",
        "SENDER_ACCOUNT_ID",
        "RECEIVER_ACCOUNT_ID",
        "CUSTOMER_ID",
        "TX_AMOUNT",
        "TIMESTAMP",
        "KYC_STATUS",
        "RISK_SCORE",
        "RISK_LEVEL",
        "EDD_REQUIRED",
        "TX_COUNT_30_MIN",
        "UNIQUE_RECEIVER_COUNT_30_MIN",
        "ALERT_REASON",
        "ALERT_SEVERITY",
        "CASE_STATUS",
        "IS_FRAUD",
    ]

    alerts = alerts[output_columns]

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    alerts.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print(
        f"Large transaction threshold: "
        f"{large_transaction_threshold:.2f}"
    )

    print(
        f"High-risk transaction threshold: "
        f"{high_risk_transaction_threshold:.2f}"
    )

    print(
        f"High-frequency threshold: "
        f"{frequency_threshold:.0f} transactions per 30 minutes"
    )

    print(
        f"Fan-out threshold: "
        f"{fan_out_threshold:.0f} unique receivers per 30 minutes"
    )
    return alerts


if __name__ == "__main__":
    results = monitor_transactions()

    print("\nTransaction monitoring completed successfully!")
    print(f"Generated alerts: {len(results)}")
    print(f"Output file: {OUTPUT_PATH}")

    if not results.empty:
        print("\nAlert severity distribution:")
        print(results["ALERT_SEVERITY"].value_counts())

        print("\nTop alert reasons:")
        print(results["ALERT_REASON"].value_counts().head(10))

        print("\nKnown fraudulent transactions detected:")
        print(int(results["IS_FRAUD"].sum()))

        print("\nSample alerts:")
        print(
            results[
                [
                    "GENERATED_ALERT_ID",
                    "TX_ID",
                    "SENDER_ACCOUNT_ID",
                    "TX_AMOUNT",
                    "RISK_LEVEL",
                    "ALERT_REASON",
                    "ALERT_SEVERITY",
                ]
            ].head()
        )

        print(
            "\nAlert rate:",
            f"{len(results) / len(pd.read_csv(TRANSACTIONS_PATH)):.2%}"
        )

    else:
        print("No alerts were generated.")