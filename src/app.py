def generate_ai_insight(filtered_df, system_name):
    trend = filtered_df["risk_score"].diff().mean()
    latest_score = filtered_df.iloc[-1]["risk_score"]

    explanation = f"System '{system_name}' currently has a risk score of {latest_score}. "

    if trend > 0:
        explanation += "Risk is increasing over time, indicating potential instability or exposure."
    elif trend < 0:
        explanation += "Risk is decreasing, suggesting improvements in governance controls."
    else:
        explanation += "Risk trend is stable with no major fluctuations."

    if latest_score >= 2.6:
        explanation += " Immediate mitigation actions are recommended."
    elif latest_score >= 2.0:
        explanation += " Continuous monitoring is advised."
    else:
        explanation += " System is operating within acceptable risk levels."

    return explanation

import streamlit as st
import pandas as pd

# Title
st.title("AI Governance Control Tower")

# Load data
df = pd.read_csv("../data/risk_data.csv")

# Fix columns
df[['system', 'date', 'risk_score']] = df['system,date,risk_score'].str.split(',', expand=True)
df['risk_score'] = df['risk_score'].astype(float)
df['date'] = pd.to_datetime(df['date'])
df = df.drop(columns=['system,date,risk_score'])

# -----------------------------
# 🔹 KPI SECTION (NEW)
# -----------------------------
st.subheader("📊 Executive Summary")

total_systems = df["system"].nunique()
latest_scores = df.sort_values("date").groupby("system").tail(1)

high_risk = len(latest_scores[latest_scores["risk_score"] >= 2.6])
medium_risk = len(latest_scores[(latest_scores["risk_score"] >= 2.0) & (latest_scores["risk_score"] < 2.6)])
low_risk = len(latest_scores[latest_scores["risk_score"] < 2.0])

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Systems", total_systems)
col2.metric("High Risk", high_risk)
col3.metric("Medium Risk", medium_risk)
col4.metric("Low Risk", low_risk)

# -----------------------------
# 🔹 SYSTEM COMPARISON (NEW)
# -----------------------------
st.subheader("📈 System Risk Comparison")

comparison_df = latest_scores.set_index("system")["risk_score"]
st.bar_chart(comparison_df)

# -----------------------------
# 🔹 SYSTEM SELECTION
# -----------------------------
systems = df["system"].unique()
selected_system = st.selectbox("Select AI System", systems)

filtered_df = df[df["system"] == selected_system]

# -----------------------------
# 🔹 TREND CHART
# -----------------------------
st.subheader(f"📉 Risk Trend for {selected_system}")
st.line_chart(filtered_df.set_index("date")["risk_score"])

st.subheader("📌 Risk Trend Insight")

trend = filtered_df["risk_score"].diff().mean()

if trend > 0:
    st.warning("Risk is trending upward 📈")
elif trend < 0:
    st.success("Risk is trending downward 📉")
else:
    st.info("Risk is stable ➡️")

# -----------------------------
# 🔹 ALERT SECTION
# -----------------------------
latest_score = filtered_df.iloc[-1]["risk_score"]

st.subheader("🚨 Current Risk Status")

if latest_score >= 2.6:
    st.error("High Risk - Immediate Action Required")
elif latest_score >= 2.0:
    st.warning("Medium Risk - Monitor Closely")
else:
    st.success("Low Risk - Safe")

st.subheader("🧠 AI Insight")

insight = generate_ai_insight(filtered_df, selected_system)
st.info(insight)

st.subheader("📥 Download Report")

report_df = filtered_df.copy()
report_df["system"] = selected_system

csv = report_df.to_csv(index=False).encode('utf-8')

st.download_button(
    label="Download Risk Report",
    data=csv,
    file_name=f"{selected_system}_risk_report.csv",
    mime='text/csv',
)