# Personal Finance Tracker

A simple web application for tracking personal finances, built with Flask and SQLAlchemy.

## Features

- User authentication (register, login, logout)
- Track income and expenses
- Categorize transactions
- Simple dashboard with financial summaries
- Monthly category totals

## Tech Stack

- Python 3.11
- Flask 2.x
- SQLAlchemy ORM
- SQLite (default) / PostgreSQL
- Bootstrap 5 (CDN)

## Setup

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the application:
```bash
flask run
```

## Database Configuration

### SQLite (Default)
The application uses SQLite by default. No additional setup is required.

### PostgreSQL
To use PostgreSQL:

1. Install PostgreSQL and create a database
2. Set the DATABASE_URL in .env:
```
DATABASE_URL=postgresql://username:password@localhost:5432/finance_tracker
```

## Project Structure

```
finance_tracker/
├── app.py               # Flask application
├── models.py           # SQLAlchemy models
├── forms.py            # WTForms
├── templates/          # Jinja2 templates
├── static/            # Static files
├── requirements.txt    # Dependencies
└── README.md          # This file
```

## Known Limitations

- No recurring transactions
- No CSV import/export
- No budget limits
- No data export
- No email verification