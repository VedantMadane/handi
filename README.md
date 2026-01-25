# Handi - Temple Management System

Handi is a modern, open-source Temple Management System designed to bring transparency and efficiency to temple operations. It features an immutable "Open Ledger" for donations, event management, and a flexible role-based user system.

## Features

*   **Immutable Open Ledger**:
    *   Cryptographically linked donation records (SHA-256 hash chain) ensure data integrity and transparency.
    *   Publicly viewable ledger.
    *   Multi-currency support.
*   **Event Management**:
    *   Schedule and display upcoming events (Poojas, Festivals).
    *   RSVP functionality for devotees.
*   **Internationalization (I18n)**:
    *   Full UI support for multiple languages.
    *   Supported Languages: **English**, **Spanish** (Español), **Hindi** (हिन्दी), **Marathi** (मराठी), and **Sanskrit** (संस्कृतम्).
*   **Role-Based Access**:
    *   Roles for Admins, Priests, Staff, and Devotees.
    *   Staff management and shift allocation.
*   **Live Darshan**: Placeholder for live streaming integration.

## Tech Stack

*   **Backend**: Python, [FastAPI](https://fastapi.tiangolo.com/)
*   **API**: [Strawberry GraphQL](https://strawberry.rocks/)
*   **Database**:
    *   SQLAlchemy (Async)
    *   PostgreSQL (Production) / SQLite (Development)
*   **Frontend**:
    *   Server-side rendering with **Jinja2**
    *   Dynamic interactions with **[HTMX](https://htmx.org/)**
    *   Styling with **Bootstrap 5**
*   **I18n**: [Babel](https://babel.pocoo.org/)

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/handi.git
    cd handi
    ```

2.  **Create a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

1.  **Start the server**:
    ```bash
    uvicorn app.main:app --reload
    ```

2.  **Access the application**:
    *   **Web UI**: [http://localhost:8000](http://localhost:8000)
    *   **GraphQL API**: [http://localhost:8000/graphql](http://localhost:8000/graphql)
    *   **OpenAPI Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

## Internationalization

To switch languages, use the dropdown in the navigation bar or append the `lang` query parameter:

*   English: `/?lang=en`
*   Spanish: `/?lang=es`
*   Hindi: `/?lang=hi`
*   Marathi: `/?lang=mr`
*   Sanskrit: `/?lang=sa`

### Adding a New Language

1.  Add the language code to `app/i18n.py` and `app/templates/base.html`.
2.  Initialize the translation file:
    ```bash
    pybabel init -i app/locales/messages.pot -d app/locales -l <code>
    ```
3.  Add translations to the generated `.po` file.
4.  Compile translations:
    ```bash
    pybabel compile -d app/locales
    ```

## Development

*   **Database**: By default, the app uses a local SQLite database (`handi.db`). To use PostgreSQL, set the `DATABASE_URL` environment variable.
*   **Seed Data**: You can seed the database with initial data using the `seed_db.py` script (if available) or by using the GraphQL API/UI.

## License

MIT License
