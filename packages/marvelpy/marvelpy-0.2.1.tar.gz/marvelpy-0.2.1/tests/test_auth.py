"""Tests for authentication utilities."""

from unittest.mock import patch

from marvelpy.utils.auth import generate_auth_params


class TestAuth:
    """Test cases for authentication utilities."""

    def test_generate_auth_params(self):
        """Test authentication parameter generation."""
        public_key = "test_public_key"
        private_key = "test_private_key"

        with patch("time.time", return_value=1234567890):
            params = generate_auth_params(public_key, private_key)

            assert "apikey" in params
            assert "ts" in params
            assert "hash" in params

            assert params["apikey"] == public_key
            assert params["ts"] == "1234567890"
            assert isinstance(params["hash"], str)
            assert len(params["hash"]) == 32  # MD5 hash length

    def test_generate_auth_params_different_timestamps(self):
        """Test that different timestamps generate different hashes."""
        public_key = "test_public_key"
        private_key = "test_private_key"

        with patch("time.time", return_value=1234567890):
            params1 = generate_auth_params(public_key, private_key)

        with patch("time.time", return_value=1234567891):
            params2 = generate_auth_params(public_key, private_key)

        assert params1["ts"] != params2["ts"]
        assert params1["hash"] != params2["hash"]
        assert params1["apikey"] == params2["apikey"]

    def test_generate_auth_params_different_keys(self):
        """Test that different keys generate different hashes."""
        public_key1 = "test_public_key_1"
        private_key1 = "test_private_key_1"
        public_key2 = "test_public_key_2"
        private_key2 = "test_private_key_2"

        with patch("time.time", return_value=1234567890):
            params1 = generate_auth_params(public_key1, private_key1)
            params2 = generate_auth_params(public_key2, private_key2)

        assert params1["apikey"] != params2["apikey"]
        assert params1["hash"] != params2["hash"]
        assert params1["ts"] == params2["ts"]  # Same timestamp

    def test_generate_auth_params_hash_format(self):
        """Test that the generated hash is a valid MD5 hash."""
        public_key = "test_public_key"
        private_key = "test_private_key"

        with patch("time.time", return_value=1234567890):
            params = generate_auth_params(public_key, private_key)

        # MD5 hash should be 32 characters long and contain only hex characters
        hash_value = params["hash"]
        assert len(hash_value) == 32
        assert all(c in "0123456789abcdef" for c in hash_value)

    def test_generate_auth_params_consistency(self):
        """Test that the same inputs generate the same hash."""
        public_key = "test_public_key"
        private_key = "test_private_key"

        with patch("time.time", return_value=1234567890):
            params1 = generate_auth_params(public_key, private_key)
            params2 = generate_auth_params(public_key, private_key)

        assert params1["hash"] == params2["hash"]
        assert params1["ts"] == params2["ts"]
        assert params1["apikey"] == params2["apikey"]
