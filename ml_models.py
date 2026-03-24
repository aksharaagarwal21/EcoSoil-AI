"""
Intelligent Environment Sustainability — ML Soil Analysis Engine
Advanced ML pipeline for soil health prediction, nutrient classification,
crop recommendation, and sustainability index computation.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingRegressor,
    RandomForestRegressor,
    VotingRegressor,
)
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.multioutput import MultiOutputClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import warnings
import json
from datetime import datetime, timedelta
import random

warnings.filterwarnings("ignore")

# ─── Synthetic Dataset Generation ────────────────────────────────────────────

SOIL_TYPES = [
    "Alluvial", "Black Cotton", "Red", "Laterite", "Desert",
    "Mountain", "Peaty", "Saline", "Loamy", "Clay",
    "Sandy", "Silt", "Chalky", "Podzol"
]

CROPS = [
    "Rice", "Wheat", "Maize", "Cotton", "Sugarcane",
    "Soybean", "Groundnut", "Sunflower", "Mustard", "Barley",
    "Millet", "Sorghum", "Chickpea", "Lentil", "Potato",
    "Tomato", "Onion", "Tea", "Coffee", "Rubber",
    "Coconut", "Banana", "Mango", "Turmeric", "Ginger"
]

CROP_REQUIREMENTS = {
    "Rice":       {"N": (80, 130), "P": (40, 60), "K": (40, 60), "pH": (5.5, 7.0), "temp": (22, 32), "humidity": (70, 95), "rainfall": (150, 300)},
    "Wheat":      {"N": (70, 120), "P": (35, 55), "K": (30, 50), "pH": (6.0, 7.5), "temp": (15, 25), "humidity": (40, 70), "rainfall": (50, 120)},
    "Maize":      {"N": (60, 110), "P": (30, 50), "K": (25, 45), "pH": (5.5, 7.5), "temp": (18, 30), "humidity": (50, 80), "rainfall": (60, 150)},
    "Cotton":     {"N": (80, 140), "P": (35, 55), "K": (20, 40), "pH": (6.0, 8.0), "temp": (25, 35), "humidity": (40, 70), "rainfall": (50, 120)},
    "Sugarcane":  {"N": (90, 150), "P": (40, 65), "K": (40, 60), "pH": (5.5, 7.5), "temp": (25, 35), "humidity": (60, 85), "rainfall": (100, 250)},
    "Soybean":    {"N": (20, 50),  "P": (50, 70), "K": (30, 50), "pH": (6.0, 7.0), "temp": (20, 30), "humidity": (55, 80), "rainfall": (60, 150)},
    "Groundnut":  {"N": (15, 40),  "P": (40, 65), "K": (30, 55), "pH": (5.5, 7.0), "temp": (25, 32), "humidity": (50, 75), "rainfall": (50, 120)},
    "Sunflower":  {"N": (50, 90),  "P": (35, 55), "K": (25, 45), "pH": (6.0, 7.5), "temp": (20, 30), "humidity": (40, 65), "rainfall": (40, 100)},
    "Mustard":    {"N": (40, 80),  "P": (25, 45), "K": (20, 40), "pH": (6.0, 7.5), "temp": (15, 25), "humidity": (35, 60), "rainfall": (30, 80)},
    "Barley":     {"N": (50, 90),  "P": (25, 45), "K": (25, 45), "pH": (6.5, 8.0), "temp": (12, 22), "humidity": (35, 65), "rainfall": (40, 100)},
    "Millet":     {"N": (40, 70),  "P": (20, 40), "K": (20, 40), "pH": (5.5, 7.5), "temp": (25, 35), "humidity": (30, 60), "rainfall": (30, 80)},
    "Sorghum":    {"N": (50, 90),  "P": (25, 45), "K": (25, 45), "pH": (5.5, 7.5), "temp": (25, 35), "humidity": (35, 65), "rainfall": (40, 100)},
    "Chickpea":   {"N": (15, 35),  "P": (40, 65), "K": (20, 40), "pH": (6.0, 8.0), "temp": (15, 30), "humidity": (30, 55), "rainfall": (30, 80)},
    "Lentil":     {"N": (10, 30),  "P": (35, 60), "K": (20, 40), "pH": (6.0, 7.5), "temp": (15, 28), "humidity": (35, 60), "rainfall": (30, 80)},
    "Potato":     {"N": (80, 130), "P": (50, 80), "K": (50, 80), "pH": (5.0, 6.5), "temp": (15, 22), "humidity": (60, 85), "rainfall": (50, 120)},
    "Tomato":     {"N": (70, 120), "P": (60, 90), "K": (50, 80), "pH": (5.5, 7.0), "temp": (20, 30), "humidity": (55, 80), "rainfall": (40, 100)},
    "Onion":      {"N": (60, 100), "P": (40, 65), "K": (40, 65), "pH": (6.0, 7.5), "temp": (15, 28), "humidity": (50, 75), "rainfall": (40, 100)},
    "Tea":        {"N": (90, 150), "P": (20, 40), "K": (30, 50), "pH": (4.5, 5.5), "temp": (18, 28), "humidity": (75, 95), "rainfall": (150, 300)},
    "Coffee":     {"N": (80, 130), "P": (25, 45), "K": (40, 65), "pH": (5.0, 6.5), "temp": (18, 28), "humidity": (70, 90), "rainfall": (120, 250)},
    "Rubber":     {"N": (60, 100), "P": (20, 40), "K": (25, 45), "pH": (4.5, 6.0), "temp": (25, 35), "humidity": (75, 95), "rainfall": (150, 300)},
    "Coconut":    {"N": (50, 90),  "P": (30, 50), "K": (60, 100),"pH": (5.5, 7.0), "temp": (25, 35), "humidity": (65, 90), "rainfall": (100, 250)},
    "Banana":     {"N": (80, 140), "P": (30, 55), "K": (70, 120),"pH": (5.5, 7.0), "temp": (25, 35), "humidity": (70, 90), "rainfall": (100, 250)},
    "Mango":      {"N": (50, 90),  "P": (25, 50), "K": (50, 80), "pH": (5.5, 7.5), "temp": (25, 35), "humidity": (50, 75), "rainfall": (60, 150)},
    "Turmeric":   {"N": (60, 100), "P": (30, 55), "K": (60, 100),"pH": (5.0, 7.0), "temp": (20, 30), "humidity": (65, 90), "rainfall": (100, 200)},
    "Ginger":     {"N": (70, 110), "P": (40, 65), "K": (50, 80), "pH": (5.5, 6.5), "temp": (20, 30), "humidity": (70, 90), "rainfall": (120, 250)},
}


def generate_soil_dataset(n_samples=3000):
    """Generate a realistic synthetic soil dataset for model training."""
    np.random.seed(42)
    data = []
    for _ in range(n_samples):
        soil_type = np.random.choice(SOIL_TYPES)
        # Base ranges depending on soil type
        base = _soil_type_base(soil_type)
        N = np.clip(np.random.normal(base["N"], 20), 0, 200)
        P = np.clip(np.random.normal(base["P"], 12), 0, 150)
        K = np.clip(np.random.normal(base["K"], 15), 0, 200)
        pH = np.clip(np.random.normal(base["pH"], 0.6), 3.0, 10.0)
        temperature = np.clip(np.random.normal(base["temp"], 5), 5, 45)
        humidity = np.clip(np.random.normal(base["humidity"], 12), 10, 100)
        rainfall = np.clip(np.random.normal(base["rainfall"], 40), 10, 400)
        organic_carbon = np.clip(np.random.normal(base["oc"], 0.3), 0.1, 5.0)
        moisture = np.clip(np.random.normal(base["moisture"], 8), 5, 80)
        EC = np.clip(np.random.normal(base["EC"], 0.2), 0.1, 4.0)

        # Determine best crop
        best_crop = _match_crop(N, P, K, pH, temperature, humidity, rainfall)

        # Compute health score (0-100) based on nutrient balance
        health_score = _compute_health_score(N, P, K, pH, organic_carbon, moisture, EC)

        # Nutrient deficiency flags
        n_def = 1 if N < 40 else 0
        p_def = 1 if P < 20 else 0
        k_def = 1 if K < 25 else 0
        ph_imbalance = 1 if pH < 5.0 or pH > 8.0 else 0
        oc_low = 1 if organic_carbon < 0.5 else 0

        data.append({
            "N": round(N, 2), "P": round(P, 2), "K": round(K, 2),
            "pH": round(pH, 2), "temperature": round(temperature, 2),
            "humidity": round(humidity, 2), "rainfall": round(rainfall, 2),
            "organic_carbon": round(organic_carbon, 2),
            "moisture": round(moisture, 2), "EC": round(EC, 2),
            "soil_type": soil_type, "crop": best_crop,
            "health_score": round(health_score, 2),
            "N_deficient": n_def, "P_deficient": p_def,
            "K_deficient": k_def, "pH_imbalance": ph_imbalance,
            "OC_low": oc_low,
        })
    return pd.DataFrame(data)


def _soil_type_base(soil_type):
    """Return base parameter means per soil type."""
    bases = {
        "Alluvial":      {"N": 80, "P": 45, "K": 50, "pH": 7.0, "temp": 27, "humidity": 65, "rainfall": 120, "oc": 1.2, "moisture": 40, "EC": 0.8},
        "Black Cotton":  {"N": 70, "P": 35, "K": 55, "pH": 7.5, "temp": 30, "humidity": 55, "rainfall": 90,  "oc": 1.0, "moisture": 45, "EC": 1.2},
        "Red":           {"N": 50, "P": 30, "K": 35, "pH": 6.0, "temp": 28, "humidity": 55, "rainfall": 80,  "oc": 0.7, "moisture": 30, "EC": 0.6},
        "Laterite":      {"N": 45, "P": 25, "K": 30, "pH": 5.5, "temp": 28, "humidity": 70, "rainfall": 180, "oc": 0.6, "moisture": 35, "EC": 0.5},
        "Desert":        {"N": 25, "P": 15, "K": 20, "pH": 8.0, "temp": 35, "humidity": 25, "rainfall": 25,  "oc": 0.3, "moisture": 12, "EC": 2.0},
        "Mountain":      {"N": 55, "P": 30, "K": 40, "pH": 5.8, "temp": 15, "humidity": 70, "rainfall": 150, "oc": 1.5, "moisture": 50, "EC": 0.4},
        "Peaty":         {"N": 90, "P": 20, "K": 25, "pH": 4.8, "temp": 20, "humidity": 80, "rainfall": 200, "oc": 3.0, "moisture": 65, "EC": 0.3},
        "Saline":        {"N": 35, "P": 20, "K": 30, "pH": 8.5, "temp": 30, "humidity": 40, "rainfall": 40,  "oc": 0.4, "moisture": 20, "EC": 3.0},
        "Loamy":         {"N": 75, "P": 50, "K": 55, "pH": 6.5, "temp": 26, "humidity": 60, "rainfall": 100, "oc": 1.4, "moisture": 42, "EC": 0.7},
        "Clay":          {"N": 65, "P": 40, "K": 50, "pH": 7.0, "temp": 27, "humidity": 60, "rainfall": 110, "oc": 1.1, "moisture": 50, "EC": 0.9},
        "Sandy":         {"N": 30, "P": 20, "K": 25, "pH": 6.5, "temp": 30, "humidity": 35, "rainfall": 50,  "oc": 0.4, "moisture": 15, "EC": 0.5},
        "Silt":          {"N": 70, "P": 45, "K": 45, "pH": 6.8, "temp": 25, "humidity": 60, "rainfall": 100, "oc": 1.3, "moisture": 45, "EC": 0.7},
        "Chalky":        {"N": 40, "P": 25, "K": 35, "pH": 8.0, "temp": 22, "humidity": 45, "rainfall": 60,  "oc": 0.6, "moisture": 25, "EC": 1.5},
        "Podzol":        {"N": 35, "P": 15, "K": 20, "pH": 4.5, "temp": 12, "humidity": 75, "rainfall": 180, "oc": 2.5, "moisture": 55, "EC": 0.3},
    }
    return bases.get(soil_type, bases["Loamy"])


def _match_crop(N, P, K, pH, temp, humidity, rainfall):
    """Find the best-matching crop from CROP_REQUIREMENTS."""
    best_crop = "Wheat"
    best_score = -1
    for crop, req in CROP_REQUIREMENTS.items():
        score = 0
        score += max(0, 1 - abs(N - np.mean(req["N"])) / (req["N"][1] - req["N"][0] + 1))
        score += max(0, 1 - abs(P - np.mean(req["P"])) / (req["P"][1] - req["P"][0] + 1))
        score += max(0, 1 - abs(K - np.mean(req["K"])) / (req["K"][1] - req["K"][0] + 1))
        score += max(0, 1 - abs(pH - np.mean(req["pH"])) / (req["pH"][1] - req["pH"][0] + 0.1))
        score += max(0, 1 - abs(temp - np.mean(req["temp"])) / (req["temp"][1] - req["temp"][0] + 1))
        score += max(0, 1 - abs(humidity - np.mean(req["humidity"])) / (req["humidity"][1] - req["humidity"][0] + 1))
        score += max(0, 1 - abs(rainfall - np.mean(req["rainfall"])) / (req["rainfall"][1] - req["rainfall"][0] + 1))
        if score > best_score:
            best_score = score
            best_crop = crop
    return best_crop


def _compute_health_score(N, P, K, pH, oc, moisture, EC):
    """Compute a composite soil health score (0-100)."""
    n_score = min(N / 100, 1.0) * 15
    p_score = min(P / 60, 1.0) * 15
    k_score = min(K / 60, 1.0) * 15
    pH_score = max(0, 1 - abs(pH - 6.5) / 3.5) * 20
    oc_score = min(oc / 2.0, 1.0) * 15
    moisture_score = max(0, 1 - abs(moisture - 40) / 40) * 10
    ec_score = max(0, 1 - EC / 4.0) * 10
    total = n_score + p_score + k_score + pH_score + oc_score + moisture_score + ec_score
    return np.clip(total, 0, 100)


# ─── ML Models ───────────────────────────────────────────────────────────────

class SoilAnalysisEngine:
    """Complete ML engine for soil analysis and sustainability assessment."""

    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.crop_encoder = LabelEncoder()
        self.health_model = None
        self.nutrient_model = None
        self.crop_model = None
        self.feature_names = [
            "N", "P", "K", "pH", "temperature", "humidity",
            "rainfall", "organic_carbon", "moisture", "EC", "soil_type_encoded"
        ]
        self.analysis_history = []
        self._train_all_models()

    def _train_all_models(self):
        """Train all ML models on synthetic data."""
        print("[ML Engine] Generating training data...")
        df = generate_soil_dataset(3000)

        # Encode categorical
        df["soil_type_encoded"] = self.label_encoder.fit_transform(df["soil_type"])
        df["crop_encoded"] = self.crop_encoder.fit_transform(df["crop"])

        X = df[self.feature_names].values
        X_scaled = self.scaler.fit_transform(X)

        # 1) Health Score Regression (Ensemble)
        print("[ML Engine] Training Soil Health Predictor (Ensemble)...")
        y_health = df["health_score"].values
        gb = GradientBoostingRegressor(n_estimators=150, max_depth=5, learning_rate=0.1, random_state=42)
        rf = RandomForestRegressor(n_estimators=150, max_depth=8, random_state=42)
        self.health_model = VotingRegressor(estimators=[("gb", gb), ("rf", rf)])
        self.health_model.fit(X_scaled, y_health)
        print("[ML Engine] ✓ Health model trained")

        # 2) Nutrient Deficiency Multi-Output Classifier
        print("[ML Engine] Training Nutrient Deficiency Classifier...")
        y_nutrients = df[["N_deficient", "P_deficient", "K_deficient", "pH_imbalance", "OC_low"]].values
        base_clf = RandomForestClassifier(n_estimators=120, max_depth=6, random_state=42)
        self.nutrient_model = MultiOutputClassifier(base_clf)
        self.nutrient_model.fit(X_scaled, y_nutrients)
        print("[ML Engine] ✓ Nutrient classifier trained")

        # 3) Crop Recommendation (KNN + Decision Tree ensemble)
        print("[ML Engine] Training Crop Recommender...")
        y_crop = df["crop_encoded"].values
        self.knn_model = KNeighborsClassifier(n_neighbors=7, weights="distance")
        self.dt_model = DecisionTreeClassifier(max_depth=10, random_state=42)
        self.knn_model.fit(X_scaled, y_crop)
        self.dt_model.fit(X_scaled, y_crop)
        print("[ML Engine] ✓ Crop recommender trained")

        print("[ML Engine] All models trained successfully!\n")

    def _prepare_input(self, soil_data):
        """Prepare and scale input features."""
        soil_type_str = soil_data.get("soil_type", "Loamy")
        if soil_type_str in self.label_encoder.classes_:
            soil_type_enc = self.label_encoder.transform([soil_type_str])[0]
        else:
            soil_type_enc = self.label_encoder.transform(["Loamy"])[0]

        features = np.array([[
            soil_data.get("N", 50),
            soil_data.get("P", 30),
            soil_data.get("K", 40),
            soil_data.get("pH", 6.5),
            soil_data.get("temperature", 25),
            soil_data.get("humidity", 60),
            soil_data.get("rainfall", 100),
            soil_data.get("organic_carbon", 1.0),
            soil_data.get("moisture", 35),
            soil_data.get("EC", 0.8),
            soil_type_enc,
        ]])
        return self.scaler.transform(features)

    def predict_health(self, soil_data):
        """Predict soil health score (0-100)."""
        X = self._prepare_input(soil_data)
        score = float(self.health_model.predict(X)[0])
        score = np.clip(score, 0, 100)

        # Determine grade
        if score >= 85:
            grade = "Excellent"
            color = "#00e676"
        elif score >= 70:
            grade = "Good"
            color = "#76ff03"
        elif score >= 50:
            grade = "Moderate"
            color = "#ffd600"
        elif score >= 30:
            grade = "Poor"
            color = "#ff9100"
        else:
            grade = "Critical"
            color = "#ff1744"

        return {
            "score": round(score, 1),
            "grade": grade,
            "color": color,
            "description": self._health_description(score, grade),
        }

    def _health_description(self, score, grade):
        descs = {
            "Excellent": "Soil is in optimal condition with well-balanced nutrients and excellent structure. Ideal for high-yield agriculture.",
            "Good": "Soil health is above average. Minor improvements in specific nutrients could optimize productivity.",
            "Moderate": "Soil requires attention. Some nutrient deficiencies or imbalances detected that may affect crop yield.",
            "Poor": "Significant soil degradation detected. Immediate remediation recommended to restore productivity.",
            "Critical": "Soil is severely degraded. Comprehensive restoration program needed before agricultural use.",
        }
        return descs.get(grade, "")

    def classify_nutrients(self, soil_data):
        """Classify nutrient deficiencies."""
        X = self._prepare_input(soil_data)
        predictions = self.nutrient_model.predict(X)[0]
        probabilities = [est.predict_proba(X)[0] for est in self.nutrient_model.estimators_]

        labels = ["Nitrogen (N)", "Phosphorus (P)", "Potassium (K)", "pH Balance", "Organic Carbon"]
        keys = ["N", "P", "K", "pH", "OC"]
        actual_values = [
            soil_data.get("N", 50),
            soil_data.get("P", 30),
            soil_data.get("K", 40),
            soil_data.get("pH", 6.5),
            soil_data.get("organic_carbon", 1.0),
        ]
        optimal_ranges = [
            (40, 120), (20, 80), (25, 80), (5.5, 7.5), (0.5, 3.0)
        ]

        results = []
        for i, (label, key, pred, prob, val, opt) in enumerate(
            zip(labels, keys, predictions, probabilities, actual_values, optimal_ranges)
        ):
            deficient = bool(pred)
            confidence = float(max(prob)) * 100
            status = "Deficient" if deficient else "Adequate"
            severity = "none"
            if deficient:
                if val < opt[0] * 0.5:
                    severity = "critical"
                elif val < opt[0] * 0.75:
                    severity = "high"
                else:
                    severity = "moderate"

            results.append({
                "nutrient": label,
                "key": key,
                "value": round(val, 2),
                "status": status,
                "deficient": deficient,
                "confidence": round(confidence, 1),
                "severity": severity,
                "optimal_range": list(opt),
                "recommendation": self._nutrient_recommendation(key, deficient, val, opt),
            })
        return results

    def _nutrient_recommendation(self, key, deficient, value, optimal):
        if not deficient:
            return f"Levels are within optimal range ({optimal[0]}-{optimal[1]}). Maintain current soil management practices."
        recs = {
            "N": "Apply nitrogen-rich fertilizers (urea, ammonium nitrate) or incorporate legume cover crops for biological nitrogen fixation.",
            "P": "Add phosphate fertilizers (superphosphate, bone meal) or rock phosphate for slow release. Ensure pH is in range for P availability.",
            "K": "Apply potash fertilizers (muriate of potash, potassium sulfate) or use wood ash as a natural potassium source.",
            "pH": f"Current pH ({value}) is outside optimal range. {'Apply lime (calcium carbonate) to raise' if value < optimal[0] else 'Apply sulfur or acidifying fertilizers to lower'} soil pH.",
            "OC": "Increase organic matter through compost, green manure, crop residues, or biochar application. Practice minimum tillage.",
        }
        return recs.get(key, "Consult a soil scientist for detailed recommendations.")

    def recommend_crops(self, soil_data, top_n=5):
        """Recommend top crops based on soil conditions."""
        X = self._prepare_input(soil_data)

        # KNN probabilities
        knn_proba = self.knn_model.predict_proba(X)[0]
        # DT probabilities
        dt_proba = self.dt_model.predict_proba(X)[0]

        # Weighted average (KNN 60%, DT 40%)
        combined = 0.6 * knn_proba + 0.4 * dt_proba
        top_indices = np.argsort(combined)[::-1][:top_n]

        recommendations = []
        for idx in top_indices:
            crop_name = self.crop_encoder.inverse_transform([idx])[0]
            confidence = float(combined[idx]) * 100

            # Get ideal conditions for this crop
            req = CROP_REQUIREMENTS.get(crop_name, {})
            suitability = self._crop_suitability(soil_data, req) if req else 50

            recommendations.append({
                "crop": crop_name,
                "confidence": round(confidence, 1),
                "suitability": round(suitability, 1),
                "season": self._get_crop_season(crop_name),
                "water_requirement": self._get_water_req(crop_name),
                "growth_period": self._get_growth_period(crop_name),
                "ideal_conditions": {
                    "N": list(req.get("N", (50, 100))),
                    "P": list(req.get("P", (30, 60))),
                    "K": list(req.get("K", (30, 60))),
                    "pH": list(req.get("pH", (6.0, 7.5))),
                    "temperature": list(req.get("temp", (20, 30))),
                }
            })
        return recommendations

    def _crop_suitability(self, soil_data, req):
        """Calculate suitability percentage for a crop."""
        score = 0
        total = 0
        for key, soil_key in [("N", "N"), ("P", "P"), ("K", "K"), ("pH", "pH"), ("temp", "temperature"), ("humidity", "humidity"), ("rainfall", "rainfall")]:
            if key in req:
                val = soil_data.get(soil_key, 0)
                low, high = req[key]
                if low <= val <= high:
                    score += 1
                else:
                    dist = min(abs(val - low), abs(val - high)) / (high - low + 1)
                    score += max(0, 1 - dist)
                total += 1
        return (score / total * 100) if total > 0 else 50

    def _get_crop_season(self, crop):
        seasons = {
            "Rice": "Kharif (Jun-Oct)", "Wheat": "Rabi (Nov-Mar)", "Maize": "Kharif/Rabi",
            "Cotton": "Kharif (Jun-Oct)", "Sugarcane": "Year-round", "Soybean": "Kharif (Jun-Oct)",
            "Groundnut": "Kharif/Rabi", "Sunflower": "Rabi (Nov-Mar)", "Mustard": "Rabi (Nov-Mar)",
            "Barley": "Rabi (Nov-Mar)", "Millet": "Kharif (Jun-Oct)", "Sorghum": "Kharif/Rabi",
            "Chickpea": "Rabi (Nov-Mar)", "Lentil": "Rabi (Nov-Mar)", "Potato": "Rabi (Nov-Mar)",
            "Tomato": "Year-round", "Onion": "Rabi (Nov-Mar)", "Tea": "Year-round",
            "Coffee": "Year-round", "Rubber": "Year-round", "Coconut": "Year-round",
            "Banana": "Year-round", "Mango": "Summer", "Turmeric": "Kharif (Jun-Oct)",
            "Ginger": "Kharif (Jun-Oct)",
        }
        return seasons.get(crop, "Varies")

    def _get_water_req(self, crop):
        reqs = {
            "Rice": "High", "Wheat": "Medium", "Maize": "Medium", "Cotton": "Medium",
            "Sugarcane": "Very High", "Soybean": "Medium", "Groundnut": "Low-Medium",
            "Sunflower": "Low", "Mustard": "Low", "Barley": "Low",
            "Millet": "Very Low", "Sorghum": "Low", "Chickpea": "Low",
            "Lentil": "Low", "Potato": "Medium", "Tomato": "Medium",
            "Onion": "Medium", "Tea": "High", "Coffee": "High",
            "Rubber": "High", "Coconut": "Medium", "Banana": "High",
            "Mango": "Medium", "Turmeric": "High", "Ginger": "High",
        }
        return reqs.get(crop, "Medium")

    def _get_growth_period(self, crop):
        periods = {
            "Rice": "120-150 days", "Wheat": "110-130 days", "Maize": "90-120 days",
            "Cotton": "150-180 days", "Sugarcane": "300-365 days", "Soybean": "90-120 days",
            "Groundnut": "100-130 days", "Sunflower": "80-100 days", "Mustard": "100-130 days",
            "Barley": "90-120 days", "Millet": "65-80 days", "Sorghum": "100-120 days",
            "Chickpea": "90-120 days", "Lentil": "80-110 days", "Potato": "75-120 days",
            "Tomato": "60-90 days", "Onion": "120-150 days", "Tea": "Perennial",
            "Coffee": "Perennial", "Rubber": "Perennial", "Coconut": "Perennial",
            "Banana": "270-365 days", "Mango": "Perennial", "Turmeric": "210-270 days",
            "Ginger": "210-270 days",
        }
        return periods.get(crop, "90-120 days")

    def compute_sustainability_index(self, soil_data, health_result, nutrient_results):
        """Calculate composite sustainability index."""
        # Soil Quality (30%)
        soil_quality = health_result["score"] / 100

        # Biodiversity Potential (20%) — based on organic carbon, pH balance, moisture
        oc = soil_data.get("organic_carbon", 1.0)
        pH = soil_data.get("pH", 6.5)
        moisture = soil_data.get("moisture", 35)
        biodiversity = (
            min(oc / 2.0, 1.0) * 0.4 +
            max(0, 1 - abs(pH - 6.5) / 3.0) * 0.3 +
            min(moisture / 50, 1.0) * 0.3
        )

        # Water Retention (20%) — soil type and moisture
        water_retention_map = {
            "Clay": 0.9, "Peaty": 0.95, "Silt": 0.8, "Loamy": 0.85,
            "Alluvial": 0.75, "Black Cotton": 0.8, "Mountain": 0.7,
            "Red": 0.5, "Laterite": 0.55, "Sandy": 0.3, "Desert": 0.15,
            "Chalky": 0.5, "Saline": 0.4, "Podzol": 0.65,
        }
        soil_type = soil_data.get("soil_type", "Loamy")
        base_retention = water_retention_map.get(soil_type, 0.5)
        water_retention = base_retention * 0.7 + min(moisture / 60, 1) * 0.3

        # Carbon Sequestration (20%)
        carbon_seq = min(oc / 2.5, 1.0) * 0.6 + soil_quality * 0.4

        # Nutrient Cycle Efficiency (10%)
        deficient_count = sum(1 for n in nutrient_results if n["deficient"])
        nutrient_efficiency = max(0, 1 - deficient_count / 5)

        # Composite
        composite = (
            soil_quality * 0.30 +
            biodiversity * 0.20 +
            water_retention * 0.20 +
            carbon_seq * 0.20 +
            nutrient_efficiency * 0.10
        )

        return {
            "composite_score": round(composite * 100, 1),
            "grade": self._sustainability_grade(composite * 100),
            "breakdown": {
                "soil_quality": round(soil_quality * 100, 1),
                "biodiversity_potential": round(biodiversity * 100, 1),
                "water_retention": round(water_retention * 100, 1),
                "carbon_sequestration": round(carbon_seq * 100, 1),
                "nutrient_efficiency": round(nutrient_efficiency * 100, 1),
            },
            "environmental_impact": {
                "carbon_footprint_reduction": round(carbon_seq * 35, 1),
                "water_conservation": round(water_retention * 40, 1),
                "biodiversity_index": round(biodiversity * 10, 2),
                "erosion_risk": self._erosion_risk(soil_type, moisture, oc),
            },
            "recommendations": self._sustainability_recommendations(composite * 100, soil_data, nutrient_results),
        }

    def _sustainability_grade(self, score):
        if score >= 85: return "A+"
        elif score >= 75: return "A"
        elif score >= 65: return "B+"
        elif score >= 55: return "B"
        elif score >= 45: return "C"
        elif score >= 35: return "D"
        else: return "F"

    def _erosion_risk(self, soil_type, moisture, oc):
        high_risk = ["Sandy", "Desert", "Chalky", "Saline"]
        medium_risk = ["Red", "Laterite", "Podzol"]
        if soil_type in high_risk:
            return "High"
        elif soil_type in medium_risk:
            return "Medium"
        elif oc < 0.5:
            return "Medium-High"
        else:
            return "Low"

    def _sustainability_recommendations(self, score, soil_data, nutrients):
        recs = []
        if score < 50:
            recs.append({
                "priority": "Critical",
                "action": "Implement immediate soil restoration program: add organic amendments, reduce tillage, and establish cover crops.",
                "impact": "Could improve sustainability score by 15-25 points"
            })
        if soil_data.get("organic_carbon", 1.0) < 0.8:
            recs.append({
                "priority": "High",
                "action": "Increase organic carbon through composting, green manuring, and biochar application.",
                "impact": "Improves carbon sequestration and biodiversity potential"
            })
        if soil_data.get("moisture", 35) < 20:
            recs.append({
                "priority": "High",
                "action": "Implement mulching and drip irrigation to improve soil moisture retention.",
                "impact": "Enhances water conservation and reduces erosion risk"
            })
        deficient_nutrients = [n["nutrient"] for n in nutrients if n["deficient"]]
        if deficient_nutrients:
            recs.append({
                "priority": "Medium",
                "action": f"Address deficiencies in: {', '.join(deficient_nutrients)}. Use targeted amendments and balanced fertilization.",
                "impact": "Improves nutrient cycle efficiency and crop yield potential"
            })
        if soil_data.get("pH", 6.5) < 5.0 or soil_data.get("pH", 6.5) > 8.0:
            recs.append({
                "priority": "Medium",
                "action": "Correct soil pH through lime (for acidic) or sulfur/gypsum (for alkaline) application.",
                "impact": "Optimizes nutrient availability and microbial activity"
            })
        recs.append({
            "priority": "Ongoing",
            "action": "Practice crop rotation, minimize chemical inputs, and conduct regular soil testing every 6 months.",
            "impact": "Maintains long-term soil health and sustainability"
        })
        return recs

    def analyze(self, soil_data):
        """Run complete analysis pipeline."""
        health = self.predict_health(soil_data)
        nutrients = self.classify_nutrients(soil_data)
        crops = self.recommend_crops(soil_data)
        sustainability = self.compute_sustainability_index(soil_data, health, nutrients)

        result = {
            "timestamp": datetime.now().isoformat(),
            "input_data": soil_data,
            "health": health,
            "nutrients": nutrients,
            "crop_recommendations": crops,
            "sustainability": sustainability,
        }

        self.analysis_history.append(result)
        return result

    def get_history(self):
        """Return analysis history."""
        return self.analysis_history

    def generate_trend_data(self):
        """Generate simulated historical sustainability trend data."""
        np.random.seed(42)
        trends = []
        base_date = datetime.now() - timedelta(days=365)
        base_score = 45
        for i in range(12):
            date = base_date + timedelta(days=i * 30)
            noise = np.random.normal(0, 3)
            improvement = i * 2.5
            score = np.clip(base_score + improvement + noise, 20, 95)
            trends.append({
                "date": date.strftime("%Y-%m-%d"),
                "month": date.strftime("%b %Y"),
                "sustainability_score": round(score, 1),
                "soil_health": round(np.clip(score + np.random.normal(0, 5), 20, 100), 1),
                "biodiversity": round(np.clip(score * 0.7 + np.random.normal(0, 4), 10, 100), 1),
                "water_retention": round(np.clip(score * 0.85 + np.random.normal(0, 3), 15, 100), 1),
                "carbon_seq": round(np.clip(score * 0.6 + np.random.normal(0, 5), 10, 100), 1),
            })
        return trends

    def get_soil_benchmarks(self):
        """Return reference soil quality benchmarks."""
        return {
            "parameters": {
                "N":  {"unit": "kg/ha", "low": 0, "medium": 40, "high": 80, "optimal": "40-120"},
                "P":  {"unit": "kg/ha", "low": 0, "medium": 20, "high": 50, "optimal": "20-80"},
                "K":  {"unit": "kg/ha", "low": 0, "medium": 25, "high": 55, "optimal": "25-80"},
                "pH": {"unit": "",      "low": 4.5, "medium": 5.5, "high": 7.5, "optimal": "5.5-7.5"},
                "organic_carbon": {"unit": "%", "low": 0.2, "medium": 0.5, "high": 1.5, "optimal": "0.5-3.0"},
                "moisture":       {"unit": "%", "low": 10,  "medium": 25,  "high": 50,  "optimal": "25-55"},
                "EC":             {"unit": "dS/m", "low": 0.2, "medium": 0.8, "high": 2.0, "optimal": "0.2-1.5"},
            },
            "soil_types": SOIL_TYPES,
            "health_grades": [
                {"grade": "Excellent", "range": "85-100", "color": "#00e676"},
                {"grade": "Good",      "range": "70-84",  "color": "#76ff03"},
                {"grade": "Moderate",  "range": "50-69",  "color": "#ffd600"},
                {"grade": "Poor",      "range": "30-49",  "color": "#ff9100"},
                {"grade": "Critical",  "range": "0-29",   "color": "#ff1744"},
            ],
        }
