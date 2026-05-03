import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from datetime import date


APP_PATH = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(APP_PATH, "data")
os.makedirs(DATA_DIR, exist_ok=True)

def get_data_path(filename: str) -> str:
    """ returns the paths to an assest files givpen the filename """
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


# load data
data_files = get_data_path("expenses.csv")
if os.path.exists(data_files):
    df = pd.read_csv(data_files)
else:
    df = pd.DataFrame(columns = ["Data","Amount","Category","Description"])

st.title("Personal Finance Tracker")


# Sidebar navigation

page = st.sidebar.selectbox("Navigate", ["Dashboard", "History", "Add Expense"])

if page == "Dashboard":
    st.header("Dashboard")
    if not df.empty:
        st.write("Total Expenses:", df["Amount"].sum())
        st.bar_chart(df.groupby("Category")["Amount"].sum())
    else:
        st.write("No expenses yet.")

elif page == "History":
    st.header("Expense History")
    st.dataframe(df)
    if not df.empty:
        if st.button("Delete Last Expense"):
            df = df.drop(df.index[-1])
            df.to_csv(data_files, index=False)
            st.success("Last expense deleted!")
            st.rerun()

elif page == "Add Expense":
    st.header("Add New Expense")
    with st.form("expense_form"):
        date = st.date_input("Date")
        amount = st.number_input("Amount", min_value=0.0)
        category = st.text_input("Category")
        description = st.text_input("Description")
        submitted = st.form_submit_button("Add Expense")
        if submitted:
            new_row = {"Date": date, "Amount": amount, "Category": category, "Description": description}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(data_files, index=False)
            st.success("Expense added!")




























