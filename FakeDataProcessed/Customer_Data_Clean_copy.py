import pandas as pd
import re
from pathlib import Path

# ────────────────────────────────────────────────
# CONFIGURATION
# ────────────────────────────────────────────────
INPUT_FILE       = "customers_input.csv"
ISSUES_REPORT    = "customers_validation_issues.csv"
CLEANED_OUTPUT   = "customers_cleaned.csv"


def is_normal_name(name):
    """
    Returns True if name contains only letters, spaces, hyphens and apostrophes.
    Rejects digits and most symbols.
    """
    if not isinstance(name, str) or not name.strip():
        return False
    # Allow: letters (any language), space, hyphen, apostrophe
    pattern = r'^[\p{L}\s\'-]+$'
    return bool(re.match(pattern, name.strip()))


def is_valid_email(email):
    """Simple but practical email format check"""
    if pd.isna(email) or not isinstance(email, str):
        return False
    email = email.strip()
    if not email:
        return False
    # Basic realistic pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_and_clean_customers():
    print("Customer CSV Data Validation")
    print("Checking for:")
    print("• Empty / missing name")
    print("• Name contains unusual symbols (only letters, space, -, ' allowed)")
    print("• Invalid or missing email")
    print("• Empty city name (reported only)")
    print("• Negative age\n")

    # ───── Load data ─────
    try:
        df = pd.read_csv(INPUT_FILE)
        print(f"Loaded {len(df):,} rows")
    except FileNotFoundError:
        print(f"Error: File '{INPUT_FILE}' not found.")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    df = df.copy()

    # ───── Collect issues ─────
    issues = []

    for idx, row in df.iterrows():
        problems = []

        # 1. Name validation
        name_raw = row.get('name')
        name = str(name_raw).strip() if pd.notna(name_raw) else ""
        if not name:
            problems.append("empty name")
        elif len(name) > 100:
            problems.append("name too long (>100 chars)")
        elif not is_normal_name(name):
            problems.append("name contains unusual symbols")

        # 2. Email validation
        email = row.get('email')
        if not is_valid_email(email):
            problems.append("invalid or missing email")

        # 3. City (report emptiness & length)
        city_raw = row.get('city')
        city = str(city_raw).strip() if pd.notna(city_raw) else ""
        if not city:
            problems.append("empty city (allowed)")
        elif len(city) > 100:
            problems.append("city too long (>100 chars)")

        # 4. Age validation
        age_raw = row.get('age')
        if pd.notna(age_raw):
            try:
                age_num = float(age_raw)
                if age_num < 0:
                    problems.append("negative age")
                if age_num != int(age_num):
                    problems.append("non-integer age")
            except (ValueError, TypeError):
                problems.append("invalid age format")

        if problems:
            issues.append({
                'row': idx + 1,
                'name': row.get('name'),
                'email': row.get('email'),
                'age': row.get('age'),
                'city': row.get('city'),
                'issues': '; '.join(problems)
            })

    # ───── Issues report ─────
    issues_df = pd.DataFrame(issues)

    if not issues_df.empty:
        issues_df.to_csv(ISSUES_REPORT, index=False)
        print(f"\nFound {len(issues_df):,} rows with issues")
        print(f"Issues saved → {ISSUES_REPORT}")
        print("\nSample issues:")
        print(issues_df.head(10).to_string(index=False))
        print()
    else:
        print("No issues detected!\n")

    # ───── Cleaned dataset ─────
    clean_df = df.copy()

    # Remove rows with critical validation failures
    remove_mask = (
        clean_df['name'].isna() |
        clean_df['name'].astype(str).str.strip().eq('') |
        ~clean_df['name'].astype(str).apply(is_normal_name) |
        ~clean_df['email'].apply(is_valid_email)
    )

    clean_df = clean_df[~remove_mask].copy()

    # Final normalization
    clean_df['name'] = clean_df['name'].astype(str).str.strip()
    clean_df['city'] = clean_df['city'].fillna('').astype(str).str.strip()

    # Age: only keep valid non-negative integers or None
    clean_df['age'] = pd.to_numeric(clean_df['age'], errors='coerce')
    clean_df['age'] = clean_df['age'].apply(
        lambda x: int(x) if pd.notna(x) and x >= 0 and x == int(x) else None
    )

    # Enforce field length limits
    clean_df['name'] = clean_df['name'].str[:100]
    clean_df['city'] = clean_df['city'].str[:100]

    clean_df.to_csv(CLEANED_OUTPUT, index=False)
    print(f"Cleaned data saved → {CLEANED_OUTPUT}")
    print(f"Original : {len(df):,} rows")
    print(f"Cleaned  : {len(clean_df):,} rows")
    print(f"Removed  : {len(df) - len(clean_df):,} rows")


if __name__ == "__main__":
    validate_and_clean_customers()