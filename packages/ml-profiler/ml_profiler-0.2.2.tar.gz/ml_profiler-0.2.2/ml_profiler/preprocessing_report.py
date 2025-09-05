from sklearn.preprocessing import LabelEncoder, StandardScaler
import pandas as pd

def preprocess_data(df, encode=True, scale=True):
    df = df.copy()
    preprocessing_steps = []

    # Handle missing values (optional: fill or drop)
    if df.isnull().sum().sum() > 0:
        df = df.fillna("missing")  # or use df.dropna()
        preprocessing_steps.append("Filled missing values with 'missing'")

    # Encode categorical columns
    if encode:
        for col in df.select_dtypes(include='object'):
            df[col] = LabelEncoder().fit_transform(df[col].astype(str))
            preprocessing_steps.append(f"Encoded column '{col}' using LabelEncoder")

    # Scale numerical columns
    if scale:
        for col in df.select_dtypes(include='number'):
            df[col] = StandardScaler().fit_transform(df[[col]])
            preprocessing_steps.append(f"Scaled column '{col}' using StandardScaler")

    return {
        "processed_df": df,
        "steps": preprocessing_steps
    }