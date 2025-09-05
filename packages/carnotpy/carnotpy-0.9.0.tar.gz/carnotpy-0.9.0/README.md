# carnotpy

A Python package for connecting to and interacting with Carnot systems.

## Installation

Install carnotpy using pip:

```bash
pip install carnotpy
```

## Dependencies

carnotpy requires the following Python packages:
- pandas
- requests
- python-dateutil

These will be automatically installed when you install carnotpy.

## Quick Start

```python
from carnotpy import CarnotPy

# Initialize connection
carnot = CarnotPy(
    url="https://your-carnot-instance.com",
    username="your_username",
    password="your_password"
)

# Discover available points
points = carnot.discover()

# Read historical data
df = carnot.read_history(
    sensor_ids=["sensor1", "sensor2"],
    start_time="2023-01-01",
    end_time="2023-01-02"
)
```

## Authentication

### Basic Authentication
```python
carnot = CarnotPy(
    url="https://your-carnot-instance.com",
    username="your_username",
    password="your_password"
)
```

### Token-based Authentication
If you already have a token, you can use it directly:
```python
carnot = CarnotPy(
    url="https://your-carnot-instance.com",
    username=None,
    password=None,
    preset_token="your_token_here"
)
```

## API Reference

### CarnotPy Class

#### `__init__(url, username, password, preset_token=None)`
Initialize a CarnotPy instance.

**Parameters:**
- `url` (str): Base URL of the Carnot instance
- `username` (str): Username for authentication
- `password` (str): Password for authentication
- `preset_token` (str, optional): Pre-existing authentication token

### Core Methods

#### `discover()`
Get the point list of the facility.

**Returns:**
- `list`: List of available points in the facility

**Example:**
```python
points = carnot.discover()
for point in points:
    print(f"Equipment: {point['equipment_name']}, Sensor: {point['sensor_name']}")
```

#### `read_history(sensor_ids, start_time, end_time)`
Read historical data for specified sensors.

**Parameters:**
- `sensor_ids` (list): List of sensor IDs to read
- `start_time` (str): Start time in YYYY-MM-DD format
- `end_time` (str): End time in YYYY-MM-DD format

**Returns:**
- `pandas.DataFrame`: Historical data with timestamp index

**Example:**
```python
df = carnot.read_history(
    sensor_ids=["temp_sensor_1", "pressure_sensor_2"],
    start_time="2023-01-01",
    end_time="2023-01-02"
)
print(df.head())
```

#### `read_data3(payload, token=None)`
Read data using the data3 API with custom payload.

**Parameters:**
- `payload` (dict): Query payload for data3 API
- `token` (str, optional): Authentication token

**Returns:**
- `pandas.DataFrame`: Query results with timestamp index

#### `read_data3_query(query, facility_name, date_range, equipment=None, on_only=False, parameters=None, data3_implementation=None)`
Execute a data3 query with advanced options.

**Parameters:**
- `query` (dict): Query configuration
- `facility_name` (str): Name of the facility
- `date_range` (dict): Date range with 'start' and 'end' keys
- `equipment` (str, optional): Equipment name filter
- `on_only` (bool): Filter for "on" status only
- `parameters` (dict, optional): Additional parameters
- `data3_implementation` (callable, optional): Custom data3 implementation

**Returns:**
- `pandas.DataFrame`: Query results

### Configuration Methods

#### `get_config(facility_name)`
Get configuration for a facility.

**Parameters:**
- `facility_name` (str): Name of the facility

**Returns:**
- `dict`: Configuration data

**Example:**
```python
config = carnot.get_config("facility_1")
print(config)
```

#### `set_config(facility_name, config_name, config, config_id=None)`
Set configuration for a facility.

**Parameters:**
- `facility_name` (str): Name of the facility
- `config_name` (str): Name of the configuration
- `config` (dict): Configuration data
- `config_id` (str, optional): Configuration ID

**Returns:**
- `dict`: Response from the API

### Notification Methods

