#!/usr/bin/env python
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

from accounts.models import User, ServiceProviderProfile
from accounts.forms import UserRegistrationForm

def test_provider_registration():
    print("Testing Provider Registration...")
    
    # Test form data
    form_data = {
        'username': 'testprovider',
        'first_name': 'John',
        'last_name': 'Doe', 
        'email': 'john.provider@test.com',
        'phone_number': '+1234567890',
        'address': '123 Test Street, Test City',
        'role': 'provider',
        'password1': 'testpass123',
        'password2': 'testpass123'
    }
    
    try:
        # Test form validation
        form = UserRegistrationForm(data=form_data)
        if form.is_valid():
            print("✅ Form is valid")
            
            # Test user creation
            user = form.save()
            print(f"✅ User created: {user.username} with role: {user.role}")
            
            # Check if provider profile was created
            try:
                provider_profile = ServiceProviderProfile.objects.get(user=user)
                print(f"✅ Provider profile created: {provider_profile.business_name}")
                print(f"   - Description: {provider_profile.description}")
                print(f"   - Experience: {provider_profile.years_of_experience} years")
                print(f"   - Status: {provider_profile.verification_status}")
                print(f"   - Available: {provider_profile.is_available}")
            except ServiceProviderProfile.DoesNotExist:
                print("❌ Provider profile not created")
            
            print("✅ Registration completed successfully!")
            
        else:
            print("❌ Form validation failed:")
            for field, errors in form.errors.items():
                print(f"   {field}: {errors}")
                
    except Exception as e:
        print(f"❌ Error during registration: {e}")
        import traceback
        traceback.print_exc()

def test_database_connectivity():
    print("\nTesting Database Connectivity...")
    try:
        # Test basic database operations
        user_count = User.objects.count()
        provider_count = ServiceProviderProfile.objects.count()
        print(f"✅ Database accessible")
        print(f"   - Total users: {user_count}")
        print(f"   - Total providers: {provider_count}")
        
        # Check if admin user exists
        if User.objects.filter(username='admin1').exists():
            admin_user = User.objects.get(username='admin1')
            print(f"✅ Admin user found: {admin_user.username} (Role: {admin_user.role})")
        
    except Exception as e:
        print(f"❌ Database error: {e}")

def test_urls():
    print("\nTesting URL patterns...")
    try:
        from django.urls import reverse
        
        # Test critical URLs
        urls_to_test = [
            ('home', None),
            ('accounts:register', None),
            ('accounts:login', None),
            ('accounts:provider_dashboard', None),
            ('services:my_services', None),
        ]
        
        for url_name, args in urls_to_test:
            try:
                url = reverse(url_name, args=args)
                print(f"✅ URL '{url_name}' resolves to: {url}")
            except Exception as e:
                print(f"❌ URL '{url_name}' failed: {e}")
                
    except Exception as e:
        print(f"❌ URL testing failed: {e}")

if __name__ == '__main__':
    test_database_connectivity()
    test_urls()
    test_provider_registration()