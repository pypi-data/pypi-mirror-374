import pandas as pd

def summarize_data(df):
    df = df.copy()

    # 📊 Basic summary statistics
    summary_stats = df.describe(include='all').transpose()

    # ❓ Missing values
    missing_values = df.isnull().sum()

    # 📐 Shape info
    shape_info = {
        "rows": df.shape[0],
        "columns": df.shape[1]
    }

    # 🔤 Column data types
    column_types = df.dtypes.to_frame(name="dtype")

    # 🔍 Unique value counts
    unique_counts = df.nunique()

    # 🚫 Constant columns (same value everywhere)
    constant_columns = unique_counts[unique_counts == 1].index.tolist()

    # ⚠️ High-cardinality columns (e.g., IDs, names)
    high_cardinality_columns = unique_counts[unique_counts > 50].index.tolist()

    return {
        "summary": summary_stats,
        "missing": missing_values,
        "shape": shape_info,
        "types": column_types,
        "unique_counts": unique_counts,
        "constant_columns": constant_columns,
        "high_cardinality_columns": high_cardinality_columns
    }