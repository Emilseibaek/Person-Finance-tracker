# Personal Finance Tracker

A simple web application for tracking personal finances, built with Flask and SQLAlchemy and the use of Jinja2 HTML templates.

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
- PostgreSQL
- Bootstrap 5 (CDN)

## Setup Guide (Local PostgreSQL)

This guide will walk you through setting up the project to use a local PostgreSQL database.

**Prerequisites:**

*   Python 3.11 or higher
*   PostgreSQL 14 or higher installed and running locally
*   `psql` command-line client installed and accessible

1.  **Clone the repository:**

    ```bash
    git clone <repository_url>
    cd Personal-Finance-tracker
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**

    Make sure your virtual environment is activated, then install the required Python packages:

    ```bash
    pip install -r requirements.txt
    pip install psycopg2-binary
    ```

4.  **Set up your local PostgreSQL database:**

    a.  **Connect to PostgreSQL using `psql`:**

        Open your terminal and connect to your local PostgreSQL server. This often involves connecting as your system user or the default `postgres` user.

        ```bash
        psql -U your_postgres_username postgres
        ```

        (Replace `your_postgres_username` with your actual PostgreSQL username, e.g., `emilseibaek`. You may be prompted for a password or connect automatically if peer authentication is configured.)

    b.  **Create the database:**

        Once connected to `psql` (your prompt will change), run the following command to create the database for the application:

        ```sql
        CREATE DATABASE finance_tracker;
        ```

    c.  **Exit `psql`:**

        ```sql
        \q
        ```

5.  **Configure environment variables:**

    Copy the example environment file and update it with your database connection details.

    ```bash
    cp .env.example .env
    ```

    Open the newly created `.env` file in a text editor and set the `DATABASE_URL` to point to your local PostgreSQL database. The format is generally:

    ```
    DATABASE_URL=postgresql://your_username:your_password@localhost:5432/finance_tracker
    ```

    *   Replace `your_username` and `your_password` with your PostgreSQL credentials.
    *   If you don't use a password (e.g., peer authentication), you can often omit the `:your_password` part: `postgresql://your_username@localhost:5432/finance_tracker`.

    Also, set a strong, unique `SECRET_KEY`:

    ```
    SECRET_KEY=a_long_random_and_unique_string
    ```

6.  **Initialize the database tables:**

    Run the initialization script to create the necessary tables in your `finance_tracker` database.

    ```bash
    python3 init_db.py
    ```

7.  **Run the application:**

    With your virtual environment activated and `.env` configured, you can now run the Flask application:

    ```bash
    python3 app.py
    ```

    The application should start and be accessible at `http://127.0.0.1:5000/`.

## Project Structure

```
finance_tracker/
├── app.py               # Flask application
├── models.py           # SQLAlchemy models
├── forms.py            # WTForms
├── init_db.py          # Database initialization script
├── templates/          # Jinja2 templates
├── static/            # Static files
├── requirements.txt    # Dependencies to install
├── .env.example        # Example environment variables
├── .gitignore          # Specifies intentionally untracked files
└── README.md          # Project overview and setup guide
```

