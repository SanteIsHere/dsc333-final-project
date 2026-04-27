import streamlit as st

# 1. Global Page Configuration
# This must be the very first Streamlit command executed
st.set_page_config(
    page_title="Lansing Building Products Analytics", page_icon="📊", layout="wide"
)

# 2. Define the Pages mapping to your views/ directory
presentation_page = st.Page(
    "views/presentation.py", title="Project Presentation", icon="📽️", default=True
)
camera_page = st.Page("views/camera.py", title="Live Camera Feed", icon="📷")
records_page = st.Page("views/records.py", title="Detection Records", icon="📜")

# 3. Build the Navigation Sidebar
# Grouping them in a dictionary creates clean headers in the sidebar menu
pg = st.navigation(
    {
        "Project Overview": [presentation_page],
        "Live Analytics": [camera_page, records_page],
    }
)

# 4. Run the selected page
pg.run()
