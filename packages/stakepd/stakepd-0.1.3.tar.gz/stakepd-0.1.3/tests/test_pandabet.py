import unittest
import pandas as pd
import pandabet as pb

class TestToImpliedProbabilitySeries(unittest.TestCase):

    def test_to_implied_probability_invalid_input(self):
        odds = pd.Series([2.0, 1.5, 1.0])
        with self.assertRaises(ValueError):
            odds.implied_probability(odds_type="invalid odds type")
        with self.assertRaises(ValueError):
            odds.implied_probability(odds_type=5)
    
    def test_decimal_odds_to_implied_probability(self):
        decimal_odds = pd.Series([2.0, 1.5, 1.0])
        true_implied_probabiliy = pd.Series([0.5, 0.6666666666666666, 1.0])
        pd.testing.assert_series_equal(decimal_odds.implied_probability(), true_implied_probabiliy)
        decimal_odds = pd.Series([0, 0.5, -3])
        with self.assertRaises(ValueError):
            decimal_odds.implied_probability(odds_type="decimal")
        decimal_odds = pd.Series(["ABC", "1.5"])
        with self.assertRaises(ValueError):
            decimal_odds.implied_probability(odds_type="decimal")

    def test_fractional_odds_to_implied_probability(self):
        fractional_odds = pd.Series([1/4, 2/1, 10/2])
        true_implied_probability = pd.Series([0.8, 0.3333333333333333, 0.16666666666666666])
        pd.testing.assert_series_equal(fractional_odds.implied_probability(odds_type="fractional"), true_implied_probability)
        fractional_odds = pd.Series([0, -1, 1/3])
        with self.assertRaises(ValueError):
            fractional_odds.implied_probability(odds_type="fractional")

    def test_american_odds_to_implied_probability(self):
        american_odds = pd.Series([100, -150, 200])
        true_implied_probability = pd.Series([0.5, 0.6, 0.333333])
        pd.testing.assert_series_equal(american_odds.implied_probability(odds_type="american"), true_implied_probability)
        american_odds = pd.Series([0, -1, 1/3])
        with self.assertRaises(ValueError):
            american_odds.implied_probability(odds_type="american")

class TestToImpliedProbabilityDataFrame(unittest.TestCase):

    def test_to_implied_probability_invalid_input(self):
        odds = pd.DataFrame({"A": [2.0, 1.5, 1.0], "B": [1.0, 0.5, 0.0]})
        with self.assertRaises(ValueError):
            odds.implied_probability(odds_type="invalid odds type")
        with self.assertRaises(ValueError):
            odds.implied_probability(odds_type=5)

    def test_decimal_odds_to_implied_probability(self):
        decimal_odds = pd.DataFrame({"A": [2.0, 1.5, 5.0], "B": [50, 8.0, 25.0]})
        true_implied_probabilities = pd.DataFrame({"A_implied_probability": [0.5, 0.6666666666666666, 0.2], "B_implied_probability": [0.02, 0.125, 0.04]})
        output = decimal_odds.implied_probability(odds_type="decimal")
        pd.testing.assert_frame_equal(output, true_implied_probabilities)

class TestToOddsSeries(unittest.TestCase):

    def test_to_odds_invalid_input(self):
        implied_probability = pd.Series(["ABC", "0.8"])
        with self.assertRaises(ValueError):
            implied_probability.odds(odds_type="decimal")
        implied_probability = pd.Series([0.8, 0.6])
        with self.assertRaises(ValueError):
            implied_probability.odds(odds_type="invalid odds type")

    def test_implied_probability_to_decimal_odds(self):
        implied_probability = pd.Series([0.5, 0.4])
        true_decimal_odds = pd.Series([2, 2.5])
        pd.testing.assert_series_equal(implied_probability.odds(odds_type="decimal"), true_decimal_odds)
        implied_probability = pd.Series([-1, 2])
        with self.assertRaises(ValueError):
            implied_probability.odds(odds_type="decimal")

    def test_implied_probability_to_fractional_odds(self):
        implied_probability = pd.Series([0.8, 0.3333333333333333, 0.16666666666666666])
        true_fractional_odds = pd.Series([1/4, 2/1, 10/2])
        pd.testing.assert_series_equal(implied_probability.odds(odds_type="fractional"), true_fractional_odds)
        implied_probability = pd.Series([-1, 2])
        with self.assertRaises(ValueError):
            implied_probability.odds(odds_type="fractional")

    def test_implied_probability_to_american_odds(self):
        implied_probability = pd.Series([0.5, 0.6, 0.333333])
        true_american_odds = pd.Series([100.0, -150.0, 200.0])
        pd.testing.assert_series_equal(implied_probability.odds(odds_type="american"), true_american_odds, atol=1e-5)
        implied_probability = pd.Series([-1, 2])
        with self.assertRaises(ValueError):
            implied_probability.odds(odds_type="american")

