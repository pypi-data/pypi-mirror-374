import random
from typing import List, Tuple, Dict
from .constants import STAGES
from .config import AppConfig
from .utils import utc_now_iso

_STATUSES = ["waiting", "retrying", "running", "failed", "overdue", "manual", "succeeded"]

def make_dummy_payload(cfg: AppConfig, num_datasets: int = 10) -> Tuple[List[dict], Dict]:
    """Return (items, meta) for the injector. Meta carries env + ingested_at."""
    random.seed()
    items: List[dict] = []
    for i in range(num_datasets):
        dn = f"dataset-{i:03d}"
        mode = cfg.default_mode if (i % 3) else "backfill"
        for stg in STAGES:
            k = random.randint(2, 5)
            chs = [{
                "id": f"{stg[:1].upper()}{i:02d}-{j}",
                "status": random.choice(_STATUSES),
                "proc": f"https://example.com/proc/{dn}/{stg}/{j}",
                "log": f"{dn}/{stg}-{j}.log",
            } for j in range(k)]
            items.append({
                "owner": cfg.default_owner.lower(),
                "mode": mode.lower(),
                "data_name": dn,
                "stage": stg,
                "chunks": chs,
                "errors": [],
            })
    meta = {"env": cfg.environment_label, "ingested_at": utc_now_iso()}
    return items, meta