# DermaScanAI

AI-assisted skin condition scanning app: a Django REST backend serving a locally-trained
image classifier (EfficientNet-B3), a React admin panel, and a Flutter mobile app for
end users. Google Gemini is used only to generate general care-recommendation text after
the local model has already produced a prediction — it never performs the classification
itself.

This is a preliminary-estimate tool, not a medical diagnosis. Every result should point
the user toward a licensed dermatologist for confirmation.

## Structure

```
skin_backend/    Django REST API (auth, conditions, analyses, analytics, AI inference)
skin_web/        React admin panel (manage conditions/users, review analyses, statistics)
skin_mobile/     Flutter app for end users (scan a photo, see results + recommendations)
skin_disease_training.ipynb   Google Colab notebook to train/retrain the classifier
```

## Setup

### Backend (`skin_backend/`)

```
cd skin_backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env          # then fill in real values
python manage.py migrate
python manage.py seed_skin_conditions
python manage.py createsuperuser
python manage.py runserver
```

The AI model is not included in this repo (see `.gitignore` — it's a large binary
artifact, not source code). Train it yourself via `skin_disease_training.ipynb` in
Google Colab, then place the two output files here:

- `skin_backend/analyses/services/ai_model/skin_model.pt`
- `skin_backend/analyses/services/label_converter.json`

Until those exist, every other endpoint works normally except `/api/analyses/scan-skin/`,
which will return a clear `502` explaining the model is missing.

### Web admin (`skin_web/`)

```
cd skin_web
npm install
npm start
```

### Mobile app (`skin_mobile/`)

```
cd skin_mobile
flutter pub get
```

Set the backend base URL in `lib/services/api_config.dart`:
- Android emulator: `http://10.0.2.2:8000/api` (default)
- Physical device: your computer's LAN IP, e.g. `http://192.168.1.23:8000/api`
  (and run Django with `python manage.py runserver 0.0.0.0:8000`, same WiFi network)

Open the folder in Android Studio and run.
