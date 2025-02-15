from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.template.loader import render_to_string
from authapp.models import Demographics, Profile
from .models import Workout, WorkoutVideo
from tracker.models import Activity
from django.conf import settings
import requests
from datetime import datetime
from django.db.models import Count
from django.core.cache import cache
from django.db.models import Q
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

# Create your views here.

@login_required
def workouts_view(request):
    try:
        demographics = Demographics.objects.get(user=request.user)

        # Track recommended workout IDs
        recommended_workout_ids = set()

        # Get ONE recommended workout based on user's exact demographics
        recommended_workouts_exact = Workout.objects.filter(
            fitness_goal=demographics.fitness_goal,
            activity_level=demographics.activity_level
        ).order_by('difficulty')[:1]

        if recommended_workouts_exact:
            recommended_workouts = recommended_workouts_exact
            recommended_workout_ids.update(w.id for w in recommended_workouts)
        else:
            # If no exact match, get ONE workout for the same goal (any activity level)
            recommended_workouts = Workout.objects.filter(
                fitness_goal=demographics.fitness_goal
            ).order_by('difficulty')[:1]
            recommended_workout_ids.update(w.id for w in recommended_workouts)

        # Get ONE alternative workout - filter by fitness goal, explicitly exclude recommended workouts
        alternative_workouts = Workout.objects.filter(
            fitness_goal=demographics.fitness_goal
        ).exclude(
            id__in=recommended_workout_ids  # Explicitly exclude recommended workouts
        ).order_by('difficulty')[:1]

        # If no alternative for the same goal, get ONE from other goals (still excluding recommended)
        if not alternative_workouts:
            alternative_workouts = Workout.objects.exclude(
                id__in=recommended_workout_ids  # Keep excluding recommended workouts
            ).order_by('difficulty')[:1]

        # --- Caching YouTube API results ---
        def fetch_workout_videos(workout, max_results=3):
            cache_key = f"workout_videos_{workout.id}_{max_results}"
            videos = cache.get(cache_key)
            if videos is not None:
                if videos: return videos
                # If videos is an empty list in cache, force refetch

            videos = []
            # Check if workout has pre-fetched videos (from database model)
            if hasattr(workout, 'videos') and workout.videos.exists():
                 for video in workout.videos.all()[:max_results]:
                      videos.append({
                           'title': video.title,
                           'description': video.description,
                           'video_id': video.video_id,
                           'thumbnail': '', # Assuming thumbnail might not be in your db model
                           'workout_name': workout.name
                      })
                 if videos: 
                      cache.set(cache_key, videos, 24 * 60 * 60) # Cache DB videos longer
                      return videos

            # Fallback to YouTube API if no DB videos or cache expired/empty
            search_query = f"{workout.name} {workout.get_fitness_goal_display()} workout tutorial"
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                'part': 'snippet',
                'q': search_query,
                'type': 'video',
                'maxResults': max_results,
                'key': settings.YOUTUBE_API_KEY,
                'videoEmbeddable': 'true',
                'videoDuration': 'medium'
            }
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                if data.get('items'):
                    for item in data['items']:
                        videos.append({
                            'title': item['snippet']['title'],
                            'description': item['snippet']['description'],
                            'video_id': item['id']['videoId'],
                            'thumbnail': item['snippet']['thumbnails']['high']['url'],
                            'workout_name': workout.name
                        })
            except (requests.RequestException, KeyError) as e:
                print(f"Error fetching YouTube videos: {e}")
                # Add a placeholder if API fails
                videos.append({
                    'title': f"{workout.name} Tutorial",
                    'description': "Video tutorial not available at the moment.",
                    'video_id': None,
                    'workout_name': workout.name
                })
            cache.set(cache_key, videos, 60 * 60)  # Cache API results for 1 hour
            return videos

        # Fetch videos for recommended workouts (only if there's a recommended workout)
        workout_videos = []
        if recommended_workouts:
            for workout in recommended_workouts:
                # Prefetch videos if using a database model for videos
                workout_videos.extend(fetch_workout_videos(workout, max_results=2))

        # Fetch videos for alternative workouts (only if there's an alternative workout)
        alternative_videos = []
        if alternative_workouts:
            for workout in alternative_workouts:
                # Prefetch videos if using a database model for videos
                alternative_videos.extend(fetch_workout_videos(workout, max_results=1))

        context = {
            'demographics': demographics,
            'recommended_workouts': recommended_workouts,
            'alternative_workouts': alternative_workouts,
            'workout_videos': workout_videos,
            'alternative_videos': alternative_videos,
        }
    except Demographics.DoesNotExist:
        context = {
            'demographics': None,
            'recommended_workouts': [],
            'alternative_workouts': [],
            'workout_videos': [],
            'alternative_videos': [],
        }

    return render(request, 'workouts.html', context)

