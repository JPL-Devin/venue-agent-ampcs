"""Integration tests for custom script endpoints."""
import json


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


class TestScriptStatus:
    def test_script_status_returns_200(self, client, auth_headers):
        response = client.request('GET', '/api/v3/custom_script/status',
            content=json.dumps({
                'scriptRunId': 'test-123',
            }),
            headers=auth_headers)
        assert response.status_code == 200


class TestScriptHalt:
    def test_script_halt_returns_204(self, client, auth_headers):
        response = client.post('/api/v3/custom_script/halt',
            json={
                'scriptRunId': 'test-123',
            },
            headers=auth_headers)
        assert response.status_code == 204