class TestToOddsDataFrame(unittest.TestCase):

    def test_to_odds_invalid_input(self):
        implied_probability = pd.DataFrame({"A": ["ABC", "0.8"], "B": [0.5, 0.6]})
        with self.assertRaises(ValueError):
            implied_probability.odds(odds_type="decimal")
        implied_probability = pd.DataFrame({"A": [0.8, 0.6], "B": [0.5, 0.6]})
        with self.assertRaises(ValueError):
            implied_probability.odds(odds_type="invalid odds type")

    def test_implied_probability_to_decimal_odds(self):
        implied_probability = pd.DataFrame({"A": [0.5, 0.4], "B": [0.3, 0.2]})
        true_decimal_odds = pd.DataFrame({"A_decimal_odds": [2, 2.5], "B_decimal_odds": [3.3333333333333335, 5]})
        pd.testing.assert_frame_equal(implied_probability.odds(odds_type="decimal"), true_decimal_odds)
        implied_probability = pd.DataFrame({"A": [-1, 2]})
        with self.assertRaises(ValueError):
            implied_probability.odds(odds_type="decimal")

    def test_implied_probability_to_fractional_odds(self):
        implied_probability = pd.DataFrame({"A": [0.8, 0.3333333333333333], "B": [0.16666666666666666, 0.1]})
        true_fractional_odds = pd.DataFrame({"A_fractional_odds": [1/4, 2/1], "B_fractional_odds": [10/2, 9/1]})
        pd.testing.assert_frame_equal(implied_probability.odds(odds_type="fractional"), true_fractional_odds)
        implied_probability = pd.DataFrame({"A": [-1, 2]})
        with self.assertRaises(ValueError):
            implied_probability.odds(odds_type="fractional")

    def test_implied_probability_to_american_odds(self):
        implied_probability = pd.DataFrame({"A": [0.5, 0.6], "B": [0.3333333333333333, 0.2]})
        true_american_odds = pd.DataFrame({"A_american_odds": [100.0, -150.0], "B_american_odds": [200.0, 400]})
        pd.testing.assert_frame_equal(implied_probability.odds(odds_type="american"), true_american_odds)
        implied_probability = pd.DataFrame({"A": [-1, 2]})
        with self.assertRaises(ValueError):
            implied_probability.odds(odds_type="american")

