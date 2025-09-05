import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def summarize_data(df):
    summary = df.describe(include='all').transpose()
    missing = df.isnull().sum()
    return {
        "summary": summary,
        "missing": missing
    }