from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

def suggest_models(task="classification"):
    if task == "classification":
        return [
            LogisticRegression(max_iter=1000),
            RandomForestClassifier()
        ]
    elif task == "regression":
        return [
            LinearRegression(),
            RandomForestRegressor()
        ]
    else:
        raise ValueError("Task must be 'classification' or 'regression'")