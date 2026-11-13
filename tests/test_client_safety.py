"""Offline tests for the parts of the clients that protect paid work: state and ledger
writes under parallel runs, downloads, polling, and the spend policy.

No network: API calls and requests.get are replaced with fakes; state, ledger and output
paths point into tmp_path.
"""
import csv
import datetime as dt
import json
import pathlib
import subprocess
import sys

import pytest
import requests

PIPELINE = pathlib.Path(__file__).resolve().parent.parent / "pipeline"
sys.path.insert(0, str(PIPELINE))
import runway  # noqa: E402
import seedance  # noqa: E402

TID = "cgt-test-0001"


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    """Point every file the client writes at tmp_path and make retries instant."""
    out = tmp_path / "output"
    out.mkdir()
    monkeypatch.setattr(seedance, "OUTPUT_DIR", out)
    monkeypatch.setattr(seedance, "LEDGER_FILE", out / "ledger.csv")
    monkeypatch.setattr(seedance, "STATE_FILE", tmp_path / "state.json")
    monkeypatch.setattr(seedance, "LOCK_FILE", tmp_path / "state.lock", raising=False)
    monkeypatch.setattr(seedance, "POLICY_FILE", tmp_path / "no-policy.json", raising=False)
    monkeypatch.setattr(seedance, "RETRY_WAIT", 0, raising=False)
    monkeypatch.setattr(seedance, "load_key", lambda: "test-key")
    return tmp_path


def succeeded(tid=TID):
    return {"id": tid, "status": "succeeded", "model": seedance.MODELS["full"],
            "content": {"video_url": "https://cdn.example/v.mp4", "last_frame_url": "https://cdn.example/l.png"},
            "usage": {"completion_tokens": 108900}}


def fake_download(url, path, **_):
    pathlib.Path(path).write_bytes(b"clip")


def run_generate(argv):
    args = seedance.build_parser().parse_args(["generate", "--prompt", "x"] + argv)
    args.fn(args)


def ledger():
    with open(seedance.LEDGER_FILE, newline="") as f:
        return list(csv.DictReader(f))


# ---- state.json under parallel runs ---------------------------------------------

def test_generate_survives_another_run_overwriting_state(sandbox, monkeypatch):
    """The Nov 7 crash: a parallel run rewrote state.json without this run's entry, and the
    status update after a paid, succeeded task raised KeyError before the download."""
    def retrieve(tid):
        seedance.STATE_FILE.write_text(json.dumps({"other-clip": {"id": "cgt-other"}}))
        return succeeded()
    monkeypatch.setattr(seedance, "api_create", lambda body: TID)
    monkeypatch.setattr(seedance, "api_retrieve", retrieve)
    monkeypatch.setattr(seedance, "download", fake_download)

    run_generate(["--name", "mine"])

    assert (seedance.OUTPUT_DIR / "mine.mp4").exists()
    state = json.loads(seedance.STATE_FILE.read_text())
    assert state["mine"]["id"] == TID and state["mine"]["status"] == "succeeded"
    assert "other-clip" in state


def test_parallel_state_updates_keep_every_entry(sandbox):
    script = (
        "import sys, pathlib, time; sys.path.insert(0, sys.argv[1]); import seedance\n"
        "root = pathlib.Path(sys.argv[2])\n"
        "seedance.STATE_FILE = root / 'state.json'; seedance.LOCK_FILE = root / 'state.lock'\n"
        "real = seedance.load_state\n"
        "def slow():\n"
        "    s = real(); time.sleep(0.05); return s\n"
        "seedance.load_state = slow\n"
        "seedance.update_state('clip-' + sys.argv[3], id='cgt-' + sys.argv[3])\n"
    )
    procs = [subprocess.Popen([sys.executable, "-c", script, str(PIPELINE), str(sandbox), str(i)])
             for i in range(8)]
    assert [p.wait() for p in procs] == [0] * 8
    state = json.loads((sandbox / "state.json").read_text())
    assert sorted(state) == [f"clip-{i}" for i in range(8)]


