# Weather Forecast API

This repository contains `API.py`, a Python script that provides weather forecast data using an external weather API. The script is designed to be simple and easy to integrate into other projects.

## Features

- Fetch current weather data for a specific location.
- Retrieve weather forecasts for multiple days.
- Easy-to-use functions for API interaction.

## Prerequisites

Before using `API.py`, ensure you have the following:

- Python 3.7 or higher installed.
- An API key from a weather service provider (e.g., OpenWeatherMap, WeatherAPI).

## Installation

1. Clone this repository:
    ```bash
    git clone https://github.com/your-username/weather-forecast-api.git
    cd weather-forecast-api
    ```

2. Install required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Add your API key:
    - Open `API.py` and replace `YOUR_API_KEY` with your actual API key.

## Usage

### Importing the Script

You can import `API.py` into your project or run it as a standalone script.

### Example Usage

#### Fetch Current Weather
```python
from API import get_current_weather

location = "Luxembourg"
weather = get_current_weather(location)
print(weather)
```

#### Fetch Weather Forecast
```python
from API import get_weather_forecast

location = "Luxembourg"
forecast = get_weather_forecast(location, days=3)
print(forecast)
```

### Command-Line Usage
Run the script directly to fetch weather data:
```bash
python API.py --location "Luxembourg" --days 3
```

## Functions in `API.py`

### `get_current_weather(location: str) -> dict`
Fetches the current weather for the specified location.

- **Parameters**:
  - `location` (str): The name of the location.
- **Returns**:
  - A dictionary containing weather details.

### `get_weather_forecast(location: str, days: int) -> dict`
Fetches the weather forecast for the specified location and number of days.

- **Parameters**:
  - `location` (str): The name of the location.
  - `days` (int): Number of days for the forecast.
- **Returns**:
  - A dictionary containing forecast details.

## Error Handling

- Ensure the location is valid and spelled correctly.
- Verify that your API key is active and has sufficient permissions.
- Handle exceptions such as network errors or invalid API responses.
