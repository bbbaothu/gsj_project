"""
Component hiển thị Giao diện Module 03: Gợi ý xả hàng & Định giá cạnh tranh (US-3.1 & US-3.2).
"""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.services.clearance_service import ClearanceService


def render_tab_clearance(service: ClearanceService, role: str = "ROLE_OWNER"):
    """Render màn hình Gợi ý Xả hàng thông minh & Radar Giá thị trường (Module 03)."""
    kpis = service.get_clearance_kpis(role=role)
    candidates = service.get_clearance_candidates(role=role)

    if not candidates:
        st.info("Hiện tại không có SKU nào cần xả hàng tồn đọng.")
        return

    # 1. HÀNG 4 THẺ KPI VĨ MÔ
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(
            label="💰 VỐN DỰ KIẾN THU HỒI",
            value=kpis["display_recovery_capital"],
            delta=f"Từ {kpis['total_target_qty']} thiết bị ({kpis['candidate_skus_count']} SKU)",
        )
    with c2:
        roi_str = f"Biên ROI vốn: {kpis['roi_pct']}%" if kpis["roi_pct"] is not None else "Đã bảo mật theo Role"
        st.metric(
            label="📈 LỢI NHUẬN GỘP KỲ VỌNG",
            value=kpis["display_gross_profit"],
            delta=roi_str,
        )
    with c3:
        st.metric(
            label="🔥 CHỈ SỐ LỢI THẾ GIÁ (PAI)",
            value="Radar Active",
            delta="Rẻ hơn đối thủ lớn 5% - 14%",
        )
    with c4:
        st.metric(
            label="🚀 CHIẾN DỊCH XẢ ĐANG CHẠY",
            value=f"{kpis['active_campaigns_count']} Hoạt động · {kpis['pending_campaigns_count']} Chờ duyệt",
            delta="Chiến dịch đẩy tồn cuối năm",
        )

    st.markdown("---")

    # 2. DẢI THẺ CHỌN THIẾT BỊ XẢ TỒN THEO NGÀNH HÀNG
    st.markdown("##### 📦 Chọn Thiết bị Xả tồn để Phân tích Kịch bản (Nhận diện theo Ngành hàng)")
    default_sku = st.session_state.get("selected_clearance_sku", candidates[0]["product_code"])
    sku_codes = [c["product_code"] for c in candidates[:4]]
    if default_sku not in sku_codes:
        default_sku = sku_codes[0]

    card_cols = st.columns(min(4, len(candidates)))
    for idx, cand in enumerate(candidates[:4]):
        with card_cols[idx]:
            is_sel = cand["product_code"] == default_sku
            border_color = "#2563EB" if is_sel else "#E2E8F0"
            bg_color = "#EFF6FF" if is_sel else "#FFFFFF"
            st.markdown(
                f"""
                <div style="border:2px solid {border_color}; background:{bg_color}; border-radius:8px; padding:10px; margin-bottom:6px;">
                    <div style="font-size:11px; font-weight:700; color:#1E293B;">{cand['category_group']} · {cand['brand']}</div>
                    <div style="font-size:12px; font-weight:700; color:#0F172A; margin-top:2px;">{cand['product_code']}</div>
                    <div style="font-size:11px; color:#475569; min-height:32px;">{cand['product_name'][:42]}</div>
                    <div style="font-size:11px; margin-top:4px;">Tồn: <b>{cand['soh']}</b> | Xả: <b style="color:#DC2626;">{cand['target_qty']}</b></div>
                    <div style="font-size:11px; color:#059669; font-weight:600; margin-top:2px;">{cand['best_tactic_label']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(
                "✅ Đang chọn" if is_sel else f"Chọn {cand['product_code']}",
                key=f"m3_card_{cand['product_code']}",
                use_container_width=True,
            ):
                st.session_state["selected_clearance_sku"] = cand["product_code"]
                st.rerun()

    selected_sku = st.session_state.get("selected_clearance_sku", sku_codes[0])
    selected_cand = next((c for c in candidates if c["product_code"] == selected_sku), candidates[0])

    st.markdown("---")

    # 3. KHÔNG GIAN PHÂN TÍCH ĐÔI (6 CỘT TRÁI SIMULATOR | 6 CỘT PHẢI BIỂU ĐỒ & RADAR GIÁ)
    left_col, right_col = st.columns([6, 6])

    with left_col:
        st.markdown(f"##### 🎛️ 4 Kịch bản Khuyến mại & Mô phỏng Dòng tiền (`{selected_sku}`)")
        tactics = service.generate_4_tactics(selected_sku, target_qty=selected_cand["target_qty"])

        tactic_labels = {
            t["tactic_code"]: (
                f"{'⭐ ' if t['is_recommended'] else ''}{t['title']} — Giá: {t['clearance_price']:,.0f} đ"
                + (" [Đề xuất tối ưu]" if t["is_recommended"] else "")
            )
            for t in tactics
        }
        rec_idx = next((i for i, t in enumerate(tactics) if t["is_recommended"]), 1)
        chosen_tactic = st.radio(
            "Chọn phương án khuyến mại:",
            options=[t["tactic_code"] for t in tactics],
            index=rec_idx,
            format_func=lambda code: tactic_labels[code],
            key=f"m3_tactic_{selected_sku}",
        )
        chosen_obj = next(t for t in tactics if t["tactic_code"] == chosen_tactic)
        st.caption(f"💡 {chosen_obj['note']}")
        if chosen_obj["map_violation"]:
            st.warning("⚠️ `ERR_CLR_002`: Giá xả phương án này thấp hơn giá sàn MAP hãng cam kết. Khuyến nghị chuyển sang PA2 Combo.")

        sim_c1, sim_c2 = st.columns(2)
        with sim_c1:
            extra_disc = st.slider("Giảm giá bổ sung (%):", min_value=0.0, max_value=15.0, value=0.0, step=0.5, key=f"m3_disc_{selected_sku}")
        with sim_c2:
            target_qty = st.number_input(
                "Số lượng xả mục tiêu:",
                min_value=1,
                max_value=max(1, selected_cand["soh"]),
                value=min(selected_cand["target_qty"], selected_cand["soh"]),
                step=1,
                key=f"m3_qty_{selected_sku}",
            )

        sim = service.simulate_financials(
            selected_sku,
            chosen_tactic,
            target_qty=int(target_qty),
            extra_discount_pct=float(extra_disc),
            role=role,
        )

        sc1, sc2, sc3 = st.columns(3)
        sc1.metric("Doanh thu dự kiến", f"{sim['expected_revenue']:,.0f} đ")
        sc2.metric("Vốn thu hồi về két", sim["display_recovered_capital"])
        sc3.metric(
            "Lợi nhuận gộp ròng",
            sim["display_net_gross_profit"],
            delta=f"ROI: {sim['roi_pct']}%" if sim["roi_pct"] is not None else "Protected",
        )

        if sim["is_loss"] and role == "ROLE_OWNER":
            st.error("🚨 CẢNH BÁO CẮT LỖ: Kịch bản hiện tại đang âm lợi nhuận gộp. Vui lòng cân nhắc trước khi duyệt!")

        if st.button("🚀 PHÊ DUYỆT & ĐẨY LÊN POS ANH TÂM", type="primary", use_container_width=True):
            res = service.approve_clearance_campaign(
                product_code=selected_sku,
                tactic_code=chosen_tactic,
                target_qty=int(target_qty),
                clearance_price=sim["effective_unit_price"],
                role=role,
            )
            if res["success"]:
                st.success(res["message"])
            else:
                st.error(f"[{res.get('error_code')}] {res['error']}")

    with right_col:
        st.markdown("##### 📊 So sánh Dòng tiền & Lợi nhuận 4 Chiến thuật")
        if role == "ROLE_SALES":
            st.info("🔒 Biểu đồ phân rã vốn thu hồi và lợi nhuận ròng chỉ hiển thị cho Chủ cửa hàng (`ROLE_OWNER`).")
        else:
            rec_cap_val = selected_cand["cost_price"] * int(target_qty)
            tactic_names = [f"{t['tactic_code']}{' ⭐' if t['is_recommended'] else ''}" for t in tactics]
            profits = [
                service.simulate_financials(selected_sku, t["tactic_code"], int(target_qty), 0.0, role="ROLE_OWNER")["net_gross_profit"]
                for t in tactics
            ]
            fig_tactic = go.Figure()
            fig_tactic.add_trace(
                go.Bar(
                    name="Vốn hoàn về két",
                    y=tactic_names,
                    x=[rec_cap_val] * 4,
                    orientation="h",
                    marker_color="#1E293B",
                    text=[f"{rec_cap_val/1e6:.1f}tr" for _ in tactics],
                    textposition="inside",
                )
            )
            fig_tactic.add_trace(
                go.Bar(
                    name="Lãi gộp ròng",
                    y=tactic_names,
                    x=profits,
                    orientation="h",
                    marker_color="#059669",
                    text=[f"+{p/1e6:.1f}tr" for p in profits],
                    textposition="outside",
                )
            )
            fig_tactic.update_layout(
                barmode="stack",
                xaxis_title="Giá trị dòng tiền (VNĐ)",
                margin=dict(l=10, r=40, t=20, b=20),
                height=260,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            )
            st.plotly_chart(fig_tactic, use_container_width=True)

        st.markdown(f"##### 📡 Radar Đối chiếu Giá Thị Trường (`{selected_sku}`)")
        radar = service.get_market_price_radar(selected_sku, role=role)
        comp_df = pd.DataFrame(radar["competitors"]).rename(
            columns={
                "competitor_name": "Đối thủ tham chiếu",
                "competitor_price": "Giá đối thủ (đ)",
                "promo_note": "Chính sách kèm theo",
                "crawled_at": "Cập nhật",
            }
        )
        comp_df["Chênh lệch với Gợi ý"] = comp_df["Giá đối thủ (đ)"].apply(lambda p: f"+{p - radar['suggested_price']:,.0f} đ")
        st.dataframe(comp_df.style.format({"Giá đối thủ (đ)": "{:,.0f}"}), use_container_width=True, height=160)

        rc1, rc2, rc3 = st.columns(3)
        rc1.metric("Giá Gợi Ý Tối Ưu", f"{radar['suggested_price']:,.0f} đ", delta=f"PAI: -{radar['pai_pct']}% vs TB")
        rc2.metric("Ngưỡng sàn Vốn", radar["display_cost_price"])
        rc3.metric(
            "Lãi còn lại / máy",
            service.mask_currency(radar["unit_margin_vnd"], role),
        )