def test_generate_refuses_a_name_whose_clip_is_already_on_disk(sandbox, monkeypatch):
    """Without this, a lost state.json lets a new paid task reuse the name, and finish()
    then skips the download because the old file is there."""
    (seedance.OUTPUT_DIR / "mine.mp4").write_bytes(b"old")
    monkeypatch.setattr(seedance, "api_create", lambda body: pytest.fail("must not spend"))
    with pytest.raises(SystemExit) as e:
        run_generate(["--name", "mine"])
    assert "already exists" in str(e.value)


# ---- downloads --------------------------------------------------------------------

class FakeResponse:
    def __init__(self, chunks, fail_after=None, status=200):
        self.chunks, self.fail_after, self.status_code = chunks, fail_after, status

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")

    def iter_content(self, _size):
        for i, c in enumerate(self.chunks):
            if self.fail_after is not None and i >= self.fail_after:
                raise requests.ConnectionError("connection dropped")
            yield c


def test_cut_off_download_leaves_no_file_at_the_final_name(sandbox, monkeypatch):
    monkeypatch.setattr(seedance.requests, "get",
                        lambda *a, **k: FakeResponse([b"aaaa", b"bbbb"], fail_after=1))
    target = seedance.OUTPUT_DIR / "clip.mp4"
    with pytest.raises(SystemExit):
        seedance.download("https://cdn.example/v.mp4", target)
    assert not target.exists()
    assert list(seedance.OUTPUT_DIR.glob("clip.mp4*")) == []


def test_download_retries_after_a_dropped_connection(sandbox, monkeypatch):
    responses = [FakeResponse([b"aaaa", b"bbbb"], fail_after=1), FakeResponse([b"aaaa", b"bbbb"])]
    monkeypatch.setattr(seedance.requests, "get", lambda *a, **k: responses.pop(0))
    target = seedance.OUTPUT_DIR / "clip.mp4"
    seedance.download("https://cdn.example/v.mp4", target)
    assert target.read_bytes() == b"aaaabbbb"


def test_finish_fetches_a_missing_last_frame_when_the_video_is_already_there(sandbox, monkeypatch):
    (seedance.OUTPUT_DIR / "mine.mp4").write_bytes(b"clip")
    got = []
    monkeypatch.setattr(seedance, "download", lambda url, path, **_: got.append(pathlib.Path(path).name))
    seedance.finish(succeeded(), "mine")
    assert got == ["mine.last.png"]


# ---- polling ------------------------------------------------------------------------

class FakeJson:
    def __init__(self, status, payload=None):
        self.status_code, self._payload, self.text = status, payload or {}, "body"

    def json(self):
        return self._payload


def test_retrieve_retries_a_transient_server_error(sandbox, monkeypatch):
    responses = [FakeJson(503), FakeJson(200, {"id": TID, "status": "running"})]
    monkeypatch.setattr(seedance.requests, "get", lambda *a, **k: responses.pop(0))
    assert seedance.api_retrieve(TID)["status"] == "running"


def test_retrieve_does_not_retry_a_client_error(sandbox, monkeypatch):
    calls = []
    monkeypatch.setattr(seedance.requests, "get", lambda *a, **k: calls.append(1) or FakeJson(404))
    with pytest.raises(SystemExit):
        seedance.api_retrieve(TID)
    assert len(calls) == 1


def test_wait_keeps_polling_through_a_network_outage(sandbox, monkeypatch):
    answers = [requests.ConnectionError("down")] * 6 + [FakeJson(200, succeeded())]

    def get(*a, **k):
        r = answers.pop(0)
        if isinstance(r, Exception):
            raise r
        return r
    monkeypatch.setattr(seedance.requests, "get", get)
    assert seedance.wait_task(TID, "mine", interval=0, timeout_s=60)["status"] == "succeeded"


