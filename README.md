# 🗳️ Student Voting System

A comprehensive Django-based electronic voting system designed for university student government elections. The system implements a two-tier voting process where students first elect delegates from their departments, and then delegates vote for student government positions.

## 📋 Table of Contents

- [Features](#features)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [Security Features](#security-features)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

### 🏛️ Multi-Tier Voting System
- **Two-Phase Elections**: Students elect delegates, delegates elect government positions
- **Department-Based Representation**: Ensures fair representation across all academic departments
- **Party System**: Support for multiple political parties with candidates and delegates

### 👥 User Management
- **Custom User Model**: Student-based authentication using registration numbers
- **Hierarchical Structure**: Faculty → Department → Programme → Student organization
- **Role-Based Access**: Students, Delegates, Candidates, and Administrative roles

### 🔐 Security & Integrity
- **Secure Authentication**: Password-based login with birth certificate validation
- **Vote Anonymity**: Votes are recorded without linking to specific voters
- **Audit Trail**: Comprehensive logging of all voting activities
- **IP Tracking**: Monitor voting locations for fraud prevention
- **One Vote Per Student**: Strict enforcement of voting limits

### 📊 Election Management
- **Phase Control**: Registration → Delegate Voting → Main Voting → Results
- **Time-Based Voting**: Configurable voting periods with automatic phase transitions
- **Real-Time Results**: Live vote counting and result caching
- **Multi-Position Elections**: Support for various student government positions

### 🎨 User Interface
- **Responsive Design**: Mobile-friendly interface for all devices
- **Intuitive Navigation**: Easy-to-use voting interface
- **Real-Time Updates**: Live election status and result updates
- **Multilingual Support**: Ready for internationalization

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Students    │    │    Delegates    │    │   Candidates    │
│                 │    │                 │    │                 │
│ Vote for        │───▶│ Vote for        │───▶│ Compete for     │
│ Delegates       │    │ Positions       │    │ Positions       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Delegate Votes  │    │   Main Votes    │    │    Results      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Voting Process Flow

1. **Registration Phase**: Students register, parties nominate candidates and delegates
2. **Delegate Voting Phase**: Students vote for delegates from their departments
3. **Main Voting Phase**: Elected delegates vote for student government positions
4. **Results Phase**: Vote counting and winner declaration

## 🚀 Installation

### Prerequisites

- Python 3.8+
- Django 4.0+
- PostgreSQL/MySQL (recommended) or SQLite for development
- Redis (optional, for caching)

### Step-by-Step Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/steve-ongera/student-voting-system.git
   cd student-voting-system
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Database Setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Load Sample Data** (Optional)
   ```bash
   python manage.py seed_data --students 300
   ```

8. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in your project root:

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/voting_db
# or for SQLite
# DATABASE_URL=sqlite:///db.sqlite3

# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Security Settings
SECURE_SSL_REDIRECT=False
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True

# Email Configuration (for notifications)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True

# Redis Configuration (optional)
REDIS_URL=redis://localhost:6379/0

# File Upload Settings
MEDIA_ROOT=media/
STATIC_ROOT=staticfiles/
```

### Database Configuration

#### PostgreSQL (Recommended)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'voting_system',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

#### MySQL
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'voting_system',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'sql_mode': 'traditional',
        }
    }
}
```

## 📖 Usage

### For System Administrators

1. **Setup Election**
   - Access admin panel at `/admin/`
   - Create faculties, departments, and programmes
   - Set up parties and positions
   - Create election with voting periods

2. **Manage Users**
   - Import student data or use seed command
   - Approve delegate registrations
   - Approve candidate applications

3. **Monitor Elections**
   - Track voting progress
   - Monitor audit logs
   - Generate reports

### For Students

1. **Login**
   ```
   URL: /login/
   Username: Registration Number (e.g., SC211/0530/2022)
   Password: Birth Certificate Number
   ```

2. **Vote for Delegates**
   - Navigate to delegate voting page
   - Select delegates from your department
   - Submit vote (one-time only)

3. **View Results**
   - Check election results after voting closes
   - View candidate manifestos and party information

### For Delegates

1. **Access Delegate Portal**
   - Login with student credentials
   - Access delegate-specific voting interface

2. **Vote for Positions**
   - Vote for candidates in each position
   - Review manifestos before voting

### Management Commands

```bash
# Seed database with sample data
python manage.py seed_data --students 300

# Clear and reseed data
python manage.py seed_data --clear --students 500

# Export election results
python manage.py export_results --election-id 1

# Send election notifications
python manage.py send_notifications --type voting_reminder

# Backup database
python manage.py backup_db

# Generate reports
python manage.py generate_reports --election-id 1
```

## 📊 Database Schema

### Core Models

#### Student (Custom User)
```python
- registration_number (Primary Key)
- birth_certificate_number
- first_name, last_name
- email, phone_number
- programme (Foreign Key)
- year_of_study
- Authentication fields
```

#### Academic Structure
```python
Faculty
├── Department
    └── Programme
        └── Student
```

#### Electoral System
```python
Party
├── Delegates (max 15 per party)
│   └── DelegateVotes (students → delegates)
└── Candidates (one per position per party)
    └── MainVotes (delegates → candidates)
```

### Key Relationships

- **Student → Programme → Department → Faculty**
- **Delegate → Student + Party + Department**
- **Candidate → Student + Party + Position**
- **Vote → Voter + Candidate/Delegate + Election**

## 🔒 Security Features

### Authentication & Authorization
- Custom user model with student registration numbers
- Password validation using birth certificate numbers
- Session-based authentication with secure cookies
- Role-based access control (RBAC)

### Vote Security
- Anonymous voting with vote separation
- One vote per student enforcement
- IP address logging for fraud detection
- Vote tampering prevention
- Audit trail for all activities

### Data Protection
- SQL injection prevention
- XSS protection
- CSRF protection
- Secure file uploads
- Input validation and sanitization

### System Security
```python
# Security settings in settings.py
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'DENY'
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test voting

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Test Categories

1. **Model Tests**: Validation, constraints, methods
2. **View Tests**: Authentication, permissions, responses
3. **Form Tests**: Validation, security, user input
4. **Integration Tests**: End-to-end voting process
5. **Security Tests**: Authentication, authorization, data protection

### Sample Test Structure

```python
# tests/test_models.py
class StudentModelTest(TestCase):
    def test_student_creation(self):
        """Test student model creation with valid data"""
        
    def test_registration_number_validation(self):
        """Test registration number format validation"""
        
    def test_voting_permissions(self):
        """Test student voting permissions"""

# tests/test_voting.py
class VotingProcessTest(TestCase):
    def test_delegate_voting_process(self):
        """Test complete delegate voting workflow"""
        
    def test_main_voting_process(self):
        """Test complete main voting workflow"""
        
    def test_vote_security(self):
        """Test vote tampering prevention"""
```

## 🚀 Deployment

### Production Setup

1. **Server Requirements**
   - Ubuntu 20.04+ or CentOS 8+
   - Python 3.8+
   - PostgreSQL 12+
   - Nginx
   - Redis (optional)

2. **Security Configuration**
   ```python
   # Production settings
   DEBUG = False
   ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
   SECURE_SSL_REDIRECT = True
   SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
   ```

3. **Static Files**
   ```bash
   python manage.py collectstatic
   ```

4. **Database Migration**
   ```bash
   python manage.py migrate --run-syncdb
   ```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.9

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "voting_project.wsgi:application"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/voting_db
    depends_on:
      - db
      - redis

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=voting_db
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6

volumes:
  postgres_data:
```

### Monitoring & Logging

```python
# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'voting_system.log',
        },
    },
    'loggers': {
        'voting': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## 📈 Performance Optimization

### Database Optimization
- Database indexing on frequently queried fields
- Query optimization with select_related and prefetch_related
- Database connection pooling
- Read replicas for reporting

### Caching Strategy
```python
# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Cache voting results
CACHE_TTL = 60 * 15  # 15 minutes
```

### Load Balancing
- Use multiple application servers
- Database read/write separation
- CDN for static files
- Session storage in Redis

## 🛠️ Maintenance

### Regular Tasks
```bash
# Weekly maintenance script
#!/bin/bash

# Backup database
python manage.py backup_db

# Clean old audit logs (older than 1 year)
python manage.py cleanup_audit_logs --days 365

# Generate weekly reports
python manage.py generate_reports --weekly

# Update vote caches
python manage.py refresh_vote_cache
```

### Monitoring Scripts
```bash
# System health check
python manage.py health_check

# Database integrity check
python manage.py check_db_integrity

# Security audit
python manage.py security_audit
```

## 🤝 Contributing

### Development Setup

1. **Fork the repository**
2. **Create feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Follow coding standards**
   - PEP 8 for Python code
   - Black for code formatting
   - pylint for code analysis

4. **Write tests**
   - Unit tests for models and views
   - Integration tests for workflows
   - Minimum 80% code coverage

5. **Submit pull request**

### Code Style

```bash
# Format code
black .

# Lint code
pylint voting/

# Sort imports
isort .

# Type checking
mypy voting/
```

### Commit Convention
```
feat: add new voting feature
fix: resolve delegate voting bug
docs: update README installation steps
style: format code with black
refactor: restructure voting models
test: add delegate voting tests
chore: update dependencies
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help

- **Documentation**: Check this README and inline code documentation
- **Issues**: Create an issue on GitHub for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Email**: Contact the maintainers at support@votingsystem.com

### Reporting Security Issues

If you discover a security vulnerability, please email security@votingsystem.com instead of creating a public issue.

### FAQ

**Q: Can students change their votes after submission?**
A: No, votes are final once submitted to maintain election integrity.

**Q: How are vote results calculated?**
A: Simple majority voting with real-time counting and result caching.

**Q: What happens if there's a tie?**
A: The system records ties and allows administrators to implement tiebreaking procedures.

**Q: Can the system handle multiple concurrent elections?**
A: Yes, the system supports multiple elections with different phases and participants.

**Q: How is vote anonymity maintained?**
A: Votes are stored separately from voter information with cryptographic techniques ensuring anonymity.

---

## 🎯 Project Status

- ✅ **Core Features**: Complete
- ✅ **Security**: Implemented
- ✅ **Testing**: Comprehensive
- ⏳ **Mobile App**: In Progress
- 📋 **Analytics Dashboard**: Planned
- 📋 **Multi-language Support**: Planned

## 📞 Contact

**Project Maintainer**: [Your Name](mailto:your.steveongera@gmail.com)  
**Project Link**: [https://github.com/steve-ongera/student-voting-system](https://github.com/steve-ongera/student-voting-system)

---

Made with Steve for democratic student governance