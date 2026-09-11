"""
gemini_service.py

"""

import json
import os
import time
from typing import List, Dict

from google import genai
from google.genai import types
from google.genai.errors import APIError

# "gemini-2.5-flash" was cut off by Google for new projects (full shutdown
# planned for October 2026) - we use the "latest" alias instead of a fixed
# version so the model doesn't need to be changed by hand every time Google
# ships a new generation (Google gives 2 weeks notice before "latest" points
# to a version with breaking changes).
GEMINI_MODEL = "gemini-flash-latest"

# HTTP statuses that mean "try again" (temporarily overloaded model /
# rate limit), not a real error in our code or prompt.
_RETRYABLE_STATUS_CODES = {429, 503}
_MAX_ATTEMPTS = 3
_RETRY_BACKOFF_SECONDS = 1.5

# Without an explicit timeout, the underlying HTTP client has NO default
# ceiling - if Google's API is slow/unreachable from the server's network,
# a single call can hang for minutes, which hangs the whole scan-skin /
# chat request (and eventually the mobile/web client's own timeout fires
# first, showing "TimeoutException..." with no useful fallback content).
# 15s per attempt keeps the worst case (3 attempts + backoff, only on
# retryable 429/503 errors) under the mobile app's 60s scan-skin timeout.
#
# Built defensively at import time: if the installed google-genai version
# doesn't recognize this field, we fall back to no explicit timeout
# instead of crashing the import (which would break every view in this
# app, since views.py imports from this module at startup).
_GEMINI_TIMEOUT_MS = 15_000
try:
    _HTTP_OPTIONS = types.HttpOptions(timeout=_GEMINI_TIMEOUT_MS)
except Exception:
    _HTTP_OPTIONS = None


def _make_client(api_key: str):
    if _HTTP_OPTIONS is not None:
        return genai.Client(api_key=api_key, http_options=_HTTP_OPTIONS)
    return genai.Client(api_key=api_key)


def _generate_content_with_retry(client, prompt, config):
    """
    Same call as client.models.generate_content, but with a few automatic
    retries on 429/503 (model temporarily overloaded - very common on the
    free tier). After the last attempt, re-raises the real error so the
    existing except blocks handle it exactly as before (fallback content).
    """
    last_error = None

    for attempt in range(_MAX_ATTEMPTS):
        try:
            return client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=config,
            )
        except APIError as error:
            last_error = error
            status_code = getattr(error, "code", None)
            is_last_attempt = attempt == _MAX_ATTEMPTS - 1

            if status_code in _RETRYABLE_STATUS_CODES and not is_last_attempt:
                time.sleep(_RETRY_BACKOFF_SECONDS * (attempt + 1))
                continue

            raise

    raise last_error


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
- The app is bilingual (English/Macedonian), so provide EVERY recommendation
  in BOTH languages: "name"/"description" in English, and "name_mk"/
  "description_mk" as a natural (not literal word-for-word) Macedonian
  translation with the same meaning and tone.

Each recommendation must have:
- name
- name_mk
- description
- description_mk
- type

The response must be a JSON array in this format:

