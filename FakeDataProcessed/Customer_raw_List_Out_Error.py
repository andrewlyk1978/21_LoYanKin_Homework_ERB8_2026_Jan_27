import pandas as pd
import re

# ---- config ----
INPUT_CSV = "/home/andrewlo/Documents/MyProject/MyHomeWork/FakeDataProcessed/customers_raw.csv"      
# your input file
OUTPUT_ERRORS_CSV = "/home/andrewlo/Documents/MyProject/MyHomeWork/FakeDataProcessed/customers_errors.csv"  
# output (invalid rows)
# /home/andrewlo/.virtualenvs/erb8/bin/python /home/andrewlo/Documents/MyProject/MyHomeWork/FakeDataProcessed/customer_raw.py
# home/andrewlo/Documents/MyProject/MyHomeWork/FakeDataProcessed/customer_raw.py


# Simple email regex: something@something.something
EMAIL_REGEX = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')


def is_valid_email(email: str) -> bool:
    if pd.isna(email):
        return False
    return bool(EMAIL_REGEX.match(str(email)))


def main():
    # 1) Load CSV
    df = pd.read_csv(INPUT_CSV)

    # Ensure expected columns exist
    required_cols = ["name", "email", "age", "city"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in CSV: {missing}")

    # 2) Build boolean masks for each error type

    # empty name (NaN or empty string after strip)
    mask_empty_name = df["name"].isna() | (df["name"].astype(str).str.strip() == "")

    # wrong email format (NaN or does not match regex)
    mask_wrong_email = ~df["email"].astype(str).apply(is_valid_email)

    # empty city (NaN or empty string after strip)
    mask_empty_city = df["city"].isna() | (df["city"].astype(str).str.strip() == "")

    # negative age (age < 0, ignoring NaN)
    mask_negative_age = df["age"].notna() & (df["age"] < 0)

    # 3) Combine all error conditions
    mask_any_error = mask_empty_name | mask_wrong_email | mask_empty_city | mask_negative_age

    # 4) Create an error report DataFrame
    errors_df = df[mask_any_error].copy()

    # Add helper columns to explain what is wrong
    errors_df["error_empty_name"] = mask_empty_name[mask_any_error]
    errors_df["error_wrong_email"] = mask_wrong_email[mask_any_error]
    errors_df["error_empty_city"] = mask_empty_city[mask_any_error]
    errors_df["error_negative_age"] = mask_negative_age[mask_any_error]

    # 5) Export invalid rows to CSV
    errors_df.to_csv(OUTPUT_ERRORS_CSV, index=False)

    # Print a quick summary
    print("Total rows:", len(df))
    print("Rows with errors:", len(errors_df))
    print(" - Empty name:", mask_empty_name.sum())
    print(" - Wrong email format:", mask_wrong_email.sum())
    print(" - Empty city:", mask_empty_city.sum())
    print(" - Negative age:", mask_negative_age.sum())
    print(f"Invalid rows exported to: {OUTPUT_ERRORS_CSV}")


if __name__ == "__main__":
    main()
