import streamlit as st
import pandas as pd
import random
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

st.title("Daily Data Logger with Firebase")

# Initialize Firebase (using Streamlit Secrets)
if not firebase_admin._apps:
    cred = credentials.Certificate(st.secrets["firebase"])
    firebase_admin.initialize_app(cred)

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

# Auto-refresh every 5 seconds
st_autorefresh = st.experimental_autorefresh(interval=5000, limit=None)

# Add new value each refresh
add_new_value()

# Read all data from Firestore
docs = collection_ref.stream()
data = [doc.to_dict() for doc in docs]
df = pd.DataFrame(data)

# Show latest values
st.write(f"Latest values from {today_str}:", df.tail(10))

# Plot graph
st.line_chart(df.set_index("timestamp")["value"])

# Download button
st.download_button(
    label=f"Download {today_str} data",
    data=df.to_csv(index=False),
    file_name=f"data_{today_str}.csv",
    mime="text/csv"
)