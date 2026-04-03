"""Integration tests for data product endpoints."""
import json


class TestDp:
    def test_dp_returns_200(self, client, auth_headers):
        response = client.request('GET', '/api/v3/dp',
            content=json.dumps({
                'sessionId': 1,
                'timeout': 60,
            }),
            headers=auth_headers)
        assert response.status_code == 200
