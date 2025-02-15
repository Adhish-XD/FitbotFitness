from django.core.management.base import BaseCommand
from workouts.models import Workout
import random
from datetime import datetime

class Command(BaseCommand):
    help = 'Generates sample workouts for different activity levels'

    def handle(self, *args, **kwargs):
        # Sample workout data
        workout_templates = {
            'beginner': [
                {
                    'name': 'Basic Bodyweight Circuit',
                    'description': 'A simple circuit of basic bodyweight exercises perfect for beginners.',
                    'duration': 30,
                    'difficulty': 'beginner'
                },
                {
                    'name': 'Chair Workout',
                    'description': 'Gentle exercises using a chair for support and stability.',
                    'duration': 25,
                    'difficulty': 'beginner'
                },
                {
                    'name': 'Walking Workout',
                    'description': 'A combination of walking and light stretching exercises.',
                    'duration': 40,
                    'difficulty': 'beginner'
                }
            ],
            'intermediate': [
                {
                    'name': 'Full Body Strength',
                    'description': 'A balanced workout targeting all major muscle groups.',
                    'duration': 45,
                    'difficulty': 'intermediate'
                },
                {
                    'name': 'HIIT Cardio',
                    'description': 'High-intensity interval training with cardio exercises.',
                    'duration': 35,
                    'difficulty': 'intermediate'
                },
                {
                    'name': 'Core Power',
                    'description': 'Focus on building core strength and stability.',
                    'duration': 40,
                    'difficulty': 'intermediate'
                }
            ],
            'advanced': [
                {
                    'name': 'Advanced Circuit Training',
                    'description': 'Challenging circuit combining strength and cardio.',
                    'duration': 50,
                    'difficulty': 'advanced'
                },
                {
                    'name': 'Power Lifting',
                    'description': 'Heavy lifting focused on major compound movements.',
                    'duration': 60,
                    'difficulty': 'advanced'
                },
                {
                    'name': 'Elite Endurance',
                    'description': 'High-intensity endurance training for advanced athletes.',
                    'duration': 55,
                    'difficulty': 'advanced'
                }
            ]
        }

        # Fitness goals
        fitness_goals = ['weight_loss', 'muscle_gain', 'endurance', 'flexibility', 'strength']

        # Generate 100 workouts for each activity level
        for activity_level in ['beginner', 'intermediate', 'advanced']:
            for i in range(100):
                # Select a random template for this level
                template = random.choice(workout_templates[activity_level])
                
                # Create variations
                workout_name = f"{template['name']} #{i+1}"
                workout_description = f"{template['description']} This variation focuses on {random.choice(['upper body', 'lower body', 'full body', 'core', 'cardio'])}."
                
                # Randomly adjust duration by ±5 minutes
                duration = template['duration'] + random.randint(-5, 5)
                duration = max(20, min(90, duration))  # Keep between 20-90 minutes
                
                # Create the workout
                Workout.objects.create(
                    name=workout_name,
                    description=workout_description,
                    duration=duration,
                    difficulty=template['difficulty'],
                    fitness_goal=random.choice(fitness_goals),
                    activity_level=activity_level
                )

        self.stdout.write(self.style.SUCCESS('Successfully generated 300 sample workouts!')) 