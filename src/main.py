import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from datetime import date


APP_PATH = os.patj.dirname(os.path.abspath(__file__))

def get_data_path(filename: str) -> star:
    """ returns the paths to an assest files givpen the filename """
    return os.path.join(APP_PATH, "data", filename)


# load data
data_files = get_data_path("expenses.csv")
if os.path.exists(data_file):
    df = pd.read_csv(data_file)
else:
    df = pd.DataFrame(colums = ["Data","Amount","Category","Description"])

st.title("Personal Finance Tracker")
































