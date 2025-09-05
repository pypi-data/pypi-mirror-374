"""Class to communicate with the Diagral e-one API."""

from datetime import datetime, timedelta
import logging
import ssl
from typing import Any, Optional

from aiohttp import ClientConnectorError, ClientResponseError, ClientSession
import aiohttp

from cts_api.requests import VehicleMode
from cts_api.utils import timedelta_isoformat

from .responses import (
    ErrorResponse,
    GeneralMessageResponse,
    LinesDiscoveryResponse,
    StopMonitoringResponse,
    StopPointsDiscoveryResponse,
)

from .const import (
    HTTP_CALL_TIMEOUT,
    RESOURCE_GENERAL_MESSAGE,
    RESOURCE_LINES_DISCOVERY,
    RESOURCE_STOP_MONITORING,
    RESOURCE_STOPPOINTS_DISCOVERY,
)
from .exceptions import (
    ApiConnectionError,
    BadRequestError,
    CtsError,
    InvalidTokenError,
    TechnicalError,
    TooManyRequestsError,
)

_LOGGER = logging.getLogger(__name__)


class CtsApi:
    """CTS API class."""

    def __init__(self, token: str, session: Optional[ClientSession]) -> None:
        """Initialize the object."""
        self.session: Optional[ClientSession] = session
        self.token = token

    async def api_request(self, method: str, url: str, data: Optional[Any] = None):
        """Make an API request."""
        if self.session is None:
            session = ClientSession()
        else:
            session = self.session

        basic_auth = aiohttp.BasicAuth(self.token, "")
        error_response = ErrorResponse(None)
        response_json = None

        params = {}
        if data:
            for k, v in data.items():
                if v is not None:
                    if isinstance(v, bool):
                        params[k] = str(v).lower()
                    else:
                        params[k] = v
        else:
            params = None

        try:
            async with session.request(
                method,
                url,
                auth=basic_auth,
                params=params,
                raise_for_status=False,
                timeout=HTTP_CALL_TIMEOUT,
            ) as response:
                if response.ok:
                    response_json = await response.json()
                else:
                    error_response = (
                        ErrorResponse.from_dict(await response.json())
                        if response.content_type == "application/json"
                        else error_response
                    )
                    response.raise_for_status()
        except ClientConnectorError as err:
            raise ApiConnectionError(err) from err
        except ClientResponseError as err:
            if err.status == 400:  # Bad request
                raise BadRequestError(error_response.message or err) from err
            if err.status == 401:  # Unauthorized
                raise InvalidTokenError(error_response.message or err) from err
            if err.status == 429:  # Too many requests
                raise TooManyRequestsError(error_response.message or err) from err
            if err.status == 500:  # Technical error
                raise TechnicalError(error_response.message or err) from err
            # Generic exception
            raise CtsError(error_response.message or err) from err
        finally:
            if self.session is None:
                await session.close()

        return response_json

    async def general_messages(
        self,
        requestor_ref: Optional[str] = None,
        message_identfier: Optional[str] = None,
        info_channel_ref: Optional[list[str]] = None,
        line_ref: Optional[list[str]] = None,
        impacted_line_ref: Optional[list[str]] = None,
    ) -> GeneralMessageResponse:
        """Returns messages about traffic, services, commercial information, etc."""
        url = RESOURCE_GENERAL_MESSAGE
        data = {
            "RequestorRef": requestor_ref,
            "MessageIdentifier": message_identfier,
            "InfoChannelRef": ",".join(info_channel_ref or []),
            "LineRef": ",".join(line_ref or []),
            "ImpactedLineRef": ",".join(impacted_line_ref or []),
        }
        response_json = await self.api_request("get", url, data)

        _LOGGER.debug("GET 'general-messages' response: %s", response_json)

        return GeneralMessageResponse.from_dict(response_json)

    async def lines_discovery(
        self,
        requestor_ref: Optional[str] = None,
        message_identifier: Optional[str] = None,
    ) -> LinesDiscoveryResponse:
        """Returns a list of all lines."""
        url = RESOURCE_LINES_DISCOVERY
        data = {"RequestorRef": requestor_ref, "MessageIdentifier": message_identifier}

        response_json = await self.api_request("get", url, data)

        _LOGGER.debug("GET 'lines-discovery' response: %s", response_json)

        return LinesDiscoveryResponse.from_dict(response_json)

    async def stoppoints_discovery(
        self,
        requestor_ref: Optional[str] = None,
        message_identifier: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        distance: Optional[int] = None,
        include_lines_destinations: Optional[bool] = None,
        stop_code: Optional[str] = None,
    ) -> StopPointsDiscoveryResponse:
        """Returns a list of stop points."""
        url = RESOURCE_STOPPOINTS_DISCOVERY
        data = {
            "RequestorRef": requestor_ref,
            "MessageIdentifier": message_identifier,
            "latitude": latitude,
            "longitude": longitude,
            "distance": distance,
            "includeLinesDestinations": include_lines_destinations,
            "stopCode": stop_code,
        }

        response_json = await self.api_request("get", url, data)

        _LOGGER.debug("GET 'stoppoints-discovery' response: %s", response_json)

        return StopPointsDiscoveryResponse.from_dict(response_json)

    async def stop_monitoring(
        self,
        monitoring_ref: str,
        requestor_ref: Optional[str] = None,
        message_identifier: Optional[str] = None,
        vehicle_mode: Optional[VehicleMode] = VehicleMode.UNDEFINED,
        preview_interval: Optional[timedelta] = timedelta(hours=1, minutes=30),
        start_time: Optional[datetime] = None,
        line_ref: Optional[str] = None,
        direction_ref: Optional[str] = None,
        maximum_stop_visits: Optional[int] = 3,
        minimum_stop_visits_per_line: Optional[int] = 3,
        include_general_message: Optional[bool] = None,
        include_fluo67: Optional[bool] = False,
    ) -> StopMonitoringResponse:
        """Provides a stop-centric view of VEHICLE
        departures (realtime) at a list of designated stops."""

        url = RESOURCE_STOP_MONITORING
        data = {
            "MonitoringRef": monitoring_ref,
            "RequestorRef": requestor_ref,
            "MessageIdentifier": message_identifier,
            "VehicleMode": (
                vehicle_mode.name.lower() if vehicle_mode is not None else None
            ),
            "PreviewInternal": (
                timedelta_isoformat(preview_interval)
                if preview_interval is not None
                else None
            ),
            "StartTime": start_time.isoformat() if start_time is not None else None,
            "LineRef": line_ref,
            "DirectionRef": direction_ref,
            "MaximumStopVisits": maximum_stop_visits,
            "MinimumStopVisitsPerLine": minimum_stop_visits_per_line,
            "IncludeGeneralMessage": include_general_message,
            "IncludeFLUO67": include_fluo67,
        }

        response_json = await self.api_request("get", url, data)

        _LOGGER.debug("GET 'stop-monitoring' response: %s", response_json)

        return StopMonitoringResponse.from_dict(response_json)
