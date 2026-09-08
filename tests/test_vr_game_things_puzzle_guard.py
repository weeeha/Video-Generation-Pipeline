import json
import multiprocessing
import pathlib

import pytest

from pipeline.promos.vr_game_things_puzzle import guard


POLICY = {"max_drafts": 4, "max_finals": 2, "max_usd": 12.0}


def request(**overrides):
    value = {
        "name": "vrgtp-d01-cockpit-approach",
        "stage": "draft",
        "prompt_sha256": "a" * 64,
        "model": "dreamina-seedance-2-0-fast-260128",
        "resolution": "720p",
        "duration": 5,
        "ratio": "16:9",
        "generate_audio": False,
        "watermark": False,
        "estimated_cost_usd": 0.60,
    }
    value.update(overrides)
    return value


def historical(stage, *, name, cost=0.60, fingerprint_suffix="a"):
    value = request(
        name=name,
        stage=stage,
        prompt_sha256=fingerprint_suffix * 64,
        model=(
            "dreamina-seedance-2-0-fast-260128"
            if stage == "draft"
            else "dreamina-seedance-2-0-260128"
        ),
        resolution="720p" if stage == "draft" else "1080p",
        estimated_cost_usd=cost,
    )
    value["event"] = "historical_generation"
    return value


def reserve_in_process(ledger_path, candidate, ready, start, results):
    ready.put(True)
    start.wait()
    try:
        guard.reserve_request(pathlib.Path(ledger_path), candidate)
    except ValueError as error:
        results.put(("blocked", str(error)))
    else:
        results.put(("reserved", candidate["name"]))


def test_rejects_a_fifth_draft():
    four_drafts = [
        historical("draft", name=f"draft-{index}", fingerprint_suffix=str(index))
        for index in range(4)
    ]
    fifth_draft = request(name="draft-5", prompt_sha256="f" * 64)

    assert guard.validate_request(POLICY, four_drafts, fifth_draft) == [
        "draft limit reached: 4/4"
    ]


def test_rejects_a_third_final():
    two_finals = [
        historical("final", name=f"final-{index}", fingerprint_suffix=str(index))
        for index in range(2)
    ]
    third_final = request(
        name="final-3",
        stage="final",
        prompt_sha256="f" * 64,
        model="dreamina-seedance-2-0-260128",
        resolution="1080p",
    )

    assert guard.validate_request(POLICY, two_finals, third_final) == [
        "final limit reached: 2/2"
    ]


def test_rejects_a_duplicate_request_fingerprint():
    duplicate = request()
    existing = [historical("draft", name="already-submitted", fingerprint_suffix="a")]

    assert guard.validate_request(POLICY, existing, duplicate) == [
        "duplicate request fingerprint"
    ]


def test_rejects_a_request_that_exceeds_the_spend_cap():
    spent_11_60 = [
        historical("draft", name="prior-spend", cost=11.60, fingerprint_suffix="b")
    ]
    costs_0_61 = request(name="costs-0-61", prompt_sha256="c" * 64, estimated_cost_usd=0.61)

    assert guard.validate_request(POLICY, spent_11_60, costs_0_61) == [
        "spend cap exceeded: USD 12.21 > USD 12.00"
    ]


def test_requires_an_estimated_cost_for_a_paid_reservation():
    candidate = request()
    del candidate["estimated_cost_usd"]

    assert guard.validate_request(POLICY, [], candidate) == [
        "estimated_cost_usd is required"
    ]


@pytest.mark.parametrize("cost", [0, -0.01, "NaN", "Infinity"])
def test_rejects_non_positive_or_non_finite_estimated_cost(cost):
    candidate = request(estimated_cost_usd=cost)

    assert guard.validate_request(POLICY, [], candidate) == [
        "estimated_cost_usd must be a finite positive number"
    ]


