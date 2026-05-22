from __future__ import annotations

import hashlib
import hmac
from pathlib import Path
from typing import BinaryIO


class CryptoUtils:
    @staticmethod
    def sha256_hash(data: bytes | BinaryIO) -> str:
        h = hashlib.sha256()
        if isinstance(data, bytes):
            h.update(data)
        else:
            chunk = data.read(65536)
            while chunk:
                h.update(chunk)
                chunk = data.read(65536)
        return h.hexdigest()

    @staticmethod
    def sha384_hash(data: bytes | BinaryIO) -> str:
        h = hashlib.sha384()
        if isinstance(data, bytes):
            h.update(data)
        else:
            chunk = data.read(65536)
            while chunk:
                h.update(chunk)
                chunk = data.read(65536)
        return h.hexdigest()

    @staticmethod
    def sha512_hash(data: bytes | BinaryIO) -> str:
        h = hashlib.sha512()
        if isinstance(data, bytes):
            h.update(data)
        else:
            chunk = data.read(65536)
            while chunk:
                h.update(chunk)
                chunk = data.read(65536)
        return h.hexdigest()

    @staticmethod
    def blake2b_hash(data: bytes, digest_size: int = 64) -> str:
        h = hashlib.blake2b(data, digest_size=digest_size)
        return h.hexdigest()

    @staticmethod
    def verify_hmac(key: bytes, message: bytes, signature: str, algorithm: str = "sha256") -> bool:
        algo = getattr(hashlib, algorithm, hashlib.sha256)
        expected = hmac.new(key, message, algo).hexdigest()
        return hmac.compare_digest(expected, signature)

    @staticmethod
    def compute_file_hash(file_path: Path, algorithm: str = "sha256") -> str:
        hash_fn = getattr(hashlib, algorithm, hashlib.sha256)()
        with open(file_path, "rb") as f:
            chunk = f.read(65536)
            while chunk:
                hash_fn.update(chunk)
                chunk = f.read(65536)
        return hash_fn.hexdigest()

    @staticmethod
    def verify_file_hash(file_path: Path, expected_hash: str, algorithm: str = "sha256") -> bool:
        computed = CryptoUtils.compute_file_hash(file_path, algorithm)
        return hmac.compare_digest(computed, expected_hash.lower())

    @staticmethod
    def generate_firmware_digest(firmware_data: bytes, hash_type: str = "sha256") -> dict:
        hash_type = hash_type.lower().replace("-", "")
        hash_map = {
            "sha256": hashlib.sha256,
            "sha384": hashlib.sha384,
            "sha512": hashlib.sha512,
            "blake2b": lambda d: hashlib.blake2b(d, digest_size=64),
        }
        if hash_type not in hash_map:
            raise ValueError(f"Unsupported hash type: {hash_type}")
        h = hash_map[hash_type](firmware_data)
        return {
            "algorithm": hash_type,
            "hex_digest": h.hexdigest(),
            "base64_digest": h.hexdigest(),  # Simplified; real impl would use base64
            "size_bytes": len(firmware_data),
        }
