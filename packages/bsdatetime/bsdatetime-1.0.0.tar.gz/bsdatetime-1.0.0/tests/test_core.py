import unittest
import datetime
import bsdatetime as bs

class TestBikramSambat(unittest.TestCase):
    def test_conversion_accuracy(self):
        """Test known date conversions for accuracy."""
        # Known conversion: 2075-01-01 BS = 2018-04-14 AD
        bs_date = (2075, 1, 1)
        expected_ad = datetime.date(2018, 4, 14)
        
        ad_result = bs.bs_to_ad(*bs_date)
        self.assertEqual(ad_result, expected_ad)
        
        # Convert back
        bs_result = bs.ad_to_bs(ad_result)
        self.assertEqual(bs_result, bs_date)

    def test_validation(self):
        """Test date validation."""
        self.assertTrue(bs.is_valid_bs_date(2075, 1, 1))
        self.assertFalse(bs.is_valid_bs_date(2075, 13, 1))  # Invalid month
        self.assertFalse(bs.is_valid_bs_date(2075, 1, 32))  # Invalid day

    def test_formatting(self):
        """Test date formatting."""
        formatted = bs.format_bs_date(2081, 5, 15, "%Y-%m-%d")
        self.assertEqual(formatted, "2081-05-15")

    def test_error_handling(self):
        """Test error handling for invalid inputs."""
        with self.assertRaises(TypeError):
            bs.bs_to_ad("2075", 1, 1)
        
        with self.assertRaises(ValueError):
            bs.bs_to_ad(3000, 1, 1)  # Out of range

if __name__ == "__main__":
    unittest.main()
