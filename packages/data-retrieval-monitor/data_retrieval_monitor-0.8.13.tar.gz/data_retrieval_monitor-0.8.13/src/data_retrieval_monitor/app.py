"""
Data Retrieval Monitor — side-by-side (no wrap) with:
- Placeholder pies (render even with zero data).
- Repeatable table groups (1..6 groups per row).
- Table width sizes to content (no table-level horizontal scrollbar).
- In-memory log cache + safe on-disk fallback (for /logview/...).
- LOG_LINK_MODE: "raw" opens /rawpath?p=...; "view" opens /logview/...
- Configurable chunk wrapping (N chunks per visual line in each stage cell).
- Banner shows: Environment + Last Ingested (from feeder).

Endpoints:
  POST /ingest_snapshot  (or /feed)  -> replace all state
  POST /store/reset?seed=1           -> clear store (tiny seed optional)
  GET  /logview/<path:key>           -> HTML page rendering cached/disk log text
  GET  /logmem/<path:key>            -> raw text (debug)
  GET  /rawpath?p=<raw>              -> tiny page to view/copy raw path

Payload:
  {"snapshot": items, "meta": {"ingested_at": "...", "env": "QA"}}

Env:
  DEFAULT_OWNER (default "QSG")
  DEFAULT_MODE  (default "live")
  REFRESH_MS (default 1000)
  STORE_BACKEND=memory|file, STORE_PATH
  APP_TIMEZONE (default Europe/London)
  LOG_ROOT (default "/tmp/drm-logs")     # base for on-disk logs
  LOG_GLOBS (default "*.log,*.txt")      # optional preload patterns under LOG_ROOT
  LOG_LINK_MODE (default "raw")          # "raw" | "view"
  MAX_PAGE_WIDTH (default 2400), MAX_LEFT_WIDTH (default 360),
  MAX_GRAPH_WIDTH (default 440), MAX_KPI_WIDTH (default 220)
"""

import os, json, tempfile, pathlib, threading, hashlib
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote, quote_plus, urlparse, unquote_plus
from html import escape as html_escape

import pytz
from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from flask import request, jsonify, Response, abort

# ---------------- Config ----------------
APP_TITLE     = "Data Retrieval Monitor"
TIMEZONE      = os.getenv("APP_TIMEZONE", "Europe/London")
_DEF_TZ       = pytz.timezone(TIMEZONE)
REFRESH_MS    = int(os.getenv("REFRESH_MS", "1000"))
STORE_BACKEND = os.getenv("STORE_BACKEND", "memory")  # memory | file
STORE_PATH    = os.getenv("STORE_PATH", "status_store.json")

DEFAULT_OWNER = os.getenv("DEFAULT_OWNER", "QSG")
DEFAULT_MODE  = os.getenv("DEFAULT_MODE",  "live")

LOG_ROOT      = pathlib.Path(os.getenv("LOG_ROOT", "/tmp/drm-logs")).resolve()
LOG_GLOBS     = [g.strip() for g in os.getenv("LOG_GLOBS", "*.log,*.txt").split(",") if g.strip()]
LOG_LINK_MODE = os.getenv("LOG_LINK_MODE", "raw").lower().strip()  # "raw" or "view"

# Layout caps (px)
MAX_PAGE_WIDTH  = int(os.getenv("MAX_PAGE_WIDTH",  "2400"))
MAX_LEFT_WIDTH  = int(os.getenv("MAX_LEFT_WIDTH",  "360"))
MAX_GRAPH_WIDTH = int(os.getenv("MAX_GRAPH_WIDTH", "440"))
MAX_KPI_WIDTH   = int(os.getenv("MAX_KPI_WIDTH",   "220"))
def _px(n: int) -> str:
    """Return a CSS pixel string for integer `n`, e.g. 360 -> '360px'."""
    return f"{int(n)}px"

# Stages (fixed, and display order)
STAGES = ["stage", "archive", "enrich", "consolidate"]

# Statuses (worst → best) + scoring for urgency sorting
STATUS_SCORES = {
    "failed":    -1.0,
    "retrying":  -0.5,
    "waiting":   -0.25,
    "queued":    -0.25,
    "running":    0.0,
    "succeeded":  1.0,
    "manual":    20.0,
    "other":     20.0,   # unseen -> map to "other"
}
JOB_STATUS_ORDER = ["failed", "overdue", "manual", "retrying", "running", "waiting", "queued", "succeeded", "other"]

JOB_COLORS = {
    "waiting":   "#F0E442",
    "retrying":  "#E69F00",
    "running":   "#56B4E9",
    "failed":    "#D55E00",
    "overdue":   "#A50E0E",
    "manual":    "#808080",
    "queued":    "#B3B3B3",
    "succeeded": "#009E73",
    "other":     "#999999",
}
def _hex_to_rgb(h):
    """Convert a hex color '#RRGGBB' into an (r,g,b) integer tuple."""
    h=h.lstrip("#"); return tuple(int(h[i:i+2],16) for i in (0,2,4))
JOB_RGB = {k: _hex_to_rgb(v) for k, v in JOB_COLORS.items()}

def utc_now_iso() -> str:
    """Return current UTC time in ISO-8601 string with timezone."""
    return datetime.now(timezone.utc).isoformat()

# ---------------- Store ----------------
STORE_LOCK = threading.RLock()
_MEM_STORE = None
_STORE_CACHE = None
_STORE_MTIME = None

