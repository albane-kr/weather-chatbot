import numpy as np
from numba import cuda, float32
import os
import pandas as pd

class AutoregressiveCUDA:
    def __init__(self, coeffs):
        self.coeffs = np.array(coeffs, dtype=np.float32)

    @staticmethod
    @cuda.jit
    def _autoregressive_kernel(data, coeffs, output):
        i = cuda.grid(1)
        if i < data.shape[0]:
            result = 0.0
            for j in range(coeffs.shape[0]):
                if i - j - 1 >= 0:
                    result += coeffs[j] * data[i - j - 1]
            output[i] = result

    def predict(self, data):
        data = np.array(data, dtype=np.float32)
        output = np.zeros_like(data, dtype=np.float32)

        threads_per_block = 256
        blocks_per_grid = (data.shape[0] + threads_per_block - 1) // threads_per_block

        d_data = cuda.to_device(data)
        d_coeffs = cuda.to_device(self.coeffs)
        d_output = cuda.device_array_like(output)

        self._autoregressive_kernel[blocks_per_grid, threads_per_block](d_data, d_coeffs, d_output)

        return d_output.copy_to_host()

# Example usage
import matplotlib.pyplot as plt
from tqdm import tqdm
from scipy.optimize import minimize

if __name__ == "__main__":
    data_dir = "data"
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]

    for csv_file in tqdm(csv_files):
        file_path = os.path.join(data_dir, csv_file)
        df = pd.read_csv(file_path)

        if 'temp' not in df.columns:
            print(f"'temp' column not found in {csv_file}, skipping.")
            continue

        data = df['temp'].values.tolist()
        def loss_function(coeffs, data):
            predicted = autoregressive_cuda(data, coeffs)
            return np.mean((np.array(data[len(coeffs):]) - predicted[len(coeffs):])**2)

        initial_coeffs = [0.5, 0.3, 0.2]
        result = minimize(loss_function, initial_coeffs, args=(data,), bounds=[(0, 1)] * len(initial_coeffs))
        coeffs = result.x
        predicted = autoregressive_cuda(data, coeffs)

        # Combine actual and predicted values
        combined = data + predicted.tolist()

        # Plot the results
        plt.figure(figsize=(10, 6))
        # Use the last 2048 dates for actual data and generate future dates for predictions
        actual_dates = pd.to_datetime(df['time'].values[-24*24:], format='%Y-%m-%d %H:%M:%S')
        delta = actual_dates[-1] - actual_dates[-2]
        future_dates = pd.date_range(start=actual_dates[-1] + delta, periods=7*24, freq=delta)

        plt.plot(actual_dates, data[-24*24:], label="Actual (Last 2048)")
        plt.plot(future_dates, predicted[:7*24], label="Predicted (Next 1024)", linestyle='--')
        plt.title(f"Temperature Data and Predictions for {csv_file}")
        plt.xlabel("Date")
        plt.ylabel("Temperature")
        plt.legend()

        # Save the plot
        output_path = os.path.join("results_ar", f"{os.path.splitext(csv_file)[0]}_plot.png")
        plt.savefig(output_path)
        plt.close()