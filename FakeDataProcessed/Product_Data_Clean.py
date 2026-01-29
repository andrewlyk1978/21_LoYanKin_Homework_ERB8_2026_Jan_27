import pandas as pd
from pathlib import Path

# Configuration - change filenames as needed
INPUT_CSV         = "/home/andrewlo/Documents/MyProject/MyHomeWork/FakeDataProcessed/products_raw.csv"
REPORT_ISSUES_CSV = "/home/andrewlo/Documents/MyProject/MyHomeWork/FakeDataProcessed/products_validation_issues.csv"
CLEANED_CSV       = "/home/andrewlo/Documents/MyProject/MyHomeWork/FakeDataProcessed/products_cleaned.csv"


def validate_and_clean_products():
    print("Product data validation & cleaning")
    print("Rules based on Django Product model:")
    print("• name     : required, non-empty, max 100 chars")
    print("• category : required, non-empty, max 100 chars")
    print("• price    : required, decimal ≥ 0\n")

    # ──────────────── Load data ────────────────
    try:
        df = pd.read_csv(INPUT_CSV)
        print(f"Loaded {len(df):,} rows from {INPUT_CSV}\n")
    except FileNotFoundError:
        print(f"Error: Cannot find file '{INPUT_CSV}'")
        return
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    # Work on a copy
    df = df.copy()

    # ──────────────── Validation flags ────────────────
    issues = []

    for idx, row in df.iterrows():
        problems = []

        # 1. Name checks
        name = str(row.get('name', '')).strip()
        if not name:
            problems.append("empty/missing name")
        elif len(name) > 100:
            problems.append("name too long (>100 chars)")

        # 2. Category checks
        category = str(row.get('category', '')).strip()
        if not category:
            problems.append("empty/missing category")
        elif len(category) > 100:
            problems.append("category too long (>100 chars)")

        # 3. Price checks
        price_raw = row.get('price')
        price_valid = False
        price_value = None

        if pd.isna(price_raw):
            problems.append("missing price")
        else:
            try:
                price_value = float(price_raw)
                if price_value < 0:
                    problems.append("negative price")
                else:
                    price_valid = True
            except (ValueError, TypeError):
                problems.append("invalid price format")

        # Record issue if any
        if problems:
            issues.append({
                'row_number': idx + 2,   # +2 because header + 1-based index
                'name': row.get('name'),
                'category': row.get('category'),
                'price': row.get('price'),
                'issues': '; '.join(problems)
            })

    # ──────────────── Issues report ────────────────
    issues_df = pd.DataFrame(issues)

    if not issues_df.empty:
        issues_df.to_csv(REPORT_ISSUES_CSV, index=False)
        print(f"Found {len(issues_df):,} rows with problems")
        print(f"→ Issues report saved: {REPORT_ISSUES_CSV}")
        print("\nFirst few problematic rows:")
        print(issues_df.head(8).to_string(index=False))
        print()
    else:
        print("No validation issues found!\n")

    # ──────────────── Cleaned dataset ────────────────
    clean_df = df.copy()

    # Remove rows with critical errors
    invalid_mask = (
        clean_df['name'].isna() |
        clean_df['name'].astype(str).str.strip().eq('') |
        clean_df['category'].isna() |
        clean_df['category'].astype(str).str.strip().eq('') |
        # price not valid number or negative
        (~clean_df['price'].apply(lambda x: pd.notna(x) and str(x).replace('.', '', 1).isdigit())) |
        (pd.to_numeric(clean_df['price'], errors='coerce') < 0)
    )

    clean_df = clean_df[~invalid_mask].copy()

    # Final cleaning steps
    clean_df['name']     = clean_df['name'].astype(str).str.strip()
    clean_df['category'] = clean_df['category'].astype(str).str.strip()

    # Convert price to proper float (ready for DecimalField)
    clean_df['price'] = pd.to_numeric(clean_df['price'], errors='coerce')

    # Optional: round to 2 decimal places
    clean_df['price'] = clean_df['price'].round(2)

    clean_df.to_csv(CLEANED_CSV, index=False)
    print(f"Cleaned data saved → {CLEANED_CSV}")
    print(f"Original rows : {len(df):,}")
    print(f"Valid rows    : {len(clean_df):,}")
    print(f"Removed       : {len(df) - len(clean_df):,} rows")


if __name__ == "__main__":
    validate_and_clean_products()