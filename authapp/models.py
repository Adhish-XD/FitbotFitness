from django.db import models
from django.contrib.auth.models import User

# Create your models here.
# this file recreated database tables.

class Contact(models.Model):
    name=models.CharField(max_length=25)
    email=models.EmailField()
    phonenumber=models.CharField(max_length=10, help_text="10-digit phone number")
    description=models.TextField()

    def __str__(self):
        return self.email

class Demographics(models.Model):
    FITNESS_GOALS = [
        ('weight_loss', 'Weight Loss'),
        ('muscle_gain', 'Muscle Gain'),
        ('endurance', 'Improve Endurance'),
        ('general_fitness', 'General Fitness'),
    ]

    ACTIVITY_LEVELS = [
        ('sedentary', 'Sedentary (Little to no exercise)'),
        ('moderate', 'Moderate (3-4 days a week)'),
        ('active', 'Active (Daily intense workouts)'),
    ]

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.PositiveIntegerField(default=18)  # Default age to avoid null
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='other')
    height = models.FloatField(help_text="Height in cm", default=170.0)  # Default height
    weight = models.FloatField(help_text="Weight in kg", default=70.0)  # Default weight
    fitness_goal = models.CharField(max_length=20, choices=FITNESS_GOALS, default="general_fitness")
    activity_level = models.CharField(max_length=20, choices=ACTIVITY_LEVELS, default="moderate")


    def __str__(self):
        return f"{self.user.username} - {self.fitness_goal}"

class Workout(models.Model):
    FITNESS_GOALS = [
        ('weight_loss', 'Weight Loss'),
        ('muscle_gain', 'Muscle Gain'),
        ('endurance', 'Improve Endurance'),
        ('general_fitness', 'General Fitness'),
    ]

    ACTIVITY_LEVELS = [
        ('sedentary', 'Sedentary (Little to no exercise)'),
        ('moderate', 'Moderate (3-4 days a week)'),
        ('active', 'Active (Daily intense workouts)'),
    ]

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('any', 'Any'),  # For gender-neutral workouts
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    difficulty = models.CharField(max_length=50, choices=[('Beginner', 'Beginner'), ('Intermediate', 'Intermediate'), ('Advanced', 'Advanced')])
    
    fitness_goal = models.CharField(max_length=20, choices=FITNESS_GOALS, default="general_fitness")
    activity_level = models.CharField(max_length=20, choices=ACTIVITY_LEVELS, default="moderate")
    
    target_age_min = models.PositiveIntegerField(default=18)
    target_age_max = models.PositiveIntegerField(default=60)
    target_gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default="any")

    # Adding BMI categories (optional)
    target_bmi_min = models.FloatField(default=18.5, help_text="Minimum BMI for this workout")
    target_bmi_max = models.FloatField(default=30.0, help_text="Maximum BMI for this workout")

    def __str__(self):
        return f"{self.name} ({self.fitness_goal} - {self.difficulty})"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    phone = models.CharField(max_length=10, blank=True, help_text="10-digit phone number")
    location = models.CharField(max_length=100, blank=True)
    workouts_completed = models.IntegerField(default=0)
    total_minutes = models.IntegerField(default=0)
    streak = models.IntegerField(default=0)
    last_workout_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
