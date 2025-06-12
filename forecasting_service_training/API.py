from flask import Flask, request, jsonify, send_file
from flask_restx import Api, Resource, fields, Namespace
import pandas as pd
import numpy as np
import os
import requests
import matplotlib.pyplot as plt
import geopy
import warnings
warnings.filterwarnings("ignore")
from meteostat import Stations, Hourly
from geopy.geocoders import Nominatim
from datetime import datetime, timedelta
from tqdm import tqdm
from LSTM import WeatherLSTM
from CNN import SequenceCNN
import torch
from torch.utils.data import DataLoader
from sklearn.preprocessing import StandardScaler
#############################################################################################################################################################


# Documentation and API setup
app = Flask(__name__)
api = Api(
    app,
    version="1.0",
    title="Weather Prediction API",
    description="This API allows users to predict weather conditions for a specified city using an Autoregressive (AR) model. "
                "It fetches historical weather data from the closest weather station and generates predictions for the next specified hours.",
)

LSTM_MODEL_PATH_TEMP = 'best_lstm_model.pt'
if not os.path.exists(LSTM_MODEL_PATH_TEMP):
    print(f"Model file '{LSTM_MODEL_PATH_TEMP}' not found. Please ensure the model is trained and available. Switching to CNN model")

CNN_MODEL_PATH_TEMP = 'last_model_temp_cnn.pt'
if not os.path.exists(CNN_MODEL_PATH_TEMP):
    print(f"Model file '{CNN_MODEL_PATH_TEMP}' not found. Please ensure the model is trained and available.")

CNN_MODEL_PATH_PRCP = 'best_model_prcp_cnn.pt'
if not os.path.exists(CNN_MODEL_PATH_PRCP):
    raise FileNotFoundError(f"Model file '{CNN_MODEL_PATH_PRCP}' not found. Please ensure the model is trained and available.")


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
    }
)

# Swagger model for return data
weather_model = weather_ns.model(
    'WeatherModel', {
        'tmax': fields.Float(
            required=True,
            description='Maximum temperature in degrees Celsius.',
        ),
        'tmin': fields.Float(
            required=True,
            description='Minimum temperature in degrees Celsius.',
        ),
        'prcp'  : fields.Float(
            required=True,
            description='Precipitation in millimeters.',
        ),
        'coco': fields.Float(
            required=True,
            description='Weather condition code (0-9).',
        )
    }
)

# Helper function to fetch weather data, location coordinates, and find the closest weather station

def get_weather_data(station_id:str, hourly_end_date, lon, lat) -> pd.DataFrame|None:
    """_summary_

    Args:
        station_id (_type_): _description_
        hourly_end_date (_type_): _description_
    """
    # Fetch hourly weather data for the given station and date range
    data = Hourly(station_id, start=hourly_end_date - timedelta(days=7), end=hourly_end_date)
    data = data.fetch()
    data.to_csv('weather_data.csv')
    data = pd.read_csv('weather_data.csv', parse_dates=['time'])
    data = data[['temp', 'prcp', 'time']]
    data['lat'] = lat
    data['lon'] = lon
    
    if not data.empty:
        #Convert to DataFrame and fill NaN values with 0
        data.fillna(0, inplace=True)
        data_temp = data[['lat', 'lon', 'temp', 'time']]
        data_prcp = data[['lat', 'lon', 'prcp', 'time']]
        data_temp['date'] = data_temp['time'].dt.date
        data_prcp['date'] = data_prcp['time'].dt.date
        data_prcp = data_prcp[['date', 'prcp', 'lat', 'lon']]
        data_temp = data_temp[['date', 'temp', 'lat', 'lon']]
        df_daily_summed = data_prcp.groupby('date', as_index=False)['prcp'].sum()
        df_daily_summed['lat'] = lat
        df_daily_summed['lon'] = lon 
        df_daily_max = data_temp.groupby('date', as_index=False)['temp'].max()
        df_daily_min = data_temp.groupby('date', as_index=False)['temp'].min()
        df_daily_max = data_temp.merge(df_daily_max, on=['date', 'temp'])
        df_daily_min = data_temp.merge(df_daily_min, on=['date', 'temp'])
        df_daily_max = df_daily_max.drop_duplicates(subset=['date'], keep='first')
        df_daily_min = df_daily_min.drop_duplicates(subset=['date'], keep='first')
        df_daily_max = df_daily_max.rename(columns={'temp': 'temp_max'})
        df_daily_min = df_daily_min.rename(columns={'temp': 'temp_min'})
        df_daily_max = df_daily_max[['date', 'temp_max', 'lat', 'lon' ]]
        df_daily_min = df_daily_min[['date', 'temp_min', 'lat', 'lon' ]]
        data_temps = df_daily_max[['date', 'temp_max']]
        
        data_temps = data_temps.merge(df_daily_min, on=['date'])
        print(f'Shape of temperature data: {data_temps.shape}')
        print(f'Shape of precipitation data: {df_daily_summed.shape}')
        print(data_temps[-7:],"\n", df_daily_summed[-7:])
        return data_temps[-7:], df_daily_summed[-7:]
    return None