class TestConvertSeries(unittest.TestCase):

    def test_convert_invalid_input(self):
        odds = pd.Series(["ABC", "0.8"])
        with self.assertRaises(ValueError):
            odds.convert(from_type="decimal", to_type="implied_probability")
        odds = pd.Series([0.8, 0.6])
        with self.assertRaises(ValueError):
            odds.convert(from_type="invalid odds type", to_type="implied_probability")

    def test_convert_decimal_to_implied_probability(self):
        decimal_odds = pd.Series([2.0, 1.5, 1.0])
        true_implied_probabilities = pd.Series([0.5, 0.6666666666666666, 1.0])
        pd.testing.assert_series_equal(decimal_odds.convert(from_type="decimal", to_type="implied_probability"), true_implied_probabilities)
        decimal_odds = pd.Series([0, 0.5, -3])
        with self.assertRaises(ValueError):
            decimal_odds.convert(from_type="decimal", to_type="implied_probability")
        decimal_odds = pd.Series(["ABC", "1.5"])
        with self.assertRaises(ValueError):
            decimal_odds.convert(from_type="decimal", to_type="implied_probability")

    def test_convert_fractional_to_implied_probability(self):
        fractional_odds = pd.Series([1/4, 2/1, 10/2])
        true_implied_probabilities = pd.Series([0.8, 0.3333333333333333, 0.16666666666666666])
        pd.testing.assert_series_equal(fractional_odds.convert(from_type="fractional", to_type="implied_probability"), true_implied_probabilities)
        fractional_odds = pd.Series([0, -1, 1/3])
        with self.assertRaises(ValueError):
            fractional_odds.convert(from_type="fractional", to_type="implied_probability")

    def test_convert_american_to_implied_probability(self):
        american_odds = pd.Series([100, -150, 200])
        true_implied_probabilities = pd.Series([0.5, 0.6, 0.333333])
        pd.testing.assert_series_equal(american_odds.convert(from_type="american", to_type="implied_probability"), true_implied_probabilities)
        american_odds = pd.Series([0, -1, 1/3])
        with self.assertRaises(ValueError):
            american_odds.convert(from_type="american", to_type="implied_probability")

    def test_convert_implied_probability_to_decimal(self):
        implied_probability = pd.Series([0.5, 0.4])
        true_decimal_odds = pd.Series([2, 2.5])
        pd.testing.assert_series_equal(implied_probability.convert(from_type="implied_probability", to_type="decimal"), true_decimal_odds)
        implied_probability = pd.Series([-1, 2])
        with self.assertRaises(ValueError):
            implied_probability.convert(from_type="implied_probability", to_type="decimal")

    def test_convert_implied_probability_to_fractional(self):
        implied_probability = pd.Series([0.8, 0.3333333333333333, 0.16666666666666666])
        true_fractional_odds = pd.Series([1/4, 2/1, 10/2])
        pd.testing.assert_series_equal(implied_probability.convert(from_type="implied_probability", to_type="fractional"), true_fractional_odds)
        implied_probability = pd.Series([-1, 2])
        with self.assertRaises(ValueError):
            implied_probability.convert(from_type="implied_probability", to_type="fractional")

    def test_convert_implied_probability_to_american(self):
        implied_probability = pd.Series([0.5, 0.6, 0.333333])
        true_american_odds = pd.Series([100.0, -150.0, 200.0])
        pd.testing.assert_series_equal(implied_probability.convert(from_type="implied_probability", to_type="american"), true_american_odds, atol=1e-5)
        implied_probability = pd.Series([-1, 2])
        with self.assertRaises(ValueError):
            implied_probability.convert(from_type="implied_probability", to_type="american")

    def test_convert_decimal_to_american(self):
        decimal_odds = pd.Series([2.0, 1.5, 3.0])
        true_american_odds = pd.Series([100.0, -200.0, 200.0])
        pd.testing.assert_series_equal(decimal_odds.convert(from_type="decimal", to_type="american"), true_american_odds, atol=1e-5)
        decimal_odds = pd.Series([0, -1])
        with self.assertRaises(ValueError):
            decimal_odds.convert(from_type="decimal", to_type="american")

    def test_convert_decimal_to_fractional(self):
        decimal_odds = pd.Series([2.0, 1.5, 3.0])
        true_fractional_odds = pd.Series([1.0, 0.5, 2.0])
        pd.testing.assert_series_equal(decimal_odds.convert(from_type="decimal", to_type="fractional"), true_fractional_odds)
        decimal_odds = pd.Series([0, -1])
        with self.assertRaises(ValueError):
            decimal_odds.convert(from_type="decimal", to_type="fractional")

    def test_convert_american_to_fractional(self):
        american_odds = pd.Series([100.0, -200.0, 300.0])
        true_fractional_odds = pd.Series([1.0, 0.5, 3.0])
        pd.testing.assert_series_equal(american_odds.convert(from_type="american", to_type="fractional"), true_fractional_odds)
        american_odds = pd.Series([0, -1])
        with self.assertRaises(ValueError):
            american_odds.convert(from_type="american", to_type="fractional")

    def test_convert_american_to_decimal(self):
        american_odds = pd.Series([100, -200, 300])
        true_decimal_odds = pd.Series([2.0, 1.5, 4.0])
        pd.testing.assert_series_equal(american_odds.convert(from_type="american", to_type="decimal"), true_decimal_odds)
        american_odds = pd.Series([0, -1])
        with self.assertRaises(ValueError):
            american_odds.convert(from_type="american", to_type="decimal")

    def test_convert_fractional_to_decimal(self):
        fractional_odds = pd.Series([1.0, 0.5, 2.0])
        true_decimal_odds = pd.Series([2.0, 1.5, 3.0])
        pd.testing.assert_series_equal(fractional_odds.convert(from_type="fractional", to_type="decimal"), true_decimal_odds)
        fractional_odds = pd.Series([0, -1])
        with self.assertRaises(ValueError):
            fractional_odds.convert(from_type="fractional", to_type="decimal")

    def test_convert_fractional_to_american(self):
        fractional_odds = pd.Series([1.0, 0.5, 2.0])
        true_american_odds = pd.Series([100.0, -200.0, 200.0])
        pd.testing.assert_series_equal(fractional_odds.convert(from_type="fractional", to_type="american"), true_american_odds, atol=1e-5)
        fractional_odds = pd.Series([0, -1])
        with self.assertRaises(ValueError):
            fractional_odds.convert(from_type="fractional", to_type="american")