def test_create_is_never_retried(sandbox, monkeypatch):
    calls = []

    def post(*a, **k):
        calls.append(1)
        raise requests.ConnectionError("timed out")
    monkeypatch.setattr(seedance.requests, "post", post)
    with pytest.raises(SystemExit) as e:
        seedance.api_create({"model": "m"})
    assert len(calls) == 1
    assert "list" in str(e.value)


# ---- ledger ---------------------------------------------------------------------------

def test_finishing_by_task_id_keeps_the_clip_name_in_the_ledger(sandbox):
    seedance.ledger_upsert(TID, name="mtl-sc01", source="seedance", model=seedance.MODELS["full"],
                           resolution="720p", status="created")
    seedance.ledger_finish(succeeded(), TID)
    assert [r["name"] for r in ledger()] == ["mtl-sc01"]


def test_parallel_ledger_writes_keep_every_row(sandbox):
    script = (
        "import sys, pathlib, time; sys.path.insert(0, sys.argv[1]); import seedance\n"
        "root = pathlib.Path(sys.argv[2])\n"
        "seedance.OUTPUT_DIR = root / 'output'; seedance.LEDGER_FILE = root / 'output' / 'ledger.csv'\n"
        "seedance.LOCK_FILE = root / 'state.lock'\n"
        "real = seedance.ledger_rows\n"
        "def slow():\n"
        "    r = real(); time.sleep(0.05); return r\n"
        "seedance.ledger_rows = slow\n"
        "seedance.ledger_upsert('cgt-' + sys.argv[3], name='clip-' + sys.argv[3], status='created')\n"
    )
    procs = [subprocess.Popen([sys.executable, "-c", script, str(PIPELINE), str(sandbox), str(i)])
             for i in range(8)]
    assert [p.wait() for p in procs] == [0] * 8
    assert sorted(r["name"] for r in ledger()) == [f"clip-{i}" for i in range(8)]


def test_report_names_unpriced_models_instead_of_showing_zero(sandbox, monkeypatch, capsys):
    monkeypatch.setattr(seedance, "PRICING_FILE", sandbox / "pricing.json")
    (sandbox / "pricing.json").write_text("{}")
    seedance.ledger_upsert(TID, name="a", source="seedance", model="some-model", resolution="720p",
                           status="succeeded", completion_tokens=108900)
    seedance.cmd_report(None)
    out = capsys.readouterr().out
    assert "no price" in out
    assert "$   0.00" not in out


def test_every_model_has_a_list_price_at_every_resolution_it_supports():
    missing = [(mk, res, vi) for mk, model in seedance.MODELS.items() for res in sorted(seedance.LIMITS[mk]["res"])
               for vi in (False, True) if seedance.rate_for(model, res, vi) is None]
    assert missing == []


