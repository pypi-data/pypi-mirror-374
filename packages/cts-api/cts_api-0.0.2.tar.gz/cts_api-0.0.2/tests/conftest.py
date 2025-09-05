import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import ClientSession


@pytest.fixture
def mock_session():
    """Mock aiohttp client session."""
    with patch("aiohttp.ClientSession", autospec=True) as mock_session:
        mock_session_instance = mock_session.return_value
        mock_session_instance.request = MagicMock()
        mock_session_instance.request.return_value = AsyncMock()
        yield mock_session_instance


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
