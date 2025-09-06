from typing import Tuple, Dict

# exact order you asked for:
STAGES = ["archive", "stage", "enrich", "consolidate"]

JOB_STATUS_ORDER = ["failed", "overdue", "manual", "retrying", "running", "waiting", "succeeded"]

JOB_COLORS: Dict[str, str] = {
    "waiting":   "#F0E442",
    "retrying":  "#E69F00",
    "running":   "#56B4E9",
    "failed":    "#D55E00",
    "overdue":   "#A50E0E",
    "manual":    "#808080",
    "succeeded": "#009E73",
}

JOB_SCORES: Dict[str, float] = {
    "failed": -1.0,
    "overdue": -0.8,
    "retrying": -0.3,
    "running": 0.5,
    "waiting": 0.0,
    "manual": 0.2,
    "succeeded": 1.0,
}

def _hex_to_rgb(h: str) -> Tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

JOB_RGB = {k: _hex_to_rgb(v) for k, v in JOB_COLORS.items()}