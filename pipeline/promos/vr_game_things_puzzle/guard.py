"""Offline reservation guard for the VR Game Things Puzzle paid promo runs."""
import fcntl
import hashlib
import json
import os
import pathlib
import subprocess
import tempfile
from decimal import Decimal


PROMO_DIR = pathlib.Path(__file__).resolve().parent
POLICY_PATH = PROMO_DIR / "generation-policy.json"
LEDGER_PATH = PROMO_DIR / "generation-ledger.json"
FINGERPRINT_FIELDS = (
    "stage",
    "prompt_sha256",
    "model",
    "resolution",
    "duration",
    "ratio",
    "generate_audio",
    "watermark",
)
SUBMISSION_EVENTS = {"reservation", "historical_generation"}


def fingerprint_request(request: dict) -> str:
    """Return a stable hash for the generation settings that affect output."""
    canonical = {field: request.get(field) for field in FINGERPRINT_FIELDS}
    encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _is_submission(record: dict) -> bool:
    return record.get("event") in SUBMISSION_EVENTS or "event" not in record


def _cost(record: dict):
    return record.get("estimated_cost_usd", 0)


def validate_request(policy: dict, ledger: list[dict], request: dict) -> list[str]:
    """Return every policy violation without changing the ledger."""
    submissions = [record for record in ledger if _is_submission(record)]
    errors = []
    name = request.get("name")
    if any(record.get("name") == name for record in submissions):
        errors.append(f"duplicate request name: {name}")

    fingerprint = fingerprint_request(request)
    if any(
        record.get("fingerprint", fingerprint_request(record)) == fingerprint
        for record in submissions
    ):
        errors.append("duplicate request fingerprint")

    stage = request.get("stage")
    if stage in ("draft", "final"):
        limit = policy[f"max_{stage}s"]
        count = sum(record.get("stage") == stage for record in submissions)
        if count >= limit:
            errors.append(f"{stage} limit reached: {count}/{limit}")
    else:
        errors.append(f"unsupported stage: {stage}")

    total = sum((Decimal(str(_cost(record))) for record in submissions), Decimal())
    projected = total + Decimal(str(_cost(request)))
    limit = Decimal(str(policy["max_usd"]))
    if projected > limit:
        errors.append(
            f"spend cap exceeded: USD {projected:.2f} > USD {limit:.2f}"
        )
    return errors


def _read_ledger(handle) -> list[dict]:
    handle.seek(0)
    content = handle.read().strip()
    return json.loads(content) if content else []


def _replace_ledger(ledger_path: pathlib.Path, ledger: list[dict]) -> None:
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=ledger_path.parent, delete=False
    ) as temporary:
        json.dump(ledger, temporary, indent=2)
        temporary.write("\n")
        temporary.flush()
        os.fsync(temporary.fileno())
        temporary_path = pathlib.Path(temporary.name)
    os.replace(temporary_path, ledger_path)


def _append_event(ledger_path: pathlib.Path, event: dict) -> None:
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            ledger = _read_ledger(handle)
            ledger.append(event)
            _replace_ledger(ledger_path, ledger)
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _reservation(request: dict) -> dict:
    record = {
        key: value
        for key, value in request.items()
        if key not in {"ledger_path", "policy_path"}
    }
    record.update(
        {
            "event": "reservation",
            "status": "reserved",
            "fingerprint": fingerprint_request(request),
        }
    )
    return record


def reserve_request(ledger_path: pathlib.Path, request: dict) -> dict:
    """Atomically revalidate and append a reserved request before delegation."""
    ledger_path = pathlib.Path(ledger_path)
    policy_path = pathlib.Path(request.get("policy_path", ledger_path.with_name("generation-policy.json")))
    policy = json.loads(policy_path.read_text())
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            ledger = _read_ledger(handle)
            errors = validate_request(policy, ledger, request)
            if errors:
                raise ValueError("; ".join(errors))
            record = _reservation(request)
            ledger.append(record)
            _replace_ledger(ledger_path, ledger)
            return record
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def guarded_generate(request: dict, argv: list[str], runner=subprocess.run) -> int:
    """Reserve a generation, then delegate to the general Seedance CLI."""
    ledger_path = pathlib.Path(request.get("ledger_path", LEDGER_PATH))
    reservation = reserve_request(ledger_path, request)
    transition = {
        "event": "delegation",
        "status": "delegated",
        "name": reservation["name"],
        "fingerprint": reservation["fingerprint"],
    }
    try:
        result = runner(argv, check=False)
    except Exception as error:
        transition["status"] = "failed_to_start"
        transition["error"] = str(error)
        _append_event(ledger_path, transition)
        raise
    transition["returncode"] = result.returncode
    _append_event(ledger_path, transition)
    return result.returncode
