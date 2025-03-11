# firebase.py
import pyrebase
from datetime import datetime

class FirebaseManager:
    def __init__(self):
        # Your Firebase configuration
        config = {
            "apiKey": "AIzaSyAt6mzhb61gXzxWnKmau0ThECrMSnEcwGM",
            "authDomain": "controlsystem-8a38d.firebaseapp.com",
            "databaseURL": "https://controlsystem-8a38d-default-rtdb.firebaseio.com",
            "storageBucket": "controlsystem-8a38d.firebasestorage.app"
        }
        
        # Initialize Firebase
        firebase = pyrebase.initialize_app(config)
        self.db = firebase.database()

    def store_recommendation(self, user, recommendation_data):
        """
        Store diet recommendation data in Firebase Realtime Database
        """
        try:
            # Create timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            
            
            data = {
                'timestamp': str(datetime.now()),
                'personal_info': {
                    'age': recommendation_data.get('age'),
                    'height': recommendation_data.get('height'),
                    'weight': recommendation_data.get('weight'),
                    'gender': recommendation_data.get('gender'),
                    'activity': recommendation_data.get('activity'),
                    'weight_loss_plan': recommendation_data.get('weight_loss_plan')
                },
                'health_metrics': {
                    'bmi': recommendation_data.get('bmi'),
                    'bmi_category': recommendation_data.get('bmi_category'),
                    'recommended_calories': recommendation_data.get('recommended_calories'),
                    'meal_calories': recommendation_data.get('meal_calories')
                },
                'meals_recommendation': recommendation_data.get('meals_recommendation')
            }

            # Store in Firebase under user's diet recommendations
            self.db.child('users').child(user.username).child('diet_recommendations').child(timestamp).set(data)
            
            return True, "Recommendation stored successfully"
        except Exception as e:
            return False, f"Error storing recommendation: {str(e)}"

    def get_user_recommendations(self, user):
        """
        Retrieve all diet recommendations for a specific user
        """
        try:
            # Get recommendations from Firebase
            recommendations = []
            recommendation_data = self.db.child('users').child(user.username).child('diet_recommendations').get()
            
            if recommendation_data.each():
                for rec in recommendation_data.each():
                    data = rec.val()
                    data['id'] = rec.key()
                    recommendations.append(data)
            
            # Sort by timestamp in descending order
            recommendations.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            return recommendations
            
        except Exception as e:
            print(f"Error retrieving recommendations: {str(e)}")
            return []

    def delete_recommendation(self, username, recommendation_id):
        """
        Delete a specific recommendation
        """
        try:
            self.db.child('users').child(username).child('diet_recommendations').child(recommendation_id).remove()
            return True, "Recommendation deleted successfully"
        except Exception as e:
            return False, f"Error deleting recommendation: {str(e)}"