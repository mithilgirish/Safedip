import numpy as np
from typing import Dict, Any

# Column indices in the forecast array (must match FEATURES order in dataset.py)
PH_IDX   = 0
TDS_IDX  = 1
TURB_IDX = 2
TEMP_IDX = 3
ORP_IDX  = 4

# Thresholds (real-world units, denormalised)
TDS_PARTIAL_REPLACE  = 1500.0   # ppm — sustained triggers partial change
TDS_FULL_REPLACE     = 2000.0   # ppm — immediate full replacement
ORP_CHLORINATION     = 620.0    # mV  — add chlorine
ORP_PERSISTENT_LOW   = 550.0    # mV  — water exhausted if repeated
PH_CAUTION_HIGH      = 7.8
PH_CAUTION_LOW       = 7.0
TURB_CAUTION         = 50.0     # NTU
TURB_UNSAFE          = 100.0    # NTU

# Interval between readings (seconds) — must match generate_data.py
READING_INTERVAL_SEC = 30


def _action(
    action: str,
    urgency: str,
    reason: str,
    instruction: str,
    parameter: str,
    forecast: np.ndarray,
    interval_sec: int = READING_INTERVAL_SEC,
) -> Dict[str, Any]:
    """Build the standard recommendation response dict."""

    # forecast shape: (10, 5) in real units
    minutes_per_step = interval_sec / 60

    # Find first breach per parameter
    def breach_eta(col_idx, threshold, above=True):
        for step in range(forecast.shape[0]):
            val = forecast[step, col_idx]
            if above and val > threshold:
                return round(step * minutes_per_step, 1)
            if not above and val < threshold:
                return round(step * minutes_per_step, 1)
        return None

    return {
        "action":     action,
        "urgency":    urgency,
        "reason":     reason,
        "instruction": instruction,
        "parameter":  parameter,
        "forecast_summary": {
            "ph_in_5min":        round(float(forecast[9, PH_IDX]),   3),
            "tds_in_5min":       round(float(forecast[9, TDS_IDX]),   1),
            "turbidity_in_5min": round(float(forecast[9, TURB_IDX]),  2),
            "temp_in_5min":      round(float(forecast[9, TEMP_IDX]),  2),
            "orp_in_5min":       round(float(forecast[9, ORP_IDX]),   1),
            "ph_breach_eta_min":   breach_eta(PH_IDX,   PH_CAUTION_HIGH, above=True),
            "orp_breach_eta_min":  breach_eta(ORP_IDX,  ORP_CHLORINATION, above=False),
            "tds_breach_eta_min":  breach_eta(TDS_IDX,  TDS_PARTIAL_REPLACE, above=True),
            "turb_breach_eta_min": breach_eta(TURB_IDX, TURB_CAUTION, above=True),
        }
    }


