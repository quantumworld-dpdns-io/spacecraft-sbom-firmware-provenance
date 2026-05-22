from __future__ import annotations

import json

import pytest

from sbom_provenance.utils.exporters import SBOMExporter


class TestSBOMExporter:
    @pytest.fixture
    def sample_sbom(self):
        return {
            "name": "Test SBOM",
            "version": "1.0.0",
            "organization": "NASA",
            "packages": [
                {
                    "spdx_id": "SPDXRef-LinuxKernel",
                    "name": "linux-kernel",
                    "version": "5.15.0",
                    "supplier": "Organization: Linux Foundation",
                    "download_location": "https://kernel.org/pub/linux/kernel/v5.x/linux-5.15.tar.xz",
                    "hashes": {"sha256": "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"},
                    "license": "GPL-2.0-only",
                    "copyright": "Copyright Linux Torvalds",
                }
            ],
            "relationships": [],
            "dependencies": [],
        }

    def test_to_spdx(self, sample_sbom):
        result = SBOMExporter.to_spdx(sample_sbom)
        assert result["spdxVersion"] == "SPDX-2.3"
        assert result["name"] == "Test SBOM"
        assert len(result["packages"]) == 1
        assert result["packages"][0]["name"] == "linux-kernel"
        assert result["packages"][0]["versionInfo"] == "5.15.0"
        assert len(result["packages"][0]["checksums"]) == 1

    def test_to_cyclonedx(self, sample_sbom):
        result = SBOMExporter.to_cyclonedx(sample_sbom)
        assert result["bomFormat"] == "CycloneDX"
        assert result["specVersion"] == "1.5"
        assert len(result["components"]) == 1
        assert result["components"][0]["name"] == "linux-kernel"

    def test_to_json(self, sample_sbom):
        result = SBOMExporter.to_json(sample_sbom)
        parsed = json.loads(result)
        assert parsed["name"] == "Test SBOM"

    def test_to_xml(self, sample_sbom):
        result = SBOMExporter.to_xml(sample_sbom)
        assert "<?xml" in result
        assert "<sbom>" in result
        assert "<name>Test SBOM</name>" in result

    def test_export_sbom_spdx(self, sample_sbom):
        result = SBOMExporter.export_sbom(sample_sbom, "spdx")
        assert isinstance(result, dict)
        assert result["spdxVersion"] == "SPDX-2.3"

    def test_export_sbom_cyclonedx(self, sample_sbom):
        result = SBOMExporter.export_sbom(sample_sbom, "cyclonedx")
        assert isinstance(result, dict)
        assert result["bomFormat"] == "CycloneDX"

    def test_export_sbom_json(self, sample_sbom):
        result = SBOMExporter.export_sbom(sample_sbom, "json")
        assert isinstance(result, str)
        assert "Test SBOM" in result

    def test_export_sbom_invalid_format(self, sample_sbom):
        with pytest.raises(ValueError, match="Unsupported format"):
            SBOMExporter.export_sbom(sample_sbom, "invalid")

    def test_spdx_creation_info(self, sample_sbom):
        result = SBOMExporter.to_spdx(sample_sbom)
        assert "creationInfo" in result
        assert "created" in result["creationInfo"]
        assert len(result["creationInfo"]["creators"]) == 2

    def test_cyclonedx_metadata(self, sample_sbom):
        result = SBOMExporter.to_cyclonedx(sample_sbom)
        assert "metadata" in result
        assert "component" in result["metadata"]
        assert result["metadata"]["component"]["name"] == "Test SBOM"

    def test_empty_packages(self):
        sbom = {"name": "Empty", "version": "1.0", "packages": [], "relationships": [], "dependencies": []}
        result = SBOMExporter.to_spdx(sbom)
        assert len(result["packages"]) == 0
