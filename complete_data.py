import argparse
import os
import re
import unicodedata
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime
from typing import Iterable, List, Optional, Tuple
from urllib.parse import urlparse

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

try:
    from duckduckgo_search import DDGS
except Exception:
    DDGS = None


MONTHS = {
    "janvier": 1,
    "fevrier": 2,
    "mars": 3,
    "avril": 4,
    "mai": 5,
    "juin": 6,
    "juillet": 7,
    "aout": 8,
    "septembre": 9,
    "octobre": 10,
    "novembre": 11,
    "decembre": 12,
}

MONTHS_RE = "(?:" + "|".join(MONTHS.keys()) + ")"

TEXT_RANGE_SAME_MONTH_RE = re.compile(
    rf"\b(\d{{1,2}})(?:er)?\s*(?:au|a|\-|–|—|to)\s*(\d{{1,2}})(?:er)?\s+({MONTHS_RE})\s+(20\d{{2}})\b",
    re.IGNORECASE,
)

TEXT_RANGE_TWO_MONTHS_RE = re.compile(
    rf"\b(\d{{1,2}})(?:er)?\s+({MONTHS_RE})\s*(?:au|a|\-|–|—|to)\s*(\d{{1,2}})(?:er)?\s+({MONTHS_RE})\s+(20\d{{2}})\b",
    re.IGNORECASE,
)

TEXT_SINGLE_RE = re.compile(
    rf"\b(\d{{1,2}})(?:er)?\s+({MONTHS_RE})\s+(20\d{{2}})\b",
    re.IGNORECASE,
)

NUM_RANGE_RE = re.compile(
    r"\b(\d{1,2})[/-](\d{1,2})[/-](20\d{2})\s*(?:au|a|\-|–|—|to)\s*(\d{1,2})[/-](\d{1,2})[/-](20\d{2})\b",
    re.IGNORECASE,
)

NUM_SINGLE_RE = re.compile(r"\b(\d{1,2})[/-](\d{1,2})[/-](20\d{2})\b")

ISO_SINGLE_RE = re.compile(r"\b(20\d{2})-(\d{2})-(\d{2})\b")
PERIOD_RANGE_RE = re.compile(r"\((\d{1,2})(?:er)?\s+([a-z]+)\s*-\s*(\d{1,2})(?:er)?\s+([a-z]+)\)")


def normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text.lower())
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")


def find_column_name(df: pd.DataFrame, expected_fragment: str, default_name: str) -> str:
    fragment = normalize_text(expected_fragment)
    for col in df.columns:
        col_norm = normalize_text(str(col))
        if fragment in col_norm:
            return col
    return default_name


def safe_date(year: int, month: int, day: int) -> Optional[date]:
    try:
        return date(year, month, day)
    except ValueError:
        return None


def format_pair(start: date, end: date) -> Tuple[str, str]:
    if end < start:
        start, end = end, start
    return start.isoformat(), end.isoformat()


def is_target_year(candidate_year: int, target_year: int) -> bool:
    return target_year == 0 or candidate_year == target_year


