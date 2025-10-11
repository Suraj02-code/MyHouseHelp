# Home Service Application

A comprehensive home service marketplace that connects customers with verified service providers for household needs like cleaning, plumbing, electrical work, appliance repair, painting, pest control, and maintenance.

## Features

### Customer Features
- 🔍 **Service Search & Discovery**: Browse and search for services by category, location, and availability
- 📅 **Easy Booking**: Book services with preferred dates and times
- 💳 **Secure Payments**: Multiple payment methods with secure processing
- 📊 **Progress Tracking**: Real-time updates on service status
- ⭐ **Review System**: Rate and review service providers
- 🎯 **Smart Recommendations**: ML-powered provider suggestions

### Service Provider Features  
- 📋 **Profile Management**: Complete business profile with verification
- 💼 **Service Listings**: Create and manage service offerings
- 📅 **Availability Management**: Set working hours and available time slots
- 💰 **Dynamic Pricing**: AI-suggested pricing based on demand
- 📈 **Analytics Dashboard**: Track bookings, earnings, and performance
- 💬 **Customer Communication**: Direct messaging and review responses

### Admin Features
- ✅ **Provider Verification**: Verify service provider credentials
- 👥 **User Management**: Manage customers and providers
- 💰 **Transaction Monitoring**: Oversee payments and disputes
- 📊 **Analytics & Reports**: Business insights and performance metrics
- 🔧 **System Configuration**: Manage categories and settings

### Machine Learning Features
- 🤖 **Provider Recommendations**: Suggest best-fit providers for customers
- 💲 **Dynamic Pricing**: Real-time price optimization based on demand
- 📈 **Demand Forecasting**: Predict seasonal service demand patterns
- 🎭 **Sentiment Analysis**: Analyze customer reviews and feedback

## Technology Stack

- **Backend**: Django 4.2.7 (Python)
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: Django Templates (with option for React)
- **Machine Learning**: scikit-learn, pandas, numpy
- **NLP**: NLTK, TextBlob
- **Payments**: Stripe (integration ready)
- **Image Processing**: Pillow

## Project Structure

```
home-service-app/
├── accounts/           # User management and profiles
├── services/          # Service categories and listings
├── bookings/          # Booking management
├── reviews/           # Review and rating system
├── payments/          # Payment processing
├── ml_engine/         # Machine learning components
├── templates/         # HTML templates
├── static/            # CSS, JavaScript, images
├── media/             # User-uploaded files
├── homeservice/       # Django project settings
├── manage.py          # Django management script
└── requirements.txt   # Python dependencies
```

## Installation & Setup

### Prerequisites
- Python 3.11+
- pip (Python package installer)

### Quick Start

1. **Clone or navigate to the project directory**
   ```bash
   cd home-service-app
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser (admin)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Main site: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

### Default Admin Credentials
- **Username**: admin  
- **Password**: admin123
- **Email**: admin@homeservice.com

## Database Models

### Core Models

**User Roles**:
- `Customer`: Book and pay for services
- `Service Provider`: Offer services and manage bookings  
- `Administrator`: Manage platform and users

**Key Entities**:
- **ServiceCategory**: Cleaning, Plumbing, Electrical, etc.
- **Service**: Individual service offerings with pricing
- **Booking**: Customer service requests and appointments
- **Payment**: Transaction records and payment processing
- **Review**: Customer feedback and ratings
- **ML Models**: Recommendations, pricing, and analytics

## API Endpoints (Future Implementation)

```
/api/auth/          # Authentication endpoints
/api/users/         # User management
/api/services/      # Service listings
/api/bookings/      # Booking management  
/api/payments/      # Payment processing
/api/reviews/       # Review system
/api/ml/           # ML recommendations
```

## Machine Learning Features

### 1. Provider Recommendations
- **Algorithm**: Collaborative filtering + content-based filtering
- **Factors**: Location, ratings, price, availability, past bookings
- **Output**: Ranked list of suitable providers

### 2. Dynamic Pricing
- **Algorithm**: Regression models with demand forecasting
- **Factors**: Time, location, demand, competition, urgency
- **Output**: Optimal price suggestions

### 3. Sentiment Analysis
- **Algorithm**: NLTK + TextBlob for review analysis
- **Input**: Customer review text
- **Output**: Sentiment score (-1 to 1) and classification

### 4. Demand Forecasting
- **Algorithm**: Time series analysis with seasonal decomposition
- **Factors**: Historical data, seasonality, external events
- **Output**: Predicted demand for services

## Development Workflow

### Adding New Features
1. Create models in appropriate app
2. Run `python manage.py makemigrations`
3. Run `python manage.py migrate`
4. Update admin.py for model management
5. Create views and templates
6. Add URL patterns
7. Write tests

### Testing
```bash
python manage.py test                    # Run all tests
python manage.py test accounts          # Test specific app
python manage.py test --verbose         # Detailed output
```

## Deployment Options

### 1. Heroku
```bash
pip install gunicorn
# Add Procfile: web: gunicorn homeservice.wsgi
git push heroku main
```

### 2. Railway
- Connect GitHub repository
- Set environment variables
- Deploy automatically

### 3. PythonAnywhere  
- Upload code via Git or files
- Configure WSGI file
- Set up static files

### 4. AWS EC2
```bash
sudo apt update
sudo apt install python3-pip nginx
# Setup Django, gunicorn, nginx
```

## Environment Configuration

Create `.env` file for sensitive settings:
```
SECRET_KEY=your-secret-key-here
DEBUG=False
DATABASE_URL=postgresql://user:pass@localhost/dbname
STRIPE_PUBLIC_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
```

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## Security Considerations

- ✅ Custom User model with role-based access
- ✅ CSRF protection enabled
- ✅ SQL injection protection (Django ORM)
- ✅ Secure password validation
- ✅ File upload validation
- ✅ Payment data encryption ready

## Performance Optimization

- **Database**: Add indexes for frequently queried fields
- **Caching**: Implement Redis for session and data caching
- **CDN**: Use CloudFlare or AWS CloudFront for static files
- **Monitoring**: Add Sentry for error tracking

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Create GitHub issue
- Email: support@homeservice.com
- Documentation: Check this README and code comments

## Roadmap

- [ ] RESTful API development
- [ ] React.js frontend
- [ ] Mobile app (React Native)
- [ ] Real-time chat system
- [ ] Advanced ML models
- [ ] Multi-language support
- [ ] Third-party integrations