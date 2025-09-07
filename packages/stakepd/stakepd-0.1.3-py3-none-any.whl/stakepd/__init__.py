import pandas as pd
from pandas.core.base import PandasObject
from math import gcd
from typing import Union

"""
Private helper functions for pybet
"""

def _american_odds_check(odds: float) -> bool:
    """
    Check if the odds are in American format. For Internal Use Only.
    
    Args:
        odds (float): The odds to check.
    
    Returns:
        bool: True if the odds are in American format, False otherwise.
    """
    return isinstance(float(odds), (int, float)) and (float(odds) >= 100 or float(odds) < -100)

def _decimal_odds_check(odds: float) -> bool:
    """
    Check if the odds are in decimal format. For Internal Use Only.
    
    Args:
        odds (float): The odds to check.
    
    Returns:
        bool: True if the odds are in decimal format, False otherwise.
    """
    return isinstance(float(odds), (int, float)) and float(odds) >= 1

def _fractional_odds_check(odds: float) -> bool:
    """
    Check if the odds are in fractional format. For Internal Use Only.
    
    Args:
        odds (float): The odds to check.
    
    Returns:
        bool: True if the odds are in fractional format, False otherwise.
    """
    return isinstance(odds, (int, float)) and odds > 0

def _payout_american(odds: Union[float, int], stake: Union[float, int]) -> float:
    """
    Calculate the payout based on American odds and stake. For Internal Use Only.
    
    Args:
        odds (float): The American odds.
        stake (float): The stake.
    
    Returns:
        float: The payout.
    """
    if _american_odds_check(odds):
        if float(odds) >= 100:
            return stake * (odds / 100) + stake
        elif float(odds) < -100:
            return stake * (100 / -odds) + stake
    raise ValueError("Invalid American odds.")

def _payout_decimal(odds: float, stake: float) -> float:
    """
    Calculate the payout based on decimal odds and stake. For Internal Use Only.
    
    Args:
        odds (float): The decimal odds.
        stake (float): The stake.
    
    Returns:
        float: The payout.
    """
    if _decimal_odds_check(odds):
        return stake * odds
    raise ValueError("Invalid decimal odds.")

def _payout_fractional(odds: float, stake: float) -> float:
    """
    Calculate the payout based on fractional odds and stake. For Internal Use Only.
    
    Args:
        odds (float): The fractional odds.
        stake (float): The stake.
    
    Returns:
        float: The payout.
    """
    if _fractional_odds_check(odds):
        return stake * (odds + 1)
    raise ValueError("Invalid fractional odds.")

def _payout(odds: float, stake: float, odds_type: str) -> float:
    """
    Calculate the payout based on the odds and stake. For Internal Use Only.
    
    Args:
        odds (float): The odds.
        stake (float): The stake.
        odds_type (str): The type of odds ('decimal', 'fractional', 'american').
    
    Returns:
        float: The payout.
    """
    if odds_type == 'decimal':
        return _payout_decimal(odds, stake)
    elif odds_type == 'fractional':
        return _payout_fractional(odds, stake)
    elif odds_type == 'american':
        return _payout_american(odds, stake)
    raise ValueError("Invalid odds_type. Must be 'decimal', 'fractional', or 'american'.")

def _implied_probability_check(probability: float) -> bool:
    """
    Check if the probability is a valid implied probability. For Internal Use Only.
    
    Args:
        probability (float): The probability to check.
    
    Returns:
        bool: True if the probability is valid, False otherwise.
    """
    if not isinstance(probability, (int, float)):
        raise TypeError("Probability must be a number.")
    if not (0 < probability < 1):
        raise ValueError("Probability must be between 0 and 1.")
    return True