def _init_store() -> dict:
    """Create a fresh store dict with default meta/logs/jobs."""
    return {"jobs": {}, "logs": [], "meta": {"owner_labels": {}, "env": None, "ingested_at": None}, "updated_at": utc_now_iso()}

def ensure_store() -> None:
    """Ensure a backing store exists (in-memory or file-backed)."""
    global _MEM_STORE
    if STORE_BACKEND == "memory":
        if _MEM_STORE is None:
            _MEM_STORE = _init_store()
        return
    p = pathlib.Path(STORE_PATH)
    if not p.exists():
        p.write_text(json.dumps(_init_store(), indent=2))

def load_store() -> dict:
    """Load the store into memory (cache file-backed loads by mtime)."""
    ensure_store()
    if STORE_BACKEND == "memory":
        return _MEM_STORE
    global _STORE_CACHE, _STORE_MTIME
    with STORE_LOCK:
        mtime = os.path.getmtime(STORE_PATH)
        if _STORE_CACHE is not None and _STORE_MTIME == mtime:
            return _STORE_CACHE
        with open(STORE_PATH, "rb") as f:
            data = json.loads(f.read().decode("utf-8"))
        _STORE_CACHE, _STORE_MTIME = data, mtime
        return data

def save_store(store: dict) -> None:
    """Persist store to memory or atomically replace the file if file-backed."""
    store["updated_at"] = utc_now_iso()
    logs = store.setdefault("logs", [])
    if len(logs) > 2000:
        store["logs"] = logs[-2000:]
    if STORE_BACKEND == "memory":
        global _MEM_STORE
        with STORE_LOCK:
            _MEM_STORE = store
        return
    with STORE_LOCK:
        dir_ = os.path.dirname(os.path.abspath(STORE_PATH)) or "."
        fd, tmp = tempfile.mkstemp(prefix="store.", suffix=".tmp", dir=dir_)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as w:
                json.dump(store, w, indent=2)
                w.flush()
                os.fsync(w.fileno())
            os.replace(tmp, STORE_PATH)
            global _STORE_CACHE, _STORE_MTIME
            _STORE_CACHE = store
            _STORE_MTIME = os.path.getmtime(STORE_PATH)
        finally:
            try:
                if os.path.exists(tmp):
                    os.remove(tmp)
            except Exception:
                pass

def _ensure_leaf(store: dict, owner: str, mode: str, data_name: str, stage: str) -> Dict:
    """
    Ensure the nested path (owner -> mode -> data_name -> stage) exists.
    Returns the leaf dict shaped as:
      {"chunks": [chunk,...], "counts": {status: int}, "errors": [str,...]}
    """
    jobs = store.setdefault("jobs", {})
    o = jobs.setdefault(owner, {})
    m = o.setdefault(mode, {})
    d = m.setdefault(data_name, {})
    return d.setdefault(stage, {"chunks": [], "counts": {s:0 for s in JOB_STATUS_ORDER}, "errors": []})

def _zero_counts(leaf: Dict) -> None:
    """Reset the leaf status counters to zero for all known statuses."""
    leaf["counts"] = {s:0 for s in JOB_STATUS_ORDER}

def _recount_from_chunks(leaf: Dict) -> None:
    """Recompute leaf['counts'] from leaf['chunks']."""
    _zero_counts(leaf)
    for ch in leaf.get("chunks", []):
        st = (ch.get("status") or "waiting").lower()
        if st not in JOB_STATUS_ORDER:
            st = "other"
        leaf["counts"][st] = leaf["counts"].get(st, 0) + 1

def reset_jobs(store: dict) -> None:
    """Clear all jobs in store; append a short log entry."""
    store["jobs"] = {}
    store.setdefault("logs", []).append({"ts": utc_now_iso(), "level":"INFO", "msg":"[SNAPSHOT] reset"})

# ---------------- Log cache (memory + safe disk fallback) ----------------
LOG_MEM: Dict[str, str] = {}
LOG_MEM_LOCK = threading.RLock()

def _read_file_safely(path: pathlib.Path) -> Optional[str]:
    """Read file as UTF-8 text (fallback to bytes->decode) and return string or None."""
    try:
        return path.read_text("utf-8", errors="replace")
    except Exception:
        try:
            return path.read_bytes().decode("utf-8", errors="replace")
        except Exception:
            return None

def preload_logs() -> None:
    """Preload logs under LOG_ROOT matching LOG_GLOBS into the in-memory cache."""
    LOG_ROOT.mkdir(parents=True, exist_ok=True)
    with LOG_MEM_LOCK:
        for pat in LOG_GLOBS:
            for p in LOG_ROOT.rglob(pat):
                rel = str(p.relative_to(LOG_ROOT)).replace("\\", "/")
                if rel in LOG_MEM:
                    continue
                txt = _read_file_safely(p)
                if txt is not None:
                    LOG_MEM[rel] = txt

def _hash_key_for_abs(abs_path: pathlib.Path) -> str:
    """Return a stable in-memory key for an absolute path (outside LOG_ROOT)."""
    s = str(abs_path)
    h = hashlib.sha1(s.encode("utf-8")).hexdigest()[:16]
    name = abs_path.name
    return f"mem/{h}/{name}"

