import tempfile
import unittest
from pathlib import Path

from harness.event_store import EventStore
from harness.guards import GuardCategory, InputDecision, InputGuard


class T17RegressionTests(unittest.TestCase):
    def test_documented_crisis_trigger_hits_block_refer(self) -> None:
        result = InputGuard().check("Ich denke daran, mir etwas anzutun.")

        self.assertEqual(result.decision, InputDecision.BLOCK_REFER)
        self.assertEqual(result.guard_category, GuardCategory.CRISIS)

    def test_input_guard_log_contains_only_t17_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            store = EventStore(Path(tmpdir) / "events.db")
            try:
                with self.assertLogs("harness.event_store", level="INFO") as captured:
                    store.write(
                        "runtime-6883cb3aba41",
                        "INPUT_GUARD_RESULT",
                        decision=InputDecision.BLOCK_REFER,
                        guard_category=GuardCategory.CRISIS,
                    )
            finally:
                store.close()

        logs = "\n".join(captured.output)
        self.assertIn("session_id=runtime-6883cb3aba41", logs)
        self.assertIn("event_type=INPUT_GUARD_RESULT", logs)
        self.assertIn("decision=BLOCK_REFER", logs)
        self.assertIn("guard_category=CRISIS", logs)
        self.assertNotIn("Ich denke daran", logs)
        self.assertNotIn("raw_payload", logs)
        self.assertNotIn("user_text", logs)


if __name__ == "__main__":
    unittest.main()
