#!/usr/bin/env python
"""
Create test bookings and reviews to demonstrate recommendation engine
"""
import os
import django
import random
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

from bookings.models import Booking
from reviews.models import Review
from django.contrib.auth import get_user_model
from django.db.models import Count
from services.models import Service

User = get_user_model()

def create_test_bookings_and_reviews():
    """Create test bookings and reviews to demonstrate recommendation engine"""
    print("🎯 Creating Test Bookings and Reviews")
    print("=" * 50)
    
    # Get customers and providers
    customers = User.objects.filter(role='customer')[:3]
    providers = User.objects.filter(role='provider')[:5]
    services = Service.objects.filter(is_active=True)[:10]
    
    if not customers.exists() or not providers.exists():
        print("❌ Need at least 3 customers and 5 providers")
        return
    
    print(f"Found {customers.count()} customers, {providers.count()} providers, {services.count()} services")
    
    # Sample review data
    review_data = [
        {
            'title': 'Excellent Service!',
            'comment': 'The provider was very professional and completed the job perfectly. Highly recommend!',
            'pros': 'Professional attitude, Quality workmanship, On time',
            'cons': '',
            'ratings': (5, 5, 5, 5, 5)  # overall, quality, timeliness, communication, value
        },
        {
            'title': 'Very Professional',
            'comment': 'Great communication throughout the process. The provider knew exactly what to do.',
            'pros': 'Good communication, Expert knowledge, Clean work',
            'cons': 'Slightly expensive',
            'ratings': (4, 4, 5, 5, 4)
        },
        {
            'title': 'Good Experience',
            'comment': 'Reliable and trustworthy service. Would definitely hire again.',
            'pros': 'Punctual, Efficient work, Fair pricing',
            'cons': 'Could have been faster',
            'ratings': (4, 5, 4, 4, 4)
        },
        {
            'title': 'Outstanding Work!',
            'comment': 'The provider went above and beyond my expectations. Exceptional quality!',
            'pros': 'Attention to detail, Expert knowledge, Friendly service',
            'cons': '',
            'ratings': (5, 5, 5, 5, 5)
        },
        {
            'title': 'Great Value',
            'comment': 'Good quality service at a reasonable price. Very satisfied.',
            'pros': 'Fair pricing, Quality work, Professional',
            'cons': 'Minor delay in start',
            'ratings': (4, 4, 3, 4, 5)
        }
    ]
    
    created_bookings = []
    created_reviews = []
    
    # Create bookings and reviews
    for i, customer in enumerate(customers):
        for j, provider in enumerate(providers):
            if j >= 2 + i:  # Create varying number of bookings per customer
                break
                
            # Get a random service
            service = random.choice(services)
            
            # Create booking
            booking_date = datetime.now() - timedelta(days=random.randint(1, 30))
            booking_time = (datetime.now() - timedelta(hours=random.randint(8, 18))).time()
            
            booking = Booking.objects.create(
                customer=customer,
                provider=provider,
                service=service,
                status='completed',
                booking_date=booking_date.date(),
                booking_time=booking_time,
                service_address=f"Test Address for {customer.username}",
                quoted_price=service.base_price,
                final_price=service.base_price,
                special_instructions='Test booking for recommendation engine demo',
                completed_at=booking_date
            )
            
            created_bookings.append(booking)
            
            # Create review for the booking
            review_info = random.choice(review_data)
            ratings = review_info['ratings']
            
            review = Review.objects.create(
                booking=booking,
                customer=customer,
                provider=provider,
                overall_rating=ratings[0],
                quality_rating=ratings[1],
                timeliness_rating=ratings[2],
                communication_rating=ratings[3],
                value_rating=ratings[4],
                title=review_info['title'],
                comment=review_info['comment'],
                pros=review_info['pros'],
                cons=review_info['cons'],
                is_verified=True
            )
            
            created_reviews.append(review)
            print(f"✅ Booking: {customer.username} → {provider.username} ({service.title})")
            print(f"   Review: {ratings[0]}/5 - {review_info['title']}")
    
    print(f"\n🎉 Created {len(created_bookings)} bookings and {len(created_reviews)} reviews!")
    
    # Update provider ratings
    print("\n📊 Updating Provider Ratings...")
    for provider in providers:
        provider.provider_profile.update_rating()
        print(f"✅ {provider.username}: {provider.provider_profile.total_reviews} reviews, {provider.provider_profile.average_rating}/5 rating")
    
    return created_reviews

