from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from bookings.models import Booking


class Review(models.Model):
    """Customer reviews for service providers"""
    
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_given'
    )
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_received'
    )
    
    # Rating (1-5 stars)
    overall_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    quality_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Quality of work"
    )
    timeliness_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Punctuality and timeliness"
    )
    communication_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Communication and professionalism"
    )
    value_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Value for money"
    )
    
    # Review content
    title = models.CharField(max_length=200, blank=True)
    comment = models.TextField()
    pros = models.TextField(blank=True, help_text="What went well")
    cons = models.TextField(blank=True, help_text="Areas for improvement")
    
    # Review metadata
    is_verified = models.BooleanField(default=True, help_text="Review from verified booking")
    is_featured = models.BooleanField(default=False, help_text="Featured review")
    helpful_count = models.PositiveIntegerField(default=0)
    
    # Sentiment analysis (to be populated by ML)
    sentiment_score = models.DecimalField(
        max_digits=3, decimal_places=2, null=True, blank=True,
        help_text="ML-generated sentiment score (-1 to 1)"
    )
    sentiment_label = models.CharField(
        max_length=20,
        choices=[
            ('positive', 'Positive'),
            ('neutral', 'Neutral'),
            ('negative', 'Negative'),
        ],
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ('booking', 'customer')
    
    def __str__(self):
        return f"Review by {self.customer.username} for {self.provider.username} - {self.overall_rating} stars"
    
    def save(self, *args, **kwargs):
        # Update provider's average rating
        super().save(*args, **kwargs)
        self.provider.provider_profile.update_rating()


class ReviewResponse(models.Model):
    """Provider responses to customer reviews"""
    review = models.OneToOneField(Review, on_delete=models.CASCADE, related_name='response')
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='review_responses'
    )
    response_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Response by {self.provider.username} to review #{self.review.id}"


class ReviewHelpful(models.Model):
    """Track which users found reviews helpful"""
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='helpful_votes')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='helpful_review_votes'
    )
    is_helpful = models.BooleanField(default=True)
    voted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('review', 'user')
    
    def __str__(self):
        return f"{self.user.username} found review #{self.review.id} helpful: {self.is_helpful}"


class ReviewFlag(models.Model):
    """User reports for inappropriate reviews"""
    
    FLAG_REASONS = [
        ('spam', 'Spam'),
        ('inappropriate', 'Inappropriate Content'),
        ('fake', 'Fake Review'),
        ('offensive', 'Offensive Language'),
        ('irrelevant', 'Irrelevant'),
        ('other', 'Other'),
    ]
    
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='flags')
    flagged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='review_flags'
    )
    reason = models.CharField(max_length=20, choices=FLAG_REASONS)
    description = models.TextField(blank=True)
    is_resolved = models.BooleanField(default=False)
    flagged_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('review', 'flagged_by')
    
    def __str__(self):
        return f"Flag by {self.flagged_by.username} for review #{self.review.id}"
