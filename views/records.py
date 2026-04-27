import streamlit as st
import requests
import pandas as pd

# Title and headers
st.title("📜 Detection Records")
st.subheader("Historical Foot Traffic Log")

# Note about the current backend status
st.info("Currently displaying placeholder data from the FastAPI backend until the Cloud SQL database is fully integrated.")

# Define the backend records endpoint
# IMPORTANT: Update this to the Pi's IP or PiTunnel URL if presenting remotely
RECORDS_URL = "http://localhost:8080/records"

def fetch_records():
    """Fetches the dummy records from the FastAPI backend."""
    try:
        # Optional timeout so the page doesn't hang forever if the backend is down
        response = requests.get(RECORDS_URL, timeout=5)
        response.raise_for_status() 
        return response.json().get("results", [])
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to connect to the backend. Ensure FastAPI is running. Error: {e}")
        return []

# Add a manual refresh button aligned to the right
col1, col2 = st.columns([3, 1])
with col2:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()

# Fetch and display the data
records_data = fetch_records()

if records_data:
    # Convert list of dictionaries to a pandas DataFrame for a cleaner UI
    df = pd.DataFrame(records_data)
    
    # Capitalize column headers to make them look more professional
    df.columns = [col.capitalize() for col in df.columns]
    
    # Display as an interactive dataframe without the ugly default index numbers
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Add a quick metrics section at the bottom
    st.divider()
    st.write("### Quick Stats")
    stat_col1, stat_col2 = st.columns(2)
    with stat_col1:
        st.metric("Total Events Logged", len(df))
    with stat_col2:
        # Grab the 'Time' value from the very last row as a placeholder stat
        latest_time = df['Time'].iloc[-1] if not df.empty else "N/A"
        st.metric("Last Detection Time", latest_time)
else:
    st.warning("No records found. The backend might be offline or returning an empty list.")
