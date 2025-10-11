from django.contrib import admin
from .models import Booking, BookingStatusHistory, BookingCancellation


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'provider', 'service', 'booking_date', 'status', 'priority')
    list_filter = ('status', 'priority', 'booking_date', 'created_at')
    search_fields = ('customer__username', 'provider__username', 'service__title')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'booking_date'


@admin.register(BookingStatusHistory)
class BookingStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('booking', 'old_status', 'new_status', 'changed_by', 'changed_at')
    list_filter = ('old_status', 'new_status', 'changed_at')
    search_fields = ('booking__id', 'changed_by__username')
    readonly_fields = ('changed_at',)


@admin.register(BookingCancellation)
class BookingCancellationAdmin(admin.ModelAdmin):
    list_display = ('booking', 'cancelled_by', 'refund_amount', 'cancelled_at')
    search_fields = ('booking__id', 'cancelled_by__username')
    readonly_fields = ('cancelled_at',)
