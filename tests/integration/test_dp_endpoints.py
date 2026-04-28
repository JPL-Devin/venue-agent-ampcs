"""Integration tests for data product endpoints."""
import json
from unittest.mock import patch


class TestDp:
    def test_dp_returns_200(self, client, auth_headers):
        response = client.request('GET', '/api/v3/dp',
            data=json.dumps({
                'sessionId': 1,
                'timeout': 60,
            }),
            headers=auth_headers)
        assert response.status_code == 200

    def test_dp_empty_results(self, client, auth_headers):
        """Returns 200 with empty list when no data products match."""
        with patch('core.venue_core.get_dp', return_value=[]):
            response = client.request('GET', '/api/v3/dp',
                data=json.dumps({
                    'sessionId': 1,
                    'timeout': 60,
                }),
                headers=auth_headers)
            assert response.status_code == 200
            assert response.json() == []

    def test_dp_with_filters(self, client, auth_headers):
        """Query data products with APID and status filters."""
        filtered_dp = [
            {
                'sessionId': 1, 'vcId': 0, 'dpStatus': 'COMPLETE',
                'apId': 37, 'apIdProductType': 'DP_EVR_REC_ACT_LOW',
                'filePath': '/tmp/dp/test.dat', 'fileSize': 1024,
                'creationTime': '2024-01-01T00:00:00.000Z',
                'sclk': '0000000001.000',
                'ert': '2024-01-01T00:00:00.000Z',
                'scet': '2024-01-01T00:00:00.000Z',
            },
        ]
        with patch('core.venue_core.get_dp', return_value=filtered_dp):
            response = client.request('GET', '/api/v3/dp',
                data=json.dumps({
                    'sessionId': 1,
                    'dpStatus': 'COMPLETE',
                    'apIds': [37],
                    'timeout': 60,
                }),
                headers=auth_headers)
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]['apId'] == 37
            assert data[0]['dpStatus'] == 'COMPLETE'
