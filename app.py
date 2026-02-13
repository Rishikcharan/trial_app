import streamlit as st
import pandas as pd
import altair as alt
import firebase_admin
from firebase_admin import credentials, db
import datetime
import json

# ---------------- FIREBASE INIT ----------------
# Load Firebase credentials from Streamlit Secrets
firebase_config = dict(st.secrets["firebase"])
cred = credentials.Certificate(firebase_config)

# Initialize Firebase app
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://trial-app-d297a-default-rtdb.asia-southeast1.firebasedatabase.app/"
    })

# ---------------- STREAMLIT UI ----------------
st.set_page_config(page_title="LEMS Smart Dashboard", layout="wide")
st.title("🌍 LEMS Smart Environment Dashboard")

# Fetch latest sensor data
ref = db.reference("/sensors")
data = ref.get()

if data:
    # Show metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("🌡 Temperature (°C)", f"{data.get('temp', '--')}")
    col2.metric("💧 Humidity (%)", f"{data.get('hum', '--')}")
    col3.metric("🌫 AQI", f"{data.get('aqi', '--')}")

    col4, col5 = st.columns(2)
    col4.metric("🔥 Gas (%)", f"{data.get('gas', '--')}")
    col5.metric("🔊 Noise (dB)", f"{data.get('noise', '--')}")

    st.subheader("System Status")
    st.info(f"{data.get('status', 'No status')}")
    st.write(f"Action: **{data.get('action', 'N/A')}**")

    # Example historical chart (if you log history in Firebase)
    history = pd.DataFrame([
        {"time": datetime.datetime.now(), "temp": data.get("temp", 0), "aqi": data.get("aqi", 0)}
    ])
    chart = alt.Chart(history).mark_line().encode(
        x="time:T",
        y="temp:Q"
    )
    st.altair_chart(chart, use_container_width=True)
else:
    st.warning("No sensor data found in Firebase yet.")