class TestConvertDataFrame(unittest.TestCase):
    
    def test_convert_invalid_input(self):
        odds = pd.DataFrame({"A": ["ABC", "0.8"], "B": [0.5, 0.6]})
        with self.assertRaises(ValueError):
            odds.convert(from_type="decimal", to_type="implied_probability")
        odds = pd.DataFrame({"A": [0.8, 0.6], "B": [0.5, 0.6]})
        with self.assertRaises(ValueError):
            odds.convert(from_type="invalid odds type", to_type="implied_probability")

    def test_convert_decimal_to_implied_probability(self):
        decimal_odds = pd.DataFrame({"A": [2.0, 1.5, 5.0], "B": [50, 8.0, 25.0]})
        true_implied_probabilities = pd.DataFrame({"A_implied_probability": [0.5, 0.6666666666666666, 0.2], "B_implied_probability": [0.02, 0.125, 0.04]})
        output = decimal_odds.convert(from_type="decimal", to_type="implied_probability")
        pd.testing.assert_frame_equal(output, true_implied_probabilities)
        decimal_odds = pd.DataFrame({"A": [-1, 2]})
        with self.assertRaises(ValueError):
            decimal_odds.convert(from_type="decimal", to_type="implied_probability")

    def test_convert_fractional_to_implied_probability(self):
        fractional_odds = pd.DataFrame({"A": [1/4, 2/1], "B": [10/2, 9/1]})
        true_implied_probabilities = pd.DataFrame({"A_implied_probability": [0.8, 0.3333333333333333], "B_implied_probability": [0.16666666666666666, 0.1]})
        output = fractional_odds.convert(from_type="fractional", to_type="implied_probability")
        pd.testing.assert_frame_equal(output, true_implied_probabilities)
        fractional_odds = pd.DataFrame({"A": [-1, 2]})
        with self.assertRaises(ValueError):
            fractional_odds.convert(from_type="fractional", to_type="implied_probability")

    def test_convert_american_to_implied_probability(self):
        american_odds = pd.DataFrame({"A": [100, -150, 200], "B": [-475, -200, 10000]})
        true_implied_probabilities = pd.DataFrame({"A_implied_probability": [0.5, 0.6, 0.3333333333333], "B_implied_probability": [0.826, 0.666666, 0.0099]})
        output = american_odds.convert(from_type="american", to_type="implied_probability")
        pd.testing.assert_frame_equal(output, true_implied_probabilities, atol=1e-3)
        american_odds = pd.DataFrame({"A": [0, -1], "B": [0, -1]})
        with self.assertRaises(ValueError):
            american_odds.convert(from_type="american", to_type="implied_probability")

    def test_convert_implied_probability_to_decimal(self):
        implied_probabilities = pd.DataFrame({"A": [0.5, 0.6666666666666666, 0.2], "B": [0.02, 0.125, 0.04]})
        true_decimal_odds = pd.DataFrame({"A_decimal_odds": [2.0, 1.5, 5.0], "B_decimal_odds": [50, 8.0, 25.0]})
        output = implied_probabilities.convert(from_type="implied_probability", to_type="decimal")
        pd.testing.assert_frame_equal(output, true_decimal_odds, atol=1e-3)
    
    def test_convert_implied_probability_to_american(self):
        implied_probabilities = pd.DataFrame({
            "A": [0.5, 0.6, 0.3333333333333],
            "B": [0.826, 0.666666, 0.1]
        })
        true_american_odds = pd.DataFrame({
            "A_american_odds": [100.0, -150.0, 200.0],
            "B_american_odds": [-474.7, -200.0, 900]
        })
        output = implied_probabilities.convert(from_type="implied_probability", to_type="american")
        pd.testing.assert_frame_equal(output, true_american_odds, atol=1e-1)
        implied_probabilities_invalid = pd.DataFrame({"A": [-1, 2], "B": [-1, 2]})
        with self.assertRaises(ValueError):
            implied_probabilities_invalid.convert(from_type="implied_probability", to_type="american")
    
    def test_convert_implied_probability_to_fractional(self):
        implied_probabilities = pd.DataFrame({"A": [0.8, 0.3333333333333333], "B": [0.16666666666666666, 0.1]})
        true_fractional_odds = pd.DataFrame({"A_fractional_odds": [1/4, 2/1], "B_fractional_odds": [10/2, 9/1]})
        output = implied_probabilities.convert(from_type="implied_probability", to_type="fractional")
        pd.testing.assert_frame_equal(output, true_fractional_odds)
        implied_probabilities_invalid = pd.DataFrame({"A": [-1, 2]})
        with self.assertRaises(ValueError):
            implied_probabilities_invalid.convert(from_type="implied_probability", to_type="fractional")
    
    def test_convert_same(self):
        # implied_probability -> implied_probability
        df = pd.DataFrame({"A": [0.5, 0.4], "B": [0.3, 0.2]})
        result = df.convert(from_type="implied_probability", to_type="implied_probability")
        pd.testing.assert_frame_equal(result, df)

        # fractional -> fractional
        df = pd.DataFrame({"A": [1.0, 0.5], "B": [2.0, 3.0]})
        result = df.convert(from_type="fractional", to_type="fractional")
        pd.testing.assert_frame_equal(result, df)

        # decimal -> decimal
        df = pd.DataFrame({"A": [2.0, 1.5], "B": [3.0, 4.0]})
        result = df.convert(from_type="decimal", to_type="decimal")
        pd.testing.assert_frame_equal(result, df)

        # american -> american
        df = pd.DataFrame({"A": [100.0, -200.0], "B": [300.0, -150.0]})
        result = df.convert(from_type="american", to_type="american")
        pd.testing.assert_frame_equal(result, df)

class TestAsFloatSeries(unittest.TestCase):

    def test_as_float(self):
        fractional_odds = pd.Series(["1/4", "1/2", "2/1"])
        true_fractional_odds = pd.Series([0.25, 0.5, 2.0])
        pd.testing.assert_series_equal(fractional_odds.as_float(), true_fractional_odds)
        fractional_odds = pd.Series([-1, 2])
        with self.assertRaises(ValueError):
            fractional_odds.as_float()

class TestAsFractionSeries(unittest.TestCase):

    def test_as_fraction(self):
        fractional_odds = pd.Series([0.25, 0.5, 2.0, 1.0])
        true_fractional_odds = pd.Series(["1/4", "1/2", "2/1", "1/1"])
        pd.testing.assert_series_equal(fractional_odds.as_fraction(), true_fractional_odds)
        fractional_odds = pd.Series([-1, 2])
        with self.assertRaises(ValueError):
            fractional_odds.as_fraction()