def _odds_check(odds: Union[pd.Series, pd.DataFrame], odds_type: str) -> bool:
    """
    Check if the Series contains valid odds. For Internal Use Only.
    
    Args:
        odds (Series): The Series to check.
        odds_type (str): The type of odds to check ('decimal', 'fractional', 'american', or 'implied_probability').
    
    Returns:
        bool: True if the Series contains valid odds, False otherwise.
    """
    if isinstance(odds, pd.Series):
        if odds_type == 'decimal':
            return odds.apply(_decimal_odds_check).all()
        elif odds_type == 'fractional':
            return odds.apply(_fractional_odds_check).all()
        elif odds_type == 'american':
            return odds.apply(_american_odds_check).all()
        elif odds_type == 'implied_probability':
            return odds.apply(_implied_probability_check).all()
        else:
            raise ValueError("Invalid odds_type. Must be 'decimal', 'fractional', 'american', or 'implied_probability'.")
    elif isinstance(odds, pd.DataFrame):
        if odds_type == 'decimal':
            return odds.applymap(_decimal_odds_check).all().all()
        elif odds_type == 'fractional':
            return odds.applymap(_fractional_odds_check).all().all()
        elif odds_type == 'american':
            return odds.applymap(_american_odds_check).all().all()
        elif odds_type == 'implied_probability':
            return odds.applymap(_implied_probability_check).all().all()
        else:
            raise ValueError("Invalid odds_type. Must be 'decimal', 'fractional', 'american', or 'implied_probability'.")
    elif isinstance(odds, (int, float)):
        if odds_type == 'decimal':
            return _decimal_odds_check(odds)
        elif odds_type == 'fractional':
            return _fractional_odds_check(odds)
        elif odds_type == 'american':
            return _american_odds_check(odds)
        elif odds_type == 'implied_probability':
            return _implied_probability_check(odds)
        else:
            raise ValueError("Invalid odds_type. Must be 'decimal', 'fractional', 'american', or 'implied_probability'.")
    else:
        raise TypeError("Odds must be a pandas Series, DataFrame, or a number.")


def _american_odds_to_implied_probability(odds: float) -> float:
    """
    Convert American odds to implied probability. For Internal Use Only.
    
    Args:
        odds (float): The American odds to convert.
    
    Returns:
        float: The implied probability.
    """
    try:
        if odds >= 100:
            return 100 / (odds + 100)
        elif odds <= -100:
            return -odds / (-odds + 100)
        else:
            raise ValueError("American odds must be greater than or equal to 100 or less than or equal to -100.")
    except Exception:
        raise ValueError("Invalid American odds.")

    
def _decimal_odds_to_implied_probability(odds: float) -> float:
    """
    Convert decimal odds to implied probability. For Internal Use Only.
    
    Args:
        odds (float): The decimal odds to convert.
    
    Returns:
        float: The implied probability.
    """
    try:
        if odds >= 1:
            return 1 / odds
        else:
            raise ValueError("Decimal odds must be greater than or equal to 1.0")
    except Exception:
        raise ValueError("Invalid decimal odds.")

def _fractional_odds_to_implied_probability(odds: float) -> float:
    """
    Convert fractional odds to implied probability. For Internal Use Only.
    
    Args:
        odds (float): The fractional odds to convert.
    
    Returns:
        float: The implied probability.
    """
    try:
        if odds > 0:
            return 1 / (odds + 1)
        else:
            raise ValueError("Fractional odds must be greater than 0.")
    except Exception:
        raise ValueError("Invalid fractional odds.")
    
def _implied_probability_to_decimal_odds(probability: float) -> float:
    """
    Convert implied probability to decimal odds. For Internal Use Only.
    
    Args:
        probability (float): The implied probability to convert.
    
    Returns:
        float: The decimal odds.
    """
    try:
        if probability > 0 and probability < 1:
            return 1 / probability
        else:
            raise ValueError("Implied Probability must be between 0 and 1.")
    except Exception:
        raise ValueError("Invalid implied probability.")

def _implied_probability_to_fractional_odds(probability: float) -> float:
    """
    Convert implied probability to fractional odds. For Internal Use Only.
    
    Args:
        probability (float): The implied probability to convert.
    
    Returns:
        float: The fractional odds.
    """
    try:
        if probability > 0 and probability < 1:
            return (1 / probability) - 1
        else:
            raise ValueError("Implied Probability must be between 0 and 1.")
    except Exception:
        raise ValueError("Invalid implied probability.")
    
    
def _implied_probability_to_american_odds(probability: float) -> float:
    """
    Convert implied probability to American odds. For Internal Use Only.
    
    Args:
        probability (float): The implied probability to convert.
    
    Returns:
        float: The American odds.
    """
    try:
        if probability > 0 and probability < 1:
            if probability <= 0.5:
                return (100 / probability) - 100
            else:
                return (probability * 100) / (1 - probability) * -1
        else:
            raise ValueError("Implied Probability must be between 0 and 1.")
    except Exception:
        raise ValueError("Invalid implied probability.")
    
