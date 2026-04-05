"""initial backend schema

Revision ID: 20260403_000001
Revises:
Create Date: 2026-04-03 22:55:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260403_000001"
down_revision = None
branch_labels = None
depends_on = None


USER_ROLE = sa.Enum("player", "admin", name="user_role", native_enum=False)
LEAGUE = sa.Enum(
    "bronze",
    "silver",
    "gold",
    "platinum",
    "diamond",
    name="league",
    native_enum=False,
)
REPUTATION_REASON = sa.Enum(
    "registration_bonus",
    "scenario_success",
    "scenario_failure",
    "manual_adjustment",
    name="reputation_reason",
    native_enum=False,
)
UUID_TYPE = sa.Uuid(as_uuid=True)
JSON_TYPE = sa.JSON()


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", UUID_TYPE, primary_key=True, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("username", sa.String(length=64), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255)),
        sa.Column("bio", sa.Text()),
        sa.Column("avatar_url", sa.String(length=512)),
        sa.Column("role", USER_ROLE, nullable=False, server_default=sa.text("'player'")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("reputation_score", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("league", LEAGUE, nullable=False, server_default=sa.text("'bronze'")),
        sa.Column("last_login_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
        sa.UniqueConstraint("username", name=op.f("uq_users_username")),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=False)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=False)
    op.create_index(op.f("ix_users_reputation_score"), "users", ["reputation_score"], unique=False)
    op.create_index(op.f("ix_users_league"), "users", ["league"], unique=False)

    op.create_table(
        "scenario_progress",
        sa.Column("id", UUID_TYPE, primary_key=True, nullable=False),
        sa.Column("user_id", UUID_TYPE, nullable=False),
        sa.Column("scenario_key", sa.String(length=128), nullable=False),
        sa.Column("scenario_title", sa.String(length=255), nullable=False),
        sa.Column("attempts_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("completions_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("successes_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("failures_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("total_score", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("average_score", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("best_score", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("success_rate", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("total_errors", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("last_score", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("last_result_success", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("last_attempt_at", sa.DateTime(timezone=True)),
        sa.Column("last_completed_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE", name=op.f("fk_scenario_progress_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_scenario_progress")),
        sa.UniqueConstraint("user_id", "scenario_key", name="uq_scenario_progress_user_scenario"),
    )
    op.create_index(op.f("ix_scenario_progress_user_id"), "scenario_progress", ["user_id"], unique=False)
    op.create_index(op.f("ix_scenario_progress_scenario_key"), "scenario_progress", ["scenario_key"], unique=False)

    op.create_table(
        "user_sessions",
        sa.Column("id", UUID_TYPE, primary_key=True, nullable=False),
        sa.Column("user_id", UUID_TYPE, nullable=False),
        sa.Column("refresh_token_jti", sa.String(length=64), nullable=False),
        sa.Column("ip_address", sa.String(length=64)),
        sa.Column("user_agent", sa.String(length=512)),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_activity_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE", name=op.f("fk_user_sessions_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user_sessions")),
        sa.UniqueConstraint("refresh_token_jti", name=op.f("uq_user_sessions_refresh_token_jti")),
    )
    op.create_index(op.f("ix_user_sessions_user_id"), "user_sessions", ["user_id"], unique=False)
    op.create_index(op.f("ix_user_sessions_refresh_token_jti"), "user_sessions", ["refresh_token_jti"], unique=False)
    op.create_index(op.f("ix_user_sessions_expires_at"), "user_sessions", ["expires_at"], unique=False)

    op.create_table(
        "scenario_attempts",
        sa.Column("id", UUID_TYPE, primary_key=True, nullable=False),
        sa.Column("user_id", UUID_TYPE, nullable=False),
        sa.Column("progress_id", UUID_TYPE, nullable=False),
        sa.Column("scenario_key", sa.String(length=128), nullable=False),
        sa.Column("scenario_title", sa.String(length=255), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("duration_seconds", sa.Integer()),
        sa.Column("success", sa.Boolean(), nullable=False),
        sa.Column("completed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("score_percentage", sa.Float(), nullable=False),
        sa.Column("errors_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("reputation_delta", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("submission_payload", JSON_TYPE, nullable=False, server_default=sa.text("'{}'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["progress_id"], ["scenario_progress.id"], ondelete="CASCADE", name=op.f("fk_scenario_attempts_progress_id_scenario_progress")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE", name=op.f("fk_scenario_attempts_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_scenario_attempts")),
    )
    op.create_index(op.f("ix_scenario_attempts_user_id"), "scenario_attempts", ["user_id"], unique=False)
    op.create_index(op.f("ix_scenario_attempts_progress_id"), "scenario_attempts", ["progress_id"], unique=False)
    op.create_index(op.f("ix_scenario_attempts_scenario_key"), "scenario_attempts", ["scenario_key"], unique=False)

    op.create_table(
        "scenario_attempt_errors",
        sa.Column("id", UUID_TYPE, primary_key=True, nullable=False),
        sa.Column("attempt_id", UUID_TYPE, nullable=False),
        sa.Column("error_code", sa.String(length=128), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(length=32), nullable=False, server_default=sa.text("'medium'")),
        sa.Column("penalty_points", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("context", JSON_TYPE, nullable=False, server_default=sa.text("'{}'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["attempt_id"], ["scenario_attempts.id"], ondelete="CASCADE", name=op.f("fk_scenario_attempt_errors_attempt_id_scenario_attempts")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_scenario_attempt_errors")),
    )
    op.create_index(op.f("ix_scenario_attempt_errors_attempt_id"), "scenario_attempt_errors", ["attempt_id"], unique=False)
    op.create_index(op.f("ix_scenario_attempt_errors_error_code"), "scenario_attempt_errors", ["error_code"], unique=False)

    op.create_table(
        "reputation_ledger",
        sa.Column("id", UUID_TYPE, primary_key=True, nullable=False),
        sa.Column("user_id", UUID_TYPE, nullable=False),
        sa.Column("attempt_id", UUID_TYPE),
        sa.Column("scenario_key", sa.String(length=128)),
        sa.Column("delta", sa.Integer(), nullable=False),
        sa.Column("balance_after", sa.Integer(), nullable=False),
        sa.Column("reason", REPUTATION_REASON, nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("context", JSON_TYPE, nullable=False, server_default=sa.text("'{}'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["attempt_id"], ["scenario_attempts.id"], ondelete="SET NULL", name=op.f("fk_reputation_ledger_attempt_id_scenario_attempts")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE", name=op.f("fk_reputation_ledger_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_reputation_ledger")),
    )
    op.create_index(op.f("ix_reputation_ledger_user_id"), "reputation_ledger", ["user_id"], unique=False)
    op.create_index(op.f("ix_reputation_ledger_attempt_id"), "reputation_ledger", ["attempt_id"], unique=False)
    op.create_index(op.f("ix_reputation_ledger_scenario_key"), "reputation_ledger", ["scenario_key"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_reputation_ledger_scenario_key"), table_name="reputation_ledger")
    op.drop_index(op.f("ix_reputation_ledger_attempt_id"), table_name="reputation_ledger")
    op.drop_index(op.f("ix_reputation_ledger_user_id"), table_name="reputation_ledger")
    op.drop_table("reputation_ledger")

    op.drop_index(op.f("ix_scenario_attempt_errors_error_code"), table_name="scenario_attempt_errors")
    op.drop_index(op.f("ix_scenario_attempt_errors_attempt_id"), table_name="scenario_attempt_errors")
    op.drop_table("scenario_attempt_errors")

    op.drop_index(op.f("ix_scenario_attempts_scenario_key"), table_name="scenario_attempts")
    op.drop_index(op.f("ix_scenario_attempts_progress_id"), table_name="scenario_attempts")
    op.drop_index(op.f("ix_scenario_attempts_user_id"), table_name="scenario_attempts")
    op.drop_table("scenario_attempts")

    op.drop_index(op.f("ix_user_sessions_expires_at"), table_name="user_sessions")
    op.drop_index(op.f("ix_user_sessions_refresh_token_jti"), table_name="user_sessions")
    op.drop_index(op.f("ix_user_sessions_user_id"), table_name="user_sessions")
    op.drop_table("user_sessions")

    op.drop_index(op.f("ix_scenario_progress_scenario_key"), table_name="scenario_progress")
    op.drop_index(op.f("ix_scenario_progress_user_id"), table_name="scenario_progress")
    op.drop_table("scenario_progress")

    op.drop_index(op.f("ix_users_league"), table_name="users")
    op.drop_index(op.f("ix_users_reputation_score"), table_name="users")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
