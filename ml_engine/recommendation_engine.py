from django.db.models import Avg, Count, Q, F
from django.utils import timezone
from typing import List, Dict, Tuple, Optional
import logging
import math

from accounts.models import User, CustomerProfile, ServiceProviderProfile
from services.models import Service, ServiceCategory
from reviews.models import Review
from bookings.models import Booking

logger = logging.getLogger(__name__)


class SimpleMinMaxScaler:
    """Simple MinMaxScaler implementation"""
    
    def fit_transform(self, values):
        """Fit and transform values to 0-1 range"""
        if not values:
            return values
        
        min_val = min(values)
        max_val = max(values)
        
        if max_val == min_val:
            return [0.5] * len(values)  # All values become 0.5 if no variation
        
        return [(val - min_val) / (max_val - min_val) for val in values]


class RecommendationEngine:
    """
    Hybrid recommendation engine combining collaborative filtering and content-based filtering
    """
    
    def __init__(self):
        # Simple min-max scaler implementation
        self.scaler = SimpleMinMaxScaler()
        
    def get_provider_recommendations(
        self, 
        customer: User, 
        service_category: Optional[str] = None,
        location: Optional[str] = None,
        max_recommendations: int = 10
    ) -> List[Dict]:
        """
        Get personalized provider recommendations for a customer
        
        Args:
            customer: Customer user object
            service_category: Optional service category filter
            location: Optional location filter
            max_recommendations: Maximum number of recommendations
            
        Returns:
            List of recommendation dictionaries with scores and details
        """
        try:
            # Get base candidate providers
            candidates = self._get_candidate_providers(service_category, location)
            
            if not candidates:
                return []
            
            # Calculate different recommendation scores
            collaborative_scores = self._collaborative_filtering_scores(customer, candidates)
            content_scores = self._content_based_scores(customer, candidates, service_category)
            rating_scores = self._rating_based_scores(candidates)  # NEW: Dedicated rating score
            popularity_scores = self._popularity_scores(candidates)
            availability_scores = self._availability_scores(candidates)
            
            # Combine scores with weights
            final_scores = self._combine_scores(
                collaborative_scores,
                content_scores,
                rating_scores,  # NEW: Include rating scores
                popularity_scores,
                availability_scores
            )
            
            # Sort by final score and create recommendation list
            recommendations = []
            for provider_id, score_data in sorted(final_scores.items(), 
                                                key=lambda x: x[1]['final_score'], 
                                                reverse=True)[:max_recommendations]:
                
                provider = User.objects.get(id=provider_id)
                recommendations.append({
                    'provider': provider,
                    'provider_profile': provider.provider_profile,
                    'final_score': round(score_data['final_score'], 4),
                    'score_breakdown': {
                        'rating': round(score_data['rating'], 4),           # NEW: Rating score
                        'collaborative': round(score_data['collaborative'], 4),
                        'content_based': round(score_data['content_based'], 4),
                        'popularity': round(score_data['popularity'], 4),
                        'availability': round(score_data['availability'], 4)
                    },
                    'services': list(provider.services_offered.filter(
                        is_active=True,
                        category__name=service_category if service_category else None
                    ).values('id', 'title', 'base_price', 'category__name'))
                })
            
            # Save recommendations to database
            self._save_recommendations(customer, recommendations, service_category)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations for customer {customer.id}: {str(e)}")
            return []
    
    def _get_candidate_providers(self, service_category: Optional[str], 
                               location: Optional[str]) -> List[int]:
        """Get list of candidate provider IDs based on filters"""
        queryset = User.objects.filter(
            role='provider',
            provider_profile__verification_status='verified',
            provider_profile__is_available=True,
            is_active=True
        )
        
        if service_category:
            queryset = queryset.filter(
                services_offered__category__name=service_category,
                services_offered__is_active=True
            )
        
        return list(queryset.distinct().values_list('id', flat=True))
    
    def _collaborative_filtering_scores(self, customer: User, 
                                      candidate_providers: List[int]) -> Dict[int, float]:
        """
        Calculate collaborative filtering scores based on similar users' preferences
        """
        scores = {}
        
        try:
            # Get customer's booking history
            customer_bookings = Booking.objects.filter(
                customer=customer,
                status='completed'
            ).select_related('provider', 'service')
            
            if not customer_bookings:
                # New user - return zero scores
                return {pid: 0.0 for pid in candidate_providers}
            
            # Find similar customers based on booking patterns
            customer_providers = set(b.provider.id for b in customer_bookings)
            customer_categories = set(b.service.category.name for b in customer_bookings)
            
            # Calculate similarity scores for other customers
            similar_customers = []
            for other_customer in User.objects.filter(role='customer').exclude(id=customer.id):
                other_bookings = Booking.objects.filter(
                    customer=other_customer,
                    status='completed'
                ).select_related('provider', 'service')
                
                if not other_bookings:
                    continue
                
                other_providers = set(b.provider.id for b in other_bookings)
                other_categories = set(b.service.category.name for b in other_bookings)
                
                # Jaccard similarity
                provider_similarity = len(customer_providers & other_providers) / len(customer_providers | other_providers) if customer_providers | other_providers else 0
                category_similarity = len(customer_categories & other_categories) / len(customer_categories | other_categories) if customer_categories | other_categories else 0
                
                overall_similarity = (provider_similarity * 0.7 + category_similarity * 0.3)
                
                if overall_similarity > 0:
                    similar_customers.append((other_customer, overall_similarity))
            
            # Sort by similarity and take top 20
            similar_customers.sort(key=lambda x: x[1], reverse=True)
            similar_customers = similar_customers[:20]
            
            # Calculate scores for candidate providers
            for provider_id in candidate_providers:
                score = 0.0
                total_weight = 0.0
                
                for similar_customer, similarity_weight in similar_customers:
                    # Check if similar customer booked this provider
                    if Booking.objects.filter(
                        customer=similar_customer,
                        provider_id=provider_id,
                        status='completed'
                    ).exists():
                        # Get rating if available
                        review = Review.objects.filter(
                            customer=similar_customer,
                            provider_id=provider_id
                        ).first()
                        
                        if review:
                            rating_score = review.overall_rating / 5.0  # Normalize to 0-1
                        else:
                            rating_score = 0.7  # Default positive assumption
                        
                        score += similarity_weight * rating_score
                        total_weight += similarity_weight
                
                # Normalize score
                scores[provider_id] = score / total_weight if total_weight > 0 else 0.0
            
            # Apply MinMax scaling
            if scores:
                score_values = list(scores.values())
                scaled_scores = self.scaler.fit_transform(score_values)
                scores = dict(zip(scores.keys(), scaled_scores))
            
        except Exception as e:
            logger.error(f"Error in collaborative filtering: {str(e)}")
            scores = {pid: 0.0 for pid in candidate_providers}
        
        return scores
    
    def _content_based_scores(self, customer: User, candidate_providers: List[int],
                            service_category: Optional[str]) -> Dict[int, float]:
        """
        Calculate content-based scores based on provider attributes and customer preferences
        """
        scores = {}
        
        try:
            # Get customer profile
            customer_profile = getattr(customer, 'customer_profile', None)
            customer_preferences = []
            
            if customer_profile and customer_profile.preferred_services:
                customer_preferences = [pref.strip().lower() 
                                      for pref in customer_profile.preferred_services.split(',')]
            
            # Get customer's location
            customer_location = customer.address if customer.address else ""
            
            for provider_id in candidate_providers:
                provider = User.objects.get(id=provider_id)
                provider_profile = provider.provider_profile
                
                score = 0.0
                
                # 1. Service category match
                if service_category:
                    category_match = provider.services_offered.filter(
                        category__name=service_category,
                        is_active=True
                    ).exists()
                    score += 0.3 if category_match else 0.0
                
                # 2. Provider rating
                if provider_profile.average_rating > 0:
                    rating_score = min(float(provider_profile.average_rating) / 5.0, 1.0)
                    score += rating_score * 0.25
                
                # 3. Experience
                experience_score = min(float(provider_profile.years_of_experience) / 10.0, 1.0)
                score += experience_score * 0.15
                
                # 4. Completion rate
                if provider_profile.completed_jobs > 0:
                    completion_score = min(float(provider_profile.completed_jobs) / 50.0, 1.0)
                    score += completion_score * 0.15
                
                # 5. Text similarity (description matching)
                provider_text = f"{provider_profile.description} {' '.join([service.title for service in provider.services_offered.all()])}".lower()
                
                if customer_preferences:
                    # Simple keyword matching
                    preference_matches = sum(1 for pref in customer_preferences 
                                          if pref in provider_text)
                    text_score = min(preference_matches / len(customer_preferences), 1.0)
                    score += text_score * 0.15
                
                scores[provider_id] = min(score, 1.0)
            
            # Apply MinMax scaling
            if scores:
                score_values = list(scores.values())
                scaled_scores = self.scaler.fit_transform(score_values)
                scores = dict(zip(scores.keys(), scaled_scores))
            
        except Exception as e:
            logger.error(f"Error in content-based scoring: {str(e)}")
            scores = {pid: 0.0 for pid in candidate_providers}
        
        return scores
    
    def _rating_based_scores(self, candidate_providers: List[int]) -> Dict[int, float]:
        """
        Calculate scores based purely on provider ratings (highest rated first)
        """
        scores = {}
        
        try:
            for provider_id in candidate_providers:
                provider = User.objects.get(id=provider_id)
                provider_profile = provider.provider_profile
                
                # Base score on average rating (0-5 scale)
                if provider_profile.average_rating > 0:
                    # Direct rating score without capping at 1.0
                    # 5.0/5 = 1.0, 4.0/5 = 0.8, 3.0/5 = 0.6, etc.
                    rating_score = float(provider_profile.average_rating) / 5.0
                else:
                    rating_score = 0.0  # Zero rating for unrated providers
                
                # Small bonus for review count (confidence)
                review_bonus = min(float(provider_profile.total_reviews) / 20.0, 0.1)  # Max 0.1 bonus
                
                # Final rating score - preserve rating differences
                final_score = min(rating_score + review_bonus, 1.0)
                scores[provider_id] = final_score
            
            # NO MinMax scaling - preserve actual rating hierarchy
            
        except Exception as e:
            logger.error(f"Error in rating-based scoring: {str(e)}")
            scores = {pid: 0.0 for pid in candidate_providers}  # Default zero score
        
        return scores
    
    def _popularity_scores(self, candidate_providers: List[int]) -> Dict[int, float]:
        """
        Calculate popularity scores based on booking counts and reviews
        """
        scores = {}
        
        try:
            for provider_id in candidate_providers:
                provider = User.objects.get(id=provider_id)
                
                # Booking count (last 30 days)
                recent_bookings = Booking.objects.filter(
                    provider=provider,
                    status='completed',
                    created_at__gte=timezone.now() - timezone.timedelta(days=30)
                ).count()
                
                # Review count
                review_count = Review.objects.filter(provider=provider).count()
                
                # Combined popularity score
                booking_score = min(recent_bookings / 20.0, 1.0)  # Normalize to 0-1
                review_score = min(review_count / 50.0, 1.0)  # Normalize to 0-1
                
                scores[provider_id] = (booking_score * 0.6 + review_score * 0.4)
            
            # Apply MinMax scaling
            if scores:
                score_values = list(scores.values())
                scaled_scores = self.scaler.fit_transform(score_values)
                scores = dict(zip(scores.keys(), scaled_scores))
            
        except Exception as e:
            logger.error(f"Error in popularity scoring: {str(e)}")
            scores = {pid: 0.0 for pid in candidate_providers}
        
        return scores
    
    def _availability_scores(self, candidate_providers: List[int]) -> Dict[int, float]:
        """
        Calculate availability scores based on provider availability patterns
        """
        scores = {}
        
        try:
            for provider_id in candidate_providers:
                provider = User.objects.get(id=provider_id)
                
                # Check if provider is marked as available
                if not provider.provider_profile.is_available:
                    scores[provider_id] = 0.0
                    continue
                
                # Count available time slots
                available_slots = provider.availability_slots.filter(
                    is_available=True
                ).count()
                
                # Maximum possible slots (7 days * typical 8 working hours)
                max_slots = 56
                availability_score = min(available_slots / max_slots, 1.0)
                
                scores[provider_id] = availability_score
            
            # Apply MinMax scaling
            if scores:
                score_values = list(scores.values())
                scaled_scores = self.scaler.fit_transform(score_values)
                scores = dict(zip(scores.keys(), scaled_scores))
            
        except Exception as e:
            logger.error(f"Error in availability scoring: {str(e)}")
            scores = {pid: 0.5 for pid in candidate_providers}  # Default neutral score
        
        return scores
    
    def _combine_scores(self, collaborative_scores: Dict, content_scores: Dict,
                       rating_scores: Dict, popularity_scores: Dict, availability_scores: Dict) -> Dict[int, Dict]:
        """
        Combine different scoring methods with weights - RATING PRIORITY
        """
        combined = {}
        
        # Updated weights - RATING IS ABSOLUTELY DOMINANT
        weights = {
            'rating': 0.80,        # DOMINANT: 80% weight for ratings
            'collaborative': 0.10, # Minimal impact
            'content_based': 0.05, # Minimal impact
            'popularity': 0.03,   # Minimal impact
            'availability': 0.02  # Minimal impact
        }
        
        for provider_id in collaborative_scores.keys():
            combined[provider_id] = {
                'collaborative': collaborative_scores.get(provider_id, 0.0),
                'content_based': content_scores.get(provider_id, 0.0),
                'rating': rating_scores.get(provider_id, 0.0),  # NEW: Rating score
                'popularity': popularity_scores.get(provider_id, 0.0),
                'availability': availability_scores.get(provider_id, 0.0)
            }
            
            # Calculate weighted final score with RATING ABSOLUTE DOMINANCE
            final_score = (
                combined[provider_id]['rating'] * weights['rating'] +           # 80% weight - ABSOLUTE DOMINANCE
                combined[provider_id]['collaborative'] * weights['collaborative'] + # 10% weight
                combined[provider_id]['content_based'] * weights['content_based'] + # 5% weight
                combined[provider_id]['popularity'] * weights['popularity'] +       # 3% weight
                combined[provider_id]['availability'] * weights['availability']    # 2% weight
            )
            
            combined[provider_id]['final_score'] = final_score
        
        return combined
    
    def _save_recommendations(self, customer: User, recommendations: List[Dict], 
                            service_category: Optional[str]):
        """Save recommendations to database"""
        try:
            from ml_engine.models import RecommendationScore
            
            # Delete old recommendations for this customer/category
            RecommendationScore.objects.filter(
                customer=customer,
                service_category=service_category or ""
            ).delete()
            
            # Save new recommendations
            for rec in recommendations:
                RecommendationScore.objects.create(
                    customer=customer,
                    provider=rec['provider'],
                    service_category=service_category or "",
                    compatibility_score=rec['score_breakdown']['content_based'],
                    distance_score=0.0,  # TODO: Implement geolocation scoring
                    rating_score=float(rec['provider'].provider_profile.average_rating) / 5.0,
                    price_score=0.0,  # TODO: Implement price scoring
                    availability_score=rec['score_breakdown']['availability'],
                    overall_score=rec['final_score'],
                    factors_used=rec['score_breakdown']
                )
        
        except Exception as e:
            logger.error(f"Error saving recommendations: {str(e)}")


