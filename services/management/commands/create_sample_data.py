from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import CustomerProfile, ServiceProviderProfile
from services.models import ServiceCategory, Service, ServiceAvailability
from reviews.models import Review
from bookings.models import Booking
from datetime import datetime, time, timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample data for development and testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset all data before creating new samples',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('Resetting existing data...')
            # Keep admin user but remove others
            User.objects.filter(role__in=['customer', 'provider']).delete()
            ServiceCategory.objects.all().delete()
            Service.objects.all().delete()

        self.stdout.write('Creating sample data...')
        
        # Create service categories
        categories_data = [
            ('Cleaning', 'Professional cleaning services for homes and offices', '🧹'),
            ('Plumbing', 'Plumbing repairs, installations, and maintenance', '🔧'),
            ('Electrical', 'Electrical repairs and installations', '⚡'),
            ('Appliance Repair', 'Repair and maintenance of home appliances', '🔨'),
            ('Painting', 'Interior and exterior painting services', '🎨'),
            ('Pest Control', 'Professional pest control and extermination', '🐜'),
            ('Maintenance', 'General home maintenance and handyman services', '🏠'),
            ('Landscaping', 'Garden and lawn care services', '🌱'),
        ]
        
        categories = []
        for name, description, icon in categories_data:
            category, created = ServiceCategory.objects.get_or_create(
                name=name,
                defaults={'description': description, 'is_active': True}
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Created category: {name}')

        # Create sample customers
        customer_data = [
            ('john_customer', 'John', 'Smith', 'john@customer.com', '+1234567890', '123 Main St, Downtown'),
            ('sarah_customer', 'Sarah', 'Johnson', 'sarah@customer.com', '+1234567891', '456 Oak Ave, Uptown'),
            ('mike_customer', 'Mike', 'Davis', 'mike@customer.com', '+1234567892', '789 Pine Rd, Midtown'),
        ]

        customers = []
        for username, first_name, last_name, email, phone, address in customer_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'phone_number': phone,
                    'address': address,
                    'role': 'customer',
                }
            )
            if created:
                user.set_password('demo123')
                user.save()
                CustomerProfile.objects.get_or_create(user=user)
                customers.append(user)
                self.stdout.write(f'Created customer: {username}')

        # Create sample service providers
        provider_data = [
            ('clean_pro', 'Clean', 'Pro', 'info@cleanpro.com', '+1234567900', '100 Service St', 'CleanPro Services', 'Professional cleaning with 10+ years experience', 10),
            ('fix_it_fast', 'Bob', 'Wilson', 'bob@fixitfast.com', '+1234567901', '200 Repair Ave', 'Fix It Fast', 'Quick and reliable handyman services', 8),
            ('electric_expert', 'Alice', 'Brown', 'alice@electricexpert.com', '+1234567902', '300 Power Ln', 'Electric Expert', 'Licensed electrician with 15+ years experience', 15),
            ('plumb_perfect', 'Tom', 'Anderson', 'tom@plumbperfect.com', '+1234567903', '400 Water St', 'Plumb Perfect', 'Your trusted plumbing partner', 12),
            ('paint_masters', 'Lisa', 'Garcia', 'lisa@paintmasters.com', '+1234567904', '500 Color Dr', 'Paint Masters', 'Interior and exterior painting specialists', 7),
        ]

        providers = []
        for username, first_name, last_name, email, phone, address, business_name, description, experience in provider_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'phone_number': phone,
                    'address': address,
                    'role': 'provider',
                }
            )
            if created:
                user.set_password('demo123')
                user.save()
                
                profile = ServiceProviderProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'business_name': business_name,
                        'description': description,
                        'years_of_experience': experience,
                        'verification_status': 'verified',
                        'is_available': True,
                        'average_rating': round(random.uniform(4.0, 5.0), 1),
                        'completed_jobs': random.randint(50, 200),
                    }
                )[0]
                
                providers.append(user)
                self.stdout.write(f'Created provider: {username}')

        # Create sample services
        services_data = [
            # Cleaning services
            (categories[0], providers[0], 'Deep House Cleaning', 'Complete deep cleaning of your entire home including all rooms, bathrooms, kitchen, and common areas.', 150.00, 'flat_rate', 4.0),
            (categories[0], providers[0], 'Weekly House Cleaning', 'Regular weekly cleaning service to keep your home spotless.', 80.00, 'flat_rate', 2.5),
            (categories[0], providers[0], 'Office Cleaning', 'Professional office cleaning services for businesses.', 120.00, 'flat_rate', 3.0),
            
            # Handyman services
            (categories[6], providers[1], 'Home Repair Service', 'General home repairs including minor plumbing, electrical, and carpentry work.', 75.00, 'per_hour', 1.0),
            (categories[6], providers[1], 'Furniture Assembly', 'Professional assembly of furniture from IKEA, Wayfair, and other retailers.', 60.00, 'per_hour', 2.0),
            (categories[6], providers[1], 'TV Wall Mounting', 'Safe and secure TV mounting service with cable management.', 120.00, 'flat_rate', 1.5),
            
            # Electrical services
            (categories[2], providers[2], 'Electrical Outlet Installation', 'Installation of new electrical outlets and switches.', 85.00, 'per_item', 1.0),
            (categories[2], providers[2], 'Ceiling Fan Installation', 'Professional ceiling fan installation with existing wiring.', 150.00, 'flat_rate', 2.0),
            (categories[2], providers[2], 'Electrical Troubleshooting', 'Diagnose and repair electrical issues in your home.', 95.00, 'per_hour', 1.0),
            
            # Plumbing services
            (categories[1], providers[3], 'Leak Repair', 'Quick repair of leaky faucets, pipes, and fixtures.', 80.00, 'per_hour', 1.5),
            (categories[1], providers[3], 'Toilet Installation', 'Complete toilet removal and installation service.', 200.00, 'flat_rate', 2.5),
            (categories[1], providers[3], 'Drain Cleaning', 'Professional drain cleaning and unclogging service.', 120.00, 'flat_rate', 1.0),
            
            # Painting services
            (categories[4], providers[4], 'Interior Room Painting', 'Professional interior painting service for single rooms.', 400.00, 'flat_rate', 8.0),
            (categories[4], providers[4], 'Exterior House Painting', 'Complete exterior house painting with premium paint.', 2500.00, 'flat_rate', 40.0),
            (categories[4], providers[4], 'Touch-up Painting', 'Small touch-up and repair painting service.', 50.00, 'per_hour', 1.0),
        ]

        services = []
        for category, provider, title, description, price, unit, duration in services_data:
            service, created = Service.objects.get_or_create(
                provider=provider,
                title=title,
                defaults={
                    'category': category,
                    'description': description,
                    'base_price': price,
                    'price_unit': unit,
                    'duration_hours': duration,
                    'is_active': True,
                }
            )
            services.append(service)
            if created:
                self.stdout.write(f'Created service: {title}')

        # Create availability for providers
        for provider in providers:
            # Create weekday availability 9-5
            for day in range(5):  # Monday to Friday
                ServiceAvailability.objects.get_or_create(
                    provider=provider,
                    day_of_week=day,
                    start_time=time(9, 0),
                    end_time=time(17, 0),
                    defaults={'is_available': True}
                )
            
            # Create weekend availability 10-4
            for day in [5, 6]:  # Saturday and Sunday
                ServiceAvailability.objects.get_or_create(
                    provider=provider,
                    day_of_week=day,
                    start_time=time(10, 0),
                    end_time=time(16, 0),
                    defaults={'is_available': True}
                )

        # Create some sample bookings and reviews
        if customers and services:
            for i in range(10):
                customer = random.choice(customers)
                service = random.choice(services)
                
                booking_date = datetime.now().date() + timedelta(days=random.randint(-30, 30))
                booking_time = time(random.randint(9, 16), random.choice([0, 30]))
                
                booking, created = Booking.objects.get_or_create(
                    customer=customer,
                    provider=service.provider,
                    service=service,
                    booking_date=booking_date,
                    booking_time=booking_time,
                    defaults={
                        'service_address': customer.address,
                        'quoted_price': service.base_price,
                        'final_price': service.base_price,
                        'status': random.choice(['completed', 'pending', 'confirmed']),
                        'estimated_duration': service.duration_hours,
                    }
                )
                
                # Create review for completed bookings
                if created and booking.status == 'completed' and random.choice([True, False]):
                    Review.objects.create(
                        booking=booking,
                        customer=customer,
                        provider=service.provider,
                        overall_rating=random.randint(4, 5),
                        quality_rating=random.randint(4, 5),
                        timeliness_rating=random.randint(4, 5),
                        communication_rating=random.randint(4, 5),
                        value_rating=random.randint(4, 5),
                        comment=random.choice([
                            'Excellent service! Very professional and thorough.',
                            'Great work, would definitely book again.',
                            'Fast, reliable, and high quality service.',
                            'Very satisfied with the results.',
                            'Professional and courteous service provider.',
                        ]),
                        is_verified=True,
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created sample data:\n'
                f'- {len(categories)} service categories\n'
                f'- {len(customers)} customers\n'
                f'- {len(providers)} service providers\n'
                f'- {len(services)} services\n'
                f'- Sample bookings and reviews\n\n'
                f'Login credentials:\n'
                f'Admin: admin / admin123\n'
                f'Customer: john_customer / demo123\n'
                f'Provider: clean_pro / demo123'
            )
        )