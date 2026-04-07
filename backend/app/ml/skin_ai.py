"""
skin_ai.py — Personalized water safety engine for SafeDip.

Takes a water reading + user skin profile and returns a personalised
safety score and advice.  No ML model is needed — the thresholds are
well-established in dermatology and aquatic-health literature.
"""

from typing import Dict, Any, List, Tuple

# ──────────────────────────────────────────────────────────────────────
#  Per-skin-type pH thresholds
#  Human skin pH is ~4.5-5.5; pool water interacts with the skin barrier.
#  Higher pool pH strips lipids → dry/eczema skin suffers most.
#  Lower pool pH can cause irritation in rosacea / sensitive types.
# ──────────────────────────────────────────────────────────────────────
SKIN_PH_THRESHOLDS: Dict[str, Dict[str, float]] = {
    "normal": {
        "safe_low": 7.0, "safe_high": 7.8,
        "caution_low": 6.8, "caution_high": 8.0,
    },
    "dry": {
        "safe_low": 7.2, "safe_high": 7.5,   # dry skin needs tighter range
        "caution_low": 7.0, "caution_high": 7.8,
    },
    "oily": {
        "safe_low": 6.8, "safe_high": 7.6,
        "caution_low": 6.5, "caution_high": 7.9,
    },
    "combination": {
        "safe_low": 7.0, "safe_high": 7.6,
        "caution_low": 6.8, "caution_high": 7.9,
    },
    "sensitive": {
        "safe_low": 7.2, "safe_high": 7.5,   # most restrictive
        "caution_low": 7.1, "caution_high": 7.7,
    },
}

# ──────────────────────────────────────────────────────────────────────
#  Condition overrides — these tighten thresholds on top of base type
# ──────────────────────────────────────────────────────────────────────
CONDITION_PH_OVERRIDES: Dict[str, Dict[str, float]] = {
    "eczema":    {"safe_low": 7.2, "safe_high": 7.5, "caution_low": 7.0, "caution_high": 7.7},
    "psoriasis": {"safe_low": 7.2, "safe_high": 7.6, "caution_low": 7.0, "caution_high": 7.8},
    "rosacea":   {"safe_low": 7.2, "safe_high": 7.5, "caution_low": 7.1, "caution_high": 7.7},
    "acne":      {"safe_low": 7.0, "safe_high": 7.6, "caution_low": 6.8, "caution_high": 7.8},
}

# ──────────────────────────────────────────────────────────────────────
#  ORP (Chlorine) thresholds
#  High ORP = high free chlorine → irritates eyes, skin, airways
# ──────────────────────────────────────────────────────────────────────
ORP_SAFE_HIGH_DEFAULT  = 750   # mV
ORP_SAFE_HIGH_EYE      = 720   # mV — stricter for eye sensitivity
ORP_SAFE_HIGH_RESP     = 700   # mV — stricter for respiratory sensitivity
ORP_SAFE_LOW           = 600   # mV — below this = under-disinfected (risk of bacteria)
ORP_CAUTION_LOW        = 550   # mV

# ──────────────────────────────────────────────────────────────────────
#  TDS — chloramine proxy (high TDS correlates with chloramine buildup)
# ──────────────────────────────────────────────────────────────────────
TDS_SAFE_HIGH_DEFAULT  = 500   # ppm
TDS_SAFE_HIGH_RESP     = 400   # ppm — stricter for asthma/respiratory
TDS_CAUTION_HIGH       = 800   # ppm

# ──────────────────────────────────────────────────────────────────────
#  Turbidity — general
# ──────────────────────────────────────────────────────────────────────
TURB_SAFE  = 50   # NTU
TURB_CAUTION = 100  # NTU

# ──────────────────────────────────────────────────────────────────────
#  Temperature — pool swimming comfort and microbial risk
# ──────────────────────────────────────────────────────────────────────
TEMP_SAFE_LOW  = 26.0   # °C
TEMP_SAFE_HIGH = 32.0   # °C
TEMP_CAUTION_LOW  = 22.0
TEMP_CAUTION_HIGH = 35.0


def _get_effective_ph_thresholds(skin_profile: Dict[str, Any]) -> Dict[str, float]:
    """Return the tightest applicable pH thresholds for this user."""
    skin_type = skin_profile.get("skin_type", "normal").lower()
    thresholds = dict(SKIN_PH_THRESHOLDS.get(skin_type, SKIN_PH_THRESHOLDS["normal"]))

    # Conditions tighten the range further
    conditions = [c.lower() for c in skin_profile.get("conditions", [])]
    for cond in conditions:
        if cond in CONDITION_PH_OVERRIDES:
            override = CONDITION_PH_OVERRIDES[cond]
            # Tightest wins
            thresholds["safe_low"]    = max(thresholds["safe_low"],    override["safe_low"])
            thresholds["safe_high"]   = min(thresholds["safe_high"],   override["safe_high"])
            thresholds["caution_low"] = max(thresholds["caution_low"], override["caution_low"])
            thresholds["caution_high"]= min(thresholds["caution_high"],override["caution_high"])

    return thresholds


