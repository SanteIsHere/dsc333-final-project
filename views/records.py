import streamlit as st
import pandas as pd
import requests


def fetch_records():
    """Fetches records from the FastAPI backend."""
    try:
        # IMPORTANT: Ensure this URL matches where your backend is hosted.
        # If running on the Pi, use localhost or 127.0.0.1. If viewing from
        # a different machine, use the Pi's IP (e.g., http://10.0.0.105:8080/records)
        response = requests.get("http://raspberrypi:8000/records")
        response.raise_for_status()

        # THE FIX: Return the JSON list directly so Pandas can consume it
        return response.json()
    except Exception as e:
        st.error(f"Failed to fetch data from backend: {e}")
        return []


# --- Page UI ---
st.title("Historical Foot Traffic Log 🔗")
st.info(
    "Currently displaying live data from the FastAPI backend and Cloud SQL database."
)

# Layout for the refresh button
col1, col2 = st.columns([3, 1])
with col2:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()

# Fetch the data
records_data = fetch_records()

# Display the interactive table
if records_data:
    df = pd.DataFrame(records_data)

    # Render the dataframe cleanly across the container
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Bottom diagnostic metrics
    st.divider()
    st.write("### Diagnostics")
    colA, colB = st.columns(2)
    with colA:
        st.metric(label="Records Displayed", value=len(df))
    with colB:
        st.metric(label="Backend Status", value="Connected", delta="Active")
else:
    st.warning("No records found. Walk in front of the camera to log an event!")
