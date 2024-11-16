#import packages
import matplotlib.pyplot as plt
import plotly.graph_objs as go
import appdirs as ad
import pandas as pd
import math
from pathlib import Path
# Specify title and logo for the webpage.
# Set up your web app
import streamlit as st
import sqlite3
import yfinance as yf
import datetime
from datetime import date, timedelta
from datetime import datetime
ad.user_cache_dir = lambda *args: "/tmp"
#Specify title and logo for the webpage.
st.set_page_config(
    page_title="Stock Price App",
    page_icon="chart_with_upwards_trend",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items=None
)
# Define a global header for all pages
def render_header(title):
    st.markdown(f"""
    <div style="background-color:#1f4e79;padding:10px;border-radius:5px">
        <h1 style="color:white;text-align:center;">{title}</h1>
    </div>
    """, unsafe_allow_html=True)
# Define a global footer for the app
def render_footer():
    st.markdown("""
    ---
    <div style="text-align:center;">
        <small>© 2024 International University of Japan. All rights reserved.</small>
    </div>
    """, unsafe_allow_html=True)

# Page Title
render_header("S&P 500 Stock Analysis")
# Create tabs
tabs = st.tabs(["Home", "Stock Analysis", "Stock Comparison", "Stock News", "Contacts"])
# Tab: Home
with tabs[0]:
    st.header("Home")
    st.write("Our web app....")
    st.image("https://st3.depositphotos.com/3108485/32120/i/600/depositphotos_321205098-stock-photo-businessman-plan-graph-growth-and.jpg?text=Today's+Stock+Information", caption="Placeholder image for the Home page.")
# Tab: Stock Information
with tabs[1]:
    st.header("Stock Information")
    st.write("Select one stock")
    # App title and description
    st.title("Enhanced Stock Information Web App")
    st.write("Enter a ticker symbol to retrieve and visualize stock information interactively.")
    # Sidebar for input controls
    st.sidebar.header("Stock Input Options")
    ticker_symbol = st.sidebar.text_input("Enter stock ticker (e.g., AAPL, MSFT):", "AAPL", key="ticker")
    start_date = st.sidebar.date_input("Start Date", value=datetime(2022, 1, 1), key="start_date")
    end_date = st.sidebar.date_input("End Date", value=datetime.now(), key="end_date")
    show_recommendation = st.sidebar.checkbox("Show Recommendation", key="show_recommendation")

# Chart type selection
chart_type = st.sidebar.radio("Select Chart Type", ["Line Chart", "Candlestick Chart"])

# Fetch data and ensure valid date range
if start_date > end_date:
    st.error("End date must be after the start date. Please adjust your dates.")