class ServiceRecommendationEngine:
    """
    Service recommendation engine for suggesting relevant services to customers
    """
    
    def __init__(self):
        pass  # No complex initialization needed for now
    
    def get_service_recommendations(self, customer: User, 
                                  max_recommendations: int = 8) -> List[Dict]:
        """
        Get personalized service recommendations for a customer
        """
        try:
            # Get customer's booking history
            past_services = Service.objects.filter(
                bookings__customer=customer,
                bookings__status='completed'
            ).distinct()
            
            # Get customer preferences
            customer_profile = getattr(customer, 'customer_profile', None)
            preferred_categories = []
            
            if customer_profile and customer_profile.preferred_services:
                preferred_categories = [pref.strip().lower() 
                                       for pref in customer_profile.preferred_services.split(',')]
            
            # Get all active services
            all_services = Service.objects.filter(is_active=True)
            
            # Calculate similarity scores
            recommendations = []
            
            for service in all_services:
                # Skip if customer already booked this service
                if past_services.filter(id=service.id).exists():
                    continue
                
                score = 0.0
                
                # 1. Category preference match
                if preferred_categories:
                    if service.category.name.lower() in preferred_categories:
                        score += 0.4
                
                # 2. Provider quality
                if service.provider.provider_profile.average_rating > 0:
                    rating_score = float(service.provider.provider_profile.average_rating) / 5.0
                    score += rating_score * 0.3
                
                # 3. Price reasonableness (compared to category average)
                category_avg = Service.objects.filter(
                    category=service.category,
                    is_active=True
                ).aggregate(avg_price=Avg('base_price'))['avg_price'] or 0
                
                if category_avg > 0:
                    price_ratio = float(service.base_price) / float(category_avg)
                    # Prefer reasonable prices (not too high, not too low)
                    if 0.8 <= price_ratio <= 1.2:
                        score += 0.2
                
                # 4. Provider availability
                if service.provider.provider_profile.is_available:
                    score += 0.1
                
                recommendations.append({
                    'service': service,
                    'score': score,
                    'provider': service.provider,
                    'category': service.category
                })
            
            # Sort by score and return top recommendations
            recommendations.sort(key=lambda x: x['score'], reverse=True)
            return recommendations[:max_recommendations]
            
        except Exception as e:
            logger.error(f"Error getting service recommendations: {str(e)}")
            return []


# Singleton instances
recommendation_engine = RecommendationEngine()
service_recommendation_engine = ServiceRecommendationEngine()
