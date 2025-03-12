from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from django.utils.timezone import now
from .models import Recommendation, Recipe, MealPlan
from django.http import HttpResponse, JsonResponse
from .firebase import FirebaseManager

# Initialize Firebase Manager
firebase_mgr = FirebaseManager()

# Your existing columns and dataset loading
columns = ['Name', 'CookTime', 'PrepTime', 'TotalTime', 'RecipeIngredientParts',
           'Calories', 'FatContent', 'SaturatedFatContent', 'CholesterolContent', 'SodiumContent', 'CarbohydrateContent',
           'FiberContent', 'SugarContent', 'ProteinContent', 'RecipeInstructions']

dataset = pd.read_csv('Data/dataset.csv', usecols=columns)

@login_required(login_url='signin')
def recommendation(request):
    return render(request, 'recommendation.html')

def recommendation_result(request):
    if request.method == 'GET':
        try:
            # Get form data
            age = int(request.GET.get('age', 0))
            height = float(request.GET.get('height', 0))
            weight = float(request.GET.get('weight', 0))
            gender = request.GET.get('gender', 'male')
            activity = request.GET.get('activity', 'no exercise')
            weight_loss_plan = request.GET.get('weight_loss_plan', 'maintain weight')

            # Your existing calculations
            bmi = calculate_bmi(weight, height)
            bmi_category = categorize_bmi(bmi)
            bmr = calculate_bmr(gender, weight, height, age)

            activity_multiplier = {
                "no exercise": 1.2,
                "light exercise": 1.375,
                "moderate exercise": 1.55,
                "very active": 1.725,
                "extra active": 1.9,
            }.get(activity, 1.2)

            maintain_calories = round(bmr * activity_multiplier)

            plan_calories = {
                "maintain weight": maintain_calories,
                "mild weight loss": maintain_calories - 250,
                "weight loss": maintain_calories - 500,
                "extreme weight loss": maintain_calories - 1000,
            }

            recommended_calories = plan_calories.get(weight_loss_plan, maintain_calories)

            meal_ratios = {"breakfast": 0.3, "lunch": 0.35, "dinner": 0.25, "snacks": 0.1}
            meal_calories = {meal: round(ratio * recommended_calories) for meal, ratio in meal_ratios.items()}

            # Get meal recommendations
            meals_recommendation = {
                meal: recommend_by_calories(dataset, calculate_nutritional_needs(meal_calories[meal]))[['Name', 'Calories', 'RecipeIngredientParts', 'RecipeInstructions', 
                                                                                                        'ProteinContent', 'SaturatedFatContent', 'CholesterolContent', 
                                                                                                        'SodiumContent', 'CarbohydrateContent', 'FiberContent', 
                                                                                                        'SugarContent']]
                for meal in meal_ratios.keys()
            }
            meals_recommendation = format_meals_recommendation(meals_recommendation)

            # Create the recommendation record
            recommendation = Recommendation.objects.create(
                user=request.user,
                age=age,
                height=height,
                weight=weight,
                gender=gender,
                activity=activity,
                weight_loss_plan=weight_loss_plan,
                bmi=bmi,
                bmi_category=bmi_category,
                recommended_calories=recommended_calories,
            )

            # Store meal plans and recipes
            for meal_type, recipes_data in meals_recommendation.items():
                # Create meal plan
                meal_plan = MealPlan.objects.create(
                    recommendation=recommendation,
                    meal_type=meal_type,
                    calories_allocated=meal_calories[meal_type]
                )
                
                # Create recipes and link to meal plan
                for recipe_data in recipes_data:
                    recipe = Recipe.objects.create(
                        name=recipe_data['Name'],
                        calories=recipe_data['Calories'],
                        ingredients=recipe_data['Ingredients'],
                        instructions=recipe_data['Instructions'],
                        protein = recipe_data['Protein'],
                        SaturatedFat = recipe_data['SaturatedFat'],
                        cholesterol = recipe_data['Cholesterol'],
                        sodium = recipe_data['Sodium'],
                        carbohydrate = recipe_data['Carbohydrate'],
                        fiber = recipe_data['Fiber'],
                        sugar = recipe_data['Sugar']
                    )
                    meal_plan.recipes.add(recipe)

            # Store in Firebase (keeping existing functionality)
            recommendation_data = {
                'age': age,
                'height': height,
                'weight': weight,
                'gender': gender,
                'activity': activity,
                'weight_loss_plan': weight_loss_plan,
                'bmi': bmi,
                'bmi_category': bmi_category,
                'recommended_calories': recommended_calories,
                'meal_calories': meal_calories,
                'meals_recommendation': meals_recommendation
            }

            success, message = firebase_mgr.store_recommendation(request.user, recommendation_data)
            if not success:
                print(f"Firebase storage error: {message}")

            # Prepare context for template
            context = {
                'bmi': bmi,
                'bmi_category': bmi_category,
                'recommended_calories': recommended_calories,
                'meal_calories': meal_calories,
                'meals_recommendation': meals_recommendation,
            }

            return render(request, 'recommendation_result.html', context)

        except ValueError as e:
            return HttpResponse(f"Invalid input: {e}", status=400)
    else:
        return HttpResponse("Invalid request", status=400)

