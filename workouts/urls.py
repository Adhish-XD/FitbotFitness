from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.workouts_view, name='workouts'),
    path('complete/<int:workout_id>/', views.complete_workout, name='complete_workout'),
    path('get_new_recommendations/<int:current_workout_id>/', views.get_new_recommendations, name='get_new_recommendations'),
    path('stats/', views.workout_stats, name='workout_stats'),
] 