class TestOverroundSeries(unittest.TestCase):

    def test_overround_invalid_input(self):
        with self.assertRaises(ValueError):
            pd.Series([2.0, 1.5, 3.0]).overround(odds_type="invalid")
        with self.assertRaises(ValueError):
            pd.Series([1.2, -0.5, 0.8]).overround(odds_type="implied_probability")
        with self.assertRaises(ValueError):
            pd.Series([0, -1, 1/3]).overround(odds_type="fractional")
        with self.assertRaises(ValueError):
            pd.Series([0, -1, 1/3]).overround(odds_type="american")
        with self.assertRaises(ValueError):
            pd.Series([0.2, -0.5, -2.2]).overround(odds_type="decimal")

    def test_overround(self):
        implied_odds = pd.Series([0.8, 0.5, 0.3])
        self.assertAlmostEqual(implied_odds.overround(), 0.6, places=2)
        fractional_odds = pd.Series([1/4, 1/2, 2/1])
        fractional_overround = fractional_odds.implied_probability("fractional").sum() - 1
        self.assertAlmostEqual(fractional_odds.overround(odds_type="fractional"), fractional_overround, places=2)
        american_odds = pd.Series([100.0, -200.0, 300.0])
        self.assertAlmostEqual(american_odds.overround(odds_type="american"), 0.41666, places=2)
        decimal_odds = pd.Series([2.0, 1.5, 3.0])
        self.assertAlmostEqual(decimal_odds.overround(odds_type="decimal"), 0.4999, places=2)

class TestOverroundDataFrame(unittest.TestCase):

    def test_overround_invalid_input(self):
        with self.assertRaises(ValueError):
            pd.DataFrame([[2.0, 1.5], [3.0, 4.0]]).overround(odds_type="invalid")
        with self.assertRaises(ValueError):
            pd.DataFrame([[1.2, -0.5], [0.8, 0.9]]).overround(odds_type="implied_probability")
        with self.assertRaises(ValueError):
            pd.DataFrame([[0, -1, 1/3], [0, -1, 1/3]]).overround(odds_type="fractional")
        with self.assertRaises(ValueError):
            pd.DataFrame([[0, -1, 1/3], [0, -1, 1/3]]).overround(odds_type="american")
        with self.assertRaises(ValueError):
            pd.DataFrame([[0.2, -0.5, -2.2], [0.2, -0.5, -2.2]]).overround(odds_type="decimal")

    def test_overround(self):
        implied_odds = pd.DataFrame({"A": [0.8, 0.5], "B": [0.3, 0.7]})
        expected_implied_overround = pd.Series([0.1, 0.2])
        pd.testing.assert_series_equal(implied_odds.overround(), expected_implied_overround)
        fractional_odds = pd.DataFrame({"A": [1/4, 1/2], "B": [2/1, 1/3]})
        expected_fractional_overround = pd.Series([0.13333, 0.416666])
        pd.testing.assert_series_equal(fractional_odds.overround(odds_type="fractional"), expected_fractional_overround, atol=1e-5)
        american_odds = pd.DataFrame({"A": [100.0, -200], "B": [300.0, 100]})
        expected_american_overround = pd.Series([-0.25, 0.16666666])
        pd.testing.assert_series_equal(american_odds.overround(odds_type="american"), expected_american_overround, atol=1e-5)
        decimal_odds = pd.DataFrame({"A": [2.0, 1.5], "B": [3.0, 4.0]})
        pd.testing.assert_series_equal(decimal_odds.overround(odds_type="decimal"), pd.Series([-0.16666666, -0.08]), atol=1e-2)

class TestVigSeries(unittest.TestCase):

    def test_vig_invalid_input(self):
        with self.assertRaises(ValueError):
            pd.Series([0.8, 0.4, 0.6]).vig(odds_type="invalid_input")
        with self.assertRaises(ValueError):
            pd.Series([0.2, -0.5, -2.2]).vig(odds_type="decimal")
        with self.assertRaises(ValueError):
            pd.Series([0.2, -0.5, -2.2]).vig(odds_type="fractional")
        with self.assertRaises(ValueError):
            pd.Series([0.2, -0.5, -2.2]).vig(odds_type="american")
        with self.assertRaises(ValueError):
            pd.Series([0.2, -0.5, -2.2]).vig(odds_type="implied_probability")

    def test_vig(self):
        decimal_odds = pd.Series([2.0, 1.5, 3.0])
        self.assertAlmostEqual(decimal_odds.vig(odds_type="decimal"), 0.3333, places=2)
        fractional_odds = pd.Series([1.0, 0.5, 2.0])
        self.assertAlmostEqual(fractional_odds.vig(odds_type="fractional"), 0.3333, places=2)
        american_odds = pd.Series([100.0, -200.0, 300.0])
        self.assertAlmostEqual(american_odds.vig(odds_type="american"), 0.294, places=2)
        implied_probability = pd.Series([0.5, 0.6, 0.333333])
        self.assertAlmostEqual(implied_probability.vig(odds_type="implied_probability"), 0.302, places=2)

