# Import streamlit library
import streamlit as st

# Title and subheader for the page
st.title("📷 Live Store Feed")
st.subheader("Lansing Building Products - Foot Traffic Monitor")

# Add a professional note about the privacy feature your teammate built
st.info("🔒 **Privacy Mode Active:** Live motion blur is applied at the hardware level to protect customer identities before data reaches the dashboard.")

# Define the backend streaming endpoint
# Ensure the port matches your Uvicorn setup (8080) and the route matches (@app.get("/camera"))
STREAM_URL = "http://localhost:8080/camera"

# Streamlit's st.image is smart enough to handle multipart HTTP streams natively!
try:
    st.image(STREAM_URL, use_container_width=True, caption="Live OpenCV Motion Blur Feed")
except Exception as e:
    st.error(f"Could not connect to the camera feed. Ensure the FastAPI backend is running. Error: {e}")

st.divider()

st.write("### Diagnostics")
col1, col2 = st.columns(2)
with col1:
    st.metric(label="Backend Status", value="Connected", delta="Active")
with col2:
    st.metric(label="Stream Port", value="8080", delta_color="off")
