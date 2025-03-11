from django.shortcuts import render, redirect
from django.contrib import messages
from .firebase import database_ref, career_db
from .firebase import save_contact_form, get_all_submissions
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .firebase import initialize_firebase

def home(request):
    return render(request, 'home.html')

def ourvalues(request):
    return render(request, 'ourvalues.html')

def leadership(request):
    return render(request, 'leadership.html')

def careers(request):
    return render(request, 'careers.html')

def research(request):
    return render(request, 'research.html')

def factors(request):
    return render(request, 'factors.html')

def diet(request):
    return render(request, 'diet.html')

def food(request):
    return render(request, 'food.html')

def chocolate(request):
    return render(request, 'chocolate.html')

def treatment(request):
    return render(request, 'treatment.html')

def weightloss(request):
    return render(request, 'weightloss.html')

def careersselection(request):
    return render(request, 'careersselection.html')

def diabeteseducator(request):
    return render(request, 'diabeteseducator.html')

def nutritionist(request):
    return render(request, 'nutritionist.html')

def fullstackdeveloper(request):
    return render(request, 'fullstackdeveloper.html')

def datascientist(request):
    return render(request, 'datascientist.html')

def customersupportspecialist(request):
    return render(request, 'customersupportspecialist.html')

def healthcareadministrator(request):
    return render(request, 'healthcareadministrator.html')

def contactus(request):
    return render(request, 'contactus.html')

def appointment(request):
    return render(request, 'appointment.html')

def job_application(request):
    if request.method == 'POST':
        try:
            # Get form data
            full_name = request.POST.get('fullName')
            country_code = request.POST.get('countryCode')
            phone = request.POST.get('phone')
            email = request.POST.get('email')
            location = request.POST.get('location')
            qualification = request.POST.get('qualification')
            degree_class = request.POST.get('degreeClass')
            
            messages.success(request, 'Application submitted successfully!')
            return redirect('careersselection')  # Replace with your success URL
            
        except Exception as e:
            messages.error(request, 'Error submitting application. Please try again.')
            return redirect('diabeteseducator')  # Replace with your form URL
            
    return render(request, 'diebeteseducator.html')
    

def contactus(request):
    if request.method == 'POST':
        # Collect form data
        form_data = {
            'subject': request.POST.get('subject'),
            'message': request.POST.get('message'),
            'country': request.POST.get('country'),
            'first_name': request.POST.get('first_name'),
            'last_name': request.POST.get('last_name'),
            'email': request.POST.get('email'),
            'mobilenumber': request.POST.get('mobilenumber')
        }
        
        # Save to Firebase
        submission_id = save_contact_form(form_data)
        
        if submission_id:
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contactus')
        else:
            messages.error(request, 'There was an error sending your message. Please try again.')
    
    return render(request, 'contactus.html')


def process_career_application(request, career_type):
    if request.method == 'POST':
        application_data = {
            'fullName': request.POST.get('fullName'),
            'countryCode': request.POST.get('countryCode'),
            'phone': request.POST.get('phone'),
            'email': request.POST.get('email'),
            'location': request.POST.get('location'),
            'qualification': request.POST.get('qualification'),
            'degreeClass': request.POST.get('degreeClass'),
            'position': career_type,
            'applicationDate': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'status': 'pending'
        }

        try:
            career_db.submit_application(career_type, application_data)
            messages.success(request, 'Application submitted successfully!')
            return redirect('careers')
        except Exception as e:
            messages.error(request, f'Error submitting application: {str(e)}')
            return redirect(request.path)

    template_map = {
        'healthcare_administrator': 'healthcare_administrator.html',
        'diabetes_educator': 'diabetes_educator.html',
        'nutritionist': 'nutritionist.html',
        'full_stack_developer': 'fullstackdeveloper.html',
        'data_scientist': 'datascientist.html',
        'customer_support_specialist': 'customersupportspecialist.html'
    }
    
    return render(request, template_map.get(career_type, 'default.html'))


@csrf_exempt
def appointment(request):
    if request.method == 'POST':
        try:
            # Initialize Firebase
            ref = initialize_firebase()
            
            # Get form data
            form_data = {
                'name': request.POST.get('name'),
                'email': request.POST.get('email'),
                'phone': request.POST.get('phone'),
                'appointmentDate': request.POST.get('appointmentDate'),
                'appointmentTime': request.POST.get('appointmentTime'),
                'dateOfBirth': request.POST.get('dateOfBirth'),
                'dietRecommendations': request.POST.get('dietRecommendations'),
                'dietGuidance': request.POST.get('dietGuidance'),
                'managementChallenges': request.POST.get('managementChallenges'),
                'timestamp': datetime.now().isoformat()
            }
            
            # Save to Firebase Realtime Database
            appointments_ref = ref.child('appointments')
            new_appointment = appointments_ref.push(form_data)
            
            return JsonResponse({
                'status': 'success',
                'message': 'Appointment saved successfully',
                'appointment_id': new_appointment.key
            })
            
        except Exception as e:
            print(f"Error saving appointment: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    return render(request, 'appointment.html')


