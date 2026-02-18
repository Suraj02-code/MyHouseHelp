import re
import json
import time
import openai
from difflib import SequenceMatcher
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from .models import ChatbotKnowledge, ChatbotIntent, ChatbotEntity, ChatbotAnalytics, ChatSession
from services.models import Service
from accounts.models import User


class AdvancedChatbotProcessor:
    """Advanced AI-powered chatbot processing logic"""
    
    def __init__(self):
        self.greetings = [
            'hello', 'hi', 'hey', 'good morning', 'good afternoon', 
            'good evening', 'greetings', 'howdy'
        ]
        self.thanks = [
            'thank you', 'thanks', 'appreciate', 'grateful'
        ]
        self.goodbyes = [
            'bye', 'goodbye', 'see you', 'farewell', 'take care'
        ]
        
        # Initialize OpenAI client if API key is available
        self.openai_client = None
        if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
            self.openai_client = openai


class ChatbotProcessor:
    """Enhanced chatbot processing logic with advanced question understanding"""
    
    def __init__(self):
        self.advanced_processor = AdvancedChatbotProcessor()
        self.greetings = self.advanced_processor.greetings
        self.thanks = self.advanced_processor.thanks
        self.goodbyes = self.advanced_processor.goodbyes
        
        # Enhanced keyword patterns for better understanding
        self.service_keywords = {
            'cleaning': ['clean', 'cleaning', 'house cleaning', 'deep clean', 'maid', 'housekeeper', 'dust', 'vacuum', 'mop'],
            'plumbing': ['plumber', 'plumbing', 'pipe', 'leak', 'faucet', 'toilet', 'drain', 'water', 'bathroom', 'kitchen sink'],
            'electrical': ['electrician', 'electrical', 'wiring', 'outlet', 'switch', 'light', 'power', 'electricity', 'circuit'],
            'painting': ['painter', 'painting', 'paint', 'wall', 'interior', 'exterior', 'color', 'brush'],
            'pest_control': ['pest', 'bug', 'insect', 'termite', 'cockroach', 'ant', 'spider', 'rodent', 'exterminator', 'pest control'],
            'appliance': ['appliance', 'repair', 'fix', 'refrigerator', 'washing machine', 'dryer', 'oven', 'microwave', 'washing machine', 'fridge', 'dishwasher'],
            'maintenance': ['maintenance', 'repair', 'fix', 'service', 'check', 'inspect', 'maintain']
        }
        
        self.booking_keywords = ['book', 'schedule', 'appointment', 'reserve', 'order', 'hire', 'get', 'need', 'want', 'looking for']
        self.pricing_keywords = ['price', 'cost', 'rate', 'fee', 'charge', 'expensive', 'cheap', 'affordable', 'how much', 'pricing']
        self.emergency_keywords = ['emergency', 'urgent', 'asap', 'immediately', 'now', 'today', 'quick', 'fast']
    
    def process_message(self, message, user=None, session_id=None):
        """Process user message with enhanced intelligence and context awareness"""
        start_time = time.time()
        message_lower = message.lower().strip()
        
        # Get conversation context
        context = self._get_conversation_context(session_id) if session_id else []
        
        # Enhanced processing with multiple strategies
        response = None
        
        # Strategy 1: Try AI-powered processing first (if available)
        if self.advanced_processor.openai_client:
            response = self._process_with_ai(message, context, user)
        
        # Strategy 2: Enhanced rule-based processing with fuzzy matching
        if not response:
            response = self._process_with_enhanced_rules(message, message_lower, user, context)
        
        # Strategy 3: Fallback to basic responses
        if not response:
            response = self._get_intelligent_fallback(message_lower, user)
        
        # Log analytics
        response_time = time.time() - start_time
        self._log_analytics(session_id, message, response, response_time, user)
        
        return response
    
    def _process_with_enhanced_rules(self, message, message_lower, user, context):
        """Enhanced rule-based processing with fuzzy matching and context awareness"""
        
        # Check for greetings
        if self._is_greeting(message_lower):
            return self._get_greeting_response(user)
        
        # Check for thanks
        if self._is_thanks(message_lower):
            return self._get_thanks_response()
        
        # Check for goodbye
        if self._is_goodbye(message_lower):
            return self._get_goodbye_response()
        
        # Check for help
        if self._is_help_request(message_lower):
            return self._get_help_response()
        
        # Enhanced service detection
        detected_service = self._detect_service_type(message_lower)
        if detected_service:
            return self._get_service_response(detected_service, message_lower, user)
        
        # Enhanced booking detection
        if self._is_booking_request(message_lower):
            return self._get_booking_response(message_lower, user)
        
        # Enhanced pricing detection
        if self._is_pricing_request(message_lower):
            return self._get_pricing_response(message_lower, user)
        
        # Enhanced knowledge base search with fuzzy matching
        knowledge_response = self._search_knowledge_base_enhanced(message_lower)
        if knowledge_response:
            return knowledge_response
        
        # Context-aware responses
        if context:
            return self._get_contextual_response(message_lower, context, user)
        
        return None
    
    def _detect_service_type(self, message_lower):
        """Detect service type with fuzzy matching"""
        best_match = None
        best_score = 0
        
        for service_type, keywords in self.service_keywords.items():
            for keyword in keywords:
                # Exact match
                if keyword in message_lower:
                    return service_type
                
                # Fuzzy match
                similarity = SequenceMatcher(None, message_lower, keyword).ratio()
                if similarity > 0.6 and similarity > best_score:
                    best_match = service_type
                    best_score = similarity
        
        # Special cases for better detection
        if 'washing machine' in message_lower or 'fridge' in message_lower or 'refrigerator' in message_lower:
            return 'appliance'
        if 'pest control' in message_lower:
            return 'pest_control'
        
        return best_match if best_score > 0.6 else None
    
    def _is_booking_request(self, message_lower):
        """Enhanced booking request detection"""
        booking_indicators = 0
        for keyword in self.booking_keywords:
            if keyword in message_lower:
                booking_indicators += 1
        
        # Also check for service keywords
        service_indicators = 0
        for service_type, keywords in self.service_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    service_indicators += 1
                    break
        
        return booking_indicators > 0 and service_indicators > 0
    
    def _is_pricing_request(self, message_lower):
        """Enhanced pricing request detection"""
        for keyword in self.pricing_keywords:
            if keyword in message_lower:
                return True
        return False
    
    def _get_service_response(self, service_type, message_lower, user):
        """Get detailed service response"""
        service_info = {
            'cleaning': {
                'name': 'Cleaning Services',
                'description': 'Professional house cleaning, deep cleaning, office cleaning, and specialized cleaning services',
                'price_range': '₹500 - ₹2000',
                'features': ['Regular cleaning', 'Deep cleaning', 'Post-construction cleaning', 'Office cleaning']
            },
            'plumbing': {
                'name': 'Plumbing Services',
                'description': 'Expert plumbing repairs, installations, maintenance, and emergency services',
                'price_range': '₹300 - ₹1500',
                'features': ['Leak repairs', 'Pipe installation', 'Faucet repairs', 'Emergency plumbing']
            },
            'electrical': {
                'name': 'Electrical Services',
                'description': 'Licensed electricians for repairs, installations, and electrical maintenance',
                'price_range': '₹400 - ₹2000',
                'features': ['Wiring repairs', 'Outlet installation', 'Light fixtures', 'Electrical troubleshooting']
            },
            'painting': {
                'name': 'Painting Services',
                'description': 'Professional interior and exterior painting services',
                'price_range': '₹800 - ₹3000',
                'features': ['Interior painting', 'Exterior painting', 'Wall preparation', 'Color consultation']
            },
            'pest_control': {
                'name': 'Pest Control Services',
                'description': 'Effective pest control and extermination services',
                'price_range': '₹600 - ₹2500',
                'features': ['Termite control', 'Cockroach treatment', 'Ant control', 'Rodent removal']
            },
            'appliance': {
                'name': 'Appliance Repair Services',
                'description': 'Expert repair services for all home appliances',
                'price_range': '₹500 - ₹3000',
                'features': ['Refrigerator repair', 'Washing machine repair', 'Oven repair', 'Microwave repair']
            },
            'maintenance': {
                'name': 'General Maintenance Services',
                'description': 'Comprehensive home maintenance and repair services',
                'price_range': '₹400 - ₹2000',
                'features': ['General repairs', 'Maintenance checks', 'Inspection services', 'Preventive maintenance']
            }
        }
        
        info = service_info.get(service_type, {})
        if not info:
            return None
        
        response = f"🔧 **{info['name']}**\n\n"
        response += f"{info['description']}\n\n"
        response += f"💰 **Price Range:** {info['price_range']}\n\n"
        response += f"✨ **Services Include:**\n"
        for feature in info['features']:
            response += f"• {feature}\n"
        
        # Add booking suggestion
        if self._is_booking_request(message_lower):
            response += f"\n📅 Would you like to book {info['name'].lower()}? I can help you schedule an appointment!"
        else:
            response += f"\n💡 Need more information or want to book? Just ask!"
        
        return response
    
    def _get_booking_response(self, message_lower, user):
        """Get booking assistance response"""
        detected_service = self._detect_service_type(message_lower)
        
        if detected_service:
            service_info = {
                'cleaning': 'cleaning service',
                'plumbing': 'plumbing service',
                'electrical': 'electrical service',
                'painting': 'painting service',
                'pest_control': 'pest control service',
                'appliance': 'appliance repair service',
                'maintenance': 'maintenance service'
            }
            
            service_name = service_info.get(detected_service, 'service')
            
            response = f"📅 **Booking {service_name.title()}**\n\n"
            response += "I can help you book this service! Here's what I need to know:\n\n"
            response += "1. **Preferred Date & Time** - When would you like the service?\n"
            response += "2. **Service Details** - Any specific requirements?\n"
            response += "3. **Location** - Your address for the service\n\n"
            
            if any(keyword in message_lower for keyword in self.emergency_keywords):
                response += "🚨 **Emergency Service Available** - We can arrange same-day service for urgent needs!\n\n"
            
            response += "Would you like to proceed with booking? You can also visit our services page to see available providers and book directly."
        else:
            response = "📅 **Service Booking**\n\n"
            response += "I'd be happy to help you book a service! What type of service are you looking for?\n\n"
            response += "We offer:\n"
            response += "• 🧹 Cleaning Services\n"
            response += "• 🔧 Plumbing Services\n"
            response += "• ⚡ Electrical Services\n"
            response += "• 🎨 Painting Services\n"
            response += "• 🐜 Pest Control\n"
            response += "• 🔨 Appliance Repair\n"
            response += "• 🛠️ General Maintenance\n\n"
            response += "Just let me know which service you need and I'll help you book it!"
        
        return response
    
    def _get_pricing_response(self, message_lower, user):
        """Get pricing information response"""
        detected_service = self._detect_service_type(message_lower)
        
        if detected_service:
            pricing_info = {
                'cleaning': '₹500 - ₹2000 (varies by size and type)',
                'plumbing': '₹300 - ₹1500 (varies by complexity)',
                'electrical': '₹400 - ₹2000 (varies by work required)',
                'painting': '₹800 - ₹3000 (varies by area and type)',
                'pest_control': '₹600 - ₹2500 (varies by treatment type)',
                'appliance': '₹500 - ₹3000 (varies by appliance and issue)',
                'maintenance': '₹400 - ₹2000 (varies by work required)'
            }
            
            price = pricing_info.get(detected_service, 'Contact us for pricing')
            
            response = f"💰 **Pricing Information**\n\n"
            response += f"**{detected_service.title()} Services:** {price}\n\n"
            response += "📋 **What affects pricing:**\n"
            response += "• Size of the area/scope of work\n"
            response += "• Complexity of the task\n"
            response += "• Materials required\n"
            response += "• Urgency (emergency services may have higher rates)\n\n"
            response += "💡 **Transparent Pricing:** No hidden fees! The price you see is what you pay.\n\n"
            response += "Would you like to get a specific quote? I can help you connect with our service providers for accurate pricing."
        else:
            response = "💰 **Our Pricing**\n\n"
            response += "We offer competitive and transparent pricing for all our services:\n\n"
            response += "• 🧹 **Cleaning:** ₹500 - ₹2000\n"
            response += "• 🔧 **Plumbing:** ₹300 - ₹1500\n"
            response += "• ⚡ **Electrical:** ₹400 - ₹2000\n"
            response += "• 🎨 **Painting:** ₹800 - ₹3000\n"
            response += "• 🐜 **Pest Control:** ₹600 - ₹2500\n"
            response += "• 🔨 **Appliance Repair:** ₹500 - ₹3000\n"
            response += "• 🛠️ **Maintenance:** ₹400 - ₹2000\n\n"
            response += "💡 **No Hidden Fees** - What you see is what you pay!\n\n"
            response += "For specific pricing, let me know which service you're interested in and I can provide more detailed information."
        
        return response
    
    def _search_knowledge_base_enhanced(self, message_lower):
        """Enhanced knowledge base search with fuzzy matching"""
        # Get all active knowledge entries
        knowledge_entries = ChatbotKnowledge.objects.filter(is_active=True)
        
        best_match = None
        best_score = 0
        
        for entry in knowledge_entries:
            # Calculate multiple similarity scores
            question_score = self._calculate_similarity(message_lower, entry.question.lower())
            keyword_score = self._calculate_keyword_similarity(message_lower, entry.get_keywords_list())
            
            # Combined score with weights
            combined_score = (question_score * 0.7) + (keyword_score * 0.3)
            
            if combined_score > best_score and combined_score > 0.4:  # Lower threshold for better matching
                best_match = entry
                best_score = combined_score
        
        if best_match:
            # Increment usage count
            best_match.increment_usage()
            return best_match.answer
        
        return None
    
    def _calculate_similarity(self, text1, text2):
        """Calculate similarity between two texts"""
        return SequenceMatcher(None, text1, text2).ratio()
    
    def _calculate_keyword_similarity(self, message, keywords):
        """Calculate similarity based on keyword matches"""
        if not keywords:
            return 0
        
        matches = 0
        for keyword in keywords:
            if keyword in message:
                matches += 1
        
        return matches / len(keywords)
    
    def _get_contextual_response(self, message_lower, context, user):
        """Generate contextual responses based on conversation history"""
        # Look for patterns in recent messages
        recent_messages = [msg.get('content', '').lower() for msg in context[-3:]]
        
        # Check if user is continuing a previous topic
        if any('service' in msg for msg in recent_messages):
            return "I see you're interested in our services. What specific information would you like to know?"
        
        if any('book' in msg for msg in recent_messages):
            return "Are you ready to book a service, or do you need more information first?"
        
        if any('price' in msg for msg in recent_messages):
            return "Would you like pricing information for a specific service, or do you have other questions?"
        
        return None
    
    def _get_intelligent_fallback(self, message_lower, user):
        """Intelligent fallback responses based on message analysis"""
        # Analyze the message for clues
        words = message_lower.split()
        
        # Check for question words
        question_words = ['what', 'how', 'when', 'where', 'why', 'which', 'who']
        has_question = any(word in question_words for word in words)
        
        # Check for service-related words
        service_words = ['service', 'help', 'need', 'want', 'looking']
        has_service_context = any(word in service_words for word in words)
        
        if has_question and has_service_context:
            return """I understand you have a question about our services! 🤔

I can help you with:
• 🔧 **Service Information** - What we offer and how it works
• 📅 **Booking Process** - How to schedule services
• 💰 **Pricing Details** - Cost information
• 📞 **Support** - Contact and customer service

Could you be more specific about what you'd like to know? For example:
- "What cleaning services do you offer?"
- "How do I book a plumber?"
- "What are your prices for electrical work?" """
        
        elif has_question:
            return """I'm here to help! 😊 

Could you please rephrase your question? I can assist you with:
• Information about our home services
• Booking appointments
• Pricing details
• Customer support

Try asking something like:
- "What services do you offer?"
- "How do I book a service?"
- "What are your prices?" """
        
        else:
            return """I want to make sure I understand you correctly! 🤖

I'm your Home Service Assistant and I can help with:
• 🧹 Cleaning services
• 🔧 Plumbing repairs
• ⚡ Electrical work
• 🎨 Painting services
• 🐜 Pest control
• 🔨 Appliance repair
• 🛠️ General maintenance

What would you like to know about our services?"""
    
    def _process_with_ai(self, message, context, user):
        """Process message using AI if available"""
        if not self.advanced_processor.openai_client:
            return None
        
        try:
            # Prepare context for AI
            system_prompt = self._get_system_prompt(user)
            conversation_history = self._format_conversation_history(context)
            
            # Get AI response
            response = self.advanced_processor.openai_client.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    *conversation_history,
                    {"role": "user", "content": message}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Enhance with service-specific information
            enhanced_response = self._enhance_with_service_data(ai_response, message)
            
            return enhanced_response
            
        except Exception as e:
            print(f"AI processing error: {e}")
            return None
    
    def _get_system_prompt(self, user):
        """Get system prompt for AI"""
        user_info = ""
        if user and user.is_authenticated:
            user_info = f"The user is logged in as {user.username}."
            if hasattr(user, 'user_type'):
                user_info += f" User type: {user.user_type}."
        
        return f"""You are a helpful AI assistant for MyHouseHelp, a home service marketplace. 
        
        {user_info}
        
        You can help with:
        - Service information (cleaning, plumbing, electrical, painting, etc.)
        - Booking assistance
        - Pricing information
        - Account management
        - Customer support
        
        Be friendly, helpful, and professional. Provide specific, actionable information.
        If you don't know something, suggest contacting customer support.
        Keep responses concise but informative."""
    
    def _format_conversation_history(self, context):
        """Format conversation history for AI"""
        formatted_history = []
        for msg in context[-6:]:  # Last 6 messages
            role = "user" if msg.get('type') == 'user' else "assistant"
            formatted_history.append({
                "role": role,
                "content": msg.get('content', '')
            })
        return formatted_history
    
    def _enhance_with_service_data(self, ai_response, user_message):
        """Enhance AI response with real service data"""
        # Check if user is asking about specific services
        service_keywords = ['cleaning', 'plumbing', 'electrical', 'painting', 'pest control']
        mentioned_services = [kw for kw in service_keywords if kw in user_message.lower()]
        
        if mentioned_services:
            try:
                services = Service.objects.filter(
                    Q(name__icontains=mentioned_services[0]) | 
                    Q(description__icontains=mentioned_services[0])
                )[:3]
                
                if services.exists():
                    service_info = "\n\n**Available Services:**\n"
                    for service in services:
                        service_info += f"• {service.name} - ₹{service.price}\n"
                    
                    return ai_response + service_info
            except Exception:
                pass
        
        return ai_response
    
    def _get_conversation_context(self, session_id):
        """Get conversation context for the session"""
        try:
            session = ChatSession.objects.get(session_id=session_id)
            messages = session.messages.all().order_by('timestamp')[:10]
            return [
                {
                    'type': msg.message_type,
                    'content': msg.content,
                    'timestamp': msg.timestamp
                }
                for msg in messages
            ]
        except ChatSession.DoesNotExist:
            return []
    
    def _log_analytics(self, session_id, user_message, bot_response, response_time, user):
        """Log analytics data"""
        if not session_id:
            return
        
        try:
            session = ChatSession.objects.get(session_id=session_id)
            ChatbotAnalytics.objects.create(
                session=session,
                response_time=response_time,
                conversation_length=session.messages.count(),
                intent_detected=self._detect_intent(user_message),
                entities_extracted=self._extract_entities(user_message)
            )
        except ChatSession.DoesNotExist:
            # Session doesn't exist, skip analytics logging
            pass
        except Exception as e:
            # Log other errors but don't break the chatbot
            print(f"Analytics logging error: {e}")
    
    def _detect_intent(self, message):
        """Detect intent from user message"""
        message_lower = message.lower()
        
        if any(greeting in message_lower for greeting in self.greetings):
            return "greeting"
        elif any(thanks in message_lower for thanks in self.thanks):
            return "thanks"
        elif any(goodbye in message_lower for goodbye in self.goodbyes):
            return "goodbye"
        elif 'book' in message_lower or 'schedule' in message_lower:
            return "booking"
        elif 'price' in message_lower or 'cost' in message_lower:
            return "pricing"
        elif 'service' in message_lower:
            return "service_inquiry"
        else:
            return "general_inquiry"
    
    def _extract_entities(self, message):
        """Extract entities from user message"""
        entities = {}
        message_lower = message.lower()
        
        # Service entities
        service_entities = ['cleaning', 'plumbing', 'electrical', 'painting', 'pest control']
        for service in service_entities:
            if service in message_lower:
                entities['service'] = service
        
        # Time entities
        time_keywords = ['today', 'tomorrow', 'week', 'month', 'urgent', 'emergency']
        for time_kw in time_keywords:
            if time_kw in message_lower:
                entities['time'] = time_kw
                break
        
        return entities
    
    def _process_with_rules(self, message_lower, user):
        """Fallback rule-based processing"""
        # Check for greetings
        if self._is_greeting(message_lower):
            return self._get_greeting_response(user)
        
        # Check for thanks
        if self._is_thanks(message_lower):
            return self._get_thanks_response()
        
        # Check for goodbye
        if self._is_goodbye(message_lower):
            return self._get_goodbye_response()
        
        # Check for help
        if self._is_help_request(message_lower):
            return self._get_help_response()
        
        # Search knowledge base
        knowledge_response = self._search_knowledge_base(message_lower)
        if knowledge_response:
            return knowledge_response
        
        # Default response
        return self._get_default_response()
    
    def _is_greeting(self, message):
        """Check if message is a greeting"""
        return any(greeting in message for greeting in self.greetings)
    
    def _is_thanks(self, message):
        """Check if message is expressing thanks"""
        return any(thanks in message for thanks in self.thanks)
    
    def _is_goodbye(self, message):
        """Check if message is a goodbye"""
        return any(goodbye in message for goodbye in self.goodbyes)
    
    def _is_help_request(self, message):
        """Check if message is asking for help"""
        help_keywords = ['help', 'support', 'assist', 'guide', 'how to']
        return any(keyword in message for keyword in help_keywords)
    
    def _get_greeting_response(self, user):
        """Get greeting response"""
        if user and user.is_authenticated:
            name = user.first_name or user.username
            return f"Hello {name}! 👋 I'm your Home Service Assistant. How can I help you today?"
        else:
            return "Hello! 👋 I'm your Home Service Assistant. I can help you with questions about our services, bookings, pricing, and more. How can I assist you today?"
    
    def _get_thanks_response(self):
        """Get thanks response"""
        responses = [
            "You're very welcome! 😊 Is there anything else I can help you with?",
            "Happy to help! 😊 Feel free to ask if you have any other questions.",
            "My pleasure! 😊 Let me know if you need assistance with anything else."
        ]
        import random
        return random.choice(responses)
    
    def _get_goodbye_response(self):
        """Get goodbye response"""
        responses = [
            "Goodbye! 👋 Have a great day and feel free to come back anytime!",
            "Take care! 👋 I'm here whenever you need help with our services.",
            "See you later! 👋 Don't hesitate to reach out if you have any questions."
        ]
        import random
        return random.choice(responses)
    
    def _get_help_response(self):
        """Get help response"""
        return """I'm here to help! 🤖 I can assist you with:

🔧 **Services**: Information about cleaning, plumbing, electrical, and other services
📅 **Bookings**: How to book services and manage appointments  
💰 **Pricing**: Service rates and payment information
👤 **Account**: Profile management and account settings
📞 **Support**: Contact information and customer service

What would you like to know more about?"""
    
    def _search_knowledge_base(self, message):
        """Search knowledge base for relevant answers"""
        # Get all active knowledge entries
        knowledge_entries = ChatbotKnowledge.objects.filter(is_active=True)
        
        best_match = None
        best_score = 0
        
        for entry in knowledge_entries:
            score = self._calculate_match_score(message, entry)
            if score > best_score and score > 0.3:  # Minimum threshold
                best_match = entry
                best_score = score
        
        if best_match:
            return best_match.answer
        
        return None
    
    def _calculate_match_score(self, message, knowledge_entry):
        """Calculate match score between message and knowledge entry"""
        message_words = set(re.findall(r'\b\w+\b', message.lower()))
        question_words = set(re.findall(r'\b\w+\b', knowledge_entry.question.lower()))
        keyword_words = set(knowledge_entry.get_keywords_list())
        
        # Calculate word overlap
        all_keywords = question_words.union(keyword_words)
        overlap = len(message_words.intersection(all_keywords))
        
        if len(message_words) == 0:
            return 0
        
        # Calculate score based on overlap ratio
        score = overlap / len(message_words)
        
        # Boost score for exact keyword matches
        keyword_matches = len(message_words.intersection(keyword_words))
        if keyword_matches > 0:
            score += keyword_matches * 0.2
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _get_default_response(self):
        """Get default response when no specific match is found"""
        responses = [
            "I'm not sure I understand that question. Could you rephrase it or ask about our services, bookings, or pricing?",
            "I'd be happy to help! Could you provide more details about what you're looking for?",
            "Let me help you with that. Could you be more specific about what you need assistance with?",
            "I'm here to help with questions about our home services. What would you like to know?",
            "I can help you with information about our services, bookings, pricing, and more. What specific question do you have?"
        ]
        import random
        return random.choice(responses)
