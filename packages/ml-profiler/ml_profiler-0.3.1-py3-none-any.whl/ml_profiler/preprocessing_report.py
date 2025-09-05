from sklearn.preprocessing import LabelEncoder, StandardScaler
import pandas as pd

def preprocess_data(df, target_column=None, encode=True, scale=True):
    df = df.copy()
    preprocessing_steps = []

    # Handle missing values
    if df.isnull().sum().sum() > 0:
        df = df.fillna("missing")
        preprocessing_steps.append("Filled missing values with 'missing'")

    # Encode categorical columns (excluding target)
    if encode:
        for col in df.select_dtypes(include='object'):
            if col != target_column:
                df[col] = LabelEncoder().fit_transform(df[col].astype(str))
                preprocessing_steps.append(f"Encoded column '{col}' using LabelEncoder")

    # Scale numeric columns (excluding target)
    if scale:
        for col in df.select_dtypes(include='number'):
            if col != target_column:
                df[col] = StandardScaler().fit_transform(df[[col]])
                preprocessing_steps.append(f"Scaled column '{col}' using StandardScaler")

    return {
        "processed_df": df,
        "steps": preprocessing_steps
    }