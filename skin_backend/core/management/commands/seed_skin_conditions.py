"""
python manage.py seed_skin_conditions

Ги полни 8-те SkinCondition записи што точно се совпаѓаат со class_names
од skin_disease_training.ipynb (UNIFIED_CLASSES). Изврши го ова ЕДНАШ,
пред прв пат да го тестираш /api/analyses/scan-skin/ endpoint-от -
инаку AI-то ќе врати condition_key што не постои во базата и ќе добиеш 404
(исто како во leafscan кога Plant/Disease не постои во табелата).

Описите подолу се намерно кратки placeholder-и - дотерај ги преку
Django admin или React admin панелот откако ќе провериш точни медицински
формулации (во идеална ситуација, проверени од дерматолог/медицинско лице).
"""

from django.core.management.base import BaseCommand

from core.models import SkinCondition, Severity, ConditionCategory


CONDITIONS = [
    {
        "key": "melanoma",
        "name": "Melanoma",
        "severity": Severity.HIGH,
        "category": ConditionCategory.MALIGNANT,
        "description": "Малигна лезија на пигментните клетки на кожата. Бара итен преглед кај дерматолог.",
    },
    {
        "key": "basal_cell_carcinoma",
        "name": "Basal Cell Carcinoma",
        "severity": Severity.HIGH,
        "category": ConditionCategory.MALIGNANT,
        "description": "Најчест тип на кожен карцином, бавно расте, но бара медицинска дијагноза и третман.",
    },
    {
        "key": "squamous_cell_carcinoma",
        "name": "Squamous Cell Carcinoma",
        "severity": Severity.HIGH,
        "category": ConditionCategory.MALIGNANT,
        "description": "Малигна лезија на плочестите клетки на кожата. Бара медицинска проценка.",
    },
    {
        "key": "actinic_keratosis",
        "name": "Actinic Keratosis",
        "severity": Severity.MEDIUM,
        "category": ConditionCategory.PRECANCEROUS,
        "description": "Прекарцинозна промена предизвикана од долготрајно изложување на сонце.",
    },
    {
        "key": "seborrheic_keratosis",
        "name": "Seborrheic Keratosis",
        "severity": Severity.LOW,
        "category": ConditionCategory.BENIGN,
        "description": "Доброќудна брадавичеста промена на кожата, честа кај постари лица.",
    },
    {
        "key": "nevus",
        "name": "Nevus (Mole)",
        "severity": Severity.LOW,
        "category": ConditionCategory.BENIGN,
        "description": "Обична бенигна младеж/крт. Следи промени во големина, боја или облик.",
    },
    {
        "key": "dermatofibroma",
        "name": "Dermatofibroma",
        "severity": Severity.LOW,
        "category": ConditionCategory.BENIGN,
        "description": "Доброќудна фиброзна кожна брадавица, обично безопасна.",
    },
    {
        "key": "vascular_lesion",
        "name": "Vascular Lesion",
        "severity": Severity.LOW,
        "category": ConditionCategory.BENIGN,
        "description": "Доброќудна промена поврзана со крвни садови во кожата.",
    },
]


class Command(BaseCommand):
    help = "Seed-ира ги 8-те SkinCondition записи што се совпаѓаат со тренинг notebook-от."

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0

        for item in CONDITIONS:
            obj, created = SkinCondition.objects.update_or_create(
                key=item["key"],
                defaults={
                    "name": item["name"],
                    "severity": item["severity"],
                    "category": item["category"],
                    "description": item["description"],
                },
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Готово. Нови: {created_count}, ажурирани: {updated_count}."
            )
        )
