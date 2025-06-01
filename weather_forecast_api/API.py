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
from LSTM_model import WeatherLSTM as LSTMModel
from WeatherDataset import WeatherDataset
import torch
from torch.utils.data import DataLoader
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
# Swagger model for LSTM input (reuse city_model)
@weather_ns.route('/predict_lstm')
class WeatherPredictionLSTM(Resource):
    @weather_ns.expect(city_model)
    @weather_ns.response(200, 'Weather predictions (LSTM) successfully generated.')
    @weather_ns.response(404, 'City not found or no suitable weather station available.')
    @weather_ns.doc(description="Predict weather conditions for a specified city and duration using the LSTM model.")
    def post(self):
        data = request.json
        city_name = data.get('city_name')
        forecast_hours = data.get('forecast_hours', 72)

        city_coordinates = get_city_coordinates(city_name)
        if not city_coordinates:
            return {"error": "City not found"}, 404
        print(f"City coordinates: {city_coordinates}")
        station = find_closest_station(city_coordinates)
        if station is None:
            # If no suitable station found, use a default path
            return {"error": "No suitable weather station found"}, 404
        station_csv_path = "data_api/"
        if station_csv_path is None:
            return {"error": "No suitable weather station found"}, 404

        # Load the LSTM model
        model_path = 'best_lstm_model.pt'
        if not os.path.exists(model_path):
            return {"error": f"Model file '{model_path}' not found."}, 404
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Ensure the station CSV path is correct
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
    
        # Load the dataset using the correct station data
        sequence_length = 72  # Match training
        dataset = WeatherDataset(station_csv_path, sequence_length=sequence_length)
        # Only use the last 72 time steps for prediction
        last_72 = [dataset[i] for i in range(len(dataset)-72, len(dataset))]
        data_loader = DataLoader(last_72, batch_size=32, shuffle=False)

        # Set model parameters to match training
        input_size = 14
        output_size = 14
        hidden_size = 64
        num_layers = 3
        dropout = 0.0
        # Instantiate the model with correct parameters
        model = LSTMModel(input_size=input_size, hidden_size=hidden_size, num_layers=num_layers, output_size=output_size, sequence_length=sequence_length, dropout=dropout)
        # Load the model state dictionary
        model.load_state_dict(torch.load(model_path, map_location=device))
        model.to(device)  # Move the model to the device

        # Use the new per-column inverse_transform
        predictions = np.array(predict_weather_lstm(model, data_loader, device))
        print(predictions)
        # Convert predictions to numpy array and DataFrame
        predictions_np = np.array(predictions)
        dataset.scalers = dataset.scalers  # Ensure scalers are available for inverse transformation
        for i in range(predictions_np.shape[1]):
            if i < len(dataset.scalers):
                scaler = dataset.scalers[i]
                predictions_np[:, i] = scaler.inverse_transform(predictions_np[:, i].reshape(-1, 1)).flatten()
        # Assign column names to the predictions DataFrame
        output_csv_path = 'lstm_predictions.csv'
        predictions_df = pd.DataFrame(predictions_np)
        predictions_df.columns = ["time", "temp", "dwpt", "rhum", "prcp", "snow", "wdir", "wspd", "wpgt", "pres", "tsun", "coco", "lon", "lat"]

        predictions_df.to_csv(output_csv_path, index=False)

        # Generate and save separate graphs for each feature
        graph_folder = 'lstm_prediction_graphs'
        os.makedirs(graph_folder, exist_ok=True)
        num_columns = predictions_df.shape[1]
        station_csv_path = os.path.join(output_folder, f"{station_id}_hourly.csv")
        # Take the last 72 features from the dataframe (blue), then append the prediction (orange)
        for i, column in enumerate(predictions_df.columns):
            plt.figure(figsize=(10, 6))
            # Plot last 72 actual values in blue
            df = pd.read_csv(station_csv_path)
            if column not in df.columns:
                continue 
            last_72_actual = df[column].values[-72:]
            plt.plot(range(72), last_72_actual, color='blue', label='Actual (last 72)')
            # Plot predictions in orange, starting after the last actual value
            plt.plot(range(72), predictions_df[column], color='orange', label='Prediction')
            plt.title(f'LSTM Weather Predictions - {column}')
            plt.xlabel('Time Step')
            plt.ylabel(column)
            plt.legend()
            plt.tight_layout()
            plt.savefig(os.path.join(graph_folder, f'lstm_predictions_{column}.png'))
            plt.close()

        return send_file(output_csv_path, as_attachment=True)


def predict_weather_lstm(model, data_loader, device):
    
    
    model.eval()  # Set the model to evaluation mode
    predictions = []
    with torch.no_grad():  # Disable gradient calculation
        for inputs, _ in data_loader:  # Iterate over the data loader
            inputs = inputs.to(device)  # Move inputs to the device
            outputs = model(inputs)  # Get the model's outputs
            predictions.extend(outputs.cpu().numpy())  # Move predictions to CPU and store
    return predictions

if __name__ == '__main__':
    app.run(debug=True)