def demonstrate_recommendation_ranking():
    """Show how most reviewed providers rank higher"""
    print("\n" + "=" * 60)
    print("🏆 RECOMMENDATION ENGINE - Most Reviewed at Top")
    print("=" * 60)
    
    from ml_engine.recommendation_engine import recommendation_engine
    
    # Test with different customers
    customers = User.objects.filter(role='customer')[:3]
    
    for customer in customers:
        print(f"\n👤 Recommendations for {customer.username}:")
        print("-" * 40)
        
        recommendations = recommendation_engine.get_provider_recommendations(
            customer=customer,
            max_recommendations=5
        )
        
        for i, rec in enumerate(recommendations, 1):
            provider = rec['provider']
            profile = provider.provider_profile
            
            print(f"{i}. {provider.username}")
            print(f"   📊 Reviews: {profile.total_reviews} | ⭐ Rating: {profile.average_rating}/5")
            print(f"   🎯 Total Score: {rec['final_score']:.3f}")
            print(f"   📈 Popularity: {rec['score_breakdown']['popularity']:.3f}")
            
            # Show why this provider ranks here
            if profile.total_reviews >= 3:
                print(f"   🔥 TOP RATED: Most reviews!")
            elif profile.total_reviews >= 2:
                print(f"   ⭐ GOOD: Multiple reviews")
            else:
                print(f"   📝 NEW: Fewer reviews")
            print()

def show_popularity_calculation():
    """Show exactly how popularity scores are calculated"""
    print("\n" + "=" * 60)
    print("📊 POPULARITY SCORE CALCULATION DETAILS")
    print("=" * 60)
    
    providers = User.objects.filter(role='provider').annotate(
        review_count=Count('reviews_received')
    ).order_by('-review_count')
    
    print("Formula: Popularity = (Recent Bookings × 0.6) + (Review Count × 0.4)")
    print("-" * 60)
    
    for provider in providers:
        profile = provider.provider_profile
        
        # Calculate recent bookings (last 30 days)
        recent_bookings = Booking.objects.filter(
            provider=provider,
            status='completed',
            completed_at__gte=datetime.now() - timedelta(days=30)
        ).count()
        
        # Calculate scores
        booking_score = min(recent_bookings / 20.0, 1.0)  # Max 20 bookings = 1.0
        review_score = min(profile.total_reviews / 50.0, 1.0)  # Max 50 reviews = 1.0
        popularity_score = booking_score * 0.6 + review_score * 0.4
        
        print(f"\n🏢 {provider.username}:")
        print(f"   Recent Bookings: {recent_bookings} → Score: {booking_score:.3f} (×0.6 = {booking_score*0.6:.3f})")
        print(f"   Total Reviews: {profile.total_reviews} → Score: {review_score:.3f} (×0.4 = {review_score*0.4:.3f})")
        print(f"   🎯 FINAL POPULARITY: {popularity_score:.3f}")
        
        # Show ranking
        if popularity_score >= 0.8:
            print("   🔥 VERY HIGH POPULARITY")
        elif popularity_score >= 0.5:
            print("   ⭐ HIGH POPULARITY")
        elif popularity_score >= 0.2:
            print("   📈 MODERATE POPULARITY")
        else:
            print("   📝 LOW POPULARITY")

if __name__ == '__main__':
    reviews = create_test_bookings_and_reviews()
    if reviews:
        demonstrate_recommendation_ranking()
        show_popularity_calculation()
        
        print(f"\n🎯 KEY INSIGHT:")
        print("=" * 50)
        print("✅ Most reviewed providers rank HIGHER in recommendations")
        print("✅ Popularity score heavily influences final ranking")
        print("✅ Recent bookings also boost popularity")
        print("✅ The system learns from real user feedback!")
        
        print(f"\n🌐 View in browser:")
        print("   http://127.0.0.1:8000/services/recommendations/")
    else:
        print("❌ Could not create test data")
