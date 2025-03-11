# userinfo/firebase.py

import firebase_admin
from firebase_admin import credentials, db, firestore
import os
from datetime import datetime
import json
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

firebase_creds = os.environ.get('FIREBASE_CREDENTIALS')

# Initialize the Firebase Admin SDK
if not firebase_admin._apps:
    creds_dict = json.loads(firebase_creds)
    cred = credentials.Certificate(creds_dict)
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://controlsystem-8a38d-default-rtdb.firebaseio.com/'  # Replace with your Firebase databas>    
    })


db_ref = db.reference()

# Create database reference
database_ref = db.reference('/')

# Export the database reference
__all__ = ['database_ref']


def save_contact_form(form_data):
    """
    Save contact form data to Firebase
    """
    try:
        # Create a reference to the 'contact_submissions' node
        contact_ref = db_ref.child('contact_submissions')
        
        # Prepare the data
        submission_data = {
            'subject': form_data.get('subject'),
            'message': form_data.get('message'),
            'country': form_data.get('country'),
            'first_name': form_data.get('first_name'),
            'last_name': form_data.get('last_name'),
            'email': form_data.get('email'),
            'mobile_number': form_data.get('mobilenumber'),
            'timestamp': datetime.now().isoformat()
        }
        
        # Push the data to Firebase
        new_submission = contact_ref.push(submission_data)
        return new_submission.key
        
    except Exception as e:
        print(f"Error saving to Firebase: {str(e)}")
        return None

def get_all_submissions():
    """
    Retrieve all contact form submissions
    """
    try:
        submissions = db_ref.child('contact_submissions').get()
        return submissions
    except Exception as e:
        print(f"Error retrieving submissions: {str(e)}")
        return None
    

class CareerDatabase:
    def __init__(self):
        self.db_ref = db.reference('careers')
        
    def submit_application(self, career_type, application_data):
        """
        Store application data for specific career type
        """
        return self.db_ref.child(career_type).push(application_data)
        
    def get_applications(self, career_type=None):
        """
        Retrieve applications, optionally filtered by career type
        """
        if career_type:
            return self.db_ref.child(career_type).get()
        return self.db_ref.get()

# Create database instance
career_db = CareerDatabase()

def initialize_firebase():
    if not firebase_admin._apps:
        cred_dict = json.loads(os.getenv('FIREBASE_CONFIG'))
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://controlsystem-8a38d-default-rtdb.asia-southeast1.firebasedatabase.app/'
        })
    return db.reference()

class FirebaseDB:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseDB, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        try:
            if not firebase_admin._apps:
                # Update with your Firebase credentials file path
                cred = credentials.Certificate(
                    Path(__file__).parent /  'controlsystem-8a38d-firebase-adminsdk-fbsvc-0b637fe231.json'
                )
                firebase_admin.initialize_app(cred, {
                    'databaseURL': 'https://controlsystem-8a38d-default-rtdb.firebaseio.com/'  # Update this
                })
            self.db = db.reference()
        except Exception as e:
            print(f"Firebase initialization error: {e}")
            self.db = None