def extract_dates(text: str, target_year: int) -> Tuple[Optional[str], Optional[str]]:
    if not text:
        return None, None

    clean = normalize_text(text)

    for match in TEXT_RANGE_SAME_MONTH_RE.finditer(clean):
        day_start, day_end, month_name, year = match.groups()
        year_int = int(year)
        if not is_target_year(year_int, target_year):
            continue
        month_int = MONTHS[month_name.lower()]
        start = safe_date(year_int, month_int, int(day_start))
        end = safe_date(year_int, month_int, int(day_end))
        if start and end:
            return format_pair(start, end)

    for match in TEXT_RANGE_TWO_MONTHS_RE.finditer(clean):
        day_start, month_start, day_end, month_end, year = match.groups()
        year_int = int(year)
        if not is_target_year(year_int, target_year):
            continue
        start = safe_date(year_int, MONTHS[month_start.lower()], int(day_start))
        end = safe_date(year_int, MONTHS[month_end.lower()], int(day_end))
        if start and end:
            return format_pair(start, end)

    for match in NUM_RANGE_RE.finditer(clean):
        d1, m1, y1, d2, m2, y2 = match.groups()
        y1_int = int(y1)
        y2_int = int(y2)
        if not (is_target_year(y1_int, target_year) and is_target_year(y2_int, target_year)):
            continue
        start = safe_date(y1_int, int(m1), int(d1))
        end = safe_date(y2_int, int(m2), int(d2))
        if start and end:
            return format_pair(start, end)

    singles: List[date] = []

    for match in TEXT_SINGLE_RE.finditer(clean):
        day_str, month_name, year_str = match.groups()
        year_int = int(year_str)
        if not is_target_year(year_int, target_year):
            continue
        parsed = safe_date(year_int, MONTHS[month_name.lower()], int(day_str))
        if parsed:
            singles.append(parsed)

    for match in NUM_SINGLE_RE.finditer(clean):
        day_str, month_str, year_str = match.groups()
        year_int = int(year_str)
        if not is_target_year(year_int, target_year):
            continue
        parsed = safe_date(year_int, int(month_str), int(day_str))
        if parsed:
            singles.append(parsed)

    for match in ISO_SINGLE_RE.finditer(clean):
        year_str, month_str, day_str = match.groups()
        year_int = int(year_str)
        if not is_target_year(year_int, target_year):
            continue
        parsed = safe_date(year_int, int(month_str), int(day_str))
        if parsed:
            singles.append(parsed)

    if singles:
        return format_pair(min(singles), max(singles))

    return None, None


def split_candidate_urls(raw_url: object) -> List[str]:
    if not isinstance(raw_url, str):
        return []

    cleaned = raw_url.strip()
    if not cleaned:
        return []

    parts = re.split(r"\s+//\s+|\s*[,;]\s*|\s+", cleaned)
    candidates = []
    for part in parts:
        candidate = part.strip()
        if not candidate:
            continue
        if not urlparse(candidate).scheme:
            candidate = f"https://{candidate}"
        candidates.append(candidate)
    return candidates


def fetch_url_text(url: str, timeout: int = 12) -> str:
    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=timeout,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    return soup.get_text(" ", strip=True)


def search_urls(festival_name: str, target_year: int, max_results: int = 2) -> List[str]:
    if DDGS is None:
        return []

    query = f"{festival_name} {target_year}" if target_year else f"{festival_name} dates festival"
    urls = []
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            with DDGS() as ddgs:
                results = ddgs.text(query, max_results=max_results)
                for result in results:
                    href = result.get("href")
                    if href:
                        urls.append(href)
    except Exception:
        return []
    return urls


def fallback_dates_from_period(period_label: object, fallback_year: int) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    if not isinstance(period_label, str) or not period_label.strip():
        return None, None, None

    clean = normalize_text(period_label)
    clean = clean.replace("1er", "1")

    range_match = PERIOD_RANGE_RE.search(clean)
    if range_match:
        d1, m1, d2, m2 = range_match.groups()
        if m1 in MONTHS and m2 in MONTHS:
            start = safe_date(fallback_year, MONTHS[m1], int(d1))
            end = safe_date(fallback_year, MONTHS[m2], int(d2))
            if start and end:
                s, e = format_pair(start, end)
                return s, e, "period-fallback"

    if "avant-saison" in clean:
        return (
            date(fallback_year, 1, 1).isoformat(),
            date(fallback_year, 6, 20).isoformat(),
            "period-fallback",
        )
    if "apres-saison" in clean:
        return (
            date(fallback_year, 9, 6).isoformat(),
            date(fallback_year, 12, 31).isoformat(),
            "period-fallback",
        )
    if "saison" in clean:
        return (
            date(fallback_year, 6, 21).isoformat(),
            date(fallback_year, 9, 5).isoformat(),
            "period-fallback",
        )

    return None, None, None


