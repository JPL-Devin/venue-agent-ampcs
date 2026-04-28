"""Unit tests for utils.py functions."""
import pytest
from unittest.mock import patch, MagicMock
import jwt
import time
import os

# Generate test RSA keypair for JWT testing
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def _generate_test_keypair():
    """Generate an RSA keypair for testing."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode('utf-8')
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode('utf-8')
    return private_pem, public_pem


PRIVATE_PEM, PUBLIC_PEM = _generate_test_keypair()


def _make_token(scopes=None, expired=False):
    """Create a JWT token for testing."""
    iat = int(time.time()) - 60
    exp = iat - 3600 if expired else iat + 3600
    payload = {
        'scopes': scopes or ['execute:wsts'],
        'exp': exp,
        'iat': iat,
        'username': 'testuser',
    }
    return jwt.encode(payload, PRIVATE_PEM, algorithm='RS256')


class TestHasPermission:
    def test_valid_scope(self):
        from utils import has_permission
        jwt_decoded = {'scopes': ['execute:wsts']}
        assert has_permission(jwt_decoded) is True

    def test_invalid_scope(self):
        from utils import has_permission
        jwt_decoded = {'scopes': ['read:only']}
        assert has_permission(jwt_decoded) is False

    def test_dict_style_scopes_r14_3(self):
        from utils import has_permission
        jwt_decoded = {'scopes': [{'scope': 'execute:testbed', 'venue_group_id': 'group1'}]}
        assert has_permission(jwt_decoded) is True

    def test_dict_style_scopes_invalid(self):
        from utils import has_permission
        jwt_decoded = {'scopes': [{'scope': 'read:only', 'venue_group_id': 'group1'}]}
        assert has_permission(jwt_decoded) is False

    def test_empty_scopes(self):
        from utils import has_permission
        jwt_decoded = {'scopes': []}
        assert has_permission(jwt_decoded) is False

    def test_no_scopes_key(self):
        from utils import has_permission
        jwt_decoded = {}
        assert has_permission(jwt_decoded) is False

    def test_multiple_scopes_one_valid(self):
        from utils import has_permission
        jwt_decoded = {'scopes': ['read:only', 'execute:sit']}
        assert has_permission(jwt_decoded) is True


class TestGetDecodedToken:
    def test_valid_bearer_token(self):
        import utils
        # Patch the public key used by the module
        token = _make_token(scopes=['execute:wsts'])
        with patch.object(utils, 'exec_venue_public_pem', PUBLIC_PEM):
            result = utils.get_decoded_token(f'Bearer {token}')
            assert result['username'] == 'testuser'
            assert 'execute:wsts' in result['scopes']

    def test_missing_header(self):
        import utils
        with pytest.raises(Exception, match='Authorization header was not provided'):
            utils.get_decoded_token(None)

    def test_malformed_header(self):
        import utils
        with pytest.raises(Exception, match='Authorization header should be of format'):
            utils.get_decoded_token('InvalidFormat')
