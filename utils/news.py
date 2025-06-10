from textblob import TextBlob
from nltk.corpus import stopwords
from datetime import datetime, timedelta
import requests
import pandas as pd
import ssl
import nltk

nltk.download('stopwords')
api_key = 'f5fe5390fbb64c64883b26acdcadc8dc'
base_url = 'https://newsapi.org/v2/everything'

def fetch_and_generate_signal():
    def preprocess_text(text):
        text = text.lower()
        text = ''.join([c for c in text if c.isalpha() or c.isspace()])
        tokens = [word for word in text.split() if word not in stopwords.words('english')]
        return ' '.join(tokens)

    def analyze_sentiment(text):
        return TextBlob(text).sentiment.polarity

    try:
        from_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        to_date = datetime.now().strftime('%Y-%m-%d')

        params = {
            'q': 'BTCUSDT OR Bitcoin AND USDT',
            'from': from_date,
            'to': to_date,
            'language': 'en',
            'apiKey': api_key,
            'pageSize': 100
        }

        response = requests.get(base_url, params=params)
        data = response.json()
        if data['status'] != 'ok':
            return "Error"

        df = pd.DataFrame(data['articles'])
        df['clean'] = df['description'].fillna('').apply(preprocess_text)
        df['sentiment'] = df['clean'].apply(analyze_sentiment)
        avg = df['sentiment'].mean()

        if avg > 0.1:
            return "BUY"
        elif avg < -0.1:
            return "SELL"
        else:
            return "HOLD"
    except Exception as e:
        return "Error"