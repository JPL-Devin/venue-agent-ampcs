"""Integration tests for command endpoints."""
import pytest
from unittest.mock import patch


class TestFswCmd:
    def test_fsw_cmd_valid(self, client, auth_headers):
        response = client.post('/api/v3/cmd/fsw_cmd',
            json={
                'sessionId': 1,
                'commandString': 'CMD_NO_OP',
                'validate': False,
                'stringSelection': 'DEFAULT',
                'timeout': 10,
            },
            headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert 'cmdRequested' in data
        assert 'dispatchTime' in data

    def test_fsw_cmd_error(self, client, auth_headers, mock_venue_core):
        mock_venue_core['core.venue_core.core_send_fsw_cmd'].side_effect = Exception('cmd failed')
        response = client.post('/api/v3/cmd/fsw_cmd',
            json={
                'sessionId': 1,
                'commandString': 'CMD_NO_OP',
                'validate': False,
                'stringSelection': 'DEFAULT',
                'timeout': 10,
            },
            headers=auth_headers)
        assert response.status_code == 400


class TestHwCmd:
    def test_hw_cmd_valid(self, client, auth_headers):
        response = client.post('/api/v3/cmd/hw_cmd',
            json={
                'sessionId': 1,
                'commandStem': 'HW_CMD_NO_OP',
                'stringSelection': 'DEFAULT',
                'timeout': 10,
            },
            headers=auth_headers)
        assert response.status_code == 200


class TestSseCmd:
    def test_sse_cmd_valid(self, client, auth_headers):
        response = client.post('/api/v3/cmd/sse',
            json={
                'sessionId': 1,
                'commandString': 'SSE_CMD_TEST',
                'timeout': 10,
            },
            headers=auth_headers)
        assert response.status_code == 200


class TestBinaryFile:
    def test_binary_file_valid(self, client, auth_headers):
        response = client.post('/api/v3/cmd/binary_file',
            json={
                'sessionId': 1,
                'sourceFilePath': '/tmp/test.bin',
                'targetFilePath': '/eng1/test.bin',
                'overwrite': True,
                'fileType': 0,
                'stringSelection': 'DEFAULT',
                'timeout': 10,
            },
            headers=auth_headers)
        assert response.status_code == 200


class TestScmf:
    def test_scmf_valid(self, client, auth_headers):
        response = client.post('/api/v3/cmd/scmf',
            json={
                'sessionId': 1,
                'filePath': '/tmp/test.scmf',
                'disableChecks': False,
                'timeout': 10,
            },
            headers=auth_headers)
        assert response.status_code == 200
