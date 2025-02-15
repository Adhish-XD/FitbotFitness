from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class Activity(models.Model):
    ACTIVITY_TYPES = [
        ('cardio', 'Cardio'),
        ('strength', 'Strength Training'),
        ('flexibility', 'Flexibility'),
        ('workout', 'Workout'),  # New type for logged workouts
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    duration = models.IntegerField(help_text="Duration in minutes")
    calories = models.IntegerField(help_text="Calories burned")
    notes = models.TextField(blank=True)
    date = models.DateTimeField(default=timezone.now)
    workout_name = models.CharField(max_length=100, blank=True, help_text="Name of the workout if activity_type is 'workout'")
    workout_difficulty = models.CharField(max_length=20, blank=True, help_text="Difficulty level of the workout")
    
    def __str__(self):
        if self.activity_type == 'workout':
            return f"{self.user.username} - {self.workout_name} - {self.date.strftime('%Y-%m-%d')}"
        return f"{self.user.username} - {self.activity_type} - {self.date.strftime('%Y-%m-%d')}"
    
    class Meta:
        ordering = ['-date']
        verbose_name_plural = "Activities"

    @classmethod
    def get_weekly_stats(cls, user):
        """Get weekly statistics for a user"""
        today = timezone.now()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=7)
        
        weekly_activities = cls.objects.filter(
            user=user,
            date__gte=week_start,
            date__lt=week_end
        )
        
        total_duration = weekly_activities.aggregate(models.Sum('duration'))['duration__sum'] or 0
        total_calories = weekly_activities.aggregate(models.Sum('calories'))['calories__sum'] or 0
        
        # Calculate weekly goals (example: 300 minutes per week)
        weekly_goal = 300
        duration_percentage = min(100, (total_duration / weekly_goal) * 100)
        
        # Calculate calories goal (example: 2000 calories per week)
        calories_goal = 2000
        calories_percentage = min(100, (total_calories / calories_goal) * 100)
        
        return {
            'total_duration': total_duration,
            'total_calories': total_calories,
            'duration_percentage': duration_percentage,
            'calories_percentage': calories_percentage,
            'weekly_goal': weekly_goal,
            'calories_goal': calories_goal
        }

    @classmethod
    def get_streak(cls, user):
        """Calculate user's current workout streak"""
        try:
            today = timezone.now().date()
            streak = 0
            current_date = today
            
            logger.debug(f"Calculating streak for user {user.username} starting from {today}")
            
            # Get all activities for the user, ordered by date
            activities = cls.objects.filter(
                user=user
            ).order_by('-date').values_list('date__date', flat=True).distinct()
            
            # Convert to list and sort in reverse chronological order
            activity_dates = sorted(list(activities), reverse=True)
            
            if not activity_dates:
                logger.debug(f"No activities found for user {user.username}")
                return 0
            
            # Check if the most recent activity was today or yesterday
            if activity_dates[0] == today:
                streak = 1
                current_date = today - timedelta(days=1)
            elif activity_dates[0] == today - timedelta(days=1):
                streak = 1
                current_date = today - timedelta(days=2)
            else:
                logger.debug(f"Most recent activity was on {activity_dates[0]}, no current streak")
                return 0
            
            # Check consecutive days
            for date in activity_dates[1:]:
                if date == current_date:
                    streak += 1
                    current_date -= timedelta(days=1)
                    logger.debug(f"Found activity on {date}, streak is now {streak}")
                else:
                    logger.debug(f"Gap found at {date}, streak ends at {streak}")
                    break
            
            logger.info(f"Final streak for user {user.username}: {streak} days")
            return streak
        except Exception as e:
            logger.error(f"Error calculating streak: {str(e)}", exc_info=True)
            return 0

    @classmethod
    def get_recent_activities(cls, user, limit=5):
        """Get user's most recent activities"""
        # Order by date descending, then by primary key descending as a tie-breaker
        return cls.objects.filter(user=user).order_by('-date', '-pk')[:limit] 