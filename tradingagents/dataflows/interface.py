from typing import Annotated, Dict
from .reddit_utils import fetch_top_from_category
from .yfin_utils import *
from .stockstats_utils import *
from .googlenews_utils import *
from .finnhub_utils import get_data_in_range
from dateutil.relativedelta import relativedelta
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import json
import os
import pandas as pd
from tqdm import tqdm
import yfinance as yf
# Import new Google Gemini SDK (google-genai)
from google import genai
from .config import get_config, set_config, DATA_DIR


def get_finnhub_news(
    ticker: Annotated[
        str,
        "Search query of a company's, e.g. 'AAPL, TSM, etc.",
    ],
    curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "how many days to look back"],
):
    """
    Retrieve news about a company within a time frame

    Args
        ticker (str): ticker for the company you are interested in
        start_date (str): Start date in yyyy-mm-dd format
        end_date (str): End date in yyyy-mm-dd format
    Returns
        str: dataframe containing the news of the company in the time frame

    """

    start_date = datetime.strptime(curr_date, "%Y-%m-%d")
    before = start_date - relativedelta(days=look_back_days)
    before = before.strftime("%Y-%m-%d")

    result = get_data_in_range(ticker, before, curr_date, "news_data", DATA_DIR)

    if len(result) == 0:
        return ""

    combined_result = ""
    for day, data in result.items():
        if len(data) == 0:
            continue
        for entry in data:
            current_news = (
                "### " + entry["headline"] + f" ({day})" + "\n" + entry["summary"]
            )
            combined_result += current_news + "\n\n"

    return f"## {ticker} News, from {before} to {curr_date}:\n" + str(combined_result)


def get_finnhub_company_insider_sentiment(
    ticker: Annotated[str, "ticker symbol for the company"],
    curr_date: Annotated[
        str,
        "current date of you are trading at, yyyy-mm-dd",
    ],
    look_back_days: Annotated[int, "number of days to look back"],
):
    """
    Retrieve insider sentiment about a company (retrieved from public SEC information) for the past 15 days
    Args:
        ticker (str): ticker symbol of the company
        curr_date (str): current date you are trading on, yyyy-mm-dd
    Returns:
        str: a report of the sentiment in the past 15 days starting at curr_date
    """

    date_obj = datetime.strptime(curr_date, "%Y-%m-%d")
    before = date_obj - relativedelta(days=look_back_days)
    before = before.strftime("%Y-%m-%d")

    data = get_data_in_range(ticker, before, curr_date, "insider_senti", DATA_DIR)

    if len(data) == 0:
        return ""

    result_str = ""
    seen_dicts = []
    for date, senti_list in data.items():
        for entry in senti_list:
            if entry not in seen_dicts:
                result_str += f"### {entry['year']}-{entry['month']}:\nChange: {entry['change']}\nMonthly Share Purchase Ratio: {entry['mspr']}\n\n"
                seen_dicts.append(entry)

    return (
        f"## {ticker} Insider Sentiment Data for {before} to {curr_date}:\n"
        + result_str
        + "The change field refers to the net buying/selling from all insiders' transactions. The mspr field refers to monthly share purchase ratio."
    )


def get_finnhub_company_insider_transactions(
    ticker: Annotated[str, "ticker symbol"],
    curr_date: Annotated[
        str,
        "current date you are trading at, yyyy-mm-dd",
    ],
    look_back_days: Annotated[int, "how many days to look back"],
):
    """
    Retrieve insider transcaction information about a company (retrieved from public SEC information) for the past 15 days
    Args:
        ticker (str): ticker symbol of the company
        curr_date (str): current date you are trading at, yyyy-mm-dd
    Returns:
        str: a report of the company's insider transaction/trading informtaion in the past 15 days
    """

    date_obj = datetime.strptime(curr_date, "%Y-%m-%d")
    before = date_obj - relativedelta(days=look_back_days)
    before = before.strftime("%Y-%m-%d")

    data = get_data_in_range(ticker, before, curr_date, "insider_trans", DATA_DIR)

    if len(data) == 0:
        return ""

    result_str = ""

    seen_dicts = []
    for date, senti_list in data.items():
        for entry in senti_list:
            if entry not in seen_dicts:
                result_str += f"### Filing Date: {entry['filingDate']}, {entry['name']}:\nChange:{entry['change']}\nShares: {entry['share']}\nTransaction Price: {entry['transactionPrice']}\nTransaction Code: {entry['transactionCode']}\n\n"
                seen_dicts.append(entry)

    return (
        f"## {ticker} insider transactions from {before} to {curr_date}:\n"
        + result_str
        + "The change field reflects the variation in share count—here a negative number indicates a reduction in holdings—while share specifies the total number of shares involved. The transactionPrice denotes the per-share price at which the trade was executed, and transactionDate marks when the transaction occurred. The name field identifies the insider making the trade, and transactionCode (e.g., S for sale) clarifies the nature of the transaction. FilingDate records when the transaction was officially reported, and the unique id links to the specific SEC filing, as indicated by the source. Additionally, the symbol ties the transaction to a particular company, isDerivative flags whether the trade involves derivative securities, and currency notes the currency context of the transaction."
    )


