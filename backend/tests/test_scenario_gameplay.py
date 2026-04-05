from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.main import app


def _unique_user_payload() -> dict[str, str]:
    suffix = uuid4().hex[:10]
    return {
        "email": f"scenario.{suffix}@example.com",
        "username": f"scenario_{suffix}",
        "password": "StrongPass123",
        "full_name": "Scenario QA User",
    }


def _register(client: TestClient) -> tuple[str, dict[str, str]]:
    payload = _unique_user_payload()
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201, response.text
    access_token = response.json()["access_token"]
    return access_token, {"Authorization": f"Bearer {access_token}"}


def test_seeded_scenarios_gameplay_and_progress_sync() -> None:
    with TestClient(app) as client:
        access_token, headers = _register(client)

        scenarios = client.get("/api/v1/scenarios")
        assert scenarios.status_code == 200, scenarios.text
        scenario_ids = {item["id"] for item in scenarios.json()}
        assert {"office-phishing", "home-passwords", "public-wifi"} <= scenario_ids

        start = client.post("/api/v1/scenarios/office-phishing/attempts", headers=headers)
        assert start.status_code == 201, start.text
        start_data = start.json()
        attempt_id = start_data["attempt_id"]
        assert start_data["status"] == "in_progress"
        assert start_data["current_step"]["id"] == "office-mail"

        state = client.get(f"/api/v1/attempts/{attempt_id}", headers=headers)
        assert state.status_code == 200, state.text
        assert state.json()["attempt_id"] == attempt_id

        invalid_answer = client.post(
            f"/api/v1/attempts/{attempt_id}/answers",
            headers=headers,
            json={"option_id": "missing-option"},
        )
        assert invalid_answer.status_code == 400, invalid_answer.text

        hint = client.post(f"/api/v1/attempts/{attempt_id}/hint", headers=headers)
        assert hint.status_code == 200, hint.text
        hint_data = hint.json()
        assert hint_data["hint_penalty"] == 2
        assert hint_data["hints_used"] == 1
        assert hint_data["score"] == -2

        repeated_hint = client.post(f"/api/v1/attempts/{attempt_id}/hint", headers=headers)
        assert repeated_hint.status_code == 409, repeated_hint.text

        with client.websocket_connect(f"/api/v1/ws/attempts/{attempt_id}?token={access_token}") as websocket:
            websocket.send_text("ping")
            assert websocket.receive_json()["type"] == "pong"

            first_answer = client.post(
                f"/api/v1/attempts/{attempt_id}/answers",
                headers=headers,
                json={"option_id": "verify-sender"},
            )
            assert first_answer.status_code == 200, first_answer.text
            first_answer_data = first_answer.json()
            assert first_answer_data["status"] == "in_progress"
            assert first_answer_data["score"] == 8
            assert first_answer_data["current_step"]["id"] == "office-link"

            first_event = websocket.receive_json()
            assert first_event["event_name"] == "scenario.answer_submitted"
            assert first_event["payload"]["option_id"] == "verify-sender"

            second_answer = client.post(
                f"/api/v1/attempts/{attempt_id}/answers",
                headers=headers,
                json={"option_id": "inspect-domain"},
            )
            assert second_answer.status_code == 200, second_answer.text
            second_answer_data = second_answer.json()
            assert second_answer_data["status"] == "completed"
            assert second_answer_data["score"] == 23
            assert second_answer_data["current_step"] is None

            second_event = websocket.receive_json()
            finished_event = websocket.receive_json()
            assert second_event["event_name"] == "scenario.answer_submitted"
            assert finished_event["event_name"] == "scenario.finished"
            assert finished_event["payload"]["success"] is True
            assert finished_event["payload"]["score_percentage"] == 92.0

        events = client.get(f"/api/v1/attempts/{attempt_id}/events", headers=headers)
        assert events.status_code == 200, events.text
        event_names = [event["event_name"] for event in events.json()]
        assert event_names == [
            "scenario.started",
            "scenario.hint_used",
            "scenario.answer_submitted",
            "scenario.answer_submitted",
            "scenario.finished",
        ]

        finished_hint = client.post(f"/api/v1/attempts/{attempt_id}/hint", headers=headers)
        assert finished_hint.status_code == 409, finished_hint.text

        summary = client.get("/api/v1/progress/summary", headers=headers)
        assert summary.status_code == 200, summary.text
        assert summary.json()["total_scenarios"] == 1
        assert summary.json()["completed_scenarios"] == 1
        assert summary.json()["total_attempts"] == 1
        assert summary.json()["average_score"] == 92.0
        assert summary.json()["total_errors"] == 0

        detail = client.get("/api/v1/progress/scenarios/office-phishing", headers=headers)
        assert detail.status_code == 200, detail.text
        assert detail.json()["progress"]["best_score"] == 92.0
        assert detail.json()["recent_attempts"][0]["score_percentage"] == 92.0

        rating = client.get("/api/v1/rating/me", headers=headers)
        assert rating.status_code == 200, rating.text
        assert rating.json()["reputation_score"] > 50


def test_attempt_access_is_isolated_between_users() -> None:
    with TestClient(app) as client:
        first_token, first_headers = _register(client)
        _, second_headers = _register(client)

        start = client.post("/api/v1/scenarios/public-wifi/attempts", headers=first_headers)
        assert start.status_code == 201, start.text
        attempt_id = start.json()["attempt_id"]

        foreign_attempt = client.get(f"/api/v1/attempts/{attempt_id}", headers=second_headers)
        assert foreign_attempt.status_code == 404, foreign_attempt.text

        foreign_events = client.get(f"/api/v1/attempts/{attempt_id}/events", headers=second_headers)
        assert foreign_events.status_code == 404, foreign_events.text

        try:
            with client.websocket_connect(f"/api/v1/ws/attempts/{attempt_id}?token={first_token[:-8]}invalid") as websocket:
                websocket.receive_text()
        except WebSocketDisconnect as error:
            assert error.code == 4401
        else:
            raise AssertionError("Unauthorized attempt websocket should not connect.")
