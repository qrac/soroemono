"""End-to-end checks, including deliberate corruptions that must be rejected."""

from pathlib import Path
import os
import subprocess
import sys
import tempfile
import unittest

from fontTools.ttLib import TTFont

from soroemono.builder import build
from soroemono.sources import digest, fetch_baseline, source_paths, verified
from soroemono.validation import check

ROOT = Path(__file__).resolve().parents[1]


class BuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.work = tempfile.TemporaryDirectory()
        cls.output = Path(cls.work.name)
        cls.font = build(ROOT, cls.output / "first")

    @classmethod
    def tearDownClass(cls):
        cls.work.cleanup()

    def test_compiled_font_preserves_sources_and_layout(self):
        report = check(ROOT, self.font)
        self.assertTrue(report["passed"])
        self.assertEqual(report["counts"]["variation_sequences"], 10160)

    def test_bold_build_preserves_inputs_and_links_to_regular(self):
        bold_path = build(ROOT, self.output / "bold", "Bold")
        rebuilt = build(ROOT, self.output / "bold-rebuilt", "Bold")
        self.assertEqual(digest(bold_path.read_bytes()), digest(rebuilt.read_bytes()))
        report = check(ROOT, bold_path, "Bold")
        self.assertTrue(report["passed"])
        self.assertEqual(report["counts"]["variation_sequences"], 10160)
        regular, bold = TTFont(self.font), TTFont(bold_path)
        self.assertEqual(regular["name"].getDebugName(1), bold["name"].getDebugName(1))
        self.assertEqual(regular["name"].getDebugName(2), "Regular")
        self.assertEqual(bold["name"].getDebugName(2), "Bold")
        self.assertEqual((regular["OS/2"].usWeightClass, bold["OS/2"].usWeightClass), (400, 700))
        self.assertEqual((regular["hhea"].ascent, regular["hhea"].descent),
                         (bold["hhea"].ascent, bold["hhea"].descent))

    def test_rebuild_is_byte_identical(self):
        directory = self.output / "second"
        subprocess.run([sys.executable, "-m", "soroemono.cli", "build", "--output", str(directory)],
                       cwd=ROOT, env={**os.environ, "PYTHONHASHSEED": "731"},
                       check=True, capture_output=True, text=True)
        second = directory / self.font.name
        self.assertEqual(digest(self.font.read_bytes()), digest(second.read_bytes()))

    def test_width_regression_is_rejected(self):
        font = TTFont(self.font)
        name = font.getBestCmap()[0xFF71]
        font["hmtx"][name] = (500, font["hmtx"][name][1])
        broken = self.output / "broken.ttf"
        font.save(broken)
        with self.assertRaisesRegex(ValueError, "Halfwidth kana U\\+FF71 is not 600"):
            check(ROOT, broken)

    def test_untrusted_inputs_are_rejected(self):
        paths = source_paths(ROOT)
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            verified(paths["latin"], "0" * 64)
        archive = self.output / "wrong-release.zip"
        archive.write_bytes(b"not the pinned release")
        with self.assertRaisesRegex(ValueError, "archive SHA-256 mismatch"):
            fetch_baseline(ROOT, archive)


if __name__ == "__main__":
    unittest.main()