def get_simfin_balance_sheet(
    ticker: Annotated[str, "ticker symbol"],
    freq: Annotated[
        str,
        "reporting frequency of the company's financial history: annual / quarterly",
    ],
    curr_date: Annotated[str, "current date you are trading at, yyyy-mm-dd"],
):
    data_path = os.path.join(
        DATA_DIR,
        "fundamental_data",
        "simfin_data_all",
        "balance_sheet",
        "companies",
        "us",
        f"us-balance-{freq}.csv",
    )
    df = pd.read_csv(data_path, sep=";")

    # Convert date strings to datetime objects and remove any time components
    df["Report Date"] = pd.to_datetime(df["Report Date"], utc=True).dt.normalize()
    df["Publish Date"] = pd.to_datetime(df["Publish Date"], utc=True).dt.normalize()

    # Convert the current date to datetime and normalize
    curr_date_dt = pd.to_datetime(curr_date, utc=True).normalize()

    # Filter the DataFrame for the given ticker and for reports that were published on or before the current date
    filtered_df = df[(df["Ticker"] == ticker) & (df["Publish Date"] <= curr_date_dt)]

    # Check if there are any available reports; if not, return a notification
    if filtered_df.empty:
        print("No balance sheet available before the given current date.")
        return ""

    # Get the most recent balance sheet by selecting the row with the latest Publish Date
    latest_balance_sheet = filtered_df.loc[filtered_df["Publish Date"].idxmax()]

    # drop the SimFinID column
    latest_balance_sheet = latest_balance_sheet.drop("SimFinId")

    return (
        f"## {freq} balance sheet for {ticker} released on {str(latest_balance_sheet['Publish Date'])[0:10]}: \n"
        + str(latest_balance_sheet)
        + "\n\nThis includes metadata like reporting dates and currency, share details, and a breakdown of assets, liabilities, and equity. Assets are grouped as current (liquid items like cash and receivables) and noncurrent (long-term investments and property). Liabilities are split between short-term obligations and long-term debts, while equity reflects shareholder funds such as paid-in capital and retained earnings. Together, these components ensure that total assets equal the sum of liabilities and equity."
    )


def get_simfin_cashflow(
    ticker: Annotated[str, "ticker symbol"],
    freq: Annotated[
        str,
        "reporting frequency of the company's financial history: annual / quarterly",
    ],
    curr_date: Annotated[str, "current date you are trading at, yyyy-mm-dd"],
):
    data_path = os.path.join(
        DATA_DIR,
        "fundamental_data",
        "simfin_data_all",
        "cash_flow",
        "companies",
        "us",
        f"us-cashflow-{freq}.csv",
    )
    df = pd.read_csv(data_path, sep=";")

    # Convert date strings to datetime objects and remove any time components
    df["Report Date"] = pd.to_datetime(df["Report Date"], utc=True).dt.normalize()
    df["Publish Date"] = pd.to_datetime(df["Publish Date"], utc=True).dt.normalize()

    # Convert the current date to datetime and normalize
    curr_date_dt = pd.to_datetime(curr_date, utc=True).normalize()

    # Filter the DataFrame for the given ticker and for reports that were published on or before the current date
    filtered_df = df[(df["Ticker"] == ticker) & (df["Publish Date"] <= curr_date_dt)]

    # Check if there are any available reports; if not, return a notification
    if filtered_df.empty:
        print("No cash flow statement available before the given current date.")
        return ""

    # Get the most recent cash flow statement by selecting the row with the latest Publish Date
    latest_cash_flow = filtered_df.loc[filtered_df["Publish Date"].idxmax()]

    # drop the SimFinID column
    latest_cash_flow = latest_cash_flow.drop("SimFinId")

    return (
        f"## {freq} cash flow statement for {ticker} released on {str(latest_cash_flow['Publish Date'])[0:10]}: \n"
        + str(latest_cash_flow)
        + "\n\nThis includes metadata like reporting dates and currency, share details, and a breakdown of cash movements. Operating activities show cash generated from core business operations, including net income adjustments for non-cash items and working capital changes. Investing activities cover asset acquisitions/disposals and investments. Financing activities include debt transactions, equity issuances/repurchases, and dividend payments. The net change in cash represents the overall increase or decrease in the company's cash position during the reporting period."
    )


