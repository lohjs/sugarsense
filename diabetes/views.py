from django.shortcuts import render
import pickle
import pandas as pd
from django.contrib.auth.decorators import login_required
from .models import Prediction
from .firebase import FirebaseDB

# Initialize Firebase
firebase_db = FirebaseDB()

# Load ML models
with open("diabetes/model/robust_scaler.pkl", 'rb') as f:
    robust_scaler = pickle.load(f)
with open("diabetes/model/standard_scaler.pkl", 'rb') as f:
    standard_scaler = pickle.load(f)
with open("diabetes/model/model.pkl", 'rb') as file:
    model = pickle.load(file)

@login_required(login_url='signin')
def prediction(request):
    return render(request, 'prediction.html')

@login_required(login_url='signin')
def result(request):
    if request.method != 'GET':
        return render(request, 'prediction.html')
        
    try:
        # Get form data
        var1 = int(request.GET.get('Pregnancies', 0))
        var2 = int(request.GET.get('Glucose', 0))
        var3 = int(request.GET.get('Blood Pressure', 0))
        var4 = int(request.GET.get('Skin Thickness', 0))
        var5 = float(request.GET.get('Insulin', 0))
        var6 = float(request.GET.get('BMI', 0))
        var7 = float(request.GET.get('Diabetes Pedigree Function', 0))
        var8 = int(request.GET.get('Age', 0))
        username = request.user
        
        # Initialize classification variables
        newBMI_Obesity1 = 0
        newBMI_Obesity2 = 0
        newBMI_Obesity3 = 0
        NewBMI_Overweight = 0
        NewBMI_Underweight = 0
        NewInsulinScore_Normal = 0
        NewGlucose_Low = 0
        NewGlucose_Normal = 0
        NewGlucose_Overweight = 0
        NewGlucose_Secret = 0
        
        # BMI Classification
        if var6 < 18.5:
            NewBMI_Underweight = 1
        elif 18.5 <= var6 <= 24.9:
            pass
        elif 25 <= var6 <= 29.9:
            NewBMI_Overweight = 1
        elif 30 <= var6 <= 34.9:
            newBMI_Obesity1 = 1
        elif 35 <= var6 <= 39.9:
            newBMI_Obesity2 = 1
        else:
            newBMI_Obesity3 = 1
        
        # Insulin Classification
        if 16 <= var5 <= 166:
            NewInsulinScore_Normal = 1
        
        # Glucose Classification
        if var2 <= 70:
            NewGlucose_Low = 1
        elif 71 <= var2 <= 99:
            NewGlucose_Normal = 1
        elif 100 <= var2 <= 126:
            NewGlucose_Overweight = 1
        else:
            NewGlucose_Secret = 1
        
        # Prepare data for prediction
        data = pd.DataFrame([[var1, var2, var3, var4, var5, var6, var7, var8]])
        data = pd.DataFrame(robust_scaler.transform(data))
        
        categorical_data = pd.DataFrame([[newBMI_Obesity1, newBMI_Obesity2, newBMI_Obesity3,
                                        NewBMI_Overweight, NewBMI_Underweight,
                                        NewInsulinScore_Normal,
                                        NewGlucose_Low, NewGlucose_Normal,
                                        NewGlucose_Overweight, NewGlucose_Secret]])
        
        data = pd.concat([data, categorical_data], axis=1)
        data = standard_scaler.transform(data)
        
        # Make prediction
        pred = model.predict(data)
        result2 = "Diabetic" if pred[0] == 1 else "Non-Diabetic"

        prediction_record = Prediction(
        pregnancies=var1,
        glucose=var2,
        blood_pressure=var3,
        skin_thickness=var4,
        insulin=var5,
        bmi=var6,
        diabetes_pedigree_function=var7,
        age=var8,
        prediction_result=result2,
        user=username
        )
        prediction_record.save()
        
        
        # Prepare data for Firebase storage
        prediction_data = {
            'user_info': {
                'username': request.user.username,
                'email': request.user.email
            },
            'input_values': {
                'pregnancies': var1,
                'glucose': var2,
                'blood_pressure': var3,
                'skin_thickness': var4,
                'insulin': var5,
                'bmi': var6,
                'diabetes_pedigree_function': var7,
                'age': var8
            },
            'classifications': {
                'bmi': {
                    'obesity1': bool(newBMI_Obesity1),
                    'obesity2': bool(newBMI_Obesity2),
                    'obesity3': bool(newBMI_Obesity3),
                    'overweight': bool(NewBMI_Overweight),
                    'underweight': bool(NewBMI_Underweight)
                },
                'insulin': {
                    'normal': bool(NewInsulinScore_Normal)
                },
                'glucose': {
                    'low': bool(NewGlucose_Low),
                    'normal': bool(NewGlucose_Normal),
                    'overweight': bool(NewGlucose_Overweight),
                    'secret': bool(NewGlucose_Secret)
                }
            },
            'prediction_result': result2
        }
        
        # Store in Firebase
        firebase_db.store_prediction(request.user.username, prediction_data)
        
        return render(request, 'prediction.html', {"result2": result2})
        
    except Exception as e:
        print(f"Error in prediction: {str(e)}")
        return render(request, 'prediction.html', {"error": "An error occurred during prediction"})
    

@login_required(login_url='signin') 
def list_prediction(request):

    predictions = Prediction.objects.filter(user=request.user)

    return render(request, 'predictionshistory.html', {'predictions': predictions})

