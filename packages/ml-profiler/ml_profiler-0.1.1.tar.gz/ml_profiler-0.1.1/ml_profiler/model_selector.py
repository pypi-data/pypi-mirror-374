from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

def suggest_model(df, task="classification"):
    if task == "classification":
        return RandomForestClassifier()
    elif task == "regression":
        return RandomForestRegressor()
    else:
        raise ValueError("Task must be 'classification' or 'regression'")