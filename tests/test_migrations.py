from pathlib import Path

MIGRATIONS_DIR = Path("app/db/migrations/versions")


def test_template_migration_chain_has_single_initial_revision() -> None:
    migrations = sorted(MIGRATIONS_DIR.glob("*.py"))

    assert [path.name for path in migrations] == [
        "20260508_0001_create_framework_template_tables.py"
    ]


def test_initial_template_migration_creates_framework_tables_only() -> None:
    migration_text = MIGRATIONS_DIR.joinpath(
        "20260508_0001_create_framework_template_tables.py",
    ).read_text(encoding="utf-8")

    expected_tables = [
        '"audit_logs"',
        '"example_items"',
        '"scheduled_jobs"',
        '"scheduled_job_runs"',
    ]
    forbidden_tokens = [
        "list" + "ings",
        "prod" + "ucts",
        "chan" + "nels",
        "market" + "place",
    ]

    for table in expected_tables:
        assert table in migration_text
    for token in forbidden_tokens:
        assert token not in migration_text


def test_migrations_do_not_use_postgresql_only_types() -> None:
    forbidden_tokens = [
        "postgresql.JSONB",
        "postgresql.ARRAY",
        "postgresql.UUID",
        "from sqlalchemy.dialects import postgresql",
    ]
    migration_text = "\n".join(
        path.read_text(encoding="utf-8") for path in MIGRATIONS_DIR.glob("*.py")
    )

    for token in forbidden_tokens:
        assert token not in migration_text


def test_initial_migration_declares_mysql_binary_collation_for_business_keys() -> None:
    migration_text = MIGRATIONS_DIR.joinpath(
        "20260508_0001_create_framework_template_tables.py",
    ).read_text(encoding="utf-8")

    assert "utf8mb4_bin" in migration_text
    assert "_case_sensitive_string(64)" in migration_text
    assert "_case_sensitive_string(128)" in migration_text
