import pandas as pd
import re
from pathlib import Path

# Configuration - change these paths as needed
INPUT_CSV = "/home/andrewlo/Documents/MyProject/MyHomeWork/FakeDataProcessed/customers_raw.csv"
OUTPUT_CLEAN_CSV = "/home/andrewlo/Documents/MyProject/MyHomeWork/FakeDataProcessed/customers_cleaned.csv"
OUTPUT_ISSUES_CSV = "/home/andrewlo/Documents/MyProject/MyHomeWork/FakeDataProcessed/customers_issues_report.csv"

def is_normal_name(name_str):
    """
    Very strict name validation:
      Allowed: unicode letters, space, hyphen (-), apostrophe (')
      Forbidden: ~ ! @ # $ % ^ & * ( ) = + { } [ ] \ | : ; " < > ? / * and most other symbols
    """
    if not isinstance(name_str, str) or not name_str.strip():
        return False

    # Only letters + space + - + '
    pattern = r'^[\p{L}\s\'-]+$'
    return bool(re.match(pattern, name_str.strip()))


def is_valid_email(email_str):
    """Very practical email format check (not 100% RFC5322 compliant, but good enough for most cases)"""
    if pd.isna(email_str) or not isinstance(email_str, str):
        return False
    email_str = email_str.strip()
    # Basic regex - allows most common valid patterns
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email_str))


def check_and_clean_customer_data(input_file, output_clean_file, output_issues_file):
    """
    Reads CSV, validates data according to Django Customer model rules,
    reports issues, and saves cleaned version
    """
    print(f"Reading file: {input_file}\n")

    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        return
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    # Make a copy for cleaning
    df_clean = df.copy()

    # ────────────────────────────────────────────────
    # Initialize issue tracking columns
    # ────────────────────────────────────────────────
    df['issues'] = ''

    # 1. Empty / missing name
    mask_empty_name = df['name'].isna() | (df['name'].astype(str).str.strip() == '')
    df.loc[mask_empty_name, 'issues'] += 'Empty name; '

    # 2. Invalid email format or empty (since model requires email)
    mask_bad_email = ~df['email'].apply(is_valid_email)
    df.loc[mask_bad_email, 'issues'] += 'Invalid or empty email; '

    # 3. Empty city (allowed, but we'll flag it for review)
    mask_empty_city = df['city'].isna() | (df['city'].astype(str).str.strip() == '')
    df.loc[mask_empty_city, 'issues'] += 'Empty city; '

    # 4. Negative or non-integer age
    # Convert to numeric first, errors become NaN
    df_clean['age'] = pd.to_numeric(df['age'], errors='coerce')
    mask_negative_age = df_clean['age'] < 0
    mask_non_integer = df_clean['age'].notna() & (df_clean['age'] % 1 != 0)
    df.loc[mask_negative_age, 'issues'] += 'Negative age; '
    df.loc[mask_non_integer, 'issues'] += 'Non-integer age; '

    # ────────────────────────────────────────────────
    # Clean the data for export
    # ────────────────────────────────────────────────

    # Remove rows with critical issues (name or email invalid)
    critical_mask = mask_empty_name | mask_bad_email
    df_clean = df_clean[~critical_mask].copy()

    # Optional: fill empty cities with something (or leave blank)
    df_clean['city'] = df_clean['city'].fillna('').astype(str).str.strip()

    # Age: keep only valid non-negative integers or NaN
    df_clean['age'] = df_clean['age'].apply(
        lambda x: int(x) if pd.notna(x) and x >= 0 and x == int(x) else None
    )

    # Strip whitespace from name & city
    df_clean['name'] = df_clean['name'].astype(str).str.strip()
    df_clean['city'] = df_clean['city'].str.strip()

    # ────────────────────────────────────────────────
    # Save results
    # ────────────────────────────────────────────────
    issues_df = df[df['issues'] != ''][['name', 'email', 'age', 'city', 'issues']]
    issues_df['issues'] = issues_df['issues'].str.rstrip('; ')

    if not issues_df.empty:
        issues_df.to_csv(output_issues_file, index=False)
        print(f"Issues report saved → {output_issues_file}")
        print(f"Found {len(issues_df)} rows with problems\n")
    else:
        print("No data quality issues found!\n")

    # Save cleaned data
    df_clean.to_csv(output_clean_file, index=False)
    print(f"Cleaned data saved → {output_clean_file}")
    print(f"Rows before: {len(df):,}")
    print(f"Rows after : {len(df_clean):,}")
    print(f"Removed    : {len(df) - len(df_clean):,} rows")


if __name__ == "__main__":
    print("Customer CSV Data Quality Check\n")
    print("Model reference:")
    print("• name     : required, max 100 chars")
    print("• email    : required, valid email, unique")
    print("• age      : integer, can be null")
    print("• city     : max 100 chars, can be blank\n")

    check_and_clean_customer_data(
        INPUT_CSV,
        OUTPUT_CLEAN_CSV,
        OUTPUT_ISSUES_CSV
    )