[
  {{
    "name": "See a dermatologist",
    "name_mk": "Посети дерматолог",
    "description": "Schedule an appointment with a dermatologist for a proper clinical evaluation and, if needed, a biopsy.",
    "description_mk": "Закажи преглед кај дерматолог за соодветна клиничка проценка и, ако е потребно, биопсија.",
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

        # name_mk/description_mk are best-effort - if Gemini omitted them,
        # fall back to the English text rather than dropping the whole
        # recommendation (an English-only card beats no card at all).
        name_mk = item.get("name_mk") or name
        description_mk = item.get("description_mk") or description

        valid_recommendations.append({
            "name": str(name).strip(),
            "name_mk": str(name_mk).strip(),
            "description": str(description).strip(),
            "description_mk": str(description_mk).strip(),
            "type": rec_type,
        })

        type_counter[rec_type] += 1

        if len(valid_recommendations) >= 6:
            break

    # GUARANTEE: there must always be at least one MEDICAL_CONSULT, even if
    # Gemini doesn't return one (or returns invalid JSON).
    if type_counter["MEDICAL_CONSULT"] == 0:
        valid_recommendations.append(get_mandatory_medical_consult())

    return valid_recommendations


def get_mandatory_medical_consult() -> Dict:
    return {
        "name": "Consult a dermatologist",
        "name_mk": "Посети дерматолог",
        "description": (
            "This result is an AI-generated estimate, not a medical diagnosis. "
            "Please consult a licensed dermatologist for accurate evaluation."
        ),
        "description_mk": (
            "Овој резултат е AI-генерирана процена, а не медицинска дијагноза. "
            "Посети лиценциран дерматолог за точна проценка."
        ),
        "type": "MEDICAL_CONSULT",
    }


def get_fallback_recommendations(condition_name: str, severity: str) -> List[Dict]:
    fallback = [get_mandatory_medical_consult()]

    fallback.append({
        "name": "Monitor for changes",
        "name_mk": "Следи ги промените",
        "description": (
            f"Keep track of any changes in size, shape, or color of the area "
            f"associated with {condition_name}, and take a dated photo for comparison."
        ),
        "description_mk": (
            f"Следи ги промените во големина, облик или боја на подрачјето "
            f"поврзано со {condition_name}, и направи датирана фотографија за споредба."
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

    prompt = build_recommendation_prompt(
        condition_name=condition_name,
        severity=severity,
    )

    try:
        client = _make_client(api_key)
        response = _generate_content_with_retry(
            client,
            prompt,
            types.GenerateContentConfig(
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


# ---------------------------------------------------------------------------
# CHAT (Q&A for a specific analysis)
#
# Unlike generate_recommendations_with_gemini (called ONCE per condition and
# cached in the database via ConditionRecommendation), the answers here are
# NOT cached - each question is personal and different, so Gemini is called
# on every question. The same safety rules apply: no diagnosis, no specific
# medications/doses, always refer anything personal to a dermatologist.
# ---------------------------------------------------------------------------

CHAT_ANSWER_FALLBACK = (
    "Sorry, I couldn't generate an answer right now. For any questions "
    "about this result, please consult a licensed dermatologist."
)


def build_chat_prompt(
    condition_name: str,
    severity: str,
    description: str,
    history: List[Dict],
    question: str,
) -> str:
    history_lines = []
    for message in history:
        speaker = "User" if message.get("role") == "USER" else "Assistant"
        history_lines.append(f"{speaker}: {message.get('content', '')}")
    history_text = "\n".join(history_lines) if history_lines else "(no previous messages)"

    return f"""
You are a dermatology information assistant answering a user's follow-up
question about an AI-predicted skin condition detected from a photo in the
DermaScanAI app.

Condition: {condition_name}
Severity category: {severity}
General description: {description or "N/A"}

Rules:
- You are NOT a doctor. Never claim to provide a medical diagnosis, never
  state with certainty what the user's lesion is, never recommend specific
  medications, dosages, or personalized treatment plans.
- Only answer questions related to this skin condition, general dermatology,
  or skin health. If the question is unrelated to these topics, politely
  decline and redirect the user back to the topic.
- ALWAYS answer in the same language the user's question below is written
  in (e.g. if it's in Macedonian, answer in Macedonian; if English, answer
  in English), regardless of what language the condition name/description
  above are in.
- Keep answers concise and in plain, accessible language (roughly 2-5
  sentences).
- If the question implies urgency (bleeding, rapid change, pain) or the
  severity category is HIGH, clearly recommend seeing a dermatologist soon.
- Always keep in mind this is general educational information, not
  personalized medical advice, and the AI prediction itself is only an
  estimate, not a confirmed diagnosis.
- Respond with plain text only - no JSON, no markdown formatting.

Conversation so far:
{history_text}

New user question: {question}
"""


def generate_chat_answer(
    condition_name: str,
    severity: str,
    description: str,
    history: List[Dict],
    question: str,
) -> str:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing. Check your .env file.")

    prompt = build_chat_prompt(
        condition_name=condition_name,
        severity=severity,
        description=description,
        history=history,
        question=question,
    )

    try:
        client = _make_client(api_key)
        response = _generate_content_with_retry(
            client,
            prompt,
            types.GenerateContentConfig(temperature=0.4),
        )

        text = (response.text or "").strip()
        return text if text else CHAT_ANSWER_FALLBACK

    except APIError as error:
        print(f"Gemini API error (chat): {error}")
        return CHAT_ANSWER_FALLBACK

    except Exception as error:
        print(f"Unexpected Gemini chat error: {error}")
        return CHAT_ANSWER_FALLBACK
