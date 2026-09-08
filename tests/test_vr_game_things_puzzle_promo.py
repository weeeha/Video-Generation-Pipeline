import copy
import pathlib
import unittest

from pipeline.promos.vr_game_things_puzzle import build as promo


REPO = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = REPO / "pipeline/promos/vr_game_things_puzzle/manifest.json"


class PromoManifestTests(unittest.TestCase):
    def test_manifest_matches_approved_delivery_contract(self):
        manifest = promo.load_manifest(MANIFEST)

        self.assertEqual((manifest["width"], manifest["height"]), (1920, 1080))
        self.assertIn(manifest["fps"], (24, 30))
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
        )

        self.assertEqual(command[0], "ffmpeg")
        self.assertIn("libx264", command)
        self.assertIn("yuv420p", command)
        self.assertIn("aac", command)
        self.assertIn("48000", command)
        self.assertIn("+faststart", command)
        self.assertEqual(command[-1], str(REPO / "output/vr-game-things-puzzle-promo/test.mp4"))

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
