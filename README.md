# n8n Bot Hub Backend

A robust backend API for managing bots, appointments, and contacts, designed to integrate with n8n automations.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL
- Firebase Project (for Authentication)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd n8n_bot_hub_backend
   ```

2. **Set up Virtual Environment**
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   Copy `.env.example` to `.env` and fill in your details:
   ```bash
   cp .env.example .env
   ```
   *See [Configuration](#configuration) for details.*

5. **Run the Server**
   ```bash
   uvicorn app.main:app --reload
   ```
   The API will be available at `http://localhost:8000`.

## ✨ Features

- **Bot Management**: Create and manage chat instances.
- **Appointment Scheduling**: Smart booking system with business hours and blocked periods.
- **Contact Management**: Store and retrieve contact details.
- **Authentication**: Secure access using Firebase Authentication.
- **Integration Ready**: Designed to work seamlessly with n8n workflows.

## 🛠 Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database**: PostgreSQL with [SQLAlchemy](https://www.sqlalchemy.org/) & [Alembic](https://alembic.sqlalchemy.org/)
- **Authentication**: Firebase Admin SDK
- **Validation**: Pydantic
- **Testing**: Pytest

## ⚙️ Configuration

The application is configured using environment variables in the `.env` file.

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `FIREBASE_PROJECT_ID` | Firebase project ID |
| `FIREBASE_API_KEY` | Firebase Web API Key |
| `FIREBASE_AUTH_DOMAIN` | Firebase Auth Domain |
| `N8N_WEBHOOK_URL` | URL for n8n webhooks |
| `API_V1_PREFIX` | API version prefix (default: `/api/v1`) |
| `PROJECT_NAME` | Name of the project |
| `DEBUG` | Enable debug mode (True/False) |

## 📚 API Documentation

Interactive API documentation (Swagger UI) is available at:
`http://localhost:8000/docs`

For a high-level overview of resources, see [docs/api.md](docs/api.md).
