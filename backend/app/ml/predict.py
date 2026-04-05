import torch
import numpy as np
import joblib
import os
from typing import List, Dict, Any

from .model import SafeDipLSTM
from .dataset import FEATURES, WINDOW_SIZE
from .decision import decide

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "artifacts")
MODEL_PATH    = os.path.join(ARTIFACTS_DIR, "safedip_lstm.pt")
SCALER_PATH   = os.path.join(ARTIFACTS_DIR, "scaler.pkl")

# ----------------------------------------------------------------
# Load model and scaler ONCE at import time
# (not per request — too slow)
# ----------------------------------------------------------------
_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

_model = SafeDipLSTM()
_model.load_state_dict(torch.load(MODEL_PATH, map_location=_device))
_model.eval()
_model.to(_device)

_scaler = joblib.load(SCALER_PATH)

print(f"[ML] SafeDip LSTM loaded from {MODEL_PATH}")
print(f"[ML] Scaler loaded from {SCALER_PATH}")


def run_inference(recent_readings: List[Any]) -> np.ndarray:
    """
    Takes the last 30 Reading ORM objects from the database
    and returns a forecast array of shape (10, 5) in real units.

    Args:
        recent_readings: list of Reading ORM objects, ordered newest first
                         (as returned by .order_by(Reading.created_at.desc()).limit(30))

    Returns:
        np.ndarray of shape (10, 5) — denormalised forecast
        columns: [ph, tds, turbidity, temperature, orp]
    """
    if len(recent_readings) < WINDOW_SIZE:
        raise ValueError(
            f"Need at least {WINDOW_SIZE} readings for inference, "
            f"got {len(recent_readings)}"
        )

    # Reverse so oldest is first (LSTM needs chronological order)
    readings_asc = list(reversed(recent_readings[:WINDOW_SIZE]))

    # Extract the 5 features in correct column order
    raw = np.array([
        [
            r.ph,
            r.tds,
            r.turbidity,
            r.temperature,
            r.orp,
        ]
        for r in readings_asc
    ], dtype=np.float32)  # shape: (30, 5)

    # Normalise using saved scaler
    raw_scaled = _scaler.transform(raw).astype(np.float32)  # (30, 5)

    # Add batch dimension → (1, 30, 5)
    tensor = torch.from_numpy(raw_scaled).unsqueeze(0).to(_device)

    # Run inference
    with torch.no_grad():
        output = _model(tensor)  # (1, 10, 5)

    # Remove batch dimension → (10, 5)
    output_np = output.squeeze(0).cpu().numpy()

    # Denormalise back to real units
    forecast = _scaler.inverse_transform(output_np)  # (10, 5)

    return forecast


def get_recommendation(
    recent_readings: List[Any],
    context: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Full pipeline: readings → LSTM forecast → decision layer → recommendation.

    Args:
        recent_readings: last 30 Reading ORM objects (newest first)
        context: dict with tds_current, tds_sustained_hours,
                 interventions_last_7days, days_since_water_change

    Returns:
        Recommendation dict from decision.py
    """
    forecast = run_inference(recent_readings)
    return decide(forecast, context)