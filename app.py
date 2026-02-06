import streamlit as st
import pandas as pd
import random
import time
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Daily Data Logger", layout="centered")
st.title("Daily Data Logger with Firebase")

# Initialize Firebase only once
if not firebase_admin._apps:
    firebase_secrets = dict(st.secrets["firebase"])
    cred = credentials.Certificate(firebase_secrets)
    firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()

# Collection name = today's date
today_str = datetime.now().strftime("%Y-%m-%d")
collection_ref = db.collection(today_str)

# Function to add new value
def add_new_value():
    new_row = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "value": random.randint(0, 100)
    }
    collection_ref.add(new_row)
    time.sleep(0.5)  # ✅ give Firestore time to commit

# Function to reset today's data
def reset_firestore():
    docs = collection_ref.stream()
    for doc in docs:
        doc.reference.delete()

# Auto-refresh every 10 seconds
st_autorefresh(interval=10000, limit=None)

# Add new value each refresh
add_new_value()

# Reset button
if st.button("Reset Today's Data"):
    reset_firestore()
    st.success(f"All data cleared for {today_str}")
    st.rerun()

# Read last 50 documents safely
try:
    docs = collection_ref.limit_to_last(50).get()
    if not docs:  # fallback if query empty
        docs = collection_ref.stream()
    data = [doc.to_dict() for doc in docs]
except Exception as e:
    st.error(f"Error reading Firestore: {e}")
    data = []

df = pd.DataFrame(data)

# Ensure required columns exist
if not df.empty and "timestamp" in df.columns and "value" in df.columns:
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp", "value"])
    df = df.sort_values("timestamp")

    if not df.empty:
        latest_value = df.iloc[-1]["value"]
        latest_time = df.iloc[-1]["timestamp"].strftime("%Y-%m-%d %H:%M:%S")

        st.metric(label="Latest Sensor Value", value=latest_value)
        st.caption(f"Last updated: {latest_time}")

        st.line_chart(df.set_index("timestamp")["value"])

        st.download_button(
            label=f"Download {today_str} data",
            data=df.to_csv(index=False),
            file_name=f"data_{today_str}.csv",
            mime="text/csv"
        )
    else:
        st.warning("No valid data available yet. Waiting for auto-refresh...")
else:
    st.warning("No data yet. Waiting for auto-refresh to log the first entry...")
