import streamlit as st
import pandas as pd
import os
import json
from datetime import date, timedelta

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

def load_budgets():
    path = get_data_path("budgets.json")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_budgets(budgets):
    with open(get_data_path("budgets.json"), "w", encoding="utf-8") as f:
        json.dump(budgets, f, indent=2)

# Load data
expenses_file = get_data_path("expenses.csv")
income_file = get_data_path("income.csv")

if os.path.exists(expenses_file):
    df_expenses = pd.read_csv(expenses_file, parse_dates=["Date"])
else:
    df_expenses = pd.DataFrame(columns=["Date", "Amount", "Category", "Description"])

if os.path.exists(income_file):
    df_income = pd.read_csv(income_file, parse_dates=["Date"])
else:
    df_income = pd.DataFrame(columns=["Date", "Amount", "Category", "Description"])

if "categories" not in st.session_state:
    st.session_state.categories = load_categories()

if "budgets" not in st.session_state:
    st.session_state.budgets = load_budgets()

st.set_page_config(page_title="Personal Finance Tracker", layout="wide")
st.title("💰 Personal Finance Tracker")
st.write("Track expenses & income, manage budgets, and review analytics.")

# Sidebar: Category & Budget Settings
with st.sidebar:
    st.header("⚙️ Settings")
    
    tab_cat, tab_bud = st.tabs(["Categories", "Budgets"])
    
    with tab_cat:
        st.subheader("Manage Categories")
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
    
    with tab_bud:
        st.subheader("Set Budget Limits")
        for cat in st.session_state.categories:
            current_budget = st.session_state.budgets.get(cat, 0)
            budget = st.number_input(f"Budget for {cat}", min_value=0.0, value=float(current_budget), step=10.0, key=f"budget_{cat}")
            st.session_state.budgets[cat] = budget
        if st.button("Save budgets"):
            save_budgets(st.session_state.budgets)
            st.success("Budgets saved!")

# Main navigation
page = st.sidebar.selectbox("Navigate", ["Dashboard", "Expenses", "Income", "Edit/Delete", "Analytics"])

if page == "Dashboard":
    st.header("📊 Dashboard")
    
    if not df_expenses.empty or not df_income.empty:
        df_expenses["Date"] = pd.to_datetime(df_expenses["Date"])
        df_income["Date"] = pd.to_datetime(df_income["Date"])
        
        current_month = df_expenses[df_expenses["Date"].dt.to_period("M") == pd.Timestamp.today().to_period("M")]
        current_month_income = df_income[df_income["Date"].dt.to_period("M") == pd.Timestamp.today().to_period("M")]
        
        total_expenses = df_expenses["Amount"].sum() if not df_expenses.empty else 0
        total_income = df_income["Amount"].sum() if not df_income.empty else 0
        this_month_expenses = current_month["Amount"].sum() if not current_month.empty else 0
        this_month_income = current_month_income["Amount"].sum() if not current_month_income.empty else 0
        net = total_income - total_expenses
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Income", f"${total_income:,.2f}", delta=f"${this_month_income:,.2f}")
        col2.metric("Total Expenses", f"${total_expenses:,.2f}", delta=f"${this_month_expenses:,.2f}")
        col3.metric("Net (Income - Expenses)", f"${net:,.2f}")
        col4.metric("This Month Balance", f"${this_month_income - this_month_expenses:,.2f}")
        
        st.subheader("Spending by Category")
        if not df_expenses.empty:
            category_spending = df_expenses.groupby("Category")["Amount"].sum()
            st.bar_chart(category_spending)
            
            # Budget alerts
            st.subheader("📢 Budget Alerts")
            for cat, budget in st.session_state.budgets.items():
                if budget > 0:
                    spent = category_spending.get(cat, 0)
                    percentage = (spent / budget) * 100
                    if spent > budget:
                        st.error(f"❌ {cat}: ${spent:,.2f} / ${budget:,.2f} ({percentage:.0f}%) - OVER BUDGET!")
                    elif spent > budget * 0.8:
                        st.warning(f"⚠️ {cat}: ${spent:,.2f} / ${budget:,.2f} ({percentage:.0f}%) - Approaching limit")
                    else:
                        st.info(f"✅ {cat}: ${spent:,.2f} / ${budget:,.2f} ({percentage:.0f}%)")
    else:
        st.write("No data yet. Start by adding expenses and income.")

