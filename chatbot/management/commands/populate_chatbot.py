from django.core.management.base import BaseCommand
from chatbot.models import ChatbotKnowledge, ChatbotIntent, ChatbotEntity


class Command(BaseCommand):
    help = 'Populate chatbot with sample knowledge base'

    def handle(self, *args, **options):
        self.stdout.write('Populating chatbot knowledge base...')
        
        # Sample knowledge base data
        knowledge_data = [
            # General Information
            {
                'category': 'general',
                'question': 'What is MyHouseHelp?',
                'answer': 'MyHouseHelp is a home service marketplace that connects customers with verified service providers for all your household needs including cleaning, plumbing, electrical work, appliance repair, painting, pest control, maintenance, and landscaping.',
                'keywords': 'what is, about, company, service, marketplace, home, help'
            },
            {
                'category': 'general',
                'question': 'How does MyHouseHelp work?',
                'answer': 'MyHouseHelp works in 3 simple steps: 1) Search and browse services by category, 2) Book your preferred service with date and time, 3) Get professional service and leave a review. Our platform connects you with verified service providers in your area.',
                'keywords': 'how does, work, process, steps, booking, service'
            },
            
            # Services
            {
                'category': 'services',
                'question': 'What services do you offer?',
                'answer': 'We offer a comprehensive range of home services including: 🧹 Cleaning (house, office, deep cleaning), 🔧 Plumbing (repairs, installations, maintenance), ⚡ Electrical work (repairs, installations), 🔨 Appliance repair, 🎨 Painting (interior/exterior), 🐜 Pest control, 🏠 General maintenance, and 🌱 Landscaping services.',
                'keywords': 'services, offer, cleaning, plumbing, electrical, painting, pest control, maintenance, landscaping, appliance repair'
            },
            {
                'category': 'services',
                'question': 'Do you provide cleaning services?',
                'answer': 'Yes! We offer professional cleaning services including regular house cleaning, deep cleaning, office cleaning, post-construction cleaning, and specialized cleaning services. All our cleaning providers are verified and experienced professionals.',
                'keywords': 'cleaning, house cleaning, office cleaning, deep cleaning, professional cleaning'
            },
            {
                'category': 'services',
                'question': 'Do you have plumbing services?',
                'answer': 'Absolutely! Our plumbing services include repairs, installations, maintenance, leak detection, pipe replacement, faucet repairs, toilet repairs, water heater services, and emergency plumbing services. All plumbers are licensed and experienced.',
                'keywords': 'plumbing, plumber, pipe, leak, faucet, toilet, water heater, emergency plumbing'
            },
            {
                'category': 'services',
                'question': 'Do you offer electrical services?',
                'answer': 'Yes! Our electrical services include repairs, installations, wiring, outlet installation, light fixture installation, electrical troubleshooting, and safety inspections. All electricians are licensed and certified professionals.',
                'keywords': 'electrical, electrician, wiring, outlet, light fixture, electrical repair, installation'
            },
            
            # Pricing
            {
                'category': 'pricing',
                'question': 'How much do services cost?',
                'answer': 'Service prices vary depending on the type of service, complexity, and duration. Most services start from ₹500 and can go up based on specific requirements. You can see exact pricing on each service listing. We offer competitive rates and transparent pricing with no hidden fees.',
                'keywords': 'price, cost, pricing, rates, fees, how much, expensive, cheap, affordable'
            },
            {
                'category': 'pricing',
                'question': 'Are there any hidden fees?',
                'answer': 'No, we believe in transparent pricing. The price you see on the service listing is what you pay. There are no hidden fees, service charges, or surprise costs. All pricing is clearly displayed upfront before booking.',
                'keywords': 'hidden fees, service charges, surprise costs, transparent pricing, no hidden fees'
            },
            {
                'category': 'pricing',
                'question': 'How do I pay for services?',
                'answer': 'You can pay for services through multiple secure payment methods including credit/debit cards, digital wallets, UPI, and bank transfers. Payment is processed securely through our platform, and you only pay after the service is completed to your satisfaction.',
                'keywords': 'payment, pay, credit card, debit card, UPI, digital wallet, bank transfer, secure payment'
            },
            
            # Booking Process
            {
                'category': 'booking',
                'question': 'How do I book a service?',
                'answer': 'Booking is easy! 1) Browse our services or search for what you need, 2) Select your preferred service provider, 3) Choose your preferred date and time, 4) Provide service details and location, 5) Confirm your booking. The service provider will contact you to confirm the appointment.',
                'keywords': 'book, booking, how to book, schedule, appointment, reserve, order service'
            },
            {
                'category': 'booking',
                'question': 'Can I cancel my booking?',
                'answer': 'Yes, you can cancel your booking up to 24 hours before the scheduled service time without any charges. Cancellations made less than 24 hours in advance may incur a small cancellation fee. You can cancel through your account dashboard or by contacting customer support.',
                'keywords': 'cancel, cancellation, cancel booking, reschedule, change appointment'
            },
            {
                'category': 'booking',
                'question': 'How far in advance should I book?',
                'answer': 'We recommend booking at least 24-48 hours in advance to ensure availability. However, many services can be booked for same-day or next-day service depending on provider availability. You can check real-time availability when booking.',
                'keywords': 'advance booking, how far ahead, same day, next day, availability, schedule'
            },
            {
                'category': 'booking',
                'question': 'What if I need emergency service?',
                'answer': 'For emergency services like plumbing leaks, electrical issues, or urgent repairs, we have emergency service providers available 24/7. Emergency services may have higher rates due to immediate availability. Contact our support team for emergency bookings.',
                'keywords': 'emergency, urgent, 24/7, immediate, same day, emergency service, urgent repair'
            },
            
            # Account Management
            {
                'category': 'account',
                'question': 'How do I create an account?',
                'answer': 'Creating an account is free and easy! Click the "Sign Up" button on our homepage, choose whether you want to be a customer or service provider, fill in your details, and verify your email. You can start booking services immediately after registration.',
                'keywords': 'create account, sign up, register, account, registration, new user'
            },
            {
                'category': 'account',
                'question': 'How do I become a service provider?',
                'answer': 'To become a service provider, click "Become a Provider" on our homepage, complete the registration form, provide your business details and verification documents, and wait for approval. Once approved, you can start listing your services and accepting bookings.',
                'keywords': 'become provider, service provider, join as provider, work with us, provider registration'
            },
            {
                'category': 'account',
                'question': 'How do I update my profile?',
                'answer': 'You can update your profile by logging into your account, going to the "Profile" section, and editing your personal information, contact details, and preferences. Make sure to keep your information up to date for better service matching.',
                'keywords': 'update profile, edit profile, change information, profile settings, account settings'
            },
            
            # Customer Support
            {
                'category': 'support',
                'question': 'How can I contact customer support?',
                'answer': 'You can contact our customer support team through multiple channels: 📧 Email: support@myhousehelp.com, 📞 Phone: +91-9876543210, 💬 Live chat (available on our website), 📱 WhatsApp: +91-9876543210. We\'re available Monday to Friday, 9 AM to 6 PM.',
                'keywords': 'contact, support, customer service, help, phone, email, live chat, whatsapp'
            },
            {
                'category': 'support',
                'question': 'What if I have a complaint?',
                'answer': 'We take complaints seriously and are committed to resolving them quickly. You can submit a complaint through your account dashboard, email us at complaints@myhousehelp.com, or call our support team. We aim to resolve all complaints within 24-48 hours.',
                'keywords': 'complaint, issue, problem, dispute, resolution, feedback, report'
            },
            {
                'category': 'support',
                'question': 'Do you have a mobile app?',
                'answer': 'Yes! We have a mobile app available for both Android and iOS devices. You can download it from the Google Play Store or Apple App Store. The app provides all the features of our website with added convenience for mobile users.',
                'keywords': 'mobile app, android, ios, download, app store, play store, smartphone'
            },
            
            # Quality and Safety
            {
                'category': 'general',
                'question': 'Are your service providers verified?',
                'answer': 'Yes! All our service providers go through a thorough verification process including background checks, license verification, insurance verification, and skill assessments. We also collect customer reviews and ratings to ensure quality service delivery.',
                'keywords': 'verified, background check, licensed, insured, quality, safety, trustworthy'
            },
            {
                'category': 'general',
                'question': 'What if I\'m not satisfied with the service?',
                'answer': 'Your satisfaction is our priority. If you\'re not satisfied with the service, please contact us within 24 hours. We\'ll work with the service provider to resolve the issue or provide a refund if appropriate. We also encourage you to leave honest reviews to help other customers.',
                'keywords': 'not satisfied, unhappy, refund, issue, problem, resolution, review, feedback'
            }
        ]
        
        # Create knowledge base entries
        created_count = 0
        for data in knowledge_data:
            knowledge, created = ChatbotKnowledge.objects.get_or_create(
                question=data['question'],
                defaults={
                    'category': data['category'],
                    'answer': data['answer'],
                    'keywords': data['keywords'],
                    'is_active': True
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f'Created: {data["question"]}')
        
        # Create intents
        self.stdout.write('Creating chatbot intents...')
        intents_data = [
            {
                'name': 'greeting',
                'description': 'User greeting messages',
                'examples': ['hello', 'hi', 'good morning', 'hey there'],
                'response_template': 'Hello! How can I help you today?'
            },
            {
                'name': 'service_inquiry',
                'description': 'Questions about available services',
                'examples': ['what services do you offer', 'do you have cleaning', 'plumbing services'],
                'response_template': 'We offer a wide range of home services including...'
            },
            {
                'name': 'booking_request',
                'description': 'Requests to book a service',
                'examples': ['book cleaning', 'schedule appointment', 'I need a plumber'],
                'response_template': 'I can help you book that service. Let me get some details...'
            },
            {
                'name': 'pricing_inquiry',
                'description': 'Questions about service pricing',
                'examples': ['how much does it cost', 'what are your prices', 'pricing information'],
                'response_template': 'Our pricing varies by service type. Here are our rates...'
            }
        ]
        
        intent_count = 0
        for intent_data in intents_data:
            intent, created = ChatbotIntent.objects.get_or_create(
                name=intent_data['name'],
                defaults=intent_data
            )
            if created:
                intent_count += 1
                self.stdout.write(f'Created intent: {intent_data["name"]}')
        
        # Create entities
        self.stdout.write('Creating chatbot entities...')
        entities_data = [
            {'name': 'cleaning', 'entity_type': 'service', 'value': 'cleaning service', 'synonyms': ['house cleaning', 'deep cleaning', 'office cleaning']},
            {'name': 'plumbing', 'entity_type': 'service', 'value': 'plumbing service', 'synonyms': ['plumber', 'pipe repair', 'leak fix']},
            {'name': 'electrical', 'entity_type': 'service', 'value': 'electrical service', 'synonyms': ['electrician', 'wiring', 'electrical repair']},
            {'name': 'painting', 'entity_type': 'service', 'value': 'painting service', 'synonyms': ['painter', 'wall painting', 'interior painting']},
            {'name': 'pest control', 'entity_type': 'service', 'value': 'pest control service', 'synonyms': ['pest management', 'bug control', 'termite treatment']},
            {'name': 'today', 'entity_type': 'time', 'value': 'same day', 'synonyms': ['immediately', 'asap', 'urgent']},
            {'name': 'tomorrow', 'entity_type': 'time', 'value': 'next day', 'synonyms': ['next day', 'day after']},
            {'name': 'emergency', 'entity_type': 'time', 'value': 'emergency service', 'synonyms': ['urgent', 'immediate', '24/7']},
        ]
        
        entity_count = 0
        for entity_data in entities_data:
            entity, created = ChatbotEntity.objects.get_or_create(
                name=entity_data['name'],
                entity_type=entity_data['entity_type'],
                defaults=entity_data
            )
            if created:
                entity_count += 1
                self.stdout.write(f'Created entity: {entity_data["name"]} ({entity_data["entity_type"]})')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully populated chatbot with:\n'
                f'- {created_count} knowledge entries\n'
                f'- {intent_count} intents\n'
                f'- {entity_count} entities'
            )
        )
