"""Static safety contract for a PowerShell script not executable on this host.

These tests are intentionally NOT claimed to validate PowerShell semantics or
actual Windows process/shortcut inventory at runtime.
"""
from pathlib import Path
import re
import unittest


SCRIPT = Path(__file__).with_name("v2_windows_inventory.ps1")


class WindowsInventorySourceContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SCRIPT.read_text(encoding="utf-8")

    def test_dry_run_is_default_and_explicit_inspect_required(self):
        self.assertIn("[switch] $Inspect", self.source)
        self.assertIn("if (-not $Inspect)", self.source)
        self.assertIn("inspectedHost = $false", self.source)

    def test_only_canonical_root_and_separate_v1_v2_ports(self):
        self.assertIn("'D:\\VERA'", self.source)
        self.assertNotIn("'C:\\VERA'", self.source)
        self.assertNotIn("[string] $VeraRoot", self.source)
        self.assertIn("Get-ListenerInventory 18777", self.source)
        self.assertIn("Get-ListenerInventory 18781", self.source)

    def test_no_host_mutations_or_credentials_in_source(self):
        forbidden = (
            r"\b(?:Set|New|Remove|Stop|Start|Register|Unregister)-"
            r"(?:Service|ScheduledTask|Item|NetFirewallRule|Process|Content|ItemProperty)\b",
            r"\b(?:Invoke-WebRequest|Invoke-RestMethod|Enter-PSSession|Start-Process)\b",
            r"\b(?:device-v2-token|Bearer|Get-Content|ReadAllText|ReadAllBytes)\b",
        )
        for pattern in forbidden:
            with self.subTest(pattern=pattern):
                self.assertIsNone(re.search(pattern, self.source, re.IGNORECASE))

    def test_never_certifies_by_process_or_shortcut_observation(self):
        self.assertIn("v2Authenticated = $false", self.source)
        self.assertIn("enrollmentQualified = $false", self.source)
        self.assertIn("releaseQualified = $false", self.source)
        self.assertIn("ExpectedClientSha256 -match", self.source)
        self.assertIn("Get-FileHash", self.source)


if __name__ == "__main__":
    unittest.main()
