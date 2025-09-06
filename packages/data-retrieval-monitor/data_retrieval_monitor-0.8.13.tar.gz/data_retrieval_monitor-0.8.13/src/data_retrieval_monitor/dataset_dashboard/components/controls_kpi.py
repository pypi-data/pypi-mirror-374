from dash import html, dcc
import dash_bootstrap_components as dbc
from ..utils import px
from ..constants import STAGES, JOB_STATUS_ORDER

class ControlsComponent:
    def render(self, cfg):
        return dbc.Card(
            dbc.CardBody([
                html.Div("Owner", className="text-muted small"),
                dcc.Dropdown(id="owner-filter", options=[], value="All", clearable=False, className="mb-2", style={"minWidth":"180px"}),

                html.Div("Mode", className="text-muted small"),
                dcc.Dropdown(id="mode-filter", options=[], value="All", clearable=False, className="mb-2", style={"minWidth":"180px"}),

                html.Div("Stage filter (ANY of)", className="text-muted small"),
                dcc.Dropdown(id="stage-filter",
                             options=[{"label": s.title(), "value": s} for s in STAGES],
                             value=STAGES, multi=True, className="mb-2"),

                html.Div("Status filter (ANY of)", className="text-muted small"),
                dcc.Dropdown(id="status-filter",
                             options=[{"label": s.title(), "value": s} for s in JOB_STATUS_ORDER],
                             value=[], multi=True, placeholder="(none)"),

                html.Div("Table groups per row", className="text-muted small mt-2"),
                dcc.Dropdown(id="table-groups", options=[{"label": str(n), "value": n} for n in (1,2,3,4,5,6)],
                             value=2, clearable=False, style={"width":"120px"}),

                html.Div("Chunks per line", className="text-muted small mt-2"),
                dcc.Dropdown(id="chunks-per-line", options=[{"label": str(n), "value": n} for n in (1,2,3,4,5,6,8,10,16)],
                             value=6, clearable=False, style={"width":"120px"}),

                html.Div("Sort by", className="text-muted small mt-2"),
                dcc.Dropdown(
                    id="sort-by",
                    options=[
                        {"label": "Data Name (A–Z)", "value": "name_asc"},
                        {"label": "Chunk Avg Score (worst→best)", "value": "chunk_asc"},
                        {"label": "Chunk Avg Score (best→worst)", "value": "chunk_desc"},
                        {"label": "Status Avg Score (worst→best)", "value": "status_asc"},
                        {"label": "Status Avg Score (best→worst)", "value": "status_desc"},
                    ],
                    value="name_asc",
                    clearable=False,
                    style={"minWidth":"220px"},
                ),
            ]),
            style={"margin":"0"}
        )

class KpiStrip:
    def __init__(self, max_kpi_width: int):
        self.max_kpi_width = max_kpi_width

    def _card(self, title, _id):
        return dbc.Card(
            dbc.CardBody([html.Div(title, className="text-muted small"), html.H4(id=_id, className="mb-0")]),
            style={"maxWidth": px(self.max_kpi_width), "margin":"0"}
        )

    def render_top(self):
        return html.Div([
            self._card("Waiting","kpi-waiting"),
            self._card("Retrying","kpi-retrying"),
            self._card("Running","kpi-running"),
            self._card("Failed","kpi-failed"),
        ], style={"display":"flex","gap":"10px","flexWrap":"wrap","marginTop":"8px"})

    def render_bottom(self):
        return html.Div([
            self._card("Overdue","kpi-overdue"),
            self._card("Manual","kpi-manual"),
            self._card("Succeeded","kpi-succeeded"),
        ], style={"display":"flex","gap":"10px","flexWrap":"wrap","marginTop":"8px"})