def get_wayback_snapshot_url(original_url: str, year: int) -> Optional[str]:
    if year == 0:
        return None

    cdx_url = "https://web.archive.org/cdx/search/cdx"
    params = {
        "url": original_url,
        "from": str(year),
        "to": str(year),
        "output": "json",
        "fl": "timestamp,original,statuscode",
        "filter": "statuscode:200",
        "limit": "1",
    }

    try:
        response = requests.get(
            cdx_url,
            params=params,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=12,
        )
        response.raise_for_status()
        payload = response.json()

        if not isinstance(payload, list) or len(payload) < 2:
            return None

        first_row = payload[1]
        if len(first_row) < 2:
            return None

        timestamp, archived_original = first_row[0], first_row[1]
        return f"https://web.archive.org/web/{timestamp}id_/{archived_original}"
    except Exception:
        return None


def apply_seed_dates(df: pd.DataFrame, seed_file: str) -> int:
    if not seed_file or not os.path.exists(seed_file):
        return 0

    seed_df = pd.read_csv(seed_file, sep=";", encoding="utf-8-sig")
    required = {"Identifiant", "Date de début", "Date de fin"}
    if not required.issubset(seed_df.columns) or "Identifiant" not in df.columns:
        return 0

    seed_map = (
        seed_df.dropna(subset=["Identifiant"])
        .drop_duplicates(subset=["Identifiant"], keep="first")
        .set_index("Identifiant")[["Date de début", "Date de fin"]]
    )

    updated = 0
    for idx in df.index:
        identifiant = df.at[idx, "Identifiant"]
        if identifiant not in seed_map.index:
            continue

        existing_start = str(df.at[idx, "Date de début"]).strip() if pd.notna(df.at[idx, "Date de début"]) else ""
        existing_end = str(df.at[idx, "Date de fin"]).strip() if pd.notna(df.at[idx, "Date de fin"]) else ""

        if existing_start and existing_end:
            continue

        seeded_start = seed_map.at[identifiant, "Date de début"]
        seeded_end = seed_map.at[identifiant, "Date de fin"]

        if pd.notna(seeded_start) and str(seeded_start).strip() and pd.notna(seeded_end) and str(seeded_end).strip():
            df.at[idx, "Date de début"] = str(seeded_start)
            df.at[idx, "Date de fin"] = str(seeded_end)
            if "Source date" in df.columns:
                df.at[idx, "Source date"] = f"seed:{os.path.basename(seed_file)}"
            updated += 1

    return updated


