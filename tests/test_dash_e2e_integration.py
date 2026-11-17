"""
Kiểm thử tích hợp End-to-End Plotly Dash App Server (src/app_dashboard.py) qua Flask test_client().
"""
import json
import unittest


class TestDashE2EIntegration(unittest.TestCase):
    """Kiểm tra HTTP 200, JSON layout đủ 6 Modules & Drawers, và POST /_dash-update-component."""

    def test_dash_app_routes_and_layout_landmarks(self):
        """GET / và GET /_dash-layout phải trả HTTP 200 với đầy đủ 6 Modules & Modals."""
        from src.app_dashboard import app, server

        client = server.test_client()

        resp_index = client.get("/")
        self.assertEqual(resp_index.status_code, 200)
        html_body = resp_index.data.decode("utf-8")
        self.assertIn("Stock Sense", html_body)
        self.assertIn("tailwind.config", html_body)

        resp_layout = client.get("/_dash-layout")
        self.assertEqual(resp_layout.status_code, 200)
        layout_text = resp_layout.data.decode("utf-8")
        for landmark in [
            "appSidebar",
            "quickSearchModal",
            "panel-m1",
            "panel-m2",
            "panel-m3",
            "panel-m4",
            "panel-m5",
            "panel-m6",
            "detailDrawer",
            "m2DecisionDrawer",
            "poPreviewModal",
            "m5CycleModal",
        ]:
            self.assertIn(landmark, layout_text, f"Thiếu ID '{landmark}' trong JSON /_dash-layout")

        # Kiểm tra đã nạp callbacks của cả Global + M1..M6
        self.assertGreater(len(app.callback_map), 15)

    def test_dash_post_rbac_and_tab_switch_callbacks(self):
        """POST /_dash-update-component mô phỏng chuyển RBAC -> ROLE_SALES và chuyển Tab m1 -> m3."""
        from src.app_dashboard import app, server

        client = server.test_client()

        role_out_key = next(k for k in app.callback_map if "store-role.data" in k)
        # 1. Chuyển vai trò RBAC sang ROLE_SALES
        rbac_payload = {
            "output": role_out_key,
            "outputs": [
                {"id": "store-role", "property": "data"},
                {"id": "btn-role-owner", "property": "className"},
                {"id": "btn-role-sales", "property": "className"},
                {"id": "userRoleSubtitle", "property": "children"},
            ],
            "inputs": [
                {"id": "btn-role-owner", "property": "n_clicks", "value": 0},
                {"id": "btn-role-sales", "property": "n_clicks", "value": 1},
            ],
            "changedPropIds": ["btn-role-sales.n_clicks"],
            "state": [{"id": "store-role", "property": "data", "value": "ROLE_OWNER"}],
        }
        r_role = client.post(
            "/_dash-update-component",
            data=json.dumps(rbac_payload),
            content_type="application/json",
        )
        self.assertEqual(r_role.status_code, 200, r_role.data.decode("utf-8"))
        role_res = r_role.get_json()
        self.assertEqual(role_res["response"]["store-role"]["data"], "ROLE_SALES")

        tab_out_key = next(k for k in app.callback_map if "store-active-tab.data" in k and "btn-nav-m3" in k)
        # 2. Chuyển tab sang M3
        tab_payload = {
            "output": tab_out_key,
            "outputs": [
                {"id": "store-active-tab", "property": "data"},
                {"id": "btn-nav-m1", "property": "className"},
                {"id": "btn-nav-m2", "property": "className"},
                {"id": "btn-nav-m3", "property": "className"},
                {"id": "btn-nav-m4", "property": "className"},
                {"id": "btn-nav-m5", "property": "className"},
                {"id": "btn-nav-m6", "property": "className"},
                {"id": "panel-m1", "property": "style"},
                {"id": "panel-m2", "property": "style"},
                {"id": "panel-m3", "property": "style"},
                {"id": "panel-m4", "property": "style"},
                {"id": "panel-m5", "property": "style"},
                {"id": "panel-m6", "property": "style"},
                {"id": "store-quick-action", "property": "data"},
            ],
            "inputs": [
                {"id": "btn-nav-m1", "property": "n_clicks", "value": 0},
                {"id": "btn-nav-m2", "property": "n_clicks", "value": 0},
                {"id": "btn-nav-m3", "property": "n_clicks", "value": 1},
                {"id": "btn-nav-m4", "property": "n_clicks", "value": 0},
                {"id": "btn-nav-m5", "property": "n_clicks", "value": 0},
                {"id": "btn-nav-m6", "property": "n_clicks", "value": 0},
                {"id": "btn-brand-home", "property": "n_clicks", "value": 0},
                {"id": "btn-topbar-bell", "property": "n_clicks", "value": 0},
                {"id": "btn-quick-serial", "property": "n_clicks", "value": 0},
                {"id": "btn-quick-po", "property": "n_clicks", "value": 0},
                {"id": "btn-quick-threshold", "property": "n_clicks", "value": 0},
            ],
            "changedPropIds": ["btn-nav-m3.n_clicks"],
            "state": [{"id": "store-active-tab", "property": "data", "value": "m1"}],
        }
        r_tab = client.post(
            "/_dash-update-component",
            data=json.dumps(tab_payload),
            content_type="application/json",
        )
        self.assertEqual(r_tab.status_code, 200, r_tab.data.decode("utf-8"))
        tab_res = r_tab.get_json()
        self.assertEqual(tab_res["response"]["store-active-tab"]["data"], "m3")
        self.assertEqual(tab_res["response"]["panel-m3"]["style"]["display"], "flex")
        self.assertEqual(tab_res["response"]["panel-m1"]["style"]["display"], "none")


if __name__ == "__main__":
    unittest.main()
