#!/usr/bin/env python3
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
YAML_PATH = ROOT / "test_list.yaml"
JSON_PATH = ROOT / "result_test_auto.json"


def tc_id_from_numero(numero: int) -> str:
    return f"TC{numero:03d}"


def parse_test_list_yaml(path: Path) -> list[dict]:
    """
    Parse minimaliste pour TON YAML (structure simple).
    On évite une dépendance PyYAML.
    Attend un format:
    tests:
      - numero: 1
        type: auto-unittest
      - numero: 2
        type: manuel
    """
    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable: {path}")

    lines = [ln.rstrip() for ln in path.read_text(encoding="utf-8").splitlines()]
    tests = []
    current = None

    for ln in lines:
        s = ln.strip()
        if not s or s.startswith("#"):
            continue

        if s.startswith("- "):
            # ex: "- numero: 1"
            if current:
                tests.append(current)
            current = {}

            after = s[2:].strip()
            if after.startswith("numero:"):
                val = after.split(":", 1)[1].strip()
                current["numero"] = int(val)
        elif s.startswith("numero:") and current is not None:
            current["numero"] = int(s.split(":", 1)[1].strip())
        elif s.startswith("type:") and current is not None:
            current["type"] = s.split(":", 1)[1].strip()

    if current:
        tests.append(current)

    # validation légère
    for t in tests:
        if "numero" not in t or "type" not in t:
            raise ValueError(f"Entrée YAML incomplète: {t}")

    return tests


def load_results_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_status_index(payload: dict) -> dict[str, str]:
    """
    Retourne un mapping: { "TC001": "OK"/"FAIL"/"ERROR"/"SKIPPED" }
    Supporte plusieurs formats possibles.
    """
    idx: dict[str, str] = {}

    tests = payload.get("tests", [])

    # Format A : tests contient tous les tests avec status + test_case_id
    # ex: {"status": "OK", "test_case_id": "TC001", ...}
    for item in tests:
        tc = item.get("test_case_id")
        st = item.get("status")
        if tc and st:
            idx[tc] = st

    # Format B : si tests ne contient que FAIL/ERROR/SKIPPED, idx aura seulement ceux-là.
    # "OK" ne sera pas déductible sans autre info.
    return idx


def normalize_type(t: str) -> str:
    # on affiche "auto" ou "manual" comme dans l'exemple
    return "auto" if t == "auto-unittest" else "manual"


def render_line(tc: str, test_type: str, status: str | None) -> str:
    t = normalize_type(test_type)

    if t == "manual":
        return f"{tc} | {t:<6} | 🟦 Manual test needed"

    # auto
    if status == "OK":
        return f"{tc} | {t:<6} | ✅ Passed"
    if status in ("FAIL", "ERROR"):
        return f"{tc} | {t:<6} | ❌ Failed"
    if status == "SKIPPED":
        return f"{tc} | {t:<6} | 🟠 Skipped"
    return f"{tc} | {t:<6} | 🟡 Not found"


def main():
    # 1) Lire YAML
    tests = parse_test_list_yaml(YAML_PATH)

    # 2) Lire JSON (si existe)
    print("Lecture des tests auto via result_test_auto.json…")
    payload = load_results_json(JSON_PATH)
    print("OK" if payload else "Fichier absent (les autos seront Not found)")

    status_idx = build_status_index(payload)

    # 3) Afficher rapport
    for t in tests:
        tc = tc_id_from_numero(int(t["numero"]))
        test_type = str(t["type"]).strip()

        # Si test manuel => pas besoin de JSON
        if test_type == "manuel":
            print(render_line(tc, "manuel", None))
            continue

        # auto-unittest => regarder dans JSON
        status = status_idx.get(tc)
        print(render_line(tc, "auto-unittest", status))


if __name__ == "__main__":
    main()