@login_required(login_url='signin')
def list_recommendation(request):
    # Fetch recommendations from Firebase
    recommendations = firebase_mgr.get_user_recommendations(request.user)
    return render(request, 'recommendation_history.html', {'recommendations': recommendations})

@login_required(login_url='signin')
def delete_recommendation(request, recommendation_id):
    if request.method == 'POST':
        success, message = firebase_mgr.delete_recommendation(request.user.username, recommendation_id)
        return JsonResponse({
            'success': success,
            'message': message
        })
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })

# Keep all your existing helper functions unchanged
def calculate_nutritional_needs(calories):
    return [
        calories,
        calories * 0.03,
        calories * 0.01,
        300,
        2300,
        calories * 0.125,
        calories * 0.014,
        calories * 0.025,
        calories * 0.2
    ]

def calculate_bmi(weight, height):
    height_m = height / 100
    return round(weight / (height_m ** 2), 2) if height > 0 else None

def categorize_bmi(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 25:
        return "Normal weight"
    elif 25 <= bmi < 30:
        return "Overweight"
    else:
        return "Obesity"

def calculate_bmr(gender, weight, height, age):
    return 10 * weight + 6.25 * height - 5 * age + (5 if gender.lower() == "male" else -161)

def recommend_by_calories(dataframe, max_nutritional_values, params={'return_distance': False}):
    extracted_data = extract_data(dataframe, max_nutritional_values)
    if extracted_data.empty:
        return "No suitable recipes found."

    prep_data, scaler = scale_data(extracted_data)
    neigh = train_nn(prep_data)
    pipeline = build_pipeline(neigh, scaler, params)
    
    test_input = np.array(max_nutritional_values).reshape(1, -1)
    test_input_scaled = scaler.transform(test_input)
    recommended_recipe = apply_pipeline(pipeline, test_input_scaled, extracted_data)
    return recommended_recipe

def extract_data(dataframe, max_nutritional_values):
    extracted_data = dataframe.copy()
    for column, maximum in zip(extracted_data.columns[5:14], max_nutritional_values):
        if column in ['FatContent', 'SaturatedFatContent', 'CholesterolContent', 'SodiumContent', 'SugarContent']:
            extracted_data = extracted_data[extracted_data[column] < maximum]
        elif column in ['ProteinContent', 'FiberContent']:
            extracted_data = extracted_data[extracted_data[column] > maximum * 0.5]
    return extracted_data

def scale_data(dataframe):
    scaler = StandardScaler()
    prep_data = scaler.fit_transform(dataframe.iloc[:, 5:14].to_numpy())
    return prep_data, scaler

def train_nn(prep_data):
    n_samples = prep_data.shape[0]
    n_neighbors = min(5, n_samples) 

    neigh = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=n_neighbors)
    neigh.fit(prep_data)
    return neigh


def build_pipeline(neigh, scaler, params):
    transformer = FunctionTransformer(neigh.kneighbors, kw_args=params)
    return Pipeline([('std_scaler', scaler), ('NN', transformer)])

def apply_pipeline(pipeline, _input, extracted_data):
    return extracted_data.iloc[pipeline.transform(_input)[0]]

def format_meals_recommendation(meals_recommendation):
    formatted_recommendations = {}
    
    for meal, df in meals_recommendation.items():
        if isinstance(df, pd.DataFrame):
            meal_data = []
            for _, row in df.iterrows():
                ingredients = parse_list_string(row.get('RecipeIngredientParts', '[]'))
                instructions = parse_list_string(row.get('RecipeInstructions', '[]'))
                
                meal_data.append({
                    'Name': row['Name'],
                    'Calories': row['Calories'],
                    'Ingredients': ingredients,
                    'Instructions': instructions,
                    'Protein': row['ProteinContent'],
                    'SaturatedFat': row['SaturatedFatContent'],
                    'Cholesterol': row['CholesterolContent'],
                    'Sodium': row['SodiumContent'],
                    'Carbohydrate': row['CarbohydrateContent'],
                    'Fiber': row['FiberContent'],
                    'Sugar': row['SugarContent']
                })
            formatted_recommendations[meal] = meal_data

    return formatted_recommendations

def parse_list_string(list_string):
    """
    Converts R-style list strings like 'c("item1", "item2")' into Python lists.
    """
    import re

    if not list_string or not isinstance(list_string, str):
        return []

    # Regular expression to extract items within quotes
    matches = re.findall(r'"(.*?)"', list_string)
    return matches


@login_required(login_url='signin')
def recommendation_history(request):
    recommendations = Recommendation.objects.filter(user=request.user).prefetch_related('meal_plans__recipes')
    
    return render(request, 'recommendation_history.html', {
        'recommendations': recommendations
    })

@login_required(login_url='signin') 
def list_recommendation(request):

    recommendations = Recommendation.objects.filter(user=request.user)

    return render(request, 'recommendation_history.html', {'recommendations': recommendations})