import streamlit as st
import pandas as pd
import altair as alt
import firebase_admin
from firebase_admin import credentials, db
import datetime

# ---------------- FIREBASE INIT ----------------
firebase_config = dict(st.secrets["firebase"])
cred = credentials.Certificate(firebase_config)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://trial-app-d297a-default-rtdb.asia-southeast1.firebasedatabase.app/"
    })

# ---------------- STREAMLIT UI ----------------
st.set_page_config(page_title="LEMS Smart Dashboard", layout="wide")
st.title("🌍 LEMS Smart Environment Dashboard")

tab_today, tab_history = st.tabs(["📊 Today", "📅 Previous Dates"])

# ---------------- TODAY TAB ----------------
with tab_today:
    from streamlit import st_autorefresh

# inside your Today tab
st_autorefresh(interval=5000, limit=None)

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

        # Append today's history from Firebase
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        history_ref = db.reference(f"/history/{today_str}")
        history_data = history_ref.get()

        if history_data:
            df = pd.DataFrame([
                {"time": ts, **entry} for ts, entry in history_data.items()
            ])
            df["time"] = pd.to_datetime(df["time"])

            st.subheader("🌡 Temperature Trend (Today)")
            temp_chart = alt.Chart(df).mark_line(color="orange").encode(
                x="time:T", y="temp:Q"
            )
            st.altair_chart(temp_chart, use_container_width=True)

            st.subheader("🌫 AQI Trend (Today)")
            aqi_chart = alt.Chart(df).mark_line(color="green").encode(
                x="time:T", y="aqi:Q"
            )
            st.altair_chart(aqi_chart, use_container_width=True)
        else:
            st.warning("No history logged yet for today.")
    else:
        st.warning("No sensor data found in Firebase yet.")

# ---------------- HISTORY TAB ----------------
with tab_history:
    st.header("Historical Graphs by Date")

    history_ref = db.reference("/history")
    history_data = history_ref.get()

    if history_data:
        available_dates = list(history_data.keys())
        selected_date = st.selectbox("Select a date:", available_dates)

        if selected_date:
            day_data = history_data[selected_date]
            df = pd.DataFrame([
                {"time": ts, **entry} for ts, entry in day_data.items()
            ])
            df["time"] = pd.to_datetime(df["time"])

            st.subheader(f"🌡 Temperature Trend ({selected_date})")
            temp_chart = alt.Chart(df).mark_line(color="orange").encode(
                x="time:T", y="temp:Q"
            )
            st.altair_chart(temp_chart, use_container_width=True)

            st.subheader(f"🌫 AQI Trend ({selected_date})")
            aqi_chart = alt.Chart(df).mark_line(color="green").encode(
                x="time:T", y="aqi:Q"
            )
            st.altair_chart(aqi_chart, use_container_width=True)

            # Download CSV
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download this day's data as CSV",
                data=csv,
                file_name=f"{selected_date}_sensor_data.csv",
                mime="text/csv",
            )
    else:
        st.warning("No historical data found yet.")


