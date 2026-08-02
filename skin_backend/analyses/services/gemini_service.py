"""
gemini_service.py

Исто како во leafscan: Gemini НЕ ја прави класификацијата (тоа го прави
skin_model_service.py со локалниот модел). Gemini само генерира
општи, читливи информации/совети за состојбата откако веќе е предвидена,
и се повикува САМО еднаш по состојба (се кешира во базата преку
ConditionRecommendation - гледај views.py -> generate_recommendations_only_if_missing).

РАЗЛИКА од leafscan (важно): наместо "третмани" (третманот на кожни
лезии е медицинска работа - лекови, биопсија, операција - тоа НЕ треба AI
да го препишува), овој промпт бара општи self-care/lifestyle совети И
задолжително минимум еден совет од тип MEDICAL_CONSULT кој јасно
препорачува преглед кај дерматолог. Апликацијата никогаш не смее да тврди
дефинитивна дијагноза.
"""

import json
import os
from typing import List, Dict

from google import genai
from google.genai import types
from google.genai.errors import APIError


ALLOWED_RECOMMENDATION_TYPES = ["SELF_CARE", "MEDICAL_CONSULT", "LIFESTYLE"]


def build_recommendation_prompt(condition_name: str, severity: str) -> str:
    return f"""
You are a dermatology information assistant. You are NOT a doctor and must
never claim to provide a medical diagnosis or prescribe treatment.

Generate general care information for the following predicted skin condition:

Condition name: {condition_name}
Severity category: {severity}

Rules:
- Return ONLY valid JSON.
- Do not include markdown.
- Do not include explanations outside the JSON.
- Return minimum 2 and maximum 6 recommendations.
- Return maximum 2 recommendations per type.
- You MUST include at least ONE recommendation of type "MEDICAL_CONSULT"
  that clearly advises the user to see a dermatologist or doctor for proper
  diagnosis and treatment. If severity is "HIGH", make this urgency explicit.
- Never suggest specific medications, dosages, or definitive diagnoses.
- Allowed recommendation types are:
  - SELF_CARE
  - MEDICAL_CONSULT
  - LIFESTYLE

Each recommendation must have:
- name
- description
- type

The response must be a JSON array in this format:

[
  {{
    "name": "See a dermatologist",
    "description": "Schedule an appointment with a dermatologist for a proper clinical evaluation and, if needed, a biopsy.",
    "type": "MEDICAL_CONSULT"
  }}
]
"""


def validate_recommendations(recommendations: List[Dict]) -> List[Dict]:
    valid_recommendations = []

    type_counter = {
        "SELF_CARE": 0,
        "MEDICAL_CONSULT": 0,
        "LIFESTYLE": 0,
    }

    for item in recommendations:
        if not isinstance(item, dict):
            continue

        name = item.get("name")
        description = item.get("description")
        rec_type = item.get("type")

        if not name or not description or not rec_type:
            continue

        rec_type = str(rec_type).upper().strip()

        if rec_type not in ALLOWED_RECOMMENDATION_TYPES:
            continue

        if type_counter[rec_type] >= 2:
            continue

        valid_recommendations.append({
            "name": str(name).strip(),
            "description": str(description).strip(),
            "type": rec_type,
        })

        type_counter[rec_type] += 1

        if len(valid_recommendations) >= 6:
            break

    # ГАРАНЦИЈА: секогаш мора да има барем еден MEDICAL_CONSULT, дури и
    # ако Gemini не врати таков (или врати неважечки JSON).
    if type_counter["MEDICAL_CONSULT"] == 0:
        valid_recommendations.append(get_mandatory_medical_consult())

    return valid_recommendations


def get_mandatory_medical_consult() -> Dict:
    return {
        "name": "Consult a dermatologist",
        "description": (
            "This result is an AI-generated estimate, not a medical diagnosis. "
            "Please consult a licensed dermatologist for accurate evaluation."
        ),
        "type": "MEDICAL_CONSULT",
    }


def get_fallback_recommendations(condition_name: str, severity: str) -> List[Dict]:
    fallback = [get_mandatory_medical_consult()]

    fallback.append({
        "name": "Monitor for changes",
        "description": (
            f"Keep track of any changes in size, shape, or color of the area "
            f"associated with {condition_name}, and take a dated photo for comparison."
        ),
        "type": "SELF_CARE",
    })

    return fallback


def generate_recommendations_with_gemini(
    condition_name: str,
    severity: str,
    use_fallback: bool = True,
) -> List[Dict]:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing. Check your .env file.")

    client = genai.Client(api_key=api_key)

    prompt = build_recommendation_prompt(
        condition_name=condition_name,
        severity=severity,
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.4,
            ),
        )

        if not response.text:
            if use_fallback:
                return get_fallback_recommendations(condition_name, severity)
            return []

        try:
            recommendations = json.loads(response.text)
        except json.JSONDecodeError:
            if use_fallback:
                return get_fallback_recommendations(condition_name, severity)
            return []

        if not isinstance(recommendations, list):
            if use_fallback:
                return get_fallback_recommendations(condition_name, severity)
            return []

        valid_recommendations = validate_recommendations(recommendations)

        if not valid_recommendations and use_fallback:
            return get_fallback_recommendations(condition_name, severity)

        return valid_recommendations

    except APIError as error:
        print(f"Gemini API error: {error}")

        if use_fallback:
            return get_fallback_recommendations(condition_name, severity)

        return []

    except Exception as error:
        print(f"Unexpected Gemini service error: {error}")

        if use_fallback:
            return get_fallback_recommendations(condition_name, severity)

        return []
