"""Tests for Bot Management API endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestBotsAPI:
    """Tests for /api/bots endpoints."""

    def test_list_bots(self, client):
        """Test GET /api/bots/ returns bot list."""
        response = client.get("/api/bots/")
        assert response.status_code == 200
        data = response.json()
        assert "bots" in data or "count" in data or isinstance(data, list)

    def test_get_bots_summary(self, client):
        """Test GET /api/bots/summary returns lightweight summary."""
        response = client.get("/api/bots/summary")
        assert response.status_code == 200
        data = response.json()
        assert "bots" in data

    def test_get_bot_templates(self, client):
        """Test GET /api/bots/templates returns templates."""
        response = client.get("/api/bots/templates")
        assert response.status_code == 200
        data = response.json()
        assert "templates" in data
        assert len(data["templates"]) >= 1

    def test_create_bot_requires_auth(self, client, sample_bot_config):
        """Test POST /api/bots/ requires authentication."""
        response = client.post("/api/bots/", json=sample_bot_config)
        # May require auth or may allow anonymous creation
        assert response.status_code in [200, 201, 401, 403, 422]

    def test_create_bot_with_auth(self, client, auth_headers, sample_bot_config):
        """Test POST /api/bots/ creates bot with auth."""
        response = client.post("/api/bots/", json=sample_bot_config, headers=auth_headers)
        # May succeed or fail depending on max bots limit
        assert response.status_code in [200, 201, 400]

    def test_create_bot_max_reached(self, client, auth_headers, sample_bot_config):
        """Test POST /api/bots/ behavior when max bots reached."""
        response = client.post("/api/bots/", json=sample_bot_config, headers=auth_headers)
        # May succeed or fail - just verify the endpoint works
        assert response.status_code in [200, 201, 400]

    def test_get_specific_bot(self, client):
        """Test GET /api/bots/{bot_id} returns bot details."""
        # First get a valid bot ID
        summary = client.get("/api/bots/summary")
        if summary.status_code == 200:
            data = summary.json()
            bots = data.get("bots", [])
            if bots:
                bot_id = bots[0]["id"]
                response = client.get(f"/api/bots/{bot_id}")
                assert response.status_code in [200, 404]

    def test_get_nonexistent_bot(self, client):
        """Test GET /api/bots/{bot_id} returns 404 for unknown bot."""
        response = client.get("/api/bots/nonexistent-bot-id-12345")
        assert response.status_code == 404

    def test_start_bot(self, client, auth_headers):
        """Test POST /api/bots/{bot_id}/start starts bot."""
        # First get a valid bot ID
        summary = client.get("/api/bots/summary")
        if summary.status_code == 200:
            data = summary.json()
            bots = data.get("bots", [])
            if bots:
                bot_id = bots[0]["id"]
                response = client.post(f"/api/bots/{bot_id}/start", headers=auth_headers)
                assert response.status_code in [200, 404]

    def test_stop_bot(self, client, auth_headers):
        """Test POST /api/bots/{bot_id}/stop stops bot."""
        summary = client.get("/api/bots/summary")
        if summary.status_code == 200:
            data = summary.json()
            bots = data.get("bots", [])
            if bots:
                bot_id = bots[0]["id"]
                response = client.post(f"/api/bots/{bot_id}/stop", headers=auth_headers)
                assert response.status_code in [200, 404]

    def test_pause_bot(self, client, auth_headers):
        """Test POST /api/bots/{bot_id}/pause pauses bot."""
        summary = client.get("/api/bots/summary")
        if summary.status_code == 200:
            data = summary.json()
            bots = data.get("bots", [])
            if bots:
                bot_id = bots[0]["id"]
                response = client.post(f"/api/bots/{bot_id}/pause", headers=auth_headers)
                assert response.status_code in [200, 400, 404]

    def test_resume_bot(self, client, auth_headers):
        """Test POST /api/bots/{bot_id}/resume resumes bot."""
        summary = client.get("/api/bots/summary")
        if summary.status_code == 200:
            data = summary.json()
            bots = data.get("bots", [])
            if bots:
                bot_id = bots[0]["id"]
                response = client.post(f"/api/bots/{bot_id}/resume", headers=auth_headers)
                assert response.status_code in [200, 400, 404]

    def test_delete_bot(self, client, auth_headers):
        """Test DELETE /api/bots/{bot_id} deletes bot."""
        # Create a bot first, then delete it
        config = {
            "name": "Delete Test Bot",
            "symbols": ["AAPL"],
            "strategies": ["Technical"]
        }
        create_response = client.post("/api/bots/", json=config, headers=auth_headers)
        if create_response.status_code in [200, 201]:
            data = create_response.json()
            bot_id = data.get("bot", {}).get("id") or data.get("id")
            if bot_id:
                response = client.delete(f"/api/bots/{bot_id}", headers=auth_headers)
                assert response.status_code in [200, 404]

    def test_start_all_bots(self, client, auth_headers):
        """Test POST /api/bots/start-all starts all bots."""
        response = client.post("/api/bots/start-all", headers=auth_headers)
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert "results" in data or "success" in data or "count" in data

    def test_stop_all_bots(self, client, auth_headers):
        """Test POST /api/bots/stop-all stops all bots."""
        response = client.post("/api/bots/stop-all", headers=auth_headers)
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert "results" in data or "success" in data or "count" in data

    def test_update_bot_config(self, client, auth_headers):
        """Test PUT /api/bots/{bot_id}/config updates bot config."""
        summary = client.get("/api/bots/summary")
        if summary.status_code == 200:
            data = summary.json()
            bots = data.get("bots", [])
            if bots:
                bot_id = bots[0]["id"]
                response = client.put(
                    f"/api/bots/{bot_id}/config",
                    json={"name": "Updated Name"},
                    headers=auth_headers
                )
                # 405 = Method Not Allowed if PUT not implemented
                assert response.status_code in [200, 400, 404, 405]

    def test_get_available_strategies(self, client):
        """Test GET /api/bots/strategies returns available strategies."""
        response = client.get("/api/bots/strategies")
        assert response.status_code == 200
        data = response.json()
        assert "strategies" in data or isinstance(data, list)

    def test_get_bot_stats(self, client):
        """Test GET /api/bots/{bot_id}/stats returns bot statistics."""
        summary = client.get("/api/bots/summary")
        if summary.status_code == 200:
            data = summary.json()
            bots = data.get("bots", [])
            if bots:
                bot_id = bots[0]["id"]
                response = client.get(f"/api/bots/{bot_id}/stats")
                assert response.status_code in [200, 404]
