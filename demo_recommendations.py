#!/usr/bin/env python
"""
Live demonstration of the ML recommendation system
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

from django.contrib.auth import get_user_model
from ml_engine.recommendation_engine import recommendation_engine

User = get_user_model()

def demonstrate_recommendations():
    """Show how the recommendation system works in detail"""
    print("🤖 ML Recommendation System Live Demo")
    print("=" * 60)
    
    # Get a customer
    customer = User.objects.filter(role='customer').first()
    if not customer:
        print("❌ No customer found. Please create a customer account first.")
        return
    
    print(f"👤 Customer: {customer.username}")
    print(f"📧 Email: {customer.email}")
    print(f"📍 Address: {customer.address or 'Not set'}")
    
    # Get customer preferences
    from accounts.models import CustomerProfile
    profile = getattr(customer, 'customer_profile', None)
    if profile:
        print(f"❤️  Preferred Services: {profile.preferred_services or 'Not set'}")
        print(f"🎯 Loyalty Points: {profile.loyalty_points}")
        print(f"📊 Total Bookings: {profile.total_bookings}")
    
    print("\n" + "=" * 60)
    print("🎯 GENERATING RECOMMENDATIONS...")
    print("=" * 60)
    
    # Get recommendations
    recommendations = recommendation_engine.get_provider_recommendations(
        customer=customer,
        max_recommendations=5
    )
    
    print(f"\n✅ Generated {len(recommendations)} personalized recommendations:\n")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"🏆 RECOMMENDATION #{i}")
        print(f"📋 Provider: {rec['provider'].username}")
        print(f"🏢 Business: {rec['provider_profile'].business_name}")
        print(f"⭐ Rating: {rec['provider_profile'].average_rating}/5 ({rec['provider_profile'].total_reviews} reviews)")
        print(f"💼 Experience: {rec['provider_profile'].years_of_experience} years")
        print(f"✅ Completed Jobs: {rec['provider_profile'].completed_jobs}")
        print(f"🎯 Match Score: {rec['final_score']:.3f}")
        
        print("\n📊 Score Breakdown:")
        breakdown = rec['score_breakdown']
        print(f"   • Compatibility (Content-based): {breakdown['content_based']:.3f} (35% weight)")
        print(f"   • Similar Users (Collaborative): {breakdown['collaborative']:.3f} (35% weight)")
        print(f"   • Popularity: {breakdown['popularity']:.3f} (20% weight)")
        print(f"   • Availability: {breakdown['availability']:.3f} (15% weight)")
        
        if rec['services']:
            print(f"\n🔧 Services Offered:")
            for service in rec['services'][:3]:
                print(f"   • {service['title']} - {service['category__name']} (${service['base_price']})")
        
        print("\n" + "-" * 50)
    
    # Show how the scoring works
    print("\n" + "=" * 60)
    print("🧮 HOW SCORING WORKS")
    print("=" * 60)
    
    print("\n1️⃣  COLLABORATIVE FILTERING (35% weight)")
    print("   • Finds customers with similar booking patterns")
    print("   • Uses Jaccard similarity on providers and categories")
    print("   • Higher score if similar customers liked this provider")
    
    print("\n2️⃣  CONTENT-BASED FILTERING (35% weight)")
    print("   • Matches provider attributes to customer preferences")
    print("   • Considers ratings, experience, completion rates")
    print("   • Text similarity on descriptions and service titles")
    
    print("\n3️⃣  POPULARITY SCORING (20% weight)")
    print("   • Recent booking frequency (last 30 days)")
    print("   • Total review count")
    print("   • Provider reputation and demand")
    
    print("\n4️⃣  AVAILABILITY SCORING (15% weight)")
    print("   • Current availability status")
    print("   • Number of available time slots")
    print("   • Service area coverage")
    
    print("\n" + "=" * 60)
    print("🎉 RECOMMENDATION SYSTEM WORKING!")
    print("=" * 60)
    print("\n💡 To see this in the web interface:")
    print("   1. Visit: http://127.0.0.1:8000/services/")
    print("   2. Login as a customer")
    print("   3. Look for the '🤖 Recommended Providers' section")
    print("   4. Click 'Why?' to see score breakdowns")

if __name__ == '__main__':
    demonstrate_recommendations()
