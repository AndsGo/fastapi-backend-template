from app.core.config import Settings


def test_settings_load_database_url_from_environment(monkeypatch) -> None:
    database_url = "postgresql+psycopg://user:password@db.example.com:5432/app"
    monkeypatch.setenv("DATABASE_URL", database_url)

    settings = Settings()

    assert str(settings.database_url) == database_url
    assert settings.api_v1_prefix == "/api/v1"


def test_mysql_database_url_loads_from_environment(monkeypatch) -> None:
    database_url = "mysql+pymysql://app:secret@localhost:3306/app?charset=utf8mb4"
    monkeypatch.setenv("DATABASE_URL", database_url)

    settings = Settings()

    assert str(settings.database_url).startswith("mysql+pymysql://app:secret@localhost")
    assert "charset=utf8mb4" in str(settings.database_url)


def test_settings_load_redis_configuration_from_environment(monkeypatch) -> None:
    monkeypatch.setenv("REDIS_URL", "redis://redis.example.com:6379/3")
    monkeypatch.setenv("REDIS_PREFIX", "pls")
    monkeypatch.setenv("REDIS_DEFAULT_TTL_SECONDS", "900")

    settings = Settings()

    assert settings.redis_url == "redis://redis.example.com:6379/3"
    assert settings.redis_prefix == "pls"
    assert settings.redis_default_ttl_seconds == 900


def test_logging_settings_defaults() -> None:
    settings = Settings()

    assert settings.log_level == "INFO"
    assert settings.log_format == "json"
    assert settings.service_name == "fastapi-backend-template"
    assert settings.environment == "dev"
    assert settings.log_output == "stdout"
    assert settings.log_file_path == "logs/app.log"
    assert settings.log_file_max_bytes == 104_857_600
    assert settings.log_file_backup_count == 10


def test_logging_settings_load_from_environment(monkeypatch) -> None:
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("LOG_FORMAT", "text")
    monkeypatch.setenv("SERVICE_NAME", "backend-worker")
    monkeypatch.setenv("ENVIRONMENT", "staging")
    monkeypatch.setenv("LOG_OUTPUT", "both")
    monkeypatch.setenv("LOG_FILE_PATH", "logs/worker.log")
    monkeypatch.setenv("LOG_FILE_MAX_BYTES", "1024")
    monkeypatch.setenv("LOG_FILE_BACKUP_COUNT", "3")

    settings = Settings()

    assert settings.log_level == "DEBUG"
    assert settings.log_format == "text"
    assert settings.service_name == "backend-worker"
    assert settings.environment == "staging"
    assert settings.log_output == "both"
    assert settings.log_file_path == "logs/worker.log"
    assert settings.log_file_max_bytes == 1024
    assert settings.log_file_backup_count == 3
