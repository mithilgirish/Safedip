import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os

def generate_pool_data(
    days: int = 45,
    interval_seconds: int = 30,
    output_path: str = "data/pool_synthetic.csv"
):
    np.random.seed(42)

    # Total number of readings
    total_readings = (days * 24 * 3600) // interval_seconds
    print(f"Generating {total_readings:,} readings over {days} days...")

    # --- Timestamps ---
    start_time = datetime(2026, 1, 1, 6, 0, 0)
    timestamps = [start_time + timedelta(seconds=i * interval_seconds)
                  for i in range(total_readings)]

    # --- Helper: hour of day (0-23) ---
    hours = np.array([t.hour + t.minute / 60 for t in timestamps])

    # --- Swimmer load (peaks at 7am and 6pm) ---
    morning_peak = np.exp(-0.5 * ((hours - 7) / 1.5) ** 2)
    evening_peak = np.exp(-0.5 * ((hours - 18) / 1.5) ** 2)
    swimmer_load = (morning_peak + evening_peak).clip(0, 1)

    # ----------------------------------------------------------------
    # TEMPERATURE
    # Daily sine wave: cooler at night, warmer midday
    # Base 28°C, ±3°C swing, + swimmer load heating + noise
    # ----------------------------------------------------------------
    temperature = (
        28.0
        + 3.0 * np.sin(2 * np.pi * (hours - 6) / 24)
        + 0.5 * swimmer_load
        + np.random.normal(0, 0.2, total_readings)
    )

    # ----------------------------------------------------------------
    # pH
    # Starts at 7.3, slowly rises during the day due to swimmer load
    # (sweat, CO2 outgassing). Chemical corrections bring it back down.
    # Around day 20 a water change resets everything.
    # ----------------------------------------------------------------
    ph = np.zeros(total_readings)
    ph[0] = 7.3

    # Water change at day 20 (index where it happens)
    water_change_idx = int((20 * 24 * 3600) / interval_seconds)

    for i in range(1, total_readings):
        drift = 0.0003 * swimmer_load[i]          # rises with swimmers
        noise = np.random.normal(0, 0.005)

        # Chemical correction: if pH > 7.7, operator adds acid
        correction = 0.0
        if ph[i - 1] > 7.7:
            correction = -0.15 * np.random.random()

        # Water change resets pH to fresh 7.2
        if i == water_change_idx:
            ph[i] = 7.2 + np.random.normal(0, 0.05)
        else:
            ph[i] = ph[i - 1] + drift + noise + correction

        ph[i] = np.clip(ph[i], 6.5, 8.5)

    # ----------------------------------------------------------------
    # TDS (Total Dissolved Solids)
    # Monotonically increases — accumulates from chemicals, sweat,
    # sunscreen. Never goes down without a water change.
    # Water change at day 20 resets it to ~200 ppm.
    # ----------------------------------------------------------------
    tds = np.zeros(total_readings)
    tds[0] = 280.0

    for i in range(1, total_readings):
        # Slow accumulation + swimmer load contribution
        accumulation = 0.08 + 0.12 * swimmer_load[i]
        noise = np.random.normal(0, 1.0)

        if i == water_change_idx:
            tds[i] = 200.0 + np.random.normal(0, 10)
        else:
            tds[i] = tds[i - 1] + accumulation + noise

        tds[i] = np.clip(tds[i], 100, 2500)

    # ----------------------------------------------------------------
    # ORP (Oxidation Reduction Potential)
    # Starts around 700 mV. Depletes under UV and swimmer load.
    # Chlorination events spike it back up.
    # ----------------------------------------------------------------
    orp = np.zeros(total_readings)
    orp[0] = 700.0

    for i in range(1, total_readings):
        depletion = 0.05 + 0.15 * swimmer_load[i]
        noise = np.random.normal(0, 2.0)

        # Chlorination: if ORP < 620, operator adds chlorine
        correction = 0.0
        if orp[i - 1] < 620:
            correction = np.random.uniform(40, 80)

        if i == water_change_idx:
            orp[i] = 710.0 + np.random.normal(0, 10)
        else:
            orp[i] = orp[i - 1] - depletion + noise + correction

        orp[i] = np.clip(orp[i], 400, 900)

    # ----------------------------------------------------------------
    # Turbidity (NTU)
    # Generally low (10-30). Spikes after heavy rain or peak usage.
    # Clears after filtration overnight.
    # ----------------------------------------------------------------
    turbidity = np.zeros(total_readings)
    turbidity[0] = 15.0

    # Random rain/contamination events (3 events over 45 days)
    rain_events = np.random.choice(total_readings, size=3, replace=False)

    for i in range(1, total_readings):
        # Natural slow increase during day, clears at night
        if 6 <= hours[i] <= 22:
            drift = 0.01 * swimmer_load[i]
        else:
            drift = -0.05   # filter clears it at night

        noise = np.random.normal(0, 0.3)

        # Rain/contamination spike
        spike = 0.0
        if i in rain_events:
            spike = np.random.uniform(30, 70)

        if i == water_change_idx:
            turbidity[i] = 12.0 + np.random.normal(0, 2)
        else:
            turbidity[i] = turbidity[i - 1] + drift + noise + spike

        turbidity[i] = np.clip(turbidity[i], 0, 200)

    # ----------------------------------------------------------------
    # Intervention type label
    # Used by the decision layer — tracks what happened at each step
    # ----------------------------------------------------------------
    intervention = ["none"] * total_readings

    for i in range(1, total_readings):
        if i == water_change_idx:
            intervention[i] = "water_change"
        elif ph[i] - ph[i-1] < -0.05:
            intervention[i] = "ph_correction"
        elif orp[i] - orp[i-1] > 30:
            intervention[i] = "chlorination"

    # ----------------------------------------------------------------
    # Days since last water change
    # ----------------------------------------------------------------
    days_since_change = np.zeros(total_readings)
    last_change = 0
    for i in range(total_readings):
        if intervention[i] == "water_change":
            last_change = i
        days_since_change[i] = (i - last_change) * interval_seconds / 86400

    # ----------------------------------------------------------------
    # Build DataFrame
    # ----------------------------------------------------------------
    df = pd.DataFrame({
        "timestamp":           timestamps,
        "ph":                  np.round(ph, 3),
        "tds":                 np.round(tds, 1),
        "turbidity":           np.round(turbidity, 2),
        "temperature":         np.round(temperature, 2),
        "orp":                 np.round(orp, 1),
        "swimmer_load":        np.round(swimmer_load, 3),
        "intervention":        intervention,
        "days_since_change":   np.round(days_since_change, 3),
    })

    # ----------------------------------------------------------------
    # Save
    # ----------------------------------------------------------------
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"Saved to {output_path}")
    print(f"Shape: {df.shape}")
    print(f"\nParameter ranges:")
    print(f"  pH:          {df.ph.min():.2f} – {df.ph.max():.2f}")
    print(f"  TDS:         {df.tds.min():.1f} – {df.tds.max():.1f} ppm")
    print(f"  Turbidity:   {df.turbidity.min():.1f} – {df.turbidity.max():.1f} NTU")
    print(f"  Temperature: {df.temperature.min():.1f} – {df.temperature.max():.1f} °C")
    print(f"  ORP:         {df.orp.min():.1f} – {df.orp.max():.1f} mV")
    print(f"\nIntervention counts:")
    print(df.intervention.value_counts())

    return df


if __name__ == "__main__":
    generate_pool_data()