def _as_fraction(fractional_odds: float) -> str:
    """
    Convert a float representing fractional odds to a string representation. Private Function

    Args:
        odds (float): The fractional odds as a float.

    Returns:
        str: The fractional odds as a string.
    """
    if not _fractional_odds_check(fractional_odds):
        raise ValueError("Invalid fractional odds.")
    numerator = int(fractional_odds * 100)
    denominator = 100
    common_divisor = gcd(numerator, denominator)
    numerator //= common_divisor
    denominator //= common_divisor
    return f"{numerator}/{denominator}"

def _as_float(fraction: str) -> float:
    """
    Convert a string representing fractional odds to a float. Private Function

    Args:
        fraction (str): The fractional odds as a string (e.g., "3/2").

    Returns:
        float: The fractional odds as a float.
    """
    try:
        numerator, denominator = map(int, fraction.split('/'))
        return numerator / denominator
    except Exception:
        raise ValueError("Invalid fractional odds string format.")
    
def _kelly_criterion(stake: Union[float, int], odds: Union[float, int], true_probability: float, odds_type: str) -> float:
    """
    Calculate the Kelly Criterion for a given bet. For Internal Use Only.
    
    Args:
        odds (float): The odds of the bet.
        true_probability (float): The true probability of winning the bet.
        stake (float): The total stake available for betting.
        odds_type (str): The type of odds ('decimal', 'fractional', 'american').
    
    Returns:
        float: The optimal amount to stake according to the Kelly Criterion.
    """
    if not _odds_check(odds, odds_type):
        raise ValueError("Invalid odds.")
    if not _implied_probability_check(true_probability):
        raise ValueError("True probability must be between 0 and 1.")
    if stake <= 0:
        raise ValueError("Stake must be positive.")
    
    profit_per_dollar = _payout(odds, 1, odds_type) - 1

    kelly_fraction = true_probability - ((1 - true_probability) / profit_per_dollar)

    return max(0, kelly_fraction * stake)

"""
Public interface functions for pybet. Series or DataFrame Methods
"""

def implied_probability(odds: Union[pd.Series, pd.DataFrame], odds_type: str = "decimal") -> Union[pd.Series, pd.DataFrame]:
        """
        Calculate the implied probability from the odds.
        
        Returns:
            pd.Series or pd.DataFrame: A Series or DataFrame of implied probabilities.
        """
        if isinstance(odds, pd.Series):
            if odds_type == 'decimal':
                return odds.apply(lambda odd: _decimal_odds_to_implied_probability(odd))
            elif odds_type == 'fractional':
                return odds.apply(lambda odd: _fractional_odds_to_implied_probability(odd))
            elif odds_type == 'american':
                return odds.apply(lambda odd: _american_odds_to_implied_probability(odd))
            else:
                raise ValueError("Invalid odds_type. Must be 'decimal', 'fractional', or 'american'.")
        elif isinstance(odds, pd.DataFrame):
            if odds_type == 'decimal':
                return_df = odds.applymap(lambda odd: _decimal_odds_to_implied_probability(odd))
                suffix_to_add = "_implied_probability"
                return_df = return_df.add_suffix(suffix_to_add)
                return return_df
            elif odds_type == 'fractional':
                return_df = odds.applymap(lambda odd: _fractional_odds_to_implied_probability(odd))
                suffix_to_add = "_implied_probability"
                return_df = return_df.add_suffix(suffix_to_add)
                return return_df
            elif odds_type == 'american':
                return_df = odds.applymap(lambda odd: _american_odds_to_implied_probability(odd))
                suffix_to_add = "_implied_probability"
                return_df = return_df.add_suffix(suffix_to_add)
                return return_df
            else:
                raise ValueError("Invalid odds_type. Must be 'decimal', 'fractional', or 'american'.")

