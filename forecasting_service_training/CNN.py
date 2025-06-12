import torch
from numba import jit

import torch.nn as nn
import torch.nn.functional as F
class SequenceCNN(nn.Module):
    def __init__(self, input_dim, hidden_dims, kernel_sizes, output_dim, activations=['relu']):
        """
        Args:
            input_dim (int): Number of input features.
            hidden_dims (list of int): List of output channels for each conv layer.
            kernel_sizes (list of int): List of kernel sizes for each conv layer.
            output_dim (int): Output feature dimension.
            activations (str or list of str): Activation function(s) for each layer.
        """
        super(SequenceCNN, self).__init__()
        assert len(hidden_dims) == len(kernel_sizes), "hidden_dims and kernel_sizes must have the same length"

        # Map string to activation function
        activations_map = {
            'relu': torch.nn.ReLU,
            'tanh': torch.nn.Tanh,
            'sigmoid': torch.nn.Sigmoid,
            'leaky_relu': torch.nn.LeakyReLU,
            'elu': torch.nn.ELU,
            'gelu': torch.nn.GELU,
            'selu': torch.nn.SELU,
            'none': nn.Identity
        }

        # Handle activations argument
        if isinstance(activations, str):
            activations = [activations] * len(hidden_dims)
        assert len(activations) == len(hidden_dims), "activations must be a string or a list with the same length as hidden_dims"
        self.activations = []
        for act in activations:
            if act not in activations_map:
                raise ValueError(f"Unsupported activation: {act}")
            self.activations.append(activations_map[act]())

        # Build convolutional layers
        conv_layers = []
        in_channels = input_dim
        for out_channels, kernel_size in zip(hidden_dims, kernel_sizes):
            conv_layers.append(
                nn.Conv1d(
                    in_channels=in_channels,
                    out_channels=out_channels,
                    kernel_size=kernel_size,
                    padding=kernel_size // 2
                )
            )
            in_channels = out_channels
        self.conv_layers = nn.ModuleList(conv_layers)

        # Final linear layer
        self.fc = nn.Linear(hidden_dims[-1], output_dim)

    def forward(self, x):
        # x shape: (batch, seq_len, input_dim) or (seq_len, input_dim)
        if x.dim() == 2:
            x = x.unsqueeze(0)  # Add batch dimension if missing
        if x.dim() != 3:
            raise ValueError(f"Input tensor must have 3 dimensions after unsqueeze, but got {x.dim()} dimensions.")
        x = x.permute(0, 2, 1)  # (batch, input_dim, seq_len)
        for conv, activation in zip(self.conv_layers, self.activations):
            x = activation(conv(x))
        x = x.permute(0, 2, 1)  # (batch, seq_len, hidden_dim)
        x = self.fc(x)
        if x.shape[0] == 1:
            x = x.squeeze(0)  # Remove batch dimension if it was added
        return x  # (batch, seq_len, output_dim) or (seq_len, output_dim)

# Example of a numba-accelerated function for preprocessing
@jit(nopython=True)
def normalize_sequence(seq):
    mean = seq.mean()
    std = seq.std()
    return (seq - mean) / (std + 1e-8)