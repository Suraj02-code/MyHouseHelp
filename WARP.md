# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is a Django-based home service marketplace that connects customers with verified service providers. The application uses Django 4.2.7 with a custom user system, machine learning features, and comprehensive business logic for bookings, payments, and reviews.

## Architecture

### Core Django Structure

**Custom User System**: Uses `AUTH_USER_MODEL = 'accounts.User'` with role-based access:
- `customer`: Books and pays for services
- `provider`: Offers services and manages bookings  
- `admin`: Manages platform and users

**App Organization**:
- `accounts/`: User management with role-specific profiles (CustomerProfile, ServiceProviderProfile, AdminProfile)
- `services/`: Service categories, listings, availability, and geographic service areas
- `bookings/`: Complete booking lifecycle with status tracking, cancellations, and history
- `reviews/`: Multi-dimensional rating system with sentiment analysis and response capabilities
- `payments/`: Payment processing with refunds, invoices, and stored payment methods
- `ml_engine/`: Machine learning predictions for recommendations, pricing, and demand forecasting

### Key Model Relationships

**Central Booking Flow**: Customer → Service → Booking → Payment → Review → ML Analysis
- Bookings link customers to providers through specific services
- Payments track the complete financial lifecycle including refunds
- Reviews feed into ML recommendation and sentiment analysis systems
- ML predictions inform dynamic pricing and provider recommendations

**Profile Extensions**: Each user role has a specialized profile model with role-specific fields and business logic

## Development Commands

### Environment Setup
```bash
# Activate virtual environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Database Management
```bash
# Create and apply migrations
python manage.py makemigrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser
```

### Development Server
```bash
# Run development server
python manage.py runserver

# Access points:
# http://127.0.0.1:8000/ - Main application
# http://127.0.0.1:8000/admin/ - Admin interface
```

### Testing
```bash
# Run all tests
python manage.py test

# Run tests for specific app
python manage.py test accounts
python manage.py test services
python manage.py test bookings

# Run with verbose output
python manage.py test --verbose

# Run specific test class or method
python manage.py test accounts.tests.UserModelTest
```

### Code Quality
```bash
# Format code with Black
black .

# Lint code with flake8
flake8 .

# Run both formatting and linting
black . && flake8 .
```

### Django Shell and Management
```bash
# Open Django shell
python manage.py shell

# Collect static files
python manage.py collectstatic

# Check for common issues
python manage.py check

# Show migrations status
python manage.py showmigrations
```

## Development Patterns

### Model Design Patterns
- **Role-based user profiles**: Each user type extends base User with OneToOneField relationship
- **Status tracking**: Models like Booking and Payment use choice fields with comprehensive status workflows
- **Audit trails**: Models include created_at/updated_at timestamps and history tracking (BookingStatusHistory)
- **ML integration**: Models store ML predictions and scores as JSONField data with version tracking

### Business Logic Patterns
- **Cascade relationships**: Related objects properly cascade on deletion where appropriate
- **Calculated fields**: Methods like `update_rating()` in ServiceProviderProfile automatically recalculate derived data
- **Validation**: Uses Django validators for phone numbers, ratings, and monetary amounts

### Key Relationships to Understand
- User → Profile (OneToOne, role-specific)
- Provider → Service (OneToMany, with categories and availability)
- Customer + Service → Booking (ManyToOne, central business object)  
- Booking → Payment → Refund (OneToMany cascade)
- Booking → Review → ML Analysis (OneToOne with sentiment processing)

## Machine Learning Integration

The `ml_engine` app provides:
- **Provider Recommendations**: Multi-factor scoring (compatibility, distance, rating, price, availability)
- **Dynamic Pricing**: Demand-based price optimization with market factors
- **Demand Forecasting**: Time series analysis with seasonal and trend factors
- **Sentiment Analysis**: Review text processing with confidence scoring

ML models store predictions as JSONField data with versioning and confidence scores.

## Database Schema Notes

- Uses SQLite for development, PostgreSQL for production
- Custom User model with role field drives application permissions
- Complex foreign key relationships require careful migration ordering
- JSONField usage for flexible ML data storage and metadata

## Configuration

- Main settings in `homeservice/settings.py`
- Custom user model configured with `AUTH_USER_MODEL`
- Static and media file handling configured for development and production
- Timezone set to UTC with internationalization enabled

## Deployment Considerations

- Configured for Heroku with `Procfile` (gunicorn)
- WhiteNoise for static file serving
- Environment variables should be used for sensitive settings (SECRET_KEY, DATABASE_URL)
- ML model files and media uploads need persistent storage in production