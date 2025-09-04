"""
Module for running user scripts.
"""

from finsenti import collection, preprocessing, sentiment, aggregation, pipeline
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()

if __name__ == "__main__":
    tickers = ['RELIANCE']
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    collect_new = True
    start_date = "2023-01-01"
    end_date = "2023-01-05"
    aggregation_method = "weighted_mean"
    df = pipeline.finsenti_pipeline(tickers=tickers, df=None, text_column='body', gemini_api_key=gemini_api_key, collect_new=collect_new, start_date=start_date, end_date=end_date, aggregation_method=aggregation_method, sentiment_col='compound')
    print(df)
