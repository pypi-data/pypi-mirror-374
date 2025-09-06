from typing import Dict, List, Optional, Tuple
from ..constants import JOB_STATUS_ORDER, JOB_SCORES

def best_status(counts: Dict[str,int]) -> Optional[str]:
    for s in JOB_STATUS_ORDER:
        if int(counts.get(s, 0) or 0) > 0:
            return s
    return None

def aggregate_counts(store: dict) -> Dict[str,int]:
    tot = {s:0 for s in JOB_STATUS_ORDER}
    for o_map in store.get("jobs", {}).values():
        for m_map in o_map.values():
            for d_map in m_map.values():
                for leaf in d_map.values():
                    for s, v in leaf["counts"].items():
                        tot[s] += int(v or 0)
    return tot

def filtered_stage_counts(store: dict, owner: Optional[str], mode: Optional[str], stage: str) -> Dict[str,int]:
    owner_sel = (owner or "").lower(); want_owner = None if owner_sel in ("","all") else owner_sel
    mode_sel  = (mode  or "").lower(); want_mode  = None if mode_sel  in ("","all") else mode_sel
    tot = {s:0 for s in JOB_STATUS_ORDER}
    for own, o_map in store.get("jobs", {}).items():
        if want_owner and own != want_owner: continue
        for md, m_map in o_map.items():
            if want_mode and md != want_mode: continue
            for d_map in m_map.values():
                leaf = d_map.get(stage)
                if not leaf: continue
                for s, v in leaf["counts"].items():
                    tot[s] += int(v or 0)
    return tot

def _avg_scores_for(d_map: dict, sel_stages: List[str]) -> Tuple[float, float]:
    chunk_scores: List[float] = []
    status_set: set = set()
    for stg in sel_stages:
        leaf = d_map.get(stg)
        if not leaf: continue
        for ch in leaf.get("chunks", []):
            st = (ch.get("status") or "waiting").lower()
            chunk_scores.append(JOB_SCORES.get(st, 0.0))
            status_set.add(st)
    avg_chunk = (sum(chunk_scores)/len(chunk_scores)) if chunk_scores else 0.0
    avg_status = (sum(JOB_SCORES.get(s,0.0) for s in status_set)/len(status_set)) if status_set else 0.0
    return avg_chunk, avg_status

def make_sort_key(d_map: dict, dataset_name: str, owner: str, mode: str,
                  sel_stages: List[str], kind: str) -> Tuple:
    avg_chunk, avg_status = _avg_scores_for(d_map, sel_stages)
    if kind == "chunk_asc":   sk = ( avg_chunk, dataset_name.lower(), owner.lower(), mode.lower())
    elif kind == "chunk_desc":   sk = (-avg_chunk, dataset_name.lower(), owner.lower(), mode.lower())
    elif kind == "status_asc":   sk = ( avg_status, dataset_name.lower(), owner.lower(), mode.lower())
    elif kind == "status_desc":  sk = (-avg_status, dataset_name.lower(), owner.lower(), mode.lower())
    else:                        sk = ( dataset_name.lower(), owner.lower(), mode.lower())
    return sk