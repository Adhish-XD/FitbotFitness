from django.db import migrations

def add_sample_workouts(apps, schema_editor):
    Workout = apps.get_model('workouts', 'Workout')
    
    # Weight Loss Workouts
    Workout.objects.create(
        name="Cardio Blast",
        description="High-intensity cardio workout focusing on fat burning and endurance. Includes jumping jacks, mountain climbers, and burpees.",
        duration=30,
        difficulty='beginner',
        fitness_goal='weight_loss',
        activity_level='moderate'
    )
    
    Workout.objects.create(
        name="HIIT Circuit",
        description="High-Intensity Interval Training circuit with alternating periods of intense exercise and rest.",
        duration=45,
        difficulty='intermediate',
        fitness_goal='weight_loss',
        activity_level='active'
    )

    Workout.objects.create(
        name="Fat Burning Dance",
        description="Fun dance-based cardio workout that burns calories while improving coordination.",
        duration=40,
        difficulty='beginner',
        fitness_goal='weight_loss',
        activity_level='moderate'
    )

    Workout.objects.create(
        name="Tabata Training",
        description="20 seconds of intense exercise followed by 10 seconds of rest, perfect for maximum calorie burn.",
        duration=35,
        difficulty='advanced',
        fitness_goal='weight_loss',
        activity_level='active'
    )
    
    # Muscle Gain Workouts
    Workout.objects.create(
        name="Upper Body Strength",
        description="Focus on chest, back, shoulders, and arms with progressive overload exercises.",
        duration=60,
        difficulty='intermediate',
        fitness_goal='muscle_gain',
        activity_level='moderate'
    )
    
    Workout.objects.create(
        name="Lower Body Power",
        description="Intensive leg workout focusing on squats, deadlifts, and lunges for muscle growth.",
        duration=60,
        difficulty='advanced',
        fitness_goal='muscle_gain',
        activity_level='active'
    )

    Workout.objects.create(
        name="Full Body Power",
        description="Compound exercises targeting multiple muscle groups for maximum muscle growth.",
        duration=75,
        difficulty='advanced',
        fitness_goal='muscle_gain',
        activity_level='active'
    )

    Workout.objects.create(
        name="Arms & Shoulders",
        description="Isolated exercises for biceps, triceps, and shoulders with proper form guidance.",
        duration=45,
        difficulty='intermediate',
        fitness_goal='muscle_gain',
        activity_level='moderate'
    )
    
    # Endurance Workouts
    Workout.objects.create(
        name="Endurance Run",
        description="Long-distance running workout to improve cardiovascular endurance and stamina.",
        duration=45,
        difficulty='intermediate',
        fitness_goal='endurance',
        activity_level='moderate'
    )
    
    Workout.objects.create(
        name="Swimming Endurance",
        description="Swimming workout focusing on different strokes and techniques to build endurance.",
        duration=60,
        difficulty='advanced',
        fitness_goal='endurance',
        activity_level='active'
    )

    Workout.objects.create(
        name="Cycling Endurance",
        description="Long-distance cycling workout to build leg endurance and cardiovascular fitness.",
        duration=75,
        difficulty='intermediate',
        fitness_goal='endurance',
        activity_level='moderate'
    )

    Workout.objects.create(
        name="Circuit Endurance",
        description="High-rep circuit training focusing on muscular endurance and stamina.",
        duration=50,
        difficulty='intermediate',
        fitness_goal='endurance',
        activity_level='active'
    )
    
    # General Fitness Workouts
    Workout.objects.create(
        name="Full Body Circuit",
        description="Complete body workout targeting all major muscle groups with a mix of cardio and strength exercises.",
        duration=45,
        difficulty='beginner',
        fitness_goal='general_fitness',
        activity_level='moderate'
    )
    
    Workout.objects.create(
        name="Core Strength",
        description="Focus on building core strength with planks, crunches, and stability exercises.",
        duration=30,
        difficulty='intermediate',
        fitness_goal='general_fitness',
        activity_level='active'
    )

    Workout.objects.create(
        name="Flexibility & Balance",
        description="Yoga and stretching exercises to improve flexibility and balance.",
        duration=40,
        difficulty='beginner',
        fitness_goal='general_fitness',
        activity_level='moderate'
    )

    Workout.objects.create(
        name="Mixed Martial Arts",
        description="Basic MMA movements combining cardio, strength, and coordination.",
        duration=60,
        difficulty='advanced',
        fitness_goal='general_fitness',
        activity_level='active'
    )

def remove_sample_workouts(apps, schema_editor):
    Workout = apps.get_model('workouts', 'Workout')
    Workout.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('workouts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_sample_workouts, remove_sample_workouts),
    ] 