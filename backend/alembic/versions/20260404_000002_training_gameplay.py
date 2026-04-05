"""add training gameplay tables

Revision ID: 20260404_000002
Revises: 20260403_000001
Create Date: 2026-04-04 03:25:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260404_000002"
down_revision = "20260403_000001"
branch_labels = None
depends_on = None


UUID_TYPE = sa.Uuid(as_uuid=True)
JSON_TYPE = sa.JSON()


def upgrade() -> None:
    op.create_table(
        "training_scenarios",
        sa.Column("id", sa.String(length=64), primary_key=True, nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("level", sa.String(length=32), nullable=False),
        sa.Column("setting", sa.String(length=64), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("threat_types", JSON_TYPE, nullable=False, server_default=sa.text("'[]'")),
        sa.Column("start_step_id", sa.String(length=64), nullable=False),
        sa.Column("passing_score", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_training_scenarios")),
    )

    op.create_table(
        "training_scenario_steps",
        sa.Column("id", sa.String(length=64), primary_key=True, nullable=False),
        sa.Column("scenario_id", sa.String(length=64), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("hint", sa.Text(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["scenario_id"],
            ["training_scenarios.id"],
            ondelete="CASCADE",
            name=op.f("fk_training_scenario_steps_scenario_id_training_scenarios"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_training_scenario_steps")),
    )
    op.create_index(op.f("ix_training_scenario_steps_scenario_id"), "training_scenario_steps", ["scenario_id"], unique=False)

    op.create_table(
        "training_step_options",
        sa.Column("id", sa.String(length=64), primary_key=True, nullable=False),
        sa.Column("step_id", sa.String(length=64), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("label", sa.String(length=255), nullable=False),
        sa.Column("outcome", sa.String(length=32)),
        sa.Column("is_safe", sa.Boolean(), nullable=False),
        sa.Column("feedback", sa.Text(), nullable=False),
        sa.Column("score_delta", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("next_step_id", sa.String(length=64)),
        sa.Column("ends_attempt", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("tags", JSON_TYPE, nullable=False, server_default=sa.text("'[]'")),
        sa.ForeignKeyConstraint(
            ["step_id"],
            ["training_scenario_steps.id"],
            ondelete="CASCADE",
            name=op.f("fk_training_step_options_step_id_training_scenario_steps"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_training_step_options")),
    )
    op.create_index(op.f("ix_training_step_options_step_id"), "training_step_options", ["step_id"], unique=False)

    op.create_table(
        "training_attempts",
        sa.Column("id", UUID_TYPE, primary_key=True, nullable=False),
        sa.Column("user_id", UUID_TYPE, nullable=False),
        sa.Column("scenario_id", sa.String(length=64), nullable=False),
        sa.Column("current_step_id", sa.String(length=64)),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("hints_used", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("progress_synced", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["scenario_id"], ["training_scenarios.id"], ondelete="CASCADE", name=op.f("fk_training_attempts_scenario_id_training_scenarios")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE", name=op.f("fk_training_attempts_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_training_attempts")),
    )
    op.create_index(op.f("ix_training_attempts_user_id"), "training_attempts", ["user_id"], unique=False)
    op.create_index(op.f("ix_training_attempts_scenario_id"), "training_attempts", ["scenario_id"], unique=False)
    op.create_index(op.f("ix_training_attempts_status"), "training_attempts", ["status"], unique=False)

    op.create_table(
        "training_attempt_answers",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("attempt_id", UUID_TYPE, nullable=False),
        sa.Column("step_id", sa.String(length=64), nullable=False),
        sa.Column("option_id", sa.String(length=64), nullable=False),
        sa.Column("is_safe", sa.Boolean(), nullable=False),
        sa.Column("score_delta", sa.Integer(), nullable=False),
        sa.Column("answered_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(
            ["attempt_id"],
            ["training_attempts.id"],
            ondelete="CASCADE",
            name=op.f("fk_training_attempt_answers_attempt_id_training_attempts"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_training_attempt_answers")),
    )
    op.create_index(op.f("ix_training_attempt_answers_attempt_id"), "training_attempt_answers", ["attempt_id"], unique=False)

    op.create_table(
        "training_event_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("attempt_id", UUID_TYPE, nullable=False),
        sa.Column("step_id", sa.String(length=64)),
        sa.Column("event_name", sa.String(length=64), nullable=False),
        sa.Column("payload", JSON_TYPE, nullable=False, server_default=sa.text("'{}'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(
            ["attempt_id"],
            ["training_attempts.id"],
            ondelete="CASCADE",
            name=op.f("fk_training_event_logs_attempt_id_training_attempts"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_training_event_logs")),
    )
    op.create_index(op.f("ix_training_event_logs_attempt_id"), "training_event_logs", ["attempt_id"], unique=False)
    op.create_index(op.f("ix_training_event_logs_step_id"), "training_event_logs", ["step_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_training_event_logs_step_id"), table_name="training_event_logs")
    op.drop_index(op.f("ix_training_event_logs_attempt_id"), table_name="training_event_logs")
    op.drop_table("training_event_logs")

    op.drop_index(op.f("ix_training_attempt_answers_attempt_id"), table_name="training_attempt_answers")
    op.drop_table("training_attempt_answers")

    op.drop_index(op.f("ix_training_attempts_status"), table_name="training_attempts")
    op.drop_index(op.f("ix_training_attempts_scenario_id"), table_name="training_attempts")
    op.drop_index(op.f("ix_training_attempts_user_id"), table_name="training_attempts")
    op.drop_table("training_attempts")

    op.drop_index(op.f("ix_training_step_options_step_id"), table_name="training_step_options")
    op.drop_table("training_step_options")

    op.drop_index(op.f("ix_training_scenario_steps_scenario_id"), table_name="training_scenario_steps")
    op.drop_table("training_scenario_steps")

    op.drop_table("training_scenarios")
