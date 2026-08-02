"""
skin_model_service.py

Инференца сервис за класификација на кожни лезии.

>>> МЕСТО КАДЕ ВЛЕГУВА ТВОЈОТ НАТРЕНИРАН МОДЕЛ <<<

Откако ќе го извршиш skin_disease_training.ipynb во Google Colab и ќе ги
симнеш `skin_model.pt` и `label_converter.json`, стави ги вака:

    analyses/
        services/
            ai_model/
                skin_model.pt          <-- ТУКА (моделот, ~40-50MB)
            label_converter.json       <-- ТУКА (едно ниво погоре, покрај овој фајл)
            skin_model_service.py      <-- (овој фајл, веќе постои)
            gemini_service.py

Додека тие два фајла ги нема, predict_skin_condition() ќе фрли
SkinModelPredictionError со јасна порака - тоа е нормално и очекувано пред
да го натренираш моделот. Останатиот дел од бекендот (views, urls, admin)
може да се тестира и без моделот - само /scan-skin/ endpoint-от ќе враќа
грешка додека не го додадеш .pt фајлот.
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

IMAGE_SIZE = 244  # мора да се совпаѓа со трансформациите користени при тренирање

# Ако largest-probability предвидувањето е под овој праг, го означуваме
# резултатот како несигурен наместо да тврдиме конкретна дијагноза.
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
    # weights=None бидејќи ги вчитуваме сопствените тежини од .pt подолу.
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
    Прима слика (file path или file-like object од request.FILES) и враќа:

    {
        "condition_key": "melanoma",        # мора да се совпаѓа со SkinCondition.key
        "condition_name": "Melanoma",       # читливо име за прикажување
        "severity": "HIGH",                 # LOW / MEDIUM / HIGH, од label_converter.json
        "confidence": 0.87,                 # 0-1
        "is_low_confidence": False,         # True ако е под LOW_CONFIDENCE_THRESHOLD
    }

    Не враќа HEALTHY/AFFECTED бидејќи двата тренинг датасети (HAM10000,
    PAD-UFES-20) содржат само слики на лезии - моделот секогаш класифицира
    ВО еден од типовите лезии.
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
