
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
sys.path.append(str(ROOT_DIR))

import streamlit as st

st.set_page_config(page_title="Weekly Bullish Scanner", layout="wide")

st.title("📈 Weekly Bullish Scanner")
st.write("Welcome to your stock scanner dashboard.")

if st.button("Run Scan"):
    with st.spinner("Running scanner..."):
        try:
            # Import directly from engine, since it's in the root folder now
            from engine import run_scanner
            st.success("Scanner executed successfully!")
        except Exception as e:
            st.error(f"Error: {e}")
