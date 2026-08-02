# Lovable prompt — SkinScan AI

Copy everything below into Lovable as your starting prompt.

---

Design and build the UI for **SkinScan AI**, a health-tech application that uses an AI model to scan photos of skin and identify possible skin conditions, then gives general care recommendations. It is NOT a diagnostic tool — every result must be clearly framed as a preliminary AI estimate, not a medical diagnosis, and always encourage seeing a real dermatologist.

I need two things designed:
1. A **web admin panel** (desktop-first) used by clinic/platform admins to manage the system.
2. A **mobile app** (used by end users) to scan their skin and view results/history.

The backend (Django REST API) and data model already exist and are fixed — design around them, don't invent different data. Details below.

## Domain model (already built, do not change)

**Skin conditions** — exactly 8 categories the AI model can detect:
- Melanoma
- Basal Cell Carcinoma
- Squamous Cell Carcinoma
- Actinic Keratosis
- Seborrheic Keratosis
- Nevus (Mole)
- Dermatofibroma
- Vascular Lesion

Each condition has: `name`, `description`, `symptoms`, `severity` (LOW / MEDIUM / HIGH), `category` (BENIGN / PRECANCEROUS / MALIGNANT / INFLAMMATORY / OTHER), an optional reference image, and a list of linked recommendations.

**Recommendations** — short pieces of advice linked to a condition, each with a `type`: SELF_CARE, MEDICAL_CONSULT, or LIFESTYLE. Every condition always has at least one MEDICAL_CONSULT recommendation.

**Analysis (a single scan result)** — belongs to a user, references the detected condition, has an `image`, a `confidence` score (0–1, shown as %), an `is_low_confidence` flag (true when the model isn't sure — needs a clearly different visual treatment, like an "uncertain result" warning state), and a timestamp.

**Users** — `full_name`, `email`, `role` (ADMIN or USER).

## Web admin panel — required screens

- **Login** — email + password.
- **Dashboard** — landing page after login. Needs: total analyses, total users, conditions detected count, model accuracy rate, low-confidence rate, a trend chart of analyses over time, a condition-distribution chart, a feed of recent analyses, and top-detected conditions.
- **Conditions** — CRUD list/grid of the 8 conditions (name, key, severity, category, description), with a way to view/add/remove linked recommendations per condition.
- **Users** — CRUD list of registered users, role, join date, and a way to view a specific user's analysis history.
- **Analysis History** — all scans across all users: condition detected, confidence, low-confidence flag, date, searchable/filterable.
- **Statistics** — deeper analytics: analyses over time (7/30/90/365 day ranges), condition distribution, user growth, detection accuracy over time, top detected conditions.
- **Settings** — language toggle (the app supports English and Macedonian), theme (light/dark), notification preferences.
- **Profile** — the logged-in admin's own info + change password.

## Mobile app (end users) — required screens

- **Onboarding/Login/Register.**
- **Home** — friendly landing screen with a clear, prominent "Scan your skin" call to action (camera + upload from gallery).
- **Scan flow** — take/choose a photo → loading/analyzing state → result screen showing: condition name, confidence %, severity, a plain-language description, and the list of recommendations grouped or tagged by type (self-care / lifestyle / see a doctor). If `is_low_confidence` is true, show a distinct "uncertain — consider rescanning or seeing a professional" state instead of presenting it as a confident result.
- **History** — list of the user's past scans (thumbnail, condition, date, confidence), tappable into the full result again.
- **Profile/Settings** — user info, change password, language, theme, logout.
- A **persistent, unobtrusive disclaimer** somewhere near every result: "AI-generated estimate — not a medical diagnosis."

## Design direction

This is a health/skincare product. Beyond that, I'm intentionally not prescribing colors, layout, or visual style — use your own design judgment for the full look and feel of both apps. Just make sure severity (LOW/MEDIUM/HIGH) and the low-confidence state are visually distinguishable from each other in whatever system you design, and that both light and dark mode are supported.
