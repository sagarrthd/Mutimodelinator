from decouple import config

# Security
SECRET_KEY = config('SECRET_KEY', default='unsafe-secret-key-change-in-production')
ALGORITHM = config('ALGORITHM', default='HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = config('ACCESS_TOKEN_EXPIRE_MINUTES', default=30, cast=int)

# Database
DATABASE_URL = config('DATABASE_URL', default='sqlite:///./app.db')

# OAuth2 Providers
GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID', default='')
GOOGLE_CLIENT_SECRET = config('GOOGLE_CLIENT_SECRET', default='')
GITHUB_CLIENT_ID = config('GITHUB_CLIENT_ID', default='')
GITHUB_CLIENT_SECRET = config('GITHUB_CLIENT_SECRET', default='')

# Redis (for Rate Limiting and Caching)
REDIS_URL = config('REDIS_URL', default='redis://localhost:6379/0')

# Application
API_V1_STR = "/api/v1"
PROJECT_NAME = "Multi-Modal AI Generator API"
