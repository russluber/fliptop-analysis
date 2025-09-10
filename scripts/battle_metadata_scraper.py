# pip install requests beautifulsoup4 python-dateutil
import time
import os
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin

DEFAULT_BASE = "https://www.fliptop.com.ph"
DEFAULT_HEADERS = {"User-Agent": "fliptop-eda/0.2 (educational, contact: you@example.com)"}
_VS = re.compile(r"\s+vs\s+", re.I)

# ---- utils ----
def _canon(name: str, rename_map: dict | None):
    if not isinstance(name, str):
        return ""
    s = name.strip()
    if not rename_map:
        return s
    lm = {k.lower(): v for k, v in rename_map.items()}
    return lm.get(s.lower(), s)

def _get_soup(
    url: str,
    session: requests.Session,
    *,
    headers: dict | None = None,
    retries: int = 2,
    sleep: float = 0.7,
) -> BeautifulSoup:
    """GET → BeautifulSoup with simple retries. Headers are configurable."""
    hdrs = headers or DEFAULT_HEADERS
    for i in range(retries + 1):
        r = session.get(url, headers=hdrs, timeout=30)
        if r.ok:
            return BeautifulSoup(r.text, "html.parser")
        time.sleep(sleep * (i + 1))
    r.raise_for_status()  # if we got here, it failed

# ---- year page: collect event links ----
def event_links_for_year(
    year: int,
    session: requests.Session,
    *,
    base: str = DEFAULT_BASE,
    headers: dict | None = None,
) -> list[tuple[str, str]]:
    """
    Return list of (event_name, event_url) from {base}/videos/battle?year=YYYY.
    Event names come from the ft-article card titles; URLs from the wrapping <a>.
    """
    list_url = f"{base}/videos/battle?year={year}"
    soup = _get_soup(list_url, session, headers=headers)
    events: list[tuple[str, str]] = []

    for a in soup.select('a[href^="/videos/battle/"]'):
        title_el = a.select_one(".ft-article h4")
        if not title_el:
            continue
        event_name = title_el.get_text(strip=True)
        href = a.get("href", "")
        # only keep single-slug battle pages (avoid nested sections)
        if re.fullmatch(r"/videos/battle/[^/]+", href):
            events.append((event_name, urljoin(base, href)))

    # de-dupe preserving order
    seen, out = set(), []
    for name, link in events:
        if link not in seen:
            seen.add(link); out.append((name, link))
    return out

# ---- event page: description & matchups ----
def parse_event_live(
    event_url: str,
    session: requests.Session,
    *,
    rename_map: dict | None = None,
    headers: dict | None = None,
) -> list[dict]:
    """
    Return rows: {'matchup','event_name','event_description'} for a single event page.
    - event_description: <div class="col-md-9"><small>…</small></div>
    - matchups: all <h4> inside the FIRST <div class="row my-4"> block only
    """
    soup = _get_soup(event_url, session, headers=headers)

    # Event name from the page header (fallback to slug)
    name_el = soup.select_one("h2.display-7, h2.display-7.fw-bold")
    event_name = (
        name_el.get_text(strip=True)
        if name_el
        else event_url.rstrip("/").split("/")[-1].replace("-", " ").title()
    )

    # Description
    desc_el = soup.select_one("div.col-md-9 small")
    event_description = desc_el.get_text(" ", strip=True) if desc_el else ""

    # Matchups (first row.my-4 only)
    top_row = soup.select_one("div.container-xxl > div.row.my-4") or soup.select_one("div.row.my-4")
    rows = []
    if top_row:
        for h4 in top_row.select("h4"):
            txt = h4.get_text(" ", strip=True)
            if _VS.search(txt) and 3 <= len(txt) <= 100:
                left_right = _VS.split(txt, maxsplit=1)
                if len(left_right) == 2:
                    em1 = _canon(left_right[0], rename_map)
                    em2 = _canon(left_right[1], rename_map)
                    # trim common postfixes on the right
                    em2 = re.split(r"\s*[@|(*]", em2)[0].strip()
                    em2 = re.sub(r"\s+\d+$", "", em2).strip()
                    rows.append({
                        "matchup": f"{em1} vs {em2}",
                        "event_name": event_name,
                        "event_description": event_description,
                    })
    return rows

# ---- public helpers ----
def scrape_year(
    year: int,
    *,
    rename_map: dict | None = None,
    sleep: float = 0.6,
    base: str = DEFAULT_BASE,
    headers: dict | None = DEFAULT_HEADERS,
) -> pd.DataFrame:
    """
    Scrape a single year → DataFrame with columns: matchup, event_name, event_description.
    Returns an empty DataFrame with the same schema if nothing is found.
    """
    session = requests.Session()
    out_rows: list[dict] = []
    for _, event_url in event_links_for_year(year, session, base=base, headers=headers):
        try:
            out_rows.extend(
                parse_event_live(event_url, session, rename_map=rename_map, headers=headers)
            )
        except Exception as e:
            print(f"[warn] {year} {event_url} -> {e}")
        time.sleep(sleep)  # be polite between event pages
    return pd.DataFrame(out_rows, columns=["matchup", "event_name", "event_description"])

def scrape_years(
    year_start: int,
    year_end_inclusive: int,
    *,
    rename_map: dict | None = None,
    base: str = DEFAULT_BASE,
    headers: dict | None = DEFAULT_HEADERS,
) -> pd.DataFrame:
    """Scrape a range of years and return one concatenated DataFrame (schema guaranteed)."""
    frames: list[pd.DataFrame] = []
    for y in range(year_start, year_end_inclusive + 1):
        print(f"Scraping {y}…")
        frames.append(scrape_year(y, rename_map=rename_map, base=base, headers=headers))
    return (
        pd.concat(frames, ignore_index=True)
        if frames else pd.DataFrame(columns=["matchup", "event_name", "event_description"])
    )

def write_events_to_csv(df: pd.DataFrame, output_path: str) -> None:
    """
    Write the scraped events DataFrame to CSV.
    Ensures the directory exists and uses UTF-8 encoding.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    # (optional) guarantee column order if present
    cols = ["matchup", "event_name", "event_description"]
    df = df.reindex(columns=[c for c in cols if c in df.columns] + [c for c in df.columns if c not in cols])
    df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"Wrote {len(df)} rows to {output_path}")