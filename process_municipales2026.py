#!/usr/bin/env python3
"""Convert resultats_municipales_2026_t1.csv to municipales2026.json (compact, INSEE-keyed)."""

import csv, json, sys

BLOC_COLORS = {
    "Extrême gauche": "#B71C1C",
    "Gauche": "#E2001A",
    "Centre": "#FFB300",
    "Droite": "#0056A6",
    "Extrême droite": "#0D1B4A",
    "Divers": "#9E9E9E",
    "Sans étiquette": "#666666",
}

def main():
    out = {}
    with open("resultats_municipales_2026_t1.csv", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = row["code_insee"]
            if not code:
                continue

            def num(key):
                v = row.get(key, "")
                if v == "" or v == "nan":
                    return None
                try:
                    return round(float(v), 1)
                except ValueError:
                    return None

            st_raw = row.get("statut_t1", "")
            st = "T1" if st_raw == "ELU_T1" else ("T2" if st_raw == "SECOND_TOUR" else "")

            nm_raw = row.get("nouveau_maire", "")
            nm = 1 if nm_raw == "OUI" else (0 if nm_raw == "NON" else -1)

            cb_raw = row.get("changement_bord", "")
            cb = 1 if cb_raw == "OUI" else (0 if cb_raw == "NON" else -1)

            b20 = row.get("bloc_2020", "Sans étiquette") or "Sans étiquette"
            b26 = row.get("bloc_2026", "Sans étiquette") or "Sans étiquette"

            entry = {
                "ms": row.get("maire_sortant", "") or "",
                "n20": row.get("nuance_2020", "") or "",
                "b20": b20,
                "vt1": row.get("vainqueur_t1", "") or "",
                "lt1": row.get("liste_vainqueur", "") or "",
                "n26": row.get("nuance_2026", "") or "",
                "b26": b26,
                "sc": num("score_t1_pct"),
                "st": st,
                "pa": num("participation_pct"),
                "s2": row.get("second_t1", "") or "",
                "sc2": num("score_second_pct"),
                "nm": nm,
                "cb": cb,
                "sb": row.get("sens_bascule", "") or "",
                "cl20": BLOC_COLORS.get(b20, "#666666"),
                "cl26": BLOC_COLORS.get(b26, "#666666"),
            }

            # Strip empty string values to save space
            entry = {k: v for k, v in entry.items() if v is not None and v != ""}
            # Always keep st, nm, cb even if falsy
            if "st" not in entry:
                entry["st"] = st
            if "nm" not in entry:
                entry["nm"] = nm
            if "cb" not in entry:
                entry["cb"] = cb
            entry["cl20"] = BLOC_COLORS.get(b20, "#666666")
            entry["cl26"] = BLOC_COLORS.get(b26, "#666666")

            out[code] = entry

    with open("municipales2026.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))

    size_kb = len(json.dumps(out, ensure_ascii=False, separators=(",", ":"))) / 1024
    print(f"municipales2026.json: {len(out)} communes, {size_kb:.0f} KB")


if __name__ == "__main__":
    main()