def _evaluate_ph(ph: float, thresholds: Dict[str, float]) -> Tuple[str, str, str]:
    """Returns (status, label, advice)."""
    if ph < thresholds["caution_low"] or ph > thresholds["caution_high"]:
        return "unsafe", f"pH {ph:.2f}", (
            f"pH {ph:.2f} is outside safe limits for your skin type. "
            f"This level can disrupt your skin barrier and cause irritation or dryness."
        )
    elif ph < thresholds["safe_low"] or ph > thresholds["safe_high"]:
        return "caution", f"pH {ph:.2f}", (
            f"pH {ph:.2f} is slightly outside the ideal range for your skin. "
            f"Short exposure is likely fine; avoid prolonged swimming."
        )
    return "safe", f"pH {ph:.2f}", f"pH {ph:.2f} is within the optimal range for your skin type."


def _evaluate_orp(orp: float, skin_profile: Dict[str, Any]) -> Tuple[str, str, str]:
    """Returns (status, label, advice)."""
    has_eye_sensitivity  = skin_profile.get("eye_sensitive", False)
    has_resp_sensitivity = skin_profile.get("respiratory_sensitive", False)

    orp_safe_high = ORP_SAFE_HIGH_DEFAULT
    if has_eye_sensitivity:
        orp_safe_high = min(orp_safe_high, ORP_SAFE_HIGH_EYE)
    if has_resp_sensitivity:
        orp_safe_high = min(orp_safe_high, ORP_SAFE_HIGH_RESP)

    if orp < ORP_CAUTION_LOW:
        return "unsafe", f"ORP {orp:.0f} mV", (
            "Chlorine level is critically low — water may harbour bacteria, algae, or pathogens. "
            "Avoid swimming."
        )
    elif orp < ORP_SAFE_LOW:
        return "caution", f"ORP {orp:.0f} mV", (
            f"Chlorine residual is below the safe minimum ({ORP_SAFE_LOW} mV). "
            "Disinfection effectiveness may be reduced."
        )
    elif orp > orp_safe_high:
        extra = ""
        if has_eye_sensitivity:
            extra += " High chlorine can cause significant eye redness and irritation for you."
        if has_resp_sensitivity:
            extra += " Elevated chloramine vapours may trigger respiratory discomfort."
        return "caution", f"ORP {orp:.0f} mV", (
            f"Chlorine level is higher than ideal for your sensitivities ({orp_safe_high} mV limit).{extra}"
        )
    return "safe", f"ORP {orp:.0f} mV", "Chlorine (ORP) level is safe for your sensitivities."


def _evaluate_tds(tds: float, skin_profile: Dict[str, Any]) -> Tuple[str, str, str]:
    """Returns (status, label, advice)."""
    has_resp = skin_profile.get("respiratory_sensitive", False)
    tds_limit = TDS_SAFE_HIGH_RESP if has_resp else TDS_SAFE_HIGH_DEFAULT

    if tds > TDS_CAUTION_HIGH:
        return "unsafe", f"TDS {tds:.0f} ppm", (
            f"Total dissolved solids are very high ({tds:.0f} ppm). "
            "This level indicates heavy chloramine buildup which can cause skin and respiratory irritation."
        )
    elif tds > tds_limit:
        msg = f"TDS {tds:.0f} ppm is above the recommended limit ({tds_limit} ppm) for your profile."
        if has_resp:
            msg += " Chloramine byproducts at this level may worsen respiratory symptoms."
        return "caution", f"TDS {tds:.0f} ppm", msg
    return "safe", f"TDS {tds:.0f} ppm", "Dissolved solids are within a safe range."


def _evaluate_turbidity(turbidity: float) -> Tuple[str, str, str]:
    """Returns (status, label, advice)."""
    if turbidity > TURB_CAUTION:
        return "unsafe", f"Turbidity {turbidity:.1f} NTU", (
            "Water visibility is very poor. High turbidity can conceal contaminants and pathogens. "
            "Avoid swimming until it clears."
        )
    elif turbidity > TURB_SAFE:
        return "caution", f"Turbidity {turbidity:.1f} NTU", (
            "Water clarity is slightly reduced. This may indicate elevated particulates or algae."
        )
    return "safe", f"Turbidity {turbidity:.1f} NTU", "Water clarity is good."