elif page == "Expenses":
    st.header("💸 Expenses")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Add New Expense")
        with st.form("expense_form"):
            exp_date = st.date_input("Date", value=date.today())
            exp_amount = st.number_input("Amount", min_value=0.01, step=0.01)
            exp_category = st.selectbox("Category", st.session_state.categories)
            exp_description = st.text_input("Description")
            submitted = st.form_submit_button("Save Expense")
            
            if submitted:
                new_row = {
                    "Date": exp_date,
                    "Amount": exp_amount,
                    "Category": exp_category,
                    "Description": exp_description,
                }
                df_expenses = pd.concat([df_expenses, pd.DataFrame([new_row])], ignore_index=True)
                df_expenses.to_csv(expenses_file, index=False)
                st.success("Expense added!")
    
    with col2:
        st.subheader("Recent Expenses")
        if not df_expenses.empty:
            recent = df_expenses.tail(5).sort_values("Date", ascending=False)
            st.dataframe(recent, hide_index=True)
        else:
            st.info("No expenses yet.")

elif page == "Income":
    st.header("💵 Income")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Add New Income")
        with st.form("income_form"):
            inc_date = st.date_input("Date", value=date.today(), key="income_date")
            inc_amount = st.number_input("Amount", min_value=0.01, step=0.01, key="income_amount")
            inc_category = st.selectbox("Source", ["Salary", "Freelance", "Investment", "Bonus", "Other"], key="income_cat")
            inc_description = st.text_input("Description", key="income_desc")
            submitted_inc = st.form_submit_button("Save Income")
            
            if submitted_inc:
                new_inc = {
                    "Date": inc_date,
                    "Amount": inc_amount,
                    "Category": inc_category,
                    "Description": inc_description,
                }
                df_income = pd.concat([df_income, pd.DataFrame([new_inc])], ignore_index=True)
                df_income.to_csv(income_file, index=False)
                st.success("Income added!")
    
    with col2:
        st.subheader("Recent Income")
        if not df_income.empty:
            recent_inc = df_income.tail(5).sort_values("Date", ascending=False)
            st.dataframe(recent_inc, hide_index=True)
        else:
            st.info("No income yet.")

elif page == "Edit/Delete":
    st.header("✏️ Edit or Delete Entries")
    
    tab_exp_edit, tab_inc_edit = st.tabs(["Expenses", "Income"])
    
    with tab_exp_edit:
        st.subheader("Manage Expenses")
        if not df_expenses.empty:
            df_expenses["Date"] = pd.to_datetime(df_expenses["Date"])
            
            # Delete expenses
            st.write("Delete an expense:")
            selected_idx = st.selectbox("Select expense to delete", 
                                       range(len(df_expenses)),
                                       format_func=lambda i: f"{df_expenses.iloc[i]['Date'].date()} - {df_expenses.iloc[i]['Category']}: ${df_expenses.iloc[i]['Amount']}")
            
            if st.button("Delete selected expense"):
                df_expenses = df_expenses.drop(index=selected_idx).reset_index(drop=True)
                df_expenses.to_csv(expenses_file, index=False)
                st.success("Expense deleted!")
                st.rerun()
            
            # Edit expenses
            st.write("Edit an expense:")
            edit_idx = st.selectbox("Select expense to edit", 
                                   range(len(df_expenses)),
                                   format_func=lambda i: f"{df_expenses.iloc[i]['Date'].date()} - {df_expenses.iloc[i]['Category']}: ${df_expenses.iloc[i]['Amount']}",
                                   key="edit_exp_idx")
            
            with st.form("edit_expense_form"):
                row = df_expenses.iloc[edit_idx]
                edit_date = st.date_input("Date", value=row["Date"].date())
                edit_amount = st.number_input("Amount", value=float(row["Amount"]), min_value=0.01)
                edit_category = st.selectbox("Category", st.session_state.categories, 
                                           index=st.session_state.categories.index(row["Category"]))
                edit_description = st.text_input("Description", value=row["Description"])
                edit_submitted = st.form_submit_button("Update Expense")
                
                if edit_submitted:
                    df_expenses.at[edit_idx, "Date"] = edit_date
                    df_expenses.at[edit_idx, "Amount"] = edit_amount
                    df_expenses.at[edit_idx, "Category"] = edit_category
                    df_expenses.at[edit_idx, "Description"] = edit_description
                    df_expenses.to_csv(expenses_file, index=False)
                    st.success("Expense updated!")
                    st.rerun()
            
            st.dataframe(df_expenses, hide_index=True)
        else:
            st.info("No expenses to manage.")
    
    with tab_inc_edit:
        st.subheader("Manage Income")
        if not df_income.empty:
            df_income["Date"] = pd.to_datetime(df_income["Date"])
            
            # Delete income
            st.write("Delete an income entry:")
            selected_inc_idx = st.selectbox("Select income to delete", 
                                           range(len(df_income)),
                                           format_func=lambda i: f"{df_income.iloc[i]['Date'].date()} - {df_income.iloc[i]['Category']}: ${df_income.iloc[i]['Amount']}")
            
            if st.button("Delete selected income"):
                df_income = df_income.drop(index=selected_inc_idx).reset_index(drop=True)
                df_income.to_csv(income_file, index=False)
                st.success("Income deleted!")
                st.rerun()
            
            # Edit income
            st.write("Edit an income entry:")
            edit_inc_idx = st.selectbox("Select income to edit", 
                                       range(len(df_income)),
                                       format_func=lambda i: f"{df_income.iloc[i]['Date'].date()} - {df_income.iloc[i]['Category']}: ${df_income.iloc[i]['Amount']}",
                                       key="edit_inc_idx")
            
            with st.form("edit_income_form"):
                row_inc = df_income.iloc[edit_inc_idx]
                edit_inc_date = st.date_input("Date", value=row_inc["Date"].date(), key="edit_inc_date")
                edit_inc_amount = st.number_input("Amount", value=float(row_inc["Amount"]), min_value=0.01, key="edit_inc_amt")
                edit_inc_category = st.selectbox("Source", ["Salary", "Freelance", "Investment", "Bonus", "Other"], 
                                                key="edit_inc_cat")
                edit_inc_description = st.text_input("Description", value=row_inc["Description"], key="edit_inc_desc")
                edit_inc_submitted = st.form_submit_button("Update Income")
                
                if edit_inc_submitted:
                    df_income.at[edit_inc_idx, "Date"] = edit_inc_date
                    df_income.at[edit_inc_idx, "Amount"] = edit_inc_amount
                    df_income.at[edit_inc_idx, "Category"] = edit_inc_category
                    df_income.at[edit_inc_idx, "Description"] = edit_inc_description
                    df_income.to_csv(income_file, index=False)
                    st.success("Income updated!")
                    st.rerun()
            
            st.dataframe(df_income, hide_index=True)
        else:
            st.info("No income to manage.")

