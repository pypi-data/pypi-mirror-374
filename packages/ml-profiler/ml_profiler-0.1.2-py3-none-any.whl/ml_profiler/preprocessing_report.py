from sklearn.preprocessing import LabelEncoder, StandardScaler

def preprocess_data(df):
    df = df.copy()
    for col in df.select_dtypes(include='object'):
        df[col] = LabelEncoder().fit_transform(df[col].astype(str))
    for col in df.select_dtypes(include='number'):
        df[col] = StandardScaler().fit_transform(df[[col]])
    return df