"""Constants for the CTS API."""

from typing import Final

BASE_URL = "https://api.cts-strasbourg.eu/v1/siri/2.0"
RESOURCE_GENERAL_MESSAGE = BASE_URL + "/general-message"
RESOURCE_LINES_DISCOVERY = BASE_URL + "/lines-discovery"
RESOURCE_STOPPOINTS_DISCOVERY = BASE_URL + "/stoppoints-discovery"
RESOURCE_STOP_MONITORING = BASE_URL + "/stop-monitoring"
HTTP_CALL_TIMEOUT: Final[int] = 10
