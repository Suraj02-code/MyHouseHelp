from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count, Avg
from django.db import models
import json
import uuid
import re

from .models import ChatSession, ChatMessage, ChatbotKnowledge, ChatbotAnalytics
from .utils import ChatbotProcessor


@csrf_exempt
@require_http_methods(["POST"])
def send_message(request):
    """Handle incoming chat messages"""
    try:
        data = json.loads(request.body)
        message_content = data.get('message', '').strip()
        session_id = data.get('session_id')
        
        if not message_content or not session_id:
            return JsonResponse({'error': 'Invalid request'}, status=400)
        
        # Get chat session
        try:
            chat_session = ChatSession.objects.get(session_id=session_id)
        except ChatSession.DoesNotExist:
            return JsonResponse({'error': 'Session not found'}, status=404)
        
        # Save user message
        user_message = ChatMessage.objects.create(
            session=chat_session,
            message_type='user',
            content=message_content
        )
        
        # Process message and get bot response
        processor = ChatbotProcessor()
        bot_response = processor.process_message(message_content, request.user, session_id)
        
        # Save bot response
        bot_message = ChatMessage.objects.create(
            session=chat_session,
            message_type='bot',
            content=bot_response
        )
        
        # Update session timestamp
        chat_session.updated_at = timezone.now()
        chat_session.save()
        
        return JsonResponse({
            'success': True,
            'user_message': {
                'id': user_message.id,
                'content': user_message.content,
                'timestamp': user_message.timestamp.isoformat(),
                'type': user_message.message_type
            },
            'bot_message': {
                'id': bot_message.id,
                'content': bot_message.content,
                'timestamp': bot_message.timestamp.isoformat(),
                'type': bot_message.message_type
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def get_quick_response(request):
    """Get quick response for predefined questions"""
    try:
        data = json.loads(request.body)
        question_id = data.get('question_id')
        
        if not question_id:
            return JsonResponse({'error': 'Question ID required'}, status=400)
        
        try:
            knowledge = ChatbotKnowledge.objects.get(
                id=question_id,
                is_active=True
            )
        except ChatbotKnowledge.DoesNotExist:
            return JsonResponse({'error': 'Question not found'}, status=404)
        
        return JsonResponse({
            'success': True,
            'question': knowledge.question,
            'answer': knowledge.answer,
            'category': knowledge.category
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def chat_history(request):
    """View chat history for authenticated users"""
    chat_sessions = ChatSession.objects.filter(
        user=request.user
    ).order_by('-updated_at')
    
    context = {
        'chat_sessions': chat_sessions,
    }
    
    return render(request, 'chatbot/chat_history.html', context)


@login_required
def chat_session_detail(request, session_id):
    """View specific chat session details"""
    chat_session = get_object_or_404(
        ChatSession, 
        session_id=session_id,
        user=request.user
    )
    
    messages = ChatMessage.objects.filter(
        session=chat_session
    ).order_by('timestamp')
    
    context = {
        'chat_session': chat_session,
        'messages': messages,
    }
    
    return render(request, 'chatbot/chat_session_detail.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def rate_response(request):
    """Rate chatbot response quality"""
    try:
        data = json.loads(request.body)
        message_id = data.get('message_id')
        rating = data.get('rating')  # 1-5 scale
        
        if not message_id or not rating or rating < 1 or rating > 5:
            return JsonResponse({'error': 'Invalid request'}, status=400)
        
        try:
            message = ChatMessage.objects.get(id=message_id)
            # Update analytics with user satisfaction
            analytics = ChatbotAnalytics.objects.filter(
                session=message.session
            ).order_by('-created_at').first()
            
            if analytics:
                analytics.user_satisfaction = rating
                analytics.resolved = rating >= 4
                analytics.save()
            
            return JsonResponse({'success': True})
            
        except ChatMessage.DoesNotExist:
            return JsonResponse({'error': 'Message not found'}, status=404)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_suggestions(request):
    """Get smart suggestions based on user context"""
    try:
        session_id = request.GET.get('session_id')
        if not session_id:
            return JsonResponse({'error': 'Session ID required'}, status=400)
        
        # Get recent conversation context
        try:
            session = ChatSession.objects.get(session_id=session_id)
            recent_messages = session.messages.all().order_by('-timestamp')[:5]
            
            suggestions = []
            
            # Generate contextual suggestions
            if not recent_messages.exists():
                suggestions = [
                    "What services do you offer?",
                    "How do I book a service?",
                    "What are your prices?",
                    "How do I become a service provider?"
                ]
            else:
                last_message = recent_messages.first()
                if last_message.message_type == 'user':
                    # Generate follow-up suggestions based on user's last message
                    message_lower = last_message.content.lower()
                    
                    if 'cleaning' in message_lower:
                        suggestions = [
                            "What types of cleaning do you offer?",
                            "How much does cleaning cost?",
                            "Can I book cleaning for today?"
                        ]
                    elif 'plumbing' in message_lower:
                        suggestions = [
                            "Do you have emergency plumbing?",
                            "What plumbing services are available?",
                            "How quickly can a plumber come?"
                        ]
                    elif 'book' in message_lower:
                        suggestions = [
                            "What services can I book?",
                            "How do I schedule an appointment?",
                            "Can I cancel my booking?"
                        ]
                    else:
                        suggestions = [
                            "Tell me about your services",
                            "How do I contact support?",
                            "What are your operating hours?"
                        ]
            
            return JsonResponse({
                'success': True,
                'suggestions': suggestions
            })
            
        except ChatSession.DoesNotExist:
            return JsonResponse({'error': 'Session not found'}, status=404)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def chatbot_analytics(request):
    """View chatbot analytics dashboard"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    # Get analytics data
    total_sessions = ChatSession.objects.count()
    total_messages = ChatMessage.objects.count()
    avg_response_time = ChatbotAnalytics.objects.aggregate(
        avg_time=models.Avg('response_time')
    )['avg_time'] or 0
    
    satisfaction_ratings = ChatbotAnalytics.objects.filter(
        user_satisfaction__isnull=False
    ).values_list('user_satisfaction', flat=True)
    
    avg_satisfaction = sum(satisfaction_ratings) / len(satisfaction_ratings) if satisfaction_ratings else 0
    
    # Get top intents
    top_intents = ChatbotAnalytics.objects.values('intent_detected').annotate(
        count=models.Count('intent_detected')
    ).order_by('-count')[:10]
    
    context = {
        'total_sessions': total_sessions,
        'total_messages': total_messages,
        'avg_response_time': round(avg_response_time, 2),
        'avg_satisfaction': round(avg_satisfaction, 2),
        'top_intents': top_intents,
    }
    
    return render(request, 'chatbot/analytics.html', context)