from flask import Flask, request, jsonify, send_file
from flask_restx import Api, Resource, fields, Namespace
import pandas as pd
import numpy as np
import os
import requests
import matplotlib.pyplot as plt
import geopy
from AR import AutoregressiveCUDA
import warnings
warnings.filterwarnings("ignore")
from meteostat import Stations, Hourly
from geopy.geocoders import Nominatim
from datetime import datetime, timedelta
from tqdm import tqdm

app = Flask(__name__)
api = Api(
    app,
    version="1.0",
    title="Weather Prediction API",
    description="This API allows users to predict weather conditions for a specified city using an Autoregressive (AR) model. "
                "It fetches historical weather data from the closest weather station and generates predictions for the next specified hours.",
)

# Define a custom namespace
weather_ns = Namespace(
    "weather",
    description="Endpoints for weather prediction and related operations",
)
api.add_namespace(weather_ns)

# Swagger model for input
city_model = weather_ns.model(
    'City', {
        'city_name': fields.String(
            required=True,
            description='Name of the city for which weather predictions are requested.',
        ),
        'forecast_hours': fields.Integer(
            required=True,
            description='Number of hours to forecast weather conditions.',
            default=72,
        ),
    }
)


@weather_ns.route('/predict')
class WeatherPrediction(Resource):
    @weather_ns.expect(city_model)
    @weather_ns.response(200, 'Weather predictions successfully generated.')
    @weather_ns.response(404, 'City not found or no suitable weather station available.')
    @weather_ns.doc(description="Predict weather conditions for a specified city and duration using the AR model.")
    def post(self):
        # Parse input
        data = request.json
        city_name = data.get('city_name')
        forecast_hours = data.get('forecast_hours', 72)

        # Step 1: Find city coordinates using geocoding API
        city_coordinates = get_city_coordinates(city_name)
        if not city_coordinates:
            return {"error": "City not found"}, 404
        print(f"City coordinates: {city_coordinates}")

        # Step 2: Find closest weather station with at least 20 years of hourly records
        station = find_closest_station(city_coordinates)
        if station is None:
            return {"error": "No suitable weather station found"}, 404

        # Step 3: Predict using AR model
        predictions, graph_path, output_csv_path = predict_weather(station, forecast_hours)

        # Return results
        return send_file(output_csv_path, as_attachment=True)


def get_city_coordinates(city_name):
    # Use a geocoding API to get city coordinates
    geolocator = Nominatim(user_agent="weather_prediction_api")
    location = geolocator.geocode(city_name)
    if location:
        return location.latitude, location.longitude
    return None


def find_closest_station(city_coordinates):
    # Calculate distance to each station and filter by 20 years of data
    stations = Stations()
    stations_nearby = stations.nearby(city_coordinates[0], city_coordinates[1])
    stations_data = stations_nearby.fetch(1)
    if not stations_data.empty:
        # Save station data to a CSV file and return its path
        station_csv_path = 'station_data.csv'
        stations_data.to_csv(station_csv_path, index=False)
        return station_csv_path
    return None


def predict_weather(station, forecast_hours):
    # Load station data (mocked for simplicity)
    stations_data = pd.read_csv(station)
    output_folder = 'data_api'

    os.makedirs(output_folder, exist_ok=True)  # Ensure the output folder exists
    for index, station in tqdm(stations_data.iterrows(), total=stations_data.shape[0]):
        station_id = str(station['wmo']).zfill(5)  # Ensure station ID is a 5-digit string
        print(station_id)
        data_start = datetime.strptime(str(station['hourly_start']), '%Y-%m-%d')
        data_end = datetime.strptime(str(station['hourly_end']), '%Y-%m-%d')
        data = Hourly(station_id, start=data_start, end=data_end)
        data = data.fetch()
        data.fillna(0)  # Fill NaN values with 0
        if not data.empty:
            # Save the data to a CSV file in the 'data_api' folder
            output_file = os.path.join(output_folder, f"{station_id}_hourly.csv")
            data.to_csv(output_file)
    # Perform AR model prediction for each column
    predictions = {}
    for column in ['temp', "dwpt", "rhum", "prcp", "snow", "wdir", "wspd", "wpgt", "pres", "tsun", "coco"]:  # Replace with actual columns
        if column in data.columns:
            ar_model = AutoregressiveCUDA([0.5, 0.3, 0.2])  # Initialize the AR model
            predictions[column] = ar_model.predict(data[column].values)[:forecast_hours]  # Use AR model for prediction

    # Save predictions to CSV
    output_csv_path = 'predictions.csv'
    pd.DataFrame(predictions).to_csv(output_csv_path, index=False)

    # Generate subgraphs for each measurement/prediction criterion
    graph_path = 'predictions.png'
    num_columns = len(predictions)
    plt.figure(figsize=(10, 6 * num_columns))

    for i, (column, values) in enumerate(predictions.items(), start=1):
        plt.subplot(num_columns, 1, i)
        plt.plot(values, label=column)
        plt.legend()
        plt.title(f'Weather Predictions - {column}')
        plt.tight_layout()

    plt.savefig(graph_path)

    return predictions, graph_path, output_csv_path


if __name__ == '__main__':
    app.run(debug=True)