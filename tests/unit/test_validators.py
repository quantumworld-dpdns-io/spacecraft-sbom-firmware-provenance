from __future__ import annotations

import pytest

from sbom_provenance.utils.validators import Validators


class TestValidators:
    def test_valid_spdx_id(self):
        assert Validators.validate_spdx_id("SPDXRef-Package")
        assert Validators.validate_spdx_id("SPDXRef-Linux-Kernel")
        assert Validators.validate_spdx_id("SPDXRef-A")

    def test_invalid_spdx_id(self):
        assert not Validators.validate_spdx_id("InvalidRef")
        assert not Validators.validate_spdx_id("SPDXRef-")
        assert not Validators.validate_spdx_id("")
        assert not Validators.validate_spdx_id("spdxref-package")

    def test_valid_cve_id(self):
        assert Validators.validate_cve_id("CVE-2024-1234")
        assert Validators.validate_cve_id("CVE-2023-12345")
        assert Validators.validate_cve_id("CVE-1999-0001")

    def test_invalid_cve_id(self):
        assert not Validators.validate_cve_id("CVE-2024-123")
        assert not Validators.validate_cve_id("cve-2024-1234")
        assert not Validators.validate_cve_id("CVE-24-1234")
        assert not Validators.validate_cve_id("")

    def test_valid_purl(self):
        assert Validators.validate_purl("pkg:pypi/django@1.11.1")
        assert Validators.validate_purl("pkg:npm/express@4.17.1")

    def test_invalid_purl(self):
        assert not Validators.validate_purl("")
        assert not Validators.validate_purl("not-a-purl")

    def test_valid_uuid(self):
        assert Validators.validate_uuid("550e8400-e29b-41d4-a716-446655440000")
        assert Validators.validate_uuid("00000000-0000-0000-0000-000000000000")

    def test_invalid_uuid(self):
        assert not Validators.validate_uuid("not-a-uuid")
        assert not Validators.validate_uuid("")

    def test_valid_semver(self):
        assert Validators.validate_semver("1.0.0")
        assert Validators.validate_semver("2.1.3-beta")
        assert Validators.validate_semver("0.0.1+build123")

    def test_invalid_semver(self):
        assert not Validators.validate_semver("1.0")
        assert not Validators.validate_semver("abc")
        assert not Validators.validate_semver("")

    def test_valid_firmware_version(self):
        assert Validators.validate_firmware_version("v1.0.0")
        assert Validators.validate_firmware_version("2.1.3-beta")

    def test_sanitize_input(self):
        assert Validators.sanitize_input("<script>alert('xss')</script>") == "scriptalert'xss'/script"
        assert Validators.sanitize_input("normal text") == "normal text"
        assert Validators.sanitize_input("") == ""

    def test_sanitize_filename(self):
        name = Validators.sanitize_filename("test<file>.bin")
        assert "<" not in name
        assert ">" not in name
        assert len(name) <= 255

    def test_validate_json_schema_valid(self):
        data = {"name": "test", "version": "1.0"}
        schema = {
            "required": ["name", "version"],
            "properties": {
                "name": {"type": "string"},
                "version": {"type": "string"},
            },
        }
        valid, errors = Validators.validate_json_schema(data, schema)
        assert valid
        assert len(errors) == 0

    def test_validate_json_schema_missing_required(self):
        data = {"name": "test"}
        schema = {
            "required": ["name", "version"],
            "properties": {
                "name": {"type": "string"},
                "version": {"type": "string"},
            },
        }
        valid, errors = Validators.validate_json_schema(data, schema)
        assert not valid
        assert len(errors) == 1
        assert "version" in errors[0]
