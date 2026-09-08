import copy
import hashlib
import pathlib
import subprocess
import sys
import unittest

from PIL import Image

from pipeline.promos.vr_game_things_puzzle import build as promo
from pipeline.promos.vr_game_things_puzzle import slate
from pipeline.promos.vr_game_things_puzzle import verify


REPO = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = REPO / "pipeline/promos/vr_game_things_puzzle/manifest.json"


def test_manifest_excludes_thirteen_system_fallbacks():
    manifest = promo.load_manifest(MANIFEST)
    paths = [str(shot.get("path", "")) for shot in manifest["shots"]]
    assert not any(path.endswith(("grab.mp4", "snap.mp4")) for path in paths)
    assert not any(
        "exploded" in asset.lower()
        for shot in manifest["shots"]
        for asset in shot.get("source_assets", [])
    )


def test_manifest_uses_only_tracked_inputs_from_fresh_checkout():
    manifest = promo.load_manifest(MANIFEST)
    errors = promo.validate_manifest(manifest, REPO, require_files=True)
    assert errors == []
    assert all(
        shot["kind"] == "title"
        or str(shot["path"]).startswith("deliverables/vr-game-things-puzzle-promo/")
        for shot in manifest["shots"]
    )


def test_slate_is_manifest_driven_and_delivery_sized(tmp_path):
    manifest = promo.load_manifest(MANIFEST)

    first = slate.render_slate(manifest, tmp_path / "first.png")
    changed = copy.deepcopy(manifest)
    changed["tagline"] = "A different approved line"
    second = slate.render_slate(changed, tmp_path / "second.png")

    assert Image.open(first).size == (1920, 1080)
    assert hashlib.sha256(first.read_bytes()).digest() != hashlib.sha256(second.read_bytes()).digest()


def test_ffmpeg_command_matches_shot_audio_and_uses_generated_slate(tmp_path):
    manifest = {
        "width": 1920,
        "height": 1080,
        "fps": 24,
        "transition": 0.25,
        "shots": [
            {
                "path": "deliverables/vr-game-things-puzzle-promo/source/library.mp4",
                "duration": 3.0,
                "kind": "repository",
                "has_audio": True,
                "source_assets": [],
            },
            {
                "path": None,
                "duration": 3.5,
                "kind": "title",
                "has_audio": False,
                "source_assets": [],
            },
        ],
    }
    slate_path = tmp_path / "approved-slate.png"
    command = promo.build_ffmpeg_command(
        manifest, REPO, tmp_path / "assembled.mp4", slate_path
    )

    filter_graph = command[command.index("-filter_complex") + 1]
    assert "[0:a]aresample=48000" in filter_graph
    assert "anullsrc=channel_layout=stereo:sample_rate=48000" in filter_graph
    assert "acrossfade=d=0.250" in filter_graph
    assert "[source_audio][ambience]amix=inputs=2" in filter_graph
    assert str(slate_path) in command
    assert "title.mp4" not in " ".join(command)


