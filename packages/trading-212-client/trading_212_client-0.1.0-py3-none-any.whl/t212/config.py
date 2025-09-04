import os

T212_API_KEY: str = os.getenv("T212_API_KEY")

T212_ENVIRONMENT: str = os.getenv("T212_ENVIRONMENT")


if T212_API_KEY is None:
    raise EnvironmentError("Environment variable T212_API_KEY is not set")

if T212_ENVIRONMENT is None or T212_ENVIRONMENT not in {"live", "demo"}:
    raise EnvironmentError(
        "Environment variable T212_ENVIRONMENT must be one one {'live', 'demo'}"
    )
