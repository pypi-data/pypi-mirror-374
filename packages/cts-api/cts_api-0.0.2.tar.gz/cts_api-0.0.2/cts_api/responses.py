"""Api response models"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime

# region COMMON


@dataclass
class ErrorResponse:
    """Response when an error occured."""

    message: Optional[str]

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ErrorResponse":
        """Convert the dictionary to the response object."""
        return ErrorResponse(message=data.get("error", ""))


@dataclass
class PreviousCall:
    """CALL which has already been made in the MonitoredVehicleJourney"""

    stop_point_name: str
    stop_code: str
    order: int

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "PreviousCall":
        """Convert the dictionary to the response object."""
        return PreviousCall(
            stop_point_name=data.get("StopPointName", ""),
            stop_code=data.get("StopCode", ""),
            order=data.get("Order", 0),
        )


@dataclass
class OnwardCall:
    """CALL which has still to be made in the MonitoredVehicleJourney"""

    stop_point_name: str
    stop_code: str
    order: int
    expected_departure_time: Optional[datetime]
    expected_arrival_time: Optional[datetime]

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "OnwardCall":
        """Convert the dictionary to the response object."""

        expected_departure_time = data.get("ExpectedDepartureTime")
        expected_arrival_time = data.get("ExpectedArrivalTime")

        return OnwardCall(
            stop_point_name=data.get("StopPointName", ""),
            stop_code=data.get("StopCode", ""),
            order=data.get("Order", 0),
            expected_departure_time=(
                datetime.fromisoformat(expected_departure_time)
                if expected_departure_time is not None
                else None
            ),
            expected_arrival_time=(
                datetime.fromisoformat(expected_arrival_time)
                if expected_arrival_time is not None
                else None
            ),
        )


@dataclass
class ExtensionMonitoredCall:
    """Extension for the monitored call."""

    is_real_time: bool
    data_source: str
    experimentation: str

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ExtensionMonitoredCall":
        """Convert the dictionary to the response object."""
        return ExtensionMonitoredCall(
            is_real_time=data.get("IsRealTime", False),
            data_source=data.get("DataSource", ""),
            experimentation=data.get("Experimentation", ""),
        )


@dataclass
class MonitoredCall:
    """Monitored call."""

    stop_point_name: str
    stop_code: str
    order: int
    expected_departure_time: Optional[datetime]
    expected_arrival_time: Optional[datetime]
    extension: ExtensionMonitoredCall

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "MonitoredCall":
        """Convert the dictionary to the response object."""
        expected_departure_time = data.get("ExpectedDepartureTime")
        expected_arrival_time = data.get("ExpectedArrivalTime")

        return MonitoredCall(
            stop_point_name=data.get("StopPointName", ""),
            stop_code=data.get("StopCode", ""),
            order=data.get("Order", 0),
            expected_departure_time=(
                datetime.fromisoformat(expected_departure_time)
                if expected_departure_time is not None
                else None
            ),
            expected_arrival_time=(
                datetime.fromisoformat(expected_arrival_time)
                if expected_arrival_time is not None
                else None
            ),
            extension=ExtensionMonitoredCall.from_dict(data.get("Extension", {})),
        )


@dataclass
class MonitoredVehicleJourney:
    """Provides information about a VEHICLE JOURNEY along which a VEHICLE is running."""

    line_ref: str
    direction_ref: int
    framed_vehicle_journey_ref: Dict[str, str]
    vehicle_mode: str
    published_line_name: str
    destination_name: str
    destination_short_name: str
    via: str
    monitored_call: MonitoredCall
    previous_call: List[PreviousCall]
    onward_call: List[OnwardCall]

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "MonitoredVehicleJourney":
        """Convert the dictionary to the response object."""
        return MonitoredVehicleJourney(
            line_ref=data.get("LineRef", ""),
            direction_ref=data.get("DirectionRef", 0),
            framed_vehicle_journey_ref=data.get("FramedVehicleJourneyRef", {}),
            vehicle_mode=data.get("VehicleMode", ""),
            published_line_name=data.get("PublishedLineName", ""),
            destination_name=data.get("DestinationName", ""),
            destination_short_name=data.get("DestinationShortName", ""),
            via=data.get("Via", ""),
            monitored_call=MonitoredCall.from_dict(data.get("MonitoredCall", {})),
            previous_call=[
                PreviousCall.from_dict(pc) for pc in data.get("PreviousCall", [])
            ],
            onward_call=[OnwardCall.from_dict(oc) for oc in data.get("OnwardCall", [])],
        )


@dataclass
class MonitoredStopVisit:
    """A visit to a SCHEDULED STOP POINT by a VEHICLE as a departure."""

    recorded_at_time: Optional[datetime]
    monitoring_ref: str
    stop_code: str
    monitored_vehicle_journey: MonitoredVehicleJourney

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "MonitoredStopVisit":
        """Convert the dictionary to the response object."""

        recorded_at_time = data.get("RecordedAtTime")

        return MonitoredStopVisit(
            recorded_at_time=(
                datetime.fromisoformat(recorded_at_time)
                if recorded_at_time is not None
                else None
            ),
            monitoring_ref=data.get("MonitoringRef", ""),
            stop_code=data.get("StopCode", ""),
            monitored_vehicle_journey=MonitoredVehicleJourney.from_dict(
                data.get("MonitoredVehicleJourney", {})
            ),
        )


@dataclass
class StopMonitoringDelivery:
    """Delivery for Stop Monitoring Service"""

    version: str
    response_timestamp: Optional[datetime]
    valid_until: Optional[datetime]
    shortest_possible_cycle: str
    monitoring_ref: List[str]
    monitored_stop_visit: List[MonitoredStopVisit]

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "StopMonitoringDelivery":
        """Convert the dictionary to the response object."""

        response_timestamp = data.get("ResponseTimestamp")
        valid_until = data.get("ValidUntil")

        return StopMonitoringDelivery(
            version=data.get("version", ""),
            response_timestamp=(
                datetime.fromisoformat(response_timestamp)
                if response_timestamp is not None
                else None
            ),
            valid_until=(
                datetime.fromisoformat(valid_until) if valid_until is not None else None
            ),
            shortest_possible_cycle=data.get("ShortestPossibleCycle", ""),
            monitoring_ref=data.get("MonitoringRef", []),
            monitored_stop_visit=[
                MonitoredStopVisit.from_dict(msv)
                for msv in data.get("MonitoredStopVisit", [])
            ],
        )


@dataclass
class VehicleMonitoringDelivery:
    """Delivery for Vehicle Monitoring Service."""

    response_timestamp: Optional[datetime]
    valid_until: Optional[datetime]
    shortest_possible_cycle: str
    vehicle_activity: List[MonitoredStopVisit]

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "VehicleMonitoringDelivery":
        """Convert the dictionary to the response object."""

        response_timestamp = data.get("ResponseTimestamp")
        valid_until = data.get("ValidUntil")

        return VehicleMonitoringDelivery(
            response_timestamp=(
                datetime.fromisoformat(response_timestamp)
                if response_timestamp is not None
                else None
            ),
            valid_until=(
                datetime.fromisoformat(valid_until) if valid_until is not None else None
            ),
            shortest_possible_cycle=data.get("ShortestPossibleCycle", ""),
            vehicle_activity=[
                MonitoredStopVisit.from_dict(va)
                for va in data.get("VehicleActivity", [])
            ],
        )


@dataclass
class EstimatedCallExtension:
    """Extension for estimated call."""

    is_real_time: bool
    is_check_out: bool
    quay: str
    data_source: str

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "EstimatedCallExtension":
        """Convert the dictionary to the response object."""
        return EstimatedCallExtension(
            is_real_time=data.get("IsRealTime", False),
            is_check_out=data.get("IsCheckOut", False),
            quay=data.get("quay", ""),
            data_source=data.get("DataSource", ""),
        )


@dataclass
class EstimatedCall:
    """Stop along the route path."""

    stop_point_ref: str
    stop_point_name: str
    destination_name: str
    destination_short_name: str
    via: str
    expected_departure_time: Optional[datetime]
    expected_arrival_time: Optional[datetime]
    extension: EstimatedCallExtension

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "EstimatedCall":
        """Convert the dictionary to the response object."""

        expected_departure_time = data.get("ExpectedDepartureTime")
        expected_arrival_time = data.get("ExpectedArrivalTime")

        return EstimatedCall(
            stop_point_ref=data.get("StopPointRef", ""),
            stop_point_name=data.get("StopPointName", ""),
            destination_name=data.get("DestinationName", ""),
            destination_short_name=data.get("DestinationShortName", ""),
            via=data.get("Via", ""),
            expected_departure_time=(
                datetime.fromisoformat(expected_departure_time)
                if expected_departure_time is not None
                else None
            ),
            expected_arrival_time=(
                datetime.fromisoformat(expected_arrival_time)
                if expected_arrival_time is not None
                else None
            ),
            extension=EstimatedCallExtension.from_dict(data.get("Extension", {})),
        )


@dataclass
class EstimatedVehicleJourney:
    """Provides information about a VEHICLE JOURNEY along which a VEHICLE is running."""

    line_ref: str
    direction_ref: int
    framed_vehicle_journey_ref: Dict[str, str]
    published_line_name: str
    is_complete_stop_sequence: bool
    estimated_calls: List[EstimatedCall]
    extension: Dict[str, str]

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "EstimatedVehicleJourney":
        """Convert the dictionary to the response object."""
        return EstimatedVehicleJourney(
            line_ref=data.get("LineRef", ""),
            direction_ref=data.get("DirectionRef", 0),
            framed_vehicle_journey_ref=data.get("FramedVehicleJourneyRef", {}),
            published_line_name=data.get("PublishedLineName", ""),
            is_complete_stop_sequence=data.get("IsCompleteStopSequence", False),
            estimated_calls=[
                EstimatedCall.from_dict(ec) for ec in data.get("EstimatedCalls", [])
            ],
            extension=data.get("Extension", {}),
        )


@dataclass
class EstimatedJourneyVersionFrame:
    """Provide a schedule of DATED VEHICLE JOURNEY for a LINE and DIRECTION."""

    recorded_at_time: Optional[datetime]
    estimated_vehicle_journey: List[EstimatedVehicleJourney]

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "EstimatedJourneyVersionFrame":
        """Convert the dictionary to the response object."""

        recorded_at_time = data.get("RecordedAtTime")

        return EstimatedJourneyVersionFrame(
            recorded_at_time=(
                datetime.fromisoformat(recorded_at_time)
                if recorded_at_time is not None
                else None
            ),
            estimated_vehicle_journey=[
                EstimatedVehicleJourney.from_dict(evj)
                for evj in data.get("EstimatedVehicleJourney", [])
            ],
        )


@dataclass
class EstimatedTimetableDelivery:
    """Delivery for Estimated Timetable Service."""

    version: str
    response_timestamp: Optional[datetime]
    valid_until: Optional[datetime]
    shortest_possible_cycle: str
    estimated_journey_version_frame: List[EstimatedJourneyVersionFrame]

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "EstimatedTimetableDelivery":
        """Convert the dictionary to the response object."""

        response_timestamp = data.get("ResponseTimestamp")
        valid_until = data.get("ValidUntil")

        return EstimatedTimetableDelivery(
            version=data.get("version", ""),
            response_timestamp=(
                datetime.fromisoformat(response_timestamp)
                if response_timestamp is not None
                else None
            ),
            valid_until=(
                datetime.fromisoformat(valid_until) if valid_until is not None else None
            ),
            shortest_possible_cycle=data.get("ShortestPossibleCycle", ""),
            estimated_journey_version_frame=[
                EstimatedJourneyVersionFrame.from_dict(ejvf)
                for ejvf in data.get("EstimatedJourneyVersionFrame", [])
            ],
        )


@dataclass
class MessageText:
    """Message for a specific language."""

    value: str
    lang: str

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "MessageText":
        """Convert the dictionary to the response object."""
        return MessageText(value=data.get("Value", ""), lang=data.get("Lang", ""))


@dataclass
class Message:
    """Informative message actuel value."""

    message_zone_ref: str
    message_text: List[MessageText]

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Message":
        """Convert the dictionary to the response object."""
        return Message(
            message_zone_ref=data.get("MessageZoneRef", ""),
            message_text=[
                MessageText.from_dict(mt) for mt in data.get("MessageText", [])
            ],
        )


@dataclass
class Content:
    """Informative message content."""

    impact_start_date_time: Optional[datetime]
    impact_end_date_time: Optional[datetime]
    impacted_group_of_lines_ref: str
    impacted_line_ref: List[str]
    type_of_passenger_equipment_ref: str
    priority: str
    send_updated_notifications_to_customers: bool
    message: List[Message]

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Content":
        """Convert the dictionary to the response object."""

        impact_start_date_time = data.get("ImpactStartDateTime")
        impact_end_date_time = data.get("ImpactEndDateTime")

        return Content(
            impact_start_date_time=(
                datetime.fromisoformat(impact_start_date_time)
                if impact_start_date_time is not None
                else None
            ),
            impact_end_date_time=(
                datetime.fromisoformat(impact_end_date_time)
                if impact_end_date_time is not None
                else None
            ),
            impacted_group_of_lines_ref=data.get("ImpactedGroupOfLinesRef", ""),
            impacted_line_ref=data.get("ImpactedLineRef", []),
            type_of_passenger_equipment_ref=data.get("TypeOfPassengerEquipmentRef", ""),
            priority=data.get("Priority", "Normal"),
            send_updated_notifications_to_customers=data.get(
                "SendUpdatedNotificationsToCustomers", False
            ),
            message=[Message.from_dict(m) for m in data.get("Message", [])],
        )


@dataclass
class InfoMessage:
    """An informative message."""

    format_ref: str
    recorded_at_time: Optional[datetime]
    item_identifier: str
    info_message_identifier: str
    info_channel_ref: str
    valid_until_time: Optional[datetime]
    content: Content

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "InfoMessage":
        """Convert the dictionary to the response object."""

        recorded_at_time = data.get("RecordedAtTime")
        valid_until_time = data.get("ValidUntilTime")

        return InfoMessage(
            format_ref=data.get("formatRef", ""),
            recorded_at_time=(
                datetime.fromisoformat(recorded_at_time)
                if recorded_at_time is not None
                else None
            ),
            item_identifier=data.get("ItemIdentifier", ""),
            info_message_identifier=data.get("InfoMessageIdentifier", ""),
            info_channel_ref=data.get("InfoChannelRef", ""),
            valid_until_time=(
                datetime.fromisoformat(valid_until_time)
                if valid_until_time is not None
                else None
            ),
            content=Content.from_dict(data.get("Content", {})),
        )


@dataclass
class GeneralMessageDelivery:
    """Delivery for general message service."""

    version: str
    response_timestamp: Optional[datetime]
    shortest_possible_cycle: str
    info_message: List[InfoMessage]

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "GeneralMessageDelivery":
        """Convert the dictionary to the response object."""

        response_timestamp = data.get("ResponseTimestamp")

        return GeneralMessageDelivery(
            version=data.get("version", ""),
            response_timestamp=(
                datetime.fromisoformat(response_timestamp)
                if response_timestamp is not None
                else None
            ),
            shortest_possible_cycle=data.get("ShortestPossibleCycle", ""),
            info_message=[
                InfoMessage.from_dict(im) for im in data.get("InfoMessage", [])
            ],
        )


@dataclass
class ServiceDelivery:
    """Service delivery."""

    response_timestamp: Optional[datetime]
    request_message_ref: str
    stop_monitoring_delivery: List[StopMonitoringDelivery]
    vehicle_monitoring_delivery: List[VehicleMonitoringDelivery]
    estimated_timetable_delivery: List[EstimatedTimetableDelivery]
    general_message_delivery: List[GeneralMessageDelivery]

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ServiceDelivery":
        """Convert the dictionary to the response object."""

        response_timestamp = data.get("ResponseTimestamp")

        return ServiceDelivery(
            response_timestamp=(
                datetime.fromisoformat(response_timestamp)
                if response_timestamp is not None
                else None
            ),
            request_message_ref=data.get("RequestMessageRef", ""),
            stop_monitoring_delivery=[
                StopMonitoringDelivery.from_dict(smd)
                for smd in data.get("StopMonitoringDelivery", [])
            ],
            vehicle_monitoring_delivery=[
                VehicleMonitoringDelivery.from_dict(vmd)
                for vmd in data.get("VehicleMonitoringDelivery", [])
            ],
            estimated_timetable_delivery=[
                EstimatedTimetableDelivery.from_dict(etd)
                for etd in data.get("EstimatedTimetableDelivery", [])
            ],
            general_message_delivery=[
                GeneralMessageDelivery.from_dict(gmd)
                for gmd in data.get("GeneralMessageDelivery", [])
            ],
        )


@dataclass
class LineExtension:
    """Extension for AnnotedLineRef."""

    route_type: str
    route_color: str
    route_text_color: str

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "LineExtension":
        """Convert the dictionary to the response object."""
        return LineExtension(
            route_type=data.get("RouteType", ""),
            route_color=data.get("RouteColor", ""),
            route_text_color=data.get("RouteTextColor", ""),
        )


@dataclass
class LineDestination:
    """Direction and destination of the line."""

    direction_ref: int
    destination_name: List[str]

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "LineDestination":
        """Convert the dictionary to the response object."""
        return LineDestination(
            direction_ref=data.get("DirectionRef", 0),
            destination_name=data.get("DestinationName", []),
        )


@dataclass
class AnnotatedLineRef:
    """Line references."""

    line_ref: str
    line_name: str
    destinations: List[LineDestination]
    extension: LineExtension

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "AnnotatedLineRef":
        """Convert the dictionary to the response object."""
        return AnnotatedLineRef(
            line_ref=data.get("LineRef", ""),
            line_name=data.get("LineName", ""),
            destinations=[
                LineDestination.from_dict(dest) for dest in data.get("Destinations", [])
            ],
            extension=LineExtension.from_dict(data.get("Extension", {})),
        )


# endregion

# region general-message


@dataclass
class GeneralMessageResponse:
    """Describe the API response."""

    service_delivery: ServiceDelivery

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "GeneralMessageResponse":
        """Convert the dictionary to the response object."""
        return GeneralMessageResponse(
            service_delivery=ServiceDelivery.from_dict(data.get("ServiceDelivery", {}))
        )


# endregion

# region lines-discovery


@dataclass
class LinesDelivery:
    """Details for lines delivery."""

    response_timestamp: Optional[datetime]
    request_message_ref: str
    valid_until: Optional[datetime]
    shortest_possible_cycle: str
    annotated_line_refs: List[AnnotatedLineRef]

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "LinesDelivery":
        """Convert the dictionary to the response object."""

        response_timestamp = data.get("ResponseTimestamp")
        valid_until = data.get("ValidUntil")

        return LinesDelivery(
            response_timestamp=(
                datetime.fromisoformat(response_timestamp)
                if response_timestamp is not None
                else None
            ),
            request_message_ref=data.get("RequestMessageRef", ""),
            valid_until=(
                datetime.fromisoformat(valid_until) if valid_until is not None else None
            ),
            shortest_possible_cycle=data.get("ShortestPossibleCycle", ""),
            annotated_line_refs=[
                AnnotatedLineRef.from_dict(alr)
                for alr in data.get("AnnotatedLineRef", [])
            ],
        )


@dataclass
class LinesDiscoveryResponse:
    """Describe the API response."""

    lines_delivery: LinesDelivery

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "LinesDiscoveryResponse":
        """Convert the dictionary to the response object."""
        return LinesDiscoveryResponse(
            lines_delivery=LinesDelivery.from_dict(data.get("LinesDelivery", {}))
        )


# endregion

# region stoppoints-discovery


@dataclass
class Location:
    """Stop point location."""

    longitude: float
    latitude: float

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Location":
        """Convert the dictionary to the response object."""
        return Location(
            longitude=data.get("Longitude", 0.0), latitude=data.get("Latitude", 0.0)
        )


@dataclass
class StopPointExtension:
    """Stop point extended information."""

    stop_code: str
    logical_stop_code: str
    is_flexhop_stop: bool
    distance: float

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "StopPointExtension":
        """Convert the dictionary to the response object."""
        return StopPointExtension(
            stop_code=data.get("StopCode", ""),
            logical_stop_code=data.get("LogicalStopCode", ""),
            is_flexhop_stop=data.get("IsFlexhopStop", False),
            distance=data.get("distance", 0.0),
        )


@dataclass
class AnnotatedStopPointRef:
    """Stop point references."""

    stop_point_ref: str
    lines: List[AnnotatedLineRef]
    location: Location
    stop_name: str
    extension: StopPointExtension

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "AnnotatedStopPointRef":
        """Convert the dictionary to the response object."""
        return AnnotatedStopPointRef(
            stop_point_ref=data.get("StopPointRef", ""),
            lines=[AnnotatedLineRef.from_dict(line) for line in data.get("Lines", [])],
            location=Location.from_dict(data.get("Location", {})),
            stop_name=data.get("StopName", ""),
            extension=StopPointExtension.from_dict(data.get("Extension", {})),
        )


@dataclass
class StopPointsDelivery:
    """Delivery for stop points."""

    response_timestamp: Optional[datetime]
    request_message_ref: str
    annotated_stop_point_ref: List[AnnotatedStopPointRef]

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "StopPointsDelivery":
        """Convert the dictionary to the response object."""

        response_time_stamp = data.get("ResponseTimestamp")

        return StopPointsDelivery(
            response_timestamp=(
                datetime.fromisoformat(response_time_stamp)
                if response_time_stamp is not None
                else None
            ),
            request_message_ref=data.get("RequestMessageRef", ""),
            annotated_stop_point_ref=[
                AnnotatedStopPointRef.from_dict(asp)
                for asp in data.get("AnnotatedStopPointRef", [])
            ],
        )


@dataclass
class StopPointsDiscoveryResponse:
    """Describe the stoppoints-discovery API response."""

    stop_points_delivery: StopPointsDelivery

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "StopPointsDiscoveryResponse":
        """Convert the dictionary to the response object."""
        return StopPointsDiscoveryResponse(
            stop_points_delivery=StopPointsDelivery.from_dict(
                data.get("StopPointsDelivery", {})
            )
        )


# endregion

# region stop-monitoring


@dataclass
class StopMonitoringResponse:
    """Describe the stop-monitoring API response."""

    service_delivery: ServiceDelivery

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "StopMonitoringResponse":
        """Convert the dictionary to the response object."""
        return StopMonitoringResponse(
            service_delivery=ServiceDelivery.from_dict(data.get("ServiceDelivery", {}))
        )


# endregion