def test_build_cli_print_command_renders_a_slate(tmp_path):
    output = tmp_path / "promo.mp4"
    result = subprocess.run(
        [
            sys.executable,
            str(REPO / "pipeline/promos/vr_game_things_puzzle/build.py"),
            "--repo",
            str(REPO),
            "--manifest",
            str(MANIFEST),
            "--output",
            str(output),
            "--print-command",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert output.with_suffix(".slate.png").is_file()
    assert "title.mp4" not in result.stdout


def _make_test_media(
    path, *, width, height=1080, pix_fmt="yuv420p", duration=0.2, faststart=True
):
    command = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        f"color=c=black:s={width}x{height}:r=24",
        "-f",
        "lavfi",
        "-i",
        "anullsrc=channel_layout=stereo:sample_rate=48000",
        "-t",
        str(duration),
        "-c:v",
        "libx264",
        "-pix_fmt",
        pix_fmt,
        "-c:a",
        "aac",
    ]
    if faststart:
        command.extend(["-movflags", "+faststart"])
    command.append(str(path))
    subprocess.run(
        command,
        check=True,
        capture_output=True,
    )


def test_media_verifier_accepts_delivery_media_and_checks_hash(tmp_path):
    media_path = tmp_path / "valid.mp4"
    _make_test_media(media_path, width=1920, duration=25.0)

    errors = verify.verify_media(
        media_path,
        {
            "width": 1920,
            "height": 1080,
            "fps": 24,
            "video_codec": "h264",
            "audio_codec": "aac",
            "sample_rate": 48000,
            "channels": 2,
            "faststart": True,
        },
    )

    assert errors == []
    payload = tmp_path / "payload.bin"
    payload.write_bytes(b"abc")
    assert verify.sha256_file(payload) == (
        "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    )


def test_media_verifier_reports_wrong_dimensions(tmp_path):
    media_path = tmp_path / "wrong-size.mp4"
    _make_test_media(media_path, width=640, height=360)

    errors = verify.verify_media(media_path, {"width": 1920, "height": 1080})

    assert "dimensions must be 1920x1080, got 640x360" in errors


def test_media_verifier_requires_faststart_atom_order(tmp_path):
    media_path = tmp_path / "slow-start.mp4"
    _make_test_media(media_path, width=1920, faststart=False)

    errors = verify.verify_media(media_path, {"width": 1920, "height": 1080})

    assert "moov atom must occur before mdat" in errors


def test_media_verifier_rejects_non_yuv420p_pixel_format(tmp_path):
    media_path = tmp_path / "wrong-pixel-format.mp4"
    _make_test_media(media_path, width=1920, pix_fmt="yuv444p", duration=25.0)

    errors = verify.verify_media(media_path, {"width": 1920, "height": 1080})

    assert "pixel format must be yuv420p, got yuv444p" in errors


def test_media_verifier_rejects_duration_outside_delivery_range(tmp_path):
    media_path = tmp_path / "too-short.mp4"
    _make_test_media(media_path, width=1920, duration=1.0)

    errors = verify.verify_media(media_path, {"width": 1920, "height": 1080})

    assert any(error.startswith("duration must be 25-30 seconds, got ") for error in errors)


class PromoManifestTests(unittest.TestCase):
    def test_manifest_matches_approved_delivery_contract(self):
        manifest = promo.load_manifest(MANIFEST)

        self.assertEqual((manifest["width"], manifest["height"]), (1920, 1080))
        self.assertEqual(manifest["fps"], 24)
        self.assertEqual(manifest["title"], "VR Game Things Puzzle")
        self.assertEqual(manifest["tagline"], "Build it. Then operate it.")
        self.assertGreaterEqual(promo.timeline_duration(manifest), 25.0)
        self.assertLessEqual(promo.timeline_duration(manifest), 30.0)
        self.assertTrue(any(shot["kind"] == "seedance" for shot in manifest["shots"]))
        self.assertIn("cinematic visualization", manifest["disclosure"].lower())

    def test_manifest_rejects_unimplemented_claims(self):
        manifest = promo.load_manifest(MANIFEST)
        manifest["tagline"] = "Fly the Apache in combat"

        errors = promo.validate_manifest(manifest, REPO, require_files=False)

        self.assertIn("forbidden claim: combat", errors)
        self.assertIn("forbidden claim: flight", errors)

    def test_manifest_rejects_missing_seedance_disclosure(self):
        manifest = promo.load_manifest(MANIFEST)
        manifest["disclosure"] = ""

        errors = promo.validate_manifest(manifest, REPO, require_files=False)

        self.assertIn("Seedance shots require a cinematic visualization disclosure", errors)

    def test_manifest_rejects_unsupported_shot_kind(self):
        manifest = promo.load_manifest(MANIFEST)
        manifest["shots"][0]["kind"] = "imaginary"

        errors = promo.validate_manifest(manifest, REPO, require_files=False)

        self.assertIn("shot 1 has unsupported kind: imaginary", errors)

    def test_manifest_rejects_non_24_fps(self):
        manifest = promo.load_manifest(MANIFEST)
        manifest["fps"] = 30

        errors = promo.validate_manifest(manifest, REPO, require_files=False)

        self.assertIn("fps must be 24", errors)

    def test_manifest_requires_boolean_audio_declaration(self):
        manifest = promo.load_manifest(MANIFEST)
        manifest["shots"][0]["has_audio"] = "false"

        errors = promo.validate_manifest(manifest, REPO, require_files=False)

        self.assertIn("shot 1 has_audio must be Boolean", errors)

    def test_manifest_requires_title_without_path(self):
        manifest = promo.load_manifest(MANIFEST)
        manifest["shots"][-1]["path"] = "deliverables/title.mp4"

        errors = promo.validate_manifest(manifest, REPO, require_files=False)

        self.assertIn("shot 7 title must not have a path", errors)

    def test_manifest_rejects_exploded_repository_source_asset(self):
        manifest = promo.load_manifest(MANIFEST)
        manifest["shots"][0]["source_assets"] = ["refs/02-apache-exploded.png"]

        errors = promo.validate_manifest(manifest, REPO, require_files=False)

        self.assertIn("shot 1 repository source asset must not be exploded", errors)

    def test_manifest_accepts_disclosed_repository_render_fallback(self):
        manifest = promo.load_manifest(MANIFEST)
        manifest["shots"][0]["kind"] = "repository"
        manifest["disclosure"] = (
            "Concept footage from repository renders with Seedance cinematic visualization."
        )

        errors = promo.validate_manifest(manifest, REPO, require_files=False)

        self.assertNotIn("shot 1 has unsupported kind: repository", errors)

    def test_timeline_duration_includes_transition_overlap(self):
        manifest = {
            "transition": 0.25,
            "shots": [
                {"duration": 3.0},
                {"duration": 5.0},
                {"duration": 4.0},
            ],
        }

        self.assertEqual(promo.timeline_duration(manifest), 11.5)

    def test_ffmpeg_command_uses_approved_delivery_codecs(self):
        manifest = promo.load_manifest(MANIFEST)
        command = promo.build_ffmpeg_command(
            manifest,
            REPO,
            REPO / "output/vr-game-things-puzzle-promo/test.mp4",
            REPO / "output/vr-game-things-puzzle-promo/test-slate.png",
        )

        self.assertEqual(command[0], "ffmpeg")
        self.assertIn("libx264", command)
        self.assertIn("yuv420p", command)
        self.assertIn("aac", command)
        self.assertIn("48000", command)
        self.assertIn("+faststart", command)
        self.assertEqual(command[-1], str(REPO / "output/vr-game-things-puzzle-promo/test.mp4"))

    def test_ffmpeg_command_sets_audible_restrained_sound_bed(self):
        manifest = promo.load_manifest(MANIFEST)
        command = promo.build_ffmpeg_command(
            manifest,
            REPO,
            REPO / "output/vr-game-things-puzzle-promo/test.mp4",
            REPO / "output/vr-game-things-puzzle-promo/test-slate.png",
        )

        filter_graph = command[command.index("-filter_complex") + 1]
        self.assertIn("anoisesrc=color=pink:amplitude=0.04", " ".join(command))
        self.assertIn("volume=0.40[noise]", filter_graph)
        self.assertIn("volume=0.12[hum]", filter_graph)
        self.assertIn("alimiter=limit=0.7", filter_graph)

    def test_missing_sources_are_reported_in_manifest_order(self):
        manifest = copy.deepcopy(promo.load_manifest(MANIFEST))
        manifest["shots"] = manifest["shots"][:2]
        manifest["shots"][0]["path"] = "output/__missing_library.mp4"
        manifest["shots"][1]["path"] = "output/__missing_grab.mp4"

        errors = promo.validate_manifest(manifest, REPO, require_files=True)

        self.assertEqual(
            errors[-2:],
            [
                "shot 1 source is missing: output/__missing_library.mp4",
                "shot 2 source is missing: output/__missing_grab.mp4",
            ],
        )


if __name__ == "__main__":
    unittest.main()
