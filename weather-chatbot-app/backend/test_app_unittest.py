import unittest
from app import get_weather

class TestWeatherFunction(unittest.TestCase):
    def test_weather_output(self):
        result = get_weather.invoke({"city": "Luxembourg", "language": "english"})
        self.assertIn("Luxembourg", result["output"])
        self.assertIn("°C", result["output"])

if __name__ == "__main__":
    unittest.main()