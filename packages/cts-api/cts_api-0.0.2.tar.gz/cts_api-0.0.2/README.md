# CTS API Client

An asynchronous Python client for the [CTS (Compagnie des Transports Strasbourgeois) API](https://api.cts-strasbourg.eu/index.html).

## Installation

You can install this library from the repository:
```bash
pip install git+https://github.com/theggz/cts-api.git
```

## Usage

First, you need to get an API token from the [CTS API website](https://api.cts-strasbourg.eu/index.html).

Then, you can initialize the client and make API calls:

```python
import asyncio
from cts_api.client import CtsApi

async def main():
    # Initialize the client with your API token
    # Make sure to replace "YOUR_API_TOKEN" with your actual token
    api = CtsApi(token="YOUR_API_TOKEN", session=None)

    # Example: Get all lines
    lines_response = await api.lines_discovery()
    for line in lines_response.lines_delivery.annotated_line_refs:
        print(f"Line {line.line_name} ({line.line_ref})")

    # Example: Get stop points near a location
    stop_points_response = await api.stoppoints_discovery(
        latitude=48.583,
        longitude=7.75,
        distance=500
    )
    for stop in stop_points_response.stop_points_delivery.annotated_stop_point_ref:
        print(f"Stop: {stop.stop_name}")

    # Example: Get next departures for a stop
    stop_monitoring_response = await api.stop_monitoring(monitoring_ref="280a")
    for visit in stop_monitoring_response.service_delivery.stop_monitoring_delivery[0].monitored_stop_visit:
        journey = visit.monitored_vehicle_journey
        print(
            f"Line {journey.published_line_name} to {journey.destination_name}: "
            f"at {journey.monitored_call.expected_departure_time}"
        )

if __name__ == "__main__":
    asyncio.run(main())
```

### API Methods

All methods are `async` and raise exceptions derived from `CtsError` on failure.

- `CtsApi(token, session=None)`: Constructor. `token` is your API key. `session` is an optional `aiohttp.ClientSession`.

- `lines_discovery()`: Returns a list of all lines.

- `stoppoints_discovery(latitude, longitude, distance, stop_code=None, ...)`: Returns a list of stop points. Can search by coordinates and distance, or by stop code.

- `stop_monitoring(monitoring_ref, ...)`: Provides a stop-centric view of vehicle departures (real-time) at a designated stop. `monitoring_ref` is typically a stop code.

- `general_messages()`: Returns messages about traffic, services, commercial information, etc.

## Running Tests

To run the tests, first clone the repository and install the development dependencies:
```bash
git clone https://github.com/theggz/cts-api.git
cd cts-api
pip install -e .
pip install pytest pytest-asyncio faker
```

### Unit Tests
The unit tests mock the API and can be run without an API token:
```bash
pytest
```

### Integration Tests
The integration tests run against the live CTS API and require a valid API token.

1.  Set your API token as an environment variable:
    ```bash
    export CTS_API_TOKEN="YOUR_API_TOKEN"
    ```

2.  Run the tests marked as `integration`:
    ```bash
    pytest -m integration
    ```
