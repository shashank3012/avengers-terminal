from datetime import datetime, timezone, timedelta
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Page setup configuration variables
st.set_page_config(page_title="Avengers Position Tracker", layout="wide")

if "trade_saved_success" not in st.session_state:
    st.session_state["trade_saved_success"] = False

if st.session_state["trade_saved_success"]:
    st.success("🎯 Trade entry successfully written directly to your Cloud Google Sheet tracker!")
    st.session_state["trade_saved_success"] = False

# --- INPUT UI FIELDS FOR YOUR TRADING RUNS ---
st.title("🛡️ Avengers Position Monitor Dashboard")

index_name = st.selectbox("Select Index Name", ["NIFTY", "BANKNIFTY", "FINNIFTY"])
buy_lots = st.number_input("Lots Count", min_value=1, value=3)
base_multiplier = st.number_input("Lot Size Base Units", min_value=1, value=25)
combined_net_pnl = st.number_input("Net P&L (₹)", value=5850.00)
buy_value = st.number_input("Average Buy Entry Price", value=135.50)
sl_exit_price = st.number_input("Stop Loss Protection Floor", value=115.00)

total_lots_allocated = buy_lots
leg1_lots, leg1_price = 1, 135.0
leg2_lots, leg2_price = 1, 136.0
leg3_lots, leg3_price = 1, 135.5

# --- APPEND SAVE BUTTON LOGIC BLOCK ---
if st.button("💾 Append & Save Trade Row to Cloud Google Sheet", use_container_width=True, type="primary"):
    if total_lots_allocated == 0:
        st.error("Cannot log a trade with zero allocated lots.")
    else:
        pnl_status_text = f"🟢 Profit: +₹{combined_net_pnl:,.2f}" if combined_net_pnl >= 0 else f"🔴 Loss: -₹{abs(combined_net_pnl):,.2f}"
        profile_log_summary = f"L1: {leg1_lots}L @ ₹{leg1_price:.1f} | L2: {leg2_lots}L @ ₹{leg2_price:.1f} | L3: {leg3_lots}L @ ₹{leg3_price:.1f}"
        
        # Formulate correct Indian Standard Time (IST) date marker
        ist_time = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)
        just_date_stamp = ist_time.strftime("%Y-%m-%d")

        try:
            # Connects directly using your hidden secrets configuration file
            conn = st.connection("gsheets", type=GSheetsConnection)
            existing_df = conn.read(worksheet="Form Responses 1", ttl=0)
            
            # If the loaded sheet contains an old Timestamp column header, strip it away cleanly
            if "Timestamp" in existing_df.columns:
                existing_df = existing_df.drop(columns=["Timestamp"])
            
            # Formatted exactly to match your lowercase sheet column framework layout
            new_row_dict = {
                "date": just_date_stamp,
                "index": str(index_name),
                "pnl": str(pnl_status_text),
                "lots": int(buy_lots),
                "quantity": int(total_lots_allocated * base_multiplier),
                "buy": f"₹{buy_value:.2f}",
                "sl": f"₹{sl_exit_price:.2f}",
                "breakdown": str(profile_log_summary)
            }
            
            new_row_df = pd.DataFrame([new_row_dict])
            updated_df = pd.concat([existing_df, new_row_df], ignore_index=True)
            
            # Push clean data payload directly onto cloud grid matrix tracking layouts
            conn.update(worksheet="Form Responses 1", data=updated_df)
            st.session_state["trade_saved_success"] = True
            st.rerun()
            
        except Exception as database_error:
            st.error(f"Spreadsheet Link Blocked: {database_error}")

# --- GRID LIVE SPREADSHEET MONITOR VIEW ---
st.markdown("---")
st.subheader("📋 Cloud Google Sheet Database Live Grid Monitor")
try:
    live_conn = st.connection("gsheets", type=GSheetsConnection)
    live_df = live_conn.read(worksheet="Form Responses 1", ttl=2)
    
    # Ensure view remains cleanly stripped of old Timestamp references dynamically
    if "Timestamp" in live_df.columns:
        live_df = live_df.drop(columns=["Timestamp"])
        
    st.dataframe(live_df, use_container_width=True, height=350)
except Exception as read_error:
    st.warning(f"Could not render active live preview grid layout: {read_error}")
