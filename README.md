# Abigon

Modern classified ads platform built with Django.

## Features

- User authentication with email verification
- Social auth (Google, Facebook)
- Responsive design with Bootstrap 5
- Real-time updates with HTMX
- Redis caching
- PostgreSQL database
- Nginx + Gunicorn deployment setup

## Tech Stack

- Python 3.10+
- Django 5.2
- PostgreSQL 14
- Redis 6.0
- Nginx
- Gunicorn
- HTMX
- Bootstrap 5

## Installation

1. Clone the repository:
```bash
git clone https://github.com/dsergy/abigon.git
cd abigon
```

2. Create virtual environment:
```bash
python3 -m venv env
source env/bin/activate  # Linux/Mac
# or
.\env\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables in `.env`:
```
DB_NAME=abigon
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create superuser:
```bash
python manage.py createsuperuser
```

7. Run development server:
```bash
python manage.py runserver
```

## Production Deployment

See [deployment guide](docs/deployment.md) for detailed instructions on setting up the production environment with Nginx and Gunicorn.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
