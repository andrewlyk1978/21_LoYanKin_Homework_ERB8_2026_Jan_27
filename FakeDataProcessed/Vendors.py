import pandas as pd
import re
from pathlib import Path

# ────────────────────────────────────────────────
# CONFIGURATION - change filenames if needed
# ────────────────────────────────────────────────
INPUT_FILE       = "/home/andrewlo/Documents/MyProject/MyHomeWork/FakeDataProcessed/vendors_raw.csv"
ISSUES_REPORT    = "/home/andrewlo/Documents/MyProject/MyHomeWork/FakeDataProcessed/vendors_issues_report.csv"
CLEANED_OUTPUT   = "/home/andrewlo/Documents/MyProject/MyHomeWork/FakeDataProcessed/vendors_cleaned.csv"


def is_valid_email(email):
    """Basic but practical email validation"""
    if pd.isna(email) or not isinstance(email, str):
        return False
    email = email.strip()
    if not email:
        return False
    # Common valid pattern (not fully RFC 5322, but good enough)
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_and_clean_vendors():
    print("Vendor CSV Data Validation & Cleaning")
    print("Rules based on Django Vendor model:")
    print("• name  : required, non-empty, max 100 chars")
    print("• email : required, valid email format")
    print("• city  : optional, max 100 chars\n")

    # ───── Load data ─────
    try:
        df = pd.read_csv(INPUT_FILE)
        print(f"Loaded {len(df):,} rows from {INPUT_FILE}")
    except FileNotFoundError:
        print(f"Error: File '{INPUT_FILE}' not found.")
        return
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    df = df.copy()

    # ───── Collect issues ─────
    issues = []

    for idx, row in df.iterrows():
        problems = []

        # 1. Name validation
        name = str(row.get('name', '')).strip()
        if not name:
            problems.append("empty/missing name")
        elif len(name) > 100:
            problems.append("name too long (>100 chars)")

        # 2. Email validation
        email = row.get('email')
        if not is_valid_email(email):
            problems.append("invalid or missing email")

        # 3. City validation (only length & reporting emptiness)
        city = str(row.get('city', '')).strip()
        if len(city) > 100:
            problems.append("city too long (>100 chars)")
        # empty city is allowed → only report if you want to review them
        # if not city:
        #     problems.append("empty city (allowed)")

        if problems:
            issues.append({
                'row': idx + 1,               # 1-based row number (after header)
                'name': row.get('name'),
                'email': row.get('email'),
                'city': row.get('city'),
                'issues': '; '.join(problems)
            })

    # ───── Save issues report ─────
    issues_df = pd.DataFrame(issues)

    if not issues_df.empty:
        issues_df.to_csv(ISSUES_REPORT, index=False)
        print(f"\nFound {len(issues_df):,} rows with issues")
        print(f"Issues report saved → {ISSUES_REPORT}")
        print("\nSample problematic rows:")
        print(issues_df.head(10).to_string(index=False))
        print()
    else:
        print("No data quality issues found!\n")

    # ───── Create cleaned version ─────
    clean_df = df.copy()

    # Critical errors → remove these rows
    invalid_mask = (
        clean_df['name'].isna() |
        clean_df['name'].astype(str).str.strip().eq('') |
        ~clean_df['email'].apply(is_valid_email)
    )

    clean_df = clean_df[~invalid_mask].copy()

    # Clean remaining data
    clean_df['name'] = clean_df['name'].astype(str).str.strip()
    clean_df['city'] = clean_df['city'].fillna('').astype(str).str.strip()

    # Optional: truncate to model max_length
    clean_df['name'] = clean_df['name'].str[:100]
    clean_df['city'] = clean_df['city'].str[:100]

    clean_df.to_csv(CLEANED_OUTPUT, index=False)
    print(f"Cleaned data saved → {CLEANED_OUTPUT}")
    print(f"Original rows : {len(df):,}")
    print(f"Cleaned rows  : {len(clean_df):,}")
    print(f"Removed       : {len(df) - len(clean_df):,} rows")


if __name__ == "__main__":
    validate_and_clean_vendors()