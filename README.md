 Equipment Rental Management System

A comprehensive web-based application for managing equipment rentals, built with modern web technologies to streamline rental operations for businesses.

🚀 Features

- Equipment Management: Add, edit, and track rental equipment inventory
- Customer Management: Maintain customer records and rental history
- Rental Tracking: Monitor active rentals, due dates, and returns
- Payment Processing: Handle rental payments and generate invoices
- Reporting: Generate detailed reports on rentals, revenue, and equipment utilization
- User Authentication: Secure login system with role-based access control
- Responsive Design: Mobile-friendly interface for on-the-go management

🛠️ Technology Stack

Frontend
- HTML5: Modern semantic markup
- CSS3: Responsive styling with modern layouts
- JavaScript (ES6+): Interactive user interface and client-side logic
- Tailwind CSS/CSS Framework: Responsive design components

 Backend
- Python: Programming language for server-side logic
- Django: High-level Python web framework
- MySQL: Database support (configurable)
- Django REST Framework: API development (if applicable)

Additional Tools
- AJAX: Asynchronous data loading and form submissions
- JSON: Data exchange format
- Django Sessions: User authentication and authorization
- Django ORM: Object-relational mapping for database operations

 Prerequisites

Before you begin, ensure you have the following installed:

- Python: Version 3.8 or higher
- pip: Python package installer
- Virtual Environment: venv or virtualenv
- Database: MySQL
- Git: Version control system

## 🔧 Installation

1. Clone the repository
   ```bash
   git clone https://github.com/Oriiswan/Equipment-Rental-Management-System.git
   cd Equipment-Rental-Management-System
   ```

2. Create and activate virtual environment
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables
   ```bash
   # Create .env file in project root
   cp .env.example .env
   
   # Edit .env file with your settings
   SECRET_KEY=your_secret_key_here
   DEBUG=True
   DATABASE_URL=sqlite:///db.sqlite3
   # or for PostgreSQL: postgresql://user:password@localhost/dbname
   ```

5. Run database migrations
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. Create superuser account
   ```bash
   python manage.py createsuperuser
   ```

7. Collect static files (for production)
   ```bash
   python manage.py collectstatic
   ```

8. Run the development server
   ```bash
   python manage.py runserver
   ```

 Usage

1. Access the application
   - Start the development server: `python manage.py runserver`
   - Open your web browser and navigate to `http://127.0.0.1:8000/`

2. Admin Panel Access
   - Navigate to `http://127.0.0.1:8000/admin/`
   - Login with your superuser credentials

3. Initial Setup
   - Configure system settings through the admin panel
   - Add equipment categories and initial inventory

4. Basic Operations
   - Add Equipment: Navigate to Equipment → Add New Equipment
   - Register Customers: Go to Customers → Add New Customer
   - Create Rentals: Use the Rental → New Rental form
   - Process Returns: Track and process equipment returns
   - Generate Reports: Access various reports from the Reports section

 📁 Project Structure

```
Equipment-Rental-Management-System/
├── equipment_rental/          # Main Django project directory
│   ├── __init__.py
│   ├── settings.py           # Django settings
│   ├── urls.py              # URL routing
│   ├── wsgi.py              # WSGI configuration
│   └── asgi.py              # ASGI configuration
├── apps/                    # Django applications
│   ├── equipment/           # Equipment management app
│   │   ├── models.py        # Equipment models
│   │   ├── views.py         # Equipment views
│   │   ├── urls.py          # Equipment URLs
│   │   └── admin.py         # Admin configuration
│   ├── customers/           # Customer management app
│   ├── rentals/            # Rental operations app
│   └── reports/            # Reporting system app
├── static/                 # Static files (CSS, JS, images)
│   ├── css/               # Stylesheets
│   ├── js/                # JavaScript files
│   └── images/            # Image assets
├── media/                 # User uploaded files
├── templates/             # Django templates
│   ├── base.html         # Base template
│   ├── equipment/        # Equipment templates
│   ├── customers/        # Customer templates
│   └── rentals/          # Rental templates
├── requirements.txt      # Python dependencies
├── manage.py            # Django management script
├── .env.example         # Environment variables example
├── db.sqlite3          # SQLite database (default)
└── README.md           # This file
```

🔐 Default Credentials

After creating a superuser account, you can log in with:
- Navigate to: `http://127.0.0.1:8000/admin/`
- Use your created superuser credentials

Important: Use strong passwords and change default settings for production deployment.

🤝 Contributing

We welcome contributions to improve the Equipment Rental Management System! Here's how you can contribute:

1. Fork the repository
2. Create a feature branch
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. Commit your changes
   ```bash
   git commit -m 'Add some amazing feature'
   ```
4. Push to the branch
   ```bash
   git push origin feature/amazing-feature
   ```
5. Open a Pull Request

Development Guidelines

- Follow PEP 8 coding standards for Python
- Use Django best practices and conventions
- Write meaningful docstrings for functions and classes
- Create Django migrations for model changes
- Use Django's built-in testing framework
- Update documentation as needed

 Setting up for Development

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python manage.py test

# Run code formatting
black .
flake8 .

# Create new Django app
python manage.py startapp app_name
```

 🐛 Troubleshooting

Common Issues

Django Server Won't Start
- Check if another process is using port 8000
- Verify virtual environment is activated
- Ensure all dependencies are installed: `pip install -r requirements.txt`

Database Migration Errors
- Delete migration files and recreate: `python manage.py makemigrations`
- Check for model conflicts or circular imports
- Reset database if needed: `python manage.py flush`

Static Files Not Loading
- Run `python manage.py collectstatic`
- Check STATIC_URL and STATIC_ROOT settings
- Verify DEBUG setting in settings.py

Import Module Errors
- Ensure virtual environment is activated
- Check Python path and Django app registration
- Verify app is listed in INSTALLED_APPS

 📊 Database Schema

The system uses Django models with the following main entities:
- User - User accounts and authentication (Django's built-in)
- Equipment - Equipment inventory and details
- Customer - Customer information and contacts
- Rental - Rental transactions and status
- Payment - Payment records and invoices
- Category - Equipment categories and types

Django automatically handles database relationships, migrations, and ORM operations.

🔒 Security Features

- Django's built-in password hashing with PBKDF2
- SQL injection prevention using Django ORM
- Cross-Site Scripting (XSS) protection with Django templates
- CSRF protection with Django middleware
- Session-based authentication with Django's auth system
- Permission and group-based access control
- Input validation using Django forms and validators

📈 Future Enhancements

- [ ] REST API development for mobile app integration
- [ ] Advanced reporting with charts and graphs
- [ ] Online payment gateway integration
- [ ] Equipment maintenance scheduling
- [ ] Multi-location support
- [ ] Barcode/QR code scanning for equipment

 📞 Support

If you encounter any issues or need assistance:

1. Check the [Issues](https://github.com/Oriiswan/Equipment-Rental-Management-System/issues) section
2. Create a new issue with detailed description
3. Contact the development team

 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

 👏 Acknowledgments

- Built with modern web development best practices
- Inspired by real-world equipment rental business needs

---

Made with ❤️ by [Oriiswan](https://github.com/Oriiswan)

For more information, visit the [project repository](https://github.com/Oriiswan/Equipment-Rental-Management-System).
