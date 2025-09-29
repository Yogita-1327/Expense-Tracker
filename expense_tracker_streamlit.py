import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import date

# ----------------------------
# App Config
# ----------------------------
st.set_page_config(page_title="Expense Tracker", page_icon="💰", layout="wide")

# ----------------------------
# CSV File Setup
# ----------------------------
CSV_FILE = "expenses.csv"

if not os.path.exists(CSV_FILE):
    df_init = pd.DataFrame(columns=["Date", "Amount", "Category", "Notes"])
    df_init.to_csv(CSV_FILE, index=False)

# ----------------------------
# Load Data
# ----------------------------
def load_data():
    return pd.read_csv(CSV_FILE)

# ----------------------------
# Save Data
# ----------------------------
def save_data(new_data):
    df = load_data()
    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

# ----------------------------
# Sidebar - Add Expense
# ----------------------------
with st.sidebar.expander("➕ Add Expense", expanded=True):
    expense_date = st.date_input("Date", value=date.today())
    amount = st.number_input("Amount (₹)", min_value=0.0, format="%.2f")

    category = st.selectbox(
        "Category",
        ["Food 🍔", "Travel 🚖", "Shopping 🛍️", "Bills 💡", "Entertainment 🎬", "Health 🏥", "Others ✨"]
    )
    notes = st.text_input("Notes (optional)")

    if st.button("Add expense"):
        try:
            save_data({
                "Date": expense_date.strftime("%Y-%m-%d"),
                "Amount": amount,
                "Category": category,
                "Notes": notes
            })
            st.success("✅ Expense added successfully!")
            st.rerun()   # <-- FIXED (no experimental_rerun)
        except Exception as e:
            st.error(f"Error saving expense: {e}")

# ----------------------------
# Main Dashboard
# ----------------------------
st.title("💰 Personal Expense Tracker")

df = load_data()

if df.empty:
    st.info("No expenses recorded yet. Add some from the sidebar ➕")
else:
    # Convert Date column
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # Show Data
    with st.expander("📊 View Expense Data"):
        st.dataframe(df, use_container_width=True)

    # ----------------------------
    # Charts
    # ----------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📅 Expenses Over Time")
        fig_bar = px.bar(
            df,
            x="Date",
            y="Amount",
            color="Category",
            title="Expenses by Date",
            template="plotly_dark"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        st.subheader("📌 Category Breakdown")
        category_summary = df.groupby("Category")["Amount"].sum().reset_index()
        fig_pie = px.pie(
            category_summary,
            values="Amount",
            names="Category",
            title="Expenses by Category",
            hole=0.4,
            template="plotly_dark"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # ----------------------------
    # Summary Stats
    # ----------------------------
    st.subheader("📈 Summary")
    total_spent = df["Amount"].sum()
    top_category = df.groupby("Category")["Amount"].sum().idxmax()
    top_category_amount = df.groupby("Category")["Amount"].sum().max()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Spent", f"₹{total_spent:,.2f}")
    col2.metric("Top Category", top_category)
    col3.metric("Max Category Spend", f"₹{top_category_amount:,.2f}")
