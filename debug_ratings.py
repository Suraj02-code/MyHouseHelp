#!/usr/bin/env python
"""
Debug the rating scores to see what's happening
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

from django.contrib.auth import get_user_model
from ml_engine.recommendation_engine import recommendation_engine

User = get_user_model()

def debug_rating_scores():
    """Debug the rating scores to understand the issue"""
    print("🔍 DEBUGGING RATING SCORES")
    print("=" * 50)
    
    # Get providers and their ratings
    providers = User.objects.filter(role='provider').select_related('provider_profile')
    
    print("📊 Provider Rating Analysis:")
    print("-" * 40)
    
    for provider in providers:
        profile = provider.provider_profile
        rating_normalized = float(profile.average_rating) / 5.0 if profile.average_rating > 0 else 0.0
        review_bonus = min(float(profile.total_reviews) / 20.0, 0.1)
        final_rating_score = min(rating_normalized + review_bonus, 1.0)
        
        print(f"{provider.username}:")
        print(f"   Rating: {profile.average_rating}/5 → Normalized: {rating_normalized:.3f}")
        print(f"   Reviews: {profile.total_reviews} → Bonus: {review_bonus:.3f}")
        print(f"   Final Rating Score: {final_rating_score:.3f}")
        print()
    
    # Test the recommendation engine
    customer = User.objects.filter(role='customer').first()
    
    # Get candidate providers
    candidates = recommendation_engine._get_candidate_providers(None, None)
    
    # Get individual scores
    rating_scores = recommendation_engine._rating_based_scores(candidates)
    collaborative_scores = recommendation_engine._collaborative_filtering_scores(customer, candidates)
    content_scores = recommendation_engine._content_based_scores(customer, candidates, None)
    popularity_scores = recommendation_engine._popularity_scores(candidates)
    availability_scores = recommendation_engine._availability_scores(candidates)
    
    print("🎯 DETAILED SCORE BREAKDOWN:")
    print("-" * 50)
    
    for provider_id in candidates:
        provider = User.objects.get(id=provider_id)
        profile = provider.provider_profile
        
        print(f"\n{provider.username} (Rating: {profile.average_rating}/5):")
        print(f"   Rating Score: {rating_scores.get(provider_id, 0):.3f}")
        print(f"   Collaborative: {collaborative_scores.get(provider_id, 0):.3f}")
        print(f"   Content: {content_scores.get(provider_id, 0):.3f}")
        print(f"   Popularity: {popularity_scores.get(provider_id, 0):.3f}")
        print(f"   Availability: {availability_scores.get(provider_id, 0):.3f}")
        
        # Calculate final score with current weights (80% rating dominance)
        final_score = (
            rating_scores.get(provider_id, 0) * 0.80 +
            collaborative_scores.get(provider_id, 0) * 0.10 +
            content_scores.get(provider_id, 0) * 0.05 +
            popularity_scores.get(provider_id, 0) * 0.03 +
            availability_scores.get(provider_id, 0) * 0.02
        )
        print(f"   Final Score: {final_score:.3f}")

if __name__ == '__main__':
    debug_rating_scores()
