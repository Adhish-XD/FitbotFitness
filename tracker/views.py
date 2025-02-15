from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Activity
from django.utils import timezone
from datetime import timedelta
from authapp.models import Profile
import logging
from django import db
from django.db import models

logger = logging.getLogger(__name__)

@login_required
def tracker(request):
    logger.info(f"Accessing tracker view for user {request.user.username}")
    # Get user's profile for additional stats
    profile = Profile.objects.get_or_create(user=request.user)[0]
    logger.info(f"Profile stats for tracker view - Workouts: {profile.workouts_completed}, Minutes: {profile.total_minutes}, Streak: {profile.streak}")

    if request.method == 'POST':
        try:
            activity_type = request.POST.get('activity_type')
            duration = request.POST.get('duration')
            calories = request.POST.get('calories')
            notes = request.POST.get('notes')
            workout_name = request.POST.get('workout_name', '')
            workout_difficulty = request.POST.get('workout_difficulty', '')

            logger.info(f"Processing activity submission - Type: {activity_type}, Duration: {duration}, Calories: {calories}")

            if activity_type and duration and calories:
                activity = Activity.objects.create(
                    user=request.user,
                    activity_type=activity_type,
                    duration=int(duration),
                    calories=int(calories),
                    notes=notes,
                    workout_name=workout_name if activity_type == 'workout' else '',
                    workout_difficulty=workout_difficulty if activity_type == 'workout' else ''
                )
                logger.info(f"Created activity: {activity}")

                # Update profile stats
                profile.workouts_completed += 1
                profile.total_minutes += int(duration)
                profile.save()
                logger.info(f"Updated profile stats - Workouts: {profile.workouts_completed}, Minutes: {profile.total_minutes}")

                messages.success(request, 'Activity logged successfully!')
            else:
                logger.warning("Missing required fields in activity submission")
                messages.error(request, 'Please fill in all required fields.')

        except Exception as e:
            logger.error(f"Error creating activity: {str(e)}", exc_info=True)
            messages.error(request, f'Error logging activity: {str(e)}')

        return redirect('tracker')

    # Handle GET request
    try:
        logger.info(f"Handling GET request for tracker view for user {request.user.username}")

        # Re-fetch recent activities to ensure latest data is displayed
        activities = Activity.get_recent_activities(user=request.user)

        logger.info(f"Fetched {len(activities)} recent activities for user {request.user.username} after re-fetch")
        for activity in activities:
            logger.debug(f"Tracker view fetched activity: {activity.activity_type}, Duration: {activity.duration}, Date: {activity.date}")

        # Get weekly stats with detailed logging
        weekly_stats = Activity.get_weekly_stats(user=request.user)
        logger.info(f"Weekly stats for user {request.user.username}: {weekly_stats}")

        # Get user's streak with detailed logging
        streak = Activity.get_streak(user=request.user)
        logger.info(f"Current streak for user {request.user.username}: {streak}")

        # Calculate total calories burned across all activities
        total_calories_burned = Activity.objects.filter(user=request.user).aggregate(total_calories=models.Sum('calories'))['total_calories'] or 0
        logger.info(f"Total calories burned for user {request.user.username}: {total_calories_burned}")

        context = {
            'activities': activities,
            'total_duration': weekly_stats['total_duration'],
            'total_calories': weekly_stats['total_calories'],
            'duration_percentage': weekly_stats['duration_percentage'],
            'calories_percentage': weekly_stats['calories_percentage'],
            'weekly_goal': weekly_stats['weekly_goal'],
            'calories_goal': weekly_stats['calories_goal'],
            'streak': streak,
            'profile': profile,
            'total_calories_burned': total_calories_burned,
        }

        logger.info(f"Rendering tracker template with context: {context}")
        return render(request, 'tracker.html', context)

    except Exception as e:
        logger.error(f"Error in tracker view: {str(e)}", exc_info=True)
        messages.error(request, 'Error loading tracker data. Please try again.')
        return render(request, 'tracker.html', {})