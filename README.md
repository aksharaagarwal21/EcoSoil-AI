# EcoSoil AI · Soil Health Analysis

A dashboard that uses machine learning to score soil health, classify nutrient levels and recommend suitable crops.

## Features

- Soil health score from a voting ensemble of gradient boosting and random forest regressors
- Nutrient level classification with a multi-output random forest
- Crop recommendation with k-nearest neighbours and a decision tree
- Sustainability trends, soil benchmarks and analysis history

> The models are trained on startup on a synthetic dataset of 3,000 soil samples generated in `ml_models.py`, so results are illustrative rather than agronomic advice.

## Tech stack

Python · Flask · scikit-learn · pandas · NumPy · HTML, CSS and JavaScript

## Run locally

```bash
pip install -r requirements.txt
python app.py
```

Open http://localhost:5000.
