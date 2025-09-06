from dash import Dash
import dash_bootstrap_components as dbc

from .config import load_config
from .dashboard import DashboardHost
from .inject import register_ingest_routes, register_callbacks
from .library import make_dummy_payload  # << changed

def create_app():
    cfg = load_config()
    app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY], title=cfg.app_title)

    # Host wires services + components and builds layout
    host = DashboardHost(app, cfg, make_items_callable=lambda: make_dummy_payload(cfg))
    app.layout = host.layout

    # Routes + callbacks (and start the periodic injector if enabled)
    register_ingest_routes(app.server, host)
    register_callbacks(app, cfg, host)
    host.start_services()

    return app, app.server

if __name__ == "__main__":
    app, server = create_app()
    app.run(host="0.0.0.0", port=8090, debug=False)