import shap

def explain_model(model, df):
    explainer = shap.Explainer(model, df.iloc[:, :-1])
    shap_values = explainer(df.iloc[:, :-1])
    return shap_values