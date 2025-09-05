def generate_report(summary, results, explanations, output):
    with open(output, "w") as f:
        f.write("<h1>ML Profiler Report</h1>")
        f.write("<h2>Summary</h2>")
        f.write(summary["summary"].to_html())
        f.write("<h2>Missing Values</h2>")
        f.write(summary["missing"].to_frame().to_html())
        f.write("<h2>Model Score</h2>")
        f.write(f"<p>{results['score']}</p>")
        f.write("<h2>Explainability</h2>")
        f.write("<p>SHAP values plotted separately</p>")