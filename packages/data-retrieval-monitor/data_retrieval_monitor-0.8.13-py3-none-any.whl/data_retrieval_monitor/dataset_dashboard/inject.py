from dash import dcc
from dash import Input, Output, State
from flask import request, jsonify
from .constants import STAGES, JOB_STATUS_ORDER
from .components import compute
from .utils import to_local_str

def register_callbacks(app, cfg, host):
    # Add heartbeat
    app.layout.children.append(dcc.Interval(id="interval", interval=cfg.refresh_ms, n_intervals=0))

    store = host.store
    table = host.table
    pie   = host.pies

    @app.callback(
        # KPIs
        Output("kpi-waiting","children"), Output("kpi-retrying","children"),
        Output("kpi-running","children"), Output("kpi-failed","children"),
        Output("kpi-overdue","children"), Output("kpi-manual","children"),
        Output("kpi-succeeded","children"),
        # filters
        Output("owner-filter","options"), Output("mode-filter","options"),
        Output("stage-filter","options"), Output("status-filter","options"),
        # pies
        Output("pie-stage","figure"), Output("pie-archive","figure"),
        Output("pie-enrich","figure"), Output("pie-consolidate","figure"),
        # table + status + interval
        Output("table-container","children"), Output("now-indicator","children"),
        Output("interval","interval"),
        # inputs
        Input("interval","n_intervals"),
        Input("owner-filter","value"), Input("mode-filter","value"),
        Input("stage-filter","value"), Input("status-filter","value"),
        Input("table-groups","value"), Input("chunks-per-line","value"), Input("sort-by","value"),
        State("interval","interval"),
    )
    def refresh(_n, owner_sel, mode_sel, stage_filter, status_filter, groups_per_row, chunks_per_line, sort_by, cur_interval):
        state = store.state()

        # KPIs
        k = compute.aggregate_counts(state)
        kpi_vals = [str(k.get(s, 0)) for s in ["waiting","retrying","running","failed","overdue","manual","succeeded"]]

        # filter options
        owner_opts, mode_opts = store.list_filters()
        stage_opts  = [{"label": s.title(), "value": s} for s in STAGES]
        status_opts = [{"label": s.title(), "value": s} for s in JOB_STATUS_ORDER]

        # pies
        figs = {stg: host.pies.figure(stg.title(), compute.filtered_stage_counts(state, owner_sel, mode_sel, stg))
                for stg in STAGES}

        # table entries (sorted)
        owner_sel = owner_sel or "All"; mode_sel = mode_sel or "All"
        sel_stages = stage_filter or STAGES
        sel_status = status_filter or []
        sort_by    = sort_by or "name_asc"
        want_owner = None if str(owner_sel).lower() in ("","all") else str(owner_sel).lower()
        want_mode  = None if str(mode_sel).lower() in ("","all") else str(mode_sel).lower()

        entries = []
        jobs = state.get("jobs", {})
        for own, o_map in jobs.items():
            if want_owner and own != want_owner: continue
            for md, m_map in o_map.items():
                if want_mode and md != want_mode: continue
                for dn, d_map in m_map.items():
                    # status filter
                    if sel_status:
                        has_any = False
                        for stg in STAGES:
                            bs = compute.best_status((d_map.get(stg) or {"counts":{}})["counts"])
                            if bs in sel_status: has_any = True; break
                        if not has_any: continue
                    sk = compute.make_sort_key(d_map, dn, own, md, sel_stages, sort_by)
                    entries.append((sk, own, md, dn, d_map))
        entries.sort(key=lambda x: x[0])

        labels = state.get("meta", {}).get("owner_labels", {})
        table_comp = table.build(state, labels, owner_sel, mode_sel, groups_per_row or 1, entries, chunks_per_line or 999999)

        # status line: Environment | Last Ingested | Refreshed
        from datetime import datetime
        import pytz
        meta = state.get("meta", {}) or {}
        env_label = meta.get("env") or cfg.environment_label or "-"
        last_ing  = to_local_str(meta.get("last_ingest_at"), cfg.timezone)
        tz = pytz.timezone(cfg.timezone)
        refreshed = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S %Z")
        status_line = f"Environment: {env_label} | Last Ingested: {last_ing} | Refreshed: {refreshed}"

        interval_ms = int(cur_interval or cfg.refresh_ms)

        return (*kpi_vals, owner_opts, mode_opts, stage_opts, status_opts,
                figs["stage"], figs["archive"], figs["enrich"], figs["consolidate"],
                table_comp, status_line, interval_ms)

def register_ingest_routes(server, host):
    """REST endpoints: inject data, reset, control injector period/enabled. Accept meta."""
    store = host.store
    injector = host.injector

    @server.post("/ingest_snapshot")
    def ingest_snapshot():
        try:
            body = request.get_json(force=True, silent=False)
            if isinstance(body, dict):
                items = body.get("snapshot") or body.get("items")
                meta  = body.get("meta", {})
            else:
                items, meta = body, {}
            if not isinstance(items, list):
                return jsonify({"ok": False, "error": "Send {snapshot:[...]} or a JSON array."}), 400
            store.apply_snapshot_with_meta(items, meta)
            return jsonify({"ok": True})
        except Exception as e:
            return jsonify({"ok": False, "error": str(e)}), 400

    @server.post("/feed")
    def feed_alias():
        return ingest_snapshot()

    @server.post("/store/reset")
    def reset_store():
        store.apply_snapshot_with_meta([], {"ingested_at": None})
        return jsonify({"ok": True})

    # injector controls
    @server.post("/ingest/period")
    def set_period():
        try:
            body = request.get_json(force=True, silent=False) or {}
            sec = int(body.get("seconds", injector.period))
            injector.set_period(sec)
            return jsonify({"ok": True, "period_sec": injector.period})
        except Exception as e:
            return jsonify({"ok": False, "error": str(e)}), 400

    @server.post("/ingest/enable")
    def set_enabled():
        try:
            body = request.get_json(force=True, silent=False) or {}
            enabled = bool(body.get("enabled", True))
            injector.enable(enabled)
            if enabled: injector.start()
            else: injector.stop()
            return jsonify({"ok": True, "enabled": injector.enabled, "period_sec": injector.period})
        except Exception as e:
            return jsonify({"ok": False, "error": str(e)}), 400