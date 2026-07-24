from datetime import datetime, timezone, timedelta
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# ----------------------------------------------------
# 1. INITIAL SETUP & SYSTEM SETTINGS
# ----------------------------------------------------
st.set_page_config(
    page_title="Avengers Position Monitor Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# Flash status notification parameters on page load cycles
if "trade_saved_success" not in st.session_state:
    st.session_state["trade_saved_success"] = False

if st.session_state["trade_saved_success"]:
    st.success("🎯 Trade entry successfully written directly to your Cloud Google Sheet tracker!")
    st.session_state["trade_saved_success"] = False


# ----------------------------------------------------
# 2. MAIN APP TITLE HEADER
# ----------------------------------------------------
st.markdown("## 🛡️ Avengers Position Monitor Dashboard")
st.markdown("<br>", unsafe_allow_html=True)


# ----------------------------------------------------
# 3. ORIGINAL TWO-COLUMN SETUP: BUY VS. SELL SIDE
# ----------------------------------------------------
# This forces the layout back into your true horizontal split columns
trade_col1, trade_col2 = st.columns(2)

with trade_col1:
    st.markdown("#### 📥 Buy Side Entry Parameters")
    
    # 🎯 ALL ORIGINAL BUY SIDE FIELDS PUT BACK EXACTLY WHERE THEY BELONG:
    index_name = st.selectbox("Select Index Name", ["NIFTY", "BANKNIFTY", "FINNIFTY", "SENSEX"])
    buy_lots = st.number_input("Lots Count", min_value=1, value=3, step=1)
    base_multiplier = st.number_input("Lot Size Base Units", min_value=1, value=25, step=5)
    buy_value = st.number_input("Average Buy Entry Price (₹)", min_value=0.0, value=135.50, step=0.5, format="%.2f")
    
    st.caption("Enter your baseline entry premium cost average.")

with trade_col2:
    st.markdown("#### 📤 Sell Side Target Parameters (3 Legs)")
    
    # Side-by-side splits inside the Sell column for clean Leg inputs
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

    # Risk safety configuration field
    st.markdown("**🛡️ Risk Management**")
    sl_exit_price = st.number_input("Stop Loss Protection Floor (₹)", min_value=0.0, value=115.00, step=0.5, format="%.2f")


# ----------------------------------------------------
# 4. MATH ENGINE: AUTOMATIC POSITION CALCULATIONS
# ----------------------------------------------------
total_lots_allocated = buy_lots
total_quantity = int(total_lots_allocated * base_multiplier)
total_sell_lots = leg1_lots + leg2_lots + leg3_lots

if total_sell_lots > 0:
    # Calculate the blended average sell price based on your multi-leg targets
    average_sell_price = ((leg1_lots * leg1_price) + (leg2_lots * leg2_price) + (leg3_lots * leg3_price)) / total_sell_lots
else:
    average_sell_price = 0.0

# Computing final net P&L completely dynamically using your live values
total_cost_basis = total_sell_lots * base_multiplier * buy_value
total_revenue_basis = total_sell_lots * base_multiplier * average_sell_price
combined_net_pnl = total_revenue_basis - total_cost_basis


# ----------------------------------------------------
# 5. SUMMARY REALIZATION PANELS & CLOUD SUBMISSION
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
    
    # Submission button triggers validation checks and database uploads
    if st.button("💾 Append & Save Trade Row to Cloud Google Sheet", use_container_width=True, type="primary"):
        if total_sell_lots != total_lots_allocated:
            st.error(f"Allocation Mismatch: Your leg lots summary ({total_sell_lots}) must equal your main Lots Count ({total_lots_allocated}).")
        else:
            pnl_status_text = f"🟢 Profit: +₹{combined_net_pnl:,.2f}" if combined_net_pnl >= 0 else f"🔴 Loss: -₹{abs(combined_net_pnl):,.2f}"
            profile_log_summary = f"L1: {leg1_lots}L @ ₹{leg1_price:.1f} | L2: {leg2_lots}L @ ₹{leg2_price:.1f} | L3: {leg3_lots}L @ ₹{leg3_price:.1f}"
            
            # Formulating timezone offset calculations for Indian Standard Time (IST)
            ist_time = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)
            just_date_stamp = ist_time.strftime("%Y-%m-%d")

            try:
                conn = st.connection("gsheets", type=GSheetsConnection)
                existing_df = conn.read(worksheet="Form Responses 1", ttl=0)
                
                if "Timestamp" in existing_df.columns:
                    existing_df = existing_df.drop(columns=["Timestamp"])
                
                # Dictionary mapping elements precisely down onto your target grid parameters column headers
                new_row_dict = {
                    "date": just_date_stamp,
                    "index": str(index_name),
                    "pnl": str(pnl_status_text),
                    "lots": int(buy_lots),
                    "quantity": int(total_quantity),
                    "buy": f"₹{buy_value:.2f}",
                    "sl": f"₹{sl_exit_price:.2f}",
                    "breakdown": str(profile_log_summary)
                }
                
                new_row_df = pd.DataFrame([new_row_dict])
                updated_df = pd.concat([existing_df, new_row_df], ignore_index=True)
                
                # Committing dataframe payload directly to cloud workspace
                conn.update(worksheet="Form Responses 1", data=updated_df)
                st.session_state["trade_saved_success"] = True
                st.rerun()
                
            except Exception as database_error:
                st.error(f"Spreadsheet Link Blocked: {database_error}")


# ----------------------------------------------------
# 6. HISTORICAL TRACKING SHEET MONITOR LIVE VIEW
# ----------------------------------------------------
st.markdown("---")
st.markdown("#### 📋 Cloud Google Sheet Database Live Grid Monitor")

try:
    live_conn = st.connection("gsheets", type=GSheetsConnection)
    live_df = live_conn.read(worksheet="Form Responses 1", ttl=2)
    
    if "Timestamp" in live_df.columns:
        live_df = live_df.drop(columns=["Timestamp"])
        
    st.dataframe(live_df, use_container_width=True, height=350)
except Exception as read_error:
    st.warning(f"Could not render active live preview grid layout: {read_error}")
