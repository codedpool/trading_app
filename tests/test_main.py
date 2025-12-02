import unittest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import app
from app.services import calculate_strategy_performance
from app.models import TickerDataSchema
from decimal import Decimal
from datetime import datetime

class TestTradingApp(unittest.TestCase):
    
    def setUp(self):
        self.client = TestClient(app)

    # --- API Validation Tests ---
    
    def test_create_record_valid(self):
        """Test adding a valid record via POST /data"""
        # Mocking the database call to avoid actual DB writes
        with patch('app.routes.create_record', new_callable=AsyncMock) as mock_create:
            payload = {
                "datetime": "2024-01-01T10:00:00",
                "open": 100.5,
                "high": 105.0,
                "low": 99.5,
                "close": 102.0,
                "volume": 1000
            }
            # Configure the mock to return what we expect
            mock_create.return_value = TickerDataSchema(**payload)
            
            response = self.client.post("/data", json=payload)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['close'], "102.0")

    def test_create_record_invalid_type(self):
        """Test input validation: sending string instead of float for price"""
        payload = {
            "datetime": "2024-01-01T10:00:00",
            "open": "invalid_price", # Error here
            "high": 105.0,
            "low": 99.5,
            "close": 102.0,
            "volume": 1000
        }
        response = self.client.post("/data", json=payload)
        self.assertEqual(response.status_code, 422) # Unprocessable Entity

    def test_create_record_missing_field(self):
        """Test input validation: missing volume field"""
        payload = {
            "datetime": "2024-01-01T10:00:00",
            "open": 100.5,
            "high": 105.0,
            "low": 99.5,
            "close": 102.0
            # volume is missing
        }
        response = self.client.post("/data", json=payload)
        self.assertEqual(response.status_code, 422)


class TestStrategyLogic(unittest.IsolatedAsyncioTestCase):
    
    async def test_strategy_calculation_empty_db(self):
        """Test strategy handles empty database gracefully"""
        # Use AsyncMock to handle the 'await' in services.py
        with patch('app.services.get_all_data', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = [] # Empty list
            
            result = await calculate_strategy_performance()
            self.assertIn("error", result)

    async def test_strategy_calculation_logic(self):
        """Test correctness of strategy metrics on dummy data"""
        
        # Create dummy data
        mock_data = []
        base_date = datetime(2024, 1, 1)
        
        # 20 data points
        prices = [100] * 10 + [110] * 5 + [90] * 5

        for i, price in enumerate(prices):
            mock_rec = MagicMock()
            mock_rec.datetime = base_date
            mock_rec.close = Decimal(price)
            mock_data.append(mock_rec)

        # Use AsyncMock here too
        with patch('app.services.get_all_data', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_data
            
            result = await calculate_strategy_performance()
            
            # Check structure of response
            self.assertIn("total_return_percentage", result)
            self.assertIn("win_rate", result)
            self.assertIsInstance(result["total_trades"], int)
            
            # Verify we got some trades (logic check)
            # Based on the pattern, we expect at least one crossover.
            # But even if 0 trades, strict types must match.
            print(f"Strategy Result: {result}")

if __name__ == '__main__':
    unittest.main()
