import shap
import matplotlib.pyplot as plt
import io
import base64

def explain_model(model, df, target_column=None):
    df = df.copy()
    if target_column:
        df = df.drop(columns=[target_column])

    # Use SHAP's auto explainer
    explainer = shap.Explainer(model, df)
    shap_values = explainer(df)

    # Generate summary plot
    fig = shap.plots.beeswarm(shap_values, show=False)
    plot_html = _plot_to_html(fig)

    return {
        "shap_values": shap_values,
        "plot_html": plot_html
    }

# 🔧 Helper: Convert Matplotlib plot to HTML image
def _plot_to_html(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return f'<img src="data:image/png;base64,{encoded}"/>'