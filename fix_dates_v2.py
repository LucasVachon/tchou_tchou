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

def generate_random_range(period_name):
    """Generate random 1-6 day range within the given period."""
    if period_name not in PERIODS:
        return None, None
    
    period_start, period_end = PERIODS[period_name]
    duration = (period_end - period_start).days + 1
    
    if duration < 1:
        return None, None
    
    # Random start date within period
    random_offset = random.randint(0, max(0, duration - 1))
    festival_start = period_start + timedelta(days=random_offset)
    
    # Random duration 1-6 days
    days_left = (period_end - festival_start).days + 1
    duration_days = random.randint(1, min(6, days_left))
    festival_end = festival_start + timedelta(days=duration_days - 1)
    
    return festival_start.isoformat(), festival_end.isoformat()

def parse_date_safe(date_str):
    """Try to parse a date, return None if fails."""
    try:
        if pd.isna(date_str) or str(date_str).strip() == "":
            return None
        d = pd.to_datetime(str(date_str).strip()).date()
        return d
    except:
        return None

def should_regenerate(start_date, end_date):
    """Check if dates should be regenerated."""
    if start_date is None or end_date is None:
        return False
    
    try:
        duration = (end_date - start_date).days + 1
        
        # Regenerate if:
        # - duration > 30 days
        # - any date not in 2019
        # - end < start
        if duration > 30 or duration < 0:
            return True
        if start_date.year != 2019 or end_date.year != 2019:
            return True
        return False
    except:
        return True

df = pd.read_csv("data/festivals-global-festivals-pl-avec-dates-FIXED.csv", sep=";", encoding="utf-8-sig")

# Find the date columns
start_col = None
end_col = None
for c in df.columns:
    if "Date de" in c and ("début" in c.lower() or "d" in c[7:10].lower()):
        start_col = c
    if "Date de fin" in c:
        end_col = c

if not (start_col and end_col):
    print("Date columns not found")
    exit(1)

# Find period column
period_col = None
for c in df.columns:
    c_norm = c.lower().replace("é", "e").replace("û", "u")
    if "periode" in c_norm and "deroulement" in c_norm:
        period_col = c
        break

print(f"Columns: start={start_col}, end={end_col}, period={period_col}")

regenerated_count = 0
year_fixed_count = 0

for idx in df.index:
    start_val = df.at[idx, start_col]
    end_val = df.at[idx, end_col]
    
    start_date = parse_date_safe(start_val)
    end_date = parse_date_safe(end_val)
    
    # Check for 2026 or non-2019 and year-fix instead of regenerate
    year_fixed = False
    if start_date and start_date.year != 2019:
        start_date = start_date.replace(year=2019)
        year_fixed = True
    if end_date and end_date.year != 2019:
        end_date = end_date.replace(year=2019)
        year_fixed = True
    
    if year_fixed:
        year_fixed_count += 1
    
    # Now check if should regenerate (>30 days or invalid range)
    if should_regenerate(start_date, end_date):
        period_label = df.at[idx, period_col] if period_col else ""
        period_name = normalize_period(period_label)
        
        if period_name and period_name in PERIODS:
            new_start, new_end = generate_random_range(period_name)
            if new_start and new_end:
                df.at[idx, start_col] = new_start
                df.at[idx, end_col] = new_end
                regenerated_count += 1
    else:
        # Update with year-corrected dates
        if start_date:
            df.at[idx, start_col] = start_date.isoformat()
        if end_date:
            df.at[idx, end_col] = end_date.isoformat()

output_file = "data/festivals-global-festivals-pl-avec-dates-V2.csv"
df.to_csv(output_file, sep=";", index=False, encoding="utf-8-sig")

print(f"\nDates regenerated (>30 days or invalid): {regenerated_count}")
print(f"Years fixed to 2019: {year_fixed_count}")
print(f"Total changes: {regenerated_count + year_fixed_count}")
print(f"Output: {output_file}")
print("Done.")
