import streamlit as st
import pandas as pd
import os
import json
from datetime import date

APP_PATH = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(APP_PATH, "data")
os.makedirs(DATA_DIR, exist_ok=True)

def get_data_path(filename: str) -> str:
    return os.path.join(DATA_DIR, filename)

def load_categories():
    path = get_data_path("categories.json")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return ["Food", "Bills", "Transport", "Shopping", "Other"]

def save_categories(categories):
    with open(get_data_path("categories.json"), "w", encoding="utf-8") as f:
        json.dump(categories, f, indent=2)

data_file = get_data_path("expenses.csv")
if os.path.exists(data_file):
    df = pd.read_csv(data_file, parse_dates=["Date"])
else:
    df = pd.DataFrame(columns=["Date", "Amount", "Category", "Description"])

if "categories" not in st.session_state:
    st.session_state.categories = load_categories()

st.title("Personal Finance Tracker")
st.write("Track expenses, add custom categories, and review monthly summaries.")

with st.sidebar:
    st.header("Category settings")
    new_category = st.text_input("Add custom category")
    if st.button("Add category"):
        new_category = new_category.strip()
        if new_category == "":
            st.warning("Enter a category name first.")
        elif new_category in st.session_state.categories:
            st.info("This category already exists.")
        else:
            st.session_state.categories.append(new_category)
            save_categories(st.session_state.categories)
            st.success(f"Category added: {new_category}")

page = st.sidebar.selectbox("Navigate", ["Dashboard", "Expense History", "Add Expense"])

if page == "Dashboard":
    st.header("Dashboard")
    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"])
        current_month = df[df["Date"].dt.to_period("M") == pd.Timestamp.today().to_period("M")]
        total = df["Amount"].sum()
        this_month = current_month["Amount"].sum()
        largest = df["Amount"].max()

        col1, col2, col3 = st.columns(3)
        col1.metric("Total expenses", f"${total:,.2f}")
        col2.metric("This month", f"${this_month:,.2f}")
        col3.metric("Largest expense", f"${largest:,.2f}")

        st.subheader("Spending by category")
        st.bar_chart(df.groupby("Category")["Amount"].sum())

        st.subheader("This month spending trend")
        if not current_month.empty:
            trend = current_month.groupby(current_month["Date"].dt.day)["Amount"].sum()
            st.line_chart(trend)
        else:
            st.info("No expenses recorded for this month yet.")
    else:
        st.write("No expenses yet. Add one on the Add Expense page.")

elif page == "Expense History":
    st.header("Expense History")
    st.dataframe(df)

elif page == "Add Expense":
    st.header("Add Expense")
    with st.form("expense_form"):
        expense_date = st.date_input("Date", value=date.today())
        amount = st.number_input("Amount", min_value=0.01, step=0.01)
        category = st.selectbox("Category", st.session_state.categories)
        description = st.text_input("Description")
        submitted = st.form_submit_button("Save Expense")

        if submitted:
            if amount <= 0:
                st.error("Amount must be greater than 0.")
            else:
                new_row = {
                    "Date": expense_date,
                    "Amount": amount,
                    "Category": category,
                    "Description": description,
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                df.to_csv(data_file, index=False)
                st.success("Expense added!")

st.markdown("---")
st.caption("Tip: use the sidebar to add custom categories, then select them when adding a new expense.")