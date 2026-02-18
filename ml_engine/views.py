from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count
from django.utils import timezone
import json
import logging

from .recommendation_engine import recommendation_engine, service_recommendation_engine
from .models import RecommendationScore, MLPrediction
from accounts.models import User
from services.models import Service, ServiceCategory
from reviews.models import Review

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class RecommendationAPIView(View):
    """
    API endpoint for getting provider recommendations
    """
    
    def get(self, request):
        """
        Get personalized provider recommendations
        Query parameters:
        - category: Service category filter
        - location: Location filter
        - limit: Maximum number of recommendations (default: 10)
        """
        try:
            customer = request.user
            if customer.role != 'customer':
                return JsonResponse({'error': 'Only customers can get recommendations'}, status=403)
            
            service_category = request.GET.get('category')
            location = request.GET.get('location')
            limit = int(request.GET.get('limit', 10))
            
            recommendations = recommendation_engine.get_provider_recommendations(
                customer=customer,
                service_category=service_category,
                location=location,
                max_recommendations=limit
            )
            
            # Format response
            response_data = {
                'success': True,
                'recommendations': [],
                'metadata': {
                    'category': service_category,
                    'location': location,
                    'total_recommendations': len(recommendations)
                }
            }
            
            for rec in recommendations:
                provider_data = {
                    'provider_id': rec['provider'].id,
                    'provider_name': rec['provider'].username,
                    'business_name': rec['provider_profile'].business_name,
                    'final_score': rec['final_score'],
                    'score_breakdown': rec['score_breakdown'],
                    'average_rating': float(rec['provider_profile'].average_rating),
                    'total_reviews': rec['provider_profile'].total_reviews,
                    'years_of_experience': rec['provider_profile'].years_of_experience,
                    'completed_jobs': rec['provider_profile'].completed_jobs,
                    'services': rec['services']
                }
                response_data['recommendations'].append(provider_data)
            
            return JsonResponse(response_data)
            
        except Exception as e:
            logger.error(f"Error in recommendation API: {str(e)}")
            return JsonResponse({'error': 'Internal server error'}, status=500)


@method_decorator(login_required, name='dispatch')
class ServiceRecommendationAPIView(View):
    """
    API endpoint for getting service recommendations
    """
    
    def get(self, request):
        """
        Get personalized service recommendations
        Query parameters:
        - limit: Maximum number of recommendations (default: 8)
        """
        try:
            customer = request.user
            if customer.role != 'customer':
                return JsonResponse({'error': 'Only customers can get recommendations'}, status=403)
            
            limit = int(request.GET.get('limit', 8))
            
            recommendations = service_recommendation_engine.get_service_recommendations(
                customer=customer,
                max_recommendations=limit
            )
            
            # Format response
            response_data = {
                'success': True,
                'recommendations': [],
                'total_recommendations': len(recommendations)
            }
            
            for rec in recommendations:
                service_data = {
                    'service_id': rec['service'].id,
                    'service_title': rec['service'].title,
                    'service_description': rec['service'].description,
                    'base_price': float(rec['service'].base_price),
                    'price_unit': rec['service'].price_unit,
                    'score': rec['score'],
                    'provider': {
                        'id': rec['provider'].id,
                        'name': rec['provider'].username,
                        'business_name': rec['provider'].provider_profile.business_name,
                        'average_rating': float(rec['provider'].provider_profile.average_rating)
                    },
                    'category': {
                        'name': rec['category'].name,
                        'description': rec['category'].description
                    }
                }
                response_data['recommendations'].append(service_data)
            
            return JsonResponse(response_data)
            
        except Exception as e:
            logger.error(f"Error in service recommendation API: {str(e)}")
            return JsonResponse({'error': 'Internal server error'}, status=500)


@login_required
def recommendation_dashboard(request):
    """
    Dashboard view for displaying recommendations
    """
    if request.user.role != 'customer':
        return render(request, 'error.html', {'error': 'Access denied'})
    
    try:
        # Get top recommendations
        recommendations = recommendation_engine.get_provider_recommendations(
            customer=request.user,
            max_recommendations=6
        )
        
        # Get service recommendations
        service_recs = service_recommendation_engine.get_service_recommendations(
            customer=request.user,
            max_recommendations=4
        )
        
        # Get popular categories
        popular_categories = ServiceCategory.objects.filter(
            services__is_active=True
        ).annotate(
            service_count=Count('services')
        ).order_by('-service_count')[:6]
        
        context = {
            'recommendations': recommendations,
            'service_recommendations': service_recs,
            'popular_categories': popular_categories,
            'page_title': 'Personalized Recommendations'
        }
        
        return render(request, 'ml_engine/recommendation_dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Error loading recommendation dashboard: {str(e)}")
        return render(request, 'error.html', {'error': 'Unable to load recommendations'})
