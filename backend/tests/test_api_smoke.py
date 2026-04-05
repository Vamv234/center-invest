from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.main import app


def _unique_user_payload() -> dict[str, str]:
    suffix = uuid4().hex[:10]
    return {
        "email": f"qa.{suffix}@example.com",
        "username": f"qa_{suffix}",
        "password": "StrongPass123",
        "full_name": "QA Smoke User",
    }


def _auth_headers(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


def test_root_serves_ui() -> None:
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert "Center-Invest Backend Console" in response.text

        api_info = client.get("/api-info")
        assert api_info.status_code == 200
        assert api_info.json()["message"] == "Center-Invest Cyber Simulator Backend"

        assert client.get("/favicon.ico").status_code == 204
        assert client.get("/apple-touch-icon.png").status_code == 204


def test_cors_allows_localhost_dev_ports() -> None:
    with TestClient(app) as client:
        response = client.options(
            "/api/v1/auth/register",
            headers={
                "Origin": "http://127.0.0.1:3002",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
        )
        assert response.status_code == 200, response.text
        assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:3002"


def test_full_auth_profile_progress_rating_and_websocket_flow() -> None:
    with TestClient(app) as client:
        payload = _unique_user_payload()

        register = client.post("/api/v1/auth/register", json=payload)
        assert register.status_code == 201, register.text
        register_data = register.json()
        access_token = register_data["access_token"]
        refresh_token = register_data["refresh_token"]
        headers = _auth_headers(access_token)

        assert register_data["user"]["email"] == payload["email"]
        assert register_data["user"]["role"] == "player"
        assert register_data["user"]["league"] == "bronze"
        assert register_data["user"]["reputation_score"] == 50
        assert register_data["session"]["is_current"] is True

        duplicate = client.post("/api/v1/auth/register", json=payload)
        assert duplicate.status_code == 409

        login = client.post(
            "/api/v1/auth/login",
            json={"login": payload["email"], "password": payload["password"]},
        )
        assert login.status_code == 200, login.text

        profile_me = client.get("/api/v1/profile/me", headers=headers)
        assert profile_me.status_code == 200, profile_me.text
        assert profile_me.json()["username"] == payload["username"]

        profile_update = client.patch(
            "/api/v1/profile/me",
            headers=headers,
            json={
                "full_name": "QA Smoke User Updated",
                "bio": "Smoke test bio",
                "avatar_url": "https://example.com/avatar.png",
            },
        )
        assert profile_update.status_code == 200, profile_update.text
        assert profile_update.json()["bio"] == "Smoke test bio"

        cabinet = client.get("/api/v1/profile/me/cabinet", headers=headers)
        assert cabinet.status_code == 200, cabinet.text
        cabinet_data = cabinet.json()
        assert cabinet_data["profile"]["full_name"] == "QA Smoke User Updated"
        assert cabinet_data["stats"]["total_scenarios"] == 0

        sessions = client.get("/api/v1/auth/sessions", headers=headers)
        assert sessions.status_code == 200, sessions.text
        assert len(sessions.json()["items"]) >= 2

        refreshed = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        assert refreshed.status_code == 200, refreshed.text
        refreshed_data = refreshed.json()
        access_token = refreshed_data["access_token"]
        refresh_token = refreshed_data["refresh_token"]
        headers = _auth_headers(access_token)
        assert refreshed_data["session"]["is_current"] is True

        with client.websocket_connect(f"/api/v1/ws/progress?token={access_token}") as websocket:
            snapshot = websocket.receive_json()
            assert snapshot["type"] == "progress.snapshot"
            websocket.send_text("ping")
            assert websocket.receive_json()["type"] == "pong"

            scenario_key = f"phishing-{uuid4().hex[:8]}"
            attempt = client.post(
                "/api/v1/progress/attempts",
                headers=headers,
                json={
                    "scenario_key": scenario_key,
                    "scenario_title": "Подозрительное письмо",
                    "success": True,
                    "completed": True,
                    "score_percentage": 92,
                    "submission_payload": {"selected_action": "report"},
                    "errors": [
                        {
                            "error_code": "slow_response",
                            "message": "User reacted with delay",
                            "severity": "low",
                            "penalty_points": 2,
                            "context": {"delay_seconds": 45},
                        }
                    ],
                },
            )
            assert attempt.status_code == 201, attempt.text
            attempt_data = attempt.json()
            assert attempt_data["attempt"]["scenario_key"] == scenario_key
            assert attempt_data["attempt"]["errors_count"] == 1
            assert attempt_data["progress"]["attempts_count"] == 1
            assert attempt_data["summary"]["total_scenarios"] == 1
            assert attempt_data["summary"]["completed_scenarios"] == 1

            ws_update = websocket.receive_json()
            assert ws_update["type"] == "progress.updated"
            assert ws_update["scenario_key"] == scenario_key

            progress_summary = client.get("/api/v1/progress/summary", headers=headers)
            assert progress_summary.status_code == 200, progress_summary.text
            assert progress_summary.json()["total_attempts"] == 1

            progress_list = client.get("/api/v1/progress/scenarios", headers=headers)
            assert progress_list.status_code == 200, progress_list.text
            assert progress_list.json()[0]["scenario_key"] == scenario_key

            progress_detail = client.get(
                f"/api/v1/progress/scenarios/{scenario_key}",
                headers=headers,
            )
            assert progress_detail.status_code == 200, progress_detail.text
            assert progress_detail.json()["recent_attempts"][0]["scenario_key"] == scenario_key

        rating_me = client.get("/api/v1/rating/me", headers=headers)
        assert rating_me.status_code == 200, rating_me.text
        assert rating_me.json()["reputation_score"] >= 50

        leaderboard = client.get("/api/v1/rating/leaderboard?limit=5&offset=0")
        assert leaderboard.status_code == 200, leaderboard.text
        assert leaderboard.json()["total"] >= 1

        logout = client.post("/api/v1/auth/logout", headers=headers)
        assert logout.status_code == 200, logout.text

        after_logout = client.get("/api/v1/profile/me", headers=headers)
        assert after_logout.status_code == 401


def test_refresh_rotation_and_session_revocation() -> None:
    with TestClient(app) as client:
        payload = _unique_user_payload()

        register = client.post("/api/v1/auth/register", json=payload)
        assert register.status_code == 201, register.text
        first_data = register.json()
        first_access_token = first_data["access_token"]
        first_refresh_token = first_data["refresh_token"]
        first_headers = _auth_headers(first_access_token)
        first_session_id = first_data["session"]["id"]

        refreshed = client.post("/api/v1/auth/refresh", json={"refresh_token": first_refresh_token})
        assert refreshed.status_code == 200, refreshed.text
        second_refresh_token = refreshed.json()["refresh_token"]

        old_refresh_reuse = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": first_refresh_token},
        )
        assert old_refresh_reuse.status_code == 401, old_refresh_reuse.text

        second_login = client.post(
            "/api/v1/auth/login",
            json={"login": payload["username"], "password": payload["password"]},
        )
        assert second_login.status_code == 200, second_login.text
        second_data = second_login.json()
        second_access_token = second_data["access_token"]
        second_headers = _auth_headers(second_access_token)
        second_session_id = second_data["session"]["id"]

        sessions = client.get("/api/v1/auth/sessions", headers=second_headers)
        assert sessions.status_code == 200, sessions.text
        assert {item["id"] for item in sessions.json()["items"]} >= {
            first_session_id,
            second_session_id,
        }

        revoke = client.delete(f"/api/v1/auth/sessions/{first_session_id}", headers=second_headers)
        assert revoke.status_code == 200, revoke.text

        old_session_access = client.get("/api/v1/profile/me", headers=first_headers)
        assert old_session_access.status_code == 401, old_session_access.text

        second_session_access = client.get("/api/v1/profile/me", headers=second_headers)
        assert second_session_access.status_code == 200, second_session_access.text

        revoked_session_refresh = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": second_refresh_token},
        )
        assert revoked_session_refresh.status_code == 401, revoked_session_refresh.text


def test_websocket_requires_token() -> None:
    with TestClient(app) as client:
        try:
            with client.websocket_connect("/api/v1/ws/progress") as websocket:
                websocket.receive_text()
        except WebSocketDisconnect as error:
            assert error.code == 4401
        else:
            raise AssertionError("WebSocket without token should not connect.")