def get_simfin_income_statements(
    ticker: Annotated[str, "ticker symbol"],
    freq: Annotated[
        str,
        "reporting frequency of the company's financial history: annual / quarterly",
    ],
    curr_date: Annotated[str, "current date you are trading at, yyyy-mm-dd"],
):
    data_path = os.path.join(
        DATA_DIR,
        "fundamental_data",
        "simfin_data_all",
        "income_statements",
        "companies",
        "us",
        f"us-income-{freq}.csv",
    )
    df = pd.read_csv(data_path, sep=";")

    # Convert date strings to datetime objects and remove any time components
    df["Report Date"] = pd.to_datetime(df["Report Date"], utc=True).dt.normalize()
    df["Publish Date"] = pd.to_datetime(df["Publish Date"], utc=True).dt.normalize()

    # Convert the current date to datetime and normalize
    curr_date_dt = pd.to_datetime(curr_date, utc=True).normalize()

    # Filter the DataFrame for the given ticker and for reports that were published on or before the current date
    filtered_df = df[(df["Ticker"] == ticker) & (df["Publish Date"] <= curr_date_dt)]

    # Check if there are any available reports; if not, return a notification
    if filtered_df.empty:
        print("No income statement available before the given current date.")
        return ""

    # Get the most recent income statement by selecting the row with the latest Publish Date
    latest_income = filtered_df.loc[filtered_df["Publish Date"].idxmax()]

    # drop the SimFinID column
    latest_income = latest_income.drop("SimFinId")

    return (
        f"## {freq} income statement for {ticker} released on {str(latest_income['Publish Date'])[0:10]}: \n"
        + str(latest_income)
        + "\n\nThis includes metadata like reporting dates and currency, share details, and a comprehensive breakdown of the company's financial performance. Starting with Revenue, it shows Cost of Revenue and resulting Gross Profit. Operating Expenses are detailed, including SG&A, R&D, and Depreciation. The statement then shows Operating Income, followed by non-operating items and Interest Expense, leading to Pretax Income. After accounting for Income Tax and any Extraordinary items, it concludes with Net Income, representing the company's bottom-line profit or loss for the period."
    )


def get_google_news(
    query: Annotated[str, "Query to search with"],
    curr_date: Annotated[str, "Curr date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "how many days to look back"],
) -> str:
    query = query.replace(" ", "+")

    start_date = datetime.strptime(curr_date, "%Y-%m-%d")
    before = start_date - relativedelta(days=look_back_days)
    before = before.strftime("%Y-%m-%d")

    news_results = getNewsData(query, before, curr_date)

    news_str = ""

    for news in news_results:
        news_str += (
            f"### {news['title']} (source: {news['source']}) \n\n{news['snippet']}\n\n"
        )

    if len(news_results) == 0:
        return ""

    return f"## {query} Google News, from {before} to {curr_date}:\n\n{news_str}"


def get_reddit_global_news(
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "how many days to look back"],
    max_limit_per_day: Annotated[int, "Maximum number of news per day"],
) -> str:
    """
    Retrieve the latest top reddit news
    Args:
        start_date: Start date in yyyy-mm-dd format
        end_date: End date in yyyy-mm-dd format
    Returns:
        str: A formatted dataframe containing the latest news articles posts on reddit and meta information in these columns: "created_utc", "id", "title", "selftext", "score", "num_comments", "url"
    """

    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    before = start_date - relativedelta(days=look_back_days)
    before = before.strftime("%Y-%m-%d")

    posts = []
    # iterate from start_date to end_date
    curr_date = datetime.strptime(before, "%Y-%m-%d")

    total_iterations = (start_date - curr_date).days + 1
    pbar = tqdm(desc=f"Getting Global News on {start_date}", total=total_iterations)

    while curr_date <= start_date:
        curr_date_str = curr_date.strftime("%Y-%m-%d")
        fetch_result = fetch_top_from_category(
            "global_news",
            curr_date_str,
            max_limit_per_day,
            data_path=os.path.join(DATA_DIR, "reddit_data"),
        )
        posts.extend(fetch_result)
        curr_date += relativedelta(days=1)
        pbar.update(1)

    pbar.close()

    if len(posts) == 0:
        return ""

    news_str = ""
    for post in posts:
        if post["content"] == "":
            news_str += f"### {post['title']}\n\n"
        else:
            news_str += f"### {post['title']}\n\n{post['content']}\n\n"

    return f"## Global News Reddit, from {before} to {curr_date}:\n{news_str}"


