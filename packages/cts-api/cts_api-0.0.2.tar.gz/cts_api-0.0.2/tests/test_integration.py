"""API integration tests."""

import os

import pytest

from cts_api.client import CtsApi


@pytest.fixture
def api_token():
    """Get the API token from the environment."""
    token = os.environ.get("CTS_API_TOKEN")
    if not token:
        pytest.skip("CTS_API_TOKEN environment variable not set")
    return token


@pytest.mark.asyncio
@pytest.mark.integration
async def test_lines_discovery_call(api_token):
    """lines-discovery test"""
    cts_api = CtsApi(api_token, None)
    response = await cts_api.lines_discovery()
    assert response.lines_delivery.annotated_line_refs is not None
    assert response.lines_delivery.annotated_line_refs.__len__() > 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_stoppoints_discovery_call(api_token):
    """stoppoints-discovery test"""
    cts_api = CtsApi(api_token, None)
    response = await cts_api.stoppoints_discovery()
    assert response.stop_points_delivery.annotated_stop_point_ref is not None
    assert response.stop_points_delivery.annotated_stop_point_ref.__len__() > 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_stop_monitoring_call(api_token):
    """stop-monitoring test"""
    cts_api = CtsApi(api_token, None)
    response = await cts_api.stop_monitoring(monitoring_ref="610")
    assert response.service_delivery.stop_monitoring_delivery is not None
    assert response.service_delivery.stop_monitoring_delivery.__len__() > 0
    assert response.service_delivery.stop_monitoring_delivery[0].monitored_stop_visit is not None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_general_messages_call(api_token):
    """general-messages test"""
    cts_api = CtsApi(api_token, None)
    response = await cts_api.general_messages()
    assert response.service_delivery.general_message_delivery is not None
