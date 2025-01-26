import os


def get_db_uri() -> str:
    return "sqlite:///order.db"


def get_api_url() -> str:
    host = os.environ.get("API_HOST", "localhost")
    port = 5005 if host == "localhost" else 80
    return f"http://{host}:{port}"


def get_redis_host_and_port() -> tuple[str, int]:
    host = os.environ.get("REDIS_HOST", "localhost")
    port = 6379 if host == "localhost" else 80
    return host, port


def get_email_host_and_port() -> dict[str, str | int]:
    host = os.environ.get("EMAIL_HOST", "localhost")
    port = 25 if host == "localhost" else 587
    return {"host": host, "port": port}