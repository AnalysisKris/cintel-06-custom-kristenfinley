import os
from dotenv import load_dotenv
from newsapi import NewsApiClient

# Load environment variables from the .env file
load_dotenv()

# Get the API key from the environment variable
API_KEY = os.getenv('NEWS_API_KEY')

# Ensure the API key is loaded correctly
if not API_KEY:
    raise ValueError("API key not found. Please make sure the '.env' file is set up correctly.")

# Initialize NewsAPI client with the API key
newsapi = NewsApiClient(api_key=API_KEY)

# Function to fetch top headlines
def fetch_top_headlines():
    try:
        top_headlines = newsapi.get_top_headlines(language='en', country='us')
        
        if top_headlines['status'] == 'ok':
            articles = top_headlines['articles']
            headlines = []
            
            for article in articles:
                headline = {
                    'title': article['title'],
                    'description': article['description'],
                    'url': article['url'],
                    'published_at': article['publishedAt'],
                    'source': article['source']['name']
                }
                headlines.append(headline)
                
            return headlines
        else:
            print("Error fetching top headlines:", top_headlines['message'])
            return []
    except Exception as e:
        print(f"An error occurred while fetching top headlines: {e}")
        return []

# Function to fetch news based on a specific query
def fetch_news_by_query(query):
    try:
        news = newsapi.get_everything(q=query, language='en', sort_by='relevancy', page_size=10)
        
        if news['status'] == 'ok':
            articles = news['articles']
            news_data = []
            
            for article in articles:
                article_data = {
                    'title': article['title'],
                    'description': article['description'],
                    'url': article['url'],
                    'published_at': article['publishedAt'],
                    'source': article['source']['name']
                }
                news_data.append(article_data)
            
            return news_data
        else:
            print("Error fetching news by query:", news['message'])
            return []
    except Exception as e:
        print(f"An error occurred while fetching news by query: {e}")
        return []

# Function to fetch news by category (e.g., 'business', 'technology', etc.)
def fetch_news_by_category(category):
    try:
        category_news = newsapi.get_top_headlines(category=category, language='en', country='us')
        
        if category_news['status'] == 'ok':
            articles = category_news['articles']
            category_data = []
            
            for article in articles:
                article_info = {
                    'title': article['title'],
                    'description': article['description'],
                    'url': article['url'],
                    'published_at': article['publishedAt'],
                    'source': article['source']['name']
                }
                category_data.append(article_info)
                
            return category_data
        else:
            print(f"Error fetching news for category {category}: {category_news['message']}")
            return []
    except Exception as e:
        print(f"An error occurred while fetching news for category {category}: {e}")
        return []

# Example usage of the functions
if __name__ == "__main__":
    # Fetching top headlines
    headlines = fetch_top_headlines()
    print("Top Headlines:")
    for headline in headlines:
        print(f"- {headline['title']} ({headline['source']})")

    # Fetching news by query
    query_news = fetch_news_by_query('technology')
    print("\nNews about Technology:")
    for article in query_news:
        print(f"- {article['title']} ({article['source']})")

    # Fetching news by category
    business_news = fetch_news_by_category('business')
    print("\nBusiness News:")
    for article in business_news:
        print(f"- {article['title']} ({article['source']})")