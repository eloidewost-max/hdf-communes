#!/usr/bin/env python3
"""
Download and process enrichment datasets for commune-level financial and social data.
Produces enrichment.json indexed by INSEE code.

Data sources:
- QPV (Quartiers Prioritaires de la Politique de la Ville) 2024 (data.gouv.fr, CSV)
- Comptes individuels des communes 2022 (DGFiP, JSON)
- Revenus Filosofi 2013 (data.gouv.fr, XLSX) -- optional, may fail
"""
import json
import math
import os
import sys
import tempfile
import urllib.request

# ---------------------------------------------------------------------------
# URLs
# ---------------------------------------------------------------------------

QPV_URL = "https://static.data.gouv.fr/resources/quartiers-prioritaires-de-la-politique-de-la-ville-qpv/20260116-110350/listeqp2024-cog2024.csv"

COMPTES_URL = "https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/comptes-individuels-des-communes-fichier-global-2022/exports/json"

REVENUS_URL = "https://static.data.gouv.fr/resources/revenus-des-francais-a-la-commune/20171102-114238/Niveau_de_vie_2013_a_la_commune-Global_Map_Solution.xlsx"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def safe_float(val):
    """Convert value to float, return None on failure or NaN."""
    try:
        if val is None:
            return None
        v = float(val)
        if math.isnan(v) or math.isinf(v):
            return None
        return v
    except (ValueError, TypeError):
        return None


def safe_int(val):
    """Convert value to int, return None on failure."""
    try:
        if val is None:
            return None
        if isinstance(val, float) and math.isnan(val):
            return None
        return int(val)
    except (ValueError, TypeError):
        return None


def build_insee_from_dep_icom(dep, icom):
    """Build 5-digit INSEE code from DGFiP dep (3-char) and icom (3-char).

    For numeric departments: strip leading zero from dep then concat with icom.
      "050" + "082" -> "50" + "082" -> "50082"
      "001" + "053" -> "1" + "053" -> "01053" (zero-padded to 5)
    For Corsica: keep dep as-is.
      "02A" + "082" -> "2A" + "082" -> "2A082"
    """
    dep = str(dep).strip()
    icom = str(icom).strip()

    # Strip leading zero from numeric 3-digit departments
    if len(dep) == 3 and dep.isdigit():
        dep = dep.lstrip("0") or "0"

    code = dep + icom
    # Zero-pad to 5 digits for numeric codes
    if code.isdigit():
        code = code.zfill(5)

    return code


# ---------------------------------------------------------------------------
# Source 1: QPV
# ---------------------------------------------------------------------------

def parse_qpv():
    """Download and parse QPV CSV.

    Returns dict {insee_code: count_of_qpv}.
    """
    print("Downloading QPV data...", file=sys.stderr)
    try:
        with urllib.request.urlopen(QPV_URL, timeout=60) as resp:
            text = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  WARNING: Could not download QPV data: {e}", file=sys.stderr)
        return {}

    import csv
    reader = csv.DictReader(text.splitlines(), delimiter=";")

    counts = {}
    rows_read = 0
    for row in reader:
        rows_read += 1
        raw_code = row.get("insee_com", "").strip()
        if not raw_code:
            continue
        # Zero-pad to 5 digits (some are just numbers like "1053")
        if raw_code.isdigit():
            raw_code = raw_code.zfill(5)
        counts[raw_code] = counts.get(raw_code, 0) + 1

    print(f"  QPV: {rows_read} rows read, {len(counts)} communes with QPV data", file=sys.stderr)
    total_qpv = sum(counts.values())
    print(f"  QPV: {total_qpv} total QPV entries", file=sys.stderr)
    return counts


# ---------------------------------------------------------------------------
# Source 2: Comptes individuels des communes (DGFiP)
# ---------------------------------------------------------------------------

def parse_comptes():
    """Download and parse DGFiP commune accounts JSON.

    Returns dict {insee_code: {dgf_hab, dgf, dette_hab, cafn_hab, perso_hab,
                                prod_hab, equip_hab, pop}}.
    """
    print("Downloading DGFiP comptes individuels 2022 (may take a few minutes)...", file=sys.stderr)
    try:
        req = urllib.request.Request(COMPTES_URL)
        req.add_header("User-Agent", "Mozilla/5.0 (carte-politique research bot)")
        with urllib.request.urlopen(req, timeout=300) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  WARNING: Could not download DGFiP data: {e}", file=sys.stderr)
        return {}

    print("  Parsing JSON...", file=sys.stderr)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"  WARNING: Invalid JSON from DGFiP: {e}", file=sys.stderr)
        return {}

    result = {}
    parsed = 0
    skipped = 0

    for entry in data:
        dep = entry.get("dep", "")
        icom = entry.get("icom", "")
        if not dep or not icom:
            skipped += 1
            continue

        code = build_insee_from_dep_icom(dep, icom)
        rec = {}

        # DGF per inhabitant
        v = safe_float(entry.get("fdgf"))
        if v is not None:
            rec["dgf_hab"] = round(v, 1)

        # Dette per inhabitant
        v = safe_float(entry.get("fdette"))
        if v is not None:
            rec["dette_hab"] = round(v, 1)

        # CAF nette per inhabitant
        v = safe_float(entry.get("fcafn"))
        if v is not None:
            rec["cafn_hab"] = round(v, 1)

        # Personnel charges per inhabitant
        v = safe_float(entry.get("fperso"))
        if v is not None:
            rec["perso_hab"] = round(v, 1)

        if rec:
            result[code] = rec
            parsed += 1

    print(f"  Comptes: {parsed} communes parsed, {skipped} skipped", file=sys.stderr)
    return result