def find_dates_for_festival(
    festival_name: str,
    website: object,
    target_year: int,
    use_search_fallback: bool,
    use_wayback_fallback: bool,
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    urls_to_try = split_candidate_urls(website)

    if use_search_fallback:
        urls_to_try.extend(search_urls(festival_name, target_year))

    tried = set()
    for url in urls_to_try:
        if url in tried:
            continue
        tried.add(url)

        try:
            text = fetch_url_text(url)
            start, end = extract_dates(text, target_year)
            if start and end:
                return start, end, url
        except Exception:
            continue

        if use_wayback_fallback and target_year != 0:
            archive_url = get_wayback_snapshot_url(url, target_year)
            if not archive_url:
                continue
            try:
                archived_text = fetch_url_text(archive_url)
                start, end = extract_dates(archived_text, target_year)
                if start and end:
                    return start, end, archive_url
            except Exception:
                continue

    return None, None, None


def to_process_indices(df: pd.DataFrame, force: bool) -> Iterable[int]:
    if force:
        return df.index.tolist()
    missing = df["Date de début"].isna() | (df["Date de début"].astype(str).str.strip() == "")
    return df.index[missing].tolist()


def main() -> None:
    parser = argparse.ArgumentParser(description="Complète les dates de festivals dans le CSV")
    parser.add_argument("--input", default="data/festivals-global-festivals-pl.csv")
    parser.add_argument("--output", default="data/festivals-global-festivals-pl-avec-dates.csv")
    parser.add_argument("--year", type=int, default=2019, help="Année cible. 0 = toute année")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--limit", type=int, default=0, help="0 = pas de limite")
    parser.add_argument("--checkpoint", type=int, default=100)
    parser.add_argument("--force", action="store_true", help="Réécrit toutes les lignes")
    parser.add_argument(
        "--period-fallback-year",
        type=int,
        default=0,
        help="Année utilisée pour déduire les dates depuis la colonne Période (0 = année courante)",
    )
    parser.add_argument(
        "--seed-file",
        default="data/festivals-global-festivals-pl-avec-dates-10-premiers.csv",
        help="CSV source pour pré-remplir des dates déjà connues",
    )
    parser.add_argument(
        "--search-fallback",
        action="store_true",
        help="Active DuckDuckGo si la colonne site ne suffit pas",
    )
    parser.add_argument(
        "--period-only",
        action="store_true",
        help="N'utilise pas le web, remplit uniquement via la colonne Période",
    )
    parser.add_argument(
        "--wayback-fallback",
        action="store_true",
        help="Teste des snapshots web archive de l'année cible",
    )
    args = parser.parse_args()

    df = pd.read_csv(args.input, sep=";", encoding="utf-8-sig")

    if "Date de début" not in df.columns:
        df["Date de début"] = None
    if "Date de fin" not in df.columns:
        df["Date de fin"] = None
    if "Source date" not in df.columns:
        df["Source date"] = None

    period_column = find_column_name(
        df,
        expected_fragment="periode principale de deroulement du festival",
        default_name="Période principale de déroulement du festival",
    )

    seeded_count = apply_seed_dates(df, args.seed_file)
    if seeded_count:
        print(f"Dates pré-remplies depuis seed: {seeded_count}")

    indices = list(to_process_indices(df, args.force))
    if args.limit and args.limit > 0:
        indices = indices[: args.limit]

    if not indices:
        print("Aucune ligne à traiter.")
        df.to_csv(args.output, sep=";", index=False, encoding="utf-8-sig")
        return

    print(f"Lignes à traiter: {len(indices)}")
    found_count = 0
    period_count = 0

    fallback_year = args.period_fallback_year if args.period_fallback_year else datetime.now().year

    def worker(idx: int) -> Tuple[int, Optional[str], Optional[str], Optional[str]]:
        row = df.loc[idx]
        period_label = row.get(period_column, "")
        start, end, source = None, None, None

        if not args.period_only:
            festival_name = str(row.get("Nom du festival", ""))
            website = row.get("Site internet du festival", "")
            start, end, source = find_dates_for_festival(
                festival_name=festival_name,
                website=website,
                target_year=args.year,
                use_search_fallback=args.search_fallback,
                use_wayback_fallback=args.wayback_fallback,
            )

        if not (start and end):
            start, end, source = fallback_dates_from_period(period_label, fallback_year)
        return idx, start, end, source

    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = [executor.submit(worker, idx) for idx in indices]

        for processed, future in enumerate(tqdm(as_completed(futures), total=len(futures)), start=1):
            idx, start, end, source = future.result()
            if start and end:
                df.at[idx, "Date de début"] = start
                df.at[idx, "Date de fin"] = end
                df.at[idx, "Source date"] = source
                found_count += 1
                if source == "period-fallback":
                    period_count += 1

            if args.checkpoint > 0 and processed % args.checkpoint == 0:
                df.to_csv(args.output, sep=";", index=False, encoding="utf-8-sig")

    df.to_csv(args.output, sep=";", index=False, encoding="utf-8-sig")
    print(f"Terminé. Dates trouvées: {found_count}/{len(indices)}")
    print(f"Dont fallback période: {period_count}")
    print(f"Fichier de sortie: {args.output}")


if __name__ == "__main__":
    main()