@login_required
def complete_workout(request, workout_id):
    try:
        workout = get_object_or_404(Workout, id=workout_id)
        logger.info(f"Processing workout completion for user {request.user.username}, workout: {workout.name}")
        
        # Get workout details from request
        workout_name = request.POST.get('workout_name', workout.name)
        workout_duration = int(request.POST.get('workout_duration', workout.duration))
        workout_difficulty = request.POST.get('workout_difficulty', workout.get_difficulty_display())
        
        # Create a new activity log entry - ALWAYS create a new one as per user's request
        activity = Activity.objects.create(
            user=request.user,
            activity_type='workout',  # Explicitly set as workout
            duration=workout_duration,
            calories=workout_duration * 5,  # Rough estimate: 5 calories per minute
            notes=f"Completed workout: {workout_name}",
            workout_name=workout_name,
            workout_difficulty=workout_difficulty
        )
        logger.info(f"Created activity log for workout {workout_name} with duration {workout_duration} minutes, calories {activity.calories}")
        
        # Update user's profile stats
        profile, created = Profile.objects.get_or_create(user=request.user)
        old_workouts = profile.workouts_completed
        old_minutes = profile.total_minutes
        old_streak = profile.streak
        
        profile.workouts_completed += 1
        profile.total_minutes += workout_duration
        
        # Update streak - Streak logic still depends on distinct days, so keep this as is
        today = timezone.now().date()
        if profile.last_workout_date:
            days_since_last = (today - profile.last_workout_date).days
            if days_since_last == 1:  # Consecutive day
                profile.streak += 1
                logger.info(f"Streak increased to {profile.streak} days")
            elif days_since_last > 1:  # Streak broken
                profile.streak = 1
                logger.info("Streak broken, reset to 1 day")
            # Note: If days_since_last is 0 (same day), streak does not change here.
        else:
            profile.streak = 1
            logger.info("First workout, streak started at 1 day")
        
        # Update last_workout_date only if the current completion is on a new day
        if not profile.last_workout_date or today > profile.last_workout_date:
             profile.last_workout_date = today
             logger.info(f"Updated last_workout_date to {today}")
        else:
             logger.info("last_workout_date not updated as workout is on the same day.")

        profile.save()
        
        logger.info(f"Updated profile stats - Workouts: {old_workouts}->{profile.workouts_completed}, "
                   f"Minutes: {old_minutes}->{profile.total_minutes}, "
                   f"Streak: {old_streak}->{profile.streak}")
        
        # Always return success=True and a positive message if activity was created
        message_text = f'Great job! Your workout "{workout_name}" has been logged.'
        # Only show streak in the message if it increased or started
        if old_streak != profile.streak:
             message_text += f' Current streak: {profile.streak} days!'

        success_status = True # Activity is always created now

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Get updated stats for the response
            weekly_stats = Activity.get_weekly_stats(request.user)
            recent_activities = Activity.get_recent_activities(request.user)
            
            logger.info(f"Weekly stats for response: {weekly_stats}")
            logger.info(f"Recent activities count: {recent_activities.count()}")
            
            # Prepare activity data for the response
            activities_data = []
            for activity in recent_activities:
                activity_data = {
                    'type': activity.get_activity_type_display(),
                    'duration': activity.duration,
                    'calories': activity.calories,
                    'notes': activity.notes,
                    'date': activity.date.strftime('%Y-%m-%d %H:%M')
                }
                
                if activity.activity_type == 'workout':
                    activity_data.update({
                        'name': activity.workout_name,
                        'difficulty': activity.workout_difficulty,
                        'is_workout': True
                    })
                else:
                    activity_data.update({
                        'name': activity.get_activity_type_display(),
                        'is_workout': False
                    })
                
                activities_data.append(activity_data)
            
            response_data = {
                'success': success_status,
                'message': message_text,
                'stats': {
                    'weekly_stats': weekly_stats,
                    'streak': profile.streak,
                    'recent_activities': activities_data
                }
            }
            
            logger.info(f"Sending response data from complete_workout: {response_data}")
            return JsonResponse(response_data)
        else:
            messages.success(request, message_text)
            return redirect('workouts')
            
    except Exception as e:
        logger.error(f"Error completing workout: {str(e)}", exc_info=True)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f'An error occurred: {str(e)}'
            }, status=500)
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('workouts')

