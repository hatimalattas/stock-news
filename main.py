import os
import requests
from twilio.rest import Client

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

# Alpha Vantage credentials
STOCK_ENDPOINT = "https://www.alphavantage.co/query"
STOCK_API_KEY = os.environ.get("STOCK_API_KEY")

# News credentials
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")

# Twilio credentials
ACCOUNT_SID = os.environ.get("ACCOUNT_SID")
AUTH_TOKEN = os.environ.get("AUTH_TOKEN")

stock_api_parameters = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": STOCK_API_KEY
}


def get_response(api_url, api_params):
    response = requests.get(url=api_url, params=api_params)
    response.raise_for_status()
    return response.json()


def percentage_change(new_number, original_number):
    difference = new_number - original_number
    percentage_difference = (difference / original_number) * 100
    percentage_difference = round(percentage_difference, 2)
    return percentage_difference


# # STEP 1: Use https://newsapi.org/docs/endpoints/everything When STOCK price increase/decreases by 5% between
# yesterday and the day before yesterday then print("Get News"). HINT 1: Get the closing price for yesterday and the
# day before yesterday. Find the positive difference between the two prices. e.g. 40 - 20 = -20, but the positive
# difference is 20. HINT 2: Work out the value of 5% of yesterday's closing stock price.

stock_data = get_response(STOCK_ENDPOINT, stock_api_parameters)

# To get the last refreshed date and the date day before
count = 0
for date in stock_data["Time Series (Daily)"]:
    if count == 0:
        last_refreshed_date = date
        count += 1
    elif count == 1:
        last_refreshed_date_day_before = date
        count += 1
    else:
        break

stock_price = stock_data["Time Series (Daily)"][last_refreshed_date]["4. close"]
stock_price_day_before = stock_data["Time Series (Daily)"][last_refreshed_date_day_before]["4. close"]

percentage = percentage_change(float(stock_price), float(stock_price_day_before))

# STEP 2: Use https://newsapi.org/docs/endpoints/everything
# Instead of printing ("Get News"), actually fetch the first 3 articles for the COMPANY_NAME. 
# HINT 1: Think about using the Python Slice Operator
if abs(percentage) > 0.1:
    news_api_parameters = {
        "q": COMPANY_NAME,
        "sortBy": "popularity",
        "apiKey": NEWS_API_KEY,
        "from": last_refreshed_date
    }
    news_data = get_response(NEWS_ENDPOINT, news_api_parameters)
    sliced_news = news_data["articles"][slice(0, 3)]
    news_list = []
    for article in sliced_news:
        title = article["title"]
        brief = article["description"]
        message = (title, brief)
        news_list.append(message)
    print(news_data)
    # print(sliced_news)

    # STEP 3: Use twilio.com/docs/sms/quickstart/python
    # Send a separate message with each article's title and description to your phone number.
    # HINT 1: Consider using a List Comprehension.
    # print(news_list)
    for news in news_list:
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        if percentage > 0:
            message = client.messages \
                .create(
                body=f"{STOCK}: 🔺{abs(percentage)}%\nHeadline: {news[0]}\nBrief: {news[1]}",
                from_='+14356339025',
                to='+966566131333'
            )
            # print(message.status)
            # print(message.body)

        elif percentage < 0:
            message = client.messages \
                .create(
                body=f"{STOCK}: 🔻{abs(percentage)}%\nHeadline: {news[0]}\nBrief: {news[1]}",
                from_='+14356339025',
                to='+966566131333'
            )
            # print(message.status)
            # print(message.body)

# Optional: Format the SMS message like this:
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""
