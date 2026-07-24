import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
from streamlit_gsheets import GSheetsConnection

# 1. Page Configuration
st.set_page_config(page_title="Avengers Trading", layout="wide")
st.title("🦸‍♂️ Avengers Trading Command Center")

LOT_SIZE_MAPPING = {"NIFTY 50": 65, "SENSEX": 20, "BANKNIFTY": 30}

# 2. Setup Data Engine (TTL=0 disables cache)
conn = st.connection("gsheets", type=GSheetsConnection)
try:
    ledger_df = conn.read(ttl=0)
except:
    ledger_df = pd.DataFrame()

# 3. Input UI
index_name = st.selectbox("Select Index", list(LOT_SIZE_MAPPING.keys()))
buy_col, sell_col = st.columns(2)

with buy_col:
    buy_lots = st.number_input("Lots", min_value=1, value=3)
    buy_value = st.number_input("Buy Value", value=100.0)
    buy_qty = buy_lots * LOT_SIZE_MAPPING[index_name]

with sell_col:
    exit_price = st.number_input("Exit Price", value=120.0)
    
if st.button("💾 Save Trade", type="primary"):
    # Calculate P&L and Prepare Data
    pnl = (exit_price - buy_value) * buy_qty
    
    new_row = pd.DataFrame([{
        "Date": datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S"),
        "Index": index_name,
        "P&L": pnl,
        "Qty": buy_qty
    }])
    
    # 4. Update Sheet
    updated_df = pd.concat([ledger_df, new_row], ignore_index=True)
    conn.update(data=updated_df)
    st.success("Trade Recorded!")
    st.rerun()

# 5. Display Sheet
if not ledger_df.empty:
    st.dataframe(ledger_df)
