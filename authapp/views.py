from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from authapp.models import Contact,Demographics
from django.contrib.auth.decorators import login_required  
from .models import Profile
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .validators import CustomPasswordValidator
import re
import os
import logging

logger = logging.getLogger(__name__)

def validate_password(password):
    """Helper function to validate password requirements"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."
    
    if not re.search(r'[!@#$%^&*]', password):
        return False, "Password must contain at least one special character (!@#$%^&*)."
    
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number."
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter."
    
    return True, ""

def home(request):
    return render(request,"index.html")

def signup(request):
    if request.method=="POST":
        username=request.POST.get('usernumber')
        email=request.POST.get('email')
        pass1=request.POST.get('pass1')
        pass2=request.POST.get('pass2')
      
        if len(username)>10 or len(username)<10:
            messages.error(request,"Phone Number Must be 10 Digits")
            return redirect('/signup')

        if pass1!=pass2:
            messages.error(request,"Passwords do not match")
            return redirect('/signup')
        
        # Validate password requirements
        is_valid, error_message = validate_password(pass1)
        if not is_valid:
            messages.error(request, error_message)
            return redirect('/signup')
       
        try:
            if User.objects.get(username=username):
                messages.error(request,"Phone Number is already registered")
                return redirect('/signup')
        except Exception as identifier:
            pass
        
        try:
            if User.objects.get(email=email):
                messages.error(request,"Email is already registered")
                return redirect('/signup')
        except Exception as identifier:
            pass
        
        try:
            # Create user with validated password
            myuser = User.objects.create_user(username, email, pass1)
            myuser.save()
            messages.success(request, "Account created successfully! Please login.")
            return redirect('/login')
        except Exception as e:
            messages.error(request, f"Error creating account: {str(e)}")
            return redirect('/signup')
        
    return render(request, "signup.html")

def handlelogin(request):
    if request.method=="POST":        
        username = request.POST.get('username')
        pass1 = request.POST.get('pass1')
        
        # Check if the input is an email
        if '@' in username:
            try:
                # Get the user by email
                user_obj = User.objects.get(email=username)
                username = user_obj.username  # Get the username (phone number) for authentication
            except User.DoesNotExist:
                messages.error(request, "Invalid Email or Password")
                return redirect('/login')
        
        # Authenticate with username (phone number) and password
        myuser = authenticate(username=username, password=pass1)
        if myuser is not None:
            login(request, myuser)
            messages.success(request, "Login Successful")
            return redirect('/')
        else:
            messages.error(request, "Invalid Credentials")
            return redirect('/login')
            
    return render(request, "handlelogin.html")

def handleLogout(request):
    logout(request)
    messages.success(request,"Logout Success")    
    return redirect('/login')

def contact(request):
    if request.method == "POST":
        name = request.POST.get('fullname')
        email = request.POST.get('email')
        number = request.POST.get('num')
        desc = request.POST.get('desc')

        myquery = Contact(name=name, email=email, phonenumber=number, description=desc)
        myquery.save()       

        messages.info(request, "Thanks for contacting us. We will get back to you soon.")
        return redirect('/contact/')  

    return render(request, "contact.html")  

@login_required  
def demographics(request):
    user = request.user  
    defaults = {
        "age": 18,
        "gender": "other",
        "height": 170.0,
        "weight": 70.0,
        "fitness_goal": "general_fitness",
        "activity_level": "moderate"
    }
    
    demographics_data, created = Demographics.objects.get_or_create(user=user)

    if request.method == "POST":
        age = request.POST.get("age")
        gender = request.POST.get("gender")
        height = request.POST.get("height")
        weight = request.POST.get("weight")
        fitness_goal = request.POST.get("fitness_goal")
        activity_level = request.POST.get("activity_level")

        demographics_data.age = age
        demographics_data.gender = gender
        demographics_data.height = height
        demographics_data.weight = weight
        demographics_data.fitness_goal = fitness_goal
        demographics_data.activity_level = activity_level
        demographics_data.save()

        messages.success(request, "Your demographics have been updated successfully.")
        return redirect("demographics")  
    return render(request, "demographics.html", {"demographics": demographics_data})

@login_required
def profile(request):
    try:
        # Get or create the user's profile
        profile, created = Profile.objects.get_or_create(user=request.user)
        logger.info(f"Retrieved profile for user {request.user.username} - "
                   f"Workouts: {profile.workouts_completed}, "
                   f"Minutes: {profile.total_minutes}, "
                   f"Streak: {profile.streak}, "
                   f"Last workout: {profile.last_workout_date}")

        if request.method == 'POST':
            # Handle profile information update
            old_bio = profile.bio
            old_phone = profile.phone
            old_location = profile.location
            
            profile.bio = request.POST.get('bio', '')
            profile.phone = request.POST.get('phone', '')
            profile.location = request.POST.get('location', '')
            profile.save()
            
            logger.info(f"Updated profile info for user {request.user.username} - "
                       f"Bio: {old_bio}->{profile.bio}, "
                       f"Phone: {old_phone}->{profile.phone}, "
                       f"Location: {old_location}->{profile.location}")
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')

        return render(request, 'profile.html', {'profile': profile})
    except Exception as e:
        logger.error(f"Error in profile view for user {request.user.username}: {str(e)}", exc_info=True)
        messages.error(request, 'Error loading profile data. Please try again.')
        return render(request, 'profile.html', {}) 
   
def about(request):
    return render(request, "about.html")
   
