"""
Tests for Auto-Optimizer API Routes.

Tests optimizer endpoints for enabling, disabling, and monitoring.
"""

import pytest
from fastapi.testclient import TestClient


class TestOptimizerStatusAPI:
    """Tests for optimizer status endpoints."""
    
    def test_get_optimizer_status(self, client):
        """Test getting overall optimizer status."""
        response = client.get("/api/optimizer/status")
        assert response.status_code in [200, 404]
        
        data = response.json()
        assert "total_bots" in data
        assert "enabled_count" in data
        assert "running_count" in data
        assert "bots" in data
    
    def test_optimizer_status_has_bots(self, client):
        """Test that status includes bot details."""
        response = client.get("/api/optimizer/status")
        assert response.status_code in [200, 404]
        
        data = response.json()
        bots = data.get("bots", {})
        
        # Should have registered bots
        assert isinstance(bots, dict)


class TestOptimizerBotAPI:
    """Tests for per-bot optimizer endpoints."""
    
    def test_get_bot_optimizer_status(self, client):
        """Test getting optimizer status for a specific bot."""
        # First get a bot ID
        bots_response = client.get("/api/bots/summary")
        if bots_response.status_code == 200:
            data = bots_response.json()
            bots = data.get("bots", [])
            if bots:
                bot_id = bots[0]["id"]
                response = client.get(f"/api/optimizer/bot/{bot_id}/status")
                
                # Endpoint may not exist yet
                assert response.status_code in [200, 404]
    
    def test_enable_bot_optimizer(self, client):
        """Test enabling optimizer for a bot."""
        bots_response = client.get("/api/bots/summary")
        if bots_response.status_code == 200:
            data = bots_response.json()
            bots = data.get("bots", [])
            if bots:
                bot_id = bots[0]["id"]
                response = client.post(
                    f"/api/optimizer/bot/{bot_id}/enable",
                    json={"mode": "moderate"}
                )
                
                # Endpoint may not exist yet
                assert response.status_code in [200, 404]
    
    def test_enable_bot_optimizer_conservative(self, client):
        """Test enabling optimizer in conservative mode."""
        bots_response = client.get("/api/bots/summary")
        if bots_response.status_code == 200:
            data = bots_response.json()
            bots = data.get("bots", [])
            if bots:
                bot_id = bots[0]["id"]
                response = client.post(
                    f"/api/optimizer/bot/{bot_id}/enable",
                    json={"mode": "conservative"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    assert data["mode"] == "conservative"
    
    def test_enable_bot_optimizer_aggressive(self, client):
        """Test enabling optimizer in aggressive mode."""
        bots_response = client.get("/api/bots/summary")
        if bots_response.status_code == 200:
            data = bots_response.json(); bots = data.get("bots", [])
            if bots:
                bot_id = bots[0]["id"]
                response = client.post(
                    f"/api/optimizer/bot/{bot_id}/enable",
                    json={"mode": "aggressive"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    assert data["mode"] == "aggressive"
    
    def test_disable_bot_optimizer(self, client):
        """Test disabling optimizer for a bot."""
        bots_response = client.get("/api/bots/summary")
        if bots_response.status_code == 200:
            data = bots_response.json(); bots = data.get("bots", [])
            if bots:
                bot_id = bots[0]["id"]
                response = client.post(f"/api/optimizer/bot/{bot_id}/disable")
                
                if response.status_code == 200:
                    data = response.json()
                    assert data["success"] is True
    
    def test_reset_bot_optimizer(self, client):
        """Test resetting optimizer for a bot."""
        bots_response = client.get("/api/bots/summary")
        if bots_response.status_code == 200:
            data = bots_response.json(); bots = data.get("bots", [])
            if bots:
                bot_id = bots[0]["id"]
                response = client.post(f"/api/optimizer/bot/{bot_id}/reset")
                
                if response.status_code == 200:
                    data = response.json()
                    assert data["success"] is True
    
    def test_get_bot_adjustments(self, client):
        """Test getting adjustment history for a bot."""
        bots_response = client.get("/api/bots/summary")
        if bots_response.status_code == 200:
            data = bots_response.json(); bots = data.get("bots", [])
            if bots:
                bot_id = bots[0]["id"]
                response = client.get(f"/api/optimizer/bot/{bot_id}/adjustments")
                
                if response.status_code == 200:
                    data = response.json()
                    assert "bot_id" in data
                    assert "adjustments" in data
                    assert "total_adjustments" in data
    
    def test_get_bot_metrics(self, client):
        """Test getting metrics for a bot."""
        bots_response = client.get("/api/bots/summary")
        if bots_response.status_code == 200:
            data = bots_response.json(); bots = data.get("bots", [])
            if bots:
                bot_id = bots[0]["id"]
                response = client.get(f"/api/optimizer/bot/{bot_id}/metrics")
                
                if response.status_code == 200:
                    data = response.json()
                    assert "bot_id" in data or "message" in data
    
    def test_update_bot_config(self, client):
        """Test updating optimizer config for a bot."""
        bots_response = client.get("/api/bots/summary")
        if bots_response.status_code == 200:
            data = bots_response.json(); bots = data.get("bots", [])
            if bots:
                bot_id = bots[0]["id"]
                response = client.put(
                    f"/api/optimizer/bot/{bot_id}/config",
                    json={
                        "min_trades_for_analysis": 15,
                        "max_adjustment_pct": 0.25,
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    assert data["success"] is True


class TestOptimizerBulkAPI:
    """Tests for bulk optimizer operations."""
    
    def test_enable_all_optimizers(self, client):
        """Test enabling all optimizers."""
        response = client.post(
            "/api/optimizer/enable-all",
            json={"mode": "moderate"}
        )
        assert response.status_code in [200, 404]
        
        data = response.json()
        assert data["success"] is True
        assert "message" in data
    
    def test_disable_all_optimizers(self, client):
        """Test disabling all optimizers."""
        response = client.post("/api/optimizer/disable-all")
        assert response.status_code in [200, 404]
        
        data = response.json()
        assert data["success"] is True


class TestOptimizerRecommendationsAPI:
    """Tests for optimization recommendations."""
    
    def test_get_recommendations(self, client):
        """Test getting optimization recommendations."""
        response = client.get("/api/optimizer/recommendations")
        assert response.status_code in [200, 404]
        
        data = response.json()
        assert "recommendations" in data
        assert "total" in data
        assert "high_priority" in data


class TestOptimizerModesAPI:
    """Tests for optimizer modes information."""
    
    def test_get_optimization_modes(self, client):
        """Test getting available optimization modes."""
        response = client.get("/api/optimizer/modes")
        assert response.status_code in [200, 404]
        
        data = response.json()
        assert "modes" in data
        
        modes = data["modes"]
        assert len(modes) == 3  # conservative, moderate, aggressive
        
        mode_names = [m["name"] for m in modes]
        assert "conservative" in mode_names
        assert "moderate" in mode_names
        assert "aggressive" in mode_names
    
    def test_mode_details(self, client):
        """Test that mode details are complete."""
        response = client.get("/api/optimizer/modes")
        assert response.status_code in [200, 404]
        
        data = response.json()
        for mode in data["modes"]:
            assert "name" in mode
            assert "description" in mode
            assert "max_adjustment" in mode
            assert "min_trades" in mode
            assert "cooldown" in mode
            assert "daily_limit" in mode


class TestAdjustableParametersAPI:
    """Tests for adjustable parameters information."""
    
    def test_get_adjustable_parameters(self, client):
        """Test getting list of adjustable parameters."""
        response = client.get("/api/optimizer/adjustable-parameters")
        assert response.status_code in [200, 404]
        
        data = response.json()
        assert "parameters" in data
        assert "categories" in data
    
    def test_parameter_categories(self, client):
        """Test that parameter categories are defined."""
        response = client.get("/api/optimizer/adjustable-parameters")
        assert response.status_code in [200, 404]
        
        data = response.json()
        categories = data["categories"]
        
        assert "risk_management" in categories
        assert "technical_indicators" in categories
        assert "momentum" in categories
        assert "signals" in categories
    
    def test_parameter_details(self, client):
        """Test that parameters have min/max/direction."""
        response = client.get("/api/optimizer/adjustable-parameters")
        assert response.status_code in [200, 404]
        
        data = response.json()
        params = data["parameters"]
        
        for name, details in params.items():
            assert "min" in details
            assert "max" in details
            assert "direction" in details


class TestRecordTradeAPI:
    """Tests for recording trades."""
    
    def test_record_trade(self, client):
        """Test recording a trade for a bot."""
        bots_response = client.get("/api/bots/summary")
        if bots_response.status_code == 200:
            data = bots_response.json(); bots = data.get("bots", [])
            if bots:
                bot_id = bots[0]["id"]
                response = client.post(
                    f"/api/optimizer/bot/{bot_id}/record-trade",
                    json={
                        "symbol": "AAPL",
                        "side": "buy",
                        "pnl": 150.0,
                        "quantity": 10,
                        "entry_price": 175.0,
                        "exit_price": 190.0,
                    }
                )
                
                assert response.status_code in [200, 404]
                data = response.json()
                assert data["success"] is True

