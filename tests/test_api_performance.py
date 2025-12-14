"""
Tests for Performance API Routes.

Tests bot performance charts, position performance, and sorting.
"""

import pytest
from fastapi.testclient import TestClient


class TestBotPerformanceAPI:
    """Tests for bot performance endpoints."""
    
    def test_get_bot_performance_1d(self, client):
        """Test getting 1-day bot performance."""
        # First get a bot ID
        bots_response = client.get("/api/bots/summary")
        if bots_response.status_code == 200:
            data = bots_response.json(); bots = data.get("bots", [])
            if bots:
                bot_id = bots[0]["id"]
                response = client.get(f"/api/performance/bot/{bot_id}?time_range=1D")
                assert response.status_code in [200, 404]
                data = response.json()
                
                assert "bot_id" in data
                assert "time_range" in data
                assert "data_points" in data
                assert "summary" in data
                assert data["time_range"] == "1D"
    
    def test_get_bot_performance_time_ranges(self, client):
        """Test different time ranges for bot performance."""
        time_ranges = ["1D", "1W", "1M", "3M", "6M", "1Y", "YTD", "ALL"]
        
        bots_response = client.get("/api/bots/summary")
        if bots_response.status_code == 200:
            data = bots_response.json(); bots = data.get("bots", [])
            if bots:
                bot_id = bots[0]["id"]
                
                for tr in time_ranges:
                    response = client.get(f"/api/performance/bot/{bot_id}?time_range={tr}")
                    assert response.status_code in [200, 404]
                    data = response.json()
                    assert data["time_range"] == tr
    
    def test_bot_performance_summary_fields(self, client):
        """Test that summary contains expected fields."""
        bots_response = client.get("/api/bots/summary")
        if bots_response.status_code == 200:
            data = bots_response.json(); bots = data.get("bots", [])
            if bots:
                bot_id = bots[0]["id"]
                response = client.get(f"/api/performance/bot/{bot_id}?time_range=1D")
                
                if response.status_code == 200:
                    data = response.json()
                    summary = data.get("summary", {})
                    
                    if summary:
                        assert "total_pnl" in summary
                        assert "total_pnl_pct" in summary
                        assert "max_drawdown_pct" in summary
                        assert "win_rate" in summary
    
    def test_bot_performance_data_points(self, client):
        """Test that data points are properly structured."""
        bots_response = client.get("/api/bots/summary")
        if bots_response.status_code == 200:
            data = bots_response.json(); bots = data.get("bots", [])
            if bots:
                bot_id = bots[0]["id"]
                response = client.get(f"/api/performance/bot/{bot_id}?time_range=1D")
                
                if response.status_code == 200:
                    data = response.json()
                    points = data.get("data_points", [])
                    
                    if points:
                        point = points[0]
                        assert "timestamp" in point
                        assert "value" in point
                        assert "pnl" in point
                        assert "pnl_pct" in point


class TestPositionPerformanceAPI:
    """Tests for position/symbol performance endpoints."""
    
    def test_get_position_performance(self, client):
        """Test getting position performance for a symbol."""
        response = client.get("/api/performance/position/AAPL?time_range=1D")
        assert response.status_code in [200, 404]
        
        data = response.json()
        assert "symbol" in data
        assert "time_range" in data
        assert "data_points" in data
        assert "summary" in data
        assert data["symbol"] == "AAPL"
    
    def test_position_performance_different_symbols(self, client):
        """Test performance for different symbols."""
        symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA"]
        
        for symbol in symbols:
            response = client.get(f"/api/performance/position/{symbol}?time_range=1D")
            assert response.status_code in [200, 404]
            data = response.json()
            assert data["symbol"] == symbol
    
    def test_position_performance_summary(self, client):
        """Test position performance summary fields."""
        response = client.get("/api/performance/position/AAPL?time_range=1W")
        assert response.status_code in [200, 404]
        
        data = response.json()
        summary = data.get("summary", {})
        
        if summary:
            assert "symbol" in summary
            assert "start_price" in summary
            assert "current_price" in summary
            assert "change" in summary
            assert "change_pct" in summary
            assert "high" in summary
            assert "low" in summary
    
    def test_position_data_points_have_price(self, client):
        """Test that position data points have price field."""
        response = client.get("/api/performance/position/AAPL?time_range=1D")
        assert response.status_code in [200, 404]
        
        data = response.json()
        points = data.get("data_points", [])
        
        if points:
            point = points[0]
            assert "timestamp" in point
            assert "price" in point
            assert "change" in point
            assert "change_pct" in point


