from datetime import datetime, timezone, timedelta
import pandas as pd
import requests
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# ----------------------------------------------------
# 1. INITIAL SETUP & SYSTEM CONFIGURATIONS
# ----------------------------------------------------
st.set_page_config(
    page_title="Mission",
    page_icon="🛡️",
    layout="wide"
)

# Flash status notification banner control across page refresh iterations
if "trade_saved_success" not in st.session_state:
    st.session_state["trade_saved_success"] = False

if st.session_state["trade_saved_success"]:
    st.success("🎯 Trade entry successfully written directly to your Cloud Google Sheet tracker!")
    st.session_state["trade_saved_success"] = False


# ----------------------------------------------------
# 2. MAIN DASHBOARD VISUAL HEADER
# ----------------------------------------------------
st.markdown("## 🛡️ Trading Database")
st.markdown("<br>", unsafe_allow_html=True)


# ----------------------------------------------------
# 3. ORIGINAL TWO-COLUMN SYSTEM: BUY SIDE VS. SELL SIDE
# ----------------------------------------------------
trade_col1, trade_col2 = st.columns(2)

with trade_col1:
    st.markdown("#### 📥 Buy Side Entry Parameters")
    
    # Core trading identifier widgets stacked inside your exact layout
    index_name = st.selectbox("Select Index Name", ["NIFTY", "BANKNIFTY", "FINNIFTY", "SENSEX"])
    
    # AUTOMATIC CORRECT EXCHANGE LOT SIZE MULTIPLIER ENGINE
    if index_name == "NIFTY":
        default_multiplier = 65
    elif index_name == "SENSEX":
        default_multiplier = 20
    elif index_name == "BANKNIFTY":
        default_multiplier = 30
    elif index_name == "FINNIFTY":
        default_multiplier = 60
    else:
        default_multiplier = 25
        
    buy_lots = st.number_input("Lots Count", min_value=1, value=3, step=1)
    base_multiplier = st.number_input("Lot Size Base Units", min_value=1, value=default_multiplier, step=5)
    buy_value = st.number_input("Average Buy Entry Price (₹)", min_value=0.0, value=135.50, step=0.5, format="%.2f")
    
    st.caption("Enter your baseline entry premium cost average.")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ORIGINAL MATHEMATICAL TARGET DISPLAY CARDS
    t25 = buy_value * 1.25
    t40 = buy_value * 1.40
    t50 = buy_value * 1.50
    t60 = buy_value * 1.60
    sl_floor = buy_value * 0.90
    
    badge_col1, badge_col2, badge_col3, badge_col4, badge_col5 = st.columns(5)
    with badge_col1:
        st.markdown(f"<div style='border:1px solid #ddd; padding:8px; border-radius:5px; text-align:center;'><b>🎯 25% Target</b><br><h3>₹{t25:.2f}</h3></div>", unsafe_allow_html=True)
    with badge_col2:
        st.markdown(f"<div style='border:1px solid #ddd; padding:8px; border-radius:5px; text-align:center;'><b>🎯 40% Target</b><br><h3>₹{t40:.2f}</h3></div>", unsafe_allow_html=True)
    with badge_col3:
        st.markdown(f"<div style='border:1px solid #ddd; padding:8px; border-radius:5px; text-align:center;'><b>🎯 50% Target</b><br><h3>₹{t50:.2f}</h3></div>", unsafe_allow_html=True)
    with badge_col4:
        st.markdown(f"<div style='border:1px solid #ddd; padding:8px; border-radius:5px; text-align:center;'><b>🎯 60% Target</b><br><h3>₹{t60:.2f}</h3></div>", unsafe_allow_html=True)
    with badge_col5:
        st.markdown(f"<div style='background-color:#ffe6e6; border:1px solid #ffcccc; padding:8px; border-radius:5px; text-align:center; color:#cc0000;'><b>🛑 SL Floor (-10%)</b><br><h3>₹{sl_floor:.2f}</h3></div>", unsafe_allow_html=True)

with trade_col2:
    st.markdown("#### 📤 Sell Side Target Parameters (3 Legs)")
    
    leg_ui_col1, leg_ui_col2 = st.columns(2)
    with leg_ui_col1:
        st.markdown("**Lot Allocation per Leg**")
        leg1_lots = st.number_input("Leg 1: Lots", min_value=0, value=1, step=1)
        leg2_lots = st.number_input("Leg 2: Lots", min_value=0, value=1, step=1)
        leg3_lots = st.number_input("Leg 3: Lots", min_value=0, value=1, step=1)
        
    with leg_ui_col2:
        st.markdown("**Target Rate per Leg (₹)**")
        leg1_price = st.number_input("Leg 1: Target Price", min_value=0.0, value=140.0, step=0.5, format="%.2f")
        leg2_price = st.number_input("Leg 2: Target Price", min_value=0.0, value=150.0, step=0.5, format="%.2f")
        leg3_price = st.number_input("Leg 3: Target Price", min_value=0.0, value=160.0, step=0.5, format="%.2f")

    st.markdown("**🛡️ Risk Management**")
    sl_exit_price = st.number_input("Stop Loss Protection Floor (₹)", min_value=0.0, value=115.00, step=0.5, format="%.2f")