class TestVigDataFrame(unittest.TestCase):

    def test_vig_invalid_input(self):
        with self.assertRaises(ValueError):
            pd.DataFrame({"A": [2.0, 3.0], "B": [1.5, 4.0]}).vig(odds_type="invalid")
        with self.assertRaises(ValueError):
            pd.DataFrame({"A": [1.2, -0.5], "B": [0.8, 0.9]}).vig(odds_type="implied_probability")
        with self.assertRaises(ValueError):
            pd.DataFrame({"A": [0, -1], "B": [1/3, 1/3]}).vig(odds_type="fractional")
        with self.assertRaises(ValueError):
            pd.DataFrame({"A": [0, -1], "B": [1/3, 1/3]}).vig(odds_type="american")
        with self.assertRaises(ValueError):
            pd.DataFrame({"A": [0.2, -0.5], "B": [-2.2, -2.2]}).vig(odds_type="decimal")

    def test_vig(self):
        implied_odds = pd.DataFrame({"A": [0.8, 0.5], "B": [0.3, 0.7]})
        expected_implied_vig = pd.Series([0.090909, 0.166666666])
        pd.testing.assert_series_equal(implied_odds.vig(), expected_implied_vig, atol=1e-3)

        fractional_odds = pd.DataFrame({"A": [1/4, 1/2], "B": [2/1, 1/3]})
        expected_fractional_vig = pd.Series([0.117647, 0.294117])
        pd.testing.assert_series_equal(fractional_odds.vig(odds_type="fractional"), expected_fractional_vig, atol=1e-5)

        american_odds = pd.DataFrame({"A": [100.0, -200], "B": [300.0, 100]})
        expected_american_vig = pd.Series([-0.333333, 0.142857])
        pd.testing.assert_series_equal(american_odds.vig(odds_type="american"), expected_american_vig, atol=1e-5)

        decimal_odds = pd.DataFrame({"A": [2.0, 1.5], "B": [3.0, 2.5]})
        expected_decimal_vig = pd.Series([-0.2, 0.0625])
        pd.testing.assert_series_equal(decimal_odds.vig(odds_type="decimal"), expected_decimal_vig, atol=1e-5)

class TestDevigSeries(unittest.TestCase):

    def test_devig_implied_probabilities(self):
        implied_probabilities = pd.Series([0.8, 0.5, 0.3])
        self.assertAlmostEqual(implied_probabilities.devig().sum(), 1.0, places=2)

    def test_devig_invalid_input(self):
        with self.assertRaises(ValueError):
            pd.Series([0.8, -0.4, 0.6]).devig()
        with self.assertRaises(ValueError):
            pd.Series([0.2, -0.5, -2.2]).devig()
        with self.assertRaises(TypeError):
            pd.Series([0.2, 0.5, "1/2"]).devig()

class TestDevigDataFrame(unittest.TestCase):

    def test_devig_valid(self):
        implied_probabilities = pd.DataFrame({
            "A": [0.8, 0.5],
            "B": [0.3, 0.7]
        })
        devigged = implied_probabilities.devig()
        self.assertTrue(isinstance(devigged, pd.DataFrame))
        # Each row should sum to 1
        self.assertTrue(all(abs(devigged.sum(axis=1) - 1) < 1e-6))

    def test_devig_invalid_input(self):
        # Negative probabilities
        implied_probabilities = pd.DataFrame({"A": [0.8, -0.5], "B": [0.3, 0.7]})
        with self.assertRaises(ValueError):
            implied_probabilities.devig()
        # Non-numeric
        implied_probabilities = pd.DataFrame({"A": [0.8, "1/2"], "B": [0.3, 0.7]})
        with self.assertRaises(TypeError):
            implied_probabilities.devig()
        # All negative
        implied_probabilities = pd.DataFrame({"A": [-0.8, -0.5], "B": [-0.3, -0.7]})
        with self.assertRaises(ValueError):
            implied_probabilities.devig()

class TestPayoutFloatingPoint(unittest.TestCase):

    def test_payout_decimal_floats(self):
        # Test with float stake and float odds (decimal)
        self.assertAlmostEqual(pb.payout(123.45, 2.75, 'decimal'), 123.45 * 2.75, places=6)
        self.assertAlmostEqual(pb.payout(0.99, 1.01, 'decimal'), 0.99 * 1.01, places=6)
        self.assertAlmostEqual(pb.payout(50.5, 10.5, 'decimal'), 50.5 * 10.5, places=6)

    def test_payout_fractional_floats(self):
        # Test with float stake and float odds (fractional)
        self.assertAlmostEqual(pb.payout(120, 2.75, 'fractional'), 450, places=6)
        self.assertAlmostEqual(pb.payout(100, 0.5, 'fractional'), 150, places=6)
        self.assertAlmostEqual(pb.payout(50, 10.5, 'fractional'), 575, places=6)

    def test_payout_american_floats(self):
        # Test with float stake and float odds (american)
        self.assertAlmostEqual(pb.payout(100.5, 150.0, 'american'), 251.25, places=6)
        self.assertAlmostEqual(pb.payout(200, -120.0, 'american'), 366.6666666666667, places=6)
        self.assertAlmostEqual(pb.payout(50, 250.0, 'american'), 175.0, places=6)

    def test_payout_invalid_float_inputs(self):
        # Negative stake
        with self.assertRaises(ValueError):
            pb.payout(-10.5, 2.0, 'decimal')
        # Zero stake
        with self.assertRaises(ValueError):
            pb.payout(0.0, 2.0, 'decimal')
        # Non-positive odds
        with self.assertRaises(ValueError):
            pb.payout(10.0, 0.0, 'decimal')
        with self.assertRaises(ValueError):
            pb.payout(10.0, -2.0, 'decimal')
        # Invalid odds type
        with self.assertRaises(ValueError):
            pb.payout(10.0, 2.0, 'not_a_type')

