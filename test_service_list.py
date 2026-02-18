#!/usr/bin/env python
"""
Test the service list view to identify the template rendering error
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from services.views import service_list

User = get_user_model()

def test_service_list():
    """Test the service list view to identify template errors"""
    print("🔍 Testing Service List View...")
    
    # Create a mock request
    factory = RequestFactory()
    request = factory.get('/services/')
    
    # Try with anonymous user first
    try:
        response = service_list(request)
        print(f"✅ Anonymous user: Status {response.status_code}")
        if response.status_code == 200:
            print("✅ Template rendered successfully for anonymous user")
        else:
            print(f"❌ Error for anonymous user: {response.status_code}")
    except Exception as e:
        print(f"❌ Anonymous user error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Try with authenticated customer
    customer = User.objects.filter(role='customer').first()
    if customer:
        request.user = customer
        try:
            response = service_list(request)
            print(f"✅ Customer user: Status {response.status_code}")
            if response.status_code == 200:
                print("✅ Template rendered successfully for customer")
            else:
                print(f"❌ Error for customer: {response.status_code}")
        except Exception as e:
            print(f"❌ Customer user error: {str(e)}")
            import traceback
            traceback.print_exc()
    else:
        print("⚠️ No customer found for testing")

if __name__ == '__main__':
    test_service_list()
