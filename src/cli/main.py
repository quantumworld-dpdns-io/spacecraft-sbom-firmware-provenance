from __future__ import annotations

import argparse
import asyncio
import json
import sys


def cli_entry() -> None:
    parser = argparse.ArgumentParser(
        description="Spacecraft SBOM & Firmware Provenance CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # SBOM commands
    sbom_parser = subparsers.add_parser("sbom", help="SBOM operations")
    sbom_sub = sbom_parser.add_subparsers(dest="sbom_action")
    sbom_create = sbom_sub.add_parser("create", help="Create a new SBOM document")
    sbom_create.add_argument("--name", required=True)
    sbom_create.add_argument("--version", required=True)
    sbom_create.add_argument("--organization")
    sbom_list = sbom_sub.add_parser("list", help="List SBOM documents")
    sbom_list.add_argument("--page", type=int, default=1)
    sbom_list.add_argument("--per-page", type=int, default=20)

    # Firmware commands
    fw_parser = subparsers.add_parser("firmware", help="Firmware operations")
    fw_sub = fw_parser.add_subparsers(dest="fw_action")
    fw_create = fw_sub.add_parser("register", help="Register firmware image")
    fw_create.add_argument("--name", required=True)
    fw_create.add_argument("--version", required=True)
    fw_create.add_argument("--device", required=True)
    fw_verify = fw_sub.add_parser("verify", help="Verify firmware")
    fw_verify.add_argument("--id", required=True)

    # Provenance commands
    prov_parser = subparsers.add_parser("provenance", help="Provenance operations")
    prov_sub = prov_parser.add_subparsers(dest="prov_action")
    prov_trace = prov_sub.add_parser("trace", help="Trace provenance")
    prov_trace.add_argument("--target-type", required=True)
    prov_trace.add_argument("--target-id", required=True)

    # Security commands
    sec_parser = subparsers.add_parser("security", help="Security operations")
    sec_sub = sec_parser.add_subparsers(dest="sec_action")
    sec_scan = sec_sub.add_parser("scan", help="Start vulnerability scan")
    sec_scan.add_argument("--target-id", required=True)
    sec_scan.add_argument("--target-type", required=True)

    # Search commands
    search_parser = subparsers.add_parser("search", help="Search operations")
    search_parser.add_argument("--query", required=True)
    search_parser.add_argument("--type", choices=["all", "sbom", "firmware"], default="all")

    # Server command
    server_parser = subparsers.add_parser("serve", help="Start the API server")
    server_parser.add_argument("--host", default="0.0.0.0")
    server_parser.add_argument("--port", type=int, default=8000)
    server_parser.add_argument("--reload", action="store_true")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "serve":
        import uvicorn
        uvicorn.run(
            "sbom_provenance.main:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
        )
    else:
        asyncio.run(_handle_command(args))


async def _handle_command(args: argparse.Namespace) -> None:
    base_url = "http://localhost:8000/api/v1"

    if args.command == "sbom":
        await _handle_sbom(args, base_url)
    elif args.command == "firmware":
        await _handle_firmware(args, base_url)
    elif args.command == "provenance":
        await _handle_provenance(args, base_url)
    elif args.command == "security":
        await _handle_security(args, base_url)
    elif args.command == "search":
        await _handle_search(args, base_url)


async def _handle_sbom(args: argparse.Namespace, base_url: str) -> None:
    import httpx

    async with httpx.AsyncClient() as client:
        if args.sbom_action == "create":
            data = {"name": args.name, "version": args.version}
            if args.organization:
                data["organization"] = args.organization
            response = await client.post(f"{base_url}/sbom", json=data)
            print(json.dumps(response.json(), indent=2))
        elif args.sbom_action == "list":
            response = await client.get(
                f"{base_url}/sbom",
                params={"page": args.page, "per_page": args.per_page},
            )
            print(json.dumps(response.json(), indent=2))
        else:
            print("Unknown SBOM action")


async def _handle_firmware(args: argparse.Namespace, base_url: str) -> None:
    import httpx

    async with httpx.AsyncClient() as client:
        if args.fw_action == "register":
            data = {
                "name": args.name,
                "version": args.version,
                "device": args.device,
            }
            response = await client.post(f"{base_url}/firmware", json=data)
            print(json.dumps(response.json(), indent=2))
        elif args.fw_action == "verify":
            response = await client.post(f"{base_url}/firmware/{args.id}/verify")
            print(json.dumps(response.json(), indent=2))
        else:
            print("Unknown firmware action")


async def _handle_provenance(args: argparse.Namespace, base_url: str) -> None:
    import httpx

    async with httpx.AsyncClient() as client:
        if args.prov_action == "trace":
            response = await client.get(
                f"{base_url}/provenance/trace/{args.target_type}/{args.target_id}"
            )
            print(json.dumps(response.json(), indent=2))
        else:
            print("Unknown provenance action")


async def _handle_security(args: argparse.Namespace, base_url: str) -> None:
    import httpx

    async with httpx.AsyncClient() as client:
        if args.sec_action == "scan":
            data = {"target_id": args.target_id, "target_type": args.target_type, "scanner_name": "cli-scan"}
            response = await client.post(f"{base_url}/security/scans", json=data)
            print(json.dumps(response.json(), indent=2))
        else:
            print("Unknown security action")


async def _handle_search(args: argparse.Namespace, base_url: str) -> None:
    import httpx

    async with httpx.AsyncClient() as client:
        params = {"q": args.query}
        if args.type == "sbom":
            response = await client.get(f"{base_url}/search/sbom", params=params)
        elif args.type == "firmware":
            response = await client.get(f"{base_url}/search/firmware", params=params)
        else:
            response = await client.get(f"{base_url}/search", params=params)
        print(json.dumps(response.json(), indent=2))
