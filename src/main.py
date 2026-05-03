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

