from collections import deque
from datetime import datetime, timedelta
import random

# Libraries for data manipulation and analysis
import pandas as pd

# Visualization libraries
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import plotly.express as px

# Shiny for building web applications
from shiny import reactive
from shiny.express import input, render, ui
from shinywidgets import render_plotly

# Sentiment analysis library
from textblob import TextBlob  # For sentiment analysis

# ## Constants
UPDATE_INTERVAL_SECS: int = 5
DEQUE_SIZE: int = 20  # Limit the deque to the last 20 entries

# ## Reactive Value with Deque
reactive_deque = reactive.Value(deque(maxlen=DEQUE_SIZE))

# ## Helper Function for Sentiment Analysis
def get_sentiment(text: str) -> str:
    sentiment = TextBlob(text).sentiment.polarity
    if sentiment > 0.1:
        return 'Positive'
    elif sentiment < -0.1:
        return 'Negative'
    else:
        return 'Neutral'

# ## Reactive Calculation for Misinformation Data
@reactive.calc()
def reactive_misinformation_data():
    # Triggers recalculation after a specific interval
    reactive.invalidate_later(UPDATE_INTERVAL_SECS)

    # Generate random misinformation data
    story_type = random.choice(["Verified", "Misleading"])
    story_count = random.randint(1, 10)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    media_outlet = random.choice(["News Network A", "News Network B", "Blog C"])
    story_category = random.choice(["Politics", "Health", "Tech", "Entertainment"])

    # Enrich the data with sentiment analysis and source credibility
    sentiment = get_sentiment(f"{story_type} story about {story_category}")
    source_credibility = random.choice([0.8, 0.9, 1.0]) if story_type == "Verified" else random.choice([0.3, 0.4, 0.5])

    # Create a new entry for the deque
    new_entry = {
        "story_type": story_type,
        "story_count": story_count,
        "timestamp": timestamp,
        "media_outlet": media_outlet,
        "story_category": story_category,
        "sentiment": sentiment,
        "source_credibility": source_credibility,
    }

    # Append the new entry to the reactive deque
    reactive_deque.get().append(new_entry)

    # Snapshot of the current deque for further processing
    deque_snapshot = reactive_deque.get()

    # Convert the deque to a Pandas DataFrame
    df = pd.DataFrame(deque_snapshot)

    # Ensure timestamp is converted to datetime
    if not df.empty and "timestamp" in df:
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Return multiple outputs for use in UI components
    return deque_snapshot, df, new_entry

# ## UI Definition
ui.page_opts(title="Misinformation Tracker", fillable=True)

with ui.sidebar():
    ui.h2("Misinformation Dashboard")
    ui.p("Live updates of misinformation data.", class_="text-center")
    ui.h4("Filter Data")
    ui.input_checkbox("filter_verified", "Include Verified Stories", value=True)
    ui.input_checkbox("filter_misleading", "Include Misleading Stories", value=True)
    ui.input_checkbox("filter_politics", "Include Politics Stories", value=True)
    ui.input_checkbox("filter_health", "Include Health Stories", value=True)
    ui.input_checkbox("filter_tech", "Include Tech Stories", value=True)
    ui.input_checkbox("filter_entertainment", "Include Entertainment Stories", value=True)
    ui.hr()
    ui.tags.div(
        ui.a(
            "GitHub Code Repository - KF",
            href="https://github.com/AnalysisKris/cintel-05-cintel-kristenfinley",
            target="_blank",
        ),
        style="font-size: 12px;"
    )

with ui.layout_columns():
    
    # Misinformation by Category box with the ⚠️ icon
    with ui.value_box(showcase="⚠️", theme="bg-gradient-blue-red"):
        ui.h4("Misinformation by Category")
        @render.text
        def misinformation_by_category():
            deque_snapshot, _, _ = reactive_misinformation_data()
            category_count = {category: 0 for category in ["Politics", "Health", "Tech", "Entertainment"]}
            for entry in deque_snapshot:
                if entry['story_type'] == 'Misleading':
                    category_count[entry['story_category']] += 1
            category_str = " | ".join([f"{category}: {count}" for category, count in category_count.items()])
            return category_str
        
    with ui.card(full_screen=True, height="400px", width="auto"):
        ui.card_header("Recent Stories")

        @render.data_frame
        def recent_stories():
            _, df, _ = reactive_misinformation_data()
            return df

with ui.layout_columns():
    with ui.navset_card_tab(id="plot_tabs"):
        # Tab for Story Trends
        with ui.nav_panel("Story Trends"):
            @render_plotly
            def story_trends():
                _, df, _ = reactive_misinformation_data()
                if not df.empty:
                    fig = px.bar(
                        df,
                        x="timestamp",
                        y="story_count",
                        color="story_type",
                        barmode="group",
                        title="Story Count Trends",
                        labels={"story_count": "Count", "timestamp": "Time"},
                        hover_data=["sentiment", "source_credibility"]
                    )
                    return fig

        # Tab for Scatter Plot
        with ui.nav_panel("Story Count vs Time"):
            @render_plotly
            def story_scatter():
                _, df, _ = reactive_misinformation_data()
                if not df.empty:
                    fig = px.scatter(
                        df,
                        x="timestamp",
                        y="story_count",
                        color="story_type",
                        title="Story Count vs Time",
                        labels={"story_count": "Story Count", "timestamp": "Time"},
                        hover_data=["story_category", "media_outlet", "sentiment", "source_credibility"]
                    )
                    return fig

        # New Tab for Story Count Heatmap
        with ui.nav_panel("Story Count Heatmap"):
            @render.plot
            def story_heatmap():
                _, df, _ = reactive_misinformation_data()
                if not df.empty:
                    heatmap_data = df.pivot_table(
                        index="story_category",
                        columns="story_type",
                        values="story_count",
                        aggfunc="sum",
                        fill_value=0
                    )
                    fig = Figure(figsize=(14, 8))
                    ax = fig.add_subplot(111)
                    sns.heatmap(
                        heatmap_data,
                        annot=True,
                        cmap="Blues",
                        linewidths=0.5,
                        cbar_kws={'label': 'Story Count'},
                        ax=ax
                    )
                    ax.set_title("Story Count Heatmap: Category vs Type")
                    fig.tight_layout()
                    return fig

        # New Tab for Story Count Forecasting
        with ui.nav_panel("Story Count Forecasting"):
            @render_plotly
            def story_forecasting():
                _, df, _ = reactive_misinformation_data()
                if not df.empty:
                    # Assuming forecast_data and the logic for forecasting exist
                    forecast_data = df.copy()  # Replace with actual forecasting logic
                    forecast_data["forecast"] = forecast_data["story_count"].rolling(window=5).mean()  # Example forecast
                    fig = px.line(
                        forecast_data,
                        x="timestamp",
                        y=["story_count", "forecast"],
                        labels={"value": "Count", "timestamp": "Time"},
                        title="Story Count Forecasting",
                        color_discrete_map={"story_count": "blue", "forecast": "red"}
                    )
                    fig.update_traces(mode="lines+markers")
                    return fig