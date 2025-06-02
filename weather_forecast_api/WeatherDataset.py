# Define the dataset class
from torch.utils.data import Dataset, DataLoader, random_split
import json
from tqdm import tqdm
import os
import numpy as np
import pandas as pd
import torch
from sklearn.preprocessing import StandardScaler
import torch.nn as nn
# Define the dataset class
class WeatherDataset(Dataset):
    def __init__(self, csv_folder, sequence_length=72, prediction_length=1):
        self.data = []
        self.sequence_length = sequence_length
        self.prediction_length = prediction_length

        with open('full.json', 'r', encoding='utf-8') as f:
            location_data = json.load(f)

        for file in tqdm(os.listdir(csv_folder)):
            if file.endswith(".csv"):
                object_id = file[:5]
                for obj in location_data:
                    if obj['id'] == object_id:
                        object_id = obj

                df = pd.read_csv(os.path.join(csv_folder, file))
                df['latitude'] = obj['location']['latitude']
                df['longitude'] = obj['location']['longitude']
                self.data.append(df.apply(pd.to_numeric, errors='coerce').fillna(0).astype(np.float32).values)

        self.data = np.concatenate(self.data, axis=0)

        # Apply scaling here: one StandardScaler per column
        self.scalers = []
        scaled_columns = []
        for i in range(self.data.shape[1]):
            scaler = StandardScaler()
            col = self.data[:, i].reshape(-1, 1)
            scaled_col = scaler.fit_transform(col)
            scaled_columns.append(scaled_col)
            self.scalers.append(scaler)
        self.data = np.concatenate(scaled_columns, axis=1)

        self.features = self.data

    def __len__(self):
        return len(self.features) - self.sequence_length

    def __getitem__(self, idx):
        x = self.features[idx:idx + self.sequence_length]
        y = self.features[idx + self.sequence_length]
        # x = x.flatten()  # Flatten for FCNN
        return torch.tensor(x, dtype=torch.float32), torch.tensor(y, dtype=torch.float32)

    def inverse_transform(self, X):
        # X shape: (n_samples, n_features)
        X_inv = np.zeros_like(X)
        for i, scaler in enumerate(self.scalers):
            X_inv[:, i] = scaler.inverse_transform(X[:, i]).flatten()
        return X_inv
