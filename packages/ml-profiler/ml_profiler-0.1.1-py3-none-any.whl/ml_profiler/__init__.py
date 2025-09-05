from .data_summary import summarize_data
from .preprocessing_report import preprocess_data
from .model_selector import suggest_model
from .training_evaluator import evaluate_model
from .explainability import explain_model
from .report_generator import generate_report

def generate_ml_report(df, task="classification", output="report.html"):
    summary = summarize_data(df)
    df_clean = preprocess_data(df)
    model = suggest_model(df_clean, task)
    results = evaluate_model(df_clean, model)
    explanations = explain_model(model, df_clean)
    generate_report(summary, results, explanations, output)