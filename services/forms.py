from django import forms
from .models import Service, ServiceCategory, ServiceAvailability, ServiceArea


class ServiceForm(forms.ModelForm):
    """Form for creating/editing services"""
    
    class Meta:
        model = Service
        fields = (
            'category', 'title', 'description', 'base_price', 'price_unit',
            'duration_hours', 'service_image', 'requires_quote', 'is_active'
        )
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'base_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            }),
            'price_unit': forms.Select(attrs={'class': 'form-control'}),
            'duration_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0.5',
                'step': '0.5'
            }),
            'service_image': forms.FileInput(attrs={'class': 'form-control'}),
            'requires_quote': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = ServiceCategory.objects.filter(is_active=True)
        
        # Add help text
        self.fields['title'].help_text = 'Give your service a clear, descriptive title'
        self.fields['description'].help_text = 'Describe what your service includes in detail'
        self.fields['base_price'].help_text = 'Starting price for this service'
        self.fields['duration_hours'].help_text = 'Estimated time to complete this service'
        self.fields['requires_quote'].help_text = 'Check if this service needs a custom quote'


class ServiceAvailabilityForm(forms.ModelForm):
    """Form for managing service availability"""
    
    class Meta:
        model = ServiceAvailability
        fields = ('day_of_week', 'start_time', 'end_time', 'is_available')
        widgets = {
            'day_of_week': forms.Select(attrs={'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time:
            if start_time >= end_time:
                raise forms.ValidationError("End time must be after start time.")
        
        return cleaned_data


class ServiceSearchForm(forms.Form):
    """Form for service search and filtering"""
    
    SORT_CHOICES = [
        ('created_at', 'Newest First'),
        ('price_low', 'Price: Low to High'),
        ('price_high', 'Price: High to Low'),
        ('rating', 'Highest Rated'),
        ('popular', 'Most Popular'),
    ]
    
    search = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search services...'
        })
    )
    category = forms.ModelChoiceField(
        queryset=ServiceCategory.objects.filter(is_active=True),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    min_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min Price',
            'min': '0'
        })
    )
    max_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max Price',
            'min': '0'
        })
    )
    sort = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class ServiceAreaForm(forms.ModelForm):
    """Form for managing service areas"""
    
    class Meta:
        model = ServiceArea
        fields = ('area_name', 'postal_code', 'latitude', 'longitude')
        widgets = {
            'area_name': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': 'any'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': 'any'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['area_name'].help_text = 'Name of the area you serve (e.g., Downtown, North Side)'
        self.fields['postal_code'].help_text = 'Postal/ZIP code for this area'
        self.fields['latitude'].help_text = 'Latitude coordinate (optional)'
        self.fields['longitude'].help_text = 'Longitude coordinate (optional)'