def runway_fake_download(url, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(b"clip")
    return dest


def test_runway_task_lands_in_the_ledger(sandbox, monkeypatch):
    monkeypatch.setattr(runway, "download", runway_fake_download)
    task = {"id": "rw-task-1", "status": "SUCCEEDED", "output": ["https://cdn.example/o.mp4"],
            "cost": {"credits": 140}}
    runway.finish(task, "aleph-plate", sandbox / "runway", model="aleph2")
    row = ledger()[0]
    assert (row["task_id"], row["source"], row["model"], row["status"]) == ("rw-task-1", "runway", "aleph2", "succeeded")
    assert float(row["est_cost_usd"]) == pytest.approx(1.40)
    assert "140 credits" in row["note"]


def test_runway_cut_off_download_leaves_no_file_at_the_final_name(sandbox, monkeypatch):
    monkeypatch.setattr(runway.requests, "get",
                        lambda *a, **k: FakeResponse([b"aaaa", b"bbbb"], fail_after=1))
    target = sandbox / "runway" / "clip.mp4"
    with pytest.raises(SystemExit):
        runway.download("https://cdn.example/o.mp4", target)
    assert list((sandbox / "runway").glob("clip.mp4*")) == []


def test_runway_wait_keeps_polling_through_a_network_outage(sandbox, monkeypatch):
    monkeypatch.setattr(runway, "load_key", lambda: "test-key")
    monkeypatch.setattr(runway, "POLL_S", 0)
    answers = [requests.ConnectionError("down")] * 6 + [FakeJson(200, {"id": "rw-1", "status": "SUCCEEDED"})]

    def request(*a, **k):
        r = answers.pop(0)
        if isinstance(r, Exception):
            raise r
        return r
    monkeypatch.setattr(runway.requests, "request", request)
    assert runway.wait_task("rw-1")["status"] == "SUCCEEDED"


def test_runway_create_is_never_retried(sandbox, monkeypatch):
    monkeypatch.setattr(runway, "load_key", lambda: "test-key")
    calls = []

    def request(*a, **k):
        calls.append(1)
        raise requests.ConnectionError("timed out")
    monkeypatch.setattr(runway.requests, "request", request)
    with pytest.raises(SystemExit):
        runway.api("POST", "/video_to_video", {"model": "aleph2"})
    assert len(calls) == 1


# ---- spend policy -------------------------------------------------------------------------

def write_policy(root, **over):
    policy = {"allowed_models": ["full"],
              "pack": {"model": "full", "tokens": 10_000_000, "expires": "2099-01-01T00:00:00+08:00"}}
    policy.update(over)
    path = root / "spend-policy.json"
    path.write_text(json.dumps(policy))
    return path


def test_policy_blocks_a_model_outside_the_allowed_list(sandbox, monkeypatch):
    monkeypatch.setattr(seedance, "POLICY_FILE", write_policy(sandbox))
    monkeypatch.setattr(seedance, "api_create", lambda body: pytest.fail("must not spend"))
    with pytest.raises(SystemExit) as e:
        run_generate(["--fast", "--name", "draft"])
    assert "spend policy" in str(e.value) and "fast" in str(e.value)


def test_policy_blocks_the_pack_model_after_the_pack_expires(sandbox, monkeypatch):
    expired = {"model": "full", "tokens": 10_000_000, "expires": "2026-11-10T23:59:00+08:00"}
    monkeypatch.setattr(seedance, "POLICY_FILE", write_policy(sandbox, pack=expired))
    monkeypatch.setattr(seedance, "api_create", lambda body: pytest.fail("must not spend"))
    with pytest.raises(SystemExit) as e:
        run_generate(["--name", "clip"])
    assert "expired" in str(e.value)


def test_policy_allows_the_pack_model_while_the_pack_is_valid(sandbox, monkeypatch):
    monkeypatch.setattr(seedance, "POLICY_FILE", write_policy(sandbox))
    now = dt.datetime(2026, 11, 9, tzinfo=dt.timezone.utc)
    assert seedance.policy_violations("full", now=now) == []


def test_pay_as_you_go_flag_overrides_the_policy_for_one_run(sandbox, monkeypatch, capsys):
    monkeypatch.setattr(seedance, "POLICY_FILE", write_policy(sandbox))
    monkeypatch.setattr(seedance, "api_create", lambda body: TID)
    monkeypatch.setattr(seedance, "api_retrieve", lambda tid: succeeded())
    monkeypatch.setattr(seedance, "download", fake_download)
    run_generate(["--fast", "--pay-as-you-go", "--name", "draft"])
    assert (seedance.OUTPUT_DIR / "draft.mp4").exists()
    assert "spend policy" in capsys.readouterr().out


def test_dry_run_reports_the_policy_verdict_without_dying(sandbox, monkeypatch, capsys):
    monkeypatch.setattr(seedance, "POLICY_FILE", write_policy(sandbox))
    run_generate(["--fast", "--dry-run"])
    assert "BLOCKED" in capsys.readouterr().out


def test_repo_policy_file_parses_and_allows_only_the_pack_model():
    policy = json.loads((PIPELINE / "spend-policy.json").read_text())
    assert policy["allowed_models"] == ["full"]
    dt.datetime.fromisoformat(policy["pack"]["expires"])