elif page == "Analytics":
    st.header("📈 Analytics")
    
    if not df_expenses.empty or not df_income.empty:
        df_expenses["Date"] = pd.to_datetime(df_expenses["Date"])
        df_income["Date"] = pd.to_datetime(df_income["Date"])
        
        # Date range filter
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start date", value=date.today() - timedelta(days=30))
        with col2:
            end_date = st.date_input("End date", value=date.today())
        
        # Filter data
        df_exp_filtered = df_expenses[(df_expenses["Date"].dt.date >= start_date) & 
                                     (df_expenses["Date"].dt.date <= end_date)]
        df_inc_filtered = df_income[(df_income["Date"].dt.date >= start_date) & 
                                   (df_income["Date"].dt.date <= end_date)]
        
        st.subheader(f"Data from {start_date} to {end_date}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Income (Period)", f"${df_inc_filtered['Amount'].sum():,.2f}")
        with col2:
            st.metric("Total Expenses (Period)", f"${df_exp_filtered['Amount'].sum():,.2f}")
        with col3:
            st.metric("Net (Period)", f"${df_inc_filtered['Amount'].sum() - df_exp_filtered['Amount'].sum():,.2f}")
        
        if not df_exp_filtered.empty:
            st.subheader("Expense Distribution")
            st.bar_chart(df_exp_filtered.groupby("Category")["Amount"].sum())
            
            st.subheader("Daily Trend")
            daily = df_exp_filtered.groupby(df_exp_filtered["Date"].dt.date)["Amount"].sum()
            st.line_chart(daily)
        
        if not df_inc_filtered.empty:
            st.subheader("Income Sources")
            st.pie_chart(df_inc_filtered.groupby("Category")["Amount"].sum())
        
        st.subheader("Detailed View")
        if not df_exp_filtered.empty:
            st.write("**Expenses:**")
            st.dataframe(df_exp_filtered.sort_values("Date", ascending=False), hide_index=True)
        
        if not df_inc_filtered.empty:
            st.write("**Income:**")
            st.dataframe(df_inc_filtered.sort_values("Date", ascending=False), hide_index=True)
    else:
        st.write("No data yet.")

st.markdown("---")
st.caption("📝 Tip: Use Settings to add categories and set budgets. All data is saved locally in the 'data' folder.")