else:
    if ticker_symbol:
        try:
            stock = yf.Ticker(ticker_symbol)
            data = stock.history(start=start_date, end=end_date)

            # Display current price
            current_price = data['Close'].iloc[-1]
            price_change = current_price - data['Close'].iloc[-2]
            percentage_change = (price_change / data['Close'].iloc[-2]) * 100
            price_class = "price-positive" if price_change > 0 else "price-negative"
            st.markdown(f"<div class='price {price_class}'>{current_price:.2f} USD</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='{price_class}'>{price_change:.2f} ({percentage_change:.2f}%)</div>", unsafe_allow_html=True)

            # Indicator toggles
            show_sma = st.sidebar.checkbox("Show Simple Moving Average (SMA)", key="show_sma")
            show_rsi = st.sidebar.checkbox("Show Relative Strength Index (RSI)", key="show_rsi")
            show_ema = st.sidebar.checkbox("Show Exponential Moving Average (EMA)", key="show_ema")
            show_macd = st.sidebar.checkbox("Show Moving Average Convergence Divergence (MACD)", key="show_macd")
            show_vwap = st.sidebar.checkbox("Show Volume Weighted Average Price (VWAP)", key="show_vwap")
            show_stochastic = st.sidebar.checkbox("Show Stochastic Oscillator", key="show_stochastic")
            show_atr = st.sidebar.checkbox("Show Average True Range (ATR)", key="show_atr")
            show_obv = st.sidebar.checkbox("Show On-Balance Volume (OBV)", key="show_obv")

            # Initialize buy signal count
            buy_signals = 0
            total_indicators = 0

            # Simple Moving Average (SMA)
            if show_sma:
                sma_period = st.sidebar.slider("SMA Period", 5, 100, 20)
                data['SMA'] = data['Close'].rolling(window=sma_period).mean()
                if data['Close'].iloc[-1] > data['SMA'].iloc[-1]:
                    buy_signals += 1
                total_indicators += 1

            # Exponential Moving Average (EMA)
            if show_ema:
                ema_period = st.sidebar.slider("EMA Period", 5, 100, 20)
                data['EMA'] = data['Close'].ewm(span=ema_period, adjust=False).mean()
                if data['Close'].iloc[-1] > data['EMA'].iloc[-1]:
                    buy_signals += 1
                total_indicators += 1

            # Relative Strength Index (RSI)
            if show_rsi:
                rsi_period = st.sidebar.slider("RSI Period", 5, 50, 14)
                delta = data['Close'].diff(1)
                gain = delta.where(delta > 0, 0)
                loss = -delta.where(delta < 0, 0)
                avg_gain = gain.rolling(window=rsi_period, min_periods=1).mean()
                avg_loss = loss.rolling(window=rsi_period, min_periods=1).mean()
                rs = avg_gain / avg_loss
                data['RSI'] = 100 - (100 / (1 + rs))
                if data['RSI'].iloc[-1] < 30:
                    buy_signals += 1
                total_indicators += 1

            # Moving Average Convergence Divergence (MACD)
            if show_macd:
                short_ema = data['Close'].ewm(span=12, adjust=False).mean()
                long_ema = data['Close'].ewm(span=26, adjust=False).mean()
                data['MACD'] = short_ema - long_ema
                data['Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()
                if data['MACD'].iloc[-1] > data['Signal'].iloc[-1]:
                    buy_signals += 1
                total_indicators += 1

            # Volume Weighted Average Price (VWAP)
            if show_vwap:
                data['VWAP'] = (data['Volume'] * (data['High'] + data['Low'] + data['Close']) / 3).cumsum() / data['Volume'].cumsum()
                if data['Close'].iloc[-1] > data['VWAP'].iloc[-1]:
                    buy_signals += 1
                total_indicators += 1

            # Stochastic Oscillator
            if show_stochastic:
                low_min = data['Low'].rolling(window=14).min()
                high_max = data['High'].rolling(window=14).max()
                data['%K'] = (data['Close'] - low_min) * 100 / (high_max - low_min)
                data['%D'] = data['%K'].rolling(window=3).mean()
                if data['%K'].iloc[-1] < 20:
                    buy_signals += 1
                total_indicators += 1

            # Average True Range (ATR)
            if show_atr:
                high_low = data['High'] - data['Low']
                high_close = abs(data['High'] - data['Close'].shift())
                low_close = abs(data['Low'] - data['Close'].shift())
                ranges = pd.concat([high_low, high_close, low_close], axis=1)
                true_range = ranges.max(axis=1)
                data['ATR'] = true_range.rolling(window=14).mean()

            # On-Balance Volume (OBV)
            if show_obv:
                data['OBV'] = (data['Volume'] * (data['Close'].diff().apply(lambda x: 1 if x > 0 else -1 if x < 0 else 0))).cumsum()
                if data['OBV'].iloc[-1] > data['OBV'].iloc[-2]:
                    buy_signals += 1
                total_indicators += 1

            # Determine Buy or Sell Recommendation
            sell_signals = total_indicators - buy_signals
            if show_recommendation:
                st.subheader("Recommendation Summary")
                st.write(f"Total Indicators: {total_indicators}")
                st.write(f"Buy Signals: {buy_signals}")
                st.write(f"Sell Signals: {sell_signals}")

                if buy_signals > sell_signals:
                    st.success("**Overall Recommendation: Buy** - Majority of indicators suggest a buy signal.")
                else:
                    st.warning("**Overall Recommendation: Sell** - Majority of indicators suggest a sell signal.")

            # Plot stock price based on selected chart type
            st.subheader(f"{ticker_symbol} Price Chart")
            fig = go.Figure()

            if chart_type == "Line Chart":
                # Line chart with indicators
                fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name="Close Price"))
                if show_sma:
                    fig.add_trace(go.Scatter(x=data.index, y=data['SMA'], mode='lines', name="SMA"))
                if show_ema:
                    fig.add_trace(go.Scatter(x=data.index, y=data['EMA'], mode='lines', name="EMA"))
                if show_vwap:
                    fig.add_trace(go.Scatter(x=data.index, y=data['VWAP'], mode='lines', name="VWAP"))

            elif chart_type == "Candlestick Chart":
                # Candlestick chart with indicators
                fig.add_trace(go.Candlestick(
                    x=data.index,
                    open=data['Open'],
                    high=data['High'],
                    low=data['Low'],
                    close=data['Close'],
                    name="Candlestick"
                ))
                if show_sma:
                    fig.add_trace(go.Scatter(x=data.index, y=data['SMA'], mode='lines', name="SMA"))
                if show_ema:
                    fig.add_trace(go.Scatter(x=data.index, y=data['EMA'], mode='lines', name="EMA"))
                if show_vwap:
                    fig.add_trace(go.Scatter(x=data.index, y=data['VWAP'], mode='lines', name="VWAP"))

            fig.update_layout(
                title=f"{ticker_symbol} Price Chart",
                xaxis_title="Date",
                yaxis_title="Price (USD)",
                xaxis_rangeslider_visible=(chart_type == "Candlestick Chart")  # Add range slider for candlesticks
            )
            st.plotly_chart(fig)

        except Exception as e:
            st.error(f"Could not retrieve data for {ticker_symbol}. Error: {e}")
