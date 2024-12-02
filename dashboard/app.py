import os
import pandas as pd
from datetime import datetime
from pathlib import Path
import logging
import requests
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash.dash_table import DataTable
from dashboard.util_logger import setup_logger
from dashboard.fetch import fetch_news_by_query

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

# Dash app initialization
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Sidebar layout
sidebar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="#")),
        dbc.NavItem(dbc.NavLink("News", href="#")),
        dbc.NavItem(dbc.NavLink("About", href="#")),
    ],
    brand="News Dashboard",
    brand_href="#",
    color="primary",
    dark=True,
)

# Define the layout of the app (what gets rendered on the web page)
app.layout = html.Div([
    sidebar,
    dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H3("Latest News Articles"),
                html.Div(id="news-output"),
                html.Button("Update News", id="update-button", n_clicks=0),
            ], width=9),
            dbc.Col([
                html.H3("News Table"),
                DataTable(
                    id="news-table",
                    columns=[
                        {"name": "Title", "id": "Title"},
                        {"name": "Description", "id": "Description"},
                        {"name": "PublishedAt", "id": "PublishedAt"},
                        {"name": "URL", "id": "URL", "presentation": "markdown"},
                    ],
                    style_table={"height": "400px", "overflowY": "auto"},
                    style_header={"backgroundColor": "rgb(230, 230, 230)", "fontWeight": "bold"},
                    style_cell={"textAlign": "left", "padding": "5px"},
                ),
            ], width=3)
        ]),
    ], fluid=True)
])

# Callback to update news data and display it in a table
@app.callback(
    [Output("news-output", "children"),
     Output("news-table", "data")],
    Input("update-button", "n_clicks")
)
def update_news_display(n_clicks):
    """Update the display with the latest news articles."""
    if n_clicks > 0:
        update_news_csv()
        data_dir = Path(__file__).parent.joinpath("data")
        fp = data_dir.joinpath("news_articles.csv")
        if os.path.exists(fp):
            df = pd.read_csv(fp)
            articles = df.to_dict(orient="records")
            table_data = articles  # Use articles data for the table
            return html.Ul([html.Li(f"{article['Title']}: {article['Description']}") for article in articles]), table_data
        else:
            return "No articles found.", []
    return "Click the button to update the news.", []

# Function to start the app
def start_app():
    """Start the app and call update_news_csv to update the news data."""
    logger.info("Starting the app...")
    update_news_csv()  # Update CSV initially
    app.run_server(debug=True, port=8050)  # Run the Dash server

if __name__ == "__main__":
    start_app()
