from __future__ import annotations

import re
from typing import Any
from uuid import UUID


class Validators:
    # SPDX identifier pattern
    SPDX_PACKAGE_PATTERN = re.compile(r"^SPDXRef-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*$")
    # CVE pattern
    CVE_PATTERN = re.compile(r"^CVE-\d{4}-\d{4,}$")
    # CPE pattern
    CPE_PATTERN = re.compile(r"^cpe:2\.3:[aho*\-](:[^\s]*){9,10}$")
    # PURL pattern
    PURL_PATTERN = re.compile(r"^pkg:[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+/.+$")
    # Hash pattern (hex)
    HEX_HASH_PATTERN = re.compile(r"^[a-fA-F0-9]{32,}$")
    # UUID pattern
    UUID_PATTERN = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)
    # Semantic version
    SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+(?:-[a-zA-Z0-9.]+)?(?:\+[a-zA-Z0-9.]+)?$")
    # Firmware version pattern
    FIRMWARE_VERSION_PATTERN = re.compile(r"^v?\d+\.\d+\.\d+(?:-[a-zA-Z0-9.]+)?$")

    @classmethod
    def validate_spdx_id(cls, value: str) -> bool:
        return bool(cls.SPDX_PACKAGE_PATTERN.match(value))

    @classmethod
    def validate_cve_id(cls, value: str) -> bool:
        return bool(cls.CVE_PATTERN.match(value))

    @classmethod
    def validate_cpe(cls, value: str) -> bool:
        return bool(cls.CPE_PATTERN.match(value))

    @classmethod
    def validate_purl(cls, value: str) -> bool:
        return bool(cls.PURL_PATTERN.match(value))

    @classmethod
    def validate_hash(cls, value: str) -> bool:
        return bool(cls.HEX_HASH_PATTERN.match(value))

    @classmethod
    def validate_uuid(cls, value: str) -> bool:
        return bool(cls.UUID_PATTERN.match(value))

    @classmethod
    def validate_semver(cls, value: str) -> bool:
        return bool(cls.SEMVER_PATTERN.match(value))

    @classmethod
    def validate_firmware_version(cls, value: str) -> bool:
        return bool(cls.FIRMWARE_VERSION_PATTERN.match(value))

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        filename = re.sub(r"[^\w\-_.]", "_", filename)
        return filename[:255]

    @staticmethod
    def sanitize_input(value: str) -> str:
        return re.sub(r"[<>\'\"%;()&+]", "", value)

    @staticmethod
    def validate_json_schema(data: dict, schema: dict) -> tuple[bool, list[str]]:
        errors = []
        for required_field in schema.get("required", []):
            if required_field not in data:
                errors.append(f"Missing required field: {required_field}")
        for field, field_schema in schema.get("properties", {}).items():
            if field in data:
                field_type = field_schema.get("type")
                if field_type == "string" and not isinstance(data[field], str):
                    errors.append(f"Field {field} should be string")
                elif field_type == "integer" and not isinstance(data[field], int):
                    errors.append(f"Field {field} should be integer")
                elif field_type == "array" and not isinstance(data[field], list):
                    errors.append(f"Field {field} should be array")
        return len(errors) == 0, errors
