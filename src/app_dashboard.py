"""
Entry point chính của ứng dụng Stock Sense Retail Analytics trên Plotly Dash (6 Modules).
Tích hợp 1:1 thiết kế Prototype HTML + Tailwind + Services Layer SQLite Retail Dien May.
"""
import os
import sys
from pathlib import Path
from typing import Any, Dict
from urllib.parse import parse_qs

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import dash
from dash import Dash, Input, Output, dcc, no_update

from src.dash_app.components.layout_shell import MODULE_KEYS, build_app_shell
from src.dash_app.callbacks.global_callbacks import register_global_callbacks
from src.dash_app.callbacks.m1_callbacks import register_m1_callbacks
from src.dash_app.callbacks.m2_callbacks import register_m2_callbacks
from src.dash_app.callbacks.m3_callbacks import register_m3_callbacks
from src.dash_app.callbacks.m4_callbacks import register_m4_callbacks
from src.dash_app.callbacks.m5_callbacks import register_m5_callbacks
from src.dash_app.callbacks.m6_callbacks import register_m6_callbacks
from src.dash_app.pages.m1_overview import build_m1_detail_drawer, build_m1_panel
from src.dash_app.pages.m2_alerts import build_m2_modals_and_drawer, build_m2_panel
from src.dash_app.pages.m3_clearance import build_m3_modals, build_m3_panel
from src.dash_app.pages.m4_replenishment import build_m4_panel
from src.dash_app.pages.m5_crm import build_m5_panel
from src.dash_app.pages.m6_performance import build_m6_panel
from src.services.alert_service import AlertService
from src.services.clearance_service import ClearanceService
from src.services.crm_service import CrmService
from src.services.inventory_service import InventoryService
from src.services.order_service import OrderService
from src.services.performance_service import PerformanceService
from src.services.replenishment_service import ReplenishmentService

DB_PATH = str(PROJECT_ROOT / "data" / "retail_dienmay.db")

PROTOTYPE_INDEX_STRING = """<!DOCTYPE html>
<html class="h-full bg-[#F1F5F9]" lang="vi">
<head>
  {%metas%}
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{%title%}</title>
  {%favicon%}
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin=""/>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&amp;family=JetBrains+Mono:wght@400;500;600;700&amp;display=swap" rel="stylesheet"/>
  <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
  <script src="https://unpkg.com/@phosphor-icons/web"></script>
  <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
  <script id="tailwind-config">
  tailwind.config = {
    darkMode: "class",
    theme: {
      extend: {
        colors: {
          "background": "#f8f9ff",
          "on-secondary-container": "#fefcff",
          "primary-fixed": "#dae2fd",
          "tertiary-fixed-dim": "#68dba9",
          "on-background": "#0b1c30",
          "outline-variant": "#c6c6cd",
          "primary-container": "#131b2e",
          "secondary-fixed-dim": "#b4c5ff",
          "on-tertiary-fixed-variant": "#005137",
          "on-tertiary": "#ffffff",
          "on-error": "#ffffff",
          "tertiary-fixed": "#85f8c4",
          "primary-fixed-dim": "#bec6e0",
          "secondary": "#0051d5",
          "on-secondary-fixed-variant": "#003ea8",
          "surface-container-highest": "#d3e4fe",
          "on-primary-container": "#7c839b",
          "on-error-container": "#93000a",
          "inverse-surface": "#213145",
          "surface": "#f8f9ff",
          "surface-container-low": "#eff4ff",
          "on-primary-fixed-variant": "#3f465c",
          "error-container": "#ffdad6",
          "on-surface": "#0b1c30",
          "inverse-on-surface": "#eaf1ff",
          "on-primary-fixed": "#131b2e",
          "secondary-fixed": "#dbe1ff",
          "surface-tint": "#565e74",
          "surface-container-lowest": "#ffffff",
          "surface-container": "#e5eeff",
          "surface-dim": "#cbdbf5",
          "surface-bright": "#f8f9ff",
          "outline": "#76777d",
          "surface-variant": "#d3e4fe",
          "inverse-primary": "#bec6e0",
          "primary": "#000000",
          "on-tertiary-container": "#069669",
          "tertiary": "#000000",
          "surface-container-high": "#dce9ff",
          "on-surface-variant": "#45464d",
          "on-secondary-fixed": "#00174b",
          "secondary-container": "#316bf3",
          "on-primary": "#ffffff",
          "error": "#ba1a1a",
          "tertiary-container": "#002114",
          "on-tertiary-fixed": "#002114",
          "on-secondary": "#ffffff"
        },
        fontFamily: {
          "label-sm": ["JetBrains Mono"],
          "headline-xl": ["Inter"],
          "body-lg": ["Inter"],
          "headline-md": ["Inter"],
          "headline-lg": ["Inter"],
          "body-md": ["Inter"],
          "label-md": ["JetBrains Mono"],
          "body-sm": ["Inter"],
          "label-lg": ["JetBrains Mono"]
        }
      }
    }
  };
  </script>
  {%css%}
</head>
<body class="h-full overflow-hidden bg-slate-50 text-slate-900 antialiased">
  {%app_entry%}
  <footer>
    {%config%}
    {%scripts%}
    {%renderer%}
  </footer>
</body>
</html>"""


