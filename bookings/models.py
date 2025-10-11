from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from services.models import Service


class Booking(models.Model):
    """Customer service bookings"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('disputed', 'Disputed'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customer_bookings'
    )
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='provider_bookings'
    )
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='bookings')
    
    # Booking details
    booking_date = models.DateField()
    booking_time = models.TimeField()
    estimated_duration = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)
    actual_duration = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Location
    service_address = models.TextField()
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Pricing
    quoted_price = models.DecimalField(max_digits=10, decimal_places=2)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Status and priority
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    
    # Additional information
    special_instructions = models.TextField(blank=True)
    customer_notes = models.TextField(blank=True)
    provider_notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Booking #{self.id} - {self.service.title} by {self.provider.username}"
    
    @property
    def is_overdue(self):
        from django.utils import timezone
        from datetime import datetime, time
        
        if self.status in ['completed', 'cancelled']:
            return False
        
        booking_datetime = timezone.make_aware(
            datetime.combine(self.booking_date, self.booking_time)
        )
        return timezone.now() > booking_datetime


class BookingStatusHistory(models.Model):
    """Track booking status changes"""
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='status_history')
    old_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='status_changes'
    )
    change_reason = models.TextField(blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-changed_at']
    
    def __str__(self):
        return f"Booking #{self.booking.id}: {self.old_status} → {self.new_status}"


class BookingCancellation(models.Model):
    """Track booking cancellations"""
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='cancellation')
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cancelled_bookings'
    )
    reason = models.TextField()
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    cancellation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    cancelled_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Cancellation for Booking #{self.booking.id}"
