from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from services.models import ServiceCategory, Service


class Command(BaseCommand):
    help = "Add 'Cook' and 'Maid' categories and sample services"

    def handle(self, *args, **options):
        User = get_user_model()

        # Ensure at least one provider exists
        provider = User.objects.filter(role='provider').first()
        if not provider:
            self.stdout.write(self.style.ERROR('No provider users found. Please create a provider first.'))
            return

        # Create categories
        cook_cat, cook_created = ServiceCategory.objects.get_or_create(
            name='Cook', defaults={'description': 'Home cooking and meal preparation services', 'is_active': True}
        )
        maid_cat, maid_created = ServiceCategory.objects.get_or_create(
            name='Maid', defaults={'description': 'Domestic help, housekeeping, and daily chores', 'is_active': True}
        )

        if cook_created:
            self.stdout.write(self.style.SUCCESS("Created category: Cook"))
        else:
            self.stdout.write("Category exists: Cook")

        if maid_created:
            self.stdout.write(self.style.SUCCESS("Created category: Maid"))
        else:
            self.stdout.write("Category exists: Maid")

        # Create sample services for these categories
        services_to_create = [
            (cook_cat, provider, 'Home Cook Service',
             'Personal home cook available for daily meal preparation tailored to your preferences.', 25.00, 'per_hour', 3.0),
            (cook_cat, provider, 'Weekly Meal Prep',
             'Preparation of weekly meals including planning, cooking, and packaging.', 180.00, 'flat_rate', 5.0),
            (maid_cat, provider, 'Daily Maid Service',
             'Daily household chores including cleaning, dishes, laundry, and organization.', 20.00, 'per_hour', 4.0),
            (maid_cat, provider, 'Full-time Maid (Monthly)',
             'Full-time maid service for daily housekeeping needs, billed monthly.', 350.00, 'per_item', 160.0),
        ]

        created_count = 0
        for category, prov, title, description, price, unit, duration in services_to_create:
            service, created = Service.objects.get_or_create(
                provider=prov,
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
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created service: {title}"))
            else:
                self.stdout.write(f"Service exists: {title}")

        self.stdout.write(self.style.SUCCESS(
            f"Done. Categories ensured and {created_count} services created (or already existed)."
        ))
