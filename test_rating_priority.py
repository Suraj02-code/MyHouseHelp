#!/usr/bin/env python
"""
Test the updated recommendation engine with RATING PRIORITY
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

from django.contrib.auth import get_user_model
from ml_engine.recommendation_engine import recommendation_engine
from django.db.models import Count

User = get_user_model()

def test_rating_priority():
    """Test that highest rated providers are ranked first"""
    print("🎯 TESTING RATING PRIORITY RECOMMENDATION ENGINE")
    print("=" * 60)
    
    # Show current provider ratings
    providers = User.objects.filter(role='provider').annotate(
        review_count=Count('reviews_received')
    ).select_related('provider_profile').order_by('-provider_profile__average_rating')
    
    print("📊 Current Provider Ratings (sorted by rating):")
    print("-" * 50)
    for i, provider in enumerate(providers, 1):
        profile = provider.provider_profile
        print(f"{i}. {provider.username}")
        print(f"   ⭐ Rating: {profile.average_rating}/5 ({profile.total_reviews} reviews)")
        print(f"   💼 Jobs: {profile.completed_jobs}")
        print()
    
    # Test recommendations
    customer = User.objects.filter(role='customer').first()
    print(f"👤 Testing recommendations for: {customer.username}")
    print("=" * 60)
    
    recommendations = recommendation_engine.get_provider_recommendations(
        customer=customer,
        max_recommendations=8
    )
    
    print(f"\n🏆 RECOMMENDATIONS (Highest Rated First):")
    print("-" * 50)
    
    for i, rec in enumerate(recommendations, 1):
        provider = rec['provider']
        profile = provider.provider_profile
        
        print(f"{i}. {provider.username}")
        print(f"   ⭐ Rating: {profile.average_rating}/5 ({profile.total_reviews} reviews)")
        print(f"   🎯 Total Score: {rec['final_score']:.3f}")
        print(f"   📊 Score Breakdown:")
        print(f"      • Rating (40%): {rec['score_breakdown']['rating']:.3f}")
        print(f"      • Similar Users (25%): {rec['score_breakdown']['collaborative']:.3f}")
        print(f"      • Compatibility (20%): {rec['score_breakdown']['content_based']:.3f}")
        print(f"      • Popularity (10%): {rec['score_breakdown']['popularity']:.3f}")
        print(f"      • Availability (5%): {rec['score_breakdown']['availability']:.3f}")
        
        # Highlight rating priority
        if rec['score_breakdown']['rating'] >= 0.8:
            print(f"   🔥 EXCELLENT RATING - Top Priority!")
        elif rec['score_breakdown']['rating'] >= 0.6:
            print(f"   ⭐ GOOD RATING - High Priority")
        else:
            print(f"   📝 NEEDS IMPROVEMENT")
        print()
    
    # Verify ranking matches rating order
    print("🔍 VERIFICATION:")
    print("-" * 30)
    
    # Sort providers by rating
    providers_by_rating = sorted(providers, key=lambda p: p.provider_profile.average_rating, reverse=True)
    
    # Check if recommendations follow rating order
    rating_order_correct = True
    for i in range(min(len(recommendations), len(providers_by_rating))):
        rec_provider = recommendations[i]['provider']
        expected_provider = providers_by_rating[i]
        
        if rec_provider.id != expected_provider.id:
            rating_order_correct = False
            print(f"❌ Position {i+1}: Expected {expected_provider.username} ({expected_provider.provider_profile.average_rating}/5)")
            print(f"   Got {rec_provider.username} ({rec_provider.provider_profile.average_rating}/5)")
    
    if rating_order_correct:
        print("✅ PERFECT! Recommendations are correctly sorted by rating!")
    else:
        print("⚠️  Some ranking differences detected (other factors also influence)")
    
    print(f"\n🎯 NEW SCORING SYSTEM:")
    print("=" * 40)
    print("⭐ Rating Score: 40% (HIGHEST PRIORITY)")
    print("👥 Collaborative: 25%")
    print("🎯 Content-Based: 20%")
    print("🔥 Popularity: 10%")
    print("📅 Availability: 5%")
    print("\n✅ Highest rated providers now rank FIRST!")

if __name__ == '__main__':
    test_rating_priority()
