from main.firebase import FirebaseDB
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore, auth
import pytz

class UserFirebase:
    def __init__(self):
        firebase = FirebaseDB()
        self.db = firebase.db
        if not self.db:
            raise Exception("Firebase database not initialized")

    def create_user(self, user_data):
        try:
            users_ref = self.db.child('users')
            users_ref.child(user_data['username']).child('user_information').set({
                'full_name': user_data.get('name', ''),
                'email': user_data.get('email', ''),
                'phone': user_data.get('phone', ''),
                'gender': user_data.get('gender', ''),
                'password': user_data.get('password', ''),
                'created_at': str(datetime.now()),
                'is_active': True
            })
            return True
        except Exception as e:
            print(f"Error creating user in Firebase: {e}")
            return False

    def get_user(self, username):
        try:
            user_ref = self.db.child('users').child(username).child('user_information')
            user_data = user_ref.get()
            return user_data if user_data else None
        except Exception as e:
            print(f"Error getting user from Firebase: {e}")
            return None

    def update_user(self, username, update_data):
        try:
            # First get existing user data
            existing_data = self.get_user(username)
            if not existing_data:
                return False
            
            # Merge existing data with update data
            merged_data = {**existing_data, **update_data}
            
            # Update timestamp
            merged_data['updated_at'] = str(datetime.now())
            
            # Update the merged data
            user_ref = self.db.child('users').child(username).child('user_information')
            user_ref.set(merged_data)  # Using set instead of update to ensure all fields are preserved
            return True
        except Exception as e:
            print(f"Error updating user in Firebase: {e}")
            return False

    def delete_user(self, username):
        try:
            user_ref = self.db.child('users').child(username).child('user_information')
            user_ref.remove()
            return True
        except Exception as e:
            print(f"Error deleting user from Firebase: {e}")
            return False

user_fb = UserFirebase()


# Get Firestore client
db = firestore.client()

class FirebaseManager:
    @staticmethod
    def get_user_profile(user_id):
        """Fetch user profile from Firestore"""
        try:
            doc_ref = db.collection('users').child('user_information').document(user_id)
            doc = doc_ref.get()
            if doc.exists:
                user_data = doc.to_dict()
                # Convert Firestore timestamp to datetime
                if 'dob' in user_data and user_data['dob']:
                    user_data['dob'] = user_data['dob'].strftime('%Y-%m-%d')
                return user_data
            return None
        except Exception as e:
            print(f"Error getting user profile: {e}")
            return None

    @staticmethod
    def update_user_profile(user_id, profile_data):
        """Update user profile in Firestore"""
        try:
            # Convert date string to Firestore timestamp
            if 'dob' in profile_data and profile_data['dob']:
                dob_date = datetime.strptime(profile_data['dob'], '%Y-%m-%d')
                profile_data['dob'] = dob_date

            # Calculate BMI
            if 'height' in profile_data and 'weight' in profile_data:
                height_m = float(profile_data['height']) / 100
                weight_kg = float(profile_data['weight'])
                profile_data['bmi'] = round(weight_kg / (height_m * height_m), 2)

            # Update Firestore
            doc_ref = db.collection('users').child('user_information').document(user_id)
            doc_ref.set(profile_data, merge=True)
            return True
        except Exception as e:
            print(f"Error updating user profile: {e}")
            return False

    @staticmethod
    def update_password(user_id, current_password, new_password):
        """Update user password in Firebase Auth"""
        try:
            # Get user email from Firestore
            user_doc = db.collection('users').child('user_information').document(user_id).get()
            if not user_doc.exists:
                return False, "User not found"

            user_data = user_doc.to_dict()
            email = user_data.get('email')

            # Update password in Firebase Auth
            user = auth.update_user(
                user_id,
                password=new_password
            )
            return True, "Password updated successfully"
        except Exception as e:
            print(f"Error updating password: {e}")
            return False, str(e)