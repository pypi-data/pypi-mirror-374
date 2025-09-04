# FinSenti

FinSenti is a comprehensive financial sentiment analysis library designed to help users analyze and interpret sentiment in financial texts.

It uses financial RoBERTa models to provide accurate sentiment analysis for financial news articles.

## Features
- **Financial Sentiment Analysis**: Analyze sentiment in financial texts using state-of-the-art RoBERTa models.
- **Compound Score Aggregation**: Aggregate sentiment scores to provide a comprehensive view of sentiment over time.

## Installation

```bash
pip install finsenti
```

## Usage

1. Preprocess your financial text data.

```python
import pandas as pd
from finsenti import finsenti_pipeline
# Input DataFrame df with a 'body' column and a list of tickers
df = pd.DataFrame({'body': ["The stock market is bullish today.", 
                             "Economic downturn expected next quarter.",
                            "Google's new product launch boosts investor confidence."]})
tickers = ['AAPL', 'GOOGL']
df = finsenti_pipeline(tickers=tickers, df=df,text_column='body', gemini_api_key='your_api_key', aggregate=True, aggregation_method='mean')
print(df.info())
```

## Dependencies
- pandas
- marketminer
- python-dotenv
- google-genai
- transformers
- torch
- hf_xet
- scipy

## License

MIT License. Free to use and modify.
