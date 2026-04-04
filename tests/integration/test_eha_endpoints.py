"""Integration tests for EHA endpoints."""
import json
from unittest.mock import patch


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

    def test_eha_realtime_empty_results(self, client, auth_headers):
        """Returns 200 with empty list when no EHA data matches."""
        with patch('core.venue_core.get_rt_eha', return_value=[]):
            response = client.request('GET', '/api/v3/eha/realtime',
                content=json.dumps({
                    'sessionId': 1,
                    'channelId': 'CH-9999',
                    'startTime': '2024-001T12:00:00',
                    'endTime': '2024-001T13:00:00',
                    'timeout': 60,
                }),
                headers=auth_headers)
            assert response.status_code == 200
            assert response.json() == []


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

    def test_eha_realtime_multi_multiple_channels(self, client, auth_headers):
        """Query multiple channel IDs at once."""
        multi_eha = [
            {
                'dn': '42', 'eu': 42.0,
                'channelId': 'CH-0001', 'sessionId': 1, 'vcId': 0,
                'channelName': 'TEMP_SENSOR_1', 'channelType': 'FSW_REALTIME',
                'channelStatus': '',
                'sclk': '0000000001.000',
                'ert': '2024-01-01T00:00:00.000Z',
                'scet': '2024-01-01T00:00:00.000Z',
                'isRecorded': False, 'dnAlarmState': '', 'euAlarmState': '',
            },
            {
                'dn': '100', 'eu': 100.5,
                'channelId': 'CH-0002', 'sessionId': 1, 'vcId': 0,
                'channelName': 'TEMP_SENSOR_2', 'channelType': 'FSW_REALTIME',
                'channelStatus': '',
                'sclk': '0000000001.000',
                'ert': '2024-01-01T00:00:00.000Z',
                'scet': '2024-01-01T00:00:00.000Z',
                'isRecorded': False, 'dnAlarmState': '', 'euAlarmState': '',
            },
            {
                'dn': '255', 'eu': 3.3,
                'channelId': 'CH-0003', 'sessionId': 1, 'vcId': 0,
                'channelName': 'VOLTAGE_BUS', 'channelType': 'FSW_REALTIME',
                'channelStatus': '',
                'sclk': '0000000001.000',
                'ert': '2024-01-01T00:00:00.000Z',
                'scet': '2024-01-01T00:00:00.000Z',
                'isRecorded': False, 'dnAlarmState': '', 'euAlarmState': '',
            },
        ]
        with patch('core.venue_core.get_rt_eha_multi', return_value=multi_eha):
            response = client.request('GET', '/api/v3/eha/realtime_multi',
                content=json.dumps({
                    'sessionId': 1,
                    'channelIds': ['CH-0001', 'CH-0002', 'CH-0003'],
                    'startTime': '2024-001T12:00:00',
                    'endTime': '2024-001T13:00:00',
                    'timeout': 60,
                }),
                headers=auth_headers)
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 3
            channel_ids = [e['channelId'] for e in data]
            assert 'CH-0001' in channel_ids
            assert 'CH-0002' in channel_ids
            assert 'CH-0003' in channel_ids

    def test_eha_realtime_multi_empty_results(self, client, auth_headers):
        """Multi EHA query returns 200 with empty list when nothing matches."""
        with patch('core.venue_core.get_rt_eha_multi', return_value=[]):
            response = client.request('GET', '/api/v3/eha/realtime_multi',
                content=json.dumps({
                    'sessionId': 1,
                    'channelIds': ['NONEXISTENT_CH'],
                    'startTime': '2024-001T12:00:00',
                    'endTime': '2024-001T13:00:00',
                    'timeout': 60,
                }),
                headers=auth_headers)
            assert response.status_code == 200
            assert response.json() == []


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

    def test_eha_chill_empty_results(self, client, auth_headers):
        """Chill EHA query returns 200 with empty list when no data matches."""
        with patch('core.venue_core.get_chill_eha', return_value=[]):
            response = client.request('GET', '/api/v3/eha/chill',
                content=json.dumps({
                    'sessionId': 1,
                    'channelIds': ['CH-9999'],
                    'timeout': 60,
                }),
                headers=auth_headers)
            assert response.status_code == 200
            assert response.json() == []


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

    def test_eha_chill_multi_multiple_channels(self, client, auth_headers):
        """Chill multi query with multiple channel IDs."""
        multi_eha = [
            {
                'dn': '42', 'eu': 42.0,
                'channelId': 'CH-0001', 'sessionId': 1, 'vcId': 0,
                'channelName': 'TEMP_SENSOR_1', 'channelType': 'FSW_REALTIME',
                'channelStatus': '',
                'sclk': '0000000001.000',
                'ert': '2024-01-01T00:00:00.000Z',
                'scet': '2024-01-01T00:00:00.000Z',
                'isRecorded': False, 'dnAlarmState': '', 'euAlarmState': '',
            },
            {
                'dn': '200', 'eu': 25.0,
                'channelId': 'CH-0010', 'sessionId': 1, 'vcId': 0,
                'channelName': 'PRESSURE_1', 'channelType': 'FSW_REALTIME',
                'channelStatus': '',
                'sclk': '0000000001.000',
                'ert': '2024-01-01T00:00:00.000Z',
                'scet': '2024-01-01T00:00:00.000Z',
                'isRecorded': False, 'dnAlarmState': '', 'euAlarmState': '',
            },
        ]
        with patch('core.venue_core.get_chill_eha_multi', return_value=multi_eha):
            response = client.request('GET', '/api/v3/eha/chill_multi',
                content=json.dumps({
                    'sessionId': 1,
                    'channelIds': ['CH-0001', 'CH-0010'],
                    'timeout': 60,
                }),
                headers=auth_headers)
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            channel_ids = [e['channelId'] for e in data]
            assert 'CH-0001' in channel_ids
            assert 'CH-0010' in channel_ids

    def test_eha_chill_multi_empty_results(self, client, auth_headers):
        """Chill multi query returns 200 with empty list when nothing matches."""
        with patch('core.venue_core.get_chill_eha_multi', return_value=[]):
            response = client.request('GET', '/api/v3/eha/chill_multi',
                content=json.dumps({
                    'sessionId': 1,
                    'channelIds': ['NONEXISTENT'],
                    'timeout': 60,
                }),
                headers=auth_headers)
            assert response.status_code == 200
            assert response.json() == []
