#!/usr/bin/env python
"""
Test script for the ML recommendation system
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

from django.contrib.auth import get_user_model
from services.models import Service, ServiceCategory
from ml_engine.recommendation_engine import recommendation_engine, service_recommendation_engine

User = get_user_model()

def test_recommendation_system():
    """Test the recommendation system with sample data"""
    print("🤖 Testing ML Recommendation System")
    print("=" * 50)
    
    # Check if we have users
    customers = User.objects.filter(role='customer')
    providers = User.objects.filter(role='provider')
    
    print(f"Found {customers.count()} customers and {providers.count()} providers")
    
    if not customers.exists():
        print("❌ No customers found. Creating test customer...")
        customer = User.objects.create_user(
            username='test_customer',
            email='customer@test.com',
            password='testpass123',
            role='customer',
            address='Test Address'
        )
        # Create customer profile
        from accounts.models import CustomerProfile
        CustomerProfile.objects.create(
            user=customer,
            preferred_services='cleaning,plumbing'
        )
        customers = User.objects.filter(role='customer')
    
    if not providers.exists():
        print("❌ No providers found. Creating test provider...")
        provider = User.objects.create_user(
            username='test_provider',
            email='provider@test.com',
            password='testpass123',
            role='provider',
            is_verified=True
        )
        # Create provider profile
        from accounts.models import ServiceProviderProfile
        ServiceProviderProfile.objects.create(
            user=provider,
            business_name='Test Service Company',
            description='Professional cleaning and plumbing services',
            years_of_experience=5,
            verification_status='verified',
            average_rating=4.5,
            total_reviews=10,
            completed_jobs=25
        )
        providers = User.objects.filter(role='provider')
    
    # Check if we have services
    services = Service.objects.filter(is_active=True)
    print(f"Found {services.count()} active services")
    
    if not services.exists():
        print("❌ No services found. Creating test services...")
        # Create test category
        category, created = ServiceCategory.objects.get_or_create(
            name='Cleaning',
            defaults={'description': 'Professional cleaning services'}
        )
        
        provider = providers.first()
        if provider:
            Service.objects.create(
                provider=provider,
                category=category,
                title='Home Cleaning Service',
                description='Professional home cleaning',
                base_price=50.00,
                price_unit='per_hour'
            )
            services = Service.objects.filter(is_active=True)
    
    # Test recommendations for first customer
    if customers.exists() and providers.exists():
        customer = customers.first()
        print(f"\n🎯 Testing recommendations for customer: {customer.username}")
        
        try:
            # Test provider recommendations
            recommendations = recommendation_engine.get_provider_recommendations(
                customer=customer,
                max_recommendations=5
            )
            
            print(f"✅ Generated {len(recommendations)} provider recommendations")
            for i, rec in enumerate(recommendations[:3], 1):
                print(f"  {i}. {rec['provider'].username} - Score: {rec['final_score']:.3f}")
            
            # Test service recommendations
            service_recs = service_recommendation_engine.get_service_recommendations(
                customer=customer,
                max_recommendations=5
            )
            
            print(f"✅ Generated {len(service_recs)} service recommendations")
            for i, rec in enumerate(service_recs[:3], 1):
                print(f"  {i}. {rec['service'].title} - Score: {rec['score']:.3f}")
            
        except Exception as e:
            print(f"❌ Error testing recommendations: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n🎉 Recommendation system test completed!")
    
    # Test API endpoints
    print("\n📡 Testing API endpoints...")
    print("To test the API endpoints:")
    print("1. Start the development server: python manage.py runserver")
    print("2. Login as a customer and visit: http://127.0.0.1:8000/services/recommendations/")
    print("3. Or test API: http://127.0.0.1:8000/ml_engine/api/recommendations/")

if __name__ == '__main__':
    test_recommendation_system()
