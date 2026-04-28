"""
Integration test conftest - provides TestClient and mocked venue_core fixtures.
"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock
import jwt
import time

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# Ensure repo root is on sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


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


def _make_token(scopes=None):
    """Create a valid JWT token for testing."""
    iat = int(time.time()) - 60
    exp = iat + 3600
    payload = {
        'scopes': scopes if scopes is not None else ['execute:wsts'],
        'exp': exp,
        'iat': iat,
        'username': 'testuser',
    }
    return jwt.encode(payload, PRIVATE_PEM, algorithm='RS256')


SAMPLE_EVR_LIST = [
    {
        'evrName': 'EVR_TEST',
        'sessionId': 1,
        'vcId': 0,
        'eventId': 100,
        'evrLevel': 'ACTIVITY',
        'fromSSE': False,
        'evrMessage': 'Test message',
        'evrModule': 'TEST',
        'sclk': '0000000001.000',
        'ert': '2024-01-01T00:00:00.000Z',
        'scet': '2024-01-01T00:00:00.000Z',
        'isRecorded': False,
    }
]

SAMPLE_EHA_LIST = [
    {
        'dn': '42',
        'eu': 42.0,
        'channelId': 'CH-0001',
        'sessionId': 1,
        'vcId': 0,
        'channelName': 'TEST_CHANNEL',
        'channelType': 'FSW_REALTIME',
        'channelStatus': '',
        'sclk': '0000000001.000',
        'ert': '2024-01-01T00:00:00.000Z',
        'scet': '2024-01-01T00:00:00.000Z',
        'isRecorded': False,
        'dnAlarmState': '',
        'euAlarmState': '',
    }
]

SAMPLE_DP_LIST = [
    {
        'sessionId': 1,
        'vcId': 0,
        'dpStatus': 'COMPLETE',
        'apId': 37,
        'apIdProductType': 'DP_EVR_REC_ACT_LOW',
        'filePath': '/tmp/dp/test.dat',
        'fileSize': 1024,
        'creationTime': '2024-01-01T00:00:00.000Z',
        'sclk': '0000000001.000',
        'ert': '2024-01-01T00:00:00.000Z',
        'scet': '2024-01-01T00:00:00.000Z',
    }
]


@pytest.fixture(autouse=True)
def mock_venue_core():
    """Mock all venue_core functions that depend on AMPCS."""
    patches = {
        'core.venue_core.core_start_mtak': MagicMock(return_value=([1], '2024-01-01T00:00:00.000Z')),
        'core.venue_core.core_stop_mtak': MagicMock(return_value=''),
        'core.venue_core.core_send_fsw_cmd': MagicMock(return_value=('CMD_NO_OP', '2024-01-01T00:00:00.000Z')),
        'core.venue_core.core_send_hw_cmd': MagicMock(return_value=('HW_CMD', '2024-01-01T00:00:00.000Z')),
        'core.venue_core.core_send_sse_cmd': MagicMock(return_value=('SSE_CMD', '2024-01-01T00:00:00.000Z')),
        'core.venue_core.core_send_fsw_file': MagicMock(return_value=('file info', '2024-01-01T00:00:00.000Z')),
        'core.venue_core.core_send_scmf_file': MagicMock(return_value=('scmf info', '2024-01-01T00:00:00.000Z')),
        'core.venue_core.get_rt_evr': MagicMock(return_value=SAMPLE_EVR_LIST),
        'core.venue_core.get_rt_eha': MagicMock(return_value=SAMPLE_EHA_LIST),
        'core.venue_core.get_rt_evr_multi': MagicMock(return_value=SAMPLE_EVR_LIST),
        'core.venue_core.get_rt_eha_multi': MagicMock(return_value=SAMPLE_EHA_LIST),
        'core.venue_core.get_chill_evr': MagicMock(return_value=SAMPLE_EVR_LIST),
        'core.venue_core.get_chill_eha': MagicMock(return_value=SAMPLE_EHA_LIST),
        'core.venue_core.get_chill_evr_multi': MagicMock(return_value=SAMPLE_EVR_LIST),
        'core.venue_core.get_chill_eha_multi': MagicMock(return_value=SAMPLE_EHA_LIST),
        'core.venue_core.get_dp': MagicMock(return_value=SAMPLE_DP_LIST),
        'core.venue_core.start_custom_script': MagicMock(return_value={'scriptRunId': 'test-123'}),
        'core.venue_core.get_custom_script_status': MagicMock(return_value={
            'logfile_url': '',
            'logfile_path': '/tmp/cs/test.log',
            'custom_script_status': 'PASS',
            'custom_script_outputs': {'outputs': {}, 'output_array': [], 'entries': {}},
            'logfile_lines': [],
        }),
        'core.venue_core.halt_custom_script': MagicMock(return_value=None),
    }

    active_patches = {}
    for target, mock_obj in patches.items():
        p = patch(target, mock_obj)
        active_patches[target] = p.start()

    yield active_patches

    for p_target in patches:
        patch.stopall()
        break  # stopall stops all patches


@pytest.fixture(autouse=True)
def mock_auth():
    """Mock JWT auth to always succeed with valid scopes."""
    import utils
    with patch.object(utils, 'exec_venue_public_pem', PUBLIC_PEM):
        yield


@pytest.fixture
def auth_headers():
    """Return valid auth headers for testing."""
    token = _make_token(scopes=['execute:wsts'])
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }


@pytest.fixture
def no_scope_headers():
    """Return auth headers with no execute scopes."""
    token = _make_token(scopes=['read:only'])
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }


@pytest.fixture
def client():
    """Return a TestClient for the FastAPI app."""
    from starlette.testclient import TestClient
    from main import app
    return TestClient(app)
