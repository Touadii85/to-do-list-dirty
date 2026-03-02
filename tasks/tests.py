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
    Parse minimaliste pour TON YAML (structure simple) sans dépendance PyYAML.
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
    Mapping { "TC001": "OK"/"FAIL"/"ERROR"/"SKIPPED" } à partir du JSON.
    """
    idx: dict[str, str] = {}
    for item in payload.get("tests", []):
        if not isinstance(item, dict):
            continue
        tc = item.get("test_case_id")
        st = item.get("status")
        if tc and st:
            idx[tc] = st
    return idx


def normalize_type(t: str) -> str:
    return "auto" if t == "auto-unittest" else "manual"


def render_line(tc: str, test_type: str, status: str | None) -> tuple[str, str]:
    """
    Retourne (ligne_affichage, categorie)
    categorie ∈ {"passed", "failed", "not_found", "manual"}
    """
    t = normalize_type(test_type)

    if t == "manual":
        return (f"{tc} | {t:<6} | 🟦 Manual test needed", "manual")

    # auto
    if status == "OK":
        return (f"{tc} | {t:<6} | ✅ Passed", "passed")
    if status in ("FAIL", "ERROR"):
        return (f"{tc} | {t:<6} | ❌ Failed", "failed")
    if status == "SKIPPED":
        # On peut le ranger où tu veux ; ici on le compte comme "failed" (pas OK).
        return (f"{tc} | {t:<6} | 🟠 Skipped", "failed")

    return (f"{tc} | {t:<6} | 🟡 Not found", "not_found")


def pct(part: int, total: int) -> float:
    if total == 0:
        return 0.0
    return (part * 100.0) / total


def main():
    tests = parse_test_list_yaml(YAML_PATH)

    print("Lecture des tests auto via result_test_auto.json…")
    payload = load_results_json(JSON_PATH)
    print("OK" if payload else "Fichier absent (les autos seront Not found)")

    status_idx = build_status_index(payload)

    counts = {"passed": 0, "failed": 0, "not_found": 0, "manual": 0}
    total = 0

    # Liste
    for t in tests:
        total += 1
        tc = tc_id_from_numero(int(t["numero"]))
        test_type = str(t["type"]).strip()

        if test_type == "manuel":
            line, cat = render_line(tc, "manuel", None)
        else:
            status = status_idx.get(tc)
            line, cat = render_line(tc, "auto-unittest", status)

        counts[cat] += 1
        print(line)

    # Résumé pourcentages
    print()
    print(f"Number of tests: {total}")

    passed = counts["passed"]
    failed = counts["failed"]
    not_found = counts["not_found"]
    manual = counts["manual"]

    print(f"✅ Passed tests: {passed} ({pct(passed, total):.1f}%)")
    print(f"❌ Failed tests: {failed} ({pct(failed, total):.1f}%)")
    print(f"🟡 Not found tests: {not_found} ({pct(not_found, total):.1f}%)")
    print(f"🟦 Test to pass manually: {manual} ({pct(manual, total):.1f}%)")

    passed_plus_manual = passed + manual
    print(f"✅ Passed + 🟦 Manual: {passed_plus_manual} ({pct(passed_plus_manual, total):.1f}%)")


if __name__ == "__main__":
    main()