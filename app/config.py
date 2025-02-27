from fastapi.middleware.cors import CORSMiddleware


# Allowed CORS origins
ALLOWED_ORIGINS = [
    "*",  # Disables all CORS protection
]


CORS_SETTINGS = {
    "allow_origins": ALLOWED_ORIGINS,
    "allow_credentials": True,
    "allow_methods": ["*"],  # Allow all methods (GET, POST, etc...)
    "allow_headers": ["*"],  # Allow all headers
}