def get_reddit_company_news(
    ticker: Annotated[str, "ticker symbol of the company"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "how many days to look back"],
    max_limit_per_day: Annotated[int, "Maximum number of news per day"],
) -> str:
    """
    Retrieve the latest top reddit news
    Args:
        ticker: ticker symbol of the company
        start_date: Start date in yyyy-mm-dd format
        end_date: End date in yyyy-mm-dd format
    Returns:
        str: A formatted dataframe containing the latest news articles posts on reddit and meta information in these columns: "created_utc", "id", "title", "selftext", "score", "num_comments", "url"
    """

    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    before = start_date - relativedelta(days=look_back_days)
    before = before.strftime("%Y-%m-%d")

    posts = []
    # iterate from start_date to end_date
    curr_date = datetime.strptime(before, "%Y-%m-%d")

    total_iterations = (start_date - curr_date).days + 1
    pbar = tqdm(
        desc=f"Getting Company News for {ticker} on {start_date}",
        total=total_iterations,
    )

    while curr_date <= start_date:
        curr_date_str = curr_date.strftime("%Y-%m-%d")
        fetch_result = fetch_top_from_category(
            "company_news",
            curr_date_str,
            max_limit_per_day,
            ticker,
            data_path=os.path.join(DATA_DIR, "reddit_data"),
        )
        posts.extend(fetch_result)
        curr_date += relativedelta(days=1)

        pbar.update(1)

    pbar.close()

    if len(posts) == 0:
        return ""

    news_str = ""
    for post in posts:
        if post["content"] == "":
            news_str += f"### {post['title']}\n\n"
        else:
            news_str += f"### {post['title']}\n\n{post['content']}\n\n"

    return f"##{ticker} News Reddit, from {before} to {curr_date}:\n\n{news_str}"


def get_stock_stats_indicators_window(
    symbol: Annotated[str, "ticker symbol of the company"],
    indicator: Annotated[str, "technical indicator to get the analysis and report of"],
    curr_date: Annotated[
        str, "The current trading date you are trading on, YYYY-mm-dd"
    ],
    look_back_days: Annotated[int, "how many days to look back"],
    online: Annotated[bool, "to fetch data online or offline"],
) -> str:

    best_ind_params = {
        # Moving Averages
        "close_50_sma": (
            "50 SMA: A medium-term trend indicator. "
            "Usage: Identify trend direction and serve as dynamic support/resistance. "
            "Tips: It lags price; combine with faster indicators for timely signals."
        ),
        "close_200_sma": (
            "200 SMA: A long-term trend benchmark. "
            "Usage: Confirm overall market trend and identify golden/death cross setups. "
            "Tips: It reacts slowly; best for strategic trend confirmation rather than frequent trading entries."
        ),
        "close_10_ema": (
            "10 EMA: A responsive short-term average. "
            "Usage: Capture quick shifts in momentum and potential entry points. "
            "Tips: Prone to noise in choppy markets; use alongside longer averages for filtering false signals."
        ),
        # MACD Related
        "macd": (
            "MACD: Computes momentum via differences of EMAs. "
            "Usage: Look for crossovers and divergence as signals of trend changes. "
            "Tips: Confirm with other indicators in low-volatility or sideways markets."
        ),
        "macds": (
            "MACD Signal: An EMA smoothing of the MACD line. "
            "Usage: Use crossovers with the MACD line to trigger trades. "
            "Tips: Should be part of a broader strategy to avoid false positives."
        ),
        "macdh": (
            "MACD Histogram: Shows the gap between the MACD line and its signal. "
            "Usage: Visualize momentum strength and spot divergence early. "
            "Tips: Can be volatile; complement with additional filters in fast-moving markets."
        ),
        # Momentum Indicators
        "rsi": (
            "RSI: Measures momentum to flag overbought/oversold conditions. "
            "Usage: Apply 70/30 thresholds and watch for divergence to signal reversals. "
            "Tips: In strong trends, RSI may remain extreme; always cross-check with trend analysis."
        ),
        # Volatility Indicators
        "boll": (
            "Bollinger Middle: A 20 SMA serving as the basis for Bollinger Bands. "
            "Usage: Acts as a dynamic benchmark for price movement. "
            "Tips: Combine with the upper and lower bands to effectively spot breakouts or reversals."
        ),
        "boll_ub": (
            "Bollinger Upper Band: Typically 2 standard deviations above the middle line. "
            "Usage: Signals potential overbought conditions and breakout zones. "
            "Tips: Confirm signals with other tools; prices may ride the band in strong trends."
        ),
        "boll_lb": (
            "Bollinger Lower Band: Typically 2 standard deviations below the middle line. "
            "Usage: Indicates potential oversold conditions. "
            "Tips: Use additional analysis to avoid false reversal signals."
        ),
        "atr": (
            "ATR: Averages true range to measure volatility. "
            "Usage: Set stop-loss levels and adjust position sizes based on current market volatility. "
            "Tips: It's a reactive measure, so use it as part of a broader risk management strategy."
        ),
        # Volume-Based Indicators
        "vwma": (
            "VWMA: A moving average weighted by volume. "
            "Usage: Confirm trends by integrating price action with volume data. "
            "Tips: Watch for skewed results from volume spikes; use in combination with other volume analyses."
        ),
        "mfi": (
            "MFI: The Money Flow Index is a momentum indicator that uses both price and volume to measure buying and selling pressure. "
            "Usage: Identify overbought (>80) or oversold (<20) conditions and confirm the strength of trends or reversals. "
            "Tips: Use alongside RSI or MACD to confirm signals; divergence between price and MFI can indicate potential reversals."
        ),
    }

    if indicator not in best_ind_params:
        raise ValueError(
            f"Indicator {indicator} is not supported. Please choose from: {list(best_ind_params.keys())}"
        )

    end_date = curr_date
    curr_date = datetime.strptime(curr_date, "%Y-%m-%d")
    before = curr_date - relativedelta(days=look_back_days)

    if not online:
        # read from YFin data
        data = pd.read_csv(
            os.path.join(
                DATA_DIR,
                f"market_data/price_data/{symbol}-YFin-data-2015-01-01-2025-03-25.csv",
            )
        )
        data["Date"] = pd.to_datetime(data["Date"], utc=True)
        dates_in_df = data["Date"].astype(str).str[:10]

        ind_string = ""
        while curr_date >= before:
            # only do the trading dates
            if curr_date.strftime("%Y-%m-%d") in dates_in_df.values:
                indicator_value = get_stockstats_indicator(
                    symbol, indicator, curr_date.strftime("%Y-%m-%d"), online
                )

                ind_string += f"{curr_date.strftime('%Y-%m-%d')}: {indicator_value}\n"

            curr_date = curr_date - relativedelta(days=1)
    else:
        # online gathering
        ind_string = ""
        while curr_date >= before:
            indicator_value = get_stockstats_indicator(
                symbol, indicator, curr_date.strftime("%Y-%m-%d"), online
            )

            ind_string += f"{curr_date.strftime('%Y-%m-%d')}: {indicator_value}\n"

            curr_date = curr_date - relativedelta(days=1)

    result_str = (
        f"## {indicator} values from {before.strftime('%Y-%m-%d')} to {end_date}:\n\n"
        + ind_string
        + "\n\n"
        + best_ind_params.get(indicator, "No description available.")
    )

    return result_str