def get_city_coordinates(city_name: str) -> tuple|None:
    # Use a geocoding API to get city coordinates
    geolocator = Nominatim(user_agent="weather_prediction_api")
    location = geolocator.geocode(city_name)
    if location:
        return location.latitude, location.longitude
    return None


def find_closest_station(city_coordinates: tuple) -> str|None:
    # Calculate distance to each station and filter by 20 years of data
    stations = Stations()
    stations_nearby = stations.nearby(city_coordinates[0], city_coordinates[1])
    stations_data = stations_nearby.fetch(1)
    if not stations_data.empty:
        # Save station data to a CSV file and return its path
        station_csv_path = 'station_data.csv'
        print(f"Closest station found: {stations_data.iloc[0]['name']} at {stations_data.iloc[0]['latitude']}, {stations_data.iloc[0]['longitude']}")
        print(f"Station ID: {stations_data.iloc[0]['wmo']}")
        station_id = stations_data.iloc[0]['wmo']
        hourly_end_date = stations_data.iloc[0]['hourly_end']
        return station_id, hourly_end_date
    raise ValueError("No suitable weather station found within the specified range.")
    return None

def get_weather_condition_code(prcp, temp_min, temp_max):
    if prcp > 20:
        return 4  # Heavy Rain
    elif prcp > 0:
        if temp_max < 2:
            return 5  # Snow
        return 3  # Rain
    elif temp_max > 35:
        return 8  # Extreme Heat
    elif temp_min < -10:
        return 9  # Extreme Cold
    elif temp_min < 2 and temp_max < 5:
        return 7  # Fog (cold and humid, but no rain)
    elif temp_max - temp_min < 3:
        return 2  # Cloudy
    elif temp_max - temp_min < 7:
        return 1  # Partly Cloudy
    else:
        return 0  # Clear

def predict_temp_cnn(temp_data, device):
    """
    Predict next day's temp_max and temp_min using the CNN model.
    temp_data: pd.DataFrame with columns ['temp_max', 'temp_min', 'lat', 'lon', 'date'] for the last 7 days
    device: torch.device
    Returns: (pred_temp_max, pred_temp_min)
    """
    input_cols = ['temp_max', 'temp_min', 'lat', 'lon', 'date']  # 5 columns
    temp_data = temp_data.copy()
    # Convert 'date' column to numeric (ordinal)
    temp_data['date'] = pd.to_datetime(temp_data['date']).map(lambda d: d.toordinal())
    scalers = []
    for i in temp_data[input_cols].columns:
        scaler = StandardScaler()
        temp_data[i] = scaler.fit_transform(temp_data[i].values.reshape(-1, 1)).flatten()
        scalers.append(scaler)
    x = temp_data[input_cols].values.astype(np.float32)  # shape (7, 5)
    x = x.flatten()  # shape (35,)
    x_tensor = torch.tensor(x, dtype=torch.float32).unsqueeze(0).to(device)  # shape (1, 35)

    model = SequenceCNN(input_dim=35, hidden_dims=[32, 64], kernel_sizes=[5, 5], output_dim=5, activations=['relu', 'relu'])
    model.load_state_dict(torch.load(CNN_MODEL_PATH_TEMP, map_location=device))
    model.to(device)
    model.eval()

    with torch.no_grad():
        pred = model(x_tensor).cpu().numpy().flatten()  # shape (5,)
    pred_temp_max = scalers[0].inverse_transform([[pred[0]]])[0, 0]
    pred_temp_min = scalers[1].inverse_transform([[pred[1]]])[0, 0]
    print(f"Predicted max temperature: {pred_temp_max}, Predicted min temperature: {pred_temp_min}")
    return pred_temp_max, pred_temp_min

