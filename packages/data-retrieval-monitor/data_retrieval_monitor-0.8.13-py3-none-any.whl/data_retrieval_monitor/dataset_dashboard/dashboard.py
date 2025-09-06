from dash import html
from .config import AppConfig
from .services.store import StoreService
from .services.logs import LogLinker, register_log_routes
from .services.injector import InjectorService
from .components import BannerComponent, ControlsComponent, KpiStrip, PieChartComponent, TableComponent
from .components.html import PageLayout

class DashboardHost:
    def __init__(self, app, cfg: AppConfig, make_items_callable):
        self.app = app
        self.cfg = cfg

        # services
        self.store = StoreService(cfg.store_backend, cfg.store_path, cfg.default_owner, cfg.default_mode)
        self.log_linker = LogLinker(cfg.log_root)
        self.injector = InjectorService(
            apply_snapshot=self.store.apply_snapshot_with_meta,
            make=make_items_callable,
            period_sec=cfg.ingest_period_sec,
            enabled=cfg.ingest_enabled
        )

        # components
        self.banner = BannerComponent()
        self.controls = ControlsComponent()
        self.kpis = KpiStrip(cfg.max_kpi_width)
        self.pies = PieChartComponent()
        self.table = TableComponent(self.log_linker, clipboard_fallback_open=cfg.clipboard_fallback_open)

        # routes  ✅ pass linker so /logmem works
        register_log_routes(app.server, self.log_linker)

        page_layout = PageLayout(cfg, self.controls, self.kpis, self.pies)
        self.layout = html.Div([
            self.banner.render(cfg.app_title),
            page_layout.build(),
        ])

    def start_services(self):
        self.injector.start()