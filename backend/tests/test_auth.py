"""
Tests for authentication
"""
import pytest
from app.services.auth_service import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_token,
)


class TestPasswordHashing:
    """Test password hashing"""

    def test_hash_creates_hash(self):
        """Should create a hash"""
        hash_val = get_password_hash("testpassword123")
        assert hash_val is not None
        assert hash_val != "testpassword123"

    def test_verify_correct_password(self):
        """Should verify correct password"""
        hash_val = get_password_hash("testpassword123")
        assert verify_password("testpassword123", hash_val) is True

    def test_verify_wrong_password(self):
        """Should reject wrong password"""
        hash_val = get_password_hash("testpassword123")
        assert verify_password("wrongpassword", hash_val) is False


class TestTokenCreation:
    """Test JWT token creation"""

    def test_create_token(self):
        """Should create token"""
        token = create_access_token({"sub": "testuser"})
        assert token is not None
        assert isinstance(token, str)

    def test_decode_token(self):
        """Should decode token"""
        token = create_access_token({"sub": "testuser"})
        token_data = decode_token(token)

        assert token_data is not None
        assert token_data.username == "testuser"

    def test_decode_invalid_token(self):
        """Should reject invalid token"""
        token_data = decode_token("invalid.token.here")
        assert token_data is None

    def test_decode_tampered_token(self):
        """Should reject tampered token"""
        token = create_access_token({"sub": "testuser"})
        tampered = token[:-5] + "xxxxx"
        token_data = decode_token(tampered)
        assert token_data is None