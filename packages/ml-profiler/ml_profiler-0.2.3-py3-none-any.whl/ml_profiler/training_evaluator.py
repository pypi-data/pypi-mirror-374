from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error, confusion_matrix
from sklearn.utils.multiclass import type_of_target

def evaluate_model(df, model, target_column, task):
    # Step 1: Validate target column
    if target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' not found in DataFrame.")

    y = df[target_column]
    X = df.drop(columns=[target_column])

    # Step 2: Validate target type
    target_type = type_of_target(y)
    if task == "classification" and target_type not in ["binary", "multiclass"]:
        raise ValueError(f"Target type '{target_type}' is not valid for classification.")
    if task == "regression" and target_type not in ["continuous"]:
        raise ValueError(f"Target type '{target_type}' is not valid for regression.")

    # Step 3: Train/test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    # Step 4: Fit model
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    # Step 5: Evaluate
    if task == "classification":
        score = accuracy_score(y_test, y_pred)
        cm = confusion_matrix(y_test, y_pred)
        return {
            "score": score,
            "confusion_matrix": cm
        }
    else:
        score = mean_squared_error(y_test, y_pred)
        return {
            "score": score,
            "residuals": y_test - y_pred
        }