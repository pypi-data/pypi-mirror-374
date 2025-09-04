"""
Module for sentiment analysis of news articles.
"""

import pandas as pd
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import re
import math
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("soleimanian/financial-roberta-large-sentiment")
model = AutoModelForSequenceClassification.from_pretrained("soleimanian/financial-roberta-large-sentiment")

sentiment_labels = ["neutral", "positive", "negative"]

def chunk_text(text: str, max_tokens: int = 512) -> list:
    """
    Chunk text into smaller segments to fit model input size.

    Parameters:
    text (str): The text to be chunked.
    max_tokens (int): Maximum number of tokens per chunk.

    Returns:
    list: List of text chunks.
    """

    if not text or not text.strip():
        return []

    tokens = tokenizer.tokenize(text)
    chunks = []
    for i in range(0, len(tokens), max_tokens):
        chunk = tokenizer.convert_tokens_to_string(tokens[i:i + max_tokens])
        chunks.append(chunk)
    return chunks

def num_tokens(text: str) -> int:
    """
    Calculate the number of tokens in the given text.

    Parameters:
    text (str): The text to be tokenized.

    Returns:
    int: Number of tokens.
    """
    if not text or not text.strip():
        return 0
    tokens = tokenizer.tokenize(text)
    return len(tokens)

def predict_sentiment(text: str) -> float:
    """
    Predict sentiment of the given text.

    Parameters:
    text (str): The text for sentiment analysis.

    Returns:
    float: Compound sentiment score ranging from -5 (most negative) to +5 (most positive).
    """

    if not text or not text.strip():
        return "neutral", 0.0

    chunks = chunk_text(text)
    # Calculate number of tokens for each chunk
    token_counts = [max(1, num_tokens(c)) for c in chunks]
    prob_list = []
    for chunk in chunks:
        inputs = tokenizer(chunk, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            if logits.device.type != "cpu":
                logits = logits.detach().cpu()

            probs = torch.softmax(logits, dim=-1).numpy()[0]
            prob_list.append(probs.tolist())

    # Calculate weighted average of probabilities based on token counts
    token_counts = np.asarray(token_counts, dtype=np.float64)
    prob_arr = np.asarray(prob_list, dtype=np.float64)

    total = token_counts.sum()
    if total <= 0:
        weights = np.full_like(token_counts, 1.0 / len(token_counts))
    else:
        weights = token_counts / total

    weighted_probs = (prob_arr * weights[:, None]).sum(axis=0)

    clip = 5.0
    eps = 1e-9
    probs = np.asarray(weighted_probs, dtype=float)
    probs /= probs.sum() + eps

    id2label = model.config.id2label
    label_map = {v.lower(): k for k, v in id2label.items()}

    P_pos = probs[label_map.get("positive", 0)]
    P_neg = probs[label_map.get("negative", 1)]
    P_neu = probs[label_map.get("neutral", 2)]

    logodds = math.log((P_pos + eps) / (P_neg + eps))
    compound = (1 - P_neu) * logodds
    compound = max(-clip, min(clip, compound))

    return compound

def enhance_ticker_specific_sentiment(text: str, tickers: list, compound : float|int) -> float:
    """
    Enhance sentiment analysis by focusing on specific stock tickers.
    We already have the general sentiment and confidence from the main text analysis.

    Parameters:
    text (str): The text for sentiment analysis.
    tickers (list): List of stock tickers to focus on.
    compound (float|int): The initial compound sentiment score.

    Returns:
    float: Enhanced compound score.
    """
    mentions = 0

    text_lc = text.lower()

    for ticker in tickers:
        pattern = r'\b' + re.escape(ticker.lower()) + r'\b'
        mentions += len(re.findall(pattern, text_lc))

    if mentions == 0:
        return compound

    if abs(compound) > 0.5:
        multiplier = 1 + 0.3 * math.log1p(mentions)
        compound *= multiplier

    return compound

def sentiment_pipeline(df: pd.DataFrame, tickers: list, text_column: str = 'body') -> pd.DataFrame:
    """
    Apply sentiment analysis pipeline to a DataFrame.

    Parameters:
    df (pd.DataFrame): DataFrame containing the text data.
    tickers (list): List of stock tickers to focus on.
    text_column (str): Name of the column containing text data.

    Returns:
    pd.DataFrame: DataFrame with added sentiment scores.
    """

    logger.info(f"Applying sentiment analysis on column '{text_column}'")

    df = df.copy()
    df['compound'] = df[text_column].apply(predict_sentiment)
    df['enhanced_compound'] = df.apply(lambda row: enhance_ticker_specific_sentiment(row[text_column], tickers, row['compound']), axis=1)
    # Drop compound column
    df = df.drop(columns=['compound'])
    # Rename enhanced_compound to compound
    df = df.rename(columns={'enhanced_compound': 'compound'})

    logger.info("Sentiment analysis completed.")

    return df