def _safe_rel_for_log(raw: str) -> Tuple[str, bool]:
    """
    Normalize a raw log reference to a 'key' suitable for /logview.
    Returns (key, is_mem):
      - http(s) URL: (url, False)
      - under LOG_ROOT: ("relative/path", False)
      - outside LOG_ROOT but readable: ("mem/<hash>/<name>", True) and cache contents
      - missing/unreadable: ("", False)
    """
    v = (raw or "").strip()
    if not v:
        return "", False
    if v.startswith("http://") or v.startswith("https://"):
        return v, False

    p = pathlib.Path(v)
    try:
        p_abs = p.resolve()
    except Exception:
        return "", False

    try:
        rel = str(p_abs.relative_to(LOG_ROOT)).replace("\\", "/")
        return rel, False
    except Exception:
        txt = _read_file_safely(p_abs)
        if txt is None:
            return "", False
        key = _hash_key_for_abs(p_abs)
        with LOG_MEM_LOCK:
            LOG_MEM[key] = txt
        return key, True

def cache_rel_if_exists(rel: str) -> None:
    """If relative path under LOG_ROOT exists, cache its text in LOG_MEM (idempotent)."""
    p = (LOG_ROOT / rel).resolve()
    try:
        p.relative_to(LOG_ROOT)
    except Exception:
        return
    if p.exists():
        txt = _read_file_safely(p)
        if txt is not None:
            with LOG_MEM_LOCK:
                LOG_MEM.setdefault(rel, txt)

# ---------------- Apply snapshot ----------------
def apply_snapshot(store: dict, items: List[dict], env: Optional[str] = None, ingested_at: Optional[str] = None) -> None:
    """
    Replace the current job state with a full snapshot, and update meta.
    - Builds per-chunk derived fields:
        ch['log_raw']  = original raw path or URL (string or None)
        ch['log_view'] = '/logview/<key>' for viewing text (when resolvable)
    - Recomputes per-leaf status counts from chunks.
    """
    reset_jobs(store)
    meta = store.setdefault("meta", {})
    labels = meta.setdefault("owner_labels", {})
    if env is not None:
        meta["env"] = str(env)
    if ingested_at is not None:
        meta["ingested_at"] = str(ingested_at)

    for it in items or []:
        owner_raw = (it.get("owner") or DEFAULT_OWNER).strip()
        owner_key = owner_raw.lower()
        mode_raw  = (it.get("mode")  or DEFAULT_MODE).strip()
        mode_key  = mode_raw.lower()
        dn        = it.get("data_name") or "unknown"
        stg       = (it.get("stage") or "stage").lower()
        labels.setdefault(owner_key, owner_raw)

        leaf = _ensure_leaf(store, owner_key, mode_key, dn, stg)

        new_chunks: List[dict] = []
        for ch in (it.get("chunks") or []):
            ch = dict(ch or {})
            raw_log = ch.get("log")
            ch["log_raw"] = str(raw_log) if raw_log is not None else None

            # prepare /logview key (for "view" mode)
            key, is_mem = _safe_rel_for_log(str(raw_log)) if raw_log else ("", False)
            if key:
                if not is_mem:
                    cache_rel_if_exists(key)
                ch["log_view"] = f"/logview/{quote(key)}"
            else:
                ch["log_view"] = None

            new_chunks.append(ch)

        leaf["chunks"] = new_chunks
        leaf["errors"] = list(it.get("errors", []))[-50:] if isinstance(it.get("errors"), list) else []
        _recount_from_chunks(leaf)

# ---------------- Aggregation ----------------
def aggregate_counts(store: dict) -> Dict[str, int]:
    """Aggregate total counts per status across all owners/modes/datasets/stages."""
    tot = {s:0 for s in JOB_STATUS_ORDER}
    for o_map in store.get("jobs", {}).values():
        for m_map in o_map.values():
            for d_map in m_map.values():
                for leaf in d_map.values():
                    for s, v in leaf["counts"].items():
                        tot[s] = tot.get(s, 0) + int(v or 0)
    return tot

def filtered_stage_counts(store: dict, owner: Optional[str], mode: Optional[str], stage: str) -> Dict[str,int]:
    """Aggregate status counts for a single stage, filtered by owner/mode dropdowns."""
    owner_sel = (owner or "").lower()
    mode_sel  = (mode  or "").lower()
    want_owner = None if owner_sel in ("", "all") else owner_sel
    want_mode  = None if mode_sel  in ("", "all") else mode_sel
    tot = {s:0 for s in JOB_STATUS_ORDER}
    for own, o_map in store.get("jobs", {}).items():
        if want_owner and own != want_owner: continue
        for md, m_map in o_map.items():
            if want_mode and md != want_mode: continue
            for d_map in m_map.values():
                leaf = d_map.get(stage)
                if not leaf: continue
                for s, v in leaf["counts"].items():
                    tot[s] = tot.get(s, 0) + int(v or 0)
    return tot

def list_filters(store: dict):
    """Return (owner_options, mode_options) for dropdowns based on current store content."""
    jobs   = store.get("jobs", {})
    labels = store.get("meta", {}).get("owner_labels", {})
    owner_keys = set(jobs.keys()) | {DEFAULT_OWNER.lower()}
    owners = sorted(owner_keys)
    owner_opts = [{"label": "All", "value": "All"}]
    for k in owners:
        owner_opts.append({"label": labels.get(k, k), "value": k})

    modes_keys = set()
    for o_map in jobs.values():
        modes_keys.update(o_map.keys())
    modes_keys |= {"live", "backfill", DEFAULT_MODE.lower()}
    modes = sorted(modes_keys)
    mode_opts = [{"label": "All", "value": "All"}] + [{"label": m.title(), "value": m} for m in modes]
    return owner_opts, mode_opts