# Tab: Comparison
with tabs[2]:
    st.header("Stock Comparison")
    st.write("This is the Visualization page. Show your plots here.")
    import matplotlib.pyplot as plt
    import numpy as np
    from datetime import date, timedelta
    import yfinance as yf
    import pandas as pd
    # Title for date and stock selection
    st.title('Select Date and Stocks')
    # Date range selection
    today = date.today()
    min_date = today - timedelta(days=365 * 5)
    max_date = today
    date_range = st.slider(
        "Select Date Range",
        min_value=min_date,
        max_value=max_date,
        value=(today - timedelta(days=365), today)
    )
    sdate, edate = date_range
    # Stock selection
    symbols = ["AAPL", "MSFT", "GOOG", "AMZN", "TSLA"]
    selected_stocks = st.multiselect(
        "Select Stocks", symbols, default=["AAPL"]
    )
    # Stock comparison
    st.title("Stock Comparison")
    if selected_stocks:
        # Fetch stock data
        data = yf.download(
            selected_stocks,
            start=sdate,
            end=edate,
            interval="1d",
            auto_adjust=True,
            prepost=True
        )
        if data.empty:
            st.error("Failed to fetch historical data or no data available for the selected period.")
        else:
            # Filter data for the selected date range
            filtered_data = data['Close'][selected_stocks]
            sdate_utc = pd.to_datetime(sdate).tz_localize('UTC')
            edate_utc = pd.to_datetime(edate).tz_localize('UTC')
            filtered_data = filtered_data[(filtered_data.index >= sdate_utc) & (filtered_data.index <= edate_utc)]
            if not filtered_data.empty:
                # Reset index to create a 'Date' column
                filtered_data = filtered_data.reset_index()
                filtered_data = filtered_data.rename(columns={'index': 'Date'})
                # Plot the data
                st.line_chart(
                    filtered_data,
                    x="Date",
                    y=selected_stocks[0] if len(selected_stocks) == 1 else selected_stocks
                )
            else:
                st.warning("No data available for the selected stock(s) and date range.")
    else:
        st.warning("Please select at least one stock.")
