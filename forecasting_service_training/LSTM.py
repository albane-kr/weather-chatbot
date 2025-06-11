import torch
from torch.utils.data import DataLoader, Dataset, random_split, Subset
from tqdm import tqdm
import torch.nn as nn
#from CNN import WeatherDataset
import matplotlib.pyplot as plt


class WeatherLSTM(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size, sequence_length, dropout=0):
        super(WeatherLSTM, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.sequence_length = sequence_length
        
        # LSTM layer
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=dropout)
        # Layer normalization after LSTM output
        self.bn_lstm = nn.LayerNorm(hidden_size)
        # Fully connected layers
        self.fc1 = nn.Linear(hidden_size, 25)
        self.bn_fc1 = nn.LayerNorm(25)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(25, output_size)
    
    def forward(self, x):
        # Ensure input is 3D (batch, seq, feature)
        if x.dim() == 2:
            x = x.unsqueeze(0)

        # Initialize hidden and cell states
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)

        # LSTM forward pass
        out, _ = self.lstm(x, (h0, c0))

        # Take only the last time step's output
        out = out[:, -1, :]
        out = self.bn_lstm(out)

        # Fully connected layers
        out = self.fc1(out)
        out = self.bn_fc1(out)
        out = self.relu(out)
        out = self.fc2(out)
        return out

