from app.core.enums import League
from app.services.rating import rating_service
from app.services.reputation import reputation_service


def test_league_thresholds() -> None:
    assert rating_service.league_for_score(0) is League.BRONZE
    assert rating_service.league_for_score(220) is League.SILVER
    assert rating_service.league_for_score(640) is League.GOLD
    assert rating_service.league_for_score(920) is League.PLATINUM
    assert rating_service.league_for_score(1500) is League.DIAMOND


def test_reputation_delta_rewards_success_and_penalizes_errors() -> None:
    computation = reputation_service.calculate_attempt_delta(
        scenario_key="email-phishing",
        success=True,
        score_percentage=93,
        previous_best_score=70,
        previous_completion_count=1,
        error_penalty_points=6,
    )

    assert computation.delta == 33
    assert computation.reason.value == "scenario_success"


def test_reputation_delta_caps_failure_penalty() -> None:
    computation = reputation_service.calculate_attempt_delta(
        scenario_key="unsafe-download",
        success=False,
        score_percentage=10,
        previous_best_score=40,
        previous_completion_count=0,
        error_penalty_points=50,
    )

    assert computation.delta == -40
