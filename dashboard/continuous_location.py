import os
import pandas as pd
from datetime import datetime
from pathlib import Path
import logging
import requests
from dashboard.util_logger import setup_logger

# Set up a file logger
logger, log_filename = setup_logger(__file__)

# Function to fetch news articles using the News API
def fetch_news():
    """Fetch the latest news articles."""
    api_key = "baf07ae095da49a8aba279628fcc43d4"  # News API key
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        news_data = response.json()
        return news_data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching news: {e}")
        return None

def update_news_csv():
    """Update the CSV file with the latest news."""
    logger.info("Calling update_news_csv")
    try:
        # Define the CSV file path
        data_dir = Path(__file__).parent.joinpath("data")
        data_dir.mkdir(parents=True, exist_ok=True)  # Create the directory if it doesn't exist
        
        fp = data_dir.joinpath("news_articles.csv")

        # Check if the file exists, if not, create it with the column headings
        if not os.path.exists(fp):
            df_empty = pd.DataFrame(columns=["Title", "Description", "PublishedAt", "URL"])
            df_empty.to_csv(fp, index=False)

        logger.info(f"Initialized CSV file at {fp}")

        # Fetch the news and write to CSV
        news_data = fetch_news()
        if news_data:
            articles = news_data["articles"]
            news_records = [
                {
                    "Title": article["title"],
                    "Description": article["description"],
                    "PublishedAt": article["publishedAt"],
                    "URL": article["url"]
                }
                for article in articles
            ]

            # Write articles to the CSV file
            df = pd.DataFrame(news_records)
            df.to_csv(fp, mode="w", index=False)
            logger.info(f"Saved {len(news_records)} articles to {fp}")
        else:
            logger.error("No news data to save.")
    except Exception as e:
        logger.error(f"ERROR in update_news_csv: {e}")
