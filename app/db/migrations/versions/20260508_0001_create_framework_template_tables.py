"""create framework template tables

Revision ID: 20260508_0001
Revises:
Create Date: 2026-05-08 00:00:00.000000
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

revision = "20260508_0001"
down_revision = None
branch_labels = None
depends_on = None


def _case_sensitive_string(length: int) -> sa.String:
    return sa.String(length=length).with_variant(
        mysql.VARCHAR(length=length, collation="utf8mb4_bin"),
        "mysql",
    )


def upgrade() -> None:
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("actor_id", sa.String(length=128), nullable=False),
        sa.Column("actor_name", sa.String(length=128), nullable=False),
        sa.Column("action", sa.String(length=128), nullable=False),
        sa.Column("resource_type", sa.String(length=128), nullable=False),
        sa.Column("resource_id", sa.String(length=128), nullable=False),
        sa.Column("before_snapshot", sa.JSON(), nullable=True),
        sa.Column("after_snapshot", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_audit_logs_id"), "audit_logs", ["id"], unique=False)

    op.create_table(
        "example_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", _case_sensitive_string(64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_example_items_code"), "example_items", ["code"], unique=True)
    op.create_index(op.f("ix_example_items_id"), "example_items", ["id"], unique=False)

    op.create_table(
        "scheduled_jobs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", _case_sensitive_string(128), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("cron_expression", sa.String(length=128), nullable=False),
        sa.Column("timezone", sa.String(length=64), nullable=False),
        sa.Column("job_type", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("last_run_at", sa.DateTime(), nullable=True),
        sa.Column("next_run_at", sa.DateTime(), nullable=True),
        sa.Column("lock_ttl_seconds", sa.Integer(), nullable=False),
        sa.Column("max_runtime_seconds", sa.Integer(), nullable=False),
        sa.Column("misfire_policy", sa.String(length=32), nullable=False),
        sa.Column("concurrent_policy", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_scheduled_jobs_code"), "scheduled_jobs", ["code"], unique=True)
    op.create_index(op.f("ix_scheduled_jobs_id"), "scheduled_jobs", ["id"], unique=False)

    op.create_table(
        "scheduled_job_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("triggered_by", sa.String(length=128), nullable=False),
        sa.Column("trigger_info", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("result", sa.JSON(), nullable=True),
        sa.Column("worker_id", sa.String(length=128), nullable=True),
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("heartbeat_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["job_id"], ["scheduled_jobs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_scheduled_job_runs_id"), "scheduled_job_runs", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_scheduled_job_runs_id"), table_name="scheduled_job_runs")
    op.drop_table("scheduled_job_runs")
    op.drop_index(op.f("ix_scheduled_jobs_id"), table_name="scheduled_jobs")
    op.drop_index(op.f("ix_scheduled_jobs_code"), table_name="scheduled_jobs")
    op.drop_table("scheduled_jobs")
    op.drop_index(op.f("ix_example_items_id"), table_name="example_items")
    op.drop_index(op.f("ix_example_items_code"), table_name="example_items")
    op.drop_table("example_items")
    op.drop_index(op.f("ix_audit_logs_id"), table_name="audit_logs")
    op.drop_table("audit_logs")