# ----------------------------------------------------
# 4. POSITION REALIZATION CALCULATIONS
# ----------------------------------------------------
total_lots_allocated = buy_lots
total_quantity = int(total_lots_allocated * base_multiplier)
total_sell_lots = leg1_lots + leg2_lots + leg3_lots

if total_sell_lots > 0:
    # Computes blended contract exit pricing dynamically
    average_sell_price = ((leg1_lots * leg1_price) + (leg2_lots * leg2_price) + (leg3_lots * leg3_price)) / total_sell_lots
else:
    average_sell_price = 0.0

total_cost_basis = total_sell_lots * base_multiplier * buy_value
total_revenue_basis = total_sell_lots * base_multiplier * average_sell_price
combined_net_pnl = total_revenue_basis - total_cost_basis


# ----------------------------------------------------
# 5. POSITION REALIZATION SUMMARY & SUBMISSION
# ----------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)
metric_col1, metric_col2 = st.columns([1.2, 1.0])

with metric_col1:
    st.markdown("#### 📝 Cumulative Position Realization Summary:")
    sub_col1, sub_col2 = st.columns(2)
    with sub_col1:
        st.markdown("**📁 Allocated Lots Tracker**")
        remaining_lots = total_lots_allocated - total_sell_lots
        st.markdown(f"### {total_sell_lots} / {total_lots_allocated} Lots Filled")
        
        if remaining_lots == 0:
            st.markdown("<span style='color:green;'>↑ 0 Lots Remaining (Perfect Sync)</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"<span style='color:orange;'>⚠️ {remaining_lots} Lots Unallocated in Legs</span>", unsafe_allow_html=True)
            
    with sub_col2:
        st.markdown("**💰 Combined Position Net P&L**")
        st.markdown(f"### ₹{combined_net_pnl:,.2f}")

with metric_col2:
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Structural Action Button Layout Split
    action_col1, action_col2 = st.columns(2)
    
    with action_col1:
        commit_btn = st.button("💾 Append & Save Trade", use_container_width=True, type="primary")
    with action_col2:
        clear_btn = st.button("🗑️ Clear Sheet Data", use_container_width=True, type="secondary")
        
    # Fixed direct transmission macro tunnel endpoint
    WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbzO0qab0Mw-eM-hGeiVs4ImXUgYIHyOhC8tRIditY42Y6Bg3Ey2EiHGsXe9RoNuzDxWbA/exec"

    # --- SAVE TO SHEET INTERFACE ENGINE ---
    if commit_btn:
        if total_sell_lots != total_lots_allocated:
            st.error(f"Allocation Mismatch: Your leg lots summary ({total_sell_lots}) must equal your main Lots Count ({total_lots_allocated}).")
        else:
            profile_log_summary = f"L1: {leg1_lots}L @ ₹{leg1_price:.1f} | L2: {leg2_lots}L @ ₹{leg2_price:.1f} | L3: {leg3_lots}L @ ₹{leg3_price:.1f}"
            
            ist_time = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)
            just_date_stamp = ist_time.strftime("%Y-%m-%d")
            
            # Formulate structured JSON payload matching the macro properties key engine exactly
            payload = {
                "action": "save",
                "date": just_date_stamp,
                "index": index_name,
                "pnl": float(combined_net_pnl),
                "lots": int(total_lots_allocated),
                "qty": int(total_quantity),
                "buy": float(buy_value),
                "sl": float(sl_exit_price),
                "breakdown": profile_log_summary
            }
            
            try:
                # Dispatches transaction payload seamlessly to the cloud macro
                response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
                if response.status_code == 200 or "success" in response.text.lower():
                    st.session_state["trade_saved_success"] = True
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(f"Web App responded with an error text sequence: {response.text}")
            except Exception as e:
                st.error(f"Failed transmission over the automated webhook pipeline: {e}")

    # --- WIPE / CLEAR WORKSHEET ENGINE ---
    if clear_btn:
        try:
            # Deliver a structured clearing flag payload over an HTTP POST request to bypass read-only locks
            response = requests.post(WEBHOOK_URL, json={"action": "clear"}, timeout=15)
            
            # Check for a valid execution response back from your Apps Script server
            if response.status_code == 200 or "success" in response.text.lower():
                # Force local application state to drop stale views
                st.cache_data.clear()
                st.toast("🧹 Sheet data records wiped clean! Ready for new entries.", icon="ℹ️")
                st.rerun()
            else:
                st.error(f"Web App clearing engine failed. Server response: {response.text}")
                
        except Exception as e:
            st.error(f"Failed transmission over the automated webhook clearing pipeline: {e}")
