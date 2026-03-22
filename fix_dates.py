import pandas as pd
import random
from datetime import date, timedelta

# Period definitions for 2019
PERIODS = {
    "avant-saison": (date(2019, 1, 1), date(2019, 6, 20)),
    "saison": (date(2019, 6, 21), date(2019, 9, 5)),
    "apres-saison": (date(2019, 9, 6), date(2019, 12, 31)),
}

def normalize_period(text):
    text_low = str(text).lower()
    if "avant" in text_low:
        return "avant-saison"
    if "apres" in text_low or "après" in text_low:
        return "apres-saison"
    if "saison" in text_low:
        return "saison"
    return None

def generate_random_range(period_name, start_date_str, end_date_str):
    """Generate random 1-6 day range within the given period."""
    if period_name not in PERIODS:
        return start_date_str, end_date_str
    
    period_start, period_end = PERIODS[period_name]
    duration = (period_end - period_start).days + 1
    
    if duration < 1:
        return start_date_str, end_date_str
    
    # Random start date within period
    random_offset = random.randint(0, max(0, duration - 1))
    festival_start = period_start + timedelta(days=random_offset)
    
    # Random duration 1-6 days, but don't exceed period end
    days_left = (period_end - festival_start).days + 1
    duration_days = random.randint(1, min(6, days_left))
    festival_end = festival_start + timedelta(days=duration_days - 1)
    
    return festival_start.isoformat(), festival_end.isoformat()

def should_regenerate(start_str, end_str):
    """Check if a date range should be regenerated (>30 days or not in 2019)."""
    try:
        if pd.isna(start_str) or pd.isna(end_str):
            return False
        start_str = str(start_str).strip()
        end_str = str(end_str).strip()
        if not start_str or not end_str:
            return False
        start = pd.to_datetime(start_str).date()
        end = pd.to_datetime(end_str).date()
        duration = (end - start).days + 1
        
        # Regenerate if duration > 30 days or not in 2019
        return duration > 30 or start.year != 2019 or end.year != 2019
    except Exception:
        return False

df = pd.read_csv("data/festivals-global-festivals-pl-avec-dates.csv", sep=";", encoding="utf-8-sig")

# Find the date columns
start_col = None
end_col = None
for c in df.columns:
    if "Date de" in c and ("début" in c.lower() or "début".replace("û", "u") in c.lower() or "debut" in c.lower()):
        start_col = c
    if "Date de fin" in c:
        end_col = c

if not (start_col and end_col):
    print("Date columns not found")
    exit(1)

period_col = None
for c in df.columns:
    c_norm = c.lower().replace("é", "e").replace("û", "u").replace("à", "a")
    if "periode" in c_norm and "deroulement" in c_norm:
        period_col = c
        break

print(f"Using columns: {start_col}, {end_col}, period={period_col}")

updated_count = 0
year_fixed_count = 0

for idx in df.index:
    start_val = df.at[idx, start_col]
    end_val = df.at[idx, end_col]
    
    # First: fix any 2026 dates to 2019
    if pd.notna(start_val):
        start_str = str(start_val).strip()
        if start_str.startswith("2026"):
            start_str = start_str.replace("2026", "2019", 1)
            df.at[idx, start_col] = start_str
            year_fixed_count += 1
    
    if pd.notna(end_val):
        end_str = str(end_val).strip()
        if end_str.startswith("2026"):
            end_str = end_str.replace("2026", "2019", 1)
            df.at[idx, end_col] = end_str
            year_fixed_count += 1
    
    # Second: regenerate if >30 days
    if should_regenerate(start_val, end_val):
        period_label = df.at[idx, period_col] if period_col else ""
        period_name = normalize_period(period_label)
        
        if period_name and period_name in PERIODS:
            new_start, new_end = generate_random_range(period_name, str(start_val), str(end_val))
            df.at[idx, start_col] = new_start
            df.at[idx, end_col] = new_end
            updated_count += 1


output_file = "data/festivals-global-festivals-pl-avec-dates-FIXED.csv"
df.to_csv(output_file, sep=";", index=False, encoding="utf-8-sig")
print(f"Dates regenerated (>30 days): {updated_count}")
print(f"Dates fixed to 2019: {year_fixed_count}")
print(f"Output file: {output_file}")
print("Rename this file to replace the original when ready.")
print(f"Total: {updated_count + year_fixed_count} changes")
print("Done.")
