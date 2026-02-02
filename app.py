# ==============================
# Dialer Connectivity Dashboard
# ==============================

import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="DM Flow Dashboard",
    layout="wide"
)

# ------------------------------
# Simple Password Protection
# ------------------------------
PASSWORD = "DM@123"

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Login")
    pwd = st.text_input("Enter password", type="password")
    if pwd == PASSWORD:
        st.session_state.auth = True
        st.rerun()
    else:
        st.stop()

# ------------------------------
# Header
# ------------------------------
st.title("📊 DM Flow – Connectivity Dashboard")
st.caption("Upload dialer Excel and dashboard updates automatically")

# ------------------------------
# File Upload
# ------------------------------
uploaded_file = st.file_uploader(
    "Upload Dialer Excel File",
    type=["xlsx"]
)

if not uploaded_file:
    st.info("Please upload a dialer Excel file to continue.")
    st.stop()

# ------------------------------
# Load Data
# ------------------------------
df = pd.read_excel(uploaded_file)

# ------------------------------
# Required Columns Check
# ------------------------------
required_cols = [
    "Leadid", "Attempt", "Campaign",
    "1-Con/Non Con", "2-Con/Non Con",
    "Status"
]

missing = [c for c in required_cols if c not in df.columns]
if missing:
    st.error(f"Missing columns in Excel: {missing}")
    st.stop()

# ------------------------------
# Data Cleaning
# ------------------------------
df["Attempt"] = df["Attempt"].fillna(0).astype(int)
df["Campaign"] = df["Campaign"].astype(str).str.strip()

# Attempt Bucket
df["Attempt Bucket"] = df["Attempt"].apply(
    lambda x: ">=3" if x >= 3 else str(x)
)

# ------------------------------
# Filters
# ------------------------------
st.sidebar.header("Filters")

campaign = st.sidebar.selectbox(
    "Campaign",
    sorted(df["Campaign"].dropna().unique())
)

df = df[df["Campaign"] == campaign]

# ------------------------------
# 1st Attempt Metrics
# ------------------------------
first_attempt = df[df["Attempt"] == 1]

total_1 = first_attempt["Leadid"].nunique()
connect_1 = first_attempt[
    first_attempt["1-Con/Non Con"] == "Connect"
]["Leadid"].nunique()

non_connect_1 = total_1 - connect_1
conn_pct_1 = round((connect_1 / total_1) * 100, 2) if total_1 else 0

# ------------------------------
# 2nd Attempt on Non-Connect
# ------------------------------
second_attempt = df[
    (df["Attempt"] == 2) &
    (df["1-Con/Non Con"] == "Non Connect")
]

total_2 = second_attempt["Leadid"].nunique()
connect_2 = second_attempt[
    second_attempt["2-Con/Non Con"] == "Connect"
]["Leadid"].nunique()

conn_pct_2 = round((connect_2 / total_2) * 100, 2) if total_2 else 0

# ------------------------------
# Final Non-Connect Bucket
# ------------------------------
final_nc = df[df["Status"].str.lower() == "pending"]
bucket_counts = (
    final_nc.groupby("Attempt Bucket")["Leadid"]
    .nunique()
    .reset_index()
    .sort_values("Attempt Bucket")
)

# ------------------------------
# Dashboard Layout
# ------------------------------
st.subheader("1️⃣ 1st Attempt Status")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total", total_1)
c2.metric("Connect", connect_1)
c3.metric("Non-Connect", non_connect_1)
c4.metric("Connectivity", f"{conn_pct_1}%")

st.divider()

st.subheader("2️⃣ 2nd Attempt on Non-Connect")

c5, c6, c7 = st.columns(3)
c5.metric("Total NC Base", total_2)
c6.metric("Connect", connect_2)
c7.metric("Connectivity", f"{conn_pct_2}%")

st.divider()

st.subheader("3️⃣ Attempt Bucket – Final Non Connect")

st.bar_chart(
    data=bucket_counts,
    x="Attempt Bucket",
    y="Leadid"
)

# ------------------------------
# Raw Data (Optional)
# ------------------------------
with st.expander("View Filtered Raw Data"):
    st.dataframe(df)
