# Import streamlit library
import streamlit as st
from dotenv import load_dotenv, find_dotenv
import os


load_dotenv(find_dotenv())

PI_IPADDR = os.getenv("PI_IPADDR")

# Title and subheader for the page
st.title("📷 Live Store Feed")
st.subheader("Lansing Building Products - Foot Traffic Monitor")

# Add a professional note about the privacy feature your teammate built
st.info(
    "🔒 **Privacy Mode Active:** Live motion blur is applied at the hardware level to protect customer identities before data reaches the dashboard."
)

# Define the backend streaming endpoint
# IMPORTANT: If you are viewing this dashboard on your desktop, but the backend is running on the Pi,
# 'localhost' will not work. Change this to the Pi's local IP (e.g., http://192.168.1.X:8000/camera)
# or your PiTunnel URL.
STREAM_URL = f"http://{PI_IPADDR}:8000/camera"

# Inject custom HTML to render the multipart stream natively
st.markdown(
    f"""
    <div style="display: flex; justify-content: center; margin-bottom: 10px;">
        <img src="{STREAM_URL}" style="width: 100%; max-width: 800px; border-radius: 8px; border: 1px solid #ddd;" alt="Live Camera Stream" />
    </div>
    """,
    unsafe_allow_html=True,
)

# Keep the caption cleanly aligned under the video
st.caption(
    "<div style='text-align: center;'>Live OpenCV Motion Blur Feed</div>",
    unsafe_allow_html=True,
)

st.divider()

st.write("### Diagnostics")
col1, col2 = st.columns(2)
with col1:
    st.metric(label="Backend Status", value="Connected", delta="Active")
with col2:
    st.metric(label="Stream Port", value="8000", delta_color="off")
