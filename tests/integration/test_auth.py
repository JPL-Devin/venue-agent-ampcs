"""Integration tests for authentication and authorization."""
import json
import pytest


class TestAuthRequired:
    def test_mtak_start_no_auth_returns_401(self, client):
        """Endpoints other than /health should require auth."""
        response = client.post('/api/v3/mtak/start',
            json={'sessionIds': [1], 'timeout': 30, 'defaultCmdString': 'AB'})
        assert response.status_code == 401

    def test_fsw_cmd_no_auth_returns_401(self, client):
        response = client.post('/api/v3/cmd/fsw_cmd',
            json={
                'sessionId': 1,
                'commandString': 'CMD_NO_OP',
                'validate': False,
                'stringSelection': 'DEFAULT',
                'timeout': 10,
            })
        assert response.status_code == 401

    def test_evr_realtime_no_auth_returns_401(self, client):
        response = client.request('GET', '/api/v3/evr/realtime',
            data=json.dumps({
                'sessionId': 1,
                'startTime': '2024-001T12:00:00',
                'endTime': '2024-001T13:00:00',
            }),
            headers={'Content-Type': 'application/json'})
        assert response.status_code == 401


class TestInsufficientScopes:
    def test_mtak_start_no_execute_scope_returns_403(self, client, no_scope_headers):
        response = client.post('/api/v3/mtak/start',
            json={'sessionIds': [1], 'timeout': 30, 'defaultCmdString': 'AB'},
            headers=no_scope_headers)
        assert response.status_code == 403

    def test_fsw_cmd_no_execute_scope_returns_403(self, client, no_scope_headers):
        response = client.post('/api/v3/cmd/fsw_cmd',
            json={
                'sessionId': 1,
                'commandString': 'CMD_NO_OP',
                'validate': False,
                'stringSelection': 'DEFAULT',
                'timeout': 10,
            },
            headers=no_scope_headers)
        assert response.status_code == 403


class TestHealthNoAuth:
    def test_health_works_without_auth(self, client):
        response = client.get('/api/v3/health')
        assert response.status_code == 200
        assert response.json()['status'] == 'OK'
