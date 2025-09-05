import shap
import matplotlib.pyplot as plt
import io
import base64

def explain_model(model, df, target_column=None):
    df = df.copy()
    if target_column and target_column in df.columns:
        df = df.drop(columns=[target_column])

    # Use SHAP's auto explainer
    explainer = shap.Explainer(model, df)
    shap_values = explainer(df, check_additivity=False)

    if len(shap_values.values.shape) == 3:

        shap_values = shap.Explanation(
            values=shap_values.values[:, :, 0],
            base_values=shap_values.base_values[:, 0],
            data=shap_values.data,
            feature_names=shap_values.feature_names
        )

    # Generate summary plot
    ax = shap.plots.beeswarm(shap_values, show=False)
    plot_html = _plot_to_html(ax)

    return {
        "shap_values": shap_values,
        "plot_html": plot_html
    }

# 🔧 Helper: Convert Matplotlib plot to HTML image
def _plot_to_html(ax):
    fig = ax.figure  # ✅ Get the parent Figure from the Axes
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return f'<img src="data:image/png;base64,{encoded}"/>'