def _evaluate_temperature(temp: float) -> Tuple[str, str, str]:
    """Returns (status, label, advice)."""
    if temp < TEMP_CAUTION_LOW or temp > TEMP_CAUTION_HIGH:
        return "unsafe", f"Temp {temp:.1f} °C", (
            f"Water temperature ({temp:.1f} °C) is outside safe swimming range. "
            "Hypothermia or heat-related illness risk is elevated."
        )
    elif temp < TEMP_SAFE_LOW or temp > TEMP_SAFE_HIGH:
        return "caution", f"Temp {temp:.1f} °C", (
            f"Water temperature ({temp:.1f} °C) is slightly outside the comfortable swimming range (26–32 °C)."
        )
    return "safe", f"Temp {temp:.1f} °C", "Water temperature is comfortable for swimming."


# ──────────────────────────────────────────────────────────────────────
#  STATUS ORDERING
# ──────────────────────────────────────────────────────────────────────
STATUS_RANK = {"safe": 0, "caution": 1, "unsafe": 2}
STATUS_LABELS = {
    "safe":   "SAFE FOR YOU",
    "caution":"USE CAUTION",
    "unsafe": "NOT SAFE FOR YOU",
}

# Score mapping: unsafe parameters penalise the score heavily
PARAM_WEIGHT = {"ph": 35, "orp": 25, "tds": 20, "turbidity": 10, "temperature": 10}
PENALTY      = {"safe": 0, "caution": 0.5, "unsafe": 1.0}


def assess(reading: Dict[str, Any], skin_profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entry point.

    Args:
        reading: dict with keys: ph, tds, turbidity, temperature, orp
                 (orp is optional — v0.5 hardware may not have it)
        skin_profile: dict with keys:
            skin_type: "normal" | "dry" | "oily" | "combination" | "sensitive"
            conditions: list of "eczema" | "psoriasis" | "rosacea" | "acne" | "none"
            eye_sensitive: bool
            respiratory_sensitive: bool

    Returns:
        dict with personal_status, score (0-100), concerns, parameter_breakdown, advice
    """

    ph_thresh = _get_effective_ph_thresholds(skin_profile)

    # Evaluate each parameter
    evaluations: Dict[str, Tuple[str, str, str]] = {}
    evaluations["ph"]          = _evaluate_ph(reading.get("ph", 7.2), ph_thresh)
    evaluations["tds"]         = _evaluate_tds(reading.get("tds", 300), skin_profile)
    evaluations["turbidity"]   = _evaluate_turbidity(reading.get("turbidity", 10))
    evaluations["temperature"] = _evaluate_temperature(reading.get("temperature", 28))

    # ORP is optional (v0.5 hardware doesn't have it)
    orp_present = reading.get("orp") is not None
    if orp_present:
        evaluations["orp"] = _evaluate_orp(reading["orp"], skin_profile)
    else:
        # Mark as N/A — excluded from scoring weight so score stays accurate
        evaluations["orp"] = ("safe", "ORP N/A", "ORP sensor not present in this reading.")

    # Overall status = worst across parameters that are actually measured
    overall_status = max(
        (evaluations[p][0] for p in evaluations),
        key=lambda s: STATUS_RANK[s]
    )

    # Score 0–100: only count weight for parameters actually measured
    scored_params = [p for p in evaluations if p != "orp" or orp_present]
    total_weight  = sum(PARAM_WEIGHT[p] for p in scored_params)
    total_penalty = sum(
        PARAM_WEIGHT[p] * PENALTY[evaluations[p][0]]
        for p in scored_params
    )
    score = round(100 * (1 - total_penalty / total_weight))

    # Build concerns list (non-safe parameters)
    concerns: List[Dict[str, str]] = []
    for param, (status, label, advice) in evaluations.items():
        if status != "safe":
            concerns.append({"parameter": param, "label": label, "status": status, "advice": advice})

    # Build full parameter breakdown
    parameter_breakdown: List[Dict[str, str]] = []
    for param, (status, label, advice) in evaluations.items():
        parameter_breakdown.append({
            "parameter": param,
            "label": label,
            "status": status,
            "advice": advice,
        })

    # Overall advice sentence
    if overall_status == "safe":
        advice_text = (
            "Water quality looks great for your skin profile. Enjoy your swim! 🏊"
        )
    elif overall_status == "caution":
        advice_text = (
            "Water conditions are borderline for your skin type. "
            "Keep your swim short, rinse off immediately after, and moisturise."
        )
    else:
        advice_text = (
            "Current water conditions are NOT recommended for your skin type. "
            "Please wait until parameters improve before entering the water."
        )

    return {
        "personal_status":     overall_status,
        "status_label":        STATUS_LABELS[overall_status],
        "score":               score,
        "concerns":            concerns,
        "parameter_breakdown": parameter_breakdown,
        "advice":              advice_text,
        "skin_type_used":      skin_profile.get("skin_type", "normal"),
        "conditions_used":     skin_profile.get("conditions", []),
    }
