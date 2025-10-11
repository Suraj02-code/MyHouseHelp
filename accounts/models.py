from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):
    """Extended User model with role-based access"""
    
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('provider', 'Service Provider'),
        ('admin', 'Administrator'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')],
        blank=True,
        null=True
    )
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class CustomerProfile(models.Model):
    """Extended profile for customers"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    preferred_services = models.TextField(blank=True, help_text="Comma-separated list of preferred service types")
    loyalty_points = models.PositiveIntegerField(default=0)
    total_bookings = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"Customer: {self.user.username}"


class ServiceProviderProfile(models.Model):
    """Extended profile for service providers"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('suspended', 'Suspended'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='provider_profile')
    business_name = models.CharField(max_length=200)
    business_license = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    years_of_experience = models.PositiveIntegerField()
    verification_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    verification_documents = models.FileField(upload_to='verification_docs/', blank=True, null=True)
    service_radius = models.PositiveIntegerField(default=10, help_text="Service radius in kilometers")
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_reviews = models.PositiveIntegerField(default=0)
    completed_jobs = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Provider: {self.business_name} ({self.user.username})"
    
    def update_rating(self):
        """Update average rating based on reviews"""
        from reviews.models import Review
        reviews = Review.objects.filter(provider=self.user)
        if reviews.exists():
            avg_rating = reviews.aggregate(models.Avg('overall_rating'))['overall_rating__avg']
            self.average_rating = round(avg_rating, 2) if avg_rating else 0.00
            self.total_reviews = reviews.count()
            self.save()


class AdminProfile(models.Model):
    """Extended profile for administrators"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    department = models.CharField(max_length=100, blank=True)
    permissions_level = models.CharField(
        max_length=20,
        choices=[
            ('basic', 'Basic Admin'),
            ('super', 'Super Admin'),
        ],
        default='basic'
    )
    
    def __str__(self):
        return f"Admin: {self.user.username}"
