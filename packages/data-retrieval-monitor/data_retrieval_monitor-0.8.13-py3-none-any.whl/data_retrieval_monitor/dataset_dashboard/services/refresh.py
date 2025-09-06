from typing import List, Optional, Dict, Tuple
from datetime import datetime
import pytz
from dash import html

from ..config import AppConfig
from ..store import DatasetStore
from ..constants import STAGES, JOB_STATUS_ORDER, JOB_SCORES
from ..logs import LogLinker
from ..components.table import best_status, chunk_line, build_table_component

class RefreshService:
    def __init__(self, cfg: AppConfig, store: DatasetStore, linker: LogLinker):
        self.cfg = cfg
        self.store = store
        self.linker = linker
        self._tz = pytz.timezone(cfg.timezone)

    def kpis(self):
        k = self.store.aggregate_counts()
        return [str(k.get(s, 0)) for s in ["waiting","retrying","running","failed","overdue","manual","succeeded"]]

    def pies(self, owner: Optional[str], mode: Optional[str]):
        return {stg: self.store.filtered_stage_counts(owner, mode, stg) for stg in STAGES}

    # ---- sorting helpers ----
    def _score_entry(self, d_map: dict, sel_stages: List[str]) -> Tuple[float, float]:
        chunk_scores: List[float] = []
        status_set: set = set()
        for stg in sel_stages:
            leaf = d_map.get(stg)
            if not leaf: continue
            for ch in leaf.get("chunks", []):
                st = (ch.get("status") or "waiting").lower()
                chunk_scores.append(JOB_SCORES.get(st, 0.0))
                status_set.add(st)
        avg_chunk = (sum(chunk_scores) / len(chunk_scores)) if chunk_scores else 0.0
        avg_status = (sum(JOB_SCORES.get(s, 0.0) for s in status_set) / len(status_set)) if status_set else 0.0
        return avg_chunk, avg_status

    def _gather_dataset_groups(self, store_dict: dict, owner: Optional[str], mode: Optional[str],
                               stage_filter: list, status_filter: list, sort_by: str) -> List[List[html.Td]]:
        owner_sel = (owner or "").lower()
        mode_sel  = (mode  or "").lower()
        want_owner = None if owner_sel in ("", "all") else owner_sel
        want_mode  = None if mode_sel  in ("", "all") else mode_sel

        sel_stages = [s for s in (stage_filter or []) if s in STAGES] or STAGES[:]
        sel_status = [s for s in (status_filter or []) if s in JOB_STATUS_ORDER]
        filter_by_status = len(sel_status) > 0

        # collect entries with sort keys
        entries: List[Tuple] = []  # (sort_key, own, md, dn, d_map)
        for own in sorted(store_dict.get("jobs", {}).keys()):
            if want_owner and own != want_owner: continue
            o_map = store_dict["jobs"][own]
            for md in sorted(o_map.keys()):
                if want_mode and md != want_mode: continue
                m_map = o_map[md]
                for dn in sorted(m_map.keys()):
                    d_map = m_map[dn]
                    stage_stat = {stg: best_status((d_map.get(stg) or {"counts":{}})["counts"]) for stg in STAGES}
                    if filter_by_status and not any((stage_stat.get(stg) in sel_status) for stg in sel_stages):
                        continue
                    avg_chunk, avg_status = self._score_entry(d_map, sel_stages)
                    if sort_by == "chunk_asc":
                        sk = (avg_chunk, dn.lower(), own.lower(), md.lower())
                    elif sort_by == "chunk_desc":
                        sk = (-avg_chunk, dn.lower(), own.lower(), md.lower())
                    elif sort_by == "status_asc":
                        sk = (avg_status, dn.lower(), own.lower(), md.lower())
                    elif sort_by == "status_desc":
                        sk = (-avg_status, dn.lower(), own.lower(), md.lower())
                    else:  # name_asc
                        sk = (dn.lower(), own.lower(), md.lower())
                    entries.append((sk, own, md, dn, d_map))

        entries.sort(key=lambda x: x[0])

        groups = []
        labels = store_dict.get("meta", {}).get("owner_labels", {})
        for _, own, md, dn, d_map in entries:
            stage_stat = {stg: best_status((d_map.get(stg) or {"counts":{}})["counts"]) for stg in STAGES}
            owner_label = labels.get(own, own)
            title = dn if want_owner else f"{owner_label} / {dn}"
            cells = [html.Td(title, style={"fontWeight":"600","whiteSpace":"nowrap"})]
            for stg in STAGES:
                leaf = d_map.get(stg, {"counts":{s:0 for s in JOB_STATUS_ORDER}, "chunks":[]})
                style = {"verticalAlign":"top","padding":"6px 10px","whiteSpace":"nowrap"}
                cells.append(html.Td(chunk_line(leaf.get("chunks", []), self.linker), style=style))
            groups.append(cells)
        return groups

    def table(self, owner: Optional[str], mode: Optional[str], stage_filter: list,
              status_filter: list, groups_per_row: int, sort_by: str):
        store_dict = self.store.state()
        groups = self._gather_dataset_groups(store_dict, owner, mode, stage_filter, status_filter, sort_by or "name_asc")
        return build_table_component(groups, groups_per_row)

    def status_line(self) -> str:
        now_local = datetime.now(self._tz).strftime("%Y-%m-%d %H:%M:%S %Z")
        return f"Refreshed: {now_local}"