# Tab: News
	with tabs[3]:
		st.header("News")
		st.write("News")

		import streamlit as st
		import requests
		from bs4 import BeautifulSoup
		import feedparser
		from datetime import datetime


		# Function to extract news from Google News RSS
		def extract_news_from_google_rss(ticker):
			"""Fetch news articles for a given stock ticker using Google News RSS."""
			url = f"https://news.google.com/rss/search?q={ticker}+stock&hl=en-US&gl=US&ceid=US:en"
			feed = feedparser.parse(url)
			news_articles = []
			for entry in feed.entries[:15]:  # Limit to the latest 15 articles
				published_date = datetime(*entry.published_parsed[:6])  # Convert to datetime
				news_articles.append({"title": entry.title, "url": entry.link, "date": published_date})
			return news_articles


		# Function to fetch and preprocess text
		def fetch_article_content(url):
			"""Fetch article content using BeautifulSoup."""
			try:
				response = requests.get(url)
				soup = BeautifulSoup(response.content, "html.parser")
				headline = soup.title.string if soup.title else "No headline"
				paragraphs = soup.find_all("p")
				content = " ".join([para.get_text() for para in paragraphs])
				return headline, content
			except Exception as e:
				return None, None


		# App layout and styling
		st.title("Stock News Fetcher")
		ticker_symbol = st.text_input("Enter stock ticker (e.g., AAPL, MSFT):", key="ticker")

		if ticker_symbol:
			try:
				# Fetch news for the given ticker automatically
				news = extract_news_from_google_rss(ticker_symbol)
				if news:
					st.subheader(f"Latest News for {ticker_symbol.upper()}")
					for article in news:
						st.write(f"**{article['title']}**")
						st.write(f"[Read more]({article['url']}) - {article['date'].strftime('%Y-%m-%d %H:%M:%S')}")
						st.write("---")
				else:
					st.warning("No news articles found for this ticker.")
			except Exception as e:
				st.error(f"An error occurred while fetching news: {e}")
		else:
			st.info("Enter a stock ticker above to fetch the latest news.")

# Tab: Contact Us
with tabs[4]:
    st.header("Contact Us")
    st.write("We'd love to hear your feedback! Please use the form below.")

    # Set up SQLite database
    def create_feedback_table():
        conn = sqlite3.connect("feedback.db")
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT,
                message TEXT,
                submitted_at TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def insert_feedback(name, email, message):
        conn = sqlite3.connect("feedback.db")
        c = conn.cursor()
        c.execute('''
            INSERT INTO feedback (name, email, message, submitted_at)
            VALUES (?, ?, ?, ?)
        ''', (name, email, message, datetime.now()))  # Use datetime.now() correctly
        conn.commit()
        conn.close()

    def fetch_all_feedback():
        conn = sqlite3.connect("feedback.db")
        c = conn.cursor()
        c.execute('SELECT * FROM feedback')
        rows = c.fetchall()
        conn.close()
        return rows

    # Initialize the database
    create_feedback_table()

    # Feedback form
    with st.form("feedback_form"):
        name = st.text_input("Your Name")
        email = st.text_input("Your Email")
        message = st.text_area("Your Message")
        submit_button = st.form_submit_button("Submit")

        if submit_button:
            if name and email and message:
                # Save feedback to the database
                insert_feedback(name, email, message)
                st.success("Thank you for your feedback!")
            else:
                st.error("Please fill out all fields.")

    # Display stored feedback (Optional)
    st.write("---")
    st.header("Feedback Received")
    feedback_data = fetch_all_feedback()
    if feedback_data:
        for entry in feedback_data:
            st.write(f"**Name:** {entry[1]}")
            st.write(f"**Email:** {entry[2]}")
            st.write(f"**Message:** {entry[3]}")
            st.write(f"**Submitted At:** {entry[4]}")
            st.write("---")
    else:
        st.info("No feedback submitted yet.")
# Render the footer on all pages
render_footer()