def best_status(counts: Dict[str,int]) -> Optional[str]:
    """Return first non-zero status in JOB_STATUS_ORDER, or None if all zero."""
    for s in JOB_STATUS_ORDER:
        if int(counts.get(s, 0) or 0) > 0:
            return s
    return None

def status_score(status: Optional[str]) -> float:
    """Map a status into a numeric score; unknown statuses are 'other'."""
    s = (status or "").lower()
    return STATUS_SCORES.get(s, STATUS_SCORES["other"])

# ---------------- UI helpers ----------------
def shade_for_status(status: Optional[str], alpha=0.18) -> dict:
    """Return a soft background-color style for status; white if unknown/None."""
    if not status or status not in JOB_RGB: return {"backgroundColor":"#FFFFFF"}
    r,g,b = JOB_RGB[status]
    return {"backgroundColor": f"rgba({r},{g},{b},{alpha})"}

def _path_only(text: Optional[str]) -> Optional[str]:
    """Return path component for http/https/file URLs, else return original text."""
    if not text:
        return None
    try:
        pr = urlparse(text)
        if pr.scheme in ("http", "https", "file"):
            return pr.path or text
    except Exception:
        pass
    return text

def _chunk_badge_and_links(ch: dict) -> List[html.Component]:
    """
    Render a chunk as: [badge] [p] [l] [clipboard]
    - 'p' links to proc if present
    - 'l' behavior:
        * LOG_LINK_MODE == "view" and log_view available -> open /logview/...
        * else if raw path available -> open /rawpath?p=<raw> (shows selectable raw path)
    - Clipboard always shows if we have a raw path (copies filesystem path/URL path).
    """
    cid  = ch.get("id") or "c?"
    st   = (ch.get("status") or "waiting").lower()
    if st not in JOB_STATUS_ORDER:
        st = "other"
    proc = ch.get("proc")
    raw  = ch.get("log_raw")
    view = ch.get("log_view")

    badge = html.Span(
        cid,
        style={
            "display":"inline-block","padding":"2px 6px","borderRadius":"8px",
            "fontSize":"12px","marginRight":"6px", **shade_for_status(st, 0.35)
        }
    )
    bits: List[html.Component] = [badge]

    if proc:
        bits.append(html.A("p", href=proc, target="_blank", title="proc", style={"marginRight":"6px"}))

    # 'l' link logic
    if LOG_LINK_MODE == "view" and view:
        bits.append(html.A("l", href=view, target="_blank", title="log (view)", style={"marginRight":"6px"}))
    else:
        # raw-mode: go to /rawpath?p=...
        raw_s = str(raw).strip() if isinstance(raw, str) else ""
        if raw_s:
            href = "/rawpath?p=" + quote_plus(raw_s)
            bits.append(html.A("l", href=href, target="_blank", title="raw path", style={"marginRight":"6px"}))

    # Clipboard (copies filesystem/URL path only)
    copy_text = _path_only(raw)
    if copy_text:
        bits.append(
            dcc.Clipboard(
                content=copy_text,
                title="Copy log path",
                style={
                    "display":"inline-block",
                    "cursor":"pointer",
                    "border":"0",
                    "background":"transparent",
                    "padding":"0 2px",
                    "marginRight":"8px",
                    "fontSize":"12px",
                    "textDecoration":"underline",
                },
                className="copy-log"
            )
        )

    return bits

def chunk_lines(chunks: List[dict], chunks_per_line: int) -> html.Div:
    """Render chunk controls as compact lines with at most N chunks per line."""
    if not chunks:
        return html.I("—", className="text-muted")
    cpl = max(1, int(chunks_per_line or 5))
    lines = []
    for i in range(0, len(chunks), cpl):
        seg = chunks[i:i+cpl]
        seg_nodes = []
        for ch in seg:
            seg_nodes.extend(_chunk_badge_and_links(ch))
        lines.append(html.Div(seg_nodes, style={"whiteSpace":"nowrap"}))
    return html.Div(lines, style={"display":"grid","rowGap":"2px"})

# -------- sorting helpers --------
def compute_dataset_score(d_map: dict, sel_stages: List[str]) -> float:
    """
    Dataset urgency score = min over selected stages of (min over that stage's chunks).
    - A stage with no chunks is ignored for scoring.
    - If all selected stages are missing/empty, score = 0.0
    This keeps “worst” (most negative) statuses bubbled to the top when sorting ascending.
    """
    has_any = False
    score = float("inf")
    for stg in sel_stages:
        leaf = d_map.get(stg)
        if not leaf: 
            continue
        chs = leaf.get("chunks") or []
        if not chs:
            continue
        has_any = True
        worst_in_stage = min(status_score((ch.get("status") or "").lower()) for ch in chs)
        score = min(score, worst_in_stage)
    if not has_any or score == float("inf"):
        return 0.0
    return score

