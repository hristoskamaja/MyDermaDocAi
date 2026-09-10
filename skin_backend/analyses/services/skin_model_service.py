"""
skin_model_service.py

Inference service for skin lesion classification.

>>> WHERE YOUR TRAINED MODEL GOES <<<

After you run skin_disease_training.ipynb in Google Colab and download
`skin_model.pt` and `label_converter.json`, place them like this:

    analyses/
        services/
            ai_model/
                skin_model.pt          <-- HERE (the model, ~40-50MB)
            label_converter.json       <-- HERE (one level up, next to this file)
            skin_model_service.py      <-- (this file, already exists)
            gemini_service.py

While those two files don't exist yet, predict_skin_condition() will raise
a SkinModelPredictionError with a clear message - that's normal and
expected before you train the model. The rest of the backend (views, urls,
admin) can be tested without the model - only the /scan-skin/ endpoint
will return an error until you add the .pt file.
"""

import json
from pathlib import Path
from typing import Mapping, Optional

import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image


MODEL_DIR = Path(__file__).resolve().parent / "ai_model"
MODEL_PATH = MODEL_DIR / "skin_model.pt"
LABEL_CONVERTER_PATH = Path(__file__).resolve().parent / "label_converter.json"

IMAGE_SIZE = 244  # must match the transforms used during training

# If the largest-probability prediction is below this threshold, we mark
# the result as uncertain instead of claiming a definitive diagnosis.
LOW_CONFIDENCE_THRESHOLD = 0.45

_cached_model: Optional[nn.Module] = None
_cached_device: Optional[str] = None
_cached_class_names: Optional[list] = None
_cached_label_converter: Optional[Mapping[str, dict]] = None


class SkinModelPredictionError(Exception):
    pass


def _load_label_converter() -> Mapping[str, dict]:
    global _cached_label_converter

    if _cached_label_converter is not None:
        return _cached_label_converter

    if not LABEL_CONVERTER_PATH.exists():
        _cached_label_converter = {}
        return _cached_label_converter

    try:
        data = json.loads(LABEL_CONVERTER_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SkinModelPredictionError(
            f"label_converter.json не е валиден JSON: {exc}"
        ) from exc

    _cached_label_converter = data if isinstance(data, dict) else {}
    return _cached_label_converter


def _build_model(num_classes: int) -> nn.Module:
    # weights=None because we load our own weights from .pt below.
    model = models.efficientnet_b3(weights=None)
    in_features = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(in_features, num_classes)
    return model


def _load_model(device: str) -> nn.Module:
    global _cached_model, _cached_device, _cached_class_names

    if _cached_model is not None and _cached_device == device:
        return _cached_model

    if not MODEL_PATH.exists():
        raise SkinModelPredictionError(
            f"Моделот не е најден на патеката: {MODEL_PATH}. "
            "Прво изврши го skin_disease_training.ipynb и стави го "
            "skin_model.pt во analyses/services/ai_model/."
        )

    bundle = torch.load(str(MODEL_PATH), map_location=device)

    if not isinstance(bundle, dict) or "state_dict" not in bundle or "class_names" not in bundle:
        raise SkinModelPredictionError(
            "Неочекуван формат на skin_model.pt. Очекувано: "
            '{"state_dict": ..., "class_names": [...]}. '
            "Провери дали моделот е зачуван од training notebook-от."
        )

    class_names = bundle["class_names"]
    state_dict = bundle["state_dict"]

    model = _build_model(num_classes=len(class_names))
    model.load_state_dict(state_dict)
    model = model.to(device)
    model.eval()

    _cached_model = model
    _cached_device = device
    _cached_class_names = class_names

    return model


def _build_transform() -> transforms.Compose:
    return transforms.Compose(
        [
            transforms.Resize(IMAGE_SIZE),
            transforms.CenterCrop(IMAGE_SIZE),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225],
            ),
        ]
    )


def predict_skin_condition(image_file) -> dict:
    """
    Takes an image (file path or file-like object from request.FILES) and
    returns:

    {
        "condition_key": "melanoma",        # must match SkinCondition.key
        "condition_name": "Melanoma",       # human-readable display name
        "severity": "HIGH",                 # LOW / MEDIUM / HIGH, from label_converter.json
        "confidence": 0.87,                 # 0-1
        "is_low_confidence": False,         # True if below LOW_CONFIDENCE_THRESHOLD
    }

    Does not return HEALTHY/AFFECTED because both training datasets
    (HAM10000, PAD-UFES-20) only contain images of lesions - the model
    always classifies INTO one of the lesion types.
    """

    try:
        if hasattr(image_file, "read"):
            image = Image.open(image_file)
        else:
            image_path = Path(image_file)
            if not image_path.exists():
                raise SkinModelPredictionError(f"Сликата не е најдена: {image_path}")
            image = Image.open(image_path)

        image = image.convert("RGB")

        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = _load_model(device)

        transform = _build_transform()
        input_tensor = transform(image).unsqueeze(0).to(device)

        with torch.no_grad():
            output = model(input_tensor)
            probabilities = torch.softmax(output, dim=1)
            confidence, predicted_idx = torch.max(probabilities, dim=1)

        predicted_index = int(predicted_idx.item())
        condition_key = _cached_class_names[predicted_index]
        confidence_value = float(confidence.item())

        label_converter = _load_label_converter()
        info = label_converter.get(condition_key, {})

        return {
            "condition_key": condition_key,
            "condition_name": info.get("display_name", condition_key.replace("_", " ").title()),
            "severity": info.get("severity", "MEDIUM"),
            "confidence": confidence_value,
            "is_low_confidence": confidence_value < LOW_CONFIDENCE_THRESHOLD,
        }

    except SkinModelPredictionError:
        raise

    except Exception as exc:
        raise SkinModelPredictionError(f"Предвидувањето не успеа: {exc}") from exc
