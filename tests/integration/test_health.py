"""Integration tests for the /health endpoint."""


class TestHealth:
    def test_health_returns_200(self, client):
        response = client.get('/api/v3/health')
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'OK'

    def test_health_no_auth_needed(self, client):
        """Health endpoint should work without auth headers."""
        response = client.get('/api/v3/health')
        assert response.status_code == 200
