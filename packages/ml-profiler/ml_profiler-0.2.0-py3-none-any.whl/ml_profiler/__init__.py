from .data_summary import summarize_data
from .preprocessing_report import preprocess_data
from .model_selector import suggest_models
from .training_evaluator import evaluate_model
from .explainability import explain_model
from .report_generator import generate_report

from sklearn.utils.multiclass import type_of_target

def generate_ml_report(
    df,
    task="auto",
    target_column=None,
    output="report.html",
    format="html",
    verbose=False
):
    # Step 1: Target column detection
    if target_column is None:
        target_column = df.columns[-1]
    if target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' not found in DataFrame.")

    y = df[target_column]
    target_type = type_of_target(y)

    # Step 2: Auto task detection
    if task == "auto":
        if target_type in ["binary", "multiclass"]:
            task = "classification"
        elif target_type in ["continuous", "multiclass-multioutput"]:
            task = "regression"
        else:
            raise ValueError(f"Unable to infer task type from target: {target_type}")

    if verbose:
        print(f"[ML Profiler] Task: {task}")
        print(f"[ML Profiler] Target column: {target_column}")
        print(f"[ML Profiler] Target type: {target_type}")

    # Step 3: Data summary
    summary = summarize_data(df)

    # Step 4: Preprocessing
    preprocessed = preprocess_data(df)
    df_clean = preprocessed["processed_df"]
    preprocessing_steps = preprocessed["steps"]

    # Step 5: Model selection and evaluation
    models = suggest_models(task)
    results = []
    for model in models:
        result = evaluate_model(df_clean, model, target_column, task)
        results.append({
        "model": model.__class__.__name__,
        "metrics": result
        })

    # Step 6: Explainability
    X_for_explain = df_clean.drop(columns=[target_column])
    explanations = explain_model(model, df_clean, target_column)

    # Step 7: Report generation
    generate_report(
        summary=summary,
        results=results,
        explanations=explanations,
        output=output,
        format=format,
        preprocessing_steps=preprocessing_steps
    )

    if verbose:
        print(f"[ML Profiler] Report saved to: {output}")

    # Optional: Return all outputs for programmatic use
    return {
        "summary": summary,
        "preprocessing": preprocessing_steps,
        "model": model,
        "results": results,
        "explanations": explanations,
        "report_path": output
    }