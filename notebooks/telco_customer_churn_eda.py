from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "WA_Fn-UseC_-Telco-Customer-Churn.csv"
IMAGE_DIR = PROJECT_ROOT / "images"

# Load the customer-level dataset.
df = pd.read_csv(DATA_PATH)
print("Dataset shape:", df.shape)
print("\nFirst five rows:")
print(df.head())

# Review column types and data quality before analysis.
print("\nColumn information:")
df.info()
print("\nMissing values per column:")
print(df.isna().sum())
print("\nDuplicate rows:", df.duplicated().sum())
print("Duplicate customer IDs:", df["customerID"].duplicated().sum())

# Convert whitespace-only TotalCharges values to missing numeric values.
blank_total_charges = df["TotalCharges"].astype(str).str.strip().eq("")
print("\nBlank TotalCharges entries:", blank_total_charges.sum())
numeric_total_charges = pd.to_numeric(df["TotalCharges"], errors="coerce")
unexpected_total_charges = numeric_total_charges.isna() & ~blank_total_charges
if unexpected_total_charges.any():
    raise ValueError("Found nonblank TotalCharges values that are not numeric.")
df["TotalCharges"] = numeric_total_charges

# All 11 blanks belong to customers with zero tenure. Use zero total charges
# for those records so they remain in the analysis rather than being dropped.
zero_tenure_blanks = blank_total_charges & df["tenure"].eq(0)
if blank_total_charges.sum() != 11 or not zero_tenure_blanks.equals(blank_total_charges):
    raise ValueError("Unexpected blank TotalCharges records; review before filling.")
df.loc[zero_tenure_blanks, "TotalCharges"] = 0
remaining_missing_total_charges = df["TotalCharges"].isna().sum()
if remaining_missing_total_charges:
    raise ValueError(
        f"Unexpected missing TotalCharges values remain: {remaining_missing_total_charges}"
    )
print("Missing TotalCharges after cleaning:", remaining_missing_total_charges)

# Overall churn and monthly charge summaries.
print("\nChurn counts:")
print(df["Churn"].value_counts())
print("\nChurn percentages:")
print(df["Churn"].value_counts(normalize=True).mul(100).round(2))
print("\nAverage monthly charges by churn status:")
print(df.groupby("Churn")["MonthlyCharges"].mean().round(2))

monthly_charges = df["MonthlyCharges"].to_numpy()
print("\nMonthly charge mean:", round(np.mean(monthly_charges), 2))
print("Monthly charge median:", round(np.median(monthly_charges), 2))

# Churn rates by contract type.
print("\nCustomer counts by contract:")
print(df["Contract"].value_counts())
churn_by_contract = df.groupby("Contract")["Churn"].apply(
    lambda churn: churn.eq("Yes").mean() * 100
)
print("\nChurn rate by contract (%):")
print(churn_by_contract.round(2))

# Churn rates by tenure group.
df["TenureGroup"] = np.where(
    df["tenure"] <= 12,
    "12 months or less",
    "More than 12 months",
)
print("\nCustomer counts by tenure group:")
print(df["TenureGroup"].value_counts())
churn_by_tenure = df.groupby("TenureGroup")["Churn"].apply(
    lambda churn: churn.eq("Yes").mean() * 100
)
print("\nChurn rate by tenure group (%):")
print(churn_by_tenure.round(2))

# One additional group comparison for the README findings.
churn_by_payment_method = df.groupby("PaymentMethod")["Churn"].apply(
    lambda churn: churn.eq("Yes").mean() * 100
)
print("\nChurn rate by payment method (%):")
print(churn_by_payment_method.round(2))

# Save the existing churn comparisons and still display them interactively.
IMAGE_DIR.mkdir(exist_ok=True)

fig, ax = plt.subplots(figsize=(8, 5))
contract_bars = ax.bar(churn_by_contract.index, churn_by_contract.values)
ax.set_title("Churn Rate by Contract Type")
ax.set_xlabel("Contract type")
ax.set_ylabel("Customers who churned (%)")
ax.set_ylim(0, 50)
ax.bar_label(contract_bars, fmt="%.1f%%", padding=3)
fig.tight_layout()
fig.savefig(IMAGE_DIR / "churn_by_contract.png", dpi=150)
if plt.get_backend().lower() != "agg":
    plt.show()
plt.close(fig)

fig, ax = plt.subplots(figsize=(8, 5))
tenure_bars = ax.bar(churn_by_tenure.index, churn_by_tenure.values)
ax.set_title("Churn Rate by Tenure Group")
ax.set_xlabel("Tenure group")
ax.set_ylabel("Customers who churned (%)")
ax.set_ylim(0, 55)
ax.tick_params(axis="x", labelrotation=10)
ax.bar_label(tenure_bars, fmt="%.1f%%", padding=3)
fig.tight_layout()
fig.savefig(IMAGE_DIR / "churn_by_tenure_group.png", dpi=150)
if plt.get_backend().lower() != "agg":
    plt.show()
plt.close(fig)