def odds(odds: Union[pd.Series, pd.DataFrame], odds_type: str = "decimal") -> Union[pd.Series, pd.DataFrame]:
    """
    Convert implied probability to the specified odds type.
    
    Args:
        odds_type (str): The type of odds to convert to ('decimal', 'fractional', 'american').
    
    Returns:
        pd.Series or pd.DataFrame: A Series or DataFrame of odds.
    """
    if isinstance(odds, pd.Series):
        if odds_type not in ['decimal', 'fractional', 'american']:
            raise ValueError("Invalid odds_type. Must be 'decimal', 'fractional', or 'american'.")
        elif odds_type == 'decimal':
            return odds.apply(lambda prob: _implied_probability_to_decimal_odds(prob))
        elif odds_type == 'fractional':
            return odds.apply(lambda prob: _implied_probability_to_fractional_odds(prob))
        elif odds_type == 'american':
            return odds.apply(lambda prob: _implied_probability_to_american_odds(prob))
    elif isinstance(odds, pd.DataFrame):
        if odds_type not in ['decimal', 'fractional', 'american']:
            raise ValueError("Invalid odds_type. Must be 'decimal', 'fractional', or 'american'.")
        elif odds_type == 'decimal':
            return_df = odds.applymap(lambda prob: _implied_probability_to_decimal_odds(prob))
            suffix_to_add = "_decimal_odds"
            return_df = return_df.add_suffix(suffix_to_add)
            return return_df
        elif odds_type == 'fractional':
            return_df = odds.applymap(lambda prob: _implied_probability_to_fractional_odds(prob))
            suffix_to_add = "_fractional_odds"
            return_df = return_df.add_suffix(suffix_to_add)
            return return_df
        elif odds_type == 'american':
            return_df = odds.applymap(lambda prob: _implied_probability_to_american_odds(prob))
            suffix_to_add = "_american_odds"
            return_df = return_df.add_suffix(suffix_to_add)
            return return_df

def convert(input: Union[pd.Series, pd.DataFrame], from_type: str, to_type: str) -> Union[pd.Series, pd.DataFrame]:
    """
    Convert odds or implied probability from one type to another.
    
    Args:
        input (pd.Series or pd.DataFrame): A series or DataFrame of odds or implied probabilities.
        from_type (str): The current type of odds ('decimal', 'fractional', 'american', 'implied_probability').
        to_type (str): The type of odds to convert to ('decimal', 'fractional', 'american', 'implied_probability').
    
    Returns:
        Series or DataFrame: A series or DataFrame of converted odds.
    """
    if isinstance(input, pd.Series):
        if _odds_check(input, from_type) is False:
            raise ValueError(f"Invalid odds in Series for type '{from_type}'.")
        if from_type not in ['decimal', 'fractional', 'american', 'implied_probability']:
            raise ValueError("Invalid from_type. Must be 'decimal', 'fractional', 'american', or 'implied_probability'.")
        if to_type not in ['decimal', 'fractional', 'american', 'implied_probability']:
            raise ValueError("Invalid to_type. Must be 'decimal', 'fractional', 'american', or 'implied_probability'.")
        if from_type == to_type:
            return input
        if from_type == 'implied_probability':
            implied_prob = input
        elif from_type in ['decimal', 'fractional', 'american']:
            implied_prob = input.implied_probability(from_type)
        if to_type == 'implied_probability':
            return implied_prob
        if to_type in ['decimal', 'fractional', 'american']:
            return implied_prob.odds(to_type)
    elif isinstance(input, pd.DataFrame):
        if from_type not in ['decimal', 'fractional', 'american', 'implied_probability']:
            raise ValueError("Invalid from_type. Must be 'decimal', 'fractional', 'american', or 'implied_probability'.")
        if to_type not in ['decimal', 'fractional', 'american', 'implied_probability']:
            raise ValueError("Invalid to_type. Must be 'decimal', 'fractional', 'american', or 'implied_probability'.")
        if from_type == to_type:
            return input
        if from_type == 'implied_probability':
            implied_prob = input
        elif from_type in ['decimal', 'fractional', 'american']:
            implied_prob = input.implied_probability(from_type)
        if to_type == 'implied_probability':
            return implied_prob
        if to_type in ['decimal', 'fractional', 'american']:
            return implied_prob.odds(to_type)
    else:
        raise TypeError("Input must be a pandas Series or DataFrame.")

def as_fraction(fractional_odds: pd.Series) -> pd.Series:
    """
    Convert a series of fractional odds from float to string representation.

    Args:
        fractional_odds (pd.Series): A series of fractional odds as floats.

    Returns:
        pd.Series: A series of fractional odds as strings.
    """
    return fractional_odds.apply(lambda x: _as_fraction(x))

def as_float(fraction: pd.Series) -> pd.Series:
    """
    Convert a series of fractional odds from string representation to float.

    Args:
        fraction (pd.Series): A series of fractional odds as strings.

    Returns:
        pd.Series: A series of fractional odds as floats.
    """
    return fraction.apply(lambda x: _as_float(x))

