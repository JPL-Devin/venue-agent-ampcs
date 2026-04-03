"""Integration tests for EVR endpoints."""
import json


class TestEvrRealtime:
    def test_evr_realtime_returns_200(self, client, auth_headers):
        response = client.request('GET', '/api/v3/evr/realtime',
            content=json.dumps({
                'sessionId': 1,
                'startTime': '2024-001T12:00:00',
                'endTime': '2024-001T13:00:00',
                'timeout': 60,
            }),
            headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestEvrRealtimeMulti:
    def test_evr_realtime_multi_returns_200(self, client, auth_headers):
        response = client.request('GET', '/api/v3/evr/realtime_multi',
            content=json.dumps({
                'sessionId': 1,
                'evrNames': ['EVR_TEST'],
                'startTime': '2024-001T12:00:00',
                'endTime': '2024-001T13:00:00',
                'timeout': 60,
            }),
            headers=auth_headers)
        assert response.status_code == 200


class TestEvrChill:
    def test_evr_chill_returns_200(self, client, auth_headers):
        response = client.request('GET', '/api/v3/evr/chill',
            content=json.dumps({
                'sessionId': 1,
                'timeout': 60,
            }),
            headers=auth_headers)
        assert response.status_code == 200


class TestEvrChillMulti:
    def test_evr_chill_multi_returns_200(self, client, auth_headers):
        response = client.request('GET', '/api/v3/evr/chill_multi',
            content=json.dumps({
                'sessionId': 1,
                'timeout': 60,
            }),
            headers=auth_headers)
        assert response.status_code == 200