def get_stockstats_indicator(
    symbol: Annotated[str, "ticker symbol of the company"],
    indicator: Annotated[str, "technical indicator to get the analysis and report of"],
    curr_date: Annotated[
        str, "The current trading date you are trading on, YYYY-mm-dd"
    ],
    online: Annotated[bool, "to fetch data online or offline"],
) -> str:

    curr_date = datetime.strptime(curr_date, "%Y-%m-%d")
    curr_date = curr_date.strftime("%Y-%m-%d")

    try:
        indicator_value = StockstatsUtils.get_stock_stats(
            symbol,
            indicator,
            curr_date,
            os.path.join(DATA_DIR, "market_data", "price_data"),
            online=online,
        )
    except Exception as e:
        print(
            f"Error getting stockstats indicator data for indicator {indicator} on {curr_date}: {e}"
        )
        return ""

    return str(indicator_value)


def get_YFin_data_window(
    symbol: Annotated[str, "ticker symbol of the company"],
    curr_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "how many days to look back"],
) -> str:
    # calculate past days
    date_obj = datetime.strptime(curr_date, "%Y-%m-%d")
    before = date_obj - relativedelta(days=look_back_days)
    start_date = before.strftime("%Y-%m-%d")

    # read in data
    data = pd.read_csv(
        os.path.join(
            DATA_DIR,
            f"market_data/price_data/{symbol}-YFin-data-2015-01-01-2025-03-25.csv",
        )
    )

    # Extract just the date part for comparison
    data["DateOnly"] = data["Date"].str[:10]

    # Filter data between the start and end dates (inclusive)
    filtered_data = data[
        (data["DateOnly"] >= start_date) & (data["DateOnly"] <= curr_date)
    ]

    # Drop the temporary column we created
    filtered_data = filtered_data.drop("DateOnly", axis=1)

    # Set pandas display options to show the full DataFrame
    with pd.option_context(
        "display.max_rows", None, "display.max_columns", None, "display.width", None
    ):
        df_string = filtered_data.to_string()

    return (
        f"## Raw Market Data for {symbol} from {start_date} to {curr_date}:\n\n"
        + df_string
    )


