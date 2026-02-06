import streamlit as st
import pandas as pd
import random
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

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

# Button to refresh data
if st.button("Refresh data"):
    add_new_value()
    st.success("New value added and data refreshed!")

# Read all data from Firestore
docs = collection_ref.stream()
data = [doc.to_dict() for doc in docs]
df = pd.DataFrame(data)

# Show latest values
if not df.empty:
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
else:
    st.warning("No data yet. Click 'Refresh data' to add the first entry.")
