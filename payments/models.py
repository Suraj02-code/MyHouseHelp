from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from bookings.models import Booking
import uuid


class Payment(models.Model):
    """Payment records for bookings"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
        ('partially_refunded', 'Partially Refunded'),
    ]
    
    METHOD_CHOICES = [
        ('card', 'Credit/Debit Card'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
        ('wallet', 'Digital Wallet'),
        ('cash', 'Cash'),
    ]
    
    # Unique payment identifier
    payment_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments_made'
    )
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments_received'
    )
    
    # Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, default='INR')
    payment_method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Platform fees
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    provider_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # External payment processor details
    external_payment_id = models.CharField(max_length=200, blank=True)
    external_processor = models.CharField(
        max_length=50,
        choices=[
            ('stripe', 'Stripe'),
            ('paypal', 'PayPal'),
            ('razorpay', 'Razorpay'),
            ('other', 'Other'),
        ],
        blank=True
    )
    
    # Metadata
    payment_metadata = models.JSONField(default=dict, blank=True)
    failure_reason = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment {self.payment_id} - ₹{self.amount} ({self.status})"
    
    def save(self, *args, **kwargs):
        # Calculate provider amount after platform fee
        if self.provider_amount is None:
            self.provider_amount = self.amount - self.platform_fee
        super().save(*args, **kwargs)


class Refund(models.Model):
    """Refund records"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    REASON_CHOICES = [
        ('customer_request', 'Customer Request'),
        ('provider_cancellation', 'Provider Cancellation'),
        ('service_not_provided', 'Service Not Provided'),
        ('dispute_resolution', 'Dispute Resolution'),
        ('system_error', 'System Error'),
        ('other', 'Other'),
    ]
    
    refund_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    original_payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    reason = models.CharField(max_length=30, choices=REASON_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # External processor details
    external_refund_id = models.CharField(max_length=200, blank=True)
    
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='refunds_requested'
    )
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='refunds_processed',
        null=True,
        blank=True
    )
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Refund {self.refund_id} - ₹{self.amount} ({self.status})"


class PaymentMethod(models.Model):
    """Stored payment methods for users"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payment_methods'
    )
    
    method_type = models.CharField(
        max_length=20,
        choices=[
            ('card', 'Credit/Debit Card'),
            ('bank', 'Bank Account'),
            ('wallet', 'Digital Wallet'),
        ]
    )
    
    # For cards
    card_last_four = models.CharField(max_length=4, blank=True)
    card_brand = models.CharField(max_length=20, blank=True)  # visa, mastercard, etc.
    card_exp_month = models.IntegerField(null=True, blank=True)
    card_exp_year = models.IntegerField(null=True, blank=True)
    
    # External processor token
    external_method_id = models.CharField(max_length=200, blank=True)
    
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        if self.method_type == 'card' and self.card_last_four:
            return f"{self.card_brand} ****{self.card_last_four}"
        return f"{self.get_method_type_display()}"


class Invoice(models.Model):
    """Invoice generation for completed bookings"""
    invoice_number = models.CharField(max_length=20, unique=True)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='invoice')
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='invoice')
    
    # Invoice details
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Additional charges
    additional_charges = models.JSONField(default=list, blank=True)
    
    issued_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - Booking #{self.booking.id}"
