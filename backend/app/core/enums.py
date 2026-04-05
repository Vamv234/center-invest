from __future__ import annotations

from enum import Enum


class UserRole(str, Enum):
    PLAYER = "player"
    ADMIN = "admin"


class League(str, Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class ReputationReason(str, Enum):
    REGISTRATION_BONUS = "registration_bonus"
    SCENARIO_SUCCESS = "scenario_success"
    SCENARIO_FAILURE = "scenario_failure"
    MANUAL_ADJUSTMENT = "manual_adjustment"

