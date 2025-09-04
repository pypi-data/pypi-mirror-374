"""
Module to integrate the entire sentiment analysis pipeline.
"""

import pandas as pd
from .collection import collect_news
from .preprocessing import preprocessing_pipeline
from .sentiment import sentiment_pipeline
from .aggregation import aggregate_sentiment
from datetime import datetime, date

def finsenti_pipeline(tickers: list, df: pd.DataFrame=None, text_column: str='body', gemini_api_key: str=None, collect_new: bool=False, start_date: str|datetime|date=None, end_date: str|datetime|date=None, aggregation_method: str='weighted_mean', sentiment_col: str='compound') -> pd.DataFrame:
    """
    Complete sentiment analysis pipeline.

    Parameters:
    tickers (list): List of stock tickers to focus on.
    df (pd.DataFrame, optional): DataFrame containing the text data. If None and collect_new is True, news will be collected.
    text_column (str): Name of the column containing text data.
    gemini_api_key (str, optional): API key for Gemini if news collection is needed.
    collect_new (bool): Whether to collect new news data.
    start_date (str|datetime|date, optional): Start date for news collection if collect_new is True.
    end_date (str|datetime|date): End date for news collection if collect_new is True.
    aggregation_method (str): Method for aggregating sentiment scores.
    sentiment_col (str): Column name containing sentiment scores. Default is 'compound'.

    Returns:
    pd.DataFrame: DataFrame with sentiment scores, aggregated if specified.
    """

    if collect_new:
        df = collect_news(start=start_date, end=end_date)

    df, tickers = preprocessing_pipeline(data=df, tickers=tickers, gemini_api_key=gemini_api_key, text_column=text_column)
    df = sentiment_pipeline(df=df, tickers=tickers, text_column=text_column)

    if aggregation_method is not None:
        df = aggregate_sentiment(df=df, method=aggregation_method, sentiment_col=sentiment_col)

    return df

