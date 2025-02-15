from django.db import models

# Create your models here.

class Workout(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    duration = models.IntegerField(help_text="Duration in minutes")
    difficulty = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ])
    fitness_goal = models.CharField(max_length=20, choices=[
        ('weight_loss', 'Weight Loss'),
        ('muscle_gain', 'Muscle Gain'),
        ('endurance', 'Improve Endurance'),
        ('general_fitness', 'General Fitness'),
    ])
    activity_level = models.CharField(max_length=20, choices=[
        ('sedentary', 'Sedentary'),
        ('moderate', 'Moderate'),
        ('active', 'Active'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class WorkoutVideo(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    video_id = models.CharField(max_length=20, help_text="YouTube video ID")
    duration = models.CharField(max_length=20)
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name='videos')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
