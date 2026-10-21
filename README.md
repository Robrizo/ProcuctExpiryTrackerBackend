# Product Expiry Tracker API (PETBackend)

A FastAPI-based backend service for tracking household products and sending automated expiry reminders via email. The API helps users manage their inventory of products with expiry dates, tracks product status, and notifies them when items are expiring soon (within 7 days).

## Features

- **User Authentication**: JWT-based authentication with access and refresh tokens
- **Product Management**: Full CRUD operations for products with purchase/expiry dates, categories, quantities, and notes
- **Automatic Expiry Tracking**: Products are categorized as Fresh, Expiring Soon (≤7 days), or Expired
- **Email Reminders**: Automated email notifications sent for products expiring within 7 days
- **Scheduled Jobs**: APScheduler runs expiry checks every 12 hours and on startup
- **Manual Triggers**: API endpoints to manually trigger expiry checks and view notification logs
- **CORS Support**: Configurable CORS origins for frontend integration

## Tech Stack

- **Framework**: [FastAPI](https://fastapi.dev/) 0.142.0
- **Database**: PostgreSQL (via SQLAlchemy ORM)
- **Authentication**: JWT tokens using python-jose, password hashing with passlib/bcrypt
- **Task Scheduling**: APScheduler
- **Email**: SMTP (aiosmtplib)
- **Validation**: Pydantic v2

## Project Structure

```
PETBackend/
├── app/
│   ├── auth/           # JWT authentication logic
│   ├── config/         # Database configuration
│   ├── models/         # SQLAlchemy models (User, Product)
│   ├── routers/        # API route handlers (auth, products, user)
│   ├── schemas/        # Pydantic schemas for request/response validation
│   ├── services/       # Email service
│   ├── tasks/          # Background tasks (expiry checker)
│   └── main.py         # FastAPI app entry point
├── requirements.txt
├── .env.example
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL database
- SMTP server credentials (for email reminders)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd PETBackend
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On Linux/macOS
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your configuration:
   ```env
   DATABASE_PASSWORD=your_database_password
   DATABASE_USER=your_database_username
   DATABASE_HOST=your_database_host
   DATABASE_PORT=your_database_port
   DATABASE_NAME=your_database_name
   
   SECRET_KEY=your_secret_key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_MINUTES=10080
   
   CORS_ORIGINS=http://localhost:3000,http://localhost:5173
   
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your_smtp_username
   SMTP_PASSWORD=your_smtp_password
   SMTP_FROM=your_smtp_from_address
   SMTP_ENABLE=true
   ```

5. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```
   
   The API will be available at `http://localhost:8000`

## API Documentation

Once running, access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Authentication (`/api/auth`)
| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/register` | Register a new user |
| POST | `/login` | Login and receive access/refresh tokens |
| POST | `/refresh` | Refresh access token using refresh token |

### Products (`/api/products`)
All product endpoints require authentication (Bearer token).

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `` | Get all products for authenticated user |
| GET | `/{product_id}` | Get a specific product |
| POST | `` | Create a new product |
| PUT | `/{product_id}` | Update a product (resets reminder if expiry date updated) |
| DELETE | `/{product_id}` | Delete a product |

### Tasks & Notifications
| Method | Endpoint | Auth Required | Description |
| --- | --- | --- | --- |
| GET | `/health` | No | Health check endpoint |
| POST | `/api/tasks/check-expiry` | No | Manually trigger expiry reminder check |
| GET | `/api/notifications/logs` | Yes | Get email reminder logs for authenticated user |

## How It Works

### Product Status
Products are automatically assigned a status based on days until expiry:
- **Fresh**: More than 7 days until expiry
- **Expiring Soon**: 7 days or less until expiry (and not expired)
- **Expired**: Expiry date has passed

### Automated Reminders
- On startup, the scheduler runs an immediate expiry check
- Then runs every 12 hours via APScheduler
- Only products expiring within the next 7 days (and not yet expired) with `reminder_sent=False` receive emails
- After successful email delivery, `reminder_sent` is set to `True` to prevent duplicate reminders
- Updating a product's `expiry_date` to a future date resets `reminder_sent` to `False`

## Models

### User
- UUID primary key
- Username, first/last name, email (unique)
- Password hash
- Role (default: "user")
- Timestamps
- One-to-many relationship with Products (cascade delete)

### Product
- UUID primary key
- Belongs to User (foreign key, cascade delete)
- Name, category, quantity
- Purchase date, expiry date
- Notes (optional)
- `reminder_sent` flag
- Timestamps
- Auto-calculated status and days until expiry in API responses

## Development

### Database Migrations
Tables are auto-created on startup via `Base.metadata.create_all(bind=engine)`. For production, consider using Alembic for migrations.


