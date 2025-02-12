from django.contrib import admin
from authapp.models import Contact,Demographics
# from unfold.admin import ModelAdmin # Not needed for basic customization

# Register your models here.
admin.site.register(Contact)

@admin.register(Demographics)
class DemographicsAdmin(admin.ModelAdmin):
    list_display = ('user', 'fitness_goal', 'activity_level', 'age', 'gender')
    list_filter = ('fitness_goal', 'activity_level', 'gender')
    search_fields = ('user__username',)