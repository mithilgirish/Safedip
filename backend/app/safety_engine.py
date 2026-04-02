from typing import Tuple, List

def evaluate_safety(p) -> Tuple[str, List[Tuple[str, str]]]:
    """
    Returns (safety_status, [(alert_message, severity), ...])
    Evaluates pH, TDS, Turbidity, Temperature, and ORP against safe limits.
    """
    unsafe_msgs  = []
    caution_msgs = []

    # pH (Safe: 7.2-7.6, Caution: 7.0-7.8, Unsafe: <6.8 or >8.0)
    if p.ph < 6.8 or p.ph > 8.0:
        unsafe_msgs.append((f"pH {p.ph:.2f} is outside safe limits (6.8–8.0).", "unsafe"))
    elif p.ph < 7.0 or p.ph > 7.19 or p.ph > 7.61 and p.ph < 7.8:
        caution_msgs.append((f"pH {p.ph:.2f} is approaching limits.", "caution"))

    # TDS (Safe: 0-500, Caution: 0-1000, Unsafe: >1000)
    if p.tds > 1000:
        unsafe_msgs.append((f"TDS {p.tds:.0f} ppm exceeds unsafe threshold (>1000 ppm).", "unsafe"))
    elif p.tds > 501:
        caution_msgs.append((f"TDS {p.tds:.0f} ppm is high (>500 ppm).", "caution"))

    # Turbidity (Safe: 0-50, Caution: 0-100, Unsafe: >100)
    if p.turbidity > 100:
        unsafe_msgs.append((f"Turbidity {p.turbidity:.1f} NTU is unsafe (>100 NTU).", "unsafe"))
    elif p.turbidity > 51:
        caution_msgs.append((f"Turbidity {p.turbidity:.1f} NTU is elevated (>50 NTU).", "caution"))

    # Temperature (Safe: 26-32, Caution: 20-35, Unsafe: <18 or >38)
    if p.temperature < 18 or p.temperature > 38:
        unsafe_msgs.append((f"Temperature {p.temperature:.1f}°C is dangerous.", "unsafe"))
    elif p.temperature < 26 or p.temperature > 32:
        caution_msgs.append((f"Temperature {p.temperature:.1f}°C is outside ideal range.", "caution"))

    # ORP (Safe: 650-750, Caution: 600-800, Unsafe: <550 or >850)
    if p.orp < 550 or p.orp > 850:
        unsafe_msgs.append((f"ORP {p.orp:.0f} mV is critical (<550 or >850 mV).", "unsafe"))
    elif p.orp < 650 or p.orp > 750:
        caution_msgs.append((f"ORP {p.orp:.0f} mV is outside safe range.", "caution"))

    if unsafe_msgs:
        return "unsafe", unsafe_msgs + caution_msgs
    elif caution_msgs:
        return "caution", caution_msgs
    
    return "safe", []
