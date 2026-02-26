from pathlib import Path

from .engine import EngineCoordinator


def _double(value: int) -> int:
    return value * 2


def run_self_check(output_root: Path, workers: int) -> tuple[bool, list[str]]:
    messages: list[str] = []
    ok = True

    try:
        output_root.mkdir(parents=True, exist_ok=True)
        test_file = output_root / ".self-check-write.tmp"
        test_file.write_text("ok", encoding="utf-8")
        test_file.unlink(missing_ok=True)
        messages.append("Output path write check: OK")
    except Exception as error:
        ok = False
        messages.append(f"Output path write check: FAIL ({error})")

    for mode in ("async", "threading", "parallel"):
        try:
            engine = EngineCoordinator(mode=mode, workers=max(1, min(workers, 2)))
            result = engine.map(_double, [1, 2, 3])
            if result != [2, 4, 6]:
                ok = False
                messages.append(f"Engine {mode}: FAIL (unexpected output)")
            else:
                messages.append(f"Engine {mode}: OK")
        except Exception as error:
            ok = False
            messages.append(f"Engine {mode}: FAIL ({error})")

    return ok, messages
