"""Integration tests for EHA endpoints."""
import json


class TestEhaRealtime:
    def test_eha_realtime_returns_200(self, client, auth_headers):
        response = client.request('GET', '/api/v3/eha/realtime',
            content=json.dumps({
                'sessionId': 1,
                'channelId': 'CH-0001',
                'startTime': '2024-001T12:00:00',
                'endTime': '2024-001T13:00:00',
                'timeout': 60,
            }),
            headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestEhaRealtimeMulti:
    def test_eha_realtime_multi_returns_200(self, client, auth_headers):
        response = client.request('GET', '/api/v3/eha/realtime_multi',
            content=json.dumps({
                'sessionId': 1,
                'channelIds': ['CH-0001'],
                'startTime': '2024-001T12:00:00',
                'endTime': '2024-001T13:00:00',
                'timeout': 60,
            }),
            headers=auth_headers)
        assert response.status_code == 200


class TestEhaChill:
    def test_eha_chill_returns_200(self, client, auth_headers):
        response = client.request('GET', '/api/v3/eha/chill',
            content=json.dumps({
                'sessionId': 1,
                'channelIds': ['CH-0001'],
                'timeout': 60,
            }),
            headers=auth_headers)
        assert response.status_code == 200


class TestEhaChillMulti:
    def test_eha_chill_multi_returns_200(self, client, auth_headers):
        response = client.request('GET', '/api/v3/eha/chill_multi',
            content=json.dumps({
                'sessionId': 1,
                'channelIds': ['CH-0001'],
                'timeout': 60,
            }),
            headers=auth_headers)
        assert response.status_code == 200