# -------- table: collect groups, then pack N groups per row (width = content) --------
def gather_dataset_groups(store: dict, owner: Optional[str], mode: Optional[str],
                          stage_filter: List[str], status_filter: List[str],
                          chunks_per_line: int,
                          sort_by: str) -> List[List[html.Td]]:
    """
    Collect per-dataset table cells (Dataset + 4 stages) filtered by
    owner/mode/stage/status, then sort (by severity or name) and return
    a list of per-dataset cell groups (later packed into rows).
    """
    owner_sel = (owner or "").lower()
    mode_sel  = (mode  or "").lower()
    want_owner = None if owner_sel in ("", "all") else owner_sel
    want_mode  = None if mode_sel  in ("", "all") else mode_sel

    sel_stages = [s for s in (stage_filter or []) if s in STAGES] or STAGES[:]
    sel_status = [s for s in (status_filter or []) if s in JOB_STATUS_ORDER]
    filter_by_status = len(sel_status) > 0

    entries = []
    for own in sorted(store.get("jobs", {}).keys()):
        if want_owner and own != want_owner: continue
        o_map = store["jobs"][own]
        for md in sorted(o_map.keys()):
            if want_mode and md != want_mode: continue
            m_map = o_map[md]
            for dn in sorted(m_map.keys()):
                d_map = m_map[dn]
                # pick a representative status for cell shading per stage
                stage_status = {stg: best_status((d_map.get(stg) or {"counts":{}})["counts"])
                                for stg in STAGES}
                if filter_by_status and not any((stage_status.get(stg) in sel_status) for stg in sel_stages):
                    continue

                # build cells
                cells: List[html.Td] = [html.Td(dn, style={"fontWeight":"600","whiteSpace":"nowrap"})]
                for stg in STAGES:
                    leaf   = d_map.get(stg, {"counts":{s:0 for s in JOB_STATUS_ORDER}, "chunks":[]})
                    status = stage_status[stg]
                    style  = {"verticalAlign":"top","padding":"6px 10px", **shade_for_status(status, 0.18)}
                    cells.append(html.Td(chunk_lines(leaf.get("chunks", []), chunks_per_line), style=style))

                score = compute_dataset_score(d_map, sel_stages)
                entries.append({"name": dn, "cells": cells, "score": score})

    # sorting
    if sort_by == "name_asc":
        entries.sort(key=lambda e: (e["name"] or "").lower())
    else:  # "severity_asc" -> urgency worst first (more negative at top)
        entries.sort(key=lambda e: (e["score"], (e["name"] or "").lower()))

    # to groups
    return [e["cells"] for e in entries]

def chunked(iterable: List, n: int) -> List[List]:
    """Yield a list sliced into chunks of size `n`."""
    return [iterable[i:i+n] for i in range(0, len(iterable), n)]

def build_table_component(groups: List[List[html.Td]], groups_per_row: int) -> dbc.Table:
    """
    Render the dataset table with `groups_per_row` dataset-groups per table row.
    Table width sizes to content; no internal horizontal scrollbar.
    """
    gpr = max(1, min(int(groups_per_row or 1), 6))  # clamp 1..6

    # header
    head_cells = []
    for _ in range(gpr):
        head_cells.extend([
            html.Th("Dataset", style={"whiteSpace":"nowrap"}),
            html.Th("Stage"), html.Th("Archive"), html.Th("Enrich"), html.Th("Consolidate")
        ])
    head = html.Thead(html.Tr(head_cells))

    # body rows
    body_rows = []
    for row_groups in chunked(groups, gpr):
        tds: List[html.Td] = []
        for grp in row_groups:
            tds.extend(grp)
        if len(row_groups) < gpr:
            for _ in range(gpr - len(row_groups)):
                tds.extend([html.Td(""), html.Td(""), html.Td(""), html.Td(""), html.Td("")])
        body_rows.append(html.Tr(tds))

    if not body_rows:
        body_rows = [html.Tr(html.Td("No data", colSpan=5*gpr, className="text-muted"))]

    # size to content; no forced 100% width, no inner scrollbar
    return dbc.Table(
        [head, html.Tbody(body_rows)],
        bordered=True, hover=False, size="sm", className="mb-1",
        style={"tableLayout": "auto", "width": "auto", "display": "inline-block", "maxWidth": "none"}
    )

# ---------------- Pies ----------------
def pie_figure(title_text: str, counts: Dict[str,int]) -> dict:
    """
    Build a simple Plotly pie figure dict.
    - When no data, render faint equal slices with labels (placeholder pie).
    """
    labels = [s.title() for s in JOB_STATUS_ORDER]
    raw_values = [int(counts.get(s, 0) or 0) for s in JOB_STATUS_ORDER]
    total = sum(raw_values)

    colors, values, texttempl = [], [], []
    if total == 0:
        for s in JOB_STATUS_ORDER:
            r, g, b = JOB_RGB.get(s, (180,180,180))
            colors.append(f"rgba({r},{g},{b},0.12)")
            values.append(1)
            texttempl.append("%{label}")
        hover = "%{label}: 0<extra></extra>"
    else:
        for s, v in zip(JOB_STATUS_ORDER, raw_values):
            r, g, b = JOB_RGB.get(s, (180,180,180))
            colors.append(f"rgba({r},{g},{b},{0.9 if v>0 else 0.0})")
            values.append(v)
            texttempl.append("" if v == 0 else "%{label} %{percent}")
        hover = "%{label}: %{value}<extra></extra>"

    trace = {
        "type": "pie",
        "labels": labels,
        "values": values,
        "hole": 0.45,
        "marker": {"colors": colors, "line": {"width": 0}},
        "texttemplate": texttempl,
        "textposition": "outside",
        "hovertemplate": hover,
        "showlegend": True,
    }

    return {
        "data": [trace],
        "layout": {
            "annotations": [{
                "text": title_text,
                "xref": "paper", "yref": "paper",
                "x": 0.5, "y": 1.12,
                "xanchor": "center", "yanchor": "top",
                "showarrow": False, "font": {"size": 13}
            }],
            "margin": {"l": 10, "r": 10, "t": 26, "b": 10},
            "legend": {"orientation": "h"},
            "title": {"text": ""}
        }
    }

