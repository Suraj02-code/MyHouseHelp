#!/usr/bin/env python
"""
Create random reviews for bookings and test recommendation engine
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

User = get_user_model()

def create_random_reviews():
    """Create realistic random reviews for existing bookings"""
    print("🎯 Creating Random Reviews for Bookings")
    print("=" * 50)
    
    # Sample review data
    review_titles = [
        "Excellent Service!", "Very Professional", "Great Experience",
        "Highly Recommended", "Outstanding Work", "Very Satisfied",
        "Good Quality", "Professional Service", "On Time", "Great Value"
    ]
    
    review_comments = [
        "The provider was very professional and completed the job on time. Very satisfied with the service.",
        "Excellent work quality! The provider knew exactly what they were doing and gave helpful advice.",
        "Great communication throughout the process. Would definitely recommend to others.",
        "Very punctual and efficient. The job was completed to my satisfaction.",
        "Professional service with attention to detail. The provider was courteous and skilled.",
        "Good value for money. The service was exactly what I needed.",
        "The provider went above and beyond my expectations. Very impressed!",
        "Clean and efficient work. Would hire again for future projects.",
        "Reliable and trustworthy. The provider explained everything clearly.",
        "Exceptional service from start to finish. Highly recommend!"
    ]
    
    pros_examples = [
        "Professional attitude", "On time arrival", "Quality workmanship",
        "Good communication", "Fair pricing", "Clean work area", "Expert knowledge",
        "Friendly service", "Efficient work", "Attention to detail"
    ]
    
    cons_examples = [
        "Could have been faster", "Slightly expensive", "Minor delay in start",
        "Could explain more", "Left small mess", "Limited availability",
        "Basic tools only", "Could be more detailed", "Arrived a bit late", "Communication could be better"
    ]
    
    # Get bookings without reviews
    bookings_without_reviews = Booking.objects.filter(
        status='completed'
    ).exclude(
        id__in=Review.objects.values_list('booking_id', flat=True)
    )
    
    print(f"Found {bookings_without_reviews.count()} completed bookings without reviews")
    
    if not bookings_without_reviews.exists():
        print("❌ No completed bookings found without reviews")
        return
    
    created_reviews = []
    
    for booking in bookings_without_reviews:
        # Generate random review data
        overall_rating = random.randint(3, 5)  # Bias toward positive reviews
        quality_rating = random.randint(3, 5)
        timeliness_rating = random.randint(3, 5)
        communication_rating = random.randint(3, 5)
        value_rating = random.randint(3, 5)
        
        # Create review
        review = Review.objects.create(
            booking=booking,
            customer=booking.customer,
            provider=booking.provider,
            overall_rating=overall_rating,
            quality_rating=quality_rating,
            timeliness_rating=timeliness_rating,
            communication_rating=communication_rating,
            value_rating=value_rating,
            title=random.choice(review_titles),
            comment=random.choice(review_comments),
            pros=random.choice(pros_examples),
            cons=random.choice(cons_examples) if random.random() < 0.3 else "",  # 30% chance of cons
            is_verified=True
        )
        
        created_reviews.append(review)
        print(f"✅ Created review for {booking.customer.username} → {booking.provider.username}")
        print(f"   Rating: {overall_rating}/5 | {review.title}")
    
    print(f"\n🎉 Created {len(created_reviews)} random reviews!")
    
    # Update provider ratings
    print("\n📊 Updating Provider Ratings...")
    providers_updated = set()
    for review in created_reviews:
        if review.provider not in providers_updated:
            review.provider.provider_profile.update_rating()
            providers_updated.add(review.provider)
            print(f"✅ Updated {review.provider.username}'s rating: {review.provider.provider_profile.average_rating}/5")
    
    return created_reviews

def test_recommendations_with_reviews():
    """Test recommendation engine after adding reviews"""
    print("\n" + "=" * 60)
    print("🎯 TESTING RECOMMENDATIONS WITH NEW REVIEWS")
    print("=" * 60)
    
    from ml_engine.recommendation_engine import recommendation_engine
    
    # Get a customer
    customer = User.objects.filter(role='customer').first()
    print(f"\n👤 Testing recommendations for: {customer.username}")
    
    # Get recommendations
    recommendations = recommendation_engine.get_provider_recommendations(
        customer=customer,
        max_recommendations=5
    )
    
    print(f"\n📈 Top 5 Recommendations (Most Reviewed at Top):")
    print("-" * 50)
    
    for i, rec in enumerate(recommendations, 1):
        provider = rec['provider']
        profile = provider.provider_profile
        
        print(f"\n🏆 #{i} {provider.username}")
        print(f"   📊 Total Reviews: {profile.total_reviews}")
        print(f"   ⭐ Average Rating: {profile.average_rating}/5")
        print(f"   💼 Completed Jobs: {profile.completed_jobs}")
        print(f"   🎯 Match Score: {rec['final_score']:.3f}")
        print(f"   📈 Popularity Score: {rec['score_breakdown']['popularity']:.3f}")
        
        # Show recent reviews for this provider
        recent_reviews = Review.objects.filter(provider=provider).order_by('-created_at')[:2]
        if recent_reviews:
            print("   💬 Recent Reviews:")
            for review in recent_reviews:
                print(f"      • {review.overall_rating}/5 - {review.title}")
    
    # Show how popularity scoring works
    print(f"\n" + "=" * 60)
    print("📊 POPULARITY SCORING BREAKDOWN")
    print("=" * 60)
    
    print("Popularity Score = (Recent Bookings × 0.6) + (Review Count × 0.4)")
    print("• Recent Bookings: Bookings in last 30 days (max 20)")
    print("• Review Count: Total number of reviews (max 50)")
    print("• Higher popularity = Higher recommendation ranking")
    
    # Show provider statistics
    print(f"\n📈 Provider Statistics (sorted by review count):")
    print("-" * 50)
    
    providers = User.objects.filter(role='provider').annotate(
        review_count=Count('reviews_received')
    ).order_by('-review_count')
    
    for provider in providers[:5]:
        profile = provider.provider_profile
        recent_bookings = Booking.objects.filter(
            provider=provider,
            status='completed',
            created_at__gte=datetime.now() - timedelta(days=30)
        ).count()
        
        booking_score = min(recent_bookings / 20.0, 1.0)
        review_score = min(profile.total_reviews / 50.0, 1.0)
        popularity_score = booking_score * 0.6 + review_score * 0.4
        
        print(f"{provider.username}:")
        print(f"  • Reviews: {profile.total_reviews} (score: {review_score:.3f})")
        print(f"  • Recent Bookings: {recent_bookings} (score: {booking_score:.3f})")
        print(f"  • Total Popularity: {popularity_score:.3f}")
        print()

if __name__ == '__main__':
    reviews = create_random_reviews()
    if reviews:
        test_recommendations_with_reviews()
    else:
        print("⚠️  No reviews were created. Please check if you have completed bookings.")
