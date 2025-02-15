from django.contrib import admin
from .models import Workout

@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ('name', 'fitness_goal', 'activity_level', 'difficulty', 'duration')
    list_filter = ('fitness_goal', 'activity_level', 'difficulty')
    search_fields = ('name', 'description')
    list_editable = ('fitness_goal', 'activity_level', 'difficulty', 'duration')
    ordering = ('fitness_goal', 'activity_level', 'difficulty', 'name')
