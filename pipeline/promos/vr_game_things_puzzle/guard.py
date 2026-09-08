"""Reservation guard and executable wrapper for VR Game Things Puzzle runs."""
import argparse
import fcntl
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import tempfile
from decimal import Decimal


PROMO_DIR = pathlib.Path(__file__).resolve().parent
REPO = PROMO_DIR.parents[2]
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


def _cost(record: dict) -> Decimal:
    return Decimal(str(record["estimated_cost_usd"]))


def _paid_cost(request: dict) -> tuple[Decimal | None, str | None]:
    if "estimated_cost_usd" not in request:
        return None, "estimated_cost_usd is required"
    try:
        cost = Decimal(str(request["estimated_cost_usd"]))
    except Exception:
        return None, "estimated_cost_usd must be a finite positive number"
    if not cost.is_finite() or cost <= 0:
        return None, "estimated_cost_usd must be a finite positive number"
    return cost, None


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

    cost, cost_error = _paid_cost(request)
    if cost_error:
        errors.append(cost_error)
    else:
        total = sum((_cost(record) for record in submissions), Decimal())
        projected = total + cost
        limit = Decimal(str(policy["max_usd"]))
        if projected > limit:
            errors.append(
                f"spend cap exceeded: USD {projected:.2f} > USD {limit:.2f}"
            )
    return errors


def _read_ledger(ledger_path: pathlib.Path) -> list[dict]:
    if not ledger_path.exists():
        return []
    content = ledger_path.read_text().strip()
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


def _lock_path(ledger_path: pathlib.Path) -> pathlib.Path:
    return ledger_path.with_name(f"{ledger_path.name}.lock")


def _with_ledger_lock(ledger_path: pathlib.Path):
    lock_path = _lock_path(ledger_path)
    lock_path.touch(exist_ok=True)
    return lock_path.open("a+", encoding="utf-8")


def _append_event(ledger_path: pathlib.Path, event: dict) -> None:
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with _with_ledger_lock(ledger_path) as lock_handle:
        fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX)
        try:
            ledger = _read_ledger(ledger_path)
            ledger.append(event)
            _replace_ledger(ledger_path, ledger)
        finally:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)


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
    with _with_ledger_lock(ledger_path) as lock_handle:
        fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX)
        try:
            ledger = _read_ledger(ledger_path)
            errors = validate_request(policy, ledger, request)
            if errors:
                raise ValueError("; ".join(errors))
            record = _reservation(request)
            ledger.append(record)
            _replace_ledger(ledger_path, ledger)
            return record
        finally:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)


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


def request_from_seedance_args(stage: str, estimated_cost_usd: str, seedance_argv: list[str]) -> tuple[dict, list[str]]:
    """Build the reserved fields from the exact general-CLI arguments."""
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    from pipeline import seedance

    args = seedance.build_parser().parse_args(seedance_argv)
    if args.cmd != "generate":
        raise ValueError("guarded CLI only delegates seedance generate")
    if args.dry_run:
        raise ValueError("guarded CLI does not reserve dry-runs")
    if bool(args.prompt) == bool(args.prompt_file):
        raise ValueError("exactly one of --prompt / --prompt-file is required")
    if not args.name:
        raise ValueError("guarded CLI requires a stable --name")
    if args.prompt_file:
        prompt_bytes = pathlib.Path(args.prompt_file).read_bytes()
        prompt = prompt_bytes.decode().strip()
        prompt_sha256 = hashlib.sha256(prompt_bytes).hexdigest()
    else:
        prompt = args.prompt
        prompt_sha256 = hashlib.sha256(prompt.encode()).hexdigest()
    content, _ = seedance.build_content(args, prompt)
    body = seedance.build_body(args, content)
    return {
        "name": args.name,
        "stage": stage,
        "prompt_sha256": prompt_sha256,
        "model": body["model"],
        "resolution": body["resolution"],
        "duration": body["duration"],
        "ratio": body["ratio"],
        "generate_audio": body["generate_audio"],
        "watermark": body["watermark"],
        "estimated_cost_usd": estimated_cost_usd,
    }, seedance_argv


def build_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    generate = commands.add_parser("generate", help="reserve then delegate one paid Seedance generation")
    generate.add_argument("--stage", required=True, choices=("draft", "final"))
    generate.add_argument("--estimated-cost-usd", required=True)
    generate.add_argument("seedance_argv", nargs=argparse.REMAINDER,
                          help="pass the complete seedance generate command after --")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_cli_parser().parse_args(argv)
    request, seedance_argv = request_from_seedance_args(
        args.stage, args.estimated_cost_usd, seedance_argv=args.seedance_argv
    )
    command = [sys.executable, str(REPO / "pipeline/seedance.py"), *seedance_argv]
    return guarded_generate(request, command)


if __name__ == "__main__":
    raise SystemExit(main())
