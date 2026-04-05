"""init schema

Revision ID: 0001_init
Revises: 
Create Date: 2026-04-04
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "scenarios",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=1000)),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )

    op.create_table(
        "missions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "scenario_id",
            sa.Integer(),
            sa.ForeignKey("scenarios.id"),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False, server_default=sa.text("0")),
    )
    op.create_index("ix_missions_scenario_id", "missions", ["scenario_id"])

    op.create_table(
        "attacks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "mission_id",
            sa.Integer(),
            sa.ForeignKey("missions.id"),
            nullable=False,
        ),
        sa.Column("attack_type", sa.String(length=64), nullable=False),
        sa.Column("description", sa.String(length=1000)),
    )
    op.create_index("ix_attacks_mission_id", "attacks", ["mission_id"])

    op.create_table(
        "choices",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "attack_id",
            sa.Integer(),
            sa.ForeignKey("attacks.id"),
            nullable=False,
        ),
        sa.Column("label", sa.String(length=255), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("hint", sa.String(length=1000)),
        sa.Column("explanation", sa.String(length=1000)),
    )
    op.create_index("ix_choices_attack_id", "choices", ["attack_id"])

    op.create_table(
        "attempts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column(
            "attack_id",
            sa.Integer(),
            sa.ForeignKey("attacks.id"),
            nullable=False,
        ),
        sa.Column(
            "choice_id",
            sa.Integer(),
            sa.ForeignKey("choices.id"),
            nullable=False,
        ),
        sa.Column("is_correct", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index("ix_attempts_user_id", "attempts", ["user_id"])
    op.create_index("ix_attempts_attack_id", "attempts", ["attack_id"])
    op.create_index("ix_attempts_choice_id", "attempts", ["choice_id"])

    op.create_table(
        "progress",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column(
            "scenario_id",
            sa.Integer(),
            sa.ForeignKey("scenarios.id"),
            nullable=False,
        ),
        sa.Column("success_rate", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("mistakes", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index("ix_progress_user_id", "progress", ["user_id"])
    op.create_index("ix_progress_scenario_id", "progress", ["scenario_id"])

    op.create_table(
        "ratings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column("reputation", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("league", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index("ix_ratings_user_id", "ratings", ["user_id"])


def downgrade() -> None:
    op.drop_table("ratings")
    op.drop_table("progress")
    op.drop_table("attempts")
    op.drop_table("choices")
    op.drop_table("attacks")
    op.drop_table("missions")
    op.drop_table("scenarios")
    op.drop_table("users")
