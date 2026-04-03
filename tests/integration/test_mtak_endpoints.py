"""Integration tests for MTAK endpoints."""
import pytest
from unittest.mock import patch


class TestMtakStart:
    def test_start_valid_body(self, client, auth_headers):
        response = client.post('/api/v3/mtak/start',
            json={'sessionIds': [1], 'timeout': 30, 'defaultCmdString': 'AB'},
            headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert 'sessionIds' in data
        assert 'startTime' in data

    def test_start_invalid_body_missing_session_ids(self, client, auth_headers):
        response = client.post('/api/v3/mtak/start',
            json={},
            headers=auth_headers)
        assert response.status_code == 400

    def test_start_error_raises_400(self, client, auth_headers, mock_venue_core):
        mock_venue_core['core.venue_core.core_start_mtak'].side_effect = Exception('MTAK failed')
        response = client.post('/api/v3/mtak/start',
            json={'sessionIds': [1], 'timeout': 30, 'defaultCmdString': 'AB'},
            headers=auth_headers)
        assert response.status_code == 400


class TestMtakShutdown:
    def test_shutdown_returns_204(self, client, auth_headers):
        response = client.post('/api/v3/mtak/shutdown', headers=auth_headers)
        assert response.status_code == 204
