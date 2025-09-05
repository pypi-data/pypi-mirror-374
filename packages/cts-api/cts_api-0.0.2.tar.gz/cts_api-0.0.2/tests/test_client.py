"""Tests for the CTS API client."""
import json
from pathlib import Path

import pytest
from aiohttp import ClientResponseError

from cts_api.client import CtsApi
from cts_api.exceptions import BadRequestError, CtsError, InvalidTokenError, TechnicalError, TooManyRequestsError


def load_fixture(filename):
    """Load a fixture."""
    return json.loads((Path(__file__).parent / "fixtures" / filename).read_text())


@pytest.mark.asyncio
async def test_lines_discovery(mock_session):
    """Test lines_discovery."""
    mock_response = mock_session.request.return_value.__aenter__.return_value
    mock_response.ok = True
    mock_response.json.return_value = load_fixture("lines_discovery.json")
    mock_response.status = 200

    api = CtsApi("test_token", mock_session)
    response = await api.lines_discovery()

    assert response is not None
    assert response.lines_delivery is not None
    assert len(response.lines_delivery.annotated_line_refs) == 1
    assert response.lines_delivery.annotated_line_refs[0].line_name == "Line 1"


@pytest.mark.asyncio
async def test_stoppoints_discovery(mock_session):
    """Test stoppoints_discovery."""
    mock_response = mock_session.request.return_value.__aenter__.return_value
    mock_response.ok = True
    mock_response.json.return_value = load_fixture("stoppoints_discovery.json")
    mock_response.status = 200

    api = CtsApi("test_token", mock_session)
    response = await api.stoppoints_discovery()

    assert response is not None
    assert response.stop_points_delivery is not None
    assert len(response.stop_points_delivery.annotated_stop_point_ref) == 1
    assert response.stop_points_delivery.annotated_stop_point_ref[0].stop_name == "Stop 1"


@pytest.mark.asyncio
async def test_stop_monitoring(mock_session):
    """Test stop_monitoring."""
    mock_response = mock_session.request.return_value.__aenter__.return_value
    mock_response.ok = True
    mock_response.json.return_value = load_fixture("stop_monitoring.json")
    mock_response.status = 200

    api = CtsApi("test_token", mock_session)
    response = await api.stop_monitoring("stop:1")

    assert response is not None
    assert response.service_delivery is not None
    assert len(response.service_delivery.stop_monitoring_delivery) == 1
    assert len(response.service_delivery.stop_monitoring_delivery[0].monitored_stop_visit) == 1
    assert response.service_delivery.stop_monitoring_delivery[0].monitored_stop_visit[0].monitoring_ref == "stop:1"


@pytest.mark.asyncio
async def test_general_messages(mock_session):
    """Test general_messages."""
    mock_response = mock_session.request.return_value.__aenter__.return_value
    mock_response.ok = True
    mock_response.json.return_value = load_fixture("general_messages.json")
    mock_response.status = 200

    api = CtsApi("test_token", mock_session)
    response = await api.general_messages()

    assert response is not None
    assert response.service_delivery is not None
    assert len(response.service_delivery.general_message_delivery) == 1
    assert len(response.service_delivery.general_message_delivery[0].info_message) == 1
    assert response.service_delivery.general_message_delivery[0].info_message[0].content.message[0].message_text[0].value == "Test message"


from unittest.mock import MagicMock


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status,exception",
    [
        (400, BadRequestError),
        (401, InvalidTokenError),
        (429, TooManyRequestsError),
        (500, TechnicalError),
        (502, CtsError),
    ],
)
async def test_api_errors(mock_session, status, exception):
    """Test API errors."""
    mock_response = mock_session.request.return_value.__aenter__.return_value
    mock_response.ok = False
    mock_response.status = status
    mock_response.content_type = "application/json"
    mock_response.json.return_value = {"error": "Test error"}

    mock_response.raise_for_status = MagicMock()
    mock_response.raise_for_status.side_effect = ClientResponseError(
        mock_response.request_info,
        mock_response.history,
        status=status,
        message="Test error",
    )

    api = CtsApi("test_token", mock_session)

    with pytest.raises(exception):
        await api.api_request("get", "https://fake.url")
