"""Integration tests for EVR endpoints."""
import json
from unittest.mock import patch


class TestEvrRealtime:
    def test_evr_realtime_returns_200(self, client, auth_headers):
        response = client.request('GET', '/api/v3/evr/realtime',
            data=json.dumps({
                'sessionId': 1,
                'startTime': '2024-001T12:00:00',
                'endTime': '2024-001T13:00:00',
                'timeout': 60,
            }),
            headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_evr_realtime_empty_results(self, client, auth_headers):
        """Returns 200 with empty list when no EVRs match."""
        with patch('core.venue_core.get_rt_evr', return_value=[]):
            response = client.request('GET', '/api/v3/evr/realtime',
                data=json.dumps({
                    'sessionId': 1,
                    'startTime': '2024-001T12:00:00',
                    'endTime': '2024-001T13:00:00',
                    'timeout': 60,
                }),
                headers=auth_headers)
            assert response.status_code == 200
            assert response.json() == []


class TestEvrRealtimeMulti:
    def test_evr_realtime_multi_returns_200(self, client, auth_headers):
        response = client.request('GET', '/api/v3/evr/realtime_multi',
            data=json.dumps({
                'sessionId': 1,
                'evrNames': ['EVR_TEST'],
                'startTime': '2024-001T12:00:00',
                'endTime': '2024-001T13:00:00',
                'timeout': 60,
            }),
            headers=auth_headers)
        assert response.status_code == 200

    def test_evr_realtime_multi_multiple_evrs(self, client, auth_headers):
        """Query multiple EVR names at once."""
        multi_evrs = [
            {
                'evrName': 'EVR_CMD_RECEIVED',
                'sessionId': 1, 'vcId': 0, 'eventId': 100,
                'evrLevel': 'ACTIVITY', 'fromSSE': False,
                'evrMessage': 'Command received', 'evrModule': 'CMD',
                'sclk': '0000000001.000',
                'ert': '2024-01-01T00:00:00.000Z',
                'scet': '2024-01-01T00:00:00.000Z',
                'isRecorded': False,
            },
            {
                'evrName': 'EVR_CMD_EXECUTED',
                'sessionId': 1, 'vcId': 0, 'eventId': 101,
                'evrLevel': 'ACTIVITY', 'fromSSE': False,
                'evrMessage': 'Command executed', 'evrModule': 'CMD',
                'sclk': '0000000002.000',
                'ert': '2024-01-01T00:00:01.000Z',
                'scet': '2024-01-01T00:00:01.000Z',
                'isRecorded': False,
            },
            {
                'evrName': 'EVR_HEALTH_CHECK',
                'sessionId': 1, 'vcId': 0, 'eventId': 200,
                'evrLevel': 'DIAGNOSTIC', 'fromSSE': False,
                'evrMessage': 'Health check OK', 'evrModule': 'HEALTH',
                'sclk': '0000000003.000',
                'ert': '2024-01-01T00:00:02.000Z',
                'scet': '2024-01-01T00:00:02.000Z',
                'isRecorded': False,
            },
        ]
        with patch('core.venue_core.get_rt_evr_multi', return_value=multi_evrs):
            response = client.request('GET', '/api/v3/evr/realtime_multi',
                data=json.dumps({
                    'sessionId': 1,
                    'evrNames': ['EVR_CMD_RECEIVED', 'EVR_CMD_EXECUTED', 'EVR_HEALTH_CHECK'],
                    'startTime': '2024-001T12:00:00',
                    'endTime': '2024-001T13:00:00',
                    'timeout': 60,
                }),
                headers=auth_headers)
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 3
            names = [e['evrName'] for e in data]
            assert 'EVR_CMD_RECEIVED' in names
            assert 'EVR_CMD_EXECUTED' in names
            assert 'EVR_HEALTH_CHECK' in names

    def test_evr_realtime_multi_empty_results(self, client, auth_headers):
        """Multi EVR query returns 200 with empty list when nothing matches."""
        with patch('core.venue_core.get_rt_evr_multi', return_value=[]):
            response = client.request('GET', '/api/v3/evr/realtime_multi',
                data=json.dumps({
                    'sessionId': 1,
                    'evrNames': ['NONEXISTENT_EVR'],
                    'startTime': '2024-001T12:00:00',
                    'endTime': '2024-001T13:00:00',
                    'timeout': 60,
                }),
                headers=auth_headers)
            assert response.status_code == 200
            assert response.json() == []


class TestEvrChill:
    def test_evr_chill_returns_200(self, client, auth_headers):
        response = client.request('GET', '/api/v3/evr/chill',
            data=json.dumps({
                'sessionId': 1,
                'timeout': 60,
            }),
            headers=auth_headers)
        assert response.status_code == 200

    def test_evr_chill_empty_results(self, client, auth_headers):
        """Chill EVR query returns 200 with empty list when no EVRs match."""
        with patch('core.venue_core.get_chill_evr', return_value=[]):
            response = client.request('GET', '/api/v3/evr/chill',
                data=json.dumps({
                    'sessionId': 1,
                    'timeout': 60,
                }),
                headers=auth_headers)
            assert response.status_code == 200
            assert response.json() == []


class TestEvrChillMulti:
    def test_evr_chill_multi_returns_200(self, client, auth_headers):
        response = client.request('GET', '/api/v3/evr/chill_multi',
            data=json.dumps({
                'sessionId': 1,
                'timeout': 60,
            }),
            headers=auth_headers)
        assert response.status_code == 200

    def test_evr_chill_multi_multiple_evrs(self, client, auth_headers):
        """Chill multi query with multiple EVR names and event IDs."""
        multi_evrs = [
            {
                'evrName': 'EVR_FSW_BOOT',
                'sessionId': 1, 'vcId': 0, 'eventId': 1,
                'evrLevel': 'ACTIVITY', 'fromSSE': False,
                'evrMessage': 'FSW booted', 'evrModule': 'BOOT',
                'sclk': '0000000001.000',
                'ert': '2024-01-01T00:00:00.000Z',
                'scet': '2024-01-01T00:00:00.000Z',
                'isRecorded': False,
            },
            {
                'evrName': 'EVR_FSW_READY',
                'sessionId': 1, 'vcId': 0, 'eventId': 2,
                'evrLevel': 'ACTIVITY', 'fromSSE': False,
                'evrMessage': 'FSW ready', 'evrModule': 'BOOT',
                'sclk': '0000000002.000',
                'ert': '2024-01-01T00:00:01.000Z',
                'scet': '2024-01-01T00:00:01.000Z',
                'isRecorded': False,
            },
        ]
        with patch('core.venue_core.get_chill_evr_multi', return_value=multi_evrs):
            response = client.request('GET', '/api/v3/evr/chill_multi',
                data=json.dumps({
                    'sessionId': 1,
                    'evrNames': ['EVR_FSW_BOOT', 'EVR_FSW_READY'],
                    'eventIds': [1, 2],
                    'timeout': 60,
                }),
                headers=auth_headers)
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2

    def test_evr_chill_multi_empty_results(self, client, auth_headers):
        """Chill multi query returns 200 with empty list when nothing matches."""
        with patch('core.venue_core.get_chill_evr_multi', return_value=[]):
            response = client.request('GET', '/api/v3/evr/chill_multi',
                data=json.dumps({
                    'sessionId': 1,
                    'evrNames': ['NONEXISTENT'],
                    'timeout': 60,
                }),
                headers=auth_headers)
            assert response.status_code == 200
            assert response.json() == []
