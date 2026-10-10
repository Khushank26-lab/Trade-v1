import streamlit as st
from app.engine import run_scanner  # Adjust based on your actual function names

st.set_page_config(page_title="Weekly Bullish Scanner", layout="wide")

st.title("📈 Weekly Bullish Scanner")
st.write("Welcome to your stock scanner dashboard.")

if st.button("Run Scanner"):
    with st.spinner("Scanning markets..."):
        # Call your backend logic here
        # results = run_scanner()
        st.success("Scan complete!")
        # st.dataframe(results)
