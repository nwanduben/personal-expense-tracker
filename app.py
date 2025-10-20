import streamlit as st
import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import seaborn as sns

# 🌍 Load environment variables
load_dotenv()

# ---------------- DATABASE CONNECTION ----------------
@st.cache_resource
def connect_db():
    return psycopg2.connect(
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"),
        dbname=os.getenv("PG_DB"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        sslmode=os.getenv("PG_SSLMODE", "require")
    )

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    conn = connect_db()
    query = "SELECT * FROM bank_transactions ORDER BY trans_date;"
    df = pd.read_sql_query(query, conn)
    conn.close()

    df["trans_date"] = pd.to_datetime(df["trans_date"], errors="coerce")
    df["month_year"] = df["trans_date"].dt.to_period("M").astype(str)
    return df

# ---------------- CATEGORIZATION LOGIC ----------------
def categorize(desc):
    d = str(desc).lower()
    if "airtime" in d or "data" in d:
        return "Airtime & Data"
    if "cold stone" in d or "food" in d or "restaurant" in d:
        return "Food & Lifestyle"
    if "transfer" in d:
        return "Transfers"
    if "auto-save" in d or "owallet" in d or "piggy" in d or "save" in d:
        return "Savings"
    if "bet" in d or "sporty" in d:
        return "Gaming & Betting"
    if "atm" in d or "pos" in d or "withdrawal" in d:
        return "Cash Withdrawal"
    return "Other"

# ---------------- STREAMLIT APP LAYOUT ----------------
st.set_page_config(page_title="💳 Personal Expense Tracker", layout="wide")
st.title("💰 Personal Expense Tracker Dashboard")

# Load data
df = load_data()
df["category"] = df["description"].apply(categorize)

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.header("🔍 Filters")

months = ["All"] + sorted(df["month_year"].unique().tolist(), reverse=True)
selected_month = st.sidebar.selectbox("Select Month-Year", months)

# Apply month filter
if selected_month == "All":
    filtered = df.copy()
else:
    filtered = df[df["month_year"] == selected_month]

# ---------------- KPI METRICS ----------------
total_spent = filtered["debit"].sum()
total_income = filtered["credit"].sum()
net_flow = total_income - total_spent

# ✅ Correct Savings Calculation
savings_out = df[(df["category"] == "Savings") & (df["debit"] > 0)]["debit"].sum()
savings_in = df[(df["category"] == "Savings") & (df["credit"] > 0)]["credit"].sum()
total_saved = savings_out - savings_in

col1, col2, col3, col4 = st.columns(4)
col1.metric("💸 Total Spent", f"₦{total_spent:,.0f}")
col2.metric("💰 Total Income", f"₦{total_income:,.0f}")
col3.metric("📊 Net Flow", f"₦{net_flow:,.0f}", delta_color="inverse" if net_flow < 0 else "normal")
col4.metric("🏦 Total Saved (All Time)", f"₦{total_saved:,.0f}")

st.markdown("---")

# ---------------- CATEGORY SPENDING ----------------
st.subheader("📂 Spending by Category")

category_summary = (
    filtered.groupby("category")["debit"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

fig, ax = plt.subplots(figsize=(9,5))
sns.barplot(data=category_summary, x="debit", y="category", palette="mako", ax=ax)
ax.set_title("💳 Total Spending by Category")
ax.set_xlabel("Total Debit (₦)")
ax.set_ylabel("Transaction Category")
st.pyplot(fig)

# ---------------- CHANNEL BREAKDOWN ----------------
st.subheader("🏦 Spending by Channel")

channel_summary = (
    filtered.groupby("channel")["debit"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)
st.bar_chart(channel_summary.set_index("channel"))

# ---------------- MONTHLY TREND ----------------
st.subheader("📆 Monthly Transaction Trend")

trend = (
    df.groupby("month_year")[["debit", "credit"]]
    .sum()
    .reset_index()
    .sort_values("month_year")
)
st.line_chart(trend.set_index("month_year"))

# ---------------- SAVINGS DETAIL ----------------
st.subheader("💾 Savings Activity Overview")

savings_df = df[df["category"] == "Savings"]
if not savings_df.empty:
    st.dataframe(
        savings_df[["trans_date", "description", "debit", "credit", "channel", "counterparty"]]
        .sort_values("trans_date", ascending=False),
        use_container_width=True
    )
    st.info(f"💡 You’ve moved ₦{savings_out:,.0f} into savings and withdrawn ₦{savings_in:,.0f} so far.")
else:
    st.warning("No savings transactions found yet!")

# ---------------- TRANSACTION TABLE ----------------
st.subheader("📋 Transaction Details")

st.dataframe(
    filtered[
        ["trans_date", "description", "debit", "credit", "category", "channel", "counterparty"]
    ].sort_values("trans_date", ascending=False),
    use_container_width=True
)

# ---------------- DOWNLOAD OPTION ----------------
csv = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    "📥 Download Filtered Transactions",
    data=csv,
    file_name=f"transactions_{selected_month}.csv",
    mime="text/csv",
)

st.success("✅ Dashboard loaded successfully!")