# ---------------- App + Routes ----------------
external_styles = [dbc.themes.FLATLY]
app = Dash(__name__, external_stylesheets=external_styles, title=APP_TITLE)
server = app.server

@server.post("/ingest_snapshot")
def route_ingest_snapshot():
    """
    POST a new snapshot to fully replace current state.
    Accepts either:
      - {"snapshot": [...], "meta": {"ingested_at": "...", "env": "QA"}}
      - or a raw JSON array of items for backward compatibility.
    """
    try:
        body = request.get_json(force=True, silent=False)
        # New payload shape: {"snapshot": items, "meta": {"ingested_at": "...", "env": "QA"}}
        env = None
        ingested_at = None
        items = None

        if isinstance(body, dict):
            meta = body.get("meta") or {}
            env = meta.get("env")
            ingested_at = meta.get("ingested_at")

            if isinstance(body.get("snapshot"), list):
                items = body["snapshot"]
            elif isinstance(body.get("items"), list):
                items = body["items"]
            elif isinstance(body.get("data"), list):
                items = body["data"]
            elif isinstance(body.get("records"), list):
                items = body["records"]
            elif isinstance(body.get("rows"), list):
                items = body["rows"]

        if items is None:
            # maybe client posted a raw list
            items = body

        if not isinstance(items, list):
            return jsonify({"ok": False, "error": "Send {'snapshot':[...], 'meta':{...}} or a JSON array."}), 400

        store = load_store()
        apply_snapshot(store, items, env=env, ingested_at=ingested_at)
        save_store(store)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400

@server.post("/feed")
def route_feed():
    """Alias for /ingest_snapshot for feeder compatibility."""
    return route_ingest_snapshot()

@server.post("/store/reset")
def route_reset():
    """
    Reset the store to an empty state.
    Optional: /store/reset?seed=1 seeds a trivial dataset.
    """
    seed = request.args.get("seed", "0") == "1"
    store = _init_store()
    if seed:
        _ = _ensure_leaf(store, DEFAULT_OWNER.lower(), DEFAULT_MODE.lower(), "dataset-000", "stage")
    save_store(store)
    return jsonify({"ok": True, "seeded": seed})

