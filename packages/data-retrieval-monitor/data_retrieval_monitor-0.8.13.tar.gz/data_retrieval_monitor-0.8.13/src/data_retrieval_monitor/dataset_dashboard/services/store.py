import os, json, tempfile, threading, pathlib
from typing import Dict, List, Optional, Tuple
from ..constants import JOB_STATUS_ORDER
from ..utils import utc_now_iso

class StoreService:
    """Holds payloads + aggregations. Memory or file-backed via config."""
    def __init__(self, backend: str, store_path: str, default_owner: str, default_mode: str):
        self.backend = backend
        self.store_path = store_path
        self.default_owner = default_owner
        self.default_mode = default_mode
        self._lock = threading.RLock()
        self._mem: Optional[dict] = None
        self._cache: Optional[dict] = None
        self._mtime: Optional[float] = None
        self._ensure()

    def _init(self) -> dict:
        return {
            "jobs": {},
            "logs": [],
            "meta": {
                "owner_labels": {},
                "env": "demo",
                "last_ingest_at": None,
            },
            "updated_at": utc_now_iso()
        }

    def _ensure(self):
        if self.backend == "memory":
            if self._mem is None: self._mem = self._init()
            return
        p = pathlib.Path(self.store_path)
        if not p.exists():
            p.write_text(json.dumps(self._init(), indent=2))

    def _load(self) -> dict:
        self._ensure()
        if self.backend == "memory":
            return self._mem
        mtime = os.path.getmtime(self.store_path)
        if self._cache is not None and self._mtime == mtime:
            return self._cache
        with open(self.store_path, "rb") as f:
            data = json.loads(f.read().decode("utf-8"))
        self._cache, self._mtime = data, mtime
        return data

    def _save(self, store: dict):
        store["updated_at"] = utc_now_iso()
        logs = store.setdefault("logs", [])
        if len(logs) > 2000: store["logs"] = logs[-2000:]
        if self.backend == "memory":
            with self._lock: self._mem = store
            return
        dir_ = os.path.dirname(os.path.abspath(self.store_path)) or "."
        fd, tmp = tempfile.mkstemp(prefix="store.", suffix=".tmp", dir=dir_)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as w:
                json.dump(store, w, indent=2)
            os.replace(tmp, self.store_path)
            self._cache = store
            self._mtime = os.path.getmtime(self.store_path)
        finally:
            try:
                if os.path.exists(tmp): os.remove(tmp)
            except Exception:
                pass

    # shape helpers
    def _ensure_leaf(self, store, owner: str, mode: str, data_name: str, stage: str) -> dict:
        jobs = store.setdefault("jobs", {})
        o = jobs.setdefault(owner, {})
        m = o.setdefault(mode, {})
        d = m.setdefault(data_name, {})
        return d.setdefault(stage, {"chunks": [], "counts": {s:0 for s in JOB_STATUS_ORDER}, "errors": []})

    def _recount(self, leaf: dict):
        leaf["counts"] = {s:0 for s in JOB_STATUS_ORDER}
        for ch in leaf.get("chunks", []):
            st = (ch.get("status") or "waiting").lower()
            if st in leaf["counts"]:
                leaf["counts"][st] += 1

    # public API
    def state(self) -> dict:
        return self._load()

    def apply_snapshot_with_meta(self, items: List[dict], meta: Optional[dict] = None):
        """Apply snapshot + optional meta: {'env':..., 'ingested_at':..., 'last_ingest_at':...}"""
        store = self._load()

        # update meta
        meta = meta or {}
        store_meta = store.setdefault("meta", {})
        if "env" in meta:
            store_meta["env"] = meta.get("env") or store_meta.get("env") or "demo"
        # allow either key
        ingest_when = meta.get("last_ingest_at") or meta.get("ingested_at") or utc_now_iso()
        store_meta["last_ingest_at"] = ingest_when

        # reset jobs then refill
        store["jobs"] = {}
        for it in items or []:
            owner = (it.get("owner") or self.default_owner).strip().lower()
            mode  = (it.get("mode")  or self.default_mode).strip().lower()
            dn    = it.get("data_name") or "unknown"
            stg   = (it.get("stage") or "stage").lower()
            leaf = self._ensure_leaf(store, owner, mode, dn, stg)
            leaf["chunks"] = list(it.get("chunks", []))
            leaf["errors"] = list(it.get("errors", []))[-50:] if isinstance(it.get("errors"), list) else []
            self._recount(leaf)

        self._save(store)

    def apply_snapshot(self, items: List[dict]):
        """Backwards-compat: apply without meta; still stamps last_ingest_at now."""
        self.apply_snapshot_with_meta(items, meta={})

    def list_filters(self) -> Tuple[list, list]:
        store = self._load()
        jobs = store.get("jobs", {})
        labels = store.get("meta", {}).get("owner_labels", {})
        owner_opts = [{"label":"All","value":"All"}] + [{"label":labels.get(k,k), "value":k} for k in sorted(jobs.keys())]
        modes = set()
        for o_map in jobs.values(): modes.update(o_map.keys())
        mode_opts = [{"label":"All","value":"All"}] + [{"label":m.title(),"value":m} for m in sorted(modes)]
        return owner_opts, mode_opts