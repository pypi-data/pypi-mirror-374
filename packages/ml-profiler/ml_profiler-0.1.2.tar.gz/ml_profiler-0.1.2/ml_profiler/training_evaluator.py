from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error

def evaluate_model(df, model):
    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    if hasattr(model, "predict_proba"):
        score = accuracy_score(y_test, y_pred)
    else:
        score = mean_squared_error(y_test, y_pred)
    return {"score": score}