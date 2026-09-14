import json
import tempfile
import unittest
from pathlib import Path

import finalize_container


class FinalizationTests(unittest.TestCase):
    def test_publishes_exact_bytes_and_updates_only_checksum(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            partial, destination = root / "image.partial", root / "image.sif"
            site, receipt = root / "site.env", root / "completed.json"
            partial.write_bytes(b"fake completed SIF")
            site.write_text("# retained\nexport VLLM_SIF_SHA256=PLACEHOLDER\nexport HF_TOKEN_PATH=/private/token\n")
            site.chmod(0o600)
            result = finalize_container.finalize(partial, destination, site, receipt)
            self.assertEqual(destination.read_bytes(), b"fake completed SIF")
            self.assertFalse(partial.exists())
            self.assertTrue(result["site_checksum_updated"])
            self.assertEqual(site.stat().st_mode & 0o777, 0o600)
            self.assertEqual(site.read_text(), "# retained\nexport VLLM_SIF_SHA256=" + result["sha256"]
                             + "\nexport HF_TOKEN_PATH=/private/token\n")
            self.assertNotIn("/private/token", receipt.read_text())

    def test_existing_image_is_never_replaced(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "old.sif").write_bytes(b"old")
            (root / "new.partial").write_bytes(b"new")
            with self.assertRaises(ValueError):
                finalize_container.finalize(root / "new.partial", root / "old.sif", root / "site", root / "receipt")
            self.assertEqual((root / "old.sif").read_bytes(), b"old")
            self.assertEqual((root / "new.partial").read_bytes(), b"new")

    def test_failed_site_update_keeps_image_and_failure_receipt(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "new.partial").write_bytes(b"new")
            (root / "site").write_text("export OTHER=keep\n")
            with self.assertRaises(ValueError):
                finalize_container.finalize(root / "new.partial", root / "image.sif", root / "site", root / "receipt")
            self.assertEqual((root / "image.sif").read_bytes(), b"new")
            self.assertFalse(json.loads((root / "receipt").read_text())["site_checksum_updated"])
            self.assertEqual((root / "site").read_text(), "export OTHER=keep\n")


if __name__ == "__main__":
    unittest.main()