# ---------------------------------------------------------------------------
# Source 3: Revenus Filosofi 2013 (optional)
# ---------------------------------------------------------------------------

def parse_revenus():
    """Download and parse Filosofi 2013 XLSX.

    Returns dict {insee_code: {rev_med, tx_pauv}}.
    May fail gracefully if file is unavailable or unparseable.
    """
    print("Downloading Revenus Filosofi 2013 XLSX (optional)...", file=sys.stderr)
    tmp_path = None
    try:
        import pandas as pd

        tmp = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
        tmp_path = tmp.name
        tmp.close()
        urllib.request.urlretrieve(REVENUS_URL, tmp_path)

        df = pd.read_excel(tmp_path, engine="openpyxl")
        print(f"  Revenus: {len(df)} rows, columns: {list(df.columns)}", file=sys.stderr)

        # Find commune code column
        code_col = None
        for candidate in ["CODGEO", "codgeo", "code_commune", "COM", "Code commune",
                          "Code_commune", "Code Commune", "INSEE", "insee",
                          "code_insee", "Code INSEE"]:
            if candidate in df.columns:
                code_col = candidate
                break
        if code_col is None:
            # Try partial match
            for col in df.columns:
                col_str = str(col).lower()
                if "code" in col_str and ("com" in col_str or "insee" in col_str or "geo" in col_str):
                    code_col = col
                    break

        if code_col is None:
            print(f"  WARNING: Could not find commune code column in revenus data", file=sys.stderr)
            print(f"  Available columns: {list(df.columns)}", file=sys.stderr)
            return {}

        # Find median income column
        rev_col = None
        for candidate in ["Q213", "q213", "MED13", "med13", "Mediane", "mediane",
                          "revenu_median", "Revenu median", "NBMENFISC13",
                          "Niveau de vie Commune"]:
            if candidate in df.columns:
                rev_col = candidate
                break
        if rev_col is None:
            for col in df.columns:
                col_str = str(col).lower()
                if "med" in col_str or "revm" in col_str or "q2" in col_str or "niveau" in col_str:
                    rev_col = col
                    break

        # Find poverty rate column
        pauv_col = None
        for candidate in ["TP6013", "tp6013", "tx_pauvrete", "Taux de pauvrete",
                          "taux_pauvrete", "PAUV", "Taux pauvrete"]:
            if candidate in df.columns:
                pauv_col = candidate
                break
        if pauv_col is None:
            for col in df.columns:
                col_str = str(col).lower()
                if "pauv" in col_str or "poverty" in col_str:
                    pauv_col = col
                    break

        print(f"  Using columns: code={code_col}, revenu={rev_col}, pauvrete={pauv_col}", file=sys.stderr)

        if rev_col is None and pauv_col is None:
            print(f"  WARNING: No income or poverty columns found", file=sys.stderr)
            return {}

        result = {}
        for _, row in df.iterrows():
            code = str(row[code_col]).strip()
            if not code or code == "nan":
                continue
            if code.isdigit():
                code = code.zfill(5)

            rec = {}
            if rev_col is not None:
                v = safe_float(row[rev_col])
                if v is not None:
                    rec["rev_med"] = round(v)
            if pauv_col is not None:
                v = safe_float(row[pauv_col])
                if v is not None:
                    rec["tx_pauv"] = round(v, 1)

            if rec:
                result[code] = rec

        print(f"  Revenus: {len(result)} communes with data", file=sys.stderr)
        return result

    except Exception as e:
        print(f"  WARNING: Could not process revenus data: {e}", file=sys.stderr)
        return {}
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def main():
    base_dir = os.path.dirname(__file__) or "."
    output_path = os.path.join(base_dir, "enrichment.json")

    # --- Source 1: QPV ---
    qpv_counts = parse_qpv()

    # --- Source 2: DGFiP comptes ---
    comptes = parse_comptes()

    # --- Source 3: Revenus Filosofi (optional) ---
    revenus = parse_revenus()

    # --- Merge all sources ---
    print("\nMerging data sources...", file=sys.stderr)
    all_codes = set()
    all_codes |= set(qpv_counts.keys())
    all_codes |= set(comptes.keys())
    all_codes |= set(revenus.keys())

    result = {}
    for code in sorted(all_codes):
        entry = {}

        # QPV count
        if code in qpv_counts:
            entry["qpv"] = qpv_counts[code]

        # DGFiP financial data
        if code in comptes:
            entry.update(comptes[code])

        # Revenus data
        if code in revenus:
            entry.update(revenus[code])

        if entry:
            result[code] = entry

    # Write output
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, separators=(",", ":"))

    size_kb = os.path.getsize(output_path) / 1024
    print(f"\nOutput: {output_path} ({size_kb:.0f} KB)", file=sys.stderr)
    print(f"  {len(result)} communes total", file=sys.stderr)
    for key in ["qpv", "dgf_hab", "dette_hab", "cafn_hab", "perso_hab",
                "rev_med", "tx_pauv"]:
        count = sum(1 for v in result.values() if key in v)
        print(f"  {key}: {count} communes", file=sys.stderr)

    # Sample: Paris
    if "75056" in result:
        print(f"\n  Sample (Paris 75056): {json.dumps(result['75056'], indent=2)}", file=sys.stderr)


if __name__ == "__main__":
    main()
