"""
Module for collecting news articles using the marketminer package.
"""

from marketminer import scrape_economic_times

def collect_news(start, end):
    """
    Collect news articles from The Economic Times between the specified start and end dates.

    Parameters:
    start (str): The start date in 'YYYY-MM-DD' format.
    end (str): The end date in 'YYYY-MM-DD' format.

    Returns:
    pd.DataFrame: A DataFrame containing the collected news articles.
    Saves the DataFrame to 'news_data.csv'.
    """
    df = scrape_economic_times(start, end)
    df.to_csv("news_data.csv")
    return df