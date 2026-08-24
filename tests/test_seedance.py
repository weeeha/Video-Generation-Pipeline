"""Offline tests for pipeline/seedance.py request building and validation.

No network: everything goes through build_parser() -> build_content()/build_body().
Reference URLs pass through untouched, so most tests need no fixture files.
"""
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "pipeline"))
import seedance  # noqa: E402

IMG = "https://example.com/ref.png"
VID = "https://example.com/ref.mp4"
AUD = "https://example.com/ref.mp3"


def body_for(argv, tmp_path=None):
    args = seedance.build_parser().parse_args(["generate", "--prompt", "x"] + argv)
    content, _ = seedance.build_content(args, "x")
    return seedance.build_body(args, content)


def dies_with(argv, fragment):
    with pytest.raises(SystemExit) as e:
        body_for(argv)
    assert fragment in str(e.value), str(e.value)


# ---- model selection ---------------------------------------------------------

def test_default_model_is_2_5():
    assert body_for([])["model"] == "dreamina-seedance-2-5-260628"

def test_fast_flag_selects_2_0_fast():
    assert body_for(["--fast"])["model"] == "dreamina-seedance-2-0-fast-260128"

def test_model_choice_2_0():
    assert body_for(["--model", "2.0"])["model"] == "dreamina-seedance-2-0-260128"

def test_model_choice_mini():
    assert body_for(["--model", "mini"])["model"] == "dreamina-seedance-2-0-mini-260615"


# ---- duration ----------------------------------------------------------------

def test_duration_30_allowed_on_2_5():
    assert body_for(["--duration", "30"])["duration"] == 30

def test_duration_30_rejected_on_2_0():
    dies_with(["--model", "2.0", "--duration", "30"], "4-15")

def test_duration_auto_maps_to_minus_1():
    assert body_for(["--duration", "auto"])["duration"] == -1

def test_duration_default_is_5():
    assert body_for([])["duration"] == 5


# ---- reference caps ----------------------------------------------------------

def test_ten_reference_images_allowed_on_2_5():
    body = body_for([x for _ in range(10) for x in ("--image", IMG)])
    roles = [i.get("role") for i in body["content"][1:]]
    assert roles.count("reference_image") == 10

def test_ten_reference_images_rejected_on_2_0():
    dies_with(["--model", "2.0"] + [x for _ in range(10) for x in ("--image", IMG)], "9")

def test_audio_only_reference_allowed_on_2_5():
    body = body_for(["--audio", AUD])
    assert body["content"][1]["role"] == "reference_audio"

def test_audio_only_reference_rejected_on_2_0():
    dies_with(["--model", "2.0", "--audio", AUD], "audio")


# ---- omni_reference_task_type ------------------------------------------------

def test_task_type_auto_attached_for_refs_on_2_5():
    assert body_for(["--image", IMG])["omni_reference_task_type"] == "auto"

def test_task_type_absent_without_refs():
    assert "omni_reference_task_type" not in body_for([])

def test_task_type_absent_on_2_0():
    assert "omni_reference_task_type" not in body_for(["--model", "2.0", "--image", IMG])

def test_task_type_flag_rejected_on_2_0():
    dies_with(["--model", "2.0", "--video", VID, "--task-type", "edit"], "2.5")


# ---- edit / extend constraints -----------------------------------------------

def test_edit_forces_adaptive_ratio_and_auto_duration():
    body = body_for(["--task-type", "edit", "--video", VID])
    assert body["omni_reference_task_type"] == "edit"
    assert body["ratio"] == "adaptive"
    assert body["duration"] == -1

def test_edit_requires_a_reference_video():
    dies_with(["--task-type", "edit", "--image", IMG], "video")

def test_edit_rejects_explicit_ratio():
    dies_with(["--task-type", "edit", "--video", VID, "--ratio", "16:9"], "adaptive")

def test_edit_rejects_explicit_duration():
    dies_with(["--task-type", "edit", "--video", VID, "--duration", "8"], "-1")

def test_extend_forces_adaptive_ratio_but_keeps_duration():
    body = body_for(["--task-type", "extend", "--video", VID, "--duration", "11"])
    assert body["omni_reference_task_type"] == "extend"
    assert body["ratio"] == "adaptive"
    assert body["duration"] == 11


# ---- first-frame ratio rule on 2.5 -------------------------------------------

def test_first_frame_on_2_5_forces_adaptive_ratio(tmp_path):
    frame = tmp_path / "frame.png"
    frame.write_bytes(b"png")
    args = seedance.build_parser().parse_args(
        ["generate", "--prompt", "x", "--first-frame", str(frame)])
    content, _ = seedance.build_content(args, "x")
    assert seedance.build_body(args, content)["ratio"] == "adaptive"

def test_first_frame_on_2_5_rejects_explicit_ratio(tmp_path):
    frame = tmp_path / "frame.png"
    frame.write_bytes(b"png")
    args = seedance.build_parser().parse_args(
        ["generate", "--prompt", "x", "--first-frame", str(frame), "--ratio", "16:9"])
    content, _ = seedance.build_content(args, "x")
    with pytest.raises(SystemExit) as e:
        seedance.build_body(args, content)
    assert "adaptive" in str(e.value)

def test_first_frame_on_2_0_keeps_explicit_ratio(tmp_path):
    frame = tmp_path / "frame.png"
    frame.write_bytes(b"png")
    args = seedance.build_parser().parse_args(
        ["generate", "--prompt", "x", "--model", "2.0", "--first-frame", str(frame), "--ratio", "16:9"])
    content, _ = seedance.build_content(args, "x")
    assert seedance.build_body(args, content)["ratio"] == "16:9"


# ---- output format -----------------------------------------------------------

def test_mov_output_format_on_2_5():
    assert body_for(["--format", "mov"])["output_format"] == "mov"

def test_default_has_no_output_format():
    assert "output_format" not in body_for([])

def test_mov_rejected_on_2_0():
    dies_with(["--model", "2.0", "--format", "mov"], "2.5")


# ---- resolution --------------------------------------------------------------

def test_4k_allowed_on_2_0_only():
    assert body_for(["--model", "2.0", "--resolution", "4k"])["resolution"] == "4k"

def test_4k_rejected_on_2_5():
    dies_with(["--resolution", "4k"], "2.0")

def test_1080p_rejected_on_fast():
    dies_with(["--fast", "--resolution", "1080p"], "720p")

def test_1080p_rejected_on_mini():
    dies_with(["--model", "mini", "--resolution", "1080p"], "720p")


# ---- label rendering ---------------------------------------------------------

def test_pretty_leaves_urls_untouched():
    assert seedance.pretty(IMG) == IMG


# ---- preserved defaults ------------------------------------------------------

def test_plain_t2v_defaults_preserved():
    body = body_for([])
    assert body["ratio"] == "16:9"
    assert body["resolution"] == "1080p"
    assert body["generate_audio"] is True
    assert body["return_last_frame"] is True
