import streamlit as st
import pandas as pd
import random
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
    # Debug log so you can see writes happening
    st.write("Added new row:", new_row)

# Auto-refresh every 10 seconds (gives Firestore time to commit)
st_autorefresh(interval=10000, limit=None)

# Add new value each refresh
add_new_value()

# Read all data from Firestore
docs = collection_ref.stream()
data = [doc.to_dict() for doc in docs if "timestamp" in doc.to_dict() and "value" in doc.to_dict()]
df = pd.DataFrame(data)

# Show summary instead of raw table
if not df.empty:
    # Sort by timestamp to ensure correct order
    df = df.sort_values("timestamp")

    latest_value = df.iloc[-1]["value"]
    latest_time = df.iloc[-1]["timestamp"]

    # Metric card for latest value
    st.metric(label="Latest Sensor Value", value=latest_value)
    st.caption(f"Last updated: {latest_time}")

    # Line chart of last 20 values (rolling window)
    st.line_chart(df.tail(20).set_index("timestamp")["value"])

    # Download button
    st.download_button(
        label=f"Download {today_str} data",
        data=df.to_csv(index=False),
        file_name=f"data_{today_str}.csv",
        mime="text/csv"
    )
else:
    st.warning("No data yet. Waiting for auto-refresh to log the first entry...")
