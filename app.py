import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone
import requests

# 1. Page Configuration Setup
st.set_page_config(page_title="Avengers Trading Terminal", layout="wide", page_icon="🦸‍♂️")
st.title("🦸‍♂️ Avengers Trading Command Center")
st.markdown("Global cloud derivative hub linked securely to your Google Sheet.")

# ⚠️ PASTE YOUR GOOGLE WEB APP URL LINK HERE BETWEEN THE QUOTES
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwlZ3lf-yPx9nPxmwOdryioCvLwRsd2lgYwu81qrsbYpBkDsnW1aJTTvuv8xUZSAywN/exec"

# Official 2026 Lot Size Configurations
LOT_SIZE_MAPPING = {
    "NIFTY 50": 65,
    "SENSEX": 20,
    "BANKNIFTY": 30,
    "FINNIFTY": 60,
    "MIDCPNIFTY": 120
}

# 2. Fetch Data from Google Sheets via Web App API Pipeline
try:
    response = requests.get(WEB_APP_URL, timeout=5)
    if response.status_code == 200:
        raw_data = response.json()
        ledger_df = pd.DataFrame(raw_data[1:], columns=raw_data[0])
    else:
        ledger_df = pd.DataFrame()
except Exception:
    columns = ["Date & Time (IST)", "Index", "Net P&L Status", "Total Lots Bought", "Total Qty", "Buy Premium", "SL Exit Price", "Exit Breakdown Mapping"]
    ledger_df = pd.DataFrame(columns=columns)

# 3. GLOBAL ASSET SELECTION HEADER BAR
index_name = st.selectbox("Select Active Index Asset", list(LOT_SIZE_MAPPING.keys()))
base_multiplier = LOT_SIZE_MAPPING[index_name]

st.markdown("---")

# 4. TWO DIFFERENT DISTINCT SECTIONS (BUY COLUMN & SELL COLUMN)
buy_col, sell_col = st.columns(2, gap="large")

