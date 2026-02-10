import sys
import os
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import psutil

# ---------------- PATH SETUP ----------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.processing.pipeline import build_pipeline
from backend.anomaly import detect_anomaly
from backend.email_service import send_mail

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Log Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- DARK THEME ----------------
st.markdown("""
<style>
body { background-color: #0E1117; color: white; }
[data-testid="stSidebar"] { background-color: #161b22; }
</style>
""", unsafe_allow_html=True)

st.title("📊 High Throughput Log Analytics & Monitoring Engine")

# ---------------- SIDEBAR ----------------
menu = st.sidebar.radio(
    "Navigation",
    ["Upload Logs", "Process Logs", "Dashboard", "Email Alerts"]
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "backend", "data")
os.makedirs(DATA_DIR, exist_ok=True)

# ---------------- UPLOAD LOGS ----------------
if menu == "Upload Logs":
    st.header("📁 Upload Log File")

    uploaded_file = st.file_uploader(
        "Upload log file",
        type=["csv", "log", "txt"]
    )

    if uploaded_file:
        file_path = os.path.join(DATA_DIR, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success(f"✅ {uploaded_file.name} uploaded successfully!")

# ---------------- PROCESS LOGS ----------------
elif menu == "Process Logs":
    st.header("⚙ Process Logs")

    file_name = st.text_input("Log File Name", value="sample_log.log")

    if st.button("🚀 Run Processing"):
        file_path = os.path.join(DATA_DIR, file_name)

        if os.path.exists(file_path):
            log_df = build_pipeline(file_path)
            anomaly_df = detect_anomaly(log_df)

            st.success("✅ Processing Complete!")
            st.write("Total Records:", log_df.shape[0].compute())
            st.write("Anomalies Detected:", len(anomaly_df))
        else:
            st.error("❌ File not found")

# ---------------- DASHBOARD ----------------
elif menu == "Dashboard":

    file_path = os.path.join(DATA_DIR, "sample_log.log")

    if not os.path.exists(file_path):
        st.error("❌ Please upload & process a log file first")
        st.stop()

    log_df = build_pipeline(file_path)
    anomaly_df = detect_anomaly(log_df)

    log_pd = log_df.compute()

    # ---------- METRICS ----------
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Logs", len(log_pd))
    col2.metric("Total Errors", (log_pd["level"] == "ERROR").sum())
    col3.metric("Anomalies", len(anomaly_df))

    st.divider()

    # ---------- PIE CHART ----------
    level_counts = (
        log_pd["level"]
        .value_counts()
        .reset_index(name="count")
        .rename(columns={"index": "level"})
    )

    pie_fig = px.pie(
        level_counts,
        names="level",
        values="count",
        hole=0.5,
        title="Log Level Distribution",
        template="plotly_dark"
    )
    st.plotly_chart(pie_fig, use_container_width=True)

    st.divider()

    # ---------- LOGS OVER TIME (ERROR / INFO / WARN) ----------
    st.subheader("📈 Logs Over Time by Level")

    log_pd["minute"] = log_pd["timestamp"].dt.floor("S")


    level_time = (
        log_pd.groupby(["minute", "level"])
        .size()
        .reset_index(name="count")
    )

    col1, col2, col3 = st.columns(3)

    for level, col in zip(["ERROR", "INFO", "WARN"], [col1, col2, col3]):
        level_df = level_time[level_time["level"] == level]

        fig = px.bar(
            level_df,
            x="minute",
            y="count",
            title=f"{level} Logs Over Time",
            template="plotly_dark"
        )
        col.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ---------- ERROR COUNT PER MINUTE ----------
    st.subheader("⏱ Error Count Per Minute")

    error_minute = (
        log_pd[log_pd["level"] == "ERROR"]
        .groupby("minute")
        .size()
        .reset_index(name="error_count")
    )

    error_line = px.line(
        error_minute,
        x="minute",
        y="error_count",
        markers=True,
        title="Error Frequency Over Time",
        template="plotly_dark"
    )

    st.plotly_chart(error_line, use_container_width=True)

    st.divider()

    # ---------- CPU & MEMORY ----------
    col1, col2 = st.columns(2)

    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory().percent

    cpu_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=cpu,
        title={"text": "CPU Usage (%)"},
        gauge={"axis": {"range": [0, 100]}}
    ))
    cpu_fig.update_layout(template="plotly_dark")
    col1.plotly_chart(cpu_fig, use_container_width=True)

    mem_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=mem,
        title={"text": "Memory Usage (%)"},
        gauge={"axis": {"range": [0, 100]}}
    ))
    mem_fig.update_layout(template="plotly_dark")
    col2.plotly_chart(mem_fig, use_container_width=True)

    st.divider()

    # ---------- RECENT LOGS ----------
    st.subheader("📋 Recent Logs")
    st.dataframe(
        log_pd.sort_values("timestamp", ascending=False).head(20),
        use_container_width=True
    )

    # ---------- ANOMALY LINE + EMAIL ----------
    if not anomaly_df.empty:
        line_fig = px.line(
            anomaly_df,
            x="timestamp",
            y="error_count",
            title="Detected Anomalies Over Time",
            markers=True,
            template="plotly_dark"
        )
        st.plotly_chart(line_fig, use_container_width=True)

        st.subheader("🚨 Detected Anomalies")
        st.dataframe(anomaly_df)

        send_mail("receiveremail@gmail.com", anomaly_df.to_dict("records"))
        st.success("📧 Alert Email Sent!")

    else:
        st.success("✅ System Stable. No anomalies detected.")

# ---------------- EMAIL ALERTS ----------------
elif menu == "Email Alerts":
    st.header("📧 Send Manual Alert")

    receiver = st.text_input("Receiver Email")

    if st.button("Send Test Email"):
        send_mail(receiver, [{
            "timestamp": "Manual Trigger",
            "error_count": "N/A",
            "z_score": "N/A"
        }])
        st.success("✅ Email sent successfully!")