def predict_prcp(prcp_data, device):
    """Predict precipitation using the CNN model with 7 days of data (4 features: lat, lon, prcp, date)."""
    # Load the CNN model
    loaded_obj = torch.load(CNN_MODEL_PATH_PRCP, map_location=device, weights_only=False)
    if isinstance(loaded_obj, dict):
        current_model = SequenceCNN(input_dim=28, output_dim=4, hidden_dims=[32, 64], kernel_sizes=[13, 5], activations=['relu', 'sigmoid'])
        current_model.load_state_dict(loaded_obj)
    else:
        current_model = loaded_obj
    current_model.to(device)
    current_model.eval()
    input_cols = ['lat', 'lon', 'prcp', 'date']  # 4 columns for 7 days
    prcp_data = prcp_data.copy()
    prcp_data['date'] = pd.to_datetime(prcp_data['date']).map(lambda d: d.toordinal())
    prcp_last = prcp_data[input_cols].tail(7)
    scalers = []
    for col in input_cols:
        scaler = StandardScaler()
        prcp_last[col] = scaler.fit_transform(prcp_last[col].values.reshape(-1, 1)).flatten()
        scalers.append(scaler)
    x = prcp_last.values.astype(np.float32).flatten()  # shape (28,)
    x_tensor = torch.tensor(x, dtype=torch.float32).unsqueeze(0).to(device)  # shape (1, 28)
    with torch.no_grad():
        prediction = current_model(x_tensor)
    pred_prcp_scaled = prediction.cpu().numpy().flatten()[0]
    predicted_prcp = scalers[2].inverse_transform([[pred_prcp_scaled]])[0, 0]  # scaler for 'prcp'
    print(f"Predicted precipitation: {predicted_prcp}")
    return predicted_prcp
# Swagger model for LSTM input (reuse city_model)
@weather_ns.route('/predict')
class WeatherPredictionLSTM(Resource):
    @weather_ns.expect(city_model)
    @weather_ns.response(200, 'Weather prediction successful.', weather_model)
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
        station, hourly_end_date = find_closest_station(city_coordinates)
        if station is None:
            # If no suitable station found, use a default path
            return {"error": "No suitable weather station found"}, 404
        station_csv_path = "data_api/"
        if station_csv_path is None:
            return {"error": "No suitable weather station found"}, 404
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        temp_data, prcp_data = get_weather_data(station, hourly_end_date, city_coordinates[1], city_coordinates[0])
        if temp_data is None or prcp_data is None:
            return {"error": "No weather data available for the specified station."}, 404
        print(f"Weather data for station {station} fetched successfully.")
        print(f"Temperature data shape: {temp_data.shape}, Precipitation data shape: {prcp_data.shape}")
        temp_max, temp_min = predict_temp_cnn(temp_data, device)
        prcp = predict_prcp(prcp_data, device)
        # Simple decision tree for weather condition code (coco)
        # 0: Clear, 1: Partly Cloudy, 2: Cloudy, 3: Rain, 4: Heavy Rain, 5: Snow, 6: Thunderstorm, 7: Fog, 8: Extreme Heat, 9: Extreme Cold

        coco = get_weather_condition_code(prcp, temp_min, temp_max)

        return {
            "tmax": float(temp_max),
            "tmin": float(temp_min),
            "prcp": float(prcp),
            "coco": float(coco)
        }, 200
if __name__ == '__main__':
    app.run(debug=True, port=5001)