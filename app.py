from flask import Flask, request, jsonify, send_from_directory
import math
import random
import os

app = Flask(__name__, static_folder=".", static_url_path="")

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
    return response

# ==========================
# DASS-21 QUESTION MAPPING
# ==========================

DEPRESSION_ITEMS = [3, 5, 10, 13, 16, 17, 21]
ANXIETY_ITEMS = [2, 4, 7, 9, 15, 19, 20]
STRESS_ITEMS = [1, 6, 8, 11, 12, 14, 18]

# ==========================
# SEVERITY THRESHOLDS
# ==========================

def classify_depression(score):
    if score <= 9: return "Normal"
    if score <= 13: return "Mild"
    if score <= 20: return "Moderate"
    if score <= 27: return "Severe"
    return "Extremely Severe"

def classify_anxiety(score):
    if score <= 7: return "Normal"
    if score <= 9: return "Mild"
    if score <= 14: return "Moderate"
    if score <= 19: return "Severe"
    return "Extremely Severe"

def classify_stress(score):
    if score <= 14: return "Normal"
    if score <= 18: return "Mild"
    if score <= 25: return "Moderate"
    if score <= 33: return "Severe"
    return "Extremely Severe"

# ==========================
# HELPER FUNCTIONS
# ==========================

def compute_subscale_score(answers, items):
    # DASS-21 scores must be multiplied by 2
    return sum(answers[i-1] for i in items) * 2

def generate_depression_curve(base_score):
    curve = []
    for week in range(1, 13):
        projected = base_score * (1 + 0.02 * week)
        curve.append(round(min(projected, 42), 2))
    return curve

def burnout_trajectory(stress, anxiety):
    base = (stress + anxiety) / 2
    trajectory = []
    for week in range(1, 13):
        growth = base * math.exp(0.03 * week)
        trajectory.append(round(min(growth / 42, 1), 3))
    return trajectory

def monte_carlo_relapse(cognitive_score, sleep_score):
    simulations = 1000
    relapse_count = 0

    base_risk = (cognitive_score + sleep_score) / 20

    for _ in range(simulations):
        if random.random() < base_risk:
            relapse_count += 1

    return round(relapse_count / simulations, 3)

def detect_cognitive_distortions(answers):
    distortions = {
        "Catastrophizing": answers[28],
        "Black-White Thinking": answers[29],
        "Mind Reading": answers[30],
        "Overgeneralization": answers[31],
        "Personalization": answers[32],
        "Emotional Reasoning": answers[33],
        "Should Statements": answers[34],
    }
    return distortions

def generate_prevention_plan(dep, anx, stress):
    plan = []

    if dep in ["Moderate", "Severe", "Extremely Severe"]:
        plan.append({
            "domain": "Depression",
            "recommendation": "Increase behavioral activation, structured daily goals, sunlight exposure."
        })

    if anx in ["Moderate", "Severe", "Extremely Severe"]:
        plan.append({
            "domain": "Anxiety",
            "recommendation": "Practice diaphragmatic breathing and reduce cognitive rumination cycles."
        })

    if stress in ["Moderate", "Severe", "Extremely Severe"]:
        plan.append({
            "domain": "Stress",
            "recommendation": "Implement workload boundary setting and weekly decompression routines."
        })

    if not plan:
        plan.append({
            "domain": "Wellbeing",
            "recommendation": "Maintain current mental hygiene habits and periodic self-assessment."
        })

    return plan

# ==========================
# ROUTES
# ==========================

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/api/predict", methods=["POST"])
def predict():
    data = request.json

    answers = data.get("answers", [])
    age = data.get("age")
    gender = data.get("gender")
    education = data.get("education")
    married = data.get("married")
    aleatoire = data.get("aleatoire")
    medical_record = data.get("medical_record")

    if len(answers) != 42:
        return jsonify({"error": "42 answers required"}), 400

    # ==========================
    # SCORES
    # ==========================

    depression_score = compute_subscale_score(answers, DEPRESSION_ITEMS)
    anxiety_score = compute_subscale_score(answers, ANXIETY_ITEMS)
    stress_score = compute_subscale_score(answers, STRESS_ITEMS)

    depression_severity = classify_depression(depression_score)
    anxiety_severity = classify_anxiety(anxiety_score)
    stress_severity = classify_stress(stress_score)

    # ==========================
    # PROJECTIONS
    # ==========================

    depression_curve = generate_depression_curve(depression_score)
    burnout_curve = burnout_trajectory(stress_score, anxiety_score)

    sleep_score = answers[0]
    cognitive_score = sum(answers[28:35]) / 7
    relapse_probability = monte_carlo_relapse(cognitive_score, sleep_score)

    distortions = detect_cognitive_distortions(answers)
    prevention_plan = generate_prevention_plan(
        depression_severity,
        anxiety_severity,
        stress_severity
    )

    response = {
        "scores": {
            "depression": depression_score,
            "anxiety": anxiety_score,
            "stress": stress_score
        },
        "severity": {
            "depression": depression_severity,
            "anxiety": anxiety_severity,
            "stress": stress_severity
        },
        "depression_curve_12_weeks": depression_curve,
        "burnout_probability_12_weeks": burnout_curve,
        "relapse_probability": relapse_probability,
        "cognitive_distortions": distortions,
        "prevention_plan": prevention_plan,
        "demographics": {
            "age": age,
            "gender": gender,
            "education": education,
            "married": married,
            "aleatoire": aleatoire,
            "medical_record": medical_record
        }
    }

    return jsonify(response)

# ==========================
# MAIN
# ==========================

if __name__ == "__main__":
    app.run(debug=True)