def get_YFin_data_online(
    symbol: Annotated[str, "ticker symbol of the company"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
):

    datetime.strptime(start_date, "%Y-%m-%d")
    datetime.strptime(end_date, "%Y-%m-%d")

    # Create ticker object
    ticker = yf.Ticker(symbol.upper())

    # Fetch historical data for the specified date range
    data = ticker.history(start=start_date, end=end_date)

    # Check if data is empty
    if data.empty:
        return (
            f"No data found for symbol '{symbol}' between {start_date} and {end_date}"
        )

    # Remove timezone info from index for cleaner output
    if data.index.tz is not None:
        data.index = data.index.tz_localize(None)

    # Round numerical values to 2 decimal places for cleaner display
    numeric_columns = ["Open", "High", "Low", "Close", "Adj Close"]
    for col in numeric_columns:
        if col in data.columns:
            data[col] = data[col].round(2)

    # Convert DataFrame to CSV string
    csv_string = data.to_csv()

    # Add header information
    header = f"# Stock data for {symbol.upper()} from {start_date} to {end_date}\n"
    header += f"# Total records: {len(data)}\n"
    header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    return header + csv_string


def get_YFin_data(
    symbol: Annotated[str, "ticker symbol of the company"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
) -> str:
    # read in data
    data = pd.read_csv(
        os.path.join(
            DATA_DIR,
            f"market_data/price_data/{symbol}-YFin-data-2015-01-01-2025-03-25.csv",
        )
    )

    if end_date > "2025-03-25":
        raise Exception(
            f"Get_YFin_Data: {end_date} is outside of the data range of 2015-01-01 to 2025-03-25"
        )

    # Extract just the date part for comparison
    data["DateOnly"] = data["Date"].str[:10]

    # Filter data between the start and end dates (inclusive)
    filtered_data = data[
        (data["DateOnly"] >= start_date) & (data["DateOnly"] <= end_date)
    ]

    # Drop the temporary column we created
    filtered_data = filtered_data.drop("DateOnly", axis=1)

    # remove the index from the dataframe
    filtered_data = filtered_data.reset_index(drop=True)

    return filtered_data


def get_stock_news_openai(ticker, curr_date):
    """
    Fetch stock news using Google Gemini's grounding feature for real web search.
    This uses Google Search to get actual, up-to-date information about the stock.
    """
    try:
        config = get_config()
        
        # Configure Google Gemini API
        api_key = config.get("google_api_key")
        if not api_key or api_key == 'your_google_api_key_here':
            return (
                f"Unable to fetch stock news for {ticker}. "
                "Google API key not configured. Please set GOOGLE_API_KEY in your .env file."
            )
        
        # Use new SDK - create client
        client = genai.Client(api_key=api_key)
        
        # Calculate date range
        end_date = datetime.strptime(curr_date, "%Y-%m-%d")
        start_date = end_date - relativedelta(days=7)
        start_date_str = start_date.strftime("%Y-%m-%d")
        
        # Create prompt for stock news search
        prompt = f"""Search for recent news and social media discussions about {ticker} stock
        from {start_date_str} to {curr_date}.
        
        Focus on:
        1. Recent company announcements and earnings
        2. Market sentiment and analyst opinions
        3. Social media discussions from Reddit, Twitter/X, and financial forums
        4. Any significant events or developments
        5. Stock price movements and trading volume changes
        
        Provide a comprehensive summary of the findings with dates and sources."""
        
        # Generate response with grounding using new SDK
        response = client.models.generate_content(
            model=config.get("quick_think_llm", "gemini-2.0-flash-exp"),
            contents=prompt,
            config={"tools": [{"google_search": {}}]}
        )
        
        if response and response.text:
            return f"## {ticker} Stock News and Social Media (via Google Search)\n### Period: {start_date_str} to {curr_date}\n\n{response.text}"
        else:
            return f"No stock news found for {ticker} in the specified period."
    
    except Exception as e:
        # Fallback to using existing tools
        results = []
        
        # Try to get Google News data
        try:
            google_news = get_google_news(ticker, curr_date, 7)
            if google_news and google_news.strip():
                results.append(google_news)
        except:
            pass
        
        # Try to get Reddit news
        try:
            reddit_news = get_reddit_company_news(ticker, curr_date, 7, 5)
            if reddit_news and reddit_news.strip():
                results.append(reddit_news)
        except:
            pass
        
        if results:
            return "\n\n".join(results)
        else:
            return f"Unable to fetch stock news for {ticker}. Error: {str(e)}"


def get_global_news_openai(curr_date):
    """
    Fetch global and macroeconomic news using Google Gemini.
    Attempts to use Google Search grounding if available, otherwise aggregates from multiple sources.
    """
    try:
        config = get_config()
        
        # Configure Google Gemini API
        api_key = config.get("google_api_key")
        if not api_key or api_key == 'your_google_api_key_here':
            return (
                f"Unable to fetch global news. "
                "Google API key not configured. Please set GOOGLE_API_KEY in your .env file."
            )
        
        # Calculate date range
        end_date = datetime.strptime(curr_date, "%Y-%m-%d")
        start_date = end_date - relativedelta(days=7)
        start_date_str = start_date.strftime("%Y-%m-%d")
        
        # Try to use Google Search grounding feature with new SDK
        try:
            # Set up API key in environment for new SDK
            os.environ['GOOGLE_API_KEY'] = api_key
            
            # Use new SDK syntax based on the notebook
            from google import genai as new_genai
            client = new_genai.Client()  # API key from environment
            
            # Create prompt for global news search
            prompt = f"""What are the latest global economic and market news from {start_date_str} to {curr_date}
            that would be relevant for trading and investment decisions?
            
            Focus on:
            1. Major economic indicators (GDP, inflation, unemployment, interest rates)
            2. Central bank policies and announcements (Fed, ECB, BOJ, etc.)
            3. Geopolitical events affecting markets
            4. Major market movements and trends
            5. Commodity prices (oil, gold, etc.)
            6. Currency movements and forex trends
            7. Sector-wide developments and industry news
            8. Global trade and supply chain updates
            
            Provide a comprehensive summary with specific dates, data points, and sources where available."""
            
            # Generate response with grounding using the exact syntax from notebook
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt,
                config={"tools": [{"google_search": {}}]}
            )
            
            if response.text:
                # Check if grounding metadata is available
                grounding_info = ""
                try:
                    if hasattr(response, 'candidates') and response.candidates:
                        candidate = response.candidates[0]
                        if hasattr(candidate, 'grounding_metadata'):
                            metadata = candidate.grounding_metadata
                            if hasattr(metadata, 'web_search_queries') and metadata.web_search_queries:
                                grounding_info = f"\n\n**Search Queries Used:** {', '.join(metadata.web_search_queries)}"
                except:
                    pass  # Ignore metadata extraction errors
                
                return f"## Global Economic & Market News (via Google Search)\n### Period: {start_date_str} to {curr_date}\n\n{response.text}{grounding_info}"
            
        except ImportError:
            # New SDK not available, try old SDK with different syntax
            print("New google-genai SDK not available, trying legacy approach...")
            
            try:
                # Try old SDK
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(model_name="gemini-2.0-flash-exp")
                
                # Try with tools parameter
                response = model.generate_content(
                    prompt,
                    generation_config=genai.GenerationConfig(
                        temperature=0.7
                    )
                )
                
                if response.text:
                    return f"## Global Economic & Market News\n### Period: {start_date_str} to {curr_date}\n\n{response.text}"
                    
            except Exception as old_sdk_error:
                print(f"Old SDK approach failed: {old_sdk_error}")
                
        except Exception as grounding_error:
            # If grounding fails, fall back to aggregation approach
            print(f"Google Search grounding not available: {grounding_error}")
            print("Falling back to aggregation from multiple sources...")
        
        # Fallback: Aggregate news from multiple sources and use Gemini to analyze
        aggregated_news = []
        
        # Try to get Google News data
        try:
            search_terms = [
                "global economy market news",
                "Federal Reserve interest rates inflation",
                "stock market trends today",
                "commodity prices oil gold"
            ]
            
            for term in search_terms[:2]:  # Limit to avoid too much data
                news = get_google_news(term, curr_date, 7)
                if news and news.strip():
                    aggregated_news.append(news)
        except Exception as e:
            print(f"Error fetching Google News: {e}")
        
        # Try to get Reddit global news
        try:
            reddit_news = get_reddit_global_news(curr_date, 7, 5)
            if reddit_news and reddit_news.strip():
                aggregated_news.append(reddit_news)
        except Exception as e:
            print(f"Error fetching Reddit news: {e}")
        
        # If we have aggregated news, use Gemini to analyze and summarize it
        if aggregated_news:
            # Create model without grounding using available SDK
            try:
                # Try new SDK first
                from google import genai as new_genai
                os.environ['GOOGLE_API_KEY'] = api_key
                client = new_genai.Client()
                model_name = config.get("quick_think_llm", "gemini-2.0-flash-exp")
            except ImportError:
                # Fall back to old SDK
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(
                    model_name=config.get("quick_think_llm", "gemini-2.0-flash-exp")
                )
            
            # Combine all news sources (limit to avoid token limits)
            combined_news = "\n\n".join(aggregated_news)
            if len(combined_news) > 15000:
                combined_news = combined_news[:15000]
            
            # Create analysis prompt
            analysis_prompt = f"""Based on the following news and market information from {start_date_str} to {curr_date},
            provide a comprehensive analysis of the current global economic and market situation relevant for trading decisions.
            
            NEWS DATA:
            {combined_news}
            
            Please analyze and summarize:
            1. Major economic indicators and trends
            2. Central bank policies and monetary environment
            3. Geopolitical events affecting markets
            4. Key market movements and sector trends
            5. Commodity and currency movements
            6. Overall market sentiment and risk factors
            7. Potential opportunities and threats for investors
            
            Provide a structured, analytical summary focusing on actionable insights for trading decisions."""
            
            # Generate analysis
            try:
                # Try new SDK syntax
                if 'client' in locals():
                    response = client.models.generate_content(
                        model=model_name,
                        contents=analysis_prompt
                    )
                else:
                    # Use old SDK
                    response = model.generate_content(analysis_prompt)
            except Exception as e:
                print(f"Error generating analysis: {e}")
                response = None
            
            if response.text:
                return f"## Global Economic & Market Analysis\n### Period: {start_date_str} to {curr_date}\n\n{response.text}"
            else:
                # Return raw aggregated news if analysis fails
                return f"## Global Economic & Market News (Aggregated)\n### Period: {start_date_str} to {curr_date}\n\n" + combined_news
        
        else:
            # If no news sources available, provide a generic market overview
            return f"""## Global Economic & Market Overview
### Period: {start_date_str} to {curr_date}

Unable to fetch real-time global news data. Please ensure:
1. Google News API is properly configured
2. Reddit data sources are accessible
3. Network connectivity is stable

For comprehensive market analysis, consider:
- Checking major financial news websites directly
- Monitoring central bank announcements
- Reviewing economic calendar for key indicators
- Analyzing sector-specific trends
- Evaluating geopolitical developments

Note: Trading decisions should be based on multiple data sources and thorough analysis."""
    
    except Exception as e:
        return f"""## Global News Fetch Error
Unable to retrieve global economic news for {curr_date}.
Error: {str(e)}

Please verify:
- Google API key is properly configured in .env file
- Network connectivity is stable
- API quotas are not exceeded

Consider using alternative news sources for market analysis."""


def get_fundamentals_openai(ticker, curr_date):
    """
    Fetch fundamental data using Google Gemini's grounding feature.
    This uses Google Search to get actual, current fundamental metrics for the stock.
    """
    try:
        config = get_config()
        
        # Configure Google Gemini API
        api_key = config.get("google_api_key")
        if not api_key or api_key == 'your_google_api_key_here':
            return (
                f"Unable to fetch fundamental data for {ticker}. "
                "Google API key not configured. Please set GOOGLE_API_KEY in your .env file."
            )
        
        genai.configure(api_key=api_key)
        
        # Calculate date range (looking at monthly data)
        end_date = datetime.strptime(curr_date, "%Y-%m-%d")
        start_date = end_date - relativedelta(months=1)
        start_date_str = start_date.strftime("%Y-%m-%d")
        
        # Create model with grounding enabled
        model = genai.GenerativeModel(
            model_name=config.get("quick_think_llm", "gemini-2.0-flash-exp"),
            tools=types.Tool(
                google_search=types.GoogleSearch()
            )
        )
        
        # Create prompt for fundamentals search
        prompt = f"""Search for the most recent fundamental financial data and metrics for {ticker} stock
        as of {curr_date} or the most recent available data.
        
        Provide the following information in a structured format:
        
        **Valuation Metrics:**
        - P/E Ratio (TTM and Forward)
        - P/S Ratio
        - P/B Ratio
        - PEG Ratio
        - EV/EBITDA
        
        **Financial Performance:**
        - Revenue (TTM and YoY growth)
        - Earnings per Share (EPS)
        - Net Income and margins
        - Operating Cash Flow
        - Free Cash Flow
        - EBITDA
        
        **Balance Sheet:**
        - Total Assets
        - Total Debt
        - Debt-to-Equity Ratio
        - Current Ratio
        - Quick Ratio
        
        **Profitability:**
        - Gross Margin
        - Operating Margin
        - Net Profit Margin
        - Return on Equity (ROE)
        - Return on Assets (ROA)
        
        **Other Key Metrics:**
        - Dividend Yield
        - Market Cap
        - Enterprise Value
        - Shares Outstanding
        
        Include the data source and date for each metric. Format as a clear table or structured list."""
        
        # Generate response with grounding
        response = model.generate_content(prompt)
        
        if response.text:
            return f"## {ticker} Fundamental Data (via Google Search)\n### As of {curr_date}\n\n{response.text}"
        else:
            # Fallback to SimFin data
            return get_simfin_fundamentals_fallback(ticker, curr_date)
    
    except Exception as e:
        # Fallback to SimFin data
        return get_simfin_fundamentals_fallback(ticker, curr_date)


def get_simfin_fundamentals_fallback(ticker, curr_date):
    """
    Fallback function to get fundamental data from SimFin when Google Search fails.
    """
    try:
        results = []
        
        # Get balance sheet
        balance = get_simfin_balance_sheet(ticker, "quarterly", curr_date)
        if balance:
            results.append(balance)
        
        # Get income statement
        income = get_simfin_income_statements(ticker, "quarterly", curr_date)
        if income:
            results.append(income)
        
        # Get cash flow
        cashflow = get_simfin_cashflow(ticker, "quarterly", curr_date)
        if cashflow:
            results.append(cashflow)
        
        if results:
            return "\n\n".join(results)
        else:
            return f"Unable to fetch fundamental data for {ticker}. Please check if the ticker is valid."
    except Exception as e:
        return f"Unable to fetch fundamental data for {ticker}. Error: {str(e)}"
