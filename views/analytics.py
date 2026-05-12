import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import os
from dotenv import find_dotenv, load_dotenv

# Load environment variables
# load_dotenv(find_dotenv())
# BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8080")
# BACKEND_URL = "http://raspberrypi:8000"


load_dotenv(find_dotenv())

PI_IPADDR = os.getenv("PI_IPADDR")

st.title("📊 Traffic & Revenue Analytics")
st.write("Analyze the correlation between store foot traffic, weather conditions, and revenue.")

@st.cache_data(ttl=600)
def fetch_analytics_data():
    try:
        response = requests.get(f"{PI_IPADDR}:8000/analytics")
        response.raise_for_status()
        return response.json()
    except Exception:
        return []

@st.cache_data(ttl=600)
def fetch_traffic_trends():
    try:
        response = requests.get(f"{PI_IPADDR}:8000/traffic-trends")
        response.raise_for_status()
        return response.json()
    except Exception:
        return None

# Fetch data from the FastAPI backend
data = fetch_analytics_data()
trends_data = fetch_traffic_trends()

# --- Fallback Logic for Presentation ---
if data and trends_data and trends_data.get("hourly"):
    st.success("🟢 Connected to Cloud SQL: Displaying live database records.")
    df = pd.DataFrame(data)
    df_hourly = pd.DataFrame(trends_data["hourly"])
    df_dow = pd.DataFrame(trends_data["day_of_week"])
else:
    st.warning("⚠️ No live data found. Displaying mock data for presentation purposes.")
    # Mock Data for Revenue/Weather
    mock_data = [
        {"date": "2026-05-05", "total_revenue": 1150.00, "foot_traffic": 45, "avg_temp": 68.5},
        {"date": "2026-05-06", "total_revenue": 1300.50, "foot_traffic": 52, "avg_temp": 71.2},
        {"date": "2026-05-07", "total_revenue": 950.75, "foot_traffic": 30, "avg_temp": 55.0},
        {"date": "2026-05-08", "total_revenue": 1420.00, "foot_traffic": 60, "avg_temp": 75.1},
        {"date": "2026-05-09", "total_revenue": 1850.25, "foot_traffic": 85, "avg_temp": 80.3},
        {"date": "2026-05-10", "total_revenue": 2100.00, "foot_traffic": 95, "avg_temp": 82.0},
        {"date": "2026-05-11", "total_revenue": 1600.50, "foot_traffic": 70, "avg_temp": 78.4},
    ]
    df = pd.DataFrame(mock_data)
    
    # Mock Data for Hourly Trends (Store Hours 7AM - 5PM)
    df_hourly = pd.DataFrame([
        {"hour": 7, "count": 15}, {"hour": 8, "count": 45}, {"hour": 9, "count": 80},
        {"hour": 10, "count": 110}, {"hour": 11, "count": 140}, {"hour": 12, "count": 185},
        {"hour": 13, "count": 170}, {"hour": 14, "count": 130}, {"hour": 15, "count": 95},
        {"hour": 16, "count": 60}, {"hour": 17, "count": 25}
    ])
    
    # Mock Data for Days of the Week
    df_dow = pd.DataFrame([
        {"day": "Monday", "count": 310}, {"day": "Tuesday", "count": 345},
        {"day": "Wednesday", "count": 420}, {"day": "Thursday", "count": 380},
        {"day": "Friday", "count": 450}, {"day": "Saturday", "count": 150},
        {"day": "Sunday", "count": 80},
    ])

# Format the DataFrames
df['date'] = pd.to_datetime(df['date'])
# Convert 24-hour integer to a clean 12-hour AM/PM string for the charts
df_hourly['time_label'] = pd.to_datetime(df_hourly['hour'], format='%H').dt.strftime('%I %p')

# --- Top Level Metrics ---
m1, m2, m3 = st.columns(3)
m1.metric("Total Days Logged", len(df))
m2.metric("Average Daily Revenue", f"${df['total_revenue'].mean():.2f}")
m3.metric("Avg Daily Foot Traffic", f"{df['foot_traffic'].mean():.0f} people")

st.divider()

# --- Visualization Grid ---
# We use two columns here so the charts display nicely side-by-side on wide screens
col1, col2 = st.columns(2)

with col1:
    # Chart 1: Hourly Trends
    st.subheader("Busiest Times of Day")
    fig_hourly = px.bar(
        df_hourly, x="time_label", y="count", 
        labels={"time_label": "Hour of the Day", "count": "Foot Traffic Count"},
        color="count", color_continuous_scale="Blues"
    )
    st.plotly_chart(fig_hourly, use_container_width=True)
    
    # Chart 3: Temperature vs Revenue
    st.subheader("Weather vs. Revenue")
    fig_temp_rev = px.scatter(
        df, x="avg_temp", y="total_revenue", size="foot_traffic", color="foot_traffic",
        labels={"avg_temp": "Average Temp (°F)", "total_revenue": "Daily Revenue ($)", "foot_traffic": "Traffic"},
        color_continuous_scale="Blues"
    )
    st.plotly_chart(fig_temp_rev, use_container_width=True)

with col2:
    # Chart 2: Day of Week Trends
    st.subheader("Busiest Days of the Week")
    fig_dow = px.bar(
        df_dow, x="day", y="count", 
        labels={"day": "Day of the Week", "count": "Total Foot Traffic"},
        color="count", color_continuous_scale="Blues"
    )
    st.plotly_chart(fig_dow, use_container_width=True)

    # Chart 4: Timeline Trend
    st.subheader("Traffic & Revenue Timeline")
    fig_timeline = px.line(
        df, x="date", y=["total_revenue", "foot_traffic"],
        labels={"value": "Count / Amount ($)", "date": "Date", "variable": "Metric"}
    )
    st.plotly_chart(fig_timeline, use_container_width=True)

st.divider()

# --- Admin Section: Upload Revenue Data ---
st.subheader("📁 Upload Daily Sales Data")
st.write("Upload a CSV containing your end-of-day point-of-sale totals to populate the live database.")

uploaded_file = st.file_uploader("Drop CSV Here", type=["csv"], label_visibility="collapsed")

if uploaded_file is not None:
    try:
        df_upload = pd.read_csv(uploaded_file)
        if not all(col in df_upload.columns for col in ['date', 'total_revenue']):
            st.error("Invalid CSV format. Please ensure columns are named 'date' and 'total_revenue'.")
        else:
            st.dataframe(df_upload.head(3), use_container_width=True) 
            if st.button("Submit to Database"):
                with st.spinner("Uploading records to Cloud SQL..."):
                    payload = df_upload.to_dict(orient="records")
                    response = requests.post(f"{PI_IPADDR}:8000/revenue", json=payload)
                    if response.status_code == 200:
                        st.success(response.json()["message"])
                        fetch_analytics_data.clear()
                        fetch_traffic_trends.clear()
                        st.rerun()
                    else:
                        st.error(f"Backend Error: {response.text}")
    except Exception as e:
        st.error(f"Error processing file: {e}")
