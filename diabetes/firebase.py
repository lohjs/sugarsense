import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime

class FirebaseDB:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseDB, cls).__new__(cls)
            if not firebase_admin._apps:
                # Update this path to your Firebase service account key
                cred = credentials.Certificate('serviceAccountKey.json')
                firebase_admin.initialize_app(cred, {
                    'databaseURL': 'https://controlsystem-8a38d-default-rtdb.firebaseio.com/'
                })
            cls._instance.db = db.reference()  # Root reference of the database
        return cls._instance

    def store_prediction(self, username, prediction_data):
        """Store prediction data in Firebase Realtime Database based on username"""
        try:
            # Reference to the user's prediction list
            predictions_ref = self.db.child('users').child(username).child('predictions')

            # Push a new prediction with timestamp
            predictions_ref.push({
                **prediction_data,
                'timestamp': datetime.now().isoformat()  # Store as ISO format string
            })

            return True
        except Exception as e:
            print(f"Firebase Error: {str(e)}")
            return False

    def get_user_predictions(self, username):
        """Retrieve user's predictions from Firebase Realtime Database based on username"""
        try:
            predictions_ref = self.db.child('users').child(username).child('predictions')
            predictions = predictions_ref.get() 
            
            if predictions:
                return sorted(predictions.values(), key=lambda x: x['timestamp'], reverse=True)
            return []
        except Exception as e:
            print(f"Firebase Error: {str(e)}")
            return []