def test_valid_request_is_reserved_once_before_local_runner(tmp_path):
    policy_path = tmp_path / "generation-policy.json"
    ledger_path = tmp_path / "generation-ledger.json"
    policy_path.write_text(json.dumps(POLICY))
    ledger_path.write_text("[]\n")
    candidate = request(prompt_sha256="d" * 64, ledger_path=str(ledger_path))
    observed = []

    def local_runner(argv, check):
        records = json.loads(ledger_path.read_text())
        observed.append((argv, check, records))
        return type("Result", (), {"returncode": 0})()

    assert guard.guarded_generate(candidate, ["local-seedance", "generate"], local_runner) == 0

    assert observed[0][0] == ["local-seedance", "generate"]
    assert observed[0][1] is False
    assert [record["event"] for record in observed[0][2]] == ["reservation"]
    assert observed[0][2][0]["status"] == "reserved"
    saved = json.loads(ledger_path.read_text())
    assert [record["event"] for record in saved] == ["reservation", "delegation"]
    assert saved[1]["status"] == "delegated"


def test_blocked_request_never_calls_the_runner(tmp_path):
    policy_path = tmp_path / "generation-policy.json"
    ledger_path = tmp_path / "generation-ledger.json"
    policy_path.write_text(json.dumps(POLICY))
    ledger_path.write_text(json.dumps([
        historical("draft", name=f"draft-{index}", fingerprint_suffix=str(index))
        for index in range(4)
    ]))
    candidate = request(name="draft-5", prompt_sha256="f" * 64, ledger_path=str(ledger_path))
    calls = []

    def local_runner(argv, check):
        calls.append((argv, check))

    with pytest.raises(ValueError, match="draft limit reached: 4/4"):
        guard.guarded_generate(candidate, ["local-seedance", "generate"], local_runner)

    assert calls == []


def test_competing_reservations_keep_exactly_one_ledger_entry(tmp_path):
    policy_path = tmp_path / "generation-policy.json"
    ledger_path = tmp_path / "generation-ledger.json"
    policy_path.write_text(json.dumps({"max_drafts": 1, "max_finals": 2, "max_usd": 12.0}))
    ledger_path.write_text("[]\n")
    context = multiprocessing.get_context("spawn")
    ready = context.Queue()
    start = context.Event()
    results = context.Queue()
    candidates = [
        request(name=f"draft-{index}", prompt_sha256=str(index) * 64)
        for index in range(2)
    ]
    processes = [
        context.Process(
            target=reserve_in_process,
            args=(str(ledger_path), candidate, ready, start, results),
        )
        for candidate in candidates
    ]
    for process in processes:
        process.start()
    for _ in processes:
        ready.get(timeout=10)
    start.set()
    for process in processes:
        process.join(timeout=10)
        assert process.exitcode == 0

    outcomes = sorted(results.get(timeout=10)[0] for _ in processes)
    assert outcomes == ["blocked", "reserved"]
    ledger = json.loads(ledger_path.read_text())
    assert len(ledger) == 1
    assert ledger[0]["name"] in {candidate["name"] for candidate in candidates}


def test_cli_derives_a_guarded_request_from_the_seedance_arguments():
    candidate, seedance_argv = guard.request_from_seedance_args(
        "final",
        "1.89",
        [
            "generate",
            "--prompt-file",
            "pipeline/prompts/vr-game-things-puzzle/03-three-piece-assembly.md",
            "--pack",
            "vehicles/apache-v1-promo",
            "--model",
            "2.0",
            "--resolution",
            "1080p",
            "--duration",
            "5",
            "--ratio",
            "16:9",
            "--no-audio",
            "--name",
            "vrgtp-f01-assembly",
        ],
    )

    assert seedance_argv[0] == "generate"
    assert candidate == {
        "name": "vrgtp-f01-assembly",
        "stage": "final",
        "prompt_sha256": "25bbea4a11eaa976cb47bd30893a34596aee313c641cebfb43626ddfd5d3ef3f",
        "model": "dreamina-seedance-2-0-260128",
        "resolution": "1080p",
        "duration": 5,
        "ratio": "16:9",
        "generate_audio": False,
        "watermark": False,
        "estimated_cost_usd": "1.89",
    }
