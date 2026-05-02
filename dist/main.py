import streamlit as st
import pandas as pd
import os
from datetime import datetime


APP_PATH = os.path.dirname(os.path.abspath(__file__))

def get_data_path(filename: str) -> str:
    '''returns the path to an asset file given its filename'''
    return os.path.join(APP_PATH, "data", filename)


# Load data
data_file = get_data_path("expenses.csv")
if os.path.exists(data_file):
    df = pd.read_csv(data_file)
else:
    df = pd.DataFrame(columns=["Data","Amount","Category","Description"])

st.title("Personal Finance Tracker")

# sidebar navigation

page = st.sidebar.selectbox("Navigate",["Dashboard", "History", "Add Expense"])


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

elif page == "Add Expenses":
    st.header("Add New expenses")
    with st.form("expense_form"):
        date = st.data_input("Date")
        amount = st.number_input("Amount", min_value=0.0)
        category = st.text_input("Category")
        description = st.text_input("Description")
        submitted = st.form_submit_button("Add Expense")
        if submitted:
            new_row = {"Date": date, "Amount": amount, "Category": category, "Description": description}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(data_file, index=False)
            st.success("Expense added!")

# Option to delete (simple, last entry or by index)
if not df.empty and st.sidebar.button("Delete Last Expense"):
    df = df[:-1]
    df.to_csv(data_file, index=False)
    st.sidebar.success("Last expense deleted!")