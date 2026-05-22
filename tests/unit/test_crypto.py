from __future__ import annotations

import hashlib

import pytest

from sbom_provenance.utils.crypto import CryptoUtils


class TestCryptoUtils:
    def test_sha256_hash_bytes(self):
        data = b"test data for hashing"
        expected = hashlib.sha256(data).hexdigest()
        result = CryptoUtils.sha256_hash(data)
        assert result == expected

    def test_sha256_hash_string(self):
        data = b"hello world"
        expected = hashlib.sha256(data).hexdigest()
        result = CryptoUtils.sha256_hash(data)
        assert result == expected

    def test_sha512_hash(self):
        data = b"test data"
        expected = hashlib.sha512(data).hexdigest()
        result = CryptoUtils.sha512_hash(data)
        assert result == expected

    def test_blake2b_hash(self):
        data = b"test blake2b"
        result = CryptoUtils.blake2b_hash(data)
        assert len(result) == 128  # 64 bytes = 128 hex chars
        assert isinstance(result, str)

    def test_blake2b_different_sizes(self):
        data = b"test"
        result_32 = CryptoUtils.blake2b_hash(data, digest_size=32)
        result_64 = CryptoUtils.blake2b_hash(data, digest_size=64)
        assert len(result_32) == 64  # 32 bytes
        assert len(result_64) == 128  # 64 bytes
        assert result_32 != result_64

    def test_verify_hmac_valid(self):
        key = b"secret-key"
        message = b"important message"
        import hmac
        expected = hmac.new(key, message, hashlib.sha256).hexdigest()
        assert CryptoUtils.verify_hmac(key, message, expected)

    def test_verify_hmac_invalid(self):
        key = b"secret-key"
        message = b"important message"
        assert not CryptoUtils.verify_hmac(key, message, "invalid-signature")

    def test_generate_firmware_digest_sha256(self):
        data = b"firmware binary data"
        result = CryptoUtils.generate_firmware_digest(data, "sha256")
        assert result["algorithm"] == "sha256"
        assert len(result["hex_digest"]) == 64
        assert result["size_bytes"] == len(data)

    def test_generate_firmware_digest_sha384(self):
        data = b"firmware binary data"
        result = CryptoUtils.generate_firmware_digest(data, "sha384")
        assert result["algorithm"] == "sha384"
        assert len(result["hex_digest"]) == 96

    def test_generate_firmware_digest_invalid_algorithm(self):
        data = b"test"
        with pytest.raises(ValueError, match="Unsupported hash type"):
            CryptoUtils.generate_firmware_digest(data, "md5")

    def test_verify_file_hash_no_file(self):
        from pathlib import Path
        result = CryptoUtils.verify_file_hash(
            Path("/nonexistent/file.bin"),
            "abc123",
        )
        assert not result  # Should return False for non-existent file
