from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class Recipe(models.Model):
    name = models.CharField(max_length=255)
    calories = models.IntegerField()
    ingredients = models.JSONField()  # Store as list of ingredients
    instructions = models.JSONField()  # Store as list of instructions
    protein = models.FloatField(null=True, blank=True)
    SaturatedFat = models.FloatField(null=True, blank=True)
    cholesterol = models.FloatField(null=True, blank=True)
    sodium = models.FloatField(null=True, blank=True)
    carbohydrate = models.FloatField(null=True, blank=True)
    fiber = models.FloatField(null=True, blank=True)
    sugar = models.FloatField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    
    def __str__(self):
        return self.name

class MealPlan(models.Model):
    MEAL_TYPE_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snacks', 'Snacks'),
    ]
    
    recommendation = models.ForeignKey('Recommendation', on_delete=models.CASCADE, related_name='meal_plans')
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES)
    calories_allocated = models.IntegerField()
    recipes = models.ManyToManyField(Recipe, related_name='meal_plans')
    
    def __str__(self):
        return f"{self.meal_type} plan for {self.recommendation}"
    
    

class Recommendation(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    
    ACTIVITY_CHOICES = [
        ('no_exercise', 'No Exercise'),
        ('light_exercise', 'Light Exercise'),
        ('moderate_exercise', 'Moderate Exercise'),
        ('very_active', 'Very Active'),
        ('extra_active', 'Extra Active'),
    ]
    
    WEIGHT_PLAN_CHOICES = [
        ('maintain_weight', 'Maintain Weight'),
        ('mild_weight_loss', 'Mild Weight Loss'),
        ('weight_loss', 'Weight Loss'),
        ('extreme_weight_loss', 'Extreme Weight Loss'),
    ]
    
    # User and timestamp
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=now)
    
    # User inputs
    age = models.IntegerField()
    height = models.FloatField()
    weight = models.FloatField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    activity = models.CharField(max_length=20, choices=ACTIVITY_CHOICES)
    weight_loss_plan = models.CharField(max_length=20, choices=WEIGHT_PLAN_CHOICES)
    
    # Calculated results
    bmi = models.FloatField(default=0.0)
    bmi_category = models.CharField(max_length=50, default='Unknown')
    recommended_calories = models.IntegerField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Recommendation for {self.user.username} on {self.timestamp}"