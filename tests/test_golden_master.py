import subprocess
import sys
from pathlib import Path

def test_golden_master():
    """Golden Master Test: Compare legacy and refactored outputs."""

    base = Path(__file__).parent.resolve()
    legacy_path = base.parent / "legacy/order_report_legacy.py"
    refactored_path = base.parent / "src/main.py"
    report_file = base.parent / "legacy/expected/report.txt"

    assert legacy_path.exists(), f"Legacy script not found: {legacy_path}"
    assert refactored_path.exists(), f"Refactored script not found: {refactored_path}"
    report_file.parent.mkdir(parents=True, exist_ok=True)

    with report_file.open("w") as f:
        subprocess.run([sys.executable, str(legacy_path)], stdout=f, check=True)
    refactored_result = subprocess.run(
        [sys.executable, str(refactored_path)],
        capture_output=True,
        text=True,
        check=True
    )
    refactored_output = refactored_result.stdout
    generated_output = report_file.read_text()
    assert generated_output == refactored_output, "Golden Master test FAILED"