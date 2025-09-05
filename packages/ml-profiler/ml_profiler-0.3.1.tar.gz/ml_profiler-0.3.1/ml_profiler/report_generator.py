import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

def generate_report(summary, results, explanations, output, format="html", preprocessing_steps=None):
    if format != "html":
        raise NotImplementedError("Only HTML format is supported currently.")

    html = "<html><head><title>ML Profiler Report</title></head><body>"
    html += "<h1 style='text-align:center;'>ML Profiler Report</h1>"

    # 🔧 Preprocessing Steps
    if preprocessing_steps:
        html += "<h2>Preprocessing Steps</h2><ul>"
        for step in preprocessing_steps:
            html += f"<li>{step}</li>"
        html += "</ul>"

    # 📊 Data Summary
    html += "<hr><h2>Data Summary</h2>"
    html += summary["summary"].to_html()
    html += "<h2>Missing Values</h2>"
    html += summary["missing"].to_frame().to_html()

    # 📈 Model Scores
    html += "<hr><h2>Model Scores</h2>"
    for result in results:
        model_name = result["model"]
        metrics = result["metrics"]
        score = metrics.get("score", "N/A")
        html += f"<h3>{model_name}</h3>"
        html += f"<p><strong>Score:</strong> {score}</p>"

        # 📉 Confusion Matrix or Residuals
        if "confusion_matrix" in metrics:
            html += "<h4>Confusion Matrix</h4>"
            cm_df = pd.DataFrame(metrics["confusion_matrix"])
            html += cm_df.to_html()
            html += _plot_to_html(_plot_confusion_matrix(metrics["confusion_matrix"]))
        elif "residuals" in metrics:
            html += "<h4>Residuals Plot</h4>"
            html += _plot_to_html(_plot_residuals(metrics["residuals"]))

    # 🔍 Explainability
    html += "<hr><h2>Explainability</h2>"
    if isinstance(explanations, list):
        for item in explanations:
            html += f"<h3>{item['model']}</h3>"
            html += item["explanation"].get("plot_html", "<p>SHAP plot unavailable</p>")
    else:
        html += explanations.get("plot_html", "<p>SHAP plot unavailable</p>")

    html += "</body></html>"

    with open(output, "w", encoding="utf-8") as f:
        f.write(html)

# 🔍 Convert Matplotlib plot to HTML image
def _plot_to_html(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return f'<img src="data:image/png;base64,{encoded}"/>'

# 📊 Confusion Matrix Plot
def _plot_confusion_matrix(cm):
    fig, ax = plt.subplots()
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax)
    ax.set_title("Confusion Matrix")
    return fig

# 📈 Residuals Plot
def _plot_residuals(residuals):
    fig, ax = plt.subplots()
    sns.histplot(residuals, kde=True, ax=ax)
    ax.set_title("Residuals Distribution")
    return fig