def decide(
    forecast: np.ndarray,
    context: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Main decision function.

    Args:
        forecast: np.ndarray of shape (10, 5) — denormalised real-world values
                  columns: [ph, tds, turbidity, temperature, orp]

        context:  dict with keys:
                  - tds_current           (float)  current TDS reading
                  - tds_sustained_hours   (float)  hours TDS has been above 1500
                  - interventions_last_7days (int)  number of chemical treatments
                  - days_since_water_change (int)   days since last water change

    Returns:
        Recommendation dict with action, urgency, reason, instruction,
        parameter, and forecast_summary.
    """

    tds_current             = context.get("tds_current", 0)
    tds_sustained_hours     = context.get("tds_sustained_hours", 0)
    interventions_7d        = context.get("interventions_last_7days", 0)
    days_since_change       = context.get("days_since_water_change", 0)

    tds_forecast_max  = float(np.max(forecast[:, TDS_IDX]))
    ph_forecast_max   = float(np.max(forecast[:, PH_IDX]))
    ph_forecast_min   = float(np.min(forecast[:, PH_IDX]))
    orp_forecast_min  = float(np.min(forecast[:, ORP_IDX]))
    turb_forecast_max = float(np.max(forecast[:, TURB_IDX]))

    # ----------------------------------------------------------------
    # PRIORITY 1 — Full water replacement
    # ----------------------------------------------------------------
    if tds_current > TDS_FULL_REPLACE:
        return _action(
            action      = "full_replace",
            urgency     = "immediate",
            reason      = f"TDS is critically high at {tds_current:.0f} ppm (limit: {TDS_FULL_REPLACE:.0f} ppm). "
                          f"Chemical treatment cannot lower TDS — only fresh water can.",
            instruction = "Close pool immediately. Drain fully and refill with fresh water. "
                          "Re-balance pH to 7.2–7.6 and ORP to 650–750 mV after refill. "
                          "Do not reopen until all parameters are in safe range.",
            parameter   = "tds",
            forecast    = forecast,
        )

    # ----------------------------------------------------------------
    # PRIORITY 2 — Partial water replacement
    # ----------------------------------------------------------------
    if tds_sustained_hours >= 48 and tds_current > TDS_PARTIAL_REPLACE:
        return _action(
            action      = "partial_replace",
            urgency     = "within_24_hours",
            reason      = f"TDS has been above {TDS_PARTIAL_REPLACE:.0f} ppm for "
                          f"{tds_sustained_hours:.0f} hours. Chemical buffering is no longer effective.",
            instruction = f"Drain 35% of pool volume and refill with fresh water. "
                          f"Re-balance pH and chlorinate after refill. "
                          f"Current TDS: {tds_current:.0f} ppm.",
            parameter   = "tds",
            forecast    = forecast,
        )

    if interventions_7d >= 5 and orp_forecast_min < ORP_PERSISTENT_LOW:
        return _action(
            action      = "partial_replace",
            urgency     = "within_48_hours",
            reason      = f"Pool has required {interventions_7d} chemical interventions in 7 days "
                          f"and ORP is still forecasted to drop to {orp_forecast_min:.0f} mV. "
                          f"Water's buffering capacity is exhausted.",
            instruction = "Drain 30–40% of pool volume and refill. "
                          "The water can no longer hold a stable chlorine residual.",
            parameter   = "orp",
            forecast    = forecast,
        )

    if days_since_change >= 30 and tds_current > TDS_PARTIAL_REPLACE:
        return _action(
            action      = "partial_replace",
            urgency     = "within_48_hours",
            reason      = f"It has been {days_since_change} days since the last water change "
                          f"and TDS is at {tds_current:.0f} ppm.",
            instruction = "Schedule a 30–40% partial drain and refill within 48 hours.",
            parameter   = "tds",
            forecast    = forecast,
        )

    # ----------------------------------------------------------------
    # PRIORITY 3 — Chemical intervention
    # ----------------------------------------------------------------
    if ph_forecast_max > PH_CAUTION_HIGH:
        return _action(
            action      = "chemical",
            urgency     = "within_2_hours",
            reason      = f"pH is forecasted to reach {ph_forecast_max:.2f} "
                          f"(caution limit: {PH_CAUTION_HIGH}).",
            instruction = "Add 80–100 ml of muriatic acid (hydrochloric acid). "
                          "Distribute around pool edges with pump running. "
                          "Retest pH after 30 minutes.",
            parameter   = "ph",
            forecast    = forecast,
        )

    if ph_forecast_min < PH_CAUTION_LOW:
        return _action(
            action      = "chemical",
            urgency     = "within_2_hours",
            reason      = f"pH is forecasted to drop to {ph_forecast_min:.2f} "
                          f"(caution limit: {PH_CAUTION_LOW}).",
            instruction = "Add 50–80g of sodium carbonate (soda ash). "
                          "Distribute evenly with pump running. "
                          "Retest pH after 30 minutes.",
            parameter   = "ph",
            forecast    = forecast,
        )

    if orp_forecast_min < ORP_CHLORINATION:
        return _action(
            action      = "chemical",
            urgency     = "within_2_hours",
            reason      = f"ORP is forecasted to drop to {orp_forecast_min:.0f} mV "
                          f"indicating low chlorine residual (limit: {ORP_CHLORINATION} mV).",
            instruction = "Add 150–200g of calcium hypochlorite (65% chlorine). "
                          "Broadcast across pool surface with pump running. "
                          "Retest ORP after 20 minutes.",
            parameter   = "orp",
            forecast    = forecast,
        )

    if turb_forecast_max > TURB_UNSAFE:
        return _action(
            action      = "chemical",
            urgency     = "within_4_hours",
            reason      = f"Turbidity is forecasted to reach {turb_forecast_max:.1f} NTU "
                          f"(unsafe limit: {TURB_UNSAFE} NTU).",
            instruction = "Run filter backwash for 10 minutes. "
                          "Add 200g of pool flocculant. "
                          "If turbidity does not clear within 6 hours consider partial water change.",
            parameter   = "turbidity",
            forecast    = forecast,
        )

    if turb_forecast_max > TURB_CAUTION:
        return _action(
            action      = "chemical",
            urgency     = "within_4_hours",
            reason      = f"Turbidity is forecasted to reach {turb_forecast_max:.1f} NTU "
                          f"(caution limit: {TURB_CAUTION} NTU).",
            instruction = "Run filter backwash for 8 minutes. Monitor turbidity over next 2 hours.",
            parameter   = "turbidity",
            forecast    = forecast,
        )

    # ----------------------------------------------------------------
    # PRIORITY 4 — Predictive warning (within safe range but drifting)
    # ----------------------------------------------------------------
    warnings = []

    if ph_forecast_max > 7.6:
        warnings.append(f"pH trending toward caution (forecasted max: {ph_forecast_max:.2f})")
    if orp_forecast_min < 650:
        warnings.append(f"ORP trending low (forecasted min: {orp_forecast_min:.0f} mV)")
    if tds_forecast_max > 800:
        warnings.append(f"TDS accumulating (forecasted: {tds_forecast_max:.0f} ppm)")

    if warnings:
        return _action(
            action      = "warning",
            urgency     = "monitor",
            reason      = "Parameters are within safe range but trending toward caution. " + " | ".join(warnings),
            instruction = "No immediate action required. Monitor closely over next 2 hours. "
                          "Prepare chemical treatments in advance.",
            parameter   = "multiple",
            forecast    = forecast,
        )

    # ----------------------------------------------------------------
    # PRIORITY 5 — All good
    # ----------------------------------------------------------------
    return _action(
        action      = "nominal",
        urgency     = "none",
        reason      = "All parameters are within safe range and stable.",
        instruction = "No action required. Next scheduled check in 4 hours.",
        parameter   = "none",
        forecast    = forecast,
    )