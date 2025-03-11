from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from user.models import Profile
from django.contrib.auth.decorators import login_required
import firebase_admin
from firebase_admin import credentials, db
from .models import Profile
from .firebase import user_fb
from .firebase import FirebaseManager
from datetime import datetime
import re

def signin(request):
    return render(request, 'signin.html')

def register(request):
    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # First try Django authentication
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            
            if not hasattr(user, 'profile'):
                Profile.objects.create(user=user)

            return redirect('home')
        else:
            # If Django auth fails, check if it's a Firebase-only user
            firebase_user = user_fb.get_user(username)
            if firebase_user and firebase_user.get('password') == password:
                # If Firebase auth succeeds, create/update Django user
                try:
                    # Get or create Django user
                    user, created = User.objects.get_or_create(username=username)
                    if created:
                        user.email = firebase_user.get('email', '')
                        
                    # Update Django password to match Firebase
                    user.set_password(password)
                    user.save()

                    # Create profile if needed
                    if not hasattr(user, 'profile'):
                        Profile.objects.create(user=user)

                    # Log user in
                    login(request, user)
                    return redirect('home')
                except Exception as e:
                    print(f"Error syncing Firebase user to Django: {e}")
                    messages.error(request, 'Error during login synchronization')
            else:
                messages.error(request, 'Username or Password is incorrect')

    return render(request, 'signin.html')

def logout_view(request):
    logout(request)
    return redirect('home')


def signup(request):
    if request.method == "POST":
        try:
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            password2 = request.POST.get('password2')
            name = request.POST.get('name')
            phone = request.POST.get('phone')
            gender = request.POST.get('gender')

            # Password validation
            if password != password2:
                messages.error(request, "Passwords do not match.")
                return redirect('register')

            # Check existing users
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists.")
                return redirect('register')
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already exists.")
                return redirect('register')

            # Create Django user first
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password  # Django will hash this password
            )
            user.save()

            # Create Django profile
            Profile.objects.get_or_create(user=user)

            # Store in Firebase
            firebase_data = {
                'username': username,
                'name': name,
                'email': email,
                'phone': phone,
                'gender': gender,
                'password': password  # Store plain password in Firebase
            }

            if user_fb.create_user(firebase_data):
                # Login user
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    messages.success(request, "Account created successfully!")
                    return redirect('profiles')
            else:
                # Rollback if Firebase save fails
                user.delete()
                messages.error(request, "Failed to create account in Firebase.")
                return redirect('signup')

        except Exception as e:
            messages.error(request, f"Registration error: {str(e)}")
            return redirect('signup')

    return render(request, 'signin.html')

@login_required
def profiles(request):
    current_user = request.user
    firebase_user = user_fb.get_user(current_user.username)
    
    if request.method == 'POST':
        try:
            # Get existing user data first
            existing_data = firebase_user or {}
            
            # Prepare new profile data while preserving existing fields
            profile_data = {
                'full_name': f"{request.POST.get('first-name')} {request.POST.get('last-name')}",
                'email': request.POST.get('email'),
                'phone': existing_data.get('phone', ''),  # Preserve existing phone
                'dob': request.POST.get('date-of-birth'),
                'gender': request.POST.get('gender', existing_data.get('gender', '')).lower(),
                'race': request.POST.get('race', existing_data.get('race', '')).lower(),
                'height': float(request.POST.get('height', existing_data.get('height', 0))),
                'weight': float(request.POST.get('weight', existing_data.get('weight', 0))),
                'profession': request.POST.get('profession', existing_data.get('profession', '')).lower(),
                'age': int(request.POST.get('age', existing_data.get('age', 0))),
                'password': existing_data.get('password', ''),  # Preserve existing password
                'is_active': existing_data.get('is_active', True),  # Preserve active status
                'created_at': existing_data.get('created_at', str(datetime.now()))  # Preserve creation date
            }

            # Calculate BMI only if both height and weight are present
            if profile_data['height'] and profile_data['weight']:
                height_m = profile_data['height'] / 100
                profile_data['bmi'] = round(profile_data['weight'] / (height_m * height_m), 2)
            else:
                profile_data['bmi'] = existing_data.get('bmi', 0)  # Preserve existing BMI

            # Update Firebase with merged data
            if user_fb.update_user(current_user.username, profile_data):
                messages.success(request, 'Profile updated successfully!')
            else:
                messages.error(request, 'Failed to update profile')

        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
        
        return redirect('profiles')    # Get existing profile data for display
    
    if firebase_user:
        # Split full name into first and last name
        full_name = firebase_user.get('full_name', '').split(' ', 1)
        first_name = full_name[0] if full_name else ''
        last_name = full_name[1] if len(full_name) > 1 else ''

        profile = {
            'first_name': first_name,
            'last_name': last_name,
            'email': firebase_user.get('email', ''),
            'phone': firebase_user.get('phone', ''),
            'dob': firebase_user.get('dob', ''),
            'gender': firebase_user.get('gender', ''),
            'race': firebase_user.get('race', ''),
            'height': firebase_user.get('height', ''),
            'weight': firebase_user.get('weight', ''),
            'profession': firebase_user.get('profession', ''),
            'age': firebase_user.get('age', ''),
            'bmi': firebase_user.get('bmi', 0)
        }
    else:
        profile = {}
        messages.warning(request, 'Unable to fetch profile data')

    context = {
        'profile': profile,
        'current_user': {
            'first_name': first_name if firebase_user else 'User'
        }
    }

    return render(request, 'profiles.html', context)

@login_required
def change_password(request):
    if request.method != 'POST':
        return redirect('profiles')

    current_user = request.user
    current_password = request.POST.get('current-password')
    new_password = request.POST.get('new-password')
    confirm_password = request.POST.get('confirm-password')

    # Password validation
    def is_valid_password(password):
        return (
            len(password) >= 8 and
            re.search(r'[A-Z]', password) and
            re.search(r'[a-z]', password) and
            re.search(r'[0-9]', password)
        )

    if new_password != confirm_password:
        messages.error(request, 'New passwords do not match')
        return redirect('profiles')

    if not is_valid_password(new_password):
        messages.error(request, 'Password must be at least 8 characters long and include at least one uppercase letter, one lowercase letter, and one number')
        return redirect('profiles')

    # First verify the current password using Django's authentication
    if not current_user.check_password(current_password):
        messages.error(request, 'Current password is incorrect')
        return redirect('profiles')

    try:
        # Update password in Django
        current_user.set_password(new_password)
        current_user.save()

        # Update password in Firebase
        update_data = {
            'password': new_password,
            'updated_at': str(datetime.now())
        }
        
        if user_fb.update_user(current_user.username, update_data):
            # Re-authenticate the user with the new password
            user = authenticate(request, username=current_user.username, password=new_password)
            if user is not None:
                login(request, user)  # Log the user back in
                messages.success(request, 'Password updated successfully')
            else:
                messages.error(request, 'Password updated but please log in again')
                return redirect('signin')
        else:
            # If Firebase update fails, roll back Django password
            current_user.set_password(current_password)
            current_user.save()
            messages.error(request, 'Failed to update password')
    except Exception as e:
        messages.error(request, f'Error updating password: {str(e)}')
        
    return redirect('profiles')