import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import altair as alt
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="ESP32 Sensor Dashboard", layout="wide")
st.title("ESP32 Smart Environment Dashboard")

# 🔑 Update with your ESP32 IP (from Serial Monitor)
ESP32_IP = "http://10.20.61.91"   # replace with your ESP32 IP
DATA_URL = f"{ESP32_IP}/data"

# Sidebar controls
st.sidebar.header("Controls")
temp_threshold = st.sidebar.slider("Temperature Threshold (°C)", 0, 50, 35)
aqi_threshold = st.sidebar.slider("Air Quality Threshold (AQI)", 0, 500, 300)

# Auto-refresh every 5 seconds
st_autorefresh(interval=5000, limit=None)

# Storage for data
if "data_log" not in st.session_state:
    st.session_state["data_log"] = []

# Fetch ESP32 data
try:
    response = requests.get(DATA_URL, timeout=3)
    if response.status_code == 200:
        d = response.json()
        d["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state["data_log"].append(d)
    else:
        st.warning("ESP32 not responding...")
except Exception as e:
    st.error(f"Error fetching ESP32 data: {e}")

df = pd.DataFrame(st.session_state["data_log"])

if not df.empty:
    latest = df.iloc[-1]

    # Metrics
    st.metric("Temperature (°C)", latest["temp"])
    st.metric("Air Quality (AQI)", latest["aqi"])
    st.caption(f"Last updated: {latest['timestamp']}")

    # ✅ Real-time alerts
    if latest["temp"] > temp_threshold:
        st.error(f"🌡️ Temperature {latest['temp']}°C exceeded {temp_threshold}°C!")
    if latest["aqi"] > aqi_threshold:
        st.error(f"🌫 AQI {latest['aqi']} exceeded {aqi_threshold}!")

    # Chart function
    def plot_chart(df, y_col, color, threshold, title):
        chart = alt.Chart(df).mark_line(color=color).encode(
            x="timestamp:T",
            y=f"{y_col}:Q"
        )
        threshold_line = alt.Chart(df).mark_rule(color="red").encode(
            y=alt.Y("y:Q", axis=None)
        ).transform_calculate(y=str(threshold))
        st.subheader(title)
        st.altair_chart(chart + threshold_line, use_container_width=True)

    # Graphs
    plot_chart(df, "temp", "green", temp_threshold, "Temperature")
    plot_chart(df, "aqi", "blue", aqi_threshold, "Air Quality (MQ-135)")

    # Download data
    st.download_button(
        label="Download Data",
        data=df.to_csv(index=False),
        file_name="esp32_data.csv",
        mime="text/csv"
    )
else:
    st.info("Waiting for ESP32 data...")
