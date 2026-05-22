from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from typing import Any


class SBOMExporter:
    @staticmethod
    def to_spdx(sbom_data: dict) -> dict:
        return {
            "spdxVersion": "SPDX-2.3",
            "dataLicense": "CC0-1.0",
            "SPDXID": "SPDXRef-DOCUMENT",
            "name": sbom_data.get("name", "Unknown SBOM"),
            "creationInfo": {
                "created": datetime.now(UTC).isoformat(),
                "creators": [
                    "Tool: spacecraft-sbom-provenance-v0.1.0",
                    f"Organization: {sbom_data.get('organization', 'Unknown')}",
                ],
            },
            "packages": [
                {
                    "SPDXID": pkg.get("spdx_id"),
                    "name": pkg.get("name"),
                    "versionInfo": pkg.get("version"),
                    "supplier": pkg.get("supplier"),
                    "downloadLocation": pkg.get("download_location", "NOASSERTION"),
                    "checksums": [
                        {
                            "algorithm": algo.upper(),
                            "checksumValue": value,
                        }
                        for algo, value in (pkg.get("hashes") or {}).items()
                    ],
                    "licenseConcluded": pkg.get("license", "NOASSERTION"),
                    "copyrightText": pkg.get("copyright", "NOASSERTION"),
                }
                for pkg in sbom_data.get("packages", [])
            ],
            "relationships": [
                {
                    "spdxElementId": rel.get("source"),
                    "relationshipType": rel.get("type", "DEPENDS_ON"),
                    "relatedSpdxElement": rel.get("target"),
                }
                for rel in sbom_data.get("relationships", [])
            ],
        }

    @staticmethod
    def to_cyclonedx(sbom_data: dict) -> dict:
        return {
            "bomFormat": "CycloneDX",
            "specVersion": "1.5",
            "version": 1,
            "metadata": {
                "timestamp": datetime.now(UTC).isoformat(),
                "tools": [
                    {
                        "vendor": "quantumworld-dpdns-io",
                        "name": "spacecraft-sbom-provenance",
                        "version": "0.1.0",
                    }
                ],
                "component": {
                    "type": "application",
                    "name": sbom_data.get("name", "Unknown"),
                    "version": sbom_data.get("version", "0.0.0"),
                },
            },
            "components": [
                {
                    "type": pkg.get("type", "library"),
                    "name": pkg.get("name"),
                    "version": pkg.get("version"),
                    "purl": pkg.get("purl"),
                    "hashes": [
                        {
                            "alg": algo.upper(),
                            "content": value,
                        }
                        for algo, value in (pkg.get("hashes") or {}).items()
                    ],
                    "licenses": (
                        [{"license": {"id": pkg.get("license")}}]
                        if pkg.get("license")
                        else []
                    ),
                }
                for pkg in sbom_data.get("packages", [])
            ],
            "dependencies": [
                {
                    "ref": dep.get("ref"),
                    "dependsOn": dep.get("dependencies", []),
                }
                for dep in sbom_data.get("dependencies", [])
            ],
        }

    @staticmethod
    def to_json(sbom_data: dict, indent: int = 2) -> str:
        return json.dumps(sbom_data, indent=indent, default=str)

    @staticmethod
    def to_xml(sbom_data: dict) -> str:
        root = ET.Element("sbom")
        name = ET.SubElement(root, "name")
        name.text = sbom_data.get("name", "Unknown")
        packages = ET.SubElement(root, "packages")
        for pkg in sbom_data.get("packages", []):
            pkg_elem = ET.SubElement(packages, "package")
            ET.SubElement(pkg_elem, "name").text = pkg.get("name", "")
            ET.SubElement(pkg_elem, "version").text = pkg.get("version", "")
            ET.SubElement(pkg_elem, "supplier").text = pkg.get("supplier", "")
        return ET.tostring(root, encoding="unicode", xml_declaration=True)

    @staticmethod
    def export_sbom(sbom_data: dict, fmt: str = "spdx") -> dict | str:
        exporters = {
            "spdx": SBOMExporter.to_spdx,
            "cyclonedx": SBOMExporter.to_cyclonedx,
            "json": SBOMExporter.to_json,
            "xml": SBOMExporter.to_xml,
        }
        exporter = exporters.get(fmt.lower())
        if not exporter:
            raise ValueError(f"Unsupported format: {fmt}. Supported: {list(exporters.keys())}")
        result = exporter(sbom_data)
        return result
