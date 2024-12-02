import os
import pandas as pd
import requests
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash.dash_table import DataTable
from textblob import TextBlob
import plotly.express as px
from pathlib import Path

# Dash app initialization
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Function to fetch news articles
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
        print(f"Error fetching news: {e}")
        return None

# Perform sentiment analysis
def perform_sentiment_analysis(text):
    """Perform sentiment analysis using TextBlob and return polarity."""
    blob = TextBlob(text)
    return blob.sentiment.polarity

# Update news CSV file with latest articles and sentiment analysis
def update_news_csv():
    """Update the CSV file with the latest news."""
    data_dir = Path(__file__).parent.joinpath("data")
    data_dir.mkdir(parents=True, exist_ok=True)  # Create directory if it doesn't exist
    fp = data_dir.joinpath("news_articles.csv")

    # If the CSV file does not exist, create it with appropriate headers
    if not os.path.exists(fp):
        df_empty = pd.DataFrame(columns=["Title", "Description", "PublishedAt", "Source", "Sentiment"])
        df_empty.to_csv(fp, index=False)

    # Fetch the latest news data
    news_data = fetch_news()
    if news_data:
        articles = news_data["articles"]
        news_records = []
        for article in articles:
            sentiment = perform_sentiment_analysis(article["description"] or article["title"])
            news_records.append({
                "Title": article["title"],
                "Description": article["description"],
                "PublishedAt": article["publishedAt"],
                "Source": article["source"]["name"],  # News source name
                "Sentiment": sentiment
            })

        # Write the articles to the CSV file
        df = pd.DataFrame(news_records)
        df.to_csv(fp, mode="w", index=False)

# Sidebar layout
sidebar = html.Div([
    html.H2("Dashboard", className="text-center"),
    html.Hr(),
    dbc.Nav([
        dbc.NavItem(dbc.NavLink("Home", href="#")),
        dbc.NavItem(dbc.NavLink("News", href="#news-section")),
        dbc.NavItem(dbc.NavLink("Sentiment Analysis", href="#sentiment-section")),
        dbc.NavItem(dbc.NavLink("About", href="#about-section")),
        dbc.NavItem(dbc.NavLink("Help", href="#help-section")),
    ], vertical=True, pills=True),
], style={
    'position': 'fixed',
    'top': '0',
    'left': '0',
    'width': '250px',
    'padding': '20px',
    'background-color': '#f8f9fa',
    'height': '100%',
    'border-right': '1px solid #ccc'
})

# Main content layout
content = html.Div([
    html.Div([
        dbc.Row([
            dbc.Col([
                html.H3("Sentiment Analysis by News Source"),
                dcc.Graph(id="sentiment-boxplot"),
            ], width=12)
        ]),
        dbc.Row([
            dbc.Col([
                html.H3("News Table"),
                DataTable(
                    id="news-table",
                    columns=[
                        {"name": "Title", "id": "Title"},
                        {"name": "Description", "id": "Description"},
                        {"name": "PublishedAt", "id": "PublishedAt"},
                        {"name": "Source", "id": "Source"},
                        {"name": "Sentiment", "id": "Sentiment"},
                        {"name": "URL", "id": "URL", "presentation": "markdown"},
                    ],
                    style_table={"height": "400px", "overflowY": "auto"},
                    style_header={"backgroundColor": "rgb(230, 230, 230)", "fontWeight": "bold"},
                    style_cell={"textAlign": "left", "padding": "5px"},
                ),
            ], width=12)
        ])
    ])
], style={
    'margin-left': '270px',
    'padding': '20px'
})

# Define the layout of the app (combining the sidebar and content)
app.layout = html.Div([
    sidebar, 
    content
])

# Callback to update the news data and plot sentiment by source
@app.callback(
    [Output("news-table", "data"),
     Output("sentiment-boxplot", "figure")],
    Input("news-table", "data"),
)
def update_news_display(n_clicks):
    """Update the display with the latest news articles and plot sentiment."""
    # Update news CSV with the latest news
    update_news_csv()

    # Read the data from the CSV
    data_dir = Path(__file__).parent.joinpath("data")
    fp = data_dir.joinpath("news_articles.csv")
    df = pd.read_csv(fp)
    
    # Prepare data for table and sentiment box plot
    table_data = df.to_dict(orient="records")
    
    # Create sentiment box plot by source
    fig = px.box(df, x="Source", y="Sentiment", color="Source", 
                 title="Sentiment Distribution by News Source",
                 labels={"Source": "News Source", "Sentiment": "Sentiment Score"})
    fig.update_layout(xaxis_title="News Source", yaxis_title="Sentiment Score")
    
    return table_data, fig

# Run the app
def start_app():
    """Start the app."""
    app.run_server(debug=True, port=8050)

if __name__ == "__main__":
    start_app()
