# Sentry API Service

A FastAPI-based service for retrieving and analyzing Sentry.io issues. This service provides a clean REST API to interact with Sentry data, perfect for integrating error monitoring into your applications.

## Features

- Retrieve detailed Sentry issue information
- Parse and format stacktraces
- Support for both issue IDs and Sentry URLs
- Comprehensive error handling
- OpenAPI documentation
- Authentication management

## Installation

```bash
# Clone the repository
git clone https://github.com/your-username/sentry-api-service.git
cd sentry-api-service

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Set your Sentry authentication token:

```bash
export SENTRY_TOKEN="your-sentry-auth-token"
```

## Usage

### Starting the Server

```bash
uvicorn src.api:app --reload
```

The server will start at `http://localhost:8000`

### API Endpoints

#### 1. Configure Sentry
```http
POST /config
Content-Type: application/json

{
    "auth_token": "your-sentry-auth-token"
}
```

#### 2. Get Issue Details
```http
POST /sentry/issue
Content-Type: application/json

{
    "issue_id_or_url": "ISSUE_ID_OR_URL"
}
```

#### 3. Health Check
```http
GET /health
```

### API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
sentry-api-service/
├── src/
│   ├── __init__.py
│   ├── api.py         # FastAPI application
│   └── utils.py       # Utility functions
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   └── test_utils.py
├── .gitignore
├── README.md
├── requirements.txt
└── pyproject.toml
```

## Development

### Running Tests

```bash
pytest
```

### Code Style

```bash
# Format code
black src tests

# Lint code
ruff check src tests
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.