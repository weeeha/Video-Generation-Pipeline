import copy
import json
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
