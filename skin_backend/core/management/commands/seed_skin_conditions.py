"""
python manage.py seed_skin_conditions

Fills the 8 SkinCondition records that exactly match the class_names from
skin_disease_training.ipynb (UNIFIED_CLASSES). Run this ONCE, before you
first test the /api/analyses/scan-skin/ endpoint - otherwise the AI will
return a condition_key that doesn't exist in the database and you'll get
a 404 (same as in leafscan when Plant/Disease doesn't exist in the table).

The symptoms and `treatment_overview` fields are general, educational
information (largely consistent with what sources like Mayo Clinic /
DermNet describe) - NOT personalized medical advice, and they don't
mention specific medications/doses. Always review/adjust them through the
Django admin or React admin panel before production use (ideally, verified
by a dermatologist).
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
        "symptoms": (
            "Младеж или дамка што е асиметрична, со неправилни/замаглени рабови, "
            "со повеќе бои во иста лезија (кафеава, црна, розева, сина), пречник "
            "поголем од 6мм, и/или се менува во големина, облик или боја со текот "
            "на времето. Може да чеша, крвави или да не заздравува."
        ),
        "treatment_overview": (
            "Дерматолозите најчесто ја отстрануваат лезијата хируршки (ексцизија), "
            "понекогаш со проверка на најблиските лимфни јазли. Кај понапредни "
            "случаи, третманот може да вклучи имунотерапија или таргетирана "
            "терапија. Точниот пристап зависи од длабочината и стадиумот и го "
            "одредува дерматолог/онколог по биопсија."
        ),
    },
    {
        "key": "basal_cell_carcinoma",
        "name": "Basal Cell Carcinoma",
        "severity": Severity.HIGH,
        "category": ConditionCategory.MALIGNANT,
        "description": "Најчест тип на кожен карцином, бавно расте, но бара медицинска дијагноза и третман.",
        "symptoms": (
            "Сјаен/восочен испакнат чвор, рамна лузна-слична лезија со кафеава или "
            "телесна боја, или рана што крвави, коричи и потоа заздравува па пак "
            "се враќа. Најчесто на делови изложени на сонце (лице, уши, врат)."
        ),
        "treatment_overview": (
            "Обично се третира со хируршко отстранување (вклучувајќи Mohs хирургија "
            "за прецизно чување на здраво ткиво). Помали лезии понекогаш се третираат "
            "со криотерапија, топикална терапија или радиотерапија. Изборот го прави "
            "дерматолог според големината и локацијата."
        ),
    },
    {
        "key": "squamous_cell_carcinoma",
        "name": "Squamous Cell Carcinoma",
        "severity": Severity.HIGH,
        "category": ConditionCategory.MALIGNANT,
        "description": "Малигна лезија на плочестите клетки на кожата. Бара медицинска проценка.",
        "symptoms": (
            "Цврст црвеникав чвор, рамна лезија со лушпеста/крастава површина, или "
            "рана/язва што не заздравува со месеци. Може да личи и на брадавица. "
            "Најчесто на делови изложени на сонце."
        ),
        "treatment_overview": (
            "Најчест пристап е хируршко отстранување (ексцизија или Mohs хирургија); "
            "кај поголеми или тешко достапни лезии може да се препорача радиотерапија. "
            "Конечната одлука ја носи дерматолог/онколог по проценка на стадиумот."
        ),
    },
    {
        "key": "actinic_keratosis",
        "name": "Actinic Keratosis",
        "severity": Severity.MEDIUM,
        "category": ConditionCategory.PRECANCEROUS,
        "description": "Прекарцинозна промена предизвикана од долготрајно изложување на сонце.",
        "symptoms": (
            "Груба, сува, лушпеста дамка (обично под 2см), розева, црвеникава или "
            "кафеава, на кожа изложена на сонце (лице, скалп, раце). Може да чеша "
            "или пецка, а понекогаш е полесно да се почувствува отколку да се види."
        ),
        "treatment_overview": (
            "Дерматолозите вообичаено користат криотерапија (замрзнување), топикална "
            "терапија или фотодинамична терапија, во зависност од бројот и локацијата "
            "на лезиите. Без третман, мал процент можат да прогресираат кон squamous "
            "cell carcinoma, затоа се препорачува преглед."
        ),
    },
    {
        "key": "seborrheic_keratosis",
        "name": "Seborrheic Keratosis",
        "severity": Severity.LOW,
        "category": ConditionCategory.BENIGN,
        "description": "Доброќудна брадавичеста промена на кожата, честа кај постари лица.",
        "symptoms": (
            "Восочна, „залепена” дамка со остар раб, кафеава/црна/бежова боја, "
            "тркалезна или овална, со малку рапава/брадавичеста површина. Расте "
            "бавно и обично не боли."
        ),
        "treatment_overview": (
            "Бидејќи е бенигна, обично не е потребен третман. Ако лезијата се "
            "иритира, чеша или пациентот сака отстранување од естетски причини, "
            "дерматолог може да ја отстрани со криотерапија, кир(е)тажа или ласер."
        ),
    },
    {
        "key": "nevus",
        "name": "Nevus (Mole)",
        "severity": Severity.LOW,
        "category": ConditionCategory.BENIGN,
        "description": "Обична бенигна младеж/крт. Следи промени во големина, боја или облик.",
        "symptoms": (
            "Мала, рамномерно обоена дамка (кафеава, црна или телесна боја), со "
            "јасно дефиниран раб и стабилен изглед со текот на времето. Обична "
            "младеж не боли и не крвави."
        ),
        "treatment_overview": (
            "Обичните младежи не бараат третман. Отстранување се разгледува само "
            "ако младежот покаже промени (асиметрија, неправилен раб, промена на "
            "боја/големина) или по лична преференција - секогаш по проценка на "
            "дерматолог."
        ),
    },
    {
        "key": "dermatofibroma",
        "name": "Dermatofibroma",
        "severity": Severity.LOW,
        "category": ConditionCategory.BENIGN,
        "description": "Доброќудна фиброзна кожна брадавица, обично безопасна.",
        "symptoms": (
            "Мал, цврст чвор (обично на нозете), розева, кафеава или црвеникава "
            "боја. Карактеристично се повлекува навнатре кога ќе се притисне од "
            "страните („dimple sign”). Може благо да чеша, но обично не боли."
        ),
        "treatment_overview": (
            "Најчесто не бара третман. Хируршко отстранување се разгледува само ако "
            "лезијата пречи, чеша постојано или пациентот сака да ја отстрани - по "
            "проценка на дерматолог."
        ),
    },
    {
        "key": "vascular_lesion",
        "name": "Vascular Lesion",
        "severity": Severity.LOW,
        "category": ConditionCategory.BENIGN,
        "description": "Доброќудна промена поврзана со крвни садови во кожата.",
        "symptoms": (
            "Црвена или темноцрвена/виолетова дамка предизвикана од крвни садови во "
            "кожата, рамна или благо издигната. Кај некои типови бојата бледнее "
            "привремено при притисок."
        ),
        "treatment_overview": (
            "Најчесто не е потребен третман. Ако лезијата пречи функционално или "
            "естетски, дерматолог може да препорача ласер терапија; пристапот "
            "зависи од типот и длабочината на садовите."
        ),
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
                    "symptoms": item["symptoms"],
                    "treatment_overview": item["treatment_overview"],
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
