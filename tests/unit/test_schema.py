"""Unit tests for core/schema.py Pydantic model validation."""
import pytest
from pydantic import ValidationError

from core.schema import (
    MtakStartBodyModel,
    FswCmdBodyModel,
    EvrRtBodyModel,
    HealthStatus,
    HealthStatusEnum,
    ErrorResponse,
)


class TestMtakStartBodyModel:
    def test_valid_input(self):
        model = MtakStartBodyModel(sessionIds=[1, 2])
        assert model.sessionIds == [1, 2]
        assert model.timeout == 30  # default
        assert model.defaultCmdString.value == 'AB'  # default

    def test_invalid_session_ids_type(self):
        with pytest.raises(ValidationError):
            MtakStartBodyModel(sessionIds="not-a-list")

    def test_timeout_below_minimum(self):
        with pytest.raises(ValidationError):
            MtakStartBodyModel(sessionIds=[1], timeout=10)

    def test_timeout_at_minimum(self):
        model = MtakStartBodyModel(sessionIds=[1], timeout=25)
        assert model.timeout == 25


class TestFswCmdBodyModel:
    def test_valid_input(self):
        model = FswCmdBodyModel(
            sessionId=1,
            commandString='CMD_NO_OP'
        )
        assert model.sessionId == 1
        assert model.commandString == 'CMD_NO_OP'
        assert model.validate_ is True  # default

    def test_alias_validate_works(self):
        model = FswCmdBodyModel(**{
            'sessionId': 1,
            'commandString': 'CMD_NO_OP',
            'validate': False
        })
        assert model.validate_ is False


class TestEvrRtBodyModel:
    def test_required_fields(self):
        model = EvrRtBodyModel(
            sessionId=1,
            startTime='2024-001T12:00:00',
            endTime='2024-001T13:00:00'
        )
        assert model.sessionId == 1
        assert model.startTime == '2024-001T12:00:00'
        assert model.endTime == '2024-001T13:00:00'

    def test_missing_required_field(self):
        with pytest.raises(ValidationError):
            EvrRtBodyModel(sessionId=1)


class TestHealthStatus:
    def test_enum_values(self):
        assert HealthStatusEnum.OK.value == 'OK'
        assert HealthStatusEnum.ERROR.value == 'ERROR'
        assert HealthStatusEnum.UNKNOWN.value == 'UNKNOWN'

    def test_model_creation(self):
        model = HealthStatus(status=HealthStatusEnum.OK, message='')
        assert model.status == HealthStatusEnum.OK


class TestErrorResponse:
    def test_default_message(self):
        model = ErrorResponse()
        assert model.message == ''

    def test_custom_message(self):
        model = ErrorResponse(message='Something went wrong')
        assert model.message == 'Something went wrong'