class TestPayoutSeries(unittest.TestCase):

    def test_payout_decimal_series(self):
        stakes = pd.Series([100, 50, 10])
        odds = pd.Series([2.0, 3.0, 1.5])
        expected = pd.Series([200.0, 150.0, 15.0])
        result = pb.payout(stakes, odds, 'decimal')
        pd.testing.assert_series_equal(result, expected)

    def test_payout_fractional_series(self):
        stakes = pd.Series([100, 50, 10])
        odds = pd.Series([1.0, 2.0, 0.5])
        expected = pd.Series([200.0, 150.0, 15.0])
        result = pb.payout(stakes, odds, 'fractional')
        pd.testing.assert_series_equal(result, expected)

    def test_payout_american_series(self):
        stakes = pd.Series([100, 50, 10])
        odds = pd.Series([100, -200, 300])
        expected = pd.Series([200.0, 75.0, 40])
        result = pb.payout(stakes, odds, 'american')
        pd.testing.assert_series_equal(result, expected)

    def test_payout_invalid_inputs(self):
        # Negative stake
        stakes = pd.Series([-10, 20])
        odds = pd.Series([2.0, 2.0])
        with self.assertRaises(ValueError):
            pb.payout(stakes, odds, 'decimal')
        # Zero stake
        stakes = pd.Series([0, 20])
        with self.assertRaises(ValueError):
            pb.payout(stakes, odds, 'decimal')
        # Non-positive odds
        stakes = pd.Series([10, 20])
        odds = pd.Series([0, -2])
        with self.assertRaises(ValueError):
            pb.payout(stakes, odds, 'decimal')
        # Invalid odds type
        odds = pd.Series([2.0, 2.0])
        with self.assertRaises(ValueError):
            pb.payout(stakes, odds, 'not_a_type')

class TestProfitFloat(unittest.TestCase):

    def test_profit_decimal(self):
        self.assertAlmostEqual(pb.profit(100, 2.5, 'decimal'), 150.0)
        self.assertAlmostEqual(pb.profit(50, 1.5, 'decimal'), 25.0)
        self.assertAlmostEqual(pb.profit(10, 10, 'decimal'), 90.0)

    def test_profit_fractional(self):
        self.assertAlmostEqual(pb.profit(100, 1.5, 'fractional'), 150.0)
        self.assertAlmostEqual(pb.profit(50, 2.0, 'fractional'), 100.0)
        self.assertAlmostEqual(pb.profit(10, 0.5, 'fractional'), 5.0)

    def test_profit_american(self):
        self.assertAlmostEqual(pb.profit(100, 150, 'american'), 150.0)
        self.assertAlmostEqual(pb.profit(200, -120, 'american'), 166.66666666666669)
        self.assertAlmostEqual(pb.profit(50, 250, 'american'), 125.0)

    def test_profit_invalid_inputs(self):
        with self.assertRaises(ValueError):
            pb.profit(-10, 2.0, 'decimal')
        with self.assertRaises(ValueError):
            pb.profit(0, 2.0, 'decimal')
        with self.assertRaises(ValueError):
            pb.profit(10, 0, 'decimal')
        with self.assertRaises(ValueError):
            pb.profit(10, -2, 'decimal')
        with self.assertRaises(ValueError):
            pb.profit(10, 2, 'not_a_type')

class TestProfitSeries(unittest.TestCase):

    def test_profit_decimal_series(self):
        stakes = pd.Series([100, 50, 10])
        odds = pd.Series([2.0, 3.0, 1.5])
        expected = pd.Series([100.0, 100.0, 5.0])
        result = pb.profit(stakes, odds, 'decimal')
        pd.testing.assert_series_equal(result, expected)

    def test_profit_fractional_series(self):
        stakes = pd.Series([100, 50, 10])
        odds = pd.Series([1.0, 2.0, 0.5])
        expected = pd.Series([100.0, 100.0, 5.0])
        result = pb.profit(stakes, odds, 'fractional')
        pd.testing.assert_series_equal(result, expected)

    def test_profit_american_series(self):
        stakes = pd.Series([100, 50, 10])
        odds = pd.Series([100, -200, 300])
        expected = pd.Series([100.0, 25.0, 30.0])
        result = pb.profit(stakes, odds, 'american')
        pd.testing.assert_series_equal(result, expected)

    def test_profit_invalid_inputs(self):
        stakes = pd.Series([-10, 20])
        odds = pd.Series([2.0, 2.0])
        with self.assertRaises(ValueError):
            pb.profit(stakes, odds, 'decimal')
        stakes = pd.Series([0, 20])
        with self.assertRaises(ValueError):
            pb.profit(stakes, odds, 'decimal')
        stakes = pd.Series([10, 20])
        odds = pd.Series([0, -2])
        with self.assertRaises(ValueError):
            pb.profit(stakes, odds, 'decimal')
        odds = pd.Series([2.0, 2.0])
        with self.assertRaises(ValueError):
            pb.profit(stakes, odds, 'not_a_type')

