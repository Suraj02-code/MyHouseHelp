from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class MLPrediction(models.Model):
    """Store ML model predictions"""
    
    PREDICTION_TYPES = [
        ('demand_forecast', 'Demand Forecasting'),
        ('price_optimization', 'Price Optimization'),
        ('provider_recommendation', 'Provider Recommendation'),
        ('sentiment_analysis', 'Sentiment Analysis'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ml_predictions',
        null=True,
        blank=True
    )
    
    prediction_type = models.CharField(max_length=30, choices=PREDICTION_TYPES)
    input_data = models.JSONField(help_text="Input features used for prediction")
    prediction_result = models.JSONField(help_text="Model prediction output")
    confidence_score = models.DecimalField(
        max_digits=5, decimal_places=4, null=True, blank=True,
        help_text="Model confidence (0-1)"
    )
    model_version = models.CharField(max_length=50, default='v1.0')
    
    # Reference to related object (booking, review, etc.)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_prediction_type_display()} - {self.created_at.date()}"


class RecommendationScore(models.Model):
    """Store provider recommendation scores for customers"""
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recommendation_scores'
    )
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_recommendation_scores'
    )
    service_category = models.CharField(max_length=100, blank=True)
    
    # Recommendation factors
    compatibility_score = models.DecimalField(max_digits=5, decimal_places=4, default=0.0)
    distance_score = models.DecimalField(max_digits=5, decimal_places=4, default=0.0)
    rating_score = models.DecimalField(max_digits=5, decimal_places=4, default=0.0)
    price_score = models.DecimalField(max_digits=5, decimal_places=4, default=0.0)
    availability_score = models.DecimalField(max_digits=5, decimal_places=4, default=0.0)
    
    # Overall recommendation score
    overall_score = models.DecimalField(max_digits=5, decimal_places=4)
    
    # Metadata
    factors_used = models.JSONField(default=dict)
    calculated_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('customer', 'provider', 'service_category')
        ordering = ['-overall_score']
    
    def __str__(self):
        return f"Recommendation: {self.provider.username} for {self.customer.username} ({self.overall_score})"


class DemandForecast(models.Model):
    """Store demand forecasting data"""
    service_category = models.CharField(max_length=100)
    location_area = models.CharField(max_length=200, blank=True)
    
    forecast_date = models.DateField()
    predicted_demand = models.DecimalField(max_digits=10, decimal_places=2)
    confidence_interval = models.JSONField(default=dict)  # {"lower": x, "upper": y}
    
    # Influencing factors
    seasonal_factor = models.DecimalField(max_digits=5, decimal_places=4, default=1.0)
    trend_factor = models.DecimalField(max_digits=5, decimal_places=4, default=1.0)
    external_factors = models.JSONField(default=dict)  # weather, events, etc.
    
    model_version = models.CharField(max_length=50, default='v1.0')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('service_category', 'location_area', 'forecast_date')
        ordering = ['forecast_date']
    
    def __str__(self):
        return f"Forecast: {self.service_category} on {self.forecast_date} - {self.predicted_demand}"


class DynamicPricing(models.Model):
    """Dynamic pricing suggestions based on ML"""
    service_category = models.CharField(max_length=100)
    location_area = models.CharField(max_length=200, blank=True)
    
    # Time-based factors
    date_range_start = models.DateTimeField()
    date_range_end = models.DateTimeField()
    
    # Pricing factors
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    suggested_price = models.DecimalField(max_digits=10, decimal_places=2)
    demand_multiplier = models.DecimalField(max_digits=5, decimal_places=4, default=1.0)
    competition_factor = models.DecimalField(max_digits=5, decimal_places=4, default=1.0)
    urgency_factor = models.DecimalField(max_digits=5, decimal_places=4, default=1.0)
    
    # Supporting data
    market_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Dynamic Pricing: {self.service_category} - ₹{self.suggested_price}"