class TestAllPositionsPerformanceAPI:
    """Tests for all positions performance with sorting."""
    
    def test_get_all_positions_default(self, client):
        """Test getting all positions with default sorting."""
        response = client.get("/api/performance/positions/all")
        assert response.status_code in [200, 404]
        
        data = response.json()
        assert "positions" in data
        assert "totals" in data
        assert "count" in data
        assert "sort_by" in data
        assert "sort_order" in data
    
    def test_sort_by_symbol(self, client):
        """Test sorting positions by symbol."""
        response = client.get("/api/performance/positions/all?sort_by=symbol&sort_order=asc")
        assert response.status_code in [200, 404]
        
        data = response.json()
        assert data["sort_by"] == "symbol"
        assert data["sort_order"] == "asc"
        
        positions = data.get("positions", [])
        if len(positions) > 1:
            # Check alphabetical order
            symbols = [p["symbol"] for p in positions]
            assert symbols == sorted(symbols)
    
    def test_sort_by_last_price(self, client):
        """Test sorting by last price."""
        response = client.get("/api/performance/positions/all?sort_by=last_price&sort_order=desc")
        assert response.status_code in [200, 404]
        
        data = response.json()
        assert data["sort_by"] == "last_price"
        
        positions = data.get("positions", [])
        if len(positions) > 1:
            prices = [p["last_price"] for p in positions]
            assert prices == sorted(prices, reverse=True)
    
    def test_sort_by_change_pct(self, client):
        """Test sorting by percent change."""
        response = client.get("/api/performance/positions/all?sort_by=change_pct&sort_order=desc")
        assert response.status_code in [200, 404]
        
        data = response.json()
        assert data["sort_by"] == "change_pct"
    
    def test_sort_by_equity(self, client):
        """Test sorting by equity value."""
        response = client.get("/api/performance/positions/all?sort_by=equity&sort_order=desc")
        assert response.status_code in [200, 404]
        
        data = response.json()
        positions = data.get("positions", [])
        if len(positions) > 1:
            equities = [p["equity"] for p in positions]
            assert equities == sorted(equities, reverse=True)
    
    def test_sort_by_today_return(self, client):
        """Test sorting by today's return."""
        response = client.get("/api/performance/positions/all?sort_by=today_return&sort_order=desc")
        assert response.status_code in [200, 404]
        
        data = response.json()
        assert data["sort_by"] == "today_return"
    
    def test_sort_by_total_return(self, client):
        """Test sorting by total return."""
        response = client.get("/api/performance/positions/all?sort_by=total_return&sort_order=desc")
        assert response.status_code in [200, 404]
        
        data = response.json()
        assert data["sort_by"] == "total_return"
    
    def test_sort_by_total_pct(self, client):
        """Test sorting by total percent change."""
        response = client.get("/api/performance/positions/all?sort_by=total_pct&sort_order=desc")
        assert response.status_code in [200, 404]
        
        data = response.json()
        assert data["sort_by"] == "total_pct"
    
    def test_positions_totals(self, client):
        """Test that totals are calculated."""
        response = client.get("/api/performance/positions/all")
        assert response.status_code in [200, 404]
        
        data = response.json()
        totals = data.get("totals", {})
        
        assert "equity" in totals
        assert "cost_basis" in totals
        assert "today_return" in totals
        assert "total_return" in totals
    
    def test_position_fields(self, client):
        """Test that positions have expected fields."""
        response = client.get("/api/performance/positions/all")
        assert response.status_code in [200, 404]
        
        data = response.json()
        positions = data.get("positions", [])
        
        if positions:
            pos = positions[0]
            assert "symbol" in pos
            assert "quantity" in pos
            assert "avg_cost" in pos
            assert "last_price" in pos
            assert "change_pct" in pos
            assert "equity" in pos
            assert "today_return" in pos
            assert "total_return" in pos
            assert "total_pct" in pos


class TestPerformanceSummaryAPI:
    """Tests for overall performance summary."""
    
    def test_get_performance_summary(self, client):
        """Test getting overall performance summary."""
        response = client.get("/api/performance/summary")
        assert response.status_code in [200, 404]
        
        data = response.json()
        assert "portfolio_value" in data
        assert "day_change" in data
        assert "day_change_pct" in data
        assert "total_return" in data
        assert "total_return_pct" in data
    
    def test_summary_has_best_worst(self, client):
        """Test summary includes best/worst performers."""
        response = client.get("/api/performance/summary")
        assert response.status_code in [200, 404]
        
        data = response.json()
        
        if "best_performer" in data:
            best = data["best_performer"]
            assert "symbol" in best
            assert "return_pct" in best
        
        if "worst_performer" in data:
            worst = data["worst_performer"]
            assert "symbol" in worst
            assert "return_pct" in worst

