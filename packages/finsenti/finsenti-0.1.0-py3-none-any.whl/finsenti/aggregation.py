"""
Module for aggregating sentiment analysis results.
"""

import pandas as pd
import numpy as np
import logging
from scipy.stats import trim_mean

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def aggregate_sentiment(df: pd.DataFrame, method: str, sentiment_col:str ='compound') -> pd.DataFrame:
    '''
    Aggregate sentiment scores using the specified method.
    Index the DataFrame by date before aggregation.

    Parameters:
    df (pd.DataFrame): DataFrame containing sentiment scores.
    method (str): Aggregation method ('mean', 'weighted_mean', 'max', 'min', 'trimmed_mean', 'ratio').
    sentiment_col (str): Column name containing sentiment scores. Default is 'compound'.
    Returns:
    pd.DataFrame: DataFrame with aggregated sentiment scores.
    '''

    if sentiment_col not in df.columns:
        raise ValueError(f"Sentiment column '{sentiment_col}' not found in DataFrame.")

    logger.info(f"Aggregating sentiment using method: {method}")

    # Check if index is datetime
    if not pd.api.types.is_datetime64_any_dtype(df.index):
        raise ValueError("DataFrame index must be of datetime type for aggregation.")

    if method == 'mean':
        agg = df.groupby(df.index.date)[sentiment_col].mean()
    elif method == 'weighted_mean':
        # Temp fix: use word count as weights if 'body' column exists
        df['word_count'] = df['body'].apply(lambda x: len(str(x).split()))
        agg = df.groupby(df.index.date).apply(lambda g: np.average(g[sentiment_col], weights=g['word_count']))
    elif method == 'max':
        agg = df.groupby(df.index.date)[sentiment_col].max()
    elif method == 'min':
        agg = df.groupby(df.index.date)[sentiment_col].min()
    elif method == 'trimmed_mean':
        agg = df.groupby(df.index.date)[sentiment_col].apply(lambda x: trim_mean(x, 0.1))  # trims 10%
    elif method == 'ratio':
        agg = df.groupby(df.index.date).apply(
            lambda g: (g[sentiment_col].gt(0).sum() - g[sentiment_col].lt(0).sum()) / len(g)
        )
    else:
        raise ValueError(f"Unsupported aggregation method: {method}")

    result = agg.rename('sentiment_score').to_frame()
    result = result.dropna(subset=['sentiment_score'])

    logger.info("Aggregation complete.")

    return result