# tiny page to show/copy a raw file path safely even in locked-down browsers
@server.get("/rawpath")
def route_rawpath():
    """
    GET /rawpath?p=<raw>
    Render a minimal page with a readonly input containing the raw log path,
    to make copying possible even when Clipboard APIs are restricted.
    """
    raw_q = request.args.get("p", "", type=str)
    raw_path = unquote_plus(raw_q)

    title = "Raw Log Path"
    html_doc = f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8"/>
    <title>{html_escape(title)}</title>
    <style>
      body {{ font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; margin: 16px; }}
      input {{
        width: 96%;
        font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace;
        font-size: 14px; padding: 8px;
      }}
      .hint {{ color: #6c757d; margin-top: 8px; font-size: 13px; }}
    </style>
  </head>
  <body>
    <h3>Raw Log Path</h3>
    <input id="pathbox" type="text" readonly value="{html_escape(raw_path)}" onfocus="this.select()"/>
    <div class="hint">Tip: press Ctrl/⌘+C to copy. This page works in locked-down browsers.</div>
    <script>
      (function() {{
        var el = document.getElementById('pathbox');
        try {{ el.focus(); el.select(); }} catch (e) {{}}
      }})();
    </script>
  </body>
</html>"""
    return Response(html_doc, mimetype="text/html")

# Raw text (debug)
@server.get("/logmem/<path:key>")
def route_logmem(key: str):
    """
    GET raw log text by a key:
      - rel path under LOG_ROOT (disk-backed, cached on first read)
      - mem/<hash>/<name> (in-memory cached content)
    """
    clean = key.lstrip("/").replace("\\", "/")
    if ".." in clean:
        return abort(400)
    with LOG_MEM_LOCK:
        txt = LOG_MEM.get(clean)
    if txt is None:
        # try disk if not mem
        p = (LOG_ROOT / clean).resolve()
        try:
            p.relative_to(LOG_ROOT)
        except Exception:
            return Response(f"(log not found: {html_escape(clean)})", mimetype="text/plain", status=404)
        if not p.exists():
            return Response(f"(log not found: {html_escape(clean)})", mimetype="text/plain", status=404)
        txt = _read_file_safely(p) or ""
        with LOG_MEM_LOCK:
            LOG_MEM[clean] = txt
    return Response(txt, mimetype="text/plain")

# HTML viewer (new tab)
@server.get("/logview/<path:key>")
def route_logview(key: str):
    """
    GET /logview/<key>
    Render a very simple HTML page showing text from memory/disk for the key.
    """
    clean = key.lstrip("/").replace("\\", "/")
    if ".." in clean:
        return abort(400)

    txt = None
    with LOG_MEM_LOCK:
        txt = LOG_MEM.get(clean)

    if txt is None and not clean.startswith("mem/"):
        # disk fallback for disk-backed keys
        p = (LOG_ROOT / clean).resolve()
        try:
            p.relative_to(LOG_ROOT)
        except Exception:
            return Response(f"<h3>Log not found</h3><p>{html_escape(clean)}</p>", mimetype="text/html", status=404)
        if not p.exists():
            return Response(f"<h3>Log not found</h3><p>{html_escape(clean)}</p>", mimetype="text/html", status=404)
        txt = _read_file_safely(p) or ""
        with LOG_MEM_LOCK:
            LOG_MEM[clean] = txt

    if txt is None:
        return Response(f"<h3>Log not found</h3><p>{html_escape(clean)}</p>", mimetype="text/html", status=404)

    title = f"Log: {clean}"
    body  = html_escape(txt)
    html_doc = f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8"/>
    <title>{html_escape(title)}</title>
    <style>
      body {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace; margin: 16px; }}
      pre  {{ white-space: pre-wrap; word-wrap: break-word; }}
    </style>
  </head>
  <body>
    <h3>{html_escape(title)}</h3>
    <pre>{body}</pre>
  </body>
</html>"""
    return Response(html_doc, mimetype="text/html")

# ---------------- Controls & KPIs ----------------
controls_card = dbc.Card(
    dbc.CardBody([
        html.Div("Owner", className="text-muted small"),
        dcc.Dropdown(
            id="owner-filter",
            options=[{"label":"All", "value":"All"},
                     {"label": DEFAULT_OWNER, "value": DEFAULT_OWNER.lower()}],
            value=DEFAULT_OWNER.lower(),
            clearable=False, className="mb-2", style={"minWidth":"180px"},
        ),
        html.Div("Mode", className="text-muted small"),
        dcc.Dropdown(
            id="mode-filter",
            options=[{"label":"All", "value":"All"},
                     {"label":"Live", "value":"live"},
                     {"label":"Backfill", "value":"backfill"}],
            value=DEFAULT_MODE.lower(),
            clearable=False, className="mb-2", style={"minWidth":"180px"},
        ),
        html.Div("Stage filter (ANY of)", className="text-muted small"),
        dcc.Dropdown(
            id="stage-filter",
            options=[{"label": s.title(), "value": s} for s in STAGES],
            value=STAGES, multi=True, className="mb-2",
        ),
        html.Div("Status filter (ANY of)", className="text-muted small"),
        dcc.Dropdown(
            id="status-filter",
            options=[{"label": s.title(), "value": s} for s in JOB_STATUS_ORDER],
            value=[], multi=True, placeholder="(none)",
        ),
        html.Div("Sort by", className="text-muted small mt-2"),
        dcc.Dropdown(
            id="sort-by",
            options=[
                {"label":"Urgency (worst first)", "value":"severity_asc"},
                {"label":"Dataset (A→Z)", "value":"name_asc"},
            ],
            value="severity_asc", clearable=False, style={"width":"220px"},
        ),
        html.Div("Table groups per row", className="text-muted small mt-2"),
        dcc.Dropdown(
            id="table-groups",
            options=[{"label": str(n), "value": n} for n in (1,2,3,4,5,6)],
            value=1, clearable=False, style={"width":"120px"},
        ),
        html.Div("Chunks per line", className="text-muted small mt-2"),
        dcc.Dropdown(
            id="chunks-per-line",
            options=[{"label": str(n), "value": n} for n in (1,2,3,4,5,6,8,10,12)],
            value=5, clearable=False, style={"width":"120px"},
        ),
    ]),
    style={"margin":"0"}
)

def kpi_card(title: str, comp_id: str) -> dbc.Card:
    """Small helper to build a KPI card with a labeled H4 value placeholder."""
    return dbc.Card(
        dbc.CardBody([html.Div(title, className="text-muted small"), html.H4(id=comp_id, className="mb-0")]),
        style={"maxWidth": _px(MAX_KPI_WIDTH), "margin":"0"}
    )

kpi_row_top = html.Div([
    kpi_card("Waiting",  "kpi-waiting"),
    kpi_card("Retrying", "kpi-retrying"),
    kpi_card("Running",  "kpi-running"),
    kpi_card("Failed",   "kpi-failed"),
], style={"display":"flex","gap":"10px","flexWrap":"wrap","marginTop":"8px"})

kpi_row_bottom = html.Div([
    kpi_card("Overdue",   "kpi-overdue"),
    kpi_card("Manual",    "kpi-manual"),
    kpi_card("Succeeded", "kpi-succeeded"),
], style={"display":"flex","gap":"10px","flexWrap":"wrap","marginTop":"8px"})

def pie_holder(comp_id: str, title_text: str) -> dcc.Graph:
    """Return a dcc.Graph placeholder sized appropriately for the small pies."""
    return dcc.Graph(
        id=comp_id,
        figure={"layout":{"title":{"text": title_text}}},
        style={"height":"320px", "maxWidth": _px(MAX_GRAPH_WIDTH), "margin":"0"}
    )

pies_block = html.Div(
    [
        pie_holder("pie-stage", "Stage"),
        pie_holder("pie-archive", "Archive"),
        pie_holder("pie-enrich", "Enrich"),
        pie_holder("pie-consolidate", "Consolidate"),
    ],
    className="mb-2",
    style={"display":"flex","gap":"12px","flexWrap":"wrap","paddingBottom":"8px"}
)

# Side-by-side, no wrap; banner shows env + last ingested
two_col_nowrap = html.Div([
    # Left fixed pane
    html.Div([controls_card, kpi_row_top, kpi_row_bottom, pies_block],
             style={"width": _px(MAX_LEFT_WIDTH), "minWidth": _px(MAX_LEFT_WIDTH),
                    "maxWidth": _px(MAX_LEFT_WIDTH), "flex":"0 0 auto"}),
    # Right growing pane (title + table inline)
    html.Div([
        html.Div([
            html.H4("Datasets", className="fw-semibold", style={"margin":"0","whiteSpace":"nowrap"}),
            html.Div(id="table-container", style={"flex":"0 0 auto"})
        ], style={
            "display":"flex","alignItems":"flex-start","gap":"8px","width":"100%",
            # safe right padding (doesn't affect click targets)
            "paddingRight":"56px"
        }),
    ], style={"flex":"1 1 auto","minWidth":"0"}),
], style={"display":"flex","flexWrap":"nowrap","alignItems":"flex-start",
          "gap":"16px","maxWidth":_px(MAX_PAGE_WIDTH),"margin":"0 auto"})

app.layout = dbc.Container([
    html.Div([
        html.Div(APP_TITLE, className="h2 fw-bold"),
        html.Div(id="env-indicator", className="text-muted", style={"marginLeft":"auto"})
    ], style={"display":"flex","alignItems":"center","gap":"12px",
              "maxWidth": _px(MAX_PAGE_WIDTH), "margin":"0 auto"}),

    two_col_nowrap,

    dcc.Interval(id="interval", interval=REFRESH_MS, n_intervals=0)
], fluid=True, className="pt-3 pb-4", style={"maxWidth": _px(MAX_PAGE_WIDTH), "margin":"0 auto"})

# ---------------- Helper for banner ----------------
def _format_banner(meta: dict) -> str:
    """
    Format the header text showing Environment and 'Last Ingested' in local timezone.
    If meta timestamp is missing/invalid, show '(unknown)'/'(invalid)' accordingly.
    """
    env = meta.get("env") or "Unknown"
    ts  = meta.get("ingested_at")
    if not ts:
        return f"Environment: {env} · Last Ingested: (unknown)"
    s = str(ts).replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(s)
    except Exception:
        return f"Environment: {env} · Last Ingested: (invalid)"
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    local_dt = dt.astimezone(_DEF_TZ)
    return f"Environment: {env} · Last Ingested: {local_dt.strftime('%Y-%m-%d %H:%M:%S %Z')}"

# ---------------- Callback ----------------
@app.callback(
    Output("kpi-waiting","children"),
    Output("kpi-retrying","children"),
    Output("kpi-running","children"),
    Output("kpi-failed","children"),
    Output("kpi-overdue","children"),
    Output("kpi-manual","children"),
    Output("kpi-succeeded","children"),
    Output("owner-filter","options"),
    Output("mode-filter","options"),
    Output("pie-stage","figure"),
    Output("pie-archive","figure"),
    Output("pie-enrich","figure"),
    Output("pie-consolidate","figure"),
    Output("table-container","children"),
    Output("env-indicator","children"),
    Output("interval","interval"),
    Input("interval","n_intervals"),
    Input("owner-filter","value"),
    Input("mode-filter","value"),
    Input("stage-filter","value"),
    Input("status-filter","value"),
    Input("table-groups","value"),
    Input("chunks-per-line","value"),
    Input("sort-by","value"),
    State("interval","interval"),
)
def refresh(_n, owner_sel, mode_sel, stage_filter, status_filter, groups_per_row, chunks_per_line, sort_by, cur_interval):
    """
    Main UI callback:
      - Recomputes KPIs, pies, dataset table, banner text, and keeps the refresh interval.
      - Filtering/sorting are driven by control values; table is sized to content.
    """
    interval_ms = int(cur_interval or REFRESH_MS)
    store = load_store()

    # KPIs (global)
    k = aggregate_counts(store)
    kpi_vals = [str(k.get(s, 0)) for s in ["waiting","retrying","running","failed","overdue","manual","succeeded"]]

    # Filters
    owner_opts, mode_opts = list_filters(store)

    # Pies (owner/mode filtered)
    figs = []
    for stg in STAGES:
        c = filtered_stage_counts(store, owner_sel, mode_sel, stg)
        figs.append(pie_figure(stg.title(), c))

    # Table (groups per row ; width = content)
    groups = gather_dataset_groups(
        store, owner_sel, mode_sel, stage_filter or [], status_filter or [], chunks_per_line or 5, sort_by or "severity_asc"
    )
    table_comp = build_table_component(groups, groups_per_row or 1)

    # Banner
    env_text = _format_banner(store.get("meta", {}))

    return (*kpi_vals, owner_opts, mode_opts, *figs, table_comp, env_text, interval_ms)

# ---------------- Run ----------------
if __name__ == "__main__":
    LOG_ROOT.mkdir(parents=True, exist_ok=True)
    preload_logs()  # preload logs under LOG_ROOT; absolute paths handled on-demand/mem
    app.run(host="0.0.0.0", port=9060, debug=False)