'''
Module for preprocessing news data for sentiment analysis.
'''

import pandas as pd
from google import genai
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_data(file_path):
    """
    Load news data from a CSV file.

    Parameters:
    file_path (str): Path to the CSV file.

    Returns:
    pd.DataFrame: DataFrame containing the news data.
    """
    logger.info(f"Loading data from {file_path}")
    return pd.read_csv(file_path, index_col=0)

def filter_data(df, text_column='body', word_count_threshold=5):
    """
    Filter out articles with fewer than a specified number of words.

    Parameters:
    df (pd.DataFrame): DataFrame containing the news data.
    text_column (str): Name of the column containing text data.
    word_count_threshold (int): Minimum number of words required to keep an article.

    Returns:
    pd.DataFrame: Filtered DataFrame.
    """
    logger.info(f"Filtering articles with fewer than {word_count_threshold} words in column '{text_column}'")
    df['word_count'] = df[text_column].apply(lambda x: len(str(x).split()))
    return df[df['word_count'] >= word_count_threshold].drop(columns=['word_count'])

def clean_data(df, text_column='body'):
    """
    Clean the news data for financial RoBERTa model.
    Expected cleaning steps:
    - Removing extra whitespace
    - Normalize Unicode characters
    Parameters:
    df (pd.DataFrame): DataFrame containing the news data.
    Returns:
    pd.DataFrame: Cleaned DataFrame.
    """
    logger.info(f"Cleaning data in column '{text_column}'")
    df[text_column] = df[text_column].str.replace(r'\s+', ' ', regex=True).str.strip()
    df[text_column] = df[text_column].apply(lambda x: x.encode('utf-8', 'ignore').decode('utf-8', 'ignore'))
    return df

def custom_ticker_aliases(tickers: list, gemini_api_key: str) -> list:
    '''
    Custom function to process tickers using Gemini API.
    Gemini will be used to get all known aliases for a given ticker.
    For example, AAPL will return ['AAPL', 'Apple Inc', 'Apple', 'Apple Corporation']
    This will help in identifying mentions of the company in the news articles.

    Parameters:
    tickers (list): List of ticker symbols.
    gemini_api_key (str): API key for Gemini.
    Returns:
    list: List of ticker symbols with their aliases.
    '''
    names = []
    client = genai.Client(api_key=gemini_api_key)
    for ticker in tickers:
        prompt = f"""Return only a Python list of aliases for ticker '{ticker}'. Include:
- The ticker symbol itself
- Full company name
- Common abbreviations
- Alternative corporate forms
- Any other known aliases

Also try to include all possible variations and common misspellings.

Return ONLY the list, no explanation, no markdown, just the list. Example format: ['AAPL', 'Apple Inc', 'Apple', 'Apple Corporation']"""

        response = client.models.generate_content(
            model = "gemini-2.5-pro",
            contents = prompt
        )
        text = response.text or ""
        try:
            alias_list = eval(text) if text.strip().startswith("[") else json.loads(text)
            if not isinstance(alias_list, list):
                raise ValueError("Not a list")
        except Exception:
            # fallback: split by commas if parsing fails
            alias_list = [alias.strip().strip('"').strip("'") for alias in text.strip("[]").split(",") if alias.strip()]

        names.extend([ticker]+alias_list)

    unique_names = list(set(names))

    # Remove unnecessary characters like `, python, \n, [, ]
    unique_names = [name.replace('`', '').replace('\n', '').replace('python','').replace('[', '').replace(']', '').strip() for name in unique_names if name]

    logger.info(f"Generated aliases for tickers: {unique_names}")

    return unique_names

def preprocessing_pipeline(data, text_column='body', word_count_threshold=5, gemini_api_key=None, tickers=None):
    """
    Complete preprocessing pipeline for news data.

    Parameters:
    data (str or pd.DataFrame): File path to the CSV file or a DataFrame.
    text_column (str): Name of the column containing text data.
    word_count_threshold (int): Minimum number of words required to keep an article.
    gemini_api_key (str): API key for Gemini (optional).
    tickers (list): List of ticker symbols (optional).

    Returns:
    pd.DataFrame: Preprocessed DataFrame.
    list: List of ticker symbols with their aliases (if tickers and gemini_api_key are provided).
    """

    # Load data if a file path is provided, otherwise assume data is already a DataFrame
    if isinstance(data, str):
        df = load_data(data)
    elif isinstance(data, pd.DataFrame):
        df = data
    else:
        raise ValueError("data must be a file path or a pandas DataFrame")

    df = filter_data(df, text_column, word_count_threshold)
    df = clean_data(df, text_column)

    ticker_aliases = None
    if gemini_api_key and tickers:
        ticker_aliases = custom_ticker_aliases(tickers, gemini_api_key)

    return df, ticker_aliases