# ==================== SECTION 1: BUY WORKSPACE ====================
with buy_col:
    st.markdown("## 🛒 SECTION A: BUY LOGIC ENGINE")
    st.markdown("<div style='background-color: rgba(46, 204, 113, 0.05); padding: 15px; border-radius: 10px; border: 1px solid rgba(46, 204, 113, 0.2);'>", unsafe_allow_html=True)
    
    buy_lots = st.number_input("Lots to Purchase", min_value=1, value=3, step=1, key="buy_lots_key")
    buy_value = st.number_input("Buy Value (Premium Entry)", min_value=0.0, value=100.0, step=0.05, format="%.2f", key="buy_val_key")
    custom_pct = st.number_input("Target Scale (%)", min_value=0.0, max_value=1000.0, value=60.0, step=1.0, key="buy_target_key")
    sl_pct = st.number_input("Stop-Loss Scale (%)", min_value=0.0, max_value=100.0, value=10.0, step=1.0, key="buy_sl_key")
    
    buy_qty = buy_lots * base_multiplier
    invested_amount = buy_qty * buy_value
    
    val_25_pct = buy_value + (buy_value * 0.25)
    val_40_pct = buy_value + (buy_value * 0.40)
    val_50_pct = buy_value + (buy_value * 0.50)
    val_custom_pct = buy_value + (buy_value * (custom_pct / 100.0))
    sl_exit_price = buy_value - (buy_value * (sl_pct / 100.0))
    
    amt_25_profit = (val_25_pct - buy_value) * buy_qty
    amt_40_profit = (val_40_pct - buy_value) * buy_qty
    amt_50_profit = (val_50_pct - buy_value) * buy_qty
    amt_custom_profit = (val_custom_pct - buy_value) * buy_qty
    amt_sl_risk = (buy_value - sl_exit_price) * buy_qty
    
    st.markdown(f"📊 Projected Invested Capital: **₹{invested_amount:,.2f}** ({buy_qty} shares)")
    st.markdown("#### 🎯 Computed Targets & Protection Matrix:")
    
    st.markdown(f"""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); gap: 8px; text-align: center; margin-top: 10px;">
        <div style="background-color: rgba(128,128,128,0.08); padding: 8px; border-radius: 6px; color: #111;">
            <div style="font-size: 0.7rem; color: gray;">🎯 25% Target</div>
            <div style="font-size: 0.95rem; font-weight: bold; margin-top: 2px;">₹{val_25_pct:,.2f}</div>
            <div style="font-size: 0.7rem; color: #2ecc71;">+₹{amt_25_profit:,.2f}</div>
        </div>
        <div style="background-color: rgba(128,128,128,0.08); padding: 8px; border-radius: 6px; color: #111;">
            <div style="font-size: 0.7rem; color: gray;">🎯 40% Target</div>
            <div style="font-size: 0.95rem; font-weight: bold; margin-top: 2px;">₹{val_40_pct:,.2f}</div>
            <div style="font-size: 0.7rem; color: #2ecc71;">+₹{amt_40_profit:,.2f}</div>
        </div>
        <div style="background-color: rgba(128,128,128,0.08); padding: 8px; border-radius: 6px; color: #111;">
            <div style="font-size: 0.7rem; color: gray;">🎯 50% Target</div>
            <div style="font-size: 0.95rem; font-weight: bold; margin-top: 2px;">₹{val_50_pct:,.2f}</div>
            <div style="font-size: 0.7rem; color: #2ecc71;">+₹{amt_50_profit:,.2f}</div>
        </div>
        <div style="background-color: rgba(128,128,128,0.08); padding: 8px; border-radius: 6px; color: #111;">
            <div style="font-size: 0.7rem; color: gray;">⚙️ Target ({custom_pct:g}%)</div>
            <div style="font-size: 0.95rem; font-weight: bold; margin-top: 2px;">₹{val_custom_pct:,.2f}</div>
            <div style="font-size: 0.7rem; color: #2ecc71;">+₹{amt_custom_profit:,.2f}</div>
        </div>
        <div style="background-color: rgba(231, 76, 60, 0.08); padding: 8px; border-radius: 6px; border: 1px solid rgba(231, 76, 60, 0.2);">
            <div style="font-size: 0.7rem; color: #e74c3c; font-weight: bold;">🛡️ SL Floor (-{sl_pct:g}%)</div>
            <div style="font-size: 0.95rem; font-weight: bold; color: #e74c3c; margin-top: 2px;">₹{sl_exit_price:,.2f}</div>
            <div style="font-size: 0.7rem; color: #e74c3c;">-₹{amt_sl_risk:,.2f}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ==================== SECTION 2: SELL WORKSPACE ====================
with sell_col:
    st.markdown("## 💰 SECTION B: SELL LOGIC ENGINE")
    st.markdown("<div style='background-color: rgba(231, 76, 60, 0.05); padding: 15px; border-radius: 10px; border: 1px solid rgba(231, 76, 60, 0.2);'>", unsafe_allow_html=True)
    
    st.markdown("##### ⚡ 3-Leg Scale-Out Partial Exit Matrix:")
    
    # LEG 1 EXIT ROW
    st.markdown("🔹 **Leg 1 Execution Block**")
    l1_c1, l1_c2 = st.columns(2)
    with l1_c1:
        leg1_lots = st.number_input("Leg 1 Lots", min_value=0, max_value=int(buy_lots), value=2, step=1, key="l1_lots")
    with l1_c2:
        leg1_price = st.number_input("Leg 1 Selling Price", min_value=0.0, value=val_25_pct, step=0.05, format="%.2f", key="l1_price")
        
    # LEG 2 EXIT ROW
    remaining_after_l1 = int(buy_lots - leg1_lots)
    st.markdown("🔹 **Leg 2 Execution Block**")
    l2_c1, l2_c2 = st.columns(2)
    with l2_c1:
        leg2_lots = st.number_input("Leg 2 Lots", min_value=0, max_value=max(0, remaining_after_l1), value=min(1, remaining_after_l1), step=1, key="l2_lots")
    with l2_c2:
        leg2_price = st.number_input("Leg 2 Selling Price", min_value=0.0, value=val_40_pct, step=0.05, format="%.2f", key="l2_price")

    # LEG 3 EXIT ROW
    remaining_after_l2 = int(remaining_after_l1 - leg2_lots)
    st.markdown("🔹 **Leg 3 Execution Block**")
    l3_c1, l3_c2 = st.columns(2)
    with l3_c1:
        leg3_lots = st.number_input("Leg 3 Lots", min_value=0, max_value=max(0, remaining_after_l2), value=max(0, remaining_after_l2), step=1, key="l3_lots")
    with l3_c2:
        leg3_price = st.number_input("Leg 3 Selling Price", min_value=0.0, value=val_50_pct, step=0.05, format="%.2f", key="l3_price")

    # Math calculations
    leg1_pnl = (leg1_price - buy_value) * (leg1_lots * base_multiplier)
    leg2_pnl = (leg2_price - buy_value) * (leg2_lots * base_multiplier)
    leg3_pnl = (leg3_price - buy_value) * (leg3_lots * base_multiplier)
    
    combined_net_pnl = leg1_pnl + leg2_pnl + leg3_pnl
    total_lots_allocated = leg1_lots + leg2_lots + leg3_lots

    st.markdown("---")
    st.markdown("#### 📈 Cumulative Position Realization Summary:")
    
    sc_1, sc_2 = st.columns(2)
    with sc_1:
        st.metric(label="🔄 Allocated Lots Tracker", value=f"{total_lots_allocated} / {buy_lots} Lots", delta=f"{int(buy_lots - total_lots_allocated)} Lots Remaining")
    with sc_2:
        st.metric(label="💰 Combined Position Net P&L", value=f"₹{combined_net_pnl:,.2f}")
        
    if st.button("💾 Append & Save Trade Row to Cloud Google Sheet", use_container_width=True, type="primary"):
        if total_lots_allocated == 0:
            st.error("Cannot log a trade with zero allocated lots.")
        elif WEB_APP_URL == "PASTE_YOUR_COPIED_WEB_APP_URL_HERE":
            st.error("Please add your deployment URL link in your GitHub script line 11.")
        else:
            pnl_status_text = f"🟢 Profit: +₹{combined_net_pnl:,.2f}" if combined_net_pnl >= 0 else f"🔴 Loss: -₹{abs(combined_net_pnl):,.2f}"
            profile_log_summary = f"L1: {leg1_lots}L @ ₹{leg1_price:.1f} | L2: {leg2_lots}L @ ₹{leg2_price:.1f} | L3: {leg3_lots}L @ ₹{leg3_price:.1f}"
            
            ist_time = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)
            current_timestamp = ist_time.strftime("%Y-%m-%d %H:%M:%S")

            payload = {
                "date": current_timestamp,
                "index": index_name,
                "pnl": pnl_status_text,
                "lots": int(buy_lots),
                "qty": int(total_lots_allocated * base_multiplier),
                "buy": f"₹{buy_value:.2f}",
                "sl": f"₹{sl_exit_price:.2f}",
                "breakdown": profile_log_summary
            }
            
            try:
                requests.post(WEB_APP_URL, data=payload, timeout=5)
                st.toast("Trade recorded permanently into cloud sheet database!", icon="☁️")
                st.rerun()
            except Exception:
                st.error("Network upload error. Verify Web App API is deployed correctly.")
    st.markdown("</div>", unsafe_allow_html=True)

# 5. BOTTOM ROW: FULL HISTORICAL DATA SPREADSHEET MONITOR
st.markdown("---")
st.subheader("📋 Cloud Google Sheet Database Live Grid Monitor")

if 'ledger_df' in locals() and not ledger_df.empty:
    st.dataframe(ledger_df, use_container_width=True, hide_index=True, height=400)
