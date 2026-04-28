"""Integration tests for custom script endpoints."""
import json
from unittest.mock import patch, MagicMock


class TestScriptStart:
    def test_script_start_returns_200(self, client, auth_headers):
        response = client.post('/api/v3/custom_script/start',
            json={
                'scriptName': 'test_script',
                'scriptPath': 'test/test_script.py',
                'scriptHash': 'abc123',
                'inputs': {},
                'outputs': {},
            },
            headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert 'scriptRunId' in data

    def test_script_start_bad_path(self, client, auth_headers):
        """Returns 400 when script path does not exist."""
        with patch('core.venue_core.start_custom_script',
                   side_effect=Exception('Custom script cannot be found: /tmp/scripts/nonexistent.py')):
            response = client.post('/api/v3/custom_script/start',
                json={
                    'scriptName': 'bad_script',
                    'scriptPath': 'nonexistent.py',
                    'scriptHash': 'abc123',
                    'inputs': {},
                    'outputs': {},
                },
                headers=auth_headers)
            assert response.status_code == 400
            data = response.json()
            assert 'message' in data
            assert 'Failed to start a custom script' in data['message']

    def test_script_start_bad_hash(self, client, auth_headers):
        """Returns 400 when script hash does not match."""
        with patch('core.venue_core.start_custom_script',
                   side_effect=Exception('File hash input (wronghash) did not match the file hash: abc123def456')):
            response = client.post('/api/v3/custom_script/start',
                json={
                    'scriptName': 'test_script',
                    'scriptPath': 'test/test_script.py',
                    'scriptHash': 'wronghash',
                    'inputs': {},
                    'outputs': {},
                },
                headers=auth_headers)
            assert response.status_code == 400
            data = response.json()
            assert 'message' in data
            assert 'Failed to start a custom script' in data['message']


class TestScriptStatus:
    def test_script_status_returns_200(self, client, auth_headers):
        response = client.request('GET', '/api/v3/custom_script/status',
            data=json.dumps({
                'scriptRunId': 'test-123',
            }),
            headers=auth_headers)
        assert response.status_code == 200

    def test_script_status_missing_run_id(self, client, auth_headers):
        """Returns 400 when scriptRunId is missing from body."""
        response = client.request('GET', '/api/v3/custom_script/status',
            data=json.dumps({}),
            headers=auth_headers)
        assert response.status_code == 400

    def test_script_status_nonexistent_run_id(self, client, auth_headers):
        """Returns 400 when scriptRunId does not correspond to a running script."""
        with patch('core.venue_core.get_custom_script_status',
                   side_effect=Exception('Script run not found: nonexistent-id')):
            response = client.request('GET', '/api/v3/custom_script/status',
                data=json.dumps({
                    'scriptRunId': 'nonexistent-id',
                }),
                headers=auth_headers)
            assert response.status_code == 400
            data = response.json()
            assert 'message' in data
            assert 'Failed to get the status of custom script' in data['message']


class TestScriptHalt:
    def test_script_halt_returns_204(self, client, auth_headers):
        response = client.post('/api/v3/custom_script/halt',
            json={
                'scriptRunId': 'test-123',
            },
            headers=auth_headers)
        assert response.status_code == 204

    def test_script_halt_nonexistent_run_id(self, client, auth_headers):
        """Returns 400 when trying to halt a nonexistent script run."""
        with patch('core.venue_core.halt_custom_script',
                   side_effect=Exception('Script run not found: nonexistent-id')):
            response = client.post('/api/v3/custom_script/halt',
                json={
                    'scriptRunId': 'nonexistent-id',
                },
                headers=auth_headers)
            assert response.status_code == 400
            data = response.json()
            assert 'message' in data
            assert 'Failed to halt custom script' in data['message']
