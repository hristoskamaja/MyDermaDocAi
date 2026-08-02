from django.urls import path

from . import views

urlpatterns = [
    # Skin conditions
    path("conditions/", views.conditions_collection, name="conditions_collection"),
    path("conditions/<int:id>/", views.condition_detail, name="condition_detail"),
    path("conditions/<int:id>/recommendations/", views.condition_recommendations, name="condition_recommendations"),
    path("conditions/<int:id>/recommendations/add/", views.add_recommendation_to_condition, name="add_recommendation_to_condition"),
    path("conditions/<int:id>/recommendations/<int:recommendation_id>/", views.remove_recommendation_from_condition, name="remove_recommendation_from_condition"),

    # Recommendations
    path("recommendations/", views.recommendations_collection, name="recommendations_collection"),
    path("recommendations/<int:id>/", views.recommendation_detail, name="recommendation_detail"),
]
