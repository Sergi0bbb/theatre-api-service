# Theatre API service
The Theatre API Service is a API designed to manage theatre plays and ticket orders.

## Features
1. User registration and authentication
2. Manage theatre plays
3. Order tickets for plays
4. Filter plays by various parameters (e.g., genre, date)

## Technologies Used
1. Python 3.x
2. Django
3. Django REST Framework
4. PostgreSQL
5. DRF simplejwt (for JWT authentication)

# Installation
```
1. Clone the repository: https://github.com/Sergi0bbb/theatre-api-service.git
2. cd theatre_api_service
3. Create a virtual environment: python -m venv venv
4. Activate the virtual environment:
   On Windows: venv\Scripts\activate
   On macOS/Linux: source venv/bin/activate
5. Install the required packages: pip install -r requirements.txt
6. Set up the database (PostgreSQL example):
   Update the database settings in settings.py.
7. Create a superuser (optional):
   python manage.py createsuperuser
8. Run the development server:
   python manage.py runserver
```