class TestKellyCriterionScalar(unittest.TestCase):

    def test_kelly_criterion(self):
        bankroll = 1
        odds = 100
        probability = 0.6
        kelly_fraction = pb.kelly_criterion(odds, probability, 'american', bankroll)
        self.assertAlmostEqual(kelly_fraction, 0.2, places=2)

    def test_kelly_criterion_no_bet(self):
        bankroll = 1
        odds = 2.0
        probability = 0.4
        kelly_fraction = pb.kelly_criterion(odds, probability, 'decimal', bankroll)
        self.assertAlmostEqual(kelly_fraction, 0.0, places=2)
    
    def test_kelly_criterion_invalid_inputs(self):
        # Negative bankroll
        with self.assertRaises(ValueError):
            pb.kelly_criterion(100, 0.6, 'american', -1)
        # Zero bankroll
        with self.assertRaises(ValueError):
            pb.kelly_criterion(100, 0.6, 'american', 0)
        # Negative probability
        with self.assertRaises(ValueError):
            pb.kelly_criterion(100, -0.5, 'american', 1)
        # Probability greater than 1
        with self.assertRaises(ValueError):
            pb.kelly_criterion(100, 1.5, 'american', 1)
        # Invalid odds type
        with self.assertRaises(ValueError):
            pb.kelly_criterion(100, 0.6, 'not_a_type', 1)
        # Non-positive odds for decimal
        with self.assertRaises(ValueError):
            pb.kelly_criterion(0, 0.6, 'decimal', 1)
        with self.assertRaises(ValueError):
            pb.kelly_criterion(-2, 0.6, 'decimal', 1)
        # Non-numeric inputs
        with self.assertRaises(TypeError):
            pb.kelly_criterion("abc", 0.6, 'decimal', 1)
        with self.assertRaises(TypeError):
            pb.kelly_criterion(2.0, "xyz", 'decimal', 1)
        with self.assertRaises(TypeError):
            pb.kelly_criterion(2.0, 0.6, 'decimal', "bankroll")

class TestKellyCriterionSeries(unittest.TestCase):

    def test_kelly_criterion_series(self):
        bankroll = 1000
        odds = pd.Series([2.0, 3.0, 1.5])
        probabilities = pd.Series([0.6, 0.4, 0.7])
        expected = pd.Series([
            bankroll * ((2.0 * 0.6 - 1) / (2.0 - 1)),
            bankroll * ((3.0 * 0.4 - 1) / (3.0 - 1)),
            bankroll * ((1.5 * 0.7 - 1) / (1.5 - 1))
        ])
        result = pb.kelly_criterion(odds, probabilities, 'decimal', bankroll)
        pd.testing.assert_series_equal(result, expected)

    def test_kelly_criterion_series_no_bet(self):
        bankroll = 100
        odds = pd.Series([2.0, 3.0])
        probabilities = pd.Series([0.4, 0.3])
        expected = pd.Series([0.0, 0.0])
        result = pb.kelly_criterion(odds, probabilities, 'decimal', bankroll)
        pd.testing.assert_series_equal(result, expected)

    def test_kelly_criterion_series_invalid_inputs(self):
        bankroll = 100
        odds = pd.Series([2.0, -1.0])
        probabilities = pd.Series([0.6, 0.4])
        with self.assertRaises(ValueError):
            pb.kelly_criterion(odds, probabilities, 'decimal', bankroll)
        odds = pd.Series([2.0, 3.0])
        probabilities = pd.Series([-0.1, 1.2])
        with self.assertRaises(ValueError):
            pb.kelly_criterion(odds, probabilities, 'decimal', bankroll)
        with self.assertRaises(ValueError):
            pb.kelly_criterion(odds, probabilities, 'not_a_type', bankroll)
        with self.assertRaises(ValueError):
            pb.kelly_criterion(odds, probabilities, 'decimal', -100)
        with self.assertRaises(ValueError):
            pb.kelly_criterion(odds, probabilities, 'decimal', 0)
        # Non-numeric odds/probabilities
        odds = pd.Series(["abc", 2.0])
        probabilities = pd.Series([0.6, 0.4])
        with self.assertRaises(TypeError):
            pb.kelly_criterion(odds, probabilities, 'decimal', bankroll)
        odds = pd.Series([2.0, 3.0])
        probabilities = pd.Series(["xyz", 0.4])
        with self.assertRaises(TypeError):
            pb.kelly_criterion(odds, probabilities, 'decimal', bankroll)

class TestArbitrage(unittest.TestCase):
    pass