import json
import os
import time
from datetime import datetime, timezone

from django.test.runner import DiscoverRunner


class JSONTestResultRunner(DiscoverRunner):
    """
    Test runner Django qui génère un fichier JSON 'result_test_auto.json'
    à la fin de l'exécution des tests.
    """

    output_filename = "result_test_auto.json"

    def run_suite(self, suite, **kwargs):
        start_ts = time.time()
        result = super().run_suite(suite, **kwargs)
        end_ts = time.time()

        # Collecte des infos test par test
        test_results = self._collect_results(result)

        payload = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "duration_seconds": round(end_ts - start_ts, 3),
            "summary": {
                "tests_run": result.testsRun,
                "failures": len(result.failures),
                "errors": len(result.errors),
                "skipped": len(getattr(result, "skipped", [])),
                "expected_failures": len(getattr(result, "expectedFailures", [])),
                "unexpected_successes": len(getattr(result, "unexpectedSuccesses", [])),
                "was_successful": result.wasSuccessful(),
            },
            "tests": test_results,
        }

        out_path = os.path.join(os.getcwd(), self.output_filename)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        return result

    def _collect_results(self, result):
        """
        Transforme failures/errors/skips en liste exploitable.
        Note: unittest ne fournit pas directement la liste complète des tests "OK",
        donc on liste surtout les non-OK + on garde un résumé global.
        """
        items = []

        def test_id(t):
            # ID unittest complet : module.Class.test_xxx
            try:
                return t.id()
            except Exception:
                return str(t)

        def test_case_id(t):
            # Récupère l'attribut test_case_id posé par @tc("TCxxx")
            try:
                method_name = getattr(t, "_testMethodName", None)
                if not method_name:
                    return None
                method = getattr(t, method_name, None)
                return getattr(method, "test_case_id", None)
            except Exception:
                return None

        # Failures
        for t, tb in result.failures:
            items.append(
                {
                    "status": "FAIL",
                    "id": test_id(t),
                    "test_case_id": test_case_id(t),
                    "traceback": tb,
                }
            )

        # Errors
        for t, tb in result.errors:
            items.append(
                {
                    "status": "ERROR",
                    "id": test_id(t),
                    "test_case_id": test_case_id(t),
                    "traceback": tb,
                }
            )

        # Skipped (si présent)
        for t, reason in getattr(result, "skipped", []):
            items.append(
                {
                    "status": "SKIPPED",
                    "id": test_id(t),
                    "test_case_id": test_case_id(t),
                    "reason": reason,
                }
            )

        return items