def overround(odds: Union[pd.Series, pd.DataFrame], odds_type: str = 'implied_probability') -> Union[float, pd.Series]:
    """
    Calculate the overround from the odds.
    
    Args:
        odds (pd.Series or pd.DataFrame): A pandas Series or DataFrame of odds or implied probabilities.
        odds_type (str): The type of odds ('decimal', 'fractional', 'american', or 'implied_probability').

    Returns:
        float: The overround.
    """
    if not isinstance(odds, (pd.Series, pd.DataFrame)):
        raise TypeError("Odds must be a pandas Series or DataFrame.")
    if not _odds_check(odds, odds_type):
        raise ValueError("Invalid input in Series.")
    if isinstance(odds, pd.Series):
        if odds_type == 'implied_probability':
            implied_probs = odds
        else:
            implied_probs = odds.implied_probability(odds_type)
        total_implied_prob = implied_probs.sum()
        return total_implied_prob - 1
    elif isinstance(odds, pd.DataFrame):
        if odds_type == 'implied_probability':
            implied_probs = odds
        else:
            implied_probs = odds.implied_probability(odds_type)
        total_implied_prob = implied_probs.apply(sum, axis=1)
        return total_implied_prob - 1

def vig(odds: Union[pd.Series, pd.DataFrame], odds_type: str = 'implied_probability') -> Union[float, pd.Series]:
    """
    Calculate the vig (vigorish) from the odds.
    
    Args:
        odds (Union[pd.Series, pd.DataFrame]): A series or DataFrame of odds.
        odds_type (str): The type of odds ('decimal', 'fractional', 'american', 'implied_probability').

    Returns:
        float: The vig.
    """
    if not isinstance(odds, pd.Series) and not isinstance(odds, pd.DataFrame):
        raise TypeError("Odds must be a pandas Series or DataFrame.")
    if not _odds_check(odds, odds_type):
        raise ValueError(f"Invalid odds in Series for type '{odds_type}'.")
    overround_value = overround(odds, odds_type)
    return (overround_value)/(overround_value + 1)

def devig(implied_probabilities: Union[pd.Series, pd.DataFrame]) -> Union[pd.Series, pd.DataFrame]:
    """
    Calculate the equal de-vigged odds from the implied probabilities.
    
    Args:
        implied_probabilities (Union[pd.Series, pd.DataFrame]): A series or DataFrame of implied probabilities.
    
    Returns:
        Series: A series of de-vigged .
    """
    if not isinstance(implied_probabilities, pd.Series) and not isinstance(implied_probabilities, pd.DataFrame):
        raise TypeError("Implied probabilities must be a pandas Series or DataFrame.")
    if not _odds_check(implied_probabilities, 'implied_probability'):
        raise ValueError("Invalid implied probabilities in Series.")

    if isinstance(implied_probabilities, pd.Series):
        overround_value = implied_probabilities.overround('implied_probability')
        equal_devigged_probs = implied_probabilities / (overround_value + 1)
        return equal_devigged_probs
    else:
        overround_value = implied_probabilities.overround('implied_probability')
        implied_probabilities["overround_value"] = overround_value
        deviged = implied_probabilities.apply(lambda row: row / (row["overround_value"] + 1), axis=1)
        return deviged.drop(columns=["overround_value"])

def arbitrage(odds: Union[pd.Series, pd.DataFrame], odds_type: str, bet_size: float) -> Union[pd.Series, pd.DataFrame]:
    """
    Check if there is an arbitrage opportunity given the odds. Return a ratio of bets to make for each outcome.

    Args:
        odds (Union[pd.Series, pd.DataFrame]): A series or DataFrame of odds.
        odds_type (str): The type of odds ('decimal', 'fractional', 'american').

    Returns:
        bool: True if there is an arbitrage opportunity, False otherwise.
    """
    if not isinstance(odds, (pd.Series, pd.DataFrame)):
        raise TypeError("Odds must be a pandas Series or DataFrame.")
    if not _odds_check(odds, odds_type):
        raise ValueError("Invalid odds in Series.")

    implied_probabilities = implied_probability(odds, odds_type)
    if isinstance(odds, pd.Series):
        if implied_probabilities < 1:
            return pd.Series(0, index=odds.index)
        # NEED TO FIGURE OUT THE MATHS
"""
Public interface functions for pybet. Not Series or DataFrame methods.
"""

def payout(stakes: Union[int, float, pd.Series], odds: Union[float, pd.Series], odds_type: str) -> Union[float, pd.Series]:
    """
    Calculate the potential payout for a given stake and odds.

    Args:
        stake (float): The amount of the stake.
        odds (float): The odds of the bet.
        odds_type (str): The type of odds ('decimal', 'fractional', 'american').

    Returns:
        float: The potential payout.
    """
    if not _odds_check(odds, odds_type):
        raise ValueError(f"Invalid odds for type '{odds_type}'.")
    if isinstance(stakes, float) or isinstance(stakes, int):
        if stakes <= 0:
            raise ValueError("Stakes must be positive.")
        return _payout(odds, stakes, odds_type)
    elif isinstance(stakes, pd.Series):
        if not (stakes > 0).all():
            raise ValueError("Stakes must be positive.")
        payout_df = pd.DataFrame({
            'stake': stakes,
            'odds': odds,
        })
        payout_series = payout_df.apply(lambda row: _payout(row['odds'], row['stake'], odds_type), axis=1)
        return payout_series
    else:
        raise TypeError("Stakes must be a pandas Series or a number.")

def profit(stake: Union[float, int, pd.Series], odds: Union[float, int, pd.Series], odds_type: str) -> Union[float, pd.Series]:
    """
    Calculates the profit from a bet given the stake, odds, and odds type.
    
    Args:
        stake (Union[float, int, pd.Series]): The amount of money wagered. Can be a single value or a pandas Series.
        odds (Union[float, int, pd.Series]): The odds for the bet. Can be a single value or a pandas Series.
        odds_type (str): The type of odds provided (e.g., 'decimal', 'fractional', 'american').
    
    Returns:
        Union[float, pd.Series]: The profit from the bet. Returns a float if inputs are scalars, or a pandas Series if inputs are Series.
    """
    payout_amount = payout(stake, odds, odds_type)
    return payout_amount - stake

def kelly_criterion(odds: Union[float, int, pd.Series], true_probability: Union[float, pd.Series], odds_type: str, bank_roll: float = 100.0, kelly_percentage: float = 1.0) -> Union[float, pd.Series]:
    """
    Calculate the Kelly Criterion for a series of bets

    Args:
        odds (Union[float, int, pd.Series]): The odds of the bet. Can be a single value or a pandas Series.
        true_probability (Union[float, pd.Series]): The true probability of winning the bet. Can be a single value or a pandas Series.
        odds_type (str): The type of odds ('decimal', 'fractional', 'american').
        bank_roll (float, optional): The current bankroll. Default is 100.0.
        kelly_percentage (float, optional): The fraction of the Kelly stake to use. Default is 1.0.

    Returns:
        Union[float, pd.Series]: The optimal stake(s) according to the Kelly Criterion.
    """
    if not isinstance(odds, (float, int, pd.Series)) or not isinstance(true_probability, (float, int, pd.Series)):
        raise TypeError("odds and true probability must be numeric scalar or pandas Series.")
    if (isinstance(odds, (float, int)) and not isinstance(true_probability, (float, int))) or (not isinstance(odds, (float, int)) and isinstance(true_probability, (float, int))):
        raise ValueError("Both odds and true_probability must be either scalars or pandas Series of the same length.")
    if isinstance(odds, (float, int)) and isinstance(true_probability, (float, int)):
        return _kelly_criterion(bank_roll, odds, true_probability, odds_type) * kelly_percentage
    elif isinstance(odds, pd.Series) and isinstance(true_probability, pd.Series):
        if len(odds) != len(true_probability):
            raise ValueError("Odds and true_probability Series must be of the same length.")
        kelly_df = pd.DataFrame({
            'odds': odds,
            'true_probability': true_probability
        })
        kelly_stakes = kelly_df.apply(lambda row: _kelly_criterion(bank_roll, row['odds'], row['true_probability'], odds_type) * kelly_percentage, axis=1)
        return kelly_stakes
    

"""
Converting interface functions to Pandas functions
"""

PandasObject.implied_probability = implied_probability
PandasObject.odds = odds
PandasObject.convert = convert
PandasObject.as_fraction = as_fraction
PandasObject.as_float = as_float
PandasObject.overround = overround
PandasObject.vig = vig
PandasObject.devig = devig
