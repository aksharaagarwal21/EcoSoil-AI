"""
Intelligent Environment Sustainability — Flask API Server
Serves the ML soil analysis dashboard and API endpoints.
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from ml_models import SoilAnalysisEngine
import traceback

app = Flask(__name__)
CORS(app)

# Initialize the ML engine (trains models on startup)
print("=" * 60)
print("  Intelligent Environment Sustainability")
print("  ML-Powered Soil Analysis Platform")
print("=" * 60)
engine = SoilAnalysisEngine()


@app.route("/")
def index():
    """Serve the main dashboard."""
    return render_template("index.html")


@app.route("/api/analyze", methods=["POST"])
def analyze_soil():
    """Run full ML analysis on soil data."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No input data provided"}), 400

        # Parse and validate input
        soil_data = {
            "N": float(data.get("N", 50)),
            "P": float(data.get("P", 30)),
            "K": float(data.get("K", 40)),
            "pH": float(data.get("pH", 6.5)),
            "temperature": float(data.get("temperature", 25)),
            "humidity": float(data.get("humidity", 60)),
            "rainfall": float(data.get("rainfall", 100)),
            "organic_carbon": float(data.get("organic_carbon", 1.0)),
            "moisture": float(data.get("moisture", 35)),
            "EC": float(data.get("EC", 0.8)),
            "soil_type": data.get("soil_type", "Loamy"),
        }

        result = engine.analyze(soil_data)
        return jsonify(result)

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/history")
def get_history():
    """Return analysis history."""
    try:
        history = engine.get_history()
        return jsonify({"history": history})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/sustainability-trends")
def get_trends():
    """Return sustainability trend data."""
    try:
        trends = engine.generate_trend_data()
        return jsonify({"trends": trends})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/soil-benchmarks")
def get_benchmarks():
    """Return soil quality benchmarks."""
    try:
        benchmarks = engine.get_soil_benchmarks()
        return jsonify(benchmarks)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