@login_required
def get_new_recommendations(request, current_workout_id):
    try:
        logger.info(f"Getting new recommendations for workout {current_workout_id}")
        workout_type = request.GET.get('workout_type', 'recommended')
        logger.info(f"Workout type requested: {workout_type}")

        # Initialize or get the set of shown workout IDs from session
        shown_workout_ids = set(request.session.get('shown_workout_ids', []))
        logger.info(f"Currently shown workout IDs in session: {shown_workout_ids}")

        # Add current workout to shown workouts (this is needed to exclude it from the next recommendation)
        if current_workout_id:
             shown_workout_ids.add(int(current_workout_id))
             request.session['shown_workout_ids'] = list(shown_workout_ids)
             request.session.modified = True # Ensure session is saved
             logger.info(f"Added workout {current_workout_id} to shown workouts in session for exclusion")

        # Now proceed with getting new recommendations
        demographics = Demographics.objects.get(user=request.user)
        logger.info(f"Found demographics for user: {request.user.username}")

        # Get IDs of all completed workouts
        completed_workouts_notes = Activity.objects.filter(
            user=request.user,
            notes__startswith="Completed workout:"
        ).values_list('notes', flat=True)

        # Extract workout names from notes and get their IDs
        completed_workout_names = [note.replace("Completed workout: ", "") for note in completed_workouts_notes]
        completed_workout_ids = set(Workout.objects.filter(name__in=completed_workout_names).values_list('id', flat=True))

        # Combine completed and shown workout IDs
        exclude_ids = completed_workout_ids.union(shown_workout_ids)
        logger.info(f"Excluding workouts with IDs: {exclude_ids}")

        # Get next workout based on type
        next_workout = None
        if workout_type == 'recommended':
            # Try to get exact match first (goal + activity level)
            next_workout = Workout.objects.filter(
                fitness_goal=demographics.fitness_goal,
                activity_level=demographics.activity_level
            ).exclude(
                id__in=exclude_ids
            ).order_by('?').first()

            if not next_workout:
                # If no exact match, try same goal any level
                next_workout = Workout.objects.filter(
                    fitness_goal=demographics.fitness_goal
                ).exclude(
                    id__in=exclude_ids
                ).order_by('?').first()

                if not next_workout:
                    # If still no workout, get any available workout
                    next_workout = Workout.objects.exclude(
                        id__in=exclude_ids
                    ).order_by('?').first()

        else:  # alternative workout
            # Get alternative workout for same goal, excluding shown and completed workouts
            next_workout = Workout.objects.filter(
                fitness_goal=demographics.fitness_goal
            ).exclude(
                id__in=exclude_ids
            ).order_by('?').first()

            # If no alternative for same goal, get any other workout
            if not next_workout:
                next_workout = Workout.objects.exclude(
                    id__in=exclude_ids
                ).order_by('?').first()

        # If we found a next workout, add it to shown workouts
        if next_workout:
            shown_workout_ids.add(next_workout.id)
            request.session['shown_workout_ids'] = list(shown_workout_ids)
            logger.info(f"Added workout {next_workout.id} to shown workouts")

        logger.info(f"Found next {workout_type} workout: {next_workout.id if next_workout else 'None'}")

        # Get updated stats for the response
        weekly_stats = Activity.get_weekly_stats(request.user)
        recent_activities = Activity.get_recent_activities(request.user)
        
        # Prepare activity data for the response
        activities_data = []
        for activity in recent_activities:
            activity_data = {
                'type': activity.get_activity_type_display(),
                'duration': activity.duration,
                'calories': activity.calories,
                'notes': activity.notes,
                'date': activity.date.strftime('%Y-%m-%d %H:%M')
            }
            
            if activity.activity_type == 'workout':
                activity_data.update({
                    'name': activity.workout_name,
                    'difficulty': activity.workout_difficulty,
                    'is_workout': True
                })
            else:
                activity_data.update({
                    'name': activity.get_activity_type_display(),
                    'is_workout': False
                })
            
            activities_data.append(activity_data)

        # Prepare workout data for JSON response
        workout_data = None
        if next_workout:
            workout_data = {
                'id': next_workout.id,
                'name': next_workout.name,
                'description': next_workout.description,
                'duration': next_workout.duration,
                'difficulty': next_workout.get_difficulty_display()
            }

        return JsonResponse({
            'success': True,
            'workout': workout_data,
            'no_more_workouts': not workout_data,
            'stats': {
                'weekly_stats': weekly_stats,
                'recent_activities': activities_data
            }
        })
    except Exception as e:
        logger.error(f"Error getting new recommendations: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'message': f'Error getting new recommendations: {str(e)}'
        }, status=500)

@login_required
def workout_stats(request):
    stats = Workout.objects.values('activity_level').annotate(count=Count('id'))
    return JsonResponse({
        'stats': list(stats),
        'total': Workout.objects.count()
    })