def init_services(db_path: str = DB_PATH) -> Dict[str, Any]:
    """Khởi tạo 7 Service Layers dùng chung cho 6 Modules."""
    return {
        "inventory": InventoryService(db_path=db_path),
        "order": OrderService(db_path=db_path),
        "alert": AlertService(db_path=db_path),
        "clearance": ClearanceService(db_path=db_path),
        "replenishment": ReplenishmentService(db_path=db_path),
        "crm": CrmService(db_path=db_path),
        "performance": PerformanceService(db_path=db_path),
    }


def create_dash_app(db_path: str = DB_PATH) -> Dash:
    """Khởi tạo và lắp ghép hoàn chỉnh Plotly Dash Application 6 Modules."""
    services = init_services(db_path)
    assets_dir = str(Path(__file__).resolve().parent / "assets")

    dash_app = Dash(
        __name__,
        suppress_callback_exceptions=True,
        assets_folder=assets_dir,
        title="Stock Sense · Điện Máy Anh Tâm (Master 6-Module Dashboard)",
    )
    dash_app.index_string = PROTOTYPE_INDEX_STRING

    page_panels = {
        "m1": build_m1_panel(services, active=True, role="ROLE_OWNER"),
        "m2": build_m2_panel(services, active=False, role="ROLE_OWNER"),
        "m3": build_m3_panel(services, active=False, role="ROLE_OWNER"),
        "m4": build_m4_panel(is_active=False),
        "m5": build_m5_panel(is_active=False),
        "m6": build_m6_panel(is_active=False),
    }
    extra_overlays = [
        dcc.Location(id="url", refresh=False),
        build_m1_detail_drawer(),
        build_m2_modals_and_drawer(),
        build_m3_modals(),
    ]

    dash_app.layout = build_app_shell(
        services,
        active_tab="m1",
        role="ROLE_OWNER",
        page_panels=page_panels,
        extra_overlays=extra_overlays,
    )

    # Đăng ký callbacks toàn cục + 6 Modules
    register_global_callbacks(dash_app, services)
    register_m1_callbacks(dash_app, services)
    register_m2_callbacks(dash_app, services)
    register_m3_callbacks(dash_app, services)
    register_m4_callbacks(dash_app, services)
    register_m5_callbacks(dash_app, services)
    register_m6_callbacks(dash_app, services)

    @dash_app.callback(
        Output("store-active-tab", "data"),
        Input("url", "search"),
    )
    def sync_tab_from_query_string(search):
        if not search:
            return "m1"
        qs = parse_qs(search.lstrip("?"))
        tab_val = (qs.get("tab") or [None])[0]
        if tab_val in MODULE_KEYS:
            return tab_val
        return "m1"

    return dash_app


app = create_dash_app()
server = app.server

if __name__ == "__main__":
    if "streamlit" in sys.modules:
        print(
            "[Stock Sense] Ứng dụng đã chuyển sang Plotly Dash (cổng 8050). "
            "Vui lòng chạy `.venv/bin/python src/app_dashboard.py` thay vì `streamlit run`."
        )
    else:
        port = int(os.environ.get("PORT", 8050))
        app.run(debug=False, host="127.0.0.1", port=port)
