import numpy as np
import pandas as pd
import joblib
import os
from sklearn.preprocessing import MinMaxScaler
from torch.utils.data import TensorDataset, DataLoader
import torch

# Column order — must be consistent across all files
FEATURES = ["ph", "tds", "turbidity", "temperature", "orp"]

WINDOW_SIZE      = 30   # past 30 readings fed as input
FORECAST_HORIZON = 10   # predict next 10 readings

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "artifacts")


def load_and_prepare(
    csv_path: str = "data/pool_synthetic.csv",
    batch_size: int = 64,
    val_split: float = 0.2,
):
    print("Loading CSV...")
    df = pd.read_csv(csv_path)

    # Keep only the 5 sensor columns
    data = df[FEATURES].values.astype(np.float32)
    print(f"Raw data shape: {data.shape}")

    # --- Normalize to [0, 1] ---
    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(data).astype(np.float32)

    # Save scaler so predict.py can denormalize later
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    scaler_path = os.path.join(ARTIFACTS_DIR, "scaler.pkl")
    joblib.dump(scaler, scaler_path)
    print(f"Scaler saved to {scaler_path}")

    # --- Build sliding windows ---
    X, y = [], []
    total = len(data_scaled)

    for i in range(total - WINDOW_SIZE - FORECAST_HORIZON + 1):
        X.append(data_scaled[i : i + WINDOW_SIZE])
        y.append(data_scaled[i + WINDOW_SIZE : i + WINDOW_SIZE + FORECAST_HORIZON])

    X = np.array(X, dtype=np.float32)  # (N, 30, 5)
    y = np.array(y, dtype=np.float32)  # (N, 10, 5)
    print(f"Windows built — X: {X.shape}, y: {y.shape}")

    # --- Train / val split (80/20, no shuffle — time series!) ---
    split_idx = int(len(X) * (1 - val_split))
    X_train, X_val = X[:split_idx], X[split_idx:]
    y_train, y_val = y[:split_idx], y[split_idx:]

    print(f"Train: {X_train.shape[0]:,} samples | Val: {X_val.shape[0]:,} samples")

    # --- Convert to PyTorch tensors ---
    train_dataset = TensorDataset(torch.from_numpy(X_train), torch.from_numpy(y_train))
    val_dataset   = TensorDataset(torch.from_numpy(X_val),   torch.from_numpy(y_val))

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader   = DataLoader(val_dataset,   batch_size=batch_size, shuffle=False)

    return train_loader, val_loader, scaler


if __name__ == "__main__":
    train_loader, val_loader, scaler = load_and_prepare()
    print("Dataset ready.")

    # Quick sanity check — print one batch shape
    for xb, yb in train_loader:
        print(f"Batch X shape: {xb.shape}")  # should be (64, 30, 5)
        print(f"Batch y shape: {yb.shape}")  # should be (64, 10, 5)
        break