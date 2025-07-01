## Project Guidelines for IT Ticketing System

This document provides guidelines for developing the IT Ticketing System.

### 1. General
    - The primary framework is Python Flask.
    - Follow PEP 8 for Python code style.
    - Use a virtual environment for managing dependencies.
    - Keep secrets (like `SECRET_KEY`, database URIs) out of the codebase; use environment variables (e.g., via a `.env` file).

### 2. Directory Structure
    - Main application logic resides in the `app/` directory.
    - Flask Blueprints should be used to organize different parts of the application (e.g., `auth`, `tickets`, `inventory`).
    - Static files (CSS, JS, images) go into `app/static/`.
    - HTML templates go into `app/templates/`.
    - Database models should be defined in `app/models.py`.
    - Forms should be defined in `app/forms.py` (globally) or `app/<blueprint_name>/forms.py` (blueprint-specific).
    - Routes for blueprints should be in `app/<blueprint_name>/routes.py`.

### 3. Database
    - SQLAlchemy is used as the ORM.
    - Flask-Migrate should be used for database migrations.
    - Define models in `app/models.py`.

### 4. Authentication
    - Use Flask-Login for managing user sessions.
    - Passwords must be hashed before storing in the database.

### 5. Forms
    - Use Flask-WTF for creating and validating forms.

### 6. Blueprints
    - Each major functional area (auth, tickets, inventory, main) should be a separate blueprint.
    - `app/main/routes.py` for general site routes (e.g., homepage, about page).
    - `app/auth/routes.py` for authentication routes (login, logout, register).
    - `app/tickets/routes.py` for ticketing system routes.
    - `app/inventory/routes.py` for inventory system routes.

### 7. Templates
    - Use a base template (`app/templates/base.html`) that other templates can extend.
    - Use Jinja2 templating features.
    - Blueprint-specific templates should be in `app/<blueprint_name>/templates/<blueprint_name>/`.

### 8. Error Handling
    - Implement custom error pages for common HTTP errors (e.g., 404, 500) - (Future Step).

### 9. Testing
    - Write unit tests for critical components (models, form validation, business logic).
    - Aim for good test coverage.

### 10. Commits
    - Write clear and concise commit messages.
    - Group related changes into single commits.

### Environment Setup (Reminder)
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    # Create a .env file with SECRET_KEY and DATABASE_URL
    # Example .env:
    # SECRET_KEY=mysecretkeythatisverylongandrandom
    # DATABASE_URL=sqlite:///instance/site.db  (For development)
    # FLASK_APP=run.py (Set this environment variable)
    flask db init  # Run once to initialize migrations (if not already done)
    flask db migrate -m "Descriptive migration message"
    flask db upgrade
    flask run
    ```

### 11. Running Tests
    - Tests are located in the `tests/` directory.
    - Ensure you have activated the virtual environment (`source venv/bin/activate`).
    - Set the `FLASK_APP=run.py` environment variable if not already set (it's used by the test base to create the app).
    - To run all tests, navigate to the project root directory and run:
      ```bash
      python -m unittest discover tests
      ```
    - To run a specific test file (e.g., `test_models.py`):
      ```bash
      python -m unittest tests.test_models
      ```
      Alternatively:
      ```bash
      python tests/test_models.py
      ```
    - To run a specific test class or method (e.g., `TestAuthRoutes.test_user_login_successful` in `test_auth.py`):
      ```bash
      python -m unittest tests.test_auth.TestAuthRoutes.test_user_login_successful
      ```
    - The test database is configured in `tests/base.py` to run in-memory (SQLite) and is created and torn down for each test class by default (or test method if setUp/tearDown are per method).

Make sure to create the blueprint directories and `__init__.py` files for them as you develop.
The `app/__init__.py` (`create_app` factory) is set up to look for these.
For example, for the `auth` blueprint, you'd have:
`app/auth/__init__.py`
`app/auth/routes.py`
`app/auth/forms.py`

Similarly for `main`, `tickets`, and `inventory`. The `models.py` and a general `forms.py` (if any) can live directly under `app/`.
The `app/decorators.py` file contains useful decorators like role checking.