#### `get_notifications(facility_name, date_range=None, ignore_acknowledged=True)`
Get notifications for a facility.

**Parameters:**
- `facility_name` (str): Name of the facility
- `date_range` (list, optional): Date range [start, end]
- `ignore_acknowledged` (bool): Whether to ignore acknowledged notifications

**Returns:**
- `list`: List of notifications

**Example:**
```python
notifications = carnot.get_notifications(
    facility_name="facility_1",
    date_range=["2023-01-01", "2023-01-02"]
)
```

### Maintenance Methods

#### `get_maintenance_records(facility_name, date_range=None, equipment_name=None)`
Get maintenance records for a facility.

**Parameters:**
- `facility_name` (str): Name of the facility
- `date_range` (list, optional): Date range [start, end]
- `equipment_name` (str, optional): Equipment name filter

**Returns:**
- `list`: List of maintenance records

**Example:**
```python
records = carnot.get_maintenance_records(
    facility_name="facility_1",
    equipment_name="compressor_1"
)
```

### Sensor Methods

#### `get_sensor_id(facility_name, equipment_name, sensor_name)`
Get sensor ID for a specific sensor.

**Parameters:**
- `facility_name` (str): Name of the facility
- `equipment_name` (str): Name of the equipment
- `sensor_name` (str): Name of the sensor

**Returns:**
- `str`: Sensor ID

**Example:**
```python
sensor_id = carnot.get_sensor_id(
    facility_name="facility_1",
    equipment_name="compressor_1",
    sensor_name="temperature"
)
```

### Control Methods

#### `write(sensor_id, value, priority, duration=None)`
Write a value to a sensor.

**Parameters:**
- `sensor_id` (str): ID of the sensor
- `value`: Value to write
- `priority` (int): Priority level
- `duration` (int, optional): Duration in seconds

**Returns:**
- `dict`: Response from the API

**Example:**
```python
result = carnot.write(
    sensor_id="sensor_123",
    value=75.5,
    priority=1,
    duration=3600
)
```

### Job Methods

#### `add_job(facility_name, job_type, meta)`
Add a job to the system.

**Parameters:**
- `facility_name` (str): Name of the facility
- `job_type` (str): Type of job
- `meta` (dict): Job metadata

**Returns:**
- `dict`: Response from the API

## Error Handling

The package will raise assertions for HTTP errors. Common issues:

- **Authentication Error**: Check your username, password, or token
- **Connection Error**: Verify the URL is correct and accessible
- **Sensor Not Found**: Use `discover()` to find available sensors
- **Invalid Date Range**: Ensure dates are in YYYY-MM-DD format

Example error handling:
```python
try:
    points = carnot.discover()
except AssertionError as e:
    print(f"API Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Examples

### Basic Data Reading
```python
from carnotpy import CarnotPy

# Initialize connection
carnot = CarnotPy(
    url="https://your-carnot-instance.com",
    username="your_username",
    password="your_password"
)

# Get available points
points = carnot.discover()
print(f"Found {len(points)} points")

# Read historical data
df = carnot.read_history(
    sensor_ids=["temp_01", "pressure_02"],
    start_time="2023-01-01",
    end_time="2023-01-02"
)

# Display data
print(df.describe())
```

### Working with Notifications
```python
# Get recent notifications
notifications = carnot.get_notifications(
    facility_name="main_facility",
    date_range=["2023-01-01", "2023-01-31"]
)

# Process notifications
for notification in notifications:
    print(f"Alert: {notification['message']}")
    print(f"Time: {notification['timestamp']}")
```

### Equipment Maintenance
```python
# Get maintenance records
records = carnot.get_maintenance_records(
    facility_name="main_facility",
    equipment_name="compressor_1",
    date_range=["2023-01-01", "2023-01-31"]
)

# Analyze maintenance frequency
print(f"Total maintenance events: {len(records)}")
```

## License

This package is developed by Carnot Innovations.

## Support

For issues and questions, please refer to your Carnot